# app/services/embedding_service.py
import google.generativeai as genai
from typing import List
from app.core.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Gemini Embedding API.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors
    """
    # Process texts in batches if needed
    embeddings = []
    
    for text in texts:
        # Call the Gemini embedding API
        embedding = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document",
        )
        
        # Extract and add the embedding vector
        embeddings.append(embedding["embedding"])
    
    return embeddings