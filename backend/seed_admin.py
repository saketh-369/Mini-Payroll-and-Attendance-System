import os
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.employee import Employee
from app.auth.jwt_handler import get_password_hash

def seed_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(Employee).filter(Employee.email == "admin@payroll.com").first()
        if not admin:
            print("Creating default admin user...")
            new_admin = Employee(
                name="System Admin",
                email="admin@payroll.com",
                password_hash=get_password_hash("admin123"),
                role="ADMIN",
                work_type="Office",
                salary_type="monthly",
                salary_amount=0.0
            )
            db.add(new_admin)
            db.commit()
            print("Admin created: admin@payroll.com / admin123")
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
