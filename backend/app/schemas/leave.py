"""Pydantic schemas for Leave requests / responses."""

from datetime import date
from typing import Literal

from pydantic import BaseModel


class LeaveCreate(BaseModel):
    """Payload to apply for leave."""
    employee_id: int
    start_date: date
    end_date: date


class LeaveUpdate(BaseModel):
    """Payload to approve or reject a leave request."""
    status: Literal["approved", "rejected"]


class LeaveResponse(BaseModel):
    """Leave record returned to the client."""
    id: int
    employee_id: int
    start_date: date
    end_date: date
    status: str

    model_config = {"from_attributes": True}
