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

        cursor.callproc('GetServicesByCategory', [id])  # Gọi stored procedure

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
                    'Area': row['Area'],
                    'Channels': row['Channels'] , # Có thể là NULL
                    'CategoryName':row['CategoryName']
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
def create_order_only():
    try:
        identity = get_jwt_identity()
        if identity.get("role", "").lower() != "customer":
            return jsonify({"msg": "Chỉ khách hàng mới được đặt gói"}), 403

        customer_id = identity.get("CustomerID")
        price_id = request.json.get("price_id")

        if not price_id:
            return jsonify({"msg": "Thiếu price_id"}), 400

        session = db_manager.get_session()

        # Kiểm tra gói cước
        price = session.query(Price).filter_by(PriceID=price_id).first()
        if not price:
            return jsonify({"msg": "Gói cước không tồn tại"}), 404

        # Kiểm tra xem khách đã từng dùng gói dịch vụ này chưa
        service_id = price.ServiceID
        existing_sub = (
            session.query(Subscription)
            .join(Order, Subscription.OrderID == Order.OrderID)
            .filter(Order.CustomerID == customer_id)
            .join(Price, Order.PriceID == Price.PriceID)
            .filter(Price.ServiceID == service_id)
            .first()
        )

        # Nếu có → tự động duyệt
        order_status = "approved" if existing_sub else "pending"

        # Tạo đơn hàng
        new_order = Order(
            CustomerID=customer_id,
            PriceID=price_id,
            Status=order_status
        )
        session.add(new_order)
        session.commit()

        return jsonify({
            "msg": f"Đơn hàng đã được tạo với trạng thái: {order_status}",
            "OrderID": new_order.OrderID
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
# register custommer
@service_blueprint.route('/register_customer', methods=['POST'])
def register_customer():
    try:
        data = request.get_json()

        required_fields = ['username', 'password', 'firstName', 'lastName', 'birthDate',
                           'gender', 'phone', 'email', 'address']
        # Kiểm tra đủ trường
        if not all(field in data and data[field] for field in required_fields):
            return jsonify({"msg": "Vui lòng nhập đầy đủ thông tin bắt buộc"}), 400

        session = db_manager.get_session()

        # Kiểm tra username đã tồn tại chưa
        existing = session.query(Account).filter_by(username=data['username']).first()
        if existing:
            return jsonify({"msg": "Tên đăng nhập đã tồn tại"}), 409
        # Kiểm tra trùng số điện thoại
        existing_phone = session.query(Customer).filter_by(Phone=data['phone']).first()
        if existing_phone:
            return jsonify({"msg": "Số điện thoại đã được sử dụng"}), 409


        # ✅ Tạo Account mới (gán sẵn RoleID là Customer role ID = 3)
        customer_role = session.query(Role).filter_by(RoleName="Customer").first()
        if not customer_role:
            return jsonify({"msg": "Role 'Customer' không tồn tại"}), 500

        new_account = Account(
            username=data['username'],
            password=data['password'],  
            RoleID=customer_role.RoleID
        )
        session.add(new_account)
        session.flush()  # Lấy được AccountID

        # ✅ Tạo Customer và gán AccountID
        new_customer = Customer(
            FirstName=data['firstName'],
            LastName=data['lastName'],
            BirthDate=datetime.strptime(data['birthDate'], "%Y-%m-%d"),
            Gender=bool(int(data['gender'])),
            Address=data['address'],
            Phone=data['phone'],
            Email=data['email'],
            AccountID=new_account.AccountID
        )
        session.add(new_customer)
        session.commit()

        return jsonify({"msg": "Đăng ký thành công", "CustomerID": new_customer.CustomerID}), 201

    except Exception as e:
        session.rollback()
        return jsonify({"msg": str(e)}), 500
# edit myifo
@service_blueprint.route('/edit_myinfo', methods=['PUT'])
@jwt_required()
def update_my_info():
    try:
        identity = get_jwt_identity()
        
        customer_id = identity.get("CustomerID")
        if not customer_id:
            return jsonify({"msg": "Thiếu CustomerID trong token"}), 400

        data = request.get_json()
        session = db_manager.get_session()
        #SQLAlchemy không flush bất kỳ thay đổi nào tạm thời trước khi query.
        with session.no_autoflush:
            customer = session.query(Customer).filter_by(CustomerID=customer_id).first()
        if not customer:
            return jsonify({"msg": "Không tìm thấy khách hàng"}), 404

        # ✅ Cập nhật từng trường nếu có trong request
        if "firstName" in data:
            customer.FirstName = data["firstName"]
        if "lastName" in data:
            customer.LastName = data["lastName"]
        if "phone" in data and data["phone"] != customer.Phone:
            existing = session.query(Customer).filter(
                Customer.Phone == data["phone"],
                Customer.CustomerID != customer_id
            ).first()
            if existing:
                return jsonify({"msg": "Số điện thoại đã được sử dụng"}), 409
            customer.Phone = data["phone"]

        if "email" in data:
            customer.Email = data["email"]
        if "address" in data:
            customer.Address = data["address"]
        if "birthDate" in data:
            customer.BirthDate = datetime.strptime(data["birthDate"], "%Y-%m-%d")
        if "gender" in data:
            customer.Gender = bool(int(data["gender"]))  # "0" hoặc "1"

        session.commit()
        return jsonify({"msg": "Cập nhật thông tin thành công"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"msg": str(e)}), 500

# my_order
@service_blueprint.route('/my_orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    try:
        identity = get_jwt_identity()
        role = identity.get("role", "").lower()

        if role != "customer":
            return jsonify({"msg": "Chỉ khách hàng mới được phép xem đơn hàng"}), 403

        customer_id = identity.get("CustomerID")
        if not customer_id:
            return jsonify({"msg": "Không tìm thấy CustomerID trong token"}), 400

        session = db_manager.get_session()

        # Lấy danh sách đơn hàng có thông tin dịch vụ và category
        orders = (
            session.query(Order)
            .join(Price, Order.PriceID == Price.PriceID)
            .join(Service, Price.ServiceID == Service.ServiceID)
            .join(Category, Service.CategoryID == Category.CategoryID)  #  Thêm join bảng Category
            .filter(Order.CustomerID == customer_id)
            .order_by(Order.OrderDate.desc())
            .all()
        )

        result = []
        for order in orders:
            result.append({
                "OrderID": order.OrderID,
                "OrderDate": order.OrderDate.strftime("%Y-%m-%d %H:%M:%S"),
                "Status": order.Status,
                "ServiceID":order.price.service.ServiceID,
                "ServiceName": order.price.service.Name,
                "Duration": order.price.Duration,
                "BonusMonths": order.price.BonusMonths,
                "PriceAmount": float(order.price.PriceAmount),
                "Currency": order.price.Currency,
                "Speed": order.price.service.Speed,
                "Area": order.price.service.Area,
                "Channels": order.price.service.Channels,
                "Type": order.price.service.category.CategoryName  # Tên loại gói (Category)
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
#thanh toan 
@service_blueprint.route('/pay_order', methods=['POST'])
@jwt_required()
def pay_and_create_subscription():
    try:
        identity = get_jwt_identity()
        if identity.get("role", "").lower() != "customer":
            return jsonify({"msg": "Chỉ khách hàng mới được thanh toán"}), 403

        customer_id = identity.get("CustomerID")
        data = request.get_json()

        order_id = data.get("order_id")
        method_name = data.get("method")
        account_number = data.get("accountNumber")
        password = data.get("password")
        bank_name = data.get("bankName", None)

        if not all([order_id, method_name, account_number, password]):
            return jsonify({"msg": "Thiếu thông tin thanh toán"}), 400

        session = db_manager.get_session()

        # Lấy đơn hàng
        order = session.query(Order).filter_by(OrderID=order_id, CustomerID=customer_id).first()
        if not order:
            return jsonify({"msg": "Đơn hàng không tồn tại hoặc không thuộc về bạn"}), 404
        if order.Status != "approved":
            return jsonify({"msg": "Đơn hàng của bạn phải được phê duyệt trước khi thanh toán."}), 403

        order = session.query(Order).filter_by(OrderID=order_id, CustomerID=customer_id).first()
        price = order.price
        service = price.service
        speed_limit = service.Speed if service else None

        # Kiểm tra phương thức và thông tin thanh toán
        method = session.query(PaymentMethod).filter_by(MethodName=method_name, Status='active').first()
        if not method:
            return jsonify({"msg": "Phương thức thanh toán không hợp lệ"}), 404

        filters = {
            PaymentInfo.MethodID == method.MethodID,
            PaymentInfo.AccountNumber == account_number,
            PaymentInfo.Password == password,
            PaymentInfo.Status == 'active'
        }
        if method_name == "Thẻ Ngân Hàng":
            filters.add(PaymentInfo.BankName == bank_name)

        payment_info = session.query(PaymentInfo).filter(*filters).first()
        if not payment_info:
            return jsonify({"msg": "Thông tin thanh toán không hợp lệ"}), 401

        # ✅ Kiểm tra Subscription cũ với gói này
        old_sub = (
            session.query(Subscription)
            .join(Order)
            .filter(Order.CustomerID == customer_id)
            .filter(Order.PriceID == price.PriceID)
            .filter(Subscription.Status == 'active')
            .order_by(Subscription.EndDate.desc())
            .first()
        )

        duration = price.Duration + (price.BonusMonths or 0)
        duration_days = duration * 30

        if old_sub:
            old_sub.EndDate += timedelta(days=duration_days)
            order.Status = "success"
            session.commit()
            
            return jsonify({
                "msg": "Thanh toán thành công, gia hạn Subscription",
                "SubscriptionID": old_sub.SubscriptionID,
                "NewEndDate": str(old_sub.EndDate),
                "ServiceName":price.service.Name
            }), 200
        else:
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
            
            return jsonify({
                "msg": "Thanh toán thành công, đã tạo Subscription mới",
                "SubscriptionID": new_sub.SubscriptionID,
                "StartDate": str(start),
                "EndDate": str(end),
                "ServiceName":price.service.Name
            }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"msg": str(e)}), 500
#huy 
@service_blueprint.route('/cancel_order', methods=['PUT'])
@jwt_required()
def cancel_order():
    try:
        identity = get_jwt_identity()
        if identity.get("role", "").lower() != "customer":
            return jsonify({"msg": "Chỉ khách hàng mới được hủy đơn hàng"}), 403

        data = request.get_json()
        order_id = data.get("order_id")
        reason = data.get("reason", "").strip()

        if not order_id:
            return jsonify({"msg": "Thiếu order_id"}), 400

        customer_id = identity.get("CustomerID")
        session = db_manager.get_session()

        order = session.query(Order).filter_by(OrderID=order_id, CustomerID=customer_id).first()
        if not order:
            return jsonify({"msg": "Không tìm thấy đơn hàng"}), 404
        if order.Status == "canceled":
            return jsonify({"msg": "Đơn hàng đã được hủy trước đó"}), 400
        if order.Status == "success":
            return jsonify({"msg": "Không thể hủy đơn hàng đã thanh toán"}), 400
        if order.Status == "approved":
            return jsonify({"msg": "Không thể hủy, đơn hàng đã được duyệt ,vui lòng liên hệ bộ phận CSKH"}), 400

        # Cập nhật trạng thái + ghi chú
        order.Status = "canceled"
        order.Note = reason or "Khách hàng không cung cấp lý do"
        session.commit()

        return jsonify({
            "msg": "✅ Đơn hàng đã được hủy",
            "OrderID": order.OrderID,
            "Note": order.Note
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({"msg": str(e)}), 500
# TÌm Kiếm 
@service_blueprint.route('/search_service', methods=['GET'])
def search_service_by_name():
    try:
        keyword = request.args.get("keyword", "").strip()

        if not keyword:
            return jsonify({"msg": "Vui lòng nhập từ khóa tìm kiếm"}), 400

        session = db_manager.get_session()

        results = (
            session.query(Service)
            .filter(Service.Name.ilike(f"%{keyword}%"))
            .all()
        )

        if not results:
            return jsonify({"msg": "Không tìm thấy gói phù hợp"}), 404

        response_data = []

        for s in results:
            # Lấy giá gói 1 tháng (duration = 1)
            price = (
                session.query(Price)
                .filter_by(ServiceID=s.ServiceID, Duration=1, Status='active')
                .first()
            )

            # ❌ Nếu không có giá -> bỏ qua
            if not price:
                continue

            # Lấy tên danh mục (quan hệ là .category, không phải .Category)
            category_name = s.category.CategoryName if s.category else None

            response_data.append({
                "ServiceID": s.ServiceID,
                "Name": s.Name,
                "Speed": s.Speed,
                "Area": s.Area,
                "Features": s.Features,
                "Channels": s.Channels,
                "CategoryID": s.CategoryID,
                "CategoryName": category_name,
                "PriceAmount": float(price.PriceAmount)
            })

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
#Lọc theo giá 
@service_blueprint.route('/filterby_price', methods=['POST'])
def filter_services_by_price():
    try:
        data = request.get_json()
        min_price = data.get("min_price")
        max_price = data.get("max_price")

        if min_price is None or max_price is None:
            return jsonify({"msg": "Vui lòng cung cấp min_price và max_price"}), 400

        session = db_manager.get_session()

        # Truy vấn theo khoảng giá và join với bảng Category để lấy CategoryName
        results = (
            session.query(Service, Price, Category)
            .join(Price, Service.ServiceID == Price.ServiceID)
            .join(Category, Service.CategoryID == Category.CategoryID)
            .filter(Price.PriceAmount >= min_price)
            .filter(Price.PriceAmount <= max_price)
            .all()
        )

        if not results:
            return jsonify({"msg": "Không tìm thấy gói phù hợp với mức giá"}), 404

        response_data = []
        for service, price, category in results:
            response_data.append({
                "ServiceID": service.ServiceID,
                "Name": service.Name,
                "Speed": service.Speed,
                "Area": service.Area,
                "PriceAmount": float(price.PriceAmount),
                "Duration": price.Duration,  # Thêm thời gian (tháng)
                "BonusMonths": price.BonusMonths,  # Thêm số tháng bonus
                "Currency": price.Currency,
                "CategoryName": category.CategoryName,  # Lấy CategoryName
                "Channels": service.Channels  # Thêm số kênh
            })

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    
@service_blueprint.route('/create_support_ticket', methods=['POST'])
@jwt_required()
def create_support_ticket():
    try:
        identity = get_jwt_identity()
        if identity.get("role", "").lower() != "customer":
            return jsonify({"msg": "Chỉ khách hàng mới có thể gửi yêu cầu hỗ trợ"}), 403

        customer_id = identity.get("CustomerID")
        data = request.get_json()

        subject = data.get("subject")
        description = data.get("description")
        order_id = data.get("order_id")      # Có thể None nếu không liên quan đến đơn
        subscription_id = data.get("subscription_id")  # Có thể None
        employee_id = None  # Có thể phân bổ sau khi nhân viên tiếp nhận

        if not subject or not description:
            return jsonify({"msg": "Tiêu đề và nội dung mô tả là bắt buộc"}), 400

        session = db_manager.get_session()

        ticket = SupportTicket(
            CustomerID=customer_id,
            SubscriptionID=subscription_id,
            OrderID=order_id,
            EmployeeID=employee_id,
            Subject=subject,
            Description=description,
            Status='open',
            CreatedAt=datetime.utcnow()
        )

        session.add(ticket)
        session.commit()

        return jsonify({
            "msg": "Yêu cầu hỗ trợ đã được tạo thành công",
            "TicketID": ticket.TicketID,
            "Status": ticket.Status,
            "CreatedAt": str(ticket.CreatedAt)
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"msg": str(e)}), 500
    
@service_blueprint.route('/support_ticket/<int:customer_id>', methods=['GET'])
def get_support_tickets_by_customer(customer_id):
    session = db_manager.get_session()
    try:
        tickets = session.query(SupportTicket).filter_by(CustomerID=customer_id).all()

        result = []
        for ticket in tickets:
            result.append({
                "TicketID": ticket.TicketID,
                "CustomerID": ticket.CustomerID,
                "SubscriptionID": ticket.SubscriptionID,
                "OrderID": ticket.OrderID,
                "EmployeeID": ticket.EmployeeID,
                "Subject": ticket.Subject,
                "Description": ticket.Description,
                "Status": ticket.Status,
                "CreatedAt": ticket.CreatedAt.strftime("%Y-%m-%d %H:%M:%S") if ticket.CreatedAt else None,
                "Resolution": ticket.Resolution,
                "ResolvedAt": ticket.ResolvedAt.strftime("%Y-%m-%d %H:%M:%S") if ticket.ResolvedAt else None
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500
    finally:
        session.close()

