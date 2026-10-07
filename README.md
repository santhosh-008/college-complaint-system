# Nandha Engineering College – College Complaint Management System

A simple, modern, professional, and fully functional Web-Based Student Grievance Redressal and Complaint Management Portal built for **Nandha Engineering College (Autonomous), Erode, Tamil Nadu**.

---

## 📌 Project Overview

The **College Complaint Management System** allows students to register academic and campus grievances with categories, priority levels, and optional attachments. Students can monitor the status of their complaints in real-time, view official administrative remarks, and print complaint records. 

Administrators have access to a dedicated Complaints Board equipped with live filtering, analytical KPI counters, status transition controls (Pending &rarr; In Progress &rarr; Resolved / Rejected), response publishing, and record management.

---

## 🛠️ Technology Stack

- **Frontend:**
  - HTML5 (Semantic Structure)
  - Vanilla CSS3 (Custom responsive design system, college brand theme, status pills, KPI cards, zero external bulky frameworks)
  - JavaScript (ES6+, real-time live table search & filtering, form validation, demo credential auto-filler)
  - Google Fonts: Plus Jakarta Sans
  - Custom SVG College Crest Logo

- **Backend:**
  - Python 3.12+
  - Flask (Lightweight WSGI Web Framework)
  - Werkzeug (Secure password hashing via PBKDF2:SHA256, secure file handling)

- **Database:**
  - SQLite 3 (Lightweight relational database with foreign key constraints)

---

## 📂 Project Structure

```
c:\Users\ELCOT\OneDrive\Desktop\santhosh/
├── app.py                      # Main Flask application with routes and controllers
├── database.py                 # SQLite database schema, initialization & seed data
├── database.db                 # Auto-generated SQLite database
├── requirements.txt            # Python dependencies (Flask, Werkzeug)
├── README.md                   # Complete documentation and setup instructions
├── static/
│   ├── css/
│   │   └── style.css           # Modern, responsive college theme stylesheet
│   ├── js/
│   │   └── script.js           # Client-side filtering, tabs, autofill & validation
│   ├── images/
│   │   └── nec_logo.svg        # Nandha Engineering College crest emblem
│   └── uploads/                # Directory for student complaint file attachments
└── templates/
    ├── base.html               # Base layout with college header, nav & footer
    ├── login.html              # Login portal with Student/Admin role switcher
    ├── student_dashboard.html  # Student overview with KPI stats & recent issues
    ├── submit_complaint.html   # Grievance registration form with file upload
    ├── my_complaints.html      # Student's complaint history with live filters
    ├── complaint_details.html  # Comprehensive details, tracker & admin actions
    ├── admin_dashboard.html    # Admin management board with stats & filters
    ├── admin_students.html     # Student directory with grievance counts
    ├── 404.html                # Not Found error page
    └── 500.html                # Server error page
```

---

## 🔑 Demo Login Credentials

The database comes pre-seeded with sample accounts for immediate testing:

### 1. Student Account
- **Role:** Student
- **Student ID:** `STU001`
- **Password:** `student123`
- *Student Name:* Santhosh Kumar (Dept: Computer Science & Engineering)

*Secondary Student Account:*
- **Student ID:** `STU002`
- **Password:** `student123`
- *Student Name:* Priya Dharshini (Dept: Electronics & Communication Engineering)

### 2. Administrator Account
- **Role:** Administrator (Grievance Redressal Cell)
- **Username:** `admin`
- **Password:** `admin123`
- *Admin Name:* Chief Grievance Officer

*(Tip: The login page includes 1-click **"Auto-fill"** buttons for both Student and Admin credentials).*

---

## 🚀 Installation & Running Guide

### Step 1: Open Terminal / Command Prompt
Navigate to the project root directory:
```bash
cd c:\Users\ELCOT\OneDrive\Desktop\santhosh
```

### Step 2: Install Dependencies
Ensure Python 3.10+ is installed, then run:
```bash
pip install -r requirements.txt
```

### Step 3: Initialize the Database (Optional / Automatic)
The database will be automatically initialized when running `app.py`. You can also manually initialize it:
```bash
python database.py
```

### Step 4: Run the Application
Start the Flask development server:
```bash
python app.py
```

### Step 5: Access the Web Portal
Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 🔄 How the System Works

1. **Authentication & Session Security:**
   - Both students and administrators authenticate via `/login`.
   - Passwords are encrypted using salted PBKDF2:SHA256 hashes.
   - Role-based route decorators (`@student_required`, `@admin_required`) ensure strict access isolation.

2. **Student Workflow:**
   - Students log in using their `Student ID` (e.g., `STU001`).
   - From the **Student Dashboard**, they can view their grievance summary (Total, Pending, In Progress, Resolved).
   - Under **Submit Complaint**, they lodge issues with a title, category, department, priority level, description, and optional file attachments (images, PDFs, documents).
   - A unique tracking ID formatted as `NEC-YYYY-XXXX` is automatically generated.
   - Under **My Complaints**, they can search, filter, and track statuses or read official administrator replies.

3. **Administrator Workflow:**
   - Administrators log in using their `Username` (`admin`).
   - The **Complaints Board** displays college-wide metrics and a complaints table with live filtering across Status, Category, Priority, and Department.
   - Administrators open any complaint to inspect full student and grievance details, update its status (`Pending` &rarr; `In Progress` &rarr; `Resolved` / `Rejected`), and submit official resolution remarks.
   - Admins can also manage records or delete invalid complaints.
