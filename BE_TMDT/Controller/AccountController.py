from flask import Blueprint, jsonify, request
from extensions.db import session_db
account_bp=Blueprint('account',__name__)
@account_bp.route('/account', methods=['GET'])
def get_account_employee():
    try:
        connection=session_db.connection().connection
        cursor=connection.cursor(dictionary=True)
        cursor.callproc('sp_get_account_employee')
        results=[]
        for result in cursor.stored_results():
            results=result.fetchall()
        return jsonify(results),200
    except Exception as e:
        return jsonify({'msg': str(e)}), 500

@account_bp.route('/employee', methods=['GET'])
def get_infor_employee():
    try:
        connection=session_db.connection().connection
        cursor=connection.cursor(dictionary=True)
        cursor.callproc('sp_get_employee')
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 500
@account_bp.route('/employee', methods=['GET'])
def get_employee_by_account():
    try:
        account_id = request.args.get('account_id')
        connection = session_db.connection().connection
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('sp_get_employee_by_account', [account_id])
        results = []
        for result in cursor.stored_results():
            results = result.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'msg': str(e)}), 500

        
