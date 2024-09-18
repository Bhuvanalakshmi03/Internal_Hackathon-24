from flask import Flask
import sqlite3

# Initialize Flask app
app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('exam_registration.db')
    conn.row_factory = sqlite3.Row  # To get dict-like results
    return conn
