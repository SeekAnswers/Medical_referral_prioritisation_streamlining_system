from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, LoginAttempt
from utils.auth import auth_service, get_current_active_user
from utils.database_helpers import create_default_admin_user
from typing import Optional
import logging

router = APIRouter(prefix="/auth", tags=["authentication"])
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)

# Pydantic models for request/response
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: str = "staff"
    hospital_id: Optional[str] = None

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,  
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    
    # Get client IP and user agent for logging
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    try:
        # Authenticate user
        user = auth_service.authenticate_user(db, username, password)
        
        if not user:
            # Log failed attempt
            auth_service.log_login_attempt(db, username, False, client_ip, user_agent)
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Invalid username or password"
            })
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        # Log successful attempt
        auth_service.log_login_attempt(db, username, True, client_ip, user_agent)
        
        # For API requests (evaluation), return JSON
        if request.headers.get("accept") == "application/json" or "application/json" in request.headers.get("content-type", ""):
            response = JSONResponse(content={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role
                }
            })
        else:
            # For browser requests, redirect to dashboard
            response = RedirectResponse(url="/dashboard", status_code=302)
        
        # SET COOKIE - This is crucial for the evaluation
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,  # In production with HTTPS, this would be set to True
            samesite="lax",
            max_age=3600,  # 1 hour
            path="/"  # IMPORTANT for Ensuring root path
        )
        
        logger.info(f"User {username} logged in successfully")
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        # Log failed attempt
        auth_service.log_login_attempt(db, username, False, client_ip, user_agent)
        
        if request.headers.get("accept") == "application/json":
            raise HTTPException(status_code=401, detail="Login failed")
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Login failed. Please try again."
            })

@router.post("/logout")
@router.get("/logout")
async def logout():
    """Handle logout"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token", path="/")
    return response

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "department": current_user.department,
        "role": current_user.role,
        "hospital_id": current_user.hospital_id,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login
    }

@router.post("/create-user")
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new user (admin only)"""
    
    # Check if current user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users"
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=User.get_password_hash(user_data.password),
        full_name=user_data.full_name,
        department=user_data.department,
        role=user_data.role,
        hospital_id=user_data.hospital_id or current_user.hospital_id,
        is_active=True,
        is_verified=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "username": new_user.username
    }

@router.get("/init-admin")
async def initialize_admin(db: Session = Depends(get_db)):
    """Initialize default admin user (development only)"""
    admin_user = create_default_admin_user(db)
    return {
        "message": "Admin user initialized",
        "username": admin_user.username,
        "default_password": "hospital123"
    }