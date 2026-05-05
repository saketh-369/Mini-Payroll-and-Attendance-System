"""Payroll API endpoint — thin controller layer."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.payroll import PayrollResponse
from app.services import payroll_service
from app.auth.dependencies import get_current_user
from app.models.employee import Employee

router = APIRouter(prefix="/payroll", tags=["Payroll"])


@router.get("/{employee_id}", response_model=PayrollResponse)
def get_payroll(
    employee_id: int, 
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Calculate and return the payroll breakdown for an employee."""
    if current_user.role != "ADMIN" and current_user.id != employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own payroll")
    return payroll_service.calculate_payroll(db, employee_id)
