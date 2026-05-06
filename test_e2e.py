import json
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.models.employee import Employee
from app.auth.jwt_handler import get_password_hash

# Set up test database
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Add admin user manually since POST /auth/register should be tested
db = SessionLocal()
admin = Employee(
    name="Test Admin",
    email="admin@test.com",
    password_hash=get_password_hash("admin123"),
    role="ADMIN",
    work_type="Office",
    salary_type="monthly",
    salary_amount=0.0
)
db.add(admin)
db.commit()
db.refresh(admin)
db.close()

client = TestClient(app)

def run_tests():
    results = {"pass": 0, "fail": 0, "errors": []}
    
    def assert_eq(actual, expected, test_name):
        if actual == expected:
            results["pass"] += 1
            print(f"PASS: {test_name}")
        else:
            results["fail"] += 1
            msg = f"FAIL: {test_name} - Expected {expected}, got {actual}"
            results["errors"].append(msg)
            print(msg)

    # 1. Auth Testing
    # Admin login
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "admin123"})
    assert_eq(res.status_code, 200, "Admin Login with valid credentials")
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Invalid login
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    assert_eq(res.status_code, 400, "Login with invalid credentials")

    # Access without token
    res = client.get("/employees/")
    assert_eq(res.status_code, 403, "Access protected API without token (FastAPI HTTPBearer returns 403 when not provided usually)")
    
    # Register EMPLOYEE via admin
    res = client.post("/auth/register", json={
        "name": "John Employee",
        "email": "emp@test.com",
        "password": "emp",
        "role": "EMPLOYEE",
        "work_type": "Office",
        "salary_type": "monthly",
        "salary_amount": 30000.0
    })
    # Wait, /auth/register doesn't have require_admin! Let's check what it returns
    emp_id = res.json()["id"]
    assert_eq(res.status_code, 201, "Register EMPLOYEE")
    
    # Employee Login
    res = client.post("/auth/login", json={"email": "emp@test.com", "password": "emp"})
    emp_token = res.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    
    # 2. RBAC Testing
    # Employee views all employees (Should fail)
    res = client.get("/employees/", headers=emp_headers)
    assert_eq(res.status_code, 403, "Employee cannot view all employees")
    
    # Admin views all employees (Should pass)
    res = client.get("/employees/", headers=admin_headers)
    assert_eq(res.status_code, 200, "Admin can view all employees")
    
    # Employee marks own attendance
    res = client.post("/attendance/", headers=emp_headers, json={
        "employee_id": emp_id,
        "date": "2026-05-01",
        "status": "present"
    })
    assert_eq(res.status_code, 201, "Employee marks own attendance")
    
    # Prevent duplicate attendance
    res = client.post("/attendance/", headers=emp_headers, json={
        "employee_id": emp_id,
        "date": "2026-05-01",
        "status": "present"
    })
    assert_eq(res.status_code, 409, "Prevent duplicate attendance")
    
    # Employee tries to mark admin attendance (Should fail)
    res = client.post("/attendance/", headers=emp_headers, json={
        "employee_id": 1,
        "date": "2026-05-02",
        "status": "present"
    })
    assert_eq(res.status_code, 403, "Employee cannot mark other attendance")

    # Employee applies leave
    res = client.post("/leave/", headers=emp_headers, json={
        "employee_id": emp_id,
        "start_date": "2026-05-10",
        "end_date": "2026-05-11"
    })
    leave_id = res.json()["id"]
    assert_eq(res.status_code, 201, "Employee applies leave")
    assert_eq(res.json()["status"], "pending", "Leave status is pending")
    
    # Invalid leave dates
    res = client.post("/leave/", headers=emp_headers, json={
        "employee_id": emp_id,
        "start_date": "2026-05-15",
        "end_date": "2026-05-10"
    })
    assert_eq(res.status_code, 400, "Leave date validation (start < end)")
    
    # Admin views leaves
    res = client.get("/leave/", headers=admin_headers)
    assert_eq(len(res.json()), 1, "Admin views all leaves")
    
    # Admin approves leave
    res = client.put(f"/leave/{leave_id}", headers=admin_headers, json={"status": "approved"})
    assert_eq(res.status_code, 200, "Admin approves leave")
    
    # Payroll Test: Monthly Employee
    # Present = 1, Approved Leave = 2 days (10th to 11th). Total effective = 3.
    # Salary = 30000. Per day = 1000. Expected salary = 3000.
    res = client.get(f"/payroll/{emp_id}", headers=emp_headers)
    assert_eq(res.status_code, 200, "Employee views own payroll")
    payroll_data = res.json()
    assert_eq(payroll_data["present_days"], 1, "Present days count")
    assert_eq(payroll_data["approved_leave_days"], 2, "Approved leave days count")
    assert_eq(payroll_data["salary"], 3000.0, "Monthly payroll calculation")
    
    # Register Daily Wage Employee
    res = client.post("/auth/register", json={
        "name": "Daily Employee",
        "email": "daily@test.com",
        "password": "emp",
        "role": "EMPLOYEE",
        "work_type": "On-site",
        "salary_type": "daily",
        "salary_amount": 500.0
    })
    daily_id = res.json()["id"]
    
    # Mark attendance for Daily
    client.post("/attendance/bulk", headers=admin_headers, json={
        "date": "2026-05-01",
        "entries": [
            {"employee_id": daily_id, "status": "present"}
        ]
    })
    
    # Daily Wage Payroll calculation
    res = client.get(f"/payroll/{daily_id}", headers=admin_headers)
    assert_eq(res.json()["salary"], 500.0, "Daily payroll calculation")
    
    # Employee tries to view another employee's payroll
    res = client.get(f"/payroll/{daily_id}", headers=emp_headers)
    assert_eq(res.status_code, 403, "Employee trying to access another's payroll")
    
    print("\n--- TEST SUMMARY ---")
    print(f"Passed: {results['pass']}")
    print(f"Failed: {results['fail']}")
    for err in results["errors"]:
        print(err)

run_tests()
