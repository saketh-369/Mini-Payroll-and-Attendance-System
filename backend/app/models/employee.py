"""Employee ORM model."""

from sqlalchemy import Column, Integer, String, Float

from app.db.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="EMPLOYEE")  # ADMIN / EMPLOYEE
    work_type = Column(String, nullable=False)       # WFH / Office / On-site
    salary_type = Column(String, nullable=False)      # monthly / daily
    salary_amount = Column(Float, nullable=False)
