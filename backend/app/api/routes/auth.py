# app/api/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from app.core.security import validate_token

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenValidationResponse(BaseModel):
    user_id: str
    email: str
    role: str
    valid: bool

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