"""Leave API endpoints — thin controller layer."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.leave import LeaveCreate, LeaveResponse, LeaveUpdate
from app.services import leave_service
from app.auth.dependencies import get_current_user, require_admin, require_employee
from app.models.employee import Employee

router = APIRouter(prefix="/leave", tags=["Leave"])


@router.post("/", response_model=LeaveResponse, status_code=201)
def apply_leave(
    payload: LeaveCreate, 
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_employee)
):
    """Apply for a new leave request. (Employee only)"""
    if payload.employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only apply for your own leave")
    return leave_service.apply_leave(db, payload)


@router.put("/{leave_id}", response_model=LeaveResponse)
def update_leave(
    leave_id: int, 
    payload: LeaveUpdate, 
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_admin)
):
    """Approve or reject an existing leave request. (Admin only)"""
    return leave_service.update_leave_status(db, leave_id, payload)


@router.get("/", response_model=List[LeaveResponse])
def get_leaves(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Retrieve leave requests. Admin sees all, Employee sees own."""
    leaves = leave_service.get_all_leaves(db)
    if current_user.role != "ADMIN":
        leaves = [l for l in leaves if l.employee_id == current_user.id]
    return leaves
