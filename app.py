from flask import Flask
from roomcontroller import room_api
from employeecontroller import employee_api
from bookingcontroller import booking_api
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.after_request
def after_request(response):
    # Thực hiện cấu hình CORS 
    # response.headers['Access-Control-Allow-Origin'] = '*'  # Cho phép tất cả các nguồn truy cập
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    response.headers['Access-Control-Allow-Credentials'] = 'true'  # hỗ trợ thông tin xác thực (credentials)
    return response

app.register_blueprint(room_api)
app.register_blueprint(employee_api)
app.register_blueprint(booking_api)

if __name__ == "__main":
    app.run(debug=True)