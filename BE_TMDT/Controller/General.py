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