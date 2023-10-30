from flask import Flask
from roomcontroller import room_api
from employeecontroller import employee_api
from flask_cors import CORS

app = Flask(__name__)

app.register_blueprint(room_api)
app.register_blueprint(employee_api)

CORS(app)


def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.after_request
def after_request(response):
    return add_cors_headers(response)


if __name__ == "__main":
    app.run(debug=True)
