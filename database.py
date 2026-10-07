import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')


def get_db_connection():
    """Returns a SQLite connection with Row row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initializes database tables and populates initial sample data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT UNIQUE,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
            department TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create complaints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            department TEXT NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('Low', 'Medium', 'High', 'Urgent')),
            description TEXT NOT NULL,
            attachment TEXT,
            status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'In Progress', 'Resolved', 'Rejected')),
            admin_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Seed demo users if not present
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        # Default student: STU001 / student123
        hashed_stu1 = generate_password_hash("student123")
        cursor.execute('''
            INSERT INTO users (name, student_id, username, password_hash, role, department, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "Santhosh Kumar",
            "STU001",
            "STU001",
            hashed_stu1,
            "student",
            "Computer Science & Engineering",
            "santhosh.stu001@nandhaengg.org",
            "+91 98765 43210"
        ))
        stu1_id = cursor.lastrowid

        # Secondary student: STU002 / student123
        hashed_stu2 = generate_password_hash("student123")
        cursor.execute('''
            INSERT INTO users (name, student_id, username, password_hash, role, department, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "Priya Dharshini",
            "STU002",
            "STU002",
            hashed_stu2,
            "student",
            "Electronics & Communication Engineering",
            "priya.stu002@nandhaengg.org",
            "+91 98421 87654"
        ))

        # Default admin: admin / admin123
        hashed_admin = generate_password_hash("admin123")
        cursor.execute('''
            INSERT INTO users (name, student_id, username, password_hash, role, department, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            "Chief Grievance Officer",
            None,
            "admin",
            hashed_admin,
            "admin",
            "Grievance Redressal Cell",
            "grievance@nandhaengg.org",
            "+91 4294 225588"
        ))

        # Seed initial realistic complaints for immediate dashboard testing
        cursor.execute('''
            INSERT INTO complaints (
                complaint_id, user_id, title, category, department, priority, description, status, admin_response, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-2 days'), datetime('now', '-1 days'))
        ''', (
            "NEC-2026-1001",
            stu1_id,
            "Poor Wi-Fi signal in Lab 3 (CSE Block)",
            "Internet/Wi-Fi",
            "Computer Science & Engineering",
            "High",
            "The wireless router in CSE 2nd floor Lab 3 frequently drops connections during practical sessions.",
            "In Progress",
            "Campus IT team has inspected the router. Access point replacement scheduled for tomorrow morning."
        ))

        cursor.execute('''
            INSERT INTO complaints (
                complaint_id, user_id, title, category, department, priority, description, status, admin_response, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-4 days'), datetime('now', '-2 days'))
        ''', (
            "NEC-2026-1002",
            stu1_id,
            "Water purifier leakage near Canteen Block B",
            "Infrastructure",
            "Campus Maintenance",
            "Medium",
            "Drinking water dispenser on the ground floor next to the student cafeteria has a continuous drip.",
            "Resolved",
            "Maintenance team replaced the valve gasket on 4th Oct. Tested and working cleanly now."
        ))

        conn.commit()
        print("Database initialized and sample data seeded successfully.")
    else:
        conn.commit()

    conn.close()


if __name__ == '__main__':
    init_db()
