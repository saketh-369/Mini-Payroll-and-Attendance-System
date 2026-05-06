"""Pydantic schema for Payroll response."""

from pydantic import BaseModel


class PayrollResponse(BaseModel):
    """Detailed salary breakdown returned by the payroll endpoint."""
    employee_id: int
    employee_name: str
    salary_type: str
    salary_amount: float
    total_days: int
    present_days: int
    approved_leave_days: int
    absent_days: int
    salary: float
