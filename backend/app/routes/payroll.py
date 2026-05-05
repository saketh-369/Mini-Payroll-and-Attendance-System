"""Payroll API endpoint — thin controller layer."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.payroll import PayrollResponse
from app.services import payroll_service

router = APIRouter(prefix="/payroll", tags=["Payroll"])


@router.get("/{employee_id}", response_model=PayrollResponse)
def get_payroll(employee_id: int, db: Session = Depends(get_db)):
    """Calculate and return the payroll breakdown for an employee."""
    return payroll_service.calculate_payroll(db, employee_id)
