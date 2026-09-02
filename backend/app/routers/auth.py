from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.middlewares.auth import get_current_user
from app.schemas.schemas import UserCreate, UserLogin, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user account with hashed credentials.
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "EMAIL_ALREADY_EXISTS",
                    "message": "An account with this email address is already registered."
                }
            }
        )
        
    hashed_pwd = get_password_hash(user_data.password)
    user = User(email=user_data.email, hashed_password=hashed_pwd)
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Auto-login after signup
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        
        return {
            "success": True,
            "message": "User registered successfully",
            "data": {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "created_at": user.created_at
                },
                "token": {
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "REGISTRATION_FAILED",
                    "message": f"Registration failed due to database error: {str(e)}"
                }
            }
        )

@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates email & password, returning a JWT access token.
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid email address or password."
                }
            }
        )
        
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user": {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at
            },
            "token": {
                "access_token": access_token,
                "token_type": "bearer"
            }
        }
    }

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the authenticated user details.
    """
    return {
        "success": True,
        "message": "Profile retrieved successfully",
        "data": {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "created_at": current_user.created_at
            }
        }
    }
