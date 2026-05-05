"""Attendance ORM model."""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint

from app.db.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)  # present / absent

    # Prevent duplicate attendance for the same employee on the same date
    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="uq_employee_date"),
    )
