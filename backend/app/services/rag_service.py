# app/services/rag_service.py
from typing import List, Tuple, Dict, Any
import logging
from app.models.rag import Citation
from app.services.vector_db_service import retrieve_documents
from app.services.generator_service import generate_response

logger = logging.getLogger(__name__)

async def generate_rag_response(
    query: str,
    user_id: str,
    session_id: str = None
) -> Tuple[str, List[Dict[str, str]], int]:
    """
    Generate a response using RAG (Retrieval Augmented Generation).
    
    Args:
        query: The user's question
        user_id: The ID of the user asking the question
        session_id: Optional session ID for conversation context
        
    Returns:
        Tuple containing:
        - response: The generated response text
        - citations: List of citation objects
        - tokens_used: Number of tokens used for this request
    """
    try:
        logger.info(f"Processing query: '{query}' from user: {user_id}")
        
        # Retrieve relevant documents
        retrieved_docs = await retrieve_documents(
            query=query,
            top_k=5  # Retrieve top 5 documents
        )
        
        if not retrieved_docs:
            logger.warning(f"No relevant documents found for query: '{query}'")
            return (
                "I couldn't find specific information related to your query in the Irish tax legislation database. "
                "Please try rephrasing your question or consult with a qualified tax professional for assistance.",
                [],
                50  # Token estimate for this response
            )
        
        # Generate response based on retrieved documents
        response_text, citations, tokens_used = await generate_response(
            query=query,
            retrieved_docs=retrieved_docs
        )
        
        # Convert citations to the format expected by the API
        citation_dicts = [
            {
                "source": citation.source,
                "text": citation.text,
                "reference": citation.reference
            }
            for citation in citations
        ]
        
        return response_text, citation_dicts, tokens_used
        
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {str(e)}")
        return (
            "I apologize, but I encountered an error processing your request. Please try again.",
            [],
            50  # Token estimate for the error response
        )