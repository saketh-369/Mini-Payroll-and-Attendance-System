"""Pydantic schemas for Employee requests / responses."""

from typing import Literal

from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    """Payload to create a new employee."""
    name: str
    role: str
    work_type: Literal["WFH", "Office", "On-site"]
    salary_type: Literal["monthly", "daily"]
    salary_amount: float = Field(gt=0, description="Must be a positive number")


class EmployeeResponse(BaseModel):
    """Employee data returned to the client."""
    id: int
    name: str
    role: str
    work_type: str
    salary_type: str
    salary_amount: float

    model_config = {"from_attributes": True}
