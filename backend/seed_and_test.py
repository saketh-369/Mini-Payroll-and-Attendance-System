import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Base, engine, SessionLocal
from app.models.employee import Employee
from app.auth.jwt_handler import get_password_hash

# 1. Clear database completely to start fresh for the test
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def run_full_test():
    # ---------------------------------------------------------
    # STEP 1: Seed Initial Data
    # ---------------------------------------------------------
    db = SessionLocal()
    admin = Employee(
        name="Test Admin",
        email="admin@test.com",
        password_hash=get_password_hash("Admin@123"),
        role="ADMIN",
        work_type="Office",
        salary_type="monthly",
        salary_amount=0.0
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()

    # Admin Login
    res = client.post("/auth/login", json={"email": "admin@test.com", "password": "Admin@123"})
    assert res.status_code == 200
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Create 3 Employees
    employees_data = [
        {"name": "Emp One", "email": "emp1@test.com", "password": "pass", "role": "EMPLOYEE", "work_type": "Office", "salary_type": "monthly", "salary_amount": 30000},
        {"name": "Emp Two", "email": "emp2@test.com", "password": "pass", "role": "EMPLOYEE", "work_type": "On-site", "salary_type": "daily", "salary_amount": 500},
        {"name": "Emp Three", "email": "emp3@test.com", "password": "pass", "role": "EMPLOYEE", "work_type": "Office", "salary_type": "monthly", "salary_amount": 45000},
    ]
    emp_ids = {}
    for emp in employees_data:
        res = client.post("/auth/register", json=emp)
        assert res.status_code == 201
        emp_ids[emp["email"]] = res.json()["id"]

    # ---------------------------------------------------------
    # STEP 2: Authentication Testing
    # ---------------------------------------------------------
    res = client.post("/auth/login", json={"email": "emp1@test.com", "password": "pass"})
    assert res.status_code == 200
    emp1_token = res.json()["access_token"]
    emp1_headers = {"Authorization": f"Bearer {emp1_token}"}
    
    # Invalid login
    res = client.post("/auth/login", json={"email": "emp1@test.com", "password": "wrong"})
    assert res.status_code == 400
    
    # Access without token
    res = client.get("/employees/")
    assert res.status_code in [401, 403]

    # ---------------------------------------------------------
    # STEP 3: Attendance Simulation
    # ---------------------------------------------------------
    # Add 15 days of attendance for emp1
    for i in range(1, 16):
        date_str = f"2026-05-{i:02d}"
        status = "present" if i <= 10 else "absent" # 10 present, 5 absent
        client.post("/attendance/", headers=emp1_headers, json={"employee_id": emp_ids["emp1@test.com"], "date": date_str, "status": status})
        
    # Duplicate attendance test
    res = client.post("/attendance/", headers=emp1_headers, json={"employee_id": emp_ids["emp1@test.com"], "date": "2026-05-01", "status": "present"})
    assert res.status_code == 409

    # Daily wage employee attendance (Emp 2) via Bulk Admin
    bulk_entries = []
    for i in range(1, 16):
        date_str = f"2026-05-{i:02d}"
        status = "present" if i <= 10 else "absent" # 10 present, 5 absent
        bulk_entries.append({"employee_id": emp_ids["emp2@test.com"], "status": status})
        client.post("/attendance/bulk", headers=admin_headers, json={"date": date_str, "entries": [{"employee_id": emp_ids["emp2@test.com"], "status": status}]})

    # ---------------------------------------------------------
    # STEP 4: Leave Workflow Simulation
    # ---------------------------------------------------------
    # Emp 1 applies leave for 2 days
    res = client.post("/leave/", headers=emp1_headers, json={
        "employee_id": emp_ids["emp1@test.com"], "start_date": "2026-05-16", "end_date": "2026-05-17"
    })
    assert res.status_code == 201
    leave_id = res.json()["id"]

    # Admin approves leave
    res = client.put(f"/leave/{leave_id}", headers=admin_headers, json={"status": "approved"})
    assert res.status_code == 200

    # ---------------------------------------------------------
    # STEP 5: Payroll Testing
    # ---------------------------------------------------------
    # Emp 1 (Monthly): Present = 10, Approved Leave = 2 -> Effective Present = 12
    # Salary = 30000. Per day = 1000. Expected: 12000.
    res = client.get(f"/payroll/{emp_ids['emp1@test.com']}", headers=emp1_headers)
    p1 = res.json()
    
    # Emp 2 (Daily): Present = 10, Approved Leave = 0 -> Effective = 10
    # Salary = 500/day. Expected: 5000.
    res = client.get(f"/payroll/{emp_ids['emp2@test.com']}", headers=admin_headers)
    p2 = res.json()

    # ---------------------------------------------------------
    # STEP 6: RBAC Testing
    # ---------------------------------------------------------
    # Emp 1 tries to view Emp 2 payroll
    res = client.get(f"/payroll/{emp_ids['emp2@test.com']}", headers=emp1_headers)
    assert res.status_code == 403
    
    print("TEST_COMPLETE")
    print(f"EMP1_PAYROLL: {p1}")
    print(f"EMP2_PAYROLL: {p2}")

if __name__ == "__main__":
    run_full_test()
