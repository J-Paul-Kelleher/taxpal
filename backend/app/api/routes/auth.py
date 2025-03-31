# app/api/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Optional, Any
import httpx
from app.core.security import validate_token
from app.core.config import settings
import logging

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

# Pydantic models for request validation
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class TokenValidationResponse(BaseModel):
    user_id: str
    email: str
    role: str
    valid: bool

class UserProfileResponse(BaseModel):
    id: str
    email: str
    subscription_plan: Optional[str] = None
    subscription_status: Optional[str] = None
    is_admin: bool = False
    usage: Optional[int] = None
    usage_limit: Optional[int] = None

async def _supabase_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """
    Helper function to make requests to Supabase REST API
    """
    url = f"{settings.SUPABASE_URL}{endpoint}"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}"
    }
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
    if response.status_code >= 400:
        logger.error(f"Supabase error: {response.status_code} {response.text}")
        return {"error": response.text, "status_code": response.status_code}
        
    return response.json()

@router.post("/register")
async def register(user_data: UserCreate):
    """
    Register a new user via Supabase Auth
    """
    try:
        # Call Supabase Auth API to sign up user
        response = await _supabase_request(
            "/auth/v1/signup",
            method="POST",
            data={"email": user_data.email, "password": user_data.password}
        )
        
        if "error" in response:
            status_code = response.get("status_code", 400)
            raise HTTPException(
                status_code=status_code,
                detail=response["error"]
            )
            
        return {"message": "User registered successfully. Please check your email to confirm your account."}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.post("/login")
async def login(credentials: UserLogin):
    """
    Log in a user via Supabase Auth
    """
    try:
        # Call Supabase Auth API to sign in user
        response = await _supabase_request(
            "/auth/v1/token?grant_type=password",
            method="POST",
            data={"email": credentials.email, "password": credentials.password}
        )
        
        if "error" in response:
            status_code = response.get("status_code", 400)
            raise HTTPException(
                status_code=status_code,
                detail=response["error"]
            )
            
        return response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.get("/verify-token", response_model=TokenValidationResponse)
async def verify_token(user_context: Dict = Depends(validate_token)):
    """
    Verifies that a token is valid and returns user information.
    This endpoint is primarily for the frontend to validate tokens.
    """
    return TokenValidationResponse(
        user_id=user_context["user_id"],
        email=user_context["email"],
        role=user_context.get("role", "user"),
        valid=True
    )

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(user_context: Dict = Depends(validate_token)):
    """
    Get the current user's profile information
    """
    try:
        user_id = user_context["user_id"]
        
        # Get user profile from Supabase
        response = await _supabase_request(f"/rest/v1/users?id=eq.{user_id}&select=*")
        
        if not response or isinstance(response, list) and len(response) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
            
        user_data = response[0] if isinstance(response, list) else response
        
        return UserProfileResponse(
            id=user_data["id"],
            email=user_context["email"],
            subscription_plan=user_data.get("subscription_plan_id"),
            subscription_status=user_data.get("subscription_status"),
            is_admin=user_data.get("is_admin", False),
            usage=user_data.get("current_period_usage"),
            usage_limit=user_data.get("usage_limit")
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred retrieving the user profile"
        )