from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from db_config import db_config
import mysql.connector
from datetime import datetime

app = Flask(__name__)

room_api = Blueprint("roomcontroller", __name__)


def create_db_connection():
    return mysql.connector.connect(**db_config)


@room_api.route("/rooms", methods=["GET"])
def get_rooms():
    try:
        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM room_meeting")
        rooms = cursor.fetchall()
        current_time = datetime.now()

        for room in rooms:
            room_id = room['room_id']

            # Kiểm tra xem có bất kỳ đặt phòng nào cho phòng này và thời gian hiện tại nằm trong khoảng đó hay không
            cursor.execute(
                "SELECT booking_id, time_start_booking, time_end_booking FROM booking WHERE room_id = %s AND %s BETWEEN time_start_booking AND time_end_booking",
                (room_id, current_time)
            )
            booking_info = cursor.fetchone()

            if booking_info:
                # Trạng thái của phòng bây giờ là 1 (bận)
                cursor.execute(
                    "UPDATE room_meeting SET status = 1 WHERE room_id = %s", (room_id,))
                conn.commit()
            else:
                # Phòng trống
                cursor.execute(
                    "UPDATE room_meeting SET status = 0 WHERE room_id = %s", (room_id,))
                conn.commit()

        return jsonify({"rooms": rooms})
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        cursor.close()
        conn.close()


@room_api.route("/rooms", methods=["POST"])
def create_room():
    try:
        data = request.get_json()
        room_name = data.get("room_name")
        status = data.get("status", 0)

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT room_name FROM room_meeting WHERE room_name = %s", (
                room_name,)
        )
        existing_room = cursor.fetchone()

        if existing_room:
            return jsonify({"error": "Room already exists"}), 400

        cursor.execute(
            "INSERT INTO room_meeting (room_name, status) VALUES (%s, %s)",
            (room_name, status),
        )
        conn.commit()
        return jsonify({"message": "Room created successfully"})
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        cursor.close()
        conn.close()


@room_api.route("/rooms/<int:room_id>", methods=["PUT"])
def update_room(room_id):
    try:
        data = request.get_json()
        room_name = data.get("room_name")

        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT room_name FROM room_meeting WHERE room_id != %s AND room_name = %s",
            (room_id, room_name),
        )
        existing_room = cursor.fetchone()

        if existing_room:
            return jsonify({"error": "Room name already exists"}), 400

        cursor.execute(
            "UPDATE room_meeting SET room_name=%s WHERE room_id=%s",
            (room_name, room_id),
        )
        conn.commit()
        return jsonify({"message": "Room updated successfully"})
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        cursor.close()
        conn.close()


@room_api.route("/rooms/<int:room_id>", methods=["DELETE"])
def delete_room(room_id):
    try:
        conn = create_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM room_meeting WHERE room_id=%s", (room_id,))
        conn.commit()
        return jsonify({"message": "Room deleted successfully"})
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        cursor.close()
        conn.close()


@room_api.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404
