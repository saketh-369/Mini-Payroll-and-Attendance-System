"""Leave API endpoints — thin controller layer."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.leave import LeaveCreate, LeaveResponse, LeaveUpdate
from app.services import leave_service

router = APIRouter(prefix="/leave", tags=["Leave"])


@router.post("/", response_model=LeaveResponse, status_code=201)
def apply_leave(payload: LeaveCreate, db: Session = Depends(get_db)):
    """Apply for a new leave request."""
    return leave_service.apply_leave(db, payload)


@router.put("/{leave_id}", response_model=LeaveResponse)
def update_leave(leave_id: int, payload: LeaveUpdate, db: Session = Depends(get_db)):
    """Approve or reject an existing leave request."""
    return leave_service.update_leave_status(db, leave_id, payload)


@router.get("/", response_model=List[LeaveResponse])
def get_leaves(db: Session = Depends(get_db)):
    """Retrieve all leave requests."""
    return leave_service.get_all_leaves(db)
