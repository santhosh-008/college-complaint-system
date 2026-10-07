import os
import uuid
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort, send_from_directory
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'nandha_engg_college_complaint_portal_2026_secure_key')

# Uploads configuration
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB max upload

# Ensure uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Predefined college categories and departments
CATEGORIES = [
    "Academic",
    "Infrastructure",
    "Hostel",
    "Transport",
    "Canteen",
    "Library",
    "Internet/Wi-Fi",
    "Faculty",
    "Other"
]

DEPARTMENTS = [
    "Computer Science & Engineering",
    "Electronics & Communication Engineering",
    "Electrical & Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Information Technology",
    "Artificial Intelligence & Data Science",
    "Biomedical Engineering",
    "Campus Maintenance",
    "Hostel Administration",
    "Transport Department"
]

PRIORITIES = ["Low", "Medium", "High", "Urgent"]
STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------------------
# Authentication Decorators
# -------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in as a student.", "warning")
            return redirect(url_for('login'))
        if session.get('role') != 'student':
            flash("Access restricted. Student credentials required.", "danger")
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in with administrator credentials.", "warning")
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash("Access denied. Administrator privileges required.", "danger")
            return redirect(url_for('student_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_global_data():
    """Inject college portal constants into all templates."""
    return {
        'college_name': 'Nandha Engineering College',
        'college_short': 'NEC',
        'portal_title': 'College Complaint System',
        'categories': CATEGORIES,
        'departments': DEPARTMENTS,
        'priorities': PRIORITIES,
        'statuses': STATUSES,
        'current_year': datetime.now().year
    }


# -------------------------------------------------------------
# Core & Auth Routes
# -------------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))

    active_tab = request.args.get('tab', 'student')

    if request.method == 'POST':
        login_type = request.form.get('login_type', 'student').strip()
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()

        active_tab = login_type

        if not identifier or not password:
            flash("Please enter both ID/Username and Password.", "danger")
            return render_template('login.html', active_tab=active_tab, identifier=identifier)

        conn = get_db_connection()
        cursor = conn.cursor()

        if login_type == 'student':
            cursor.execute('''
                SELECT * FROM users
                WHERE (UPPER(student_id) = UPPER(?) OR UPPER(username) = UPPER(?)) AND role = 'student'
            ''', (identifier, identifier))
            user = cursor.fetchone()
        else:
            cursor.execute('''
                SELECT * FROM users
                WHERE UPPER(username) = UPPER(?) AND role = 'admin'
            ''', (identifier,))
            user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            conn.close()
            # Login successful
            session.clear()
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['username'] = user['username']
            session['student_id'] = user['student_id']
            session['role'] = user['role']
            session['department'] = user['department']
            session['email'] = user['email']

            flash(f"Welcome back, {user['name']}!", "success")
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            # Check if user entered credentials for the alternate tab (e.g., admin on student tab)
            if login_type == 'student':
                cursor.execute('''
                    SELECT * FROM users WHERE UPPER(username) = UPPER(?) AND role = 'admin'
                ''', (identifier,))
                cross_user = cursor.fetchone()
                if cross_user and check_password_hash(cross_user['password_hash'], password):
                    conn.close()
                    flash("These are Administrator credentials. Please switch to the 'Admin Login' tab to sign in.", "warning")
                    return render_template('login.html', active_tab='admin', identifier=identifier)
            else:
                cursor.execute('''
                    SELECT * FROM users
                    WHERE (UPPER(student_id) = UPPER(?) OR UPPER(username) = UPPER(?)) AND role = 'student'
                ''', (identifier, identifier))
                cross_user = cursor.fetchone()
                if cross_user and check_password_hash(cross_user['password_hash'], password):
                    conn.close()
                    flash("These are Student credentials. Please switch to the 'Student Login' tab to sign in.", "warning")
                    return render_template('login.html', active_tab='student', identifier=identifier)

            conn.close()

            if login_type == 'student':
                flash("Invalid Student ID or password. Try demo Student ID: STU001 / student123", "danger")
            else:
                flash("Invalid Admin username or password. Try demo username: admin / admin123", "danger")

            return render_template('login.html', active_tab=active_tab, identifier=identifier)

    return render_template('login.html', active_tab=active_tab)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('login'))


# -------------------------------------------------------------
# Student Portal Routes
# -------------------------------------------------------------
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = session['user_id']

    # Total counts for current student
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE user_id = ?", (user_id,))
    total_complaints = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE user_id = ? AND status = 'Pending'", (user_id,))
    pending_complaints = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE user_id = ? AND status = 'In Progress'", (user_id,))
    in_progress_complaints = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE user_id = ? AND status = 'Resolved'", (user_id,))
    resolved_complaints = cursor.fetchone()[0]

    # Recent complaints
    cursor.execute('''
        SELECT * FROM complaints
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    ''', (user_id,))
    recent_complaints = cursor.fetchall()

    conn.close()

    stats = {
        'total': total_complaints,
        'pending': pending_complaints,
        'in_progress': in_progress_complaints,
        'resolved': resolved_complaints
    }

    return render_template('student_dashboard.html', stats=stats, recent_complaints=recent_complaints)


@app.route('/student/submit', methods=['GET', 'POST'])
@student_required
def submit_complaint():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        department = request.form.get('department', '').strip()
        priority = request.form.get('priority', 'Medium').strip()
        description = request.form.get('description', '').strip()

        # Validation
        if not title:
            flash("Please enter a complaint title.", "danger")
            return render_template('submit_complaint.html')
        if not category or category not in CATEGORIES:
            flash("Please select a valid complaint category.", "danger")
            return render_template('submit_complaint.html')
        if not department:
            flash("Please select your department.", "danger")
            return render_template('submit_complaint.html')
        if not priority or priority not in PRIORITIES:
            priority = "Medium"
        if not description:
            flash("Please provide a detailed description of your complaint.", "danger")
            return render_template('submit_complaint.html')

        # Handle file attachment
        attachment_filename = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Unique prefix to avoid collision
                    unique_name = f"{int(datetime.now().timestamp())}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
                    attachment_filename = unique_name
                else:
                    flash("Invalid file format. Allowed: images (png, jpg), pdf, doc, txt.", "danger")
                    return render_template('submit_complaint.html')

        # Generate unique complaint ID: NEC-YYYY-XXXX
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM complaints")
        total_count = cursor.fetchone()[0] + 1001
        year = datetime.now().year
        complaint_id = f"NEC-{year}-{total_count:04d}"

        # Ensure unique complaint_id
        while True:
            cursor.execute("SELECT id FROM complaints WHERE complaint_id = ?", (complaint_id,))
            if not cursor.fetchone():
                break
            total_count += 1
            complaint_id = f"NEC-{year}-{total_count:04d}"

        cursor.execute('''
            INSERT INTO complaints (
                complaint_id, user_id, title, category, department, priority,
                description, attachment, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', datetime('now'), datetime('now'))
        ''', (
            complaint_id, session['user_id'], title, category, department, priority,
            description, attachment_filename
        ))

        conn.commit()
        conn.close()

        flash(f"Complaint submitted successfully! Your tracking ID is {complaint_id}.", "success")
        return redirect(url_for('complaint_details', complaint_id=complaint_id))

    return render_template('submit_complaint.html')


@app.route('/student/complaints')
@student_required
def my_complaints():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM complaints
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    complaints = cursor.fetchall()
    conn.close()

    return render_template('my_complaints.html', complaints=complaints)


# -------------------------------------------------------------
# Common Complaint Details Route
# -------------------------------------------------------------
@app.route('/complaint/<complaint_id>')
@login_required
def complaint_details(complaint_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT c.*, u.name as student_name, u.student_id, u.email as student_email,
               u.phone as student_phone, u.department as student_department
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        WHERE c.complaint_id = ?
    ''', (complaint_id,))
    complaint = cursor.fetchone()
    conn.close()

    if not complaint:
        flash("Complaint not found.", "danger")
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('my_complaints'))

    # If student, verify this complaint belongs to them
    if session.get('role') == 'student' and complaint['user_id'] != session['user_id']:
        flash("Unauthorized access to this complaint.", "danger")
        return redirect(url_for('my_complaints'))

    return render_template('complaint_details.html', complaint=complaint)


# -------------------------------------------------------------
# Admin Portal Routes
# -------------------------------------------------------------
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Metrics
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total_complaints = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'")
    pending_complaints = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
    in_progress_complaints = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
    resolved_complaints = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Rejected'")
    rejected_complaints = cursor.fetchone()[0]

    # Complaints list with joined student information
    cursor.execute('''
        SELECT c.*, u.name as student_name, u.student_id, u.email as student_email,
               u.department as student_dept
        FROM complaints c
        JOIN users u ON c.user_id = u.id
        ORDER BY
            CASE c.status
                WHEN 'Pending' THEN 1
                WHEN 'In Progress' THEN 2
                WHEN 'Resolved' THEN 3
                WHEN 'Rejected' THEN 4
                ELSE 5
            END,
            c.created_at DESC
    ''')
    all_complaints = cursor.fetchall()

    conn.close()

    stats = {
        'total': total_complaints,
        'pending': pending_complaints,
        'in_progress': in_progress_complaints,
        'resolved': resolved_complaints,
        'rejected': rejected_complaints
    }

    return render_template('admin_dashboard.html', stats=stats, complaints=all_complaints)


@app.route('/admin/complaints/<complaint_id>/update', methods=['POST'])
@admin_required
def update_complaint_status(complaint_id):
    status = request.form.get('status', '').strip()
    admin_response = request.form.get('admin_response', '').strip()

    if status not in STATUSES:
        flash("Invalid status selected.", "danger")
        return redirect(url_for('complaint_details', complaint_id=complaint_id))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE complaints
        SET status = ?, admin_response = ?, updated_at = datetime('now')
        WHERE complaint_id = ?
    ''', (status, admin_response, complaint_id))

    conn.commit()
    conn.close()

    flash(f"Complaint {complaint_id} status updated to '{status}' successfully.", "success")
    return redirect(url_for('complaint_details', complaint_id=complaint_id))


@app.route('/admin/complaints/<complaint_id>/delete', methods=['POST'])
@admin_required
def delete_complaint(complaint_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check and delete attachment if exists
    cursor.execute("SELECT attachment FROM complaints WHERE complaint_id = ?", (complaint_id,))
    row = cursor.fetchone()
    if row and row['attachment']:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], row['attachment'])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

    cursor.execute("DELETE FROM complaints WHERE complaint_id = ?", (complaint_id,))
    conn.commit()
    conn.close()

    flash(f"Complaint {complaint_id} has been permanently deleted.", "info")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/students')
@admin_required
def admin_students():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT u.*, COUNT(c.id) as total_complaints,
               SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count
        FROM users u
        LEFT JOIN complaints c ON u.id = c.user_id
        WHERE u.role = 'student'
        GROUP BY u.id
        ORDER BY u.student_id ASC
    ''')
    students = cursor.fetchall()
    conn.close()

    return render_template('admin_students.html', students=students)


# -------------------------------------------------------------
# Static File Downloads
# -------------------------------------------------------------
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# -------------------------------------------------------------
# Error Handlers
# -------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
