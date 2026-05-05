"""Business logic for Attendance operations."""

from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.attendance import Attendance
from app.schemas.attendance import AttendanceCreate, BulkAttendanceCreate
from app.services.employee_service import get_employee_by_id
from app.utils.exceptions import not_found, conflict


def mark_attendance(db: Session, payload: AttendanceCreate) -> Attendance:
    """Mark attendance for a single employee on a given date."""
    # Validate employee exists
    employee = get_employee_by_id(db, payload.employee_id)
    if not employee:
        not_found(f"Employee with id {payload.employee_id} not found")

    record = Attendance(**payload.model_dump())
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        conflict(
            f"Attendance already recorded for employee {payload.employee_id} "
            f"on {payload.date}"
        )
    return record


def mark_bulk_attendance(
    db: Session, payload: BulkAttendanceCreate
) -> List[Attendance]:
    """Mark attendance for multiple employees on the same date."""
    results: List[Attendance] = []
    errors: List[str] = []

    for entry in payload.entries:
        # Validate employee exists
        employee = get_employee_by_id(db, entry.employee_id)
        if not employee:
            errors.append(f"Employee {entry.employee_id} not found")
            continue

        record = Attendance(
            employee_id=entry.employee_id,
            date=payload.date,
            status=entry.status,
        )
        db.add(record)
        try:
            db.flush()  # flush to catch unique-constraint violations early
            results.append(record)
        except IntegrityError:
            db.rollback()
            errors.append(
                f"Duplicate attendance for employee {entry.employee_id} "
                f"on {payload.date}"
            )

    if errors:
        db.rollback()
        conflict("; ".join(errors))

    db.commit()
    for r in results:
        db.refresh(r)
    return results


def get_attendance_by_employee(
    db: Session, employee_id: int
) -> List[Attendance]:
    """Return all attendance records for a given employee."""
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        not_found(f"Employee with id {employee_id} not found")

    return (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee_id)
        .order_by(Attendance.date)
        .all()
    )
