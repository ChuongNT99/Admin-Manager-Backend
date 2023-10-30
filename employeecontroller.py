import  mysql.connector
from flask import *
from flask_cors import CORS
from db_config import db_config

app=Flask(__name__)

employee_api = Blueprint("employeecontroller", __name__)

@employee_api.route('/employee', methods=['POST', 'GET'])
def data():
    if request.method=='GET':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM employees")
            rows = cursor.fetchall()
            return jsonify({'employee': rows})
        except Exception as e:
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            cursor.close()
            conn.close()
    if request.method=='POST':   
        try:
            _json=request.json
            _employees_name=_json['employees_name']
            _email=_json['email']
            _phone_number=_json['phone_number']
            conn = mysql.connector.connect(**db_config)
            cursor=conn.cursor()
            cursor.execute("INSERT INTO employees(employees_name,email,phone_number) VALUES(%s,%s,%s)",(_employees_name,_email,_phone_number))
            conn.commit()  
            return jsonify({"message": "Created employee successfully"})
        except Exception as e:
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            cursor.close()
            conn.close()
@employee_api.route('/employee/<int:employees_id>',methods=[ 'DELETE', 'PUT'])
def employee_one(employees_id):
    
    if request.method=='PUT':
        try:
            _json = request.json
            _employee_name = _json['employees_name']
            _email=_json['email']
            _phone_number=_json['phone_number']
            conn = mysql.connector.connect(**db_config)
            cursor=conn.cursor()
            query = "UPDATE employees SET employees_name=%s, email=%s, phone_number=%s WHERE employees_id=%s" 
            cursor.execute(query, (_employee_name,_email,_phone_number,employees_id))
            conn.commit()  
            return jsonify({"message": "Update employee successfully"})
        except Exception as e:
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            cursor.close()
            conn.close()

    if request.method=='DELETE':
        try:    
            conn=mysql.connector.connect(**db_config)
            cursor=conn.cursor()
            cursor.execute("DELETE FROM employees WHERE employees_id =%s",(employees_id,))
            conn.commit()
            return jsonify({"message": "Delete employee successfully"})
        except Exception as e:
            return jsonify({'error': 'Internal Server Error'}), 500
        finally:
            cursor.close()
            conn.close()   
   
        