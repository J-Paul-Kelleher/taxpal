# app/services/user_service.py
import httpx
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def get_user_by_id(user_id: str) -> Dict:
    """
    Retrieve a user by their ID
    
    Args:
        user_id: The user's UUID
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If user is not found or an error occurs
    """
    url = f"{settings.SUPABASE_URL}/rest/v1/users?id=eq.{user_id}&select=*"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
        if response.status_code != 200:
            logger.error(f"Failed to get user: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user: {response.text}"
            )
            
        users = response.json()
        if not users or len(users) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return users[0]
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

async def update_usage_count(user_id: str, tokens_used: int) -> Dict:
    """
    Update a user's token usage count
    
    Args:
        user_id: The user's UUID
        tokens_used: Number of tokens to add to current usage
        
    Returns:
        Dict containing updated user information
        
    Raises:
        HTTPException: If update fails or user exceeds quota
    """
    try:
        # First get current user data
        user = await get_user_by_id(user_id)
        
        current_usage = user.get("current_period_usage", 0)
        usage_limit = user.get("usage_limit", 10)  # Default limit for free tier
        new_usage = current_usage + tokens_used
        
        # Check if user would exceed their limit
        if new_usage > usage_limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usage limit exceeded. Please upgrade your plan."
            )
            
        # Update the usage in database
        url = f"{settings.SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        update_data = {"current_period_usage": new_usage}
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, json=update_data)
            
        if response.status_code != 200:
            logger.error(f"Failed to update usage: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update usage count"
            )
            
        updated_user = response.json()
        return updated_user[0] if isinstance(updated_user, list) else updated_user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating usage count: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

async def check_user_quota(user_id: str) -> bool:
    """
    Check if a user has remaining quota
    
    Args:
        user_id: The user's UUID
        
    Returns:
        bool: True if user has remaining quota, False otherwise
        
    Raises:
        HTTPException: If checking quota fails
    """
    try:
        user = await get_user_by_id(user_id)
        
        current_usage = user.get("current_period_usage", 0)
        usage_limit = user.get("usage_limit", 10)
        
        return current_usage < usage_limit
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error checking user quota: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

async def get_subscription_plans() -> List[Dict]:
    """
    Get all available subscription plans
    
    Returns:
        List of subscription plan dictionaries
        
    Raises:
        HTTPException: If retrieving plans fails
    """
    url = f"{settings.SUPABASE_URL}/rest/v1/subscription_plans?select=*&is_active=eq.true"
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
        if response.status_code != 200:
            logger.error(f"Failed to get subscription plans: {response.status_code} {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving subscription plans"
            )
            
        return response.json()
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting subscription plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )