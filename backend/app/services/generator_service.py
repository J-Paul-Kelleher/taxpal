import os
import re
import logging
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import google.generativeai as genai
from pathlib import Path
import time
import uuid
from tqdm import tqdm

# Import our services
from app.services.retrieval_service import RetrievalService, RetrievalResult

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Citation:
    """Represents a citation extracted from the generated response."""
    text: str
    document_id: str
    section_id: Optional[str] = None
    section_title: Optional[str] = None
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "document_id": self.document_id,
            "section_id": self.section_id,
            "section_title": self.section_title,
            "confidence": self.confidence
        }

@dataclass
class GeneratedResponse:
    """Represents a generated response with citations."""
    response_text: str
    citations: List[Citation] = field(default_factory=list)
    cited_documents: List[Dict[str, Any]] = field(default_factory=list)
    sources_used: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "response_text": self.response_text,
            "citations": [citation.to_dict() for citation in self.citations],
            "cited_documents": self.cited_documents,
            "sources_used": self.sources_used,
            "confidence_score": self.confidence_score,
            "response_id": self.response_id
        }

class GeneratorService:
    """Service for generating responses to user queries."""
    
    def __init__(
        self,
        retrieval_service: RetrievalService,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-flash",
        cache_dir: Optional[Path] = None,
        temperature: float = 0.2
    ):
        """Initialize the generator service.
        
        Args:
            retrieval_service: Service for retrieving relevant documents
            api_key: Google AI API key (will try to read from env if not provided)
            model_name: Name of the model to use for generation
            cache_dir: Directory to cache generated responses
            temperature: Temperature for response generation (higher = more creative)
        """
        # Set up Google AI API
        self.api_key = api_key or os.environ.get("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("Google AI API key is required.")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        self.temperature = temperature
        
        # Get the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={"temperature": self.temperature}
        )
        
        # Set up retrieval service
        self.retrieval_service = retrieval_service
        
        # Cache directory
        self.cache_dir = cache_dir
        if self.cache_dir and not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
    
    def generate_response(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        extract_citations: bool = True
    ) -> GeneratedResponse:
        """Generate a response to a user query with relevant context.
        
        Args:
            query: User's query
            top_k: Number of relevant documents to retrieve
            filters: Metadata filters to apply to retrieval
            extract_citations: Whether to extract citations from the response
            
        Returns:
            Generated response with citations
        """
        # 1. Retrieve relevant documents
        relevant_docs = self.retrieval_service.retrieve_with_rerank(
            query=query,
            top_k=top_k,
            filters=filters
        )
        
        if not relevant_docs:
            logger.warning("No relevant documents found for query")
            return GeneratedResponse(
                response_text="I couldn't find any specific information on this topic in the Irish tax legislation I have access to. Please try a different query or provide more details about what you're looking for."
            )
        
        # 2. Create RAG prompt
        contexts = [doc.content for doc in relevant_docs]
        prompt = PromptTemplate.rag_prompt(query, contexts)
        
        # 3. Generate response
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # 4. Extract citations if requested
            citations = []
            cited_documents = []
            sources_used = []
            confidence_score = 0.0
            
            if extract_citations:
                # Prepare contexts with metadata for citation extraction
                contexts_with_meta = [
                    {
                        "content": doc.content,
                        "document_id": doc.document_id,
                        "metadata": doc.metadata
                    }
                    for doc in relevant_docs
                ]
                
                citations, cited_documents, sources_used, confidence_score = self._extract_citations(
                    response_text, contexts_with_meta
                )
            
            # 5. Create and return the response
            return GeneratedResponse(
                response_text=response_text,
                citations=citations,
                cited_documents=cited_documents,
                sources_used=sources_used,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return GeneratedResponse(
                response_text="I encountered an error while generating a response. Please try again or rephrase your query."
            )
    
    def _extract_citations(
        self, 
        response_text: str, 
        contexts: List[Dict[str, Any]]
    ) -> Tuple[List[Citation], List[Dict[str, Any]], List[str], float]:
        """Extract citations from a generated response.
        
        Args:
            response_text: Generated response text
            contexts: List of contexts with metadata
            
        Returns:
            Tuple of (citations, cited_documents, sources_used, confidence_score)
        """
        try:
            # Create citation extraction prompt
            prompt = PromptTemplate.citation_extraction_prompt(response_text, contexts)
            
            # Generate citations
            citation_response = self.model.generate_content(prompt)
            citation_text = citation_response.text
            
            # Extract JSON from the response
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', citation_text)
            if json_match:
                citation_json = json_match.group(1).strip()
            else:
                # Try to find JSON without code blocks
                json_match = re.search(r'\[\s*\{.*\}\s*\]', citation_text, re.DOTALL)
                if json_match:
                    citation_json = json_match.group(0).strip()
                else:
                    # If still no match, use the entire response
                    citation_json = citation_text.strip()
            
            # Parse JSON
            citation_data = json.loads(citation_json)
            
            # Create Citation objects
            citations = []
            cited_doc_ids = set()
            for item in citation_data:
                citation = Citation(
                    text=item.get("text", ""),
                    document_id=item.get("document_id", ""),
                    section_id=item.get("section_id"),
                    section_title=item.get("section_title"),
                    confidence=item.get("confidence", 1.0)
                )
                citations.append(citation)
                cited_doc_ids.add(citation.document_id)
            
            # Create cited documents list
            cited_documents = []
            sources_used = []
            
            for doc_id in cited_doc_ids:
                # Find the context with matching document_id
                matching_contexts = [ctx for ctx in contexts if ctx.get("document_id") == doc_id]
                if matching_contexts:
                    ctx = matching_contexts[0]
                    metadata = ctx.get("metadata", {})
                    
                    # Add to cited documents
                    cited_documents.append({
                        "document_id": doc_id,
                        "section_id": metadata.get("section_id"),
                        "section_title": metadata.get("section_title"),
                        "content_snippet": ctx.get("content", "")[:200] + "..." if len(ctx.get("content", "")) > 200 else ctx.get("content", "")
                    })
                    
                    # Add to sources
                    source = f"{metadata.get('title', 'Unknown Document')}"
                    if metadata.get("section_id") and metadata.get("section_title"):
                        source += f" - Section {metadata.get('section_id')}: {metadata.get('section_title')}"
                    
                    sources_used.append(source)
            
            # Calculate overall confidence score (average of all citation confidences)
            avg_confidence = sum(citation.confidence for citation in citations) / max(1, len(citations))
            
            return citations, cited_documents, sources_used, avg_confidence
            
        except Exception as e:
            logger.error(f"Error extracting citations: {e}")
            return [], [], [], 0.0
    
    def format_response_with_citations(
        self, generated_response: GeneratedResponse, include_sources: bool = True
    ) -> str:
        """Format a response with citations for display.
        
        Args:
            generated_response: The generated response with citations
            include_sources: Whether to include sources at the end
            
        Returns:
            Formatted response text
        """
        response_text = generated_response.response_text
        
        # Add superscript citation numbers
        citations = sorted(generated_response.citations, key=lambda x: len(x.text), reverse=True)
        for i, citation in enumerate(citations):
            citation_text = citation.text
            if citation_text in response_text:
                response_text = response_text.replace(
                    citation_text, 
                    f"{citation_text}[{i+1}]"
                )
        
        # Add sources if requested
        if include_sources and generated_response.sources_used:
            response_text += "\n\nSources:\n"
            for i, source in enumerate(generated_response.sources_used):
                response_text += f"[{i+1}] {source}\n"
        
        return response_text


class PromptTemplate:
    """Class for managing prompt templates."""
    
    @staticmethod
    def rag_prompt(query: str, contexts: List[str]) -> str:
        """Create a RAG prompt with context.
        
        Args:
            query: The user's query
            contexts: List of relevant document chunks
            
        Returns:
            Formatted prompt
        """
        context_str = "\n\n---\n\n".join([f"CONTEXT {i+1}:\n{context}" for i, context in enumerate(contexts)])
        
        return f"""You are TaxPal, an expert assistant specializing in Irish tax legislation. Your responses should be helpful, accurate, and based only on the provided context information about Irish tax laws and regulations.

CONTEXT INFORMATION:

{context_str}

USER QUERY: {query}

Please provide a clear and accurate response to the user's query based solely on the information in the context provided above. Be concise but thorough, focusing on directly answering the query.

If the context doesn't contain information to answer the query, acknowledge this limitation by stating which specific aspects of the query you cannot answer based on the available information. Do not make up or infer information not present in the context.

Use natural, conversational language, but maintain professionalism as a tax expert. Cite the relevant sections of legislation or regulations when appropriate.

Format your response with a clear structure. If the query touches on multiple topics, use paragraphs to separate different aspects of your response."""
    
    @staticmethod
    def citation_extraction_prompt(response: str, contexts: List[Dict[str, Any]]) -> str:
        """Create a prompt for citation extraction.
        
        Args:
            response: The generated response
            contexts: List of contexts with their metadata
            
        Returns:
            Formatted prompt
        """
        # Format contexts with their metadata
        context_str = ""
        for i, context in enumerate(contexts):
            metadata = context.get("metadata", {})
            doc_id = context.get("document_id", f"doc{i}")
            section_id = metadata.get("section_id", "N/A")
            section_title = metadata.get("section_title", "N/A")
            
            context_str += f"DOCUMENT {doc_id} (Section {section_id}: {section_title}):\n{context.get('content', '')}\n\n"
        
        return f"""You are an expert citation extractor. Your task is to identify which parts of a generated response are based on which reference documents. You'll output citations in a specific JSON format.

REFERENCE DOCUMENTS:

{context_str}

GENERATED RESPONSE:

{response}

Task: For each factual statement or claim in the generated response, identify which reference document it came from. Create a citation for each relevant piece of information.

Format your output as a JSON array of citation objects, where each citation has:
- "text": The exact text from the response that is being cited
- "document_id": The ID of the source document 
- "section_id": The section ID (if available)
- "section_title": The section title (if available)
- "confidence": A number between 0 and 1 indicating your confidence in this citation

Only include factual information that clearly comes from the reference documents. General knowledge, common phrases, or transitional text should not be cited.

Example output format:
```json
[
  {
    "text": "The standard rate of corporation tax in Ireland is 12.5% on trading income.",
    "document_id": "doc1",
    "section_id": "2.1",
    "section_title": "Corporate Tax Provisions",
    "confidence": 0.95
  },
  {
    "text": "A rate of 25% applies to non-trading income, including rental income from land and buildings.",
    "document_id": "doc1",
    "section_id": "2.2",
    "section_title": "Corporate Tax Provisions",
    "confidence": 0.9
  }
]
```

Return only the JSON array without any additional explanation."""