from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.services import employee_service
from app.auth.jwt_handler import verify_password, create_access_token
from app.utils.exceptions import not_found, bad_request

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: EmployeeResponse

@router.post("/register", response_model=EmployeeResponse, status_code=201)
def register(payload: EmployeeCreate, db: Session = Depends(get_db)):
    """Register a new user (Admin only can access this via frontend logic or dependency if needed)"""
    # For MVP, keeping it open or you could enforce require_admin if this is called by an already logged in admin
    # but initially, we need an admin. Let's allow creating employees via auth/register.
    return employee_service.create_employee(db, payload)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT"""
    user = employee_service.get_employee_by_email(db, payload.email)
    if not user:
        bad_request("Incorrect email or password")
    
    if not verify_password(payload.password, user.password_hash):
        bad_request("Incorrect email or password")
        
    access_token = create_access_token(subject=user.id, role=user.role)
    
    return TokenResponse(
        access_token=access_token,
        user=user
    )
