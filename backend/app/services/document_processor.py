# app/services/document_processor.py
import re
from typing import List, Dict, Any
from app.models.rag import DocumentChunk

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace, etc."""
    # Remove multiple newlines
    text = re.sub(r'\n+', '\n', text)
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text

def chunk_document(
    text: str,
    metadata: Dict[str, Any],
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[DocumentChunk]:
    """
    Split a document into chunks of specified size with overlap.
    
    Args:
        text: The document text
        metadata: Metadata about the document
        chunk_size: The target size of each chunk in characters
        chunk_overlap: The overlap between chunks in characters
        
    Returns:
        List of DocumentChunk objects
    """
    # Clean the text
    text = clean_text(text)
    
    # For simple chunking, we'll just split by paragraphs and then combine
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""
    
    for i, paragraph in enumerate(paragraphs):
        # Skip empty paragraphs
        if not paragraph.strip():
            continue
            
        # If adding this paragraph would exceed chunk size, save the current chunk
        if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
            # Create chunk with metadata
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = len(chunks)
            
            # Create the chunk
            chunks.append(
                DocumentChunk(
                    id=f"{metadata.get('id', 'doc')}_chunk_{len(chunks)}",
                    text=current_chunk,
                    metadata=chunk_metadata
                )
            )
            
            # Start new chunk with overlap from the end of previous chunk
            if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                # Get the last N characters for overlap
                overlap_text = current_chunk[-chunk_overlap:]
                current_chunk = overlap_text + "\n" + paragraph
            else:
                current_chunk = paragraph
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Don't forget the last chunk
    if current_chunk:
        chunk_metadata = metadata.copy()
        chunk_metadata["chunk_index"] = len(chunks)
        
        chunks.append(
            DocumentChunk(
                id=f"{metadata.get('id', 'doc')}_chunk_{len(chunks)}",
                text=current_chunk,
                metadata=chunk_metadata
            )
        )
    
    return chunks