"""
Mini Payroll & Attendance System — FastAPI application entry point.

Registers all routers, enables CORS, and creates DB tables on startup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base

# Import all models so Base.metadata.create_all picks them up
from app.models import employee, attendance, leave  # noqa: F401

from app.routes.employee import router as employee_router
from app.routes.attendance import router as attendance_router
from app.routes.leave import router as leave_router
from app.routes.payroll import router as payroll_router
from app.auth.auth_routes import router as auth_router


# ---------------------------------------------------------------------------
# Lifespan — create tables on startup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Mini Payroll & Attendance System",
    description="SaaS MVP for managing employees, attendance, leave, and payroll.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow specific origins for production and local development
# ---------------------------------------------------------------------------
origins = [
    "https://mini-payroll-and-attendance-system.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(attendance_router)
app.include_router(leave_router)
app.include_router(payroll_router)


@app.get("/", tags=["Health"])
def health_check():
    """Simple health-check endpoint."""
    return {"status": "ok", "message": "Mini Payroll & Attendance System is running"}
