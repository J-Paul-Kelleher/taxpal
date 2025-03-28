# app/core/config.py
import os
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TaxPal"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Supabase settings
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    SUPABASE_JWT_SECRET: str = Field(..., env="SUPABASE_JWT_SECRET")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # LLM Settings
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    
    # Vector Database
    PINECONE_API_KEY: str = Field(..., env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = Field(..., env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX: str = Field(..., env="PINECONE_INDEX")
    
    # Subscription
    STRIPE_API_KEY: str = Field(..., env="STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: str = Field(..., env="STRIPE_WEBHOOK_SECRET")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()