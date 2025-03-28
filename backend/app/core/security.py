# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from typing import Dict, Optional

security = HTTPBearer()

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Validates the Supabase-issued JWT token and returns user context.
    """
    try:
        token = credentials.credentials
        # Decode the JWT, without verification (we already get a validated token from Supabase)
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": True}
        )
        
        # Extract user information from JWT claims
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Return user context
        return {
            "user_id": user_id,
            "role": role,
            "email": email,
            "token": token
        }
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_admin(user_context: Dict = Depends(validate_token)) -> Dict:
    """
    Ensures the user has admin privileges.
    """
    if user_context.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user_context