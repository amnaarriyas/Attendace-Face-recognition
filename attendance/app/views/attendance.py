from flask import Blueprint, jsonify, request, session
from datetime import datetime
from app.database import students_collection, attendance_collection

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/add', methods=['POST'])
def add_attendance():
    data = request.json
    admission_no = data.get('admission_no')
    class_date = data.get('class_date', datetime.now().strftime("%d-%m-%Y"))
  #  periods_attended = data.get('periods')

    student = students_collection.find_one({"admission_no": admission_no})
    if not student:
        return jsonify({"error": "Student not found!"}), 404

    attendance_data = {
        "admission_no": admission_no,
        "class_date": class_date,
        #  "periods": periods_attended,
        "department": student['department'],  # Add department
        "year": student['year']  # Add year
    }
    attendance_collection.insert_one(attendance_data)
    return jsonify({"message": "Attendance recorded successfully"}), 201

@attendance_bp.route('/percentage', methods=['GET'])
def calculate_percentage():
    # Get the student's details from the session
    admission_no = session.get('admission_no')
    if not admission_no:
        return jsonify({"error": "Unauthorized!"}), 401

    # Find the student by their admission number
    student = students_collection.find_one({"admission_no": admission_no})
    if not student:
        return jsonify({"error": "Student not found!"}), 404

    department = student['department']
    year = student['year']

    # Calculate total classes for the department and year
    total_classes = attendance_collection.distinct("class_date")
    total_days = len(total_classes)

    # Calculate the number of classes attended by the student
    attended_classes = attendance_collection.count_documents({
        "admission_no": admission_no,
        "department": department,
        "year": year
    })

    # Handle case where no classes have been recorded yet
    if total_days == 0:
        return jsonify({"percentage": 0, "message": "No classes recorded for your department and year"}), 200

    # Calculate the attendance percentage
    percentage = (attended_classes / total_days) * 100

    return jsonify({
        "admission_no": admission_no,
        "department": department,
        "year": year,
        "total_classes": total_days,
        "attended_classes": attended_classes,
        "percentage": round(percentage, 2)
    }), 200



@attendance_bp.route('/student/view', methods=['GET'])
def student_view_attendance():
    if session.get('role') != 'student':
        return jsonify({"error": "Unauthorized access!"}), 401

    admission_no = session.get('admission_no')
    records = list(attendance_collection.find({"admission_no": admission_no}, {"_id": 0}))
    return jsonify(records), 200

@attendance_bp.route('/professor/view', methods=['GET'])
def professor_view_attendance():
    if session.get('role') != 'professor':
        return jsonify({"error": "Unauthorized access!"}), 401

    professor_department = session.get('department')
    year = request.args.get('year')  # Optional year filter

    # Fetch attendance for the professor's department
    query = {"department": professor_department}
    if year:
        query["year"] = year

    records = list(attendance_collection.find(query, {"_id": 0}))
    return jsonify(records), 200
