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
# Tạo blueprint
service_blueprint = Blueprint('service', __name__)

# Kết nối với cơ sở dữ liệu qua MyConnectPro (Giả sử đã có sẵn thông tin kết nối)
db_manager = MyConnectPro(user=user, password=password_db, database=database, host=host, port=port)
db_manager.connect()
session_db = db_manager.get_session()
@service_blueprint.route('admin/internet', methods=['GET'])
def get_internet_services():
    category_id = 1  # Chỉ định category_id = 1 trong truy vấn SP
    try:
        # Lấy kết nối và cursor từ MySQL
        connection = db_manager.get_session().bind.raw_connection()
        cursor = connection.cursor(dictionary=True)

        # Gọi Stored Procedure GetServicesByCategory với tham số category_id
        cursor.callproc('GetServicesByCategory', [category_id])

        # Lấy kết quả trả về từ SP
        results = cursor.stored_results()
        
        # Chuẩn bị kết quả trả về
        service_data = {}
        for result_set in results:
            for row in result_set:
                service_id = row['ServiceID']
                
                # Kiểm tra xem dịch vụ này đã được thêm chưa
                if service_id not in service_data:
                    service_data[service_id] = {
                        'service': {
                            'ServiceID': row['ServiceID'],
                            'ServiceName': row['ServiceName'],
                            'Speed': row['Speed'],
                            'Channels': row['Channels'],
                            'Area': row['Area'],
                            'Features': row['Features']
                        },
                        'prices': {}
                    }

                # Phân loại mức giá theo duration
                if row['Duration'] == 1:
                    service_data[service_id]['prices']['1_month'] = {
                        'price': float(row['PriceAmount']),
                        'bonus_months': row['BonusMonths'],
                        'currency': row['Currency'],
                        'status': row['Status']
                    }
                elif row['Duration'] == 6:
                    service_data[service_id]['prices']['6_months'] = {
                        'price': float(row['PriceAmount']),
                        'bonus_months': row['BonusMonths'],
                        'currency': row['Currency'],
                        'status': row['Status']
                    }
                elif row['Duration'] == 12:
                    service_data[service_id]['prices']['12_months'] = {
                        'price': float(row['PriceAmount']),
                        'bonus_months': row['BonusMonths'],
                        'currency': row['Currency'],
                        'status': row['Status']
                    }

        # Convert service_data dictionary to list
        result_list = list(service_data.values())

        return jsonify(result_list), 200

    except Exception as e:
        return jsonify({'msg': str(e)}), 500