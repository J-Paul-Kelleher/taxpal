# app/services/generator_service.py
import google.generativeai as genai
from typing import List, Dict, Any, Tuple
import logging
import re
from app.core.config import settings
from app.models.rag import RetrievedDocument, Citation

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Get Gemini model
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')