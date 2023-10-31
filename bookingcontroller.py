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
    employee_id = data.get('employees_id')
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

        cursor.execute(
            "SELECT status FROM room_meeting WHERE room_id = %s", (room_id,))
        room_status = cursor.fetchone()
        if room_status:
            room_status = room_status[0]
            if room_status == 0:
                # Phòng đang trống, bạn có thể đặt phòng thành công
                cursor.execute(
                    "UPDATE room_meeting SET status = %s WHERE room_id = %s", (1, room_id))
                conn.commit()
                return jsonify({'message': 'Booking created successfully'})
            else:
                # Phòng đang bận, không thể đặt phòng
                return jsonify({'error': 'Room is not available, it is already booked'}), 400
        else:
            # Không tìm thấy thông tin phòng
            return jsonify({'error': 'Room information not found'}), 400
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
