from flask import Blueprint, jsonify, request
import os
from Utils.MyConnectPro import MyConnectPro
from extensions.db import session_db
customer_bp=Blueprint('customer',__name__)
order_bp=Blueprint('order',__name__)
employee_bp=Blueprint('employee',__name__)
user = os.environ.get('USER_NAME')
password_db = os.environ.get('PASSWORD')
database = os.environ.get('DATABASE')
host = os.environ.get('HOST')
port = os.environ.get('PORT')
db_manager = MyConnectPro(user=user, password=password_db,
                          database=database, host=host, port=port)
db_manager.connect()
session_db = db_manager.get_session()
@order_bp.route('/order', methods=['GET'])
def get_infor_order():
    
    try:
        connection = db_manager.get_session().bind.raw_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT 
                CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
                s.Name AS ServiceName,
                p.PriceAmount,
                p.Duration,
                p.BonusMonths,
                o.OrderDate,
                o.Status,
                o.CustomerID,
                category.CategoryName
            FROM `order` AS o
            JOIN customer AS c ON c.CustomerID = o.CustomerID
            JOIN employee AS e ON e.EmployeeID = o.EmployeeID
            JOIN price AS p ON p.PriceID = o.PriceID
            JOIN service AS s ON s.ServiceID = p.ServiceID
            JOIN category ON category.CategoryID = s.CategoryID;
        """

        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results), 200

    except Exception as e:
        return jsonify({'msg': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@customer_bp.route('/customer', methods=['GET'])
def get_infor_customer():
    try:
        # Kết nối cơ sở dữ liệu
        connection = db_manager.get_session().bind.raw_connection()
        cursor = connection.cursor(dictionary=True)

        # Lệnh SQL trực tiếp thay vì gọi stored procedure
        query = """
            SELECT 
                CONCAT(FirstName, ' ', LastName) AS Name,
                BirthDate,
                CASE 
                    WHEN Gender = 1 THEN 'Nam'
                    WHEN Gender = 0 THEN 'Nữ'
                    ELSE 'Không xác định'
                END AS Gender,
                Address,
                Phone,
                Email
            FROM customer;
        """

        # Thực thi câu lệnh SQL
        cursor.execute(query)
        results = cursor.fetchall()

        # Trả về kết quả dưới dạng JSON
        return jsonify(results), 200

    except Exception as e:
        return jsonify({'msg': str(e)}), 500
@customer_bp.route('/customerfilter', methods=['GET'])
def is__member():
    try:
        connection=session_db.connection().connection
        cursor=connection.cursor(dictionary=True)
        cursor.callproc('is_member')
        results=[]
        for result in cursor.stored_results():
            results=result.fetchall()
        return jsonify(results),200
    except Exception as e:
        return jsonify({'msg': str(e)}),500
    
@employee_bp.route('/employee', methods=['GET'])
def get_infor_employee():
    
    try:
        connection = db_manager.get_session().bind.raw_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT 
                CONCAT(FirstName, ' ', LastName) AS Name,
                BirthDate,
                CASE 
                    WHEN Gender = 1 THEN 'Nam'
                    WHEN Gender = 0 THEN 'Nữ'
                    ELSE 'Không xác định'
                END AS Gender,
                Address,
                Phone,
                Email
            FROM employee;
        """

        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify(results), 200

    except Exception as e:
        return jsonify({'msg': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@customer_bp.route('/customer/order-history/<int:customer_id>', methods=['GET'])
def get_customer_order_history():
    customer_id = request.args.get('customer_id', type=int)
    if not customer_id:
        return jsonify({'msg': 'Thiếu customer_id'}), 400

    try:
        connection = db_manager.get_session().bind.raw_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT 
                CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
                s.Name AS ServiceName,
                p.PriceAmount,
                p.Duration,
                p.BonusMonths,
                o.OrderDate,
                o.Status,
                category.CategoryName
            FROM `order` AS o
            JOIN customer AS c ON c.CustomerID = o.CustomerID
            JOIN employee AS e ON e.EmployeeID = o.EmployeeID
            JOIN price AS p ON p.PriceID = o.PriceID
            JOIN service AS s ON s.ServiceID = p.ServiceID
            JOIN category ON category.CategoryID = s.CategoryID
            WHERE o.CustomerID = %s
            ORDER BY o.OrderDate DESC;
        """
        cursor.execute(query, (customer_id,))
        results = cursor.fetchall()
        return jsonify(results), 200

    except Exception as e:
        return jsonify({'msg': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
