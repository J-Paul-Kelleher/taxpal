# app/services/vector_db_service.py
from pinecone import Pinecone
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings
from app.models.rag import DocumentChunk, RetrievedDocument
from app.services.embedding_service import get_embeddings

logger = logging.getLogger(__name__)

# Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

# Get or create index
index_name = settings.PINECONE_INDEX
dimension = 768  # Gemini embeddings dimension

# Check if the index already exists
if index_name not in pc.list_indexes().names():
    # Create the index if it doesn't exist
    from pinecone import ServerlessSpec
    
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",  # or "gcp" based on your preference
            region="us-west-2"  # choose an appropriate region
        )
    )

# Get the index
index = pc.Index(index_name)