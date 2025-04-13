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
db_manager = MyConnectPro(user=user, password=password_db, database=database, host=host, port=port)
db_manager.connect()
session_db = db_manager.get_session()

@login_blueprint.route('/login', methods=['POST'])
def login():
    # Lấy username và password từ body request
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"msg": "Tên đăng nhập và mật khẩu là bắt buộc"}), 400

    try:
        # Truy vấn tài khoản người dùng từ cơ sở dữ liệu
        client = session_db.query(Account).filter_by(username=username).one_or_none()
        # Nếu không tìm thấy tài khoản hoặc mật khẩu không đúng
        if not client or client.password != password:
            return jsonify({"msg": "Tên đăng nhập hoặc mật khẩu không chính xác"}), 400

        # Truy vấn vai trò của người dùng từ bảng Role
        role = session_db.query(Role).filter_by(RoleID=client.RoleID).one_or_none()

        if not role:
            return jsonify({"msg": "Role không tồn tại"}), 400

        # Lấy tên vai trò
        role_name = role.RoleName

        # Tạo JWT Token
        idenInfo = {
            "role": role_name,  # Gán role cho người dùng
            "userID": client.AccountID,
            "username": client.username
        }

        access_token = create_access_token(identity=idenInfo, fresh=True)

        # Trả về các token trong response
        return jsonify({
            "msg": "Đăng nhập thành công",
            "token": access_token,
            "userID": client.AccountID,
            "role": role_name
        }), 200

    except Exception as e:
        return jsonify({"msg": str(e)}), 500
