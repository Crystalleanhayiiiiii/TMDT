from flask import Blueprint, request, jsonify
from extensions.db import session_db

# Tạo Blueprint cho category và service
category_bp = Blueprint('category', __name__)
service_bp = Blueprint('service1', __name__)

# ------------------------ CATEGORY API ------------------------

@category_bp.route('/category', methods=['GET'])
def get_all_categories():
    try:
        connection = session_db.connection().connection
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('sp_get_all_category')
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 500

@category_bp.route('/category', methods=['POST'])
def add_category():
    try:
        data = request.get_json()
        connection = session_db.connection().connection
        cursor = connection.cursor(dictionary=True)

        cursor.callproc('sp_add_category1', (data['CategoryName'],))
        connection.commit()
        return jsonify({'msg': 'Category added successfully'}), 201
    except Exception as e:
        return jsonify({'msg': str(e)}), 500

@category_bp.route('/category/<int:categoryID>', methods=['GET'])
def get_category_by_id(categoryID):
    try:
        connection = session_db.connection().connection
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('sp_get_category', (categoryID,))
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 500

# ------------------------ SERVICE API ------------------------

@service_bp.route('/service', methods=['GET'])
def get_all_services():
    try:
        connection = session_db.connection().connection
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('sp_get_all_services')
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 500

@service_bp.route('/service/by_ID/<int:serviceID>', methods=['GET'])
def get_service_by_id(serviceID):
    try:
        connection = session_db.connection().connection
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('sp_get_service', (serviceID,))
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 500

@service_bp.route('/service/by_category/<int:categoryID>', methods=['GET'])
def get_services_by_category(categoryID):
    try:
        connection = session_db.connection().connection
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('get_services_by_category2', (categoryID,))
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 500

@service_bp.route('/service', methods=['POST'])
def add_service():
    try:
        data = request.get_json()
        connection = session_db.connection().connection
        cursor = connection.cursor(dictionary=True)

        cursor.callproc('sp_add_service', (
            data['CategoryID'],
            data['ManagementID'],
            data['Name'],
            data['Speed'],
            data['Channels'],
            data['Area'],
            data['Features'],
            data['ImageURL'],
        ))

        connection.commit()
        return jsonify({'msg': 'Service added successfully'}), 201
    except Exception as e:
        return jsonify({'msg': str(e)}), 500
