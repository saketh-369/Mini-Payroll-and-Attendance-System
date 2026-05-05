"""Business logic for Employee operations."""

from typing import List

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate


def create_employee(db: Session, payload: EmployeeCreate) -> Employee:
    """Insert a new employee record."""
    employee = Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_all_employees(db: Session) -> List[Employee]:
    """Return every employee."""
    return db.query(Employee).all()


def get_employee_by_id(db: Session, employee_id: int) -> Employee | None:
    """Fetch a single employee or None."""
    return db.query(Employee).filter(Employee.id == employee_id).first()
