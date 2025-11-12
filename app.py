from flask import Flask, jsonify
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'visitordb')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

def get_db_connection():
    """Create database connection"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def init_db():
    """Initialize database table"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id SERIAL PRIMARY KEY,
                visit_time TIMESTAMP NOT NULL,
                ip_address VARCHAR(50)
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "message": "Welcome to the Visitor Counter API By @A1samka",
        "endpoints": {
            "/": "This help message",
            "/visit": "Record a visit",
            "/count": "Get total visit count",
            "/health": "Health check"
        }
    })

@app.route('/visit', methods=['POST'])
def record_visit():
    """Record a new visit"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO visitors (visit_time, ip_address) VALUES (%s, %s)',
            (datetime.now(), 'unknown')
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Visit recorded"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/count')
def get_count():
    """Get total visitor count"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM visitors')
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({"total_visits": count})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)