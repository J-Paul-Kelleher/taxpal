# app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from app.core.security import validate_token
from app.services.rag_service import generate_rag_response

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class Citation(BaseModel):
    source: str
    text: str
    reference: str

class ChatResponse(BaseModel):
    response: str
    citations: List[Citation]
    tokens_used: int

@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    user_context: Dict = Depends(validate_token)
):
    try:
        # Call the RAG service to generate a response
        response, citations, tokens_used = await generate_rag_response(
            query=request.query,
            user_id=user_context["user_id"],
            session_id=request.session_id
        )
        
        return ChatResponse(
            response=response,
            citations=citations,
            tokens_used=tokens_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))