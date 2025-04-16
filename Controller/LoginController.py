from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from Utils.MyConnectPro import MyConnectPro
import os
from Service.Models import *
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


@login_blueprint.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"msg": "Tên đăng nhập và mật khẩu là bắt buộc"}), 400

    try:
        # Truy vấn tài khoản người dùng
        client = session_db.query(Account).filter_by(
            username=username).one_or_none()

        if not client or client.password != password:
            return jsonify({"msg": "Tên đăng nhập hoặc mật khẩu không chính xác"}), 400

        # Truy vấn vai trò
        role = session_db.query(Role).filter_by(
            RoleID=client.RoleID).one_or_none()
        if not role:
            return jsonify({"msg": "Role không tồn tại"}), 400

        role_name = role.RoleName

        # Mặc định thông tin mở rộng là rỗng
        extra_info = {}

        # Nếu là customer
        if role_name.lower() == "customer":
            customer = session_db.query(Customer).filter_by(
                AccountID=client.AccountID).one_or_none()
            if customer:
                extra_info = {
                    "CustomerID": customer.CustomerID,
                    "FirstName": customer.FirstName,
                    "LastName": customer.LastName
                }

        # Nếu là employee
        elif role_name.lower() in ["employee", "admin"]:
            employee = session_db.query(Employee).filter_by(
                AccountID=client.AccountID).one_or_none()
            if employee:
                extra_info = {
                    "EmployeeID": employee.EmployeeID,
                    "FirstName": employee.FirstName,
                    "LastName": employee.LastName
                }

        # Tạo JWT
        idenInfo = {
            "role": role_name,
            "userID": client.AccountID,
            "username": client.username,
            **extra_info  # Gộp thêm info vào token
        }

        access_token = create_access_token(identity=idenInfo, fresh=True)

        # Trả về kết quả
        return jsonify({
            "msg": "Đăng nhập thành công",
            "token": access_token,
            "userID": client.AccountID,
            "role": role_name,
            **extra_info  # Trả thêm thông tin người dùng
        }), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500
