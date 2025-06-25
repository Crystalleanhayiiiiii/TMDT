# payment_routes.py
from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime, timedelta
import hmac
import hashlib
from urllib.parse import urlencode
from datetime import timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from Utils.MyConnectPro import MyConnectPro
import os
from Service.Models import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

# Lấy thông tin kết nối từ biến môi trường
user = os.environ.get('USER_NAME')
password_db = os.environ.get('PASSWORD')
database = os.environ.get('DATABASE')
host = os.environ.get('HOST')
port = os.environ.get('PORT')

# Khởi tạo kết nối cơ sở dữ liệu
db_manager = MyConnectPro(user=user, password=password_db,
                          database=database, host=host, port=port)
db_manager.connect()
session_db = db_manager.get_session()

# Kết nối với cơ sở dữ liệu qua MyConnectPro (Giả sử đã có sẵn thông tin kết nối)
db_manager = MyConnectPro(user=user, password=password_db,
                          database=database, host=host, port=port)
db_manager.connect()
session_db = db_manager.get_session()

payment_blueprint = Blueprint("payment", __name__)

def get_client_ip():
    return request.remote_addr or '127.0.0.1'

@payment_blueprint.route('/create_payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        amount = int(data.get("amount", 0))
        order_info = data.get("order_info", "Thanh toan don hang")

        if amount <= 0:
            return jsonify({"msg": "Số tiền không hợp lệ"}), 400

        order_id = f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        ip_addr = get_client_ip()
        create_date = datetime.now().strftime('%Y%m%d%H%M%S')
        expire_date = (datetime.now() + timedelta(minutes=15)).strftime('%Y%m%d%H%M%S')

        vnp_params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': current_app.config['VNPAY_TMN_CODE'],
            'vnp_Amount': str(amount * 100),
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': order_id,
            'vnp_OrderInfo': order_info,
            'vnp_OrderType': 'billpayment',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': current_app.config['VNPAY_RETURN_URL'],
            'vnp_IpAddr': ip_addr,
            'vnp_CreateDate': create_date,
            'vnp_ExpireDate': expire_date
        }

        sorted_params = dict(sorted(vnp_params.items()))
        query_string = urlencode(sorted_params)
        hash_data = query_string.encode('utf-8')
        secure_hash = hmac.new(
            current_app.config['VNPAY_HASH_SECRET_KEY'].encode('utf-8'),
            hash_data,
            hashlib.sha512
        ).hexdigest()
        sorted_params['vnp_SecureHash'] = secure_hash

        payment_url = f"{current_app.config['VNPAY_PAYMENT_URL']}?{urlencode(sorted_params)}"
        return jsonify({"payment_url": payment_url, "order_id": order_id})

    except Exception as e:
        return jsonify({"msg": str(e)}), 500


@payment_blueprint.route('/vnpay_return')
def vnpay_return():
    session = db_manager.get_session()

    # Lấy các tham số từ URL
    params = request.args.to_dict()
    response_code = params.get('vnp_ResponseCode')
    transaction_status = params.get('vnp_TransactionStatus')
    order_info = params.get('vnp_OrderInfo')  # VD: "Thanh toan don hang 91 ..."

    message = ''
    status = ''
    order_id = None

    try:
        # ✅ Trích xuất OrderID từ chuỗi order_info
        import re
        match = re.search(r'thanh toan don hang (\d+)', order_info.lower())
        if match:
            order_id = int(match.group(1))
        else:
            return render_template('payment_result.html',
                                   message="Không tìm thấy mã đơn hàng trong OrderInfo.",
                                   status="error",
                                   order_code="N/A")

        # ✅ Kiểm tra trạng thái phản hồi
        if response_code == '24':
            message = '❌ Giao dịch bị hủy bởi người dùng!'
            status = 'canceled'

        elif transaction_status == '02':
            message = '❌ Giao dịch không thành công!'
            status = 'failed'

        elif response_code == '00' and transaction_status == '00':
            status = 'success'

            # ✅ Lấy đơn hàng
            order = session.query(Order).filter_by(OrderID=order_id).first()
            if not order:
                message = "Không tìm thấy đơn hàng"
                status = "error"
            elif order.Status == 'success':
                message = "Đơn hàng đã được thanh toán trước đó"
            elif order.Status != 'approved':
                message = "Đơn hàng chưa được phê duyệt"
                status = "error"
            else:
                # ✅ Lấy thông tin gói cước và dịch vụ
                price = order.price
                service = price.service
                speed_limit = service.Speed if service else None

                duration = price.Duration + (price.BonusMonths or 0)
                duration_days = duration * 30

                # ✅ Tìm subscription active cùng gói
                old_sub = (
                    session.query(Subscription)
                    .join(Order)
                    .filter(Order.CustomerID == order.CustomerID)
                    .filter(Order.PriceID == price.PriceID)
                    .filter(Subscription.Status == 'active')
                    .order_by(Subscription.EndDate.desc())
                    .first()
                )

                if old_sub:
                    # ➕ Gia hạn subscription cũ
                    old_sub.EndDate += timedelta(days=duration_days)
                    order.Status = "success"
                    session.commit()
                    message = f"✅ Thanh toán thành công. Gia hạn {duration} tháng cho gói {service.Name}. HSD mới: {old_sub.EndDate.strftime('%d/%m/%Y')}"
                else:
                    # ➕ Tạo mới subscription
                    start = datetime.utcnow().date()
                    end = start + timedelta(days=duration_days)
                    new_sub = Subscription(
                        OrderID=order.OrderID,
                        StartDate=start,
                        EndDate=end,
                        SpeedLimit=speed_limit,
                        Status='active'
                    )
                    session.add(new_sub)
                    order.Status = "success"
                    session.commit()
                    message = f"✅ Thanh toán thành công. Đã đăng ký mới gói {service.Name} đến ngày {end.strftime('%d/%m/%Y')}."

        else:
            message = '⚠️ Đã xảy ra lỗi không xác định.'
            status = 'error'

    except Exception as e:
        session.rollback()
        message = f"Lỗi hệ thống: {str(e)}"
        status = 'error'

    return render_template('payment_result.html',
                           message=message,
                           status=status,
                           order_code=order_id or "N/A")
