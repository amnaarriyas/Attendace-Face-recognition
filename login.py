from flask import Flask, request, jsonify, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["attendance_system"]  # Database name
students_collection = db['students']  # Collection name
professors_collection = db['professors']  # Collection name


# Route for student registration
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role')  # "student" or "teacher"
    admission_no = request.json.get('admission_no')  # Collect admission_no for students

    if not username or not password or not role:
        return jsonify({"error": "Username, password, and role are required!"}), 400

    # Check for valid role
    if role not in ['student', 'teacher']:
        return jsonify({"error": "Invalid role! Choose either 'student' or 'teacher'."}), 400

    if role == 'student' and students_collection.find_one({'username': username}):
        return jsonify({"error": "Username already exists in students!"}), 400
    if role == 'teacher' and professors_collection.find_one({'username': username}):
        return jsonify({"error": "Username already exists in teachers!"}), 400
    # Insert user with hashed password into the appropriate collection
    hashed_password = generate_password_hash(password)
    if role == 'student':
        if not admission_no:
            return jsonify({"error": "Admission number is required for students!"}), 400
        students_collection.insert_one({
            'username': username,
            'password': hashed_password,
            'admission_no': admission_no  # Save admission_no for students
        })
    else:
        professors_collection.insert_one({'username': username, 'password': hashed_password})

    # Start user session
    session['username'] = username
    session['role'] = role  # Store the role in the session
    if role == 'student':
        session['admission_no'] = admission_no  # Store admission_no in session for students
    return jsonify({"message": f"{role.capitalize()} registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role')  # "student" or "teacher"

    if not username or not password or not role:
        return jsonify({"error": "Username, password, and role are required!"}), 400

    # Check for valid role
    if role not in ['student', 'teacher']:
        return jsonify({"error": "Invalid role! Choose either 'student' or 'teacher'."}), 400

    # Check if username exists and password is correct
    if role == "student":
        user = students_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['admission_no'] = user['admission_no']
            session['role'] = 'student'
            return jsonify({"message": "Student logged in successfully"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    elif role == "professor":
        user = professors_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = 'professor'
            return jsonify({"message": "Professor logged in successfully"}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    else:

        return jsonify({"error": "Invalid credentials!"}), 401


# Route for the dashboard (only accessible if logged in)
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' not in session or 'role' not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    return jsonify({"message": f"Welcome, {session['username']}! You are logged in as a {session['role']}."}), 200


# Run the application
if __name__ == '__main__':
    app.run(debug=True)

