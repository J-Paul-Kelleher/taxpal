# app/models/rag.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    """A chunk of a document with metadata."""
    id: str
    text: str
    metadata: Dict[str, Any]
    
class RetrievedDocument(BaseModel):
    """A document retrieved from the vector store."""
    id: str
    text: str
    metadata: Dict[str, Any]
    score: float
    
class Citation(BaseModel):
    """A citation for a response."""
    source: str
    text: str
    reference: str
    
class RAGResponse(BaseModel):
    """A response from the RAG pipeline."""
    response: str
    citations: List[Citation]
    tokens_used: int