from flask import Flask, redirect
from flask_restful import Api, Resource, reqparse
from healthcheck import HealthCheck, EnvironmentDump
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.core import patch_all

from time import sleep
import random
import logging
import json_logging
import sys
import os

service_name = os.getenv('SERVICE_NAME', '-')
service_version = os.getenv('SERVICE_VERSION', '-')
service_environment = os.getenv('SERVICE_ENVIRONMENT', '-')
app_mesh_version = os.getenv('APPMESH_VERSION', '-')
prefix = ('/%s' % service_name)

db_password = os.getenv('DB_PASSWORD', '-')

#Logging
json_logging.ENABLE_JSON_LOGGING = True
json_logging.init(framework_name='flask')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [stdout_handler]
logging.basicConfig(
    level=logging.INFO,
    handlers=handlers
)
json_logging.config_root_logger()

app = Flask(__name__)
api = Api(app)
json_logging.init_request_instrument(app)
LOGGER = logging.getLogger(__name__)
LOGGER.info('start application - %s', service_name)

xray_recorder.configure(service=service_name)
XRayMiddleware(app, xray_recorder)
patch_all()

# wrap the flask app and give a heathcheck url
health = HealthCheck(app, prefix + '/admin/healthcheck')
envdump = EnvironmentDump(app, prefix + '/admin/environment')

users = [
    {
        'name': 'Jonas',
        'age': 123,
        'occupation': 'Racing Driver'
    },
    {
        'name': 'Viktor',
        'age': 456,
        'occupation': 'Doctor'
    },
    {
        'name': 'Jerrett',
        'age': 789,
        'occupation': 'Super Hero'
    },
    {
        'name': 'Martin',
        'age': 999,
        'occupation': 'Dancer'
    }
]


class User(Resource):
    def get(self, name):
        for user in users:
            if (name == user['name']):
                return user, 200
        return 'User not found', 404

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument('age')
        parser.add_argument('occupation')
        args = parser.parse_args()

        for user in users:
            if (name == user['name']):
                return 'User with name {} already exists'.format(name), 400

        user = {
            'name': name,
            'age': args['age'],
            'occupation': args['occupation']
        }
        users.append(user)
        return user, 201

    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument('age')
        parser.add_argument('occupation')
        args = parser.parse_args()

        for user in users:
            if (name == user['name']):
                user['age'] = args['age']
                user['occupation'] = args['occupation']
                return user, 200

        user = {
            'name': name,
            'age': args['age'],
            'occupation': args['occupation']
        }
        users.append(user)
        return user, 201

    def delete(self, name):
        global users
        users = [user for user in users if user['name'] != name]
        return '{} is deleted.'.format(name), 200

@app.route(prefix + '/')
def main_index():
    LOGGER.info('main_index', extra = {'props' : {'name' : service_name, 'version' : service_version, 'environment' : service_environment, 'db_password': db_password}})
    return '\nNAME: %s\nVERSION: %s\nENVIRONMENT: %s\nAPPMESH_VERSION: %s \nDB_PASSWORD: %s' % (service_name, service_version, service_environment, app_mesh_version, db_password)

@app.route(prefix + '/stats')
def stats():
    random_float_number = random.uniform(0.01, 4.0)
    if (random_float_number > 3.0):
        return ('ERROR %s' % random_float_number), 500
    else:
        sleep(random_float_number)
        return 'OK', 200

api.add_resource(User, prefix + '/user/<string:name>')
