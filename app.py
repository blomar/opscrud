from flask import Flask, redirect
from flask_restful import Api, Resource, reqparse
from healthcheck import HealthCheck, EnvironmentDump

app = Flask(__name__)
api = Api(app)

# wrap the flask app and give a heathcheck url
health = HealthCheck(app, "/healthcheck")
envdump = EnvironmentDump(app, "/environment")

users = [
    {
        "name": "Jonas",
        "age": 12,
        "occupation": "Network Engineer"
    },
    {
        "name": "Viktor",
        "age": 13,
        "occupation": "Doctor"
    },
    {
        "name": "Jerret",
        "age": 14,
        "occupation": "Web Developer"
    },
    {
        "name": "Martin",
        "age": 15,
        "occupation": "Cleaner"
    }
]


class User(Resource):
    def get(self, name):
        for user in users:
            if (name == user["name"]):
                return user, 200
        return "User not found", 404

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("age")
        parser.add_argument("occupation")
        args = parser.parse_args()

        for user in users:
            if (name == user["name"]):
                return "User with name {} already exists".format(name), 400

        user = {
            "name": name,
            "age": args["age"],
            "occupation": args["occupation"]
        }
        users.append(user)
        return user, 201

    def put(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("age")
        parser.add_argument("occupation")
        args = parser.parse_args()

        for user in users:
            if (name == user["name"]):
                user["age"] = args["age"]
                user["occupation"] = args["occupation"]
                return user, 200

        user = {
            "name": name,
            "age": args["age"],
            "occupation": args["occupation"]
        }
        users.append(user)
        return user, 201

    def delete(self, name):
        global users
        users = [user for user in users if user["name"] != name]
        return "{} is deleted.".format(name), 200

@app.route('/')
def main_index():
    return "This is OPS Crud service - GET/POST/PUT/DELETE - http://127.0.0.1:5000/user/'string:name'"

@app.route('/ping')
def ping():
    return redirect('/healthcheck')

api.add_resource(User, "/user/<string:name>")
