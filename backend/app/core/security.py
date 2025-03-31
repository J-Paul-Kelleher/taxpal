# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Dict, Optional, Union, Any, List
from app.core.config import settings
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Security scheme for JWT
security = HTTPBearer()

async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Validates the Supabase-issued JWT token and returns user context.
    
    Args:
        credentials: The JWT token from the request Authorization header
        
    Returns:
        Dict containing user information from the token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        # Decode the JWT with verification against the Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": True}
        )
        
        # Extract user information from JWT claims
        user_id = payload.get("sub")
        expiration = payload.get("exp")
        role = payload.get("role", "user")
        email = payload.get("email")
        
        # Check for token expiration
        if expiration is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing expiration",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if datetime.utcfromtimestamp(expiration) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Return user context
        return {
            "user_id": user_id,
            "role": role,
            "email": email,
            "token": token
        }
    
    except JWTError as e:
        logger.error(f"JWT error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error in token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_admin(user_context: Dict = Depends(validate_token)) -> Dict:
    """
    Ensures the user has admin privileges.
    
    Args:
        user_context: The user context from validate_token
        
    Returns:
        The user context if the user is an admin
        
    Raises:
        HTTPException: If the user is not an admin
    """
    if user_context.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user_context

async def rate_limit_check(user_context: Dict = Depends(validate_token)) -> Dict:
    """
    Checks if the user has exceeded their rate limit or usage quota.
    
    Args:
        user_context: The user context from validate_token
        
    Returns:
        The user context if within limits
        
    Raises:
        HTTPException: If user has exceeded their limits
    """
    # TO-DO: Implement actual quota checking against the database
    # This is a placeholder for now. We'll implement this in the user service.
    return user_context