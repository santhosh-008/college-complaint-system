import io
import sqlite3
from app import app
from database import DB_PATH, init_db

def run_tests():
    print("==================================================")
    print("STARTING COMPREHENSIVE END-TO-END TESTS")
    print("==================================================")

    init_db()
    client = app.test_client()

    # 1. Test Home Page Redirect
    res = client.get('/', follow_redirects=True)
    assert res.status_code == 200
    assert b"Sign In" in res.data or b"Nandha Engineering College" in res.data
    print("[PASS] 1. Root route redirects to login page correctly.")

    # 2. Test Invalid Student Login
    res = client.post('/login', data={
        'login_type': 'student',
        'identifier': 'STU001',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Invalid Student ID or password" in res.data
    print("[PASS] 2. Invalid student password rejected with error alert.")

    # 3. Test Invalid Admin Login
    res = client.post('/login', data={
        'login_type': 'admin',
        'identifier': 'admin',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Invalid Admin username or password" in res.data
    print("[PASS] 3. Invalid admin password rejected with error alert.")

    # 4. Test Valid Student Login (STU001 / student123)
    res = client.post('/login', data={
        'login_type': 'student',
        'identifier': 'STU001',
        'password': 'student123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome back, Santhosh Kumar!" in res.data
    assert b"Student Dashboard" in res.data
    print("[PASS] 4. Valid student login successful; redirected to Student Dashboard.")

    # 5. Test Unauthorized Admin Access by Student
    res = client.get('/admin/dashboard', follow_redirects=True)
    assert res.status_code == 200
    assert b"Access denied" in res.data or b"Student Dashboard" in res.data
    print("[PASS] 5. Role protection prevents student from accessing Admin Dashboard.")

    # 6. Test Submit New Complaint by Student (with attachment)
    dummy_file = (io.BytesIO(b"Sample attachment log data for testing."), "network_report.txt")
    res = client.post('/student/submit', data={
        'title': 'Autonomous Exam Cell Hall Ticket Printing Delay',
        'category': 'Academic',
        'department': 'Computer Science & Engineering',
        'priority': 'High',
        'description': 'Students are unable to print hall tickets for semester examination from the portal.',
        'attachment': dummy_file
    }, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    assert b"Complaint submitted successfully" in res.data
    print("[PASS] 6. Complaint submitted with attachment; received confirmation message.")

    # 7. Verify Complaint in SQLite Database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE title = ? ORDER BY id DESC LIMIT 1", ('Autonomous Exam Cell Hall Ticket Printing Delay',))
    new_comp = cursor.fetchone()
    assert new_comp is not None
    new_comp_id = new_comp['complaint_id']
    assert new_comp['status'] == 'Pending'
    assert new_comp['priority'] == 'High'
    assert new_comp['attachment'] is not None
    conn.close()
    print(f"[PASS] 7. Complaint verified in SQLite database: ID {new_comp_id}, Status: Pending.")

    # 8. Test "My Complaints" Page for Student
    res = client.get('/student/complaints')
    assert res.status_code == 200
    assert new_comp_id.encode() in res.data
    assert b"Autonomous Exam Cell Hall Ticket Printing Delay" in res.data
    print(f"[PASS] 8. Complaint {new_comp_id} appears in 'My Complaints'.")

    # 9. Test Student Logout
    res = client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
    assert b"You have been signed out successfully" in res.data
    print("[PASS] 9. Student logout completed successfully.")

    # 10. Test Valid Admin Login (admin / admin123)
    res = client.post('/login', data={
        'login_type': 'admin',
        'identifier': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Grievance Redressal Board" in res.data
    print("[PASS] 10. Admin login successful; redirected to Administrator Dashboard.")

    # 11. Verify Complaint Appears on Admin Board
    res = client.get('/admin/dashboard')
    assert res.status_code == 200
    assert new_comp_id.encode() in res.data
    print(f"[PASS] 11. Complaint {new_comp_id} listed on Admin Complaints Board.")

    # 12. View Complaint Details as Admin
    res = client.get(f'/complaint/{new_comp_id}')
    assert res.status_code == 200
    assert b"Administrative Actions & Status Update" in res.data
    assert b"Santhosh Kumar" in res.data
    print(f"[PASS] 12. Complaint details page rendered for Admin with student information.")

    # 13 & 14. Admin Updates Status to 'In Progress' and Adds Response
    admin_reply_text = "Controller of Examinations contacted. Server cache cleared; printing restored."
    res = client.post(f'/admin/complaints/{new_comp_id}/update', data={
        'status': 'In Progress',
        'admin_response': admin_reply_text
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"updated to &#39;In Progress&#39; successfully" in res.data or b"In Progress" in res.data
    print(f"[PASS] 13 & 14. Admin updated complaint status to 'In Progress' with response remarks.")

    # Verify update in DB
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT status, admin_response FROM complaints WHERE complaint_id = ?", (new_comp_id,))
    updated_row = cursor.fetchone()
    assert updated_row['status'] == 'In Progress'
    assert updated_row['admin_response'] == admin_reply_text
    conn.close()
    print("[PASS] Verified updated status and admin response in SQLite.")

    # 15. Admin Logout
    res = client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
    print("[PASS] 15. Admin logout completed.")

    # 16 & 17. Student Logs in and Verifies Updated Status and Admin Response
    res = client.post('/login', data={
        'login_type': 'student',
        'identifier': 'STU001',
        'password': 'student123'
    }, follow_redirects=True)
    assert res.status_code == 200

    res = client.get(f'/complaint/{new_comp_id}')
    assert res.status_code == 200
    assert b"In Progress" in res.data
    assert admin_reply_text.encode() in res.data
    print(f"[PASS] 16 & 17. Student successfully viewed updated 'In Progress' status and Admin reply: '{admin_reply_text}'.")

    # 18. Admin Marks Complaint as Resolved
    client.get('/logout', follow_redirects=True)
    client.post('/login', data={
        'login_type': 'admin',
        'identifier': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)

    res = client.post(f'/admin/complaints/{new_comp_id}/update', data={
        'status': 'Resolved',
        'admin_response': "All students confirmed issue resolved. Ticket marked closed."
    }, follow_redirects=True)
    assert res.status_code == 200

    # Verify student directory view
    res = client.get('/admin/students')
    assert res.status_code == 200
    assert b"Student Directory" in res.data
    assert b"STU001" in res.data
    print("[PASS] 18. Student directory page verified.")

    # 19. Clean up / Final logout
    client.get('/logout', follow_redirects=True)
    print("[PASS] 19. Final logout completed.")

    print("==================================================")
    print("ALL 19 AUTOMATED TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == '__main__':
    run_tests()
