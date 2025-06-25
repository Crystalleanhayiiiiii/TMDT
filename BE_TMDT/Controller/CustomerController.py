from datetime import timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from Utils.MyConnectPro import MyConnectPro
import os
from Service.Models import *
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
# Khởi tạo Blueprint cho Login
login_blueprint = Blueprint('login', __name__)

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
# Tạo blueprint
service_blueprint = Blueprint('service', __name__)

# Kết nối với cơ sở dữ liệu qua MyConnectPro (Giả sử đã có sẵn thông tin kết nối)
db_manager = MyConnectPro(user=user, password=password_db,
                          database=database, host=host, port=port)
db_manager.connect()
session_db = db_manager.get_session()


@service_blueprint.route('/service/<int:id>', methods=['GET'])
def get_servicesById(id):
    try:
        connection = session_db.connection().connection  # Lấy raw MySQL connection
        # Dùng dictionary=True để trả về dict
        cursor = connection.cursor(dictionary=True)

        cursor.callproc('GetServicesByCategory1', [id])  # Gọi stored procedure

        # Lấy tất cả kết quả trả về từ stored procedure
        results = []
        for result_set in cursor.stored_results():
            for row in result_set:
                # Mỗi dòng sẽ là 1 dịch vụ, ánh xạ đúng trường dữ liệu
                results.append({
                    'ServiceID': row['ServiceID'],
                    'Name': row['Name'],
                    'Speed': row['Speed'],
                    'PriceAmount': float(row['PriceAmount']),
                    'Area': row['area'],
                    'Features': row['Features'],
                    'Channels': row['Channels']  # Có thể là NULL
                })

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'msg': str(e)}), 500


@service_blueprint.route('/service_detail/<int:id>', methods=['GET'])
def get_internet_service_by_id(id):
    try:
        # Lấy kết nối và cursor từ MySQL
        connection = db_manager.get_session().bind.raw_connection()
        cursor = connection.cursor(dictionary=True)

        # Gọi Stored Procedure GetServiceDetailsByID với tham số service_id
        cursor.callproc('GetServiceDetailsByID', [id])

        # Lấy kết quả trả về từ SP
        results = cursor.stored_results()

        # Chuẩn bị kết quả trả về
        service_data = []
        for result_set in results:
            for row in result_set:
                # Trả về các trường trực tiếp từ SP
                service_data.append({
                    'ServiceID': row['ServiceID'],
                    'ServiceName': row['ServiceName'],
                    'Speed': row['Speed'],
                    'Channels': row['Channels'],
                    'Area': row['Area'],
                    'Features': row['Features'],
                    'PriceID_1_month': float(row['PriceID_1_month']),
                    'Price_1_month': float(row['Price_1_month']),
                    'Bonus_1_month': row['Bonus_1_month'],
                    'PriceID_6_months': float(row['PriceID_6_months']),
                    'Price_6_months': float(row['Price_6_months']),
                    'Bonus_6_months': row['Bonus_6_months'],
                    'PriceID_12_months': float(row['PriceID_12_months']),
                    'Price_12_months': float(row['Price_12_months']),
                    'Bonus_12_months': row['Bonus_12_months'],
                    'Currency': row['Currency'],
                    'Status': row['Status']
                })

        # Trả về chi tiết dịch vụ
        if service_data:
            # Chỉ trả về đối tượng đầu tiên trong danh sách (nếu có)
            return jsonify(service_data[0]), 200
        else:
            return jsonify({'msg': 'Service not found'}), 404

    except Exception as e:
        return jsonify({'msg': str(e)}), 500


@service_blueprint.route('/myinfo/', methods=['GET'])
@jwt_required()
def get_my_info():
    try:
        identity = get_jwt_identity()
        print(">> Token identity:", identity)

        if not identity or "role" not in identity:
            return jsonify({"msg": "Token không hợp lệ"}), 400

        role = identity["role"].strip().lower()
        session = db_manager.get_session()

        # Nếu là nhân viên hoặc admin
        if role in ["employee", "admin"]:
            employee_id = identity.get("EmployeeID")
            if not employee_id:
                return jsonify({"msg": "Token không chứa EmployeeID"}), 400

            employee = session.query(Employee).filter_by(
                EmployeeID=employee_id).one_or_none()
            if not employee:
                return jsonify({"msg": "Không tìm thấy nhân viên"}), 404

            return jsonify({
                "type": "employee",
                "EmployeeID": employee.EmployeeID,
                "FirstName": employee.FirstName,
                "LastName": employee.LastName,
                "BirthDate": str(employee.BirthDate) if employee.BirthDate else None,
                "Gender": "Nam" if employee.Gender else "Nữ",
                "Phone": employee.Phone,
                "Email": employee.Email,
                "Address": employee.Address,
                "Status": "Hoạt động" if employee.Status else "Ngưng hoạt động"
            }), 200

        # Nếu là khách hàng
        elif role == "customer":
            customer_id = identity.get("CustomerID")
            if not customer_id:
                return jsonify({"msg": "Token không chứa CustomerID"}), 400

            customer = session.query(Customer).filter_by(
                CustomerID=customer_id).one_or_none()
            if not customer:
                return jsonify({"msg": "Không tìm thấy khách hàng"}), 404

            return jsonify({
                "type": "customer",
                "CustomerID": customer.CustomerID,
                "FirstName": customer.FirstName,
                "LastName": customer.LastName,
                "BirthDate": str(customer.BirthDate) if customer.BirthDate else None,
                "Gender": "Nam" if customer.Gender else "Nữ",
                "Phone": customer.Phone,
                "Email": customer.Email,
                "Address": customer.Address,
                "Status": "Hoạt động" if customer.Status else "Ngưng hoạt động"
            }), 200

        else:
            return jsonify({"msg": "Vai trò không được hỗ trợ"}), 403

    except Exception as e:
        return jsonify({"msg": str(e)}), 500


@service_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ["username", "password",
                       "first_name", "last_name", "phone"]

    # Kiểm tra các trường bắt buộc
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"msg": "Vui lòng nhập đầy đủ thông tin bắt buộc"}), 400

    try:
        session = db_manager.get_session()

        # Kiểm tra username đã tồn tại chưa
        existing_account = session.query(Account).filter_by(
            username=data["username"]).first()
        if existing_account:
            return jsonify({"msg": "Tên đăng nhập đã được sử dụng"}), 409

        # Kiểm tra số điện thoại đã tồn tại chưa
        existing_phone = session.query(Customer).filter_by(
            Phone=data["phone"]).first()
        if existing_phone:
            return jsonify({"msg": "Số điện thoại đã được đăng ký"}), 409

        # Gán mặc định Role là Customer (giả sử RoleID = 3)
        customer_role = session.query(Role).filter_by(
            RoleName="Customer").one_or_none()
        if not customer_role:
            return jsonify({"msg": "Không tìm thấy vai trò Customer"}), 500

        # Tạo account
        new_account = Account(
            username=data["username"],
            password=data["password"],
            RoleID=customer_role.RoleID
        )
        session.add(new_account)
        session.flush()  # Để lấy được AccountID mới tạo

        # Tạo customer
        new_customer = Customer(
            FirstName=data["first_name"],
            LastName=data["last_name"],
            BirthDate=data.get("birth_date"),
            Gender=data.get("gender", True),
            Address=data.get("address"),
            Phone=data["phone"],
            Email=data.get("email"),
            Status=True,
            AccountID=new_account.AccountID
        )
        session.add(new_customer)

        session.commit()

        return jsonify({"msg": "Đăng ký thành công"}), 201

    except IntegrityError:
        session.rollback()
        return jsonify({"msg": "Dữ liệu bị trùng hoặc không hợp lệ"}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"msg": str(e)}), 500


@service_blueprint.route('/my_subcriptions', methods=['GET'])
@jwt_required()
def get_my_subscriptions():
    try:
        identity = get_jwt_identity()

        # Kiểm tra role
        if not identity or identity.get("role", "").lower() != "customer":
            return jsonify({"msg": "Chỉ khách hàng mới được phép truy cập"}), 403

        customer_id = identity.get("CustomerID")
        if not customer_id:
            return jsonify({"msg": "Không tìm thấy thông tin khách hàng trong token"}), 400

        session = db_manager.get_session()

        # JOIN bảng Subscription -> Order -> Price -> Service
        subscriptions = (
            session.query(Subscription, Price, Service)
            .join(Order, Subscription.OrderID == Order.OrderID)
            .join(Price, Order.PriceID == Price.PriceID)
            .join(Service, Price.ServiceID == Service.ServiceID)
            .filter(Order.CustomerID == customer_id)
            .all()
        )

        result = []
        for sub, price, service in subscriptions:
            result.append({
                "SubscriptionID": sub.SubscriptionID,
                "Status": sub.Status,
                "StartDate": str(sub.StartDate),
                "EndDate": str(sub.EndDate),
                "SpeedLimit": sub.SpeedLimit,
                "ServiceName": service.Name,
                "ServiceID": service.ServiceID, 
                "Speed": service.Speed,
                "Area": service.Area,
                "Duration": price.Duration,
                "BonusMonths": price.BonusMonths,
                "Price": float(price.PriceAmount),
                "Currency": price.Currency
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500


@service_blueprint.route('/order_service', methods=['POST'])
@jwt_required()
def create_order_and_extend_subscription():
    try:
        identity = get_jwt_identity()
        role = identity.get("role", "").lower()

        if role != "customer":
            return jsonify({"msg": "Chỉ khách hàng mới được đặt gói"}), 403

        customer_id = identity.get("CustomerID")
        data = request.get_json()
        price_id = data.get("price_id")

        if not price_id:
            return jsonify({"msg": "Thiếu price_id"}), 400

        session = db_manager.get_session()

        # Lấy gói cước
        price = session.query(Price).filter_by(PriceID=price_id).one_or_none()
        if not price:
            return jsonify({"msg": "Gói cước không tồn tại"}), 404

        # Lấy thông tin Service để biết tốc độ
        service = session.query(Service).filter_by(
            ServiceID=price.ServiceID).one_or_none()
        if service:
            print(">> Service.Speed:", service.Speed)

        speed_limit = service.Speed if service else None
        # ✅ Tạo Order mới
        new_order = Order(
            CustomerID=customer_id,
            PriceID=price_id,
            Status="pending"
        )
        session.add(new_order)
        session.flush()

        # ✅ Kiểm tra xem có subscription đang active với gói này không
        active_subscription = (
            session.query(Subscription)
            .join(Order, Subscription.OrderID == Order.OrderID)
            .filter(Order.CustomerID == customer_id)
            .filter(Order.PriceID == price_id)
            .filter(Subscription.Status == 'active')
            .order_by(Subscription.EndDate.desc())
            .first()
        )

        duration = price.Duration + (price.BonusMonths or 0)
        duration_days = duration * 30

        if active_subscription:
            # Cộng thêm thời gian vào subscription cũ
            active_subscription.EndDate += timedelta(days=duration_days)
            session.commit()
            return jsonify({
                "msg": "Gia hạn gói thành công (và tạo Order mới)",
                "OrderID": new_order.OrderID,
                "SubscriptionID": active_subscription.SubscriptionID,
                "NewEndDate": str(active_subscription.EndDate)
            }), 200

        else:
            # Không có → tạo subscription mới
            start_date = datetime.utcnow().date()
            end_date = start_date + timedelta(days=duration_days)

            new_sub = Subscription(
                OrderID=new_order.OrderID,
                StartDate=start_date,
                EndDate=end_date,
                SpeedLimit=speed_limit,
                Status='active'
            )
            session.add(new_sub)
            session.commit()

            return jsonify({
                "msg": "Đặt gói thành công và tạo Subscription mới",
                "OrderID": new_order.OrderID,
                "SubscriptionID": new_sub.SubscriptionID,
                "StartDate": str(start_date),
                "EndDate": str(end_date)
            }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"msg": str(e)}), 500
@service_blueprint.route('/change_account', methods=['PUT'])
@jwt_required()
def change_account():
    try:
        identity = get_jwt_identity()
        account_id = identity.get("userID")  # Lấy từ token
        session = db_manager.get_session()

        data = request.get_json()
        new_username = data.get("username")
        new_password = data.get("password")

        if not new_username and not new_password:
            return jsonify({"msg": "Cần ít nhất username hoặc password để cập nhật"}), 400

        # Lấy tài khoản hiện tại
        account = session.query(Account).filter_by(AccountID=account_id).one_or_none()
        if not account:
            return jsonify({"msg": "Tài khoản không tồn tại"}), 404

        # Kiểm tra username trùng
        if new_username and new_username != account.username:
            existing = session.query(Account).filter_by(username=new_username).first()
            if existing:
                return jsonify({"msg": "Tên đăng nhập đã tồn tại"}), 409
            account.username = new_username

        if new_password:
            account.password = new_password  # (Gợi ý: dùng hash trong thực tế)

        session.commit()

        return jsonify({"msg": "Cập nhật tài khoản thành công"}), 200

    except IntegrityError:
        session.rollback()
        return jsonify({"msg": "Tên đăng nhập đã tồn tại"}), 409
    except Exception as e:
        session.rollback()
        return jsonify({"msg": str(e)}), 500