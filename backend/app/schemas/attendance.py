"""Pydantic schemas for Attendance requests / responses."""

from datetime import date
from typing import List, Literal

from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    """Payload to mark attendance for a single employee."""
    employee_id: int
    date: date
    status: Literal["present", "absent"]


class BulkAttendanceEntry(BaseModel):
    """Single entry inside a bulk-attendance request."""
    employee_id: int
    status: Literal["present", "absent"]


class BulkAttendanceCreate(BaseModel):
    """Payload for bulk attendance — one date, many employees."""
    date: date
    entries: List[BulkAttendanceEntry]


class AttendanceResponse(BaseModel):
    """Attendance record returned to the client."""
    id: int
    employee_id: int
    date: date
    status: str

    model_config = {"from_attributes": True}
