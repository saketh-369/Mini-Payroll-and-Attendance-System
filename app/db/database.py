"""
Database engine, session factory, and declarative Base.
Reads DATABASE_URL from environment (.env) — defaults to SQLite.
Swap to a PostgreSQL URL for production with zero code changes.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # load .env at module import time

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./payroll.db")

# For SQLite we need check_same_thread=False so FastAPI's threaded
# request handling works. PostgreSQL doesn't need this flag.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
