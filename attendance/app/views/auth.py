from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import students_collection, professors_collection

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role')
    department = request.json.get('department')  # New field for both students and professors
    year = request.json.get('year')  # New field for students only
    admission_no = request.json.get('admission_no')  # Only for students

    if not username or not password or not role:
        return jsonify({"error": "Username, password, and role are required!"}), 400

    if role not in ['student', 'professor']:
        return jsonify({"error": "Invalid role!"}), 400

    hashed_password = generate_password_hash(password)

    if role == 'student':
        if not admission_no or not department or not year:
            return jsonify({"error": "Admission number, department, and year are required for students!"}), 400
        if students_collection.find_one({'username': username}):
            return jsonify({"error": "Username already exists for a student!"}), 400

        students_collection.insert_one({
            'username': username,
            'password': hashed_password,
            'admission_no': admission_no,
            'department': department,
            'year': year
        })

    elif role == 'professor':
        if not department:
            return jsonify({"error": "Department is required for professors!"}), 400
        if professors_collection.find_one({'username': username}):
            return jsonify({"error": "Username already exists for a professor!"}), 400

        professors_collection.insert_one({
            'username': username,
            'password': hashed_password,
            'department': department
        })

    session['username'] = username
    session['role'] = role
    if role == 'student':
        session['admission_no'] = admission_no
        session['department'] = department
        session['year'] = year
    else:
        session['department'] = department

    return jsonify({"message": f"{role.capitalize()} registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required!"}), 400

    # Check if the user is a student
    user = students_collection.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        session['username'] = username
        session['admission_no'] = user['admission_no']
        session['department'] = user['department']
        session['year'] = user['year']
        session['role'] = 'student'
        return jsonify({"message": "Student logged in successfully"}), 200

    # Check if the user is a professor
    user = professors_collection.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        session['username'] = username
        session['department'] = user['department']
        session['role'] = 'professor'
        return jsonify({"message": "Professor logged in successfully"}), 200

    # If no matching user is found
    return jsonify({"error": "Invalid username or password!"}), 401
