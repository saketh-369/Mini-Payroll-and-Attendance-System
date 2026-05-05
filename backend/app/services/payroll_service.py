"""
Business logic for Payroll calculation.

Rules:
  - Monthly salary: salary_per_day = salary_amount / 30; pay = salary_per_day × effective_present_days
  - Daily salary:   pay = salary_amount × effective_present_days
  - Approved leaves are NOT counted as absences.
    effective_present_days = attendance_present_count + approved_leave_days_that_overlap_attendance_period
"""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.leave import Leave
from app.schemas.payroll import PayrollResponse
from app.services.employee_service import get_employee_by_id
from app.utils.exceptions import not_found


def _count_approved_leave_days(db: Session, employee_id: int) -> int:
    """Sum the calendar days of all approved leave requests for an employee."""
    approved_leaves = (
        db.query(Leave)
        .filter(Leave.employee_id == employee_id, Leave.status == "approved")
        .all()
    )
    total = 0
    for leave in approved_leaves:
        # inclusive range: end - start + 1
        delta = (leave.end_date - leave.start_date).days + 1
        total += delta
    return total


def calculate_payroll(db: Session, employee_id: int) -> PayrollResponse:
    """Build and return the salary breakdown for a given employee."""
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        not_found(f"Employee with id {employee_id} not found")

    # All attendance records for this employee
    records = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee_id)
        .all()
    )

    total_days = len(records)
    present_days = sum(1 for r in records if r.status == "present")
    approved_leave_days = _count_approved_leave_days(db, employee_id)

    # Effective present = actual present + approved leave days
    effective_present = present_days + approved_leave_days
    absent_days = total_days - present_days  # raw absences from attendance log

    # Calculate salary
    if employee.salary_type == "monthly":
        salary_per_day = employee.salary_amount / 30
        salary = round(salary_per_day * effective_present, 2)
    else:  # daily
        salary = round(employee.salary_amount * effective_present, 2)

    return PayrollResponse(
        employee_id=employee.id,
        employee_name=employee.name,
        salary_type=employee.salary_type,
        salary_amount=employee.salary_amount,
        total_days=total_days,
        present_days=present_days,
        approved_leave_days=approved_leave_days,
        absent_days=absent_days,
        salary=salary,
    )
