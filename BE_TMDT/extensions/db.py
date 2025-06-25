import os
from Utils.MyConnectPro import MyConnectPro

user = os.environ.get('USER_NAME')
password_db = os.environ.get('PASSWORD')
database = os.environ.get('DATABASE')
host = os.environ.get('HOST')
port = os.environ.get('PORT')

db_manager = MyConnectPro(user=user, password=password_db, database=database, host=host, port=port)
db_manager.connect()
session_db = db_manager.get_session()
