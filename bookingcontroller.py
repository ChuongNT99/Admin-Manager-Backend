from flask import Flask, request, jsonify, Blueprint
import mysql.connector
from mysql.connector.errors import Error
from flask_cors import CORS
from db_config import db_config

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
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()

        if not employees:
            return jsonify({'error': 'No employees found'}), 404

        return jsonify({'employees': employees})
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
        # Kiểm tra xem thời gian mới có nằm trong khoảng thời gian đã đặt trước đó không
        cursor.execute(
            "SELECT booking_id FROM booking WHERE room_id = %s AND (%s <= time_end_booking AND %s >= time_start_booking)",
            (room_id, time_start, time_end)
        )
        existing_booking = cursor.fetchone()

        if existing_booking:
            return jsonify({'error': 'Room is already booked for this time'}), 400

        # Tiếp tục thêm thông tin đặt phòng
        cursor.execute("INSERT INTO booking (room_id, time_start_booking, time_end_booking) VALUES (%s, %s, %s)",
                       (room_id, time_start, time_end))
        booking_id = cursor.lastrowid
        conn.commit()

        employee_id = data.get('employees_id')
        cursor.execute("INSERT INTO booking_employees (booking_id, employees_id) VALUES (%s, %s)",
                       (booking_id, employee_id))

        return jsonify({'message': 'Booking created successfully'})

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
            "SELECT booking.booking_id, booking.room_id, booking.time_start_booking, booking.time_end_booking, "
            "room_meeting.room_name, employees.employees_name "
            "FROM booking "
            "INNER JOIN room_meeting ON booking.room_id = room_meeting.room_id "
            "INNER JOIN booking_employees ON booking.booking_id = booking_employees.booking_id "
            "INNER JOIN employees ON booking_employees.employees_id = employees.employees_id"
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
