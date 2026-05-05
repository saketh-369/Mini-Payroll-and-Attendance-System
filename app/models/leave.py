"""Leave ORM model."""

from sqlalchemy import Column, Integer, String, Date, ForeignKey

from app.db.database import Base


class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending / approved / rejected
