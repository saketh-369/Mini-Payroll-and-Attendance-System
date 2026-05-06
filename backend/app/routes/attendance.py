"""Attendance API endpoints — thin controller layer."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    BulkAttendanceCreate,
)
from app.services import attendance_service
from app.auth.dependencies import get_current_user, require_admin, require_employee
from app.models.employee import Employee

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/", response_model=AttendanceResponse, status_code=201)
def mark_attendance(
    payload: AttendanceCreate, 
    db: Session = Depends(get_db), 
    current_user: Employee = Depends(require_employee)
):
    """Mark attendance for a single employee (Employee only, can only mark their own)."""
    if payload.employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only mark your own attendance")
    return attendance_service.mark_attendance(db, payload)


@router.post("/bulk", response_model=List[AttendanceResponse], status_code=201)
def mark_bulk_attendance(
    payload: BulkAttendanceCreate, 
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_admin)
):
    """Mark attendance for multiple employees on the same date. (Admin only)"""
    return attendance_service.mark_bulk_attendance(db, payload)


@router.get("/{employee_id}", response_model=List[AttendanceResponse])
def get_attendance(
    employee_id: int, 
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Retrieve attendance records for a specific employee."""
    if current_user.role != "ADMIN" and current_user.id != employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own attendance")
    return attendance_service.get_attendance_by_employee(db, employee_id)
