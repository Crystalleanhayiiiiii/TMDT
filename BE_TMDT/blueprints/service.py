from flask import Blueprint
from Controller.AdminController import get_services

service_blueprint = Blueprint('service', __name__)
service_blueprint.route('/service', methods=['GET'])(get_services)
