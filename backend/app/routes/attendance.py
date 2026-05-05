"""Attendance API endpoints — thin controller layer."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    BulkAttendanceCreate,
)
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/", response_model=AttendanceResponse, status_code=201)
def mark_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    """Mark attendance for a single employee."""
    return attendance_service.mark_attendance(db, payload)


@router.post("/bulk", response_model=List[AttendanceResponse], status_code=201)
def mark_bulk_attendance(
    payload: BulkAttendanceCreate, db: Session = Depends(get_db)
):
    """Mark attendance for multiple employees on the same date."""
    return attendance_service.mark_bulk_attendance(db, payload)


@router.get("/{employee_id}", response_model=List[AttendanceResponse])
def get_attendance(employee_id: int, db: Session = Depends(get_db)):
    """Retrieve attendance records for a specific employee."""
    return attendance_service.get_attendance_by_employee(db, employee_id)
