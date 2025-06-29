import config
from flask import Flask
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta

from Controller.AdminController import service_bp, category_bp
from Controller.CustomerAdmin import customer_bp,order_bp, employee_bp
from Controller.AccountController import account_bp

from Controller.LoginController import login_blueprint
from Controller.CustomerController import service_blueprint
app = Flask(__name__)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CORS(app)

# Đăng ký các blueprint cho các controller
app.register_blueprint(login_blueprint)  # Đăng ký login blueprint
app.register_blueprint(customer_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(service_bp)
app.register_blueprint(service_blueprint)
app.register_blueprint(category_bp)
app.register_blueprint(account_bp)
app.register_blueprint(order_bp)
# Cấu hình JWT
secret_key = os.environ.get('SECRET_KEY')
app.config["JWT_SECRET_KEY"] = secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

jwt = JWTManager(app)

@app.route('/')
def index():
    response = jsonify({"msg": "Test successfully"})
    return response, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=7777)
