"""Business logic for Leave operations."""

from sqlalchemy.orm import Session

from app.models.leave import Leave
from app.schemas.leave import LeaveCreate, LeaveUpdate
from app.services.employee_service import get_employee_by_id
from app.utils.exceptions import not_found, bad_request


def apply_leave(db: Session, payload: LeaveCreate) -> Leave:
    """Create a new leave request after validating dates and employee."""
    # Validate employee exists
    employee = get_employee_by_id(db, payload.employee_id)
    if not employee:
        not_found(f"Employee with id {payload.employee_id} not found")

    # Validate date range
    if payload.start_date > payload.end_date:
        bad_request("start_date must be before or equal to end_date")

    leave = Leave(**payload.model_dump())
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


def update_leave_status(db: Session, leave_id: int, payload: LeaveUpdate) -> Leave:
    """Approve or reject an existing leave request."""
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        not_found(f"Leave request with id {leave_id} not found")

    allowed_statuses = {"approved", "rejected"}
    if payload.status not in allowed_statuses:
        bad_request(f"Status must be one of: {allowed_statuses}")

    leave.status = payload.status
    db.commit()
    db.refresh(leave)
    return leave


def get_all_leaves(db: Session):
    """Return every leave request."""
    return db.query(Leave).order_by(Leave.id.desc()).all()
