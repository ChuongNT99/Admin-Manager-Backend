from flask import Flask, request, jsonify, Blueprint
import mysql.connector
from mysql.connector.errors import Error
from flask_cors import CORS
from db_config import db_config
from datetime import datetime


app = Flask(__name__)

booking_api = Blueprint("bookingcontroller", __name__)


def create_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None


@booking_api.route('/get_employee', methods=['GET'])
def get_employee():
    employee_id = request.args.get('employee_id')

    if not employee_id:
        return jsonify({'error': 'employee_id is required'}), 400

    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM employees WHERE employees_id = %s", (employee_id,))
        employee = cursor.fetchone()

        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        return jsonify(employee)
    except Error as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    finally:
        cursor.close()
        conn.close()


@booking_api.route('/bookings', methods=['POST'])
def book_room():
    data = request.get_json()
    room_id = data.get('room_id')
    time_start = data.get('time_start_booking')
    time_end = data.get('time_end_booking')
    print(time_start, "TIME STARTTTTTTTTTTTTTTTTT")
    print(time_end, "TIME ENDDDDDDDDDDDDDDDĐ")
    employee_id = data.get('employees_id')
    current_time = datetime.now()
    formatted_current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    print(formatted_current_time, "CURRENT TIMEEEEEEEEEE")
    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO booking (room_id, time_start_booking, time_end_booking) VALUES (%s, %s, %s)",
                       (room_id, time_start, time_end))
        booking_id = cursor.lastrowid
        conn.commit()

        employee_id = data.get('employees_id')
        cursor.execute("INSERT INTO booking_employees (booking_id, employees_id) VALUES (%s, %s)",
                       (booking_id, employee_id))
        cursor.execute(
            "SELECT * FROM employees WHERE employees_id = %s", (employee_id,))
        employee_info = cursor.fetchall()
        if employee_info:
            print("Employee Info:", employee_info)
        else:
            print("Employee not found with ID:", employee_id)
            return jsonify({'error': 'Employee not found'}), 404
        conn.commit()

        cursor.execute("SELECT * FROM booking WHERE room_id = %s", (room_id,))
        booking_info = cursor.fetchall()

    # Kiểm tra xem thời gian hiện tại có nằm trong khoảng đặt phòng hay không
        if booking_info:
            time_start_booking = booking_info[0][2]
            time_end_booking = booking_info[0][3]
        # Kiểm tra xem thời gian hiện tại có nằm trong khoảng đặt phòng hay không
            if time_start_booking <= formatted_current_time <= time_end_booking:
                cursor.execute(
                    "UPDATE room_meeting SET status = %s WHERE room_id = %s", (1, room_id))
                conn.commit()
                return jsonify({'message': 'Booking created successfully'})
            else:
                # Nếu thời gian hiện tại không nằm trong khoảng đặt phòng, trả về lỗi
                print("Phòng không còn trống cho thời gian này")
                return jsonify({'error': 'Room is not available for this time'}), 400
        else:
            print("Không tìm thấy thông tin đặt phòng cho phòng có room_id =", room_id)
            return jsonify({'error': 'Room booking information not found'})
    except Error as e:
        print("Error:", e)
        return jsonify({'error': 'Internal Server Error'}), 500
    finally:
        cursor.close()
        conn.close()


@booking_api.route('/bookings', methods=['GET'])
def get_bookings():
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT booking.*, room_meeting.room_name, employees.employees_name "
            "FROM booking "
            "INNER JOIN room_meeting ON booking.room_id = room_meeting.room_id "
            "INNER JOIN employees ON booking.employee_id = employees.employees_id"
        )
        rows = cursor.fetchall()
        return jsonify({'bookings': rows})
    except Error as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
