"""Employee API endpoints — thin controller layer."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.services import employee_service
from app.auth.dependencies import require_admin
from app.models.employee import Employee

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db), current_user: Employee = Depends(require_admin)):
    """Create a new employee. (Admin only)"""
    return employee_service.create_employee(db, payload)


@router.get("/", response_model=List[EmployeeResponse])
def get_employees(db: Session = Depends(get_db), current_user: Employee = Depends(require_admin)):
    """Retrieve all employees. (Admin only)"""
    return employee_service.get_all_employees(db)
