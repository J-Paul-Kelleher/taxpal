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
model = genai.GenerativeModel('gemini-pro')

def create_prompt(query: str, retrieved_docs: List[RetrievedDocument]) -> str:
    """
    Create a prompt for the LLM based on the query and retrieved documents.
    
    Args:
        query: The user's query
        retrieved_docs: List of retrieved documents
        
    Returns:
        Formatted prompt string
    """
    # Prepare context from retrieved documents
    context_parts = []
    for i, doc in enumerate(retrieved_docs):
        # Format each document with its metadata
        source = doc.metadata.get("source", "Unknown Source")
        section = doc.metadata.get("section", "")
        reference = f"{source} {section}".strip()
        
        context_part = f"Document {i+1} [Source: {reference}]:\n{doc.text}\n"
        context_parts.append(context_part)
    
    context = "\n".join(context_parts)
    
    # Create the full prompt
    prompt = f"""You are TaxPal, an AI assistant specializing in Irish tax legislation. You provide accurate information based on official Irish tax law and guidance documentation. 

Your responses should:
1. Be formal, precise, and in a legal/professional tone
2. Include specific citations to relevant sections of the tax code
3. Be factual and directly backed by the context provided
4. Include a disclaimer when appropriate
5. Acknowledge limitations when information is ambiguous or not available in the context

IMPORTANT GUIDELINES:
- Only use information from the provided context
- Do not hallucinate or make up tax rates, thresholds, or legislation
- If you cannot find the answer in the context, acknowledge the limitations of your knowledge
- Do not provide personal opinions on tax matters
- Always provide the relevant citation with your answer

CONTEXT:
{context}

USER QUERY: {query}

Based on the context provided, answer the user query about Irish tax legislation. Be concise but complete, and always cite your sources.

DISCLAIMER:
This information is provided for general guidance only and does not constitute formal legal advice. For definitive guidance, please consult with a qualified tax professional or contact the Irish Revenue Commissioners.
"""
    return prompt

def extract_citations(response_text: str, retrieved_docs: List[RetrievedDocument]) -> Tuple[str, List[Citation]]:
    """
    Extract citations from the response.
    
    Args:
        response_text: The generated response text
        retrieved_docs: The retrieved documents used for generation
        
    Returns:
        Tuple containing cleaned response text and list of citations
    """
    # Extract sources from retrieved documents
    doc_sources = {}
    for doc in retrieved_docs:
        source = doc.metadata.get("source", "Unknown Source")
        section = doc.metadata.get("section", "")
        reference = f"{source} {section}".strip()
        doc_sources[reference] = {
            "source": source,
            "text": doc.text[:150] + "..." if len(doc.text) > 150 else doc.text,
            "reference": section
        }
    
    # Look for citation patterns in the response
    # This is a simple regex pattern - may need to be refined based on actual responses
    citation_pattern = r'((?:Section|Regulation|Act|Part)\s+[\w\d\.\-]+)'
    matches = re.finditer(citation_pattern, response_text)
    
    citations = []
    for match in matches:
        citation_text = match.group(1)
        
        # Find the most relevant source
        best_match = None
        for ref, info in doc_sources.items():
            if citation_text in ref or info["reference"] in citation_text:
                best_match = info
                break
        
        if best_match:
            citation = Citation(
                source=best_match["source"],
                text=best_match["text"],
                reference=citation_text
            )
            
            # Add citation if it's not already in the list
            if citation not in citations:
                citations.append(citation)
    
    return response_text, citations

async def generate_response(
    query: str,
    retrieved_docs: List[RetrievedDocument]
) -> Tuple[str, List[Citation], int]:
    """
    Generate a response using the LLM based on retrieved documents.
    
    Args:
        query: The user's query
        retrieved_docs: List of retrieved documents
        
    Returns:
        Tuple containing the response text, citations, and tokens used
    """
    try:
        # Create the prompt
        prompt = create_prompt(query, retrieved_docs)
        
        # Generate response using Gemini
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract citations
        cleaned_response, citations = extract_citations(response_text, retrieved_docs)
        
        # Estimate tokens used (simplified)
        tokens_used = len(prompt.split()) + len(response_text.split())
        
        return cleaned_response, citations, tokens_used
    
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return (
            "I apologize, but I encountered an error processing your request. Please try again.",
            [],
            0
        )