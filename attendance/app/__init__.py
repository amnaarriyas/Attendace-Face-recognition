from flask import Flask
from pymongo import MongoClient

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['attendance_system']

# Import blueprints
from app.views.auth import auth_bp
from app.views.attendance import attendance_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(attendance_bp, url_prefix='/attendance')
