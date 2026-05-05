"""Business logic for Employee operations."""

from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate
from app.utils.exceptions import conflict
from app.auth.jwt_handler import get_password_hash


def create_employee(db: Session, payload: EmployeeCreate) -> Employee:
    """Insert a new employee record."""
    employee_data = payload.model_dump()
    # Hash password
    plain_password = employee_data.pop("password")
    employee_data["password_hash"] = get_password_hash(plain_password)
    
    employee = Employee(**employee_data)
    db.add(employee)
    try:
        db.commit()
        db.refresh(employee)
    except IntegrityError:
        db.rollback()
        conflict(f"Employee with email {payload.email} already exists")
    return employee


def get_all_employees(db: Session) -> List[Employee]:
    """Return every employee."""
    return db.query(Employee).all()


def get_employee_by_id(db: Session, employee_id: int) -> Employee | None:
    """Fetch a single employee or None."""
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employee_by_email(db: Session, email: str) -> Employee | None:
    """Fetch a single employee by email or None."""
    return db.query(Employee).filter(Employee.email == email).first()
