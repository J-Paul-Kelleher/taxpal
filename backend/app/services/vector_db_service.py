# app/services/vector_db_service.py
import pinecone
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings
from app.models.rag import DocumentChunk, RetrievedDocument
from app.services.embedding_service import get_embeddings

logger = logging.getLogger(__name__)

# Initialize Pinecone
pinecone.init(
    api_key=settings.PINECONE_API_KEY,
    environment=settings.PINECONE_ENVIRONMENT
)

# Get or create index
index_name = settings.PINECONE_INDEX
dimension = 768  # Gemini embeddings dimension

# Check if the index already exists
if index_name not in pinecone.list_indexes():
    # Create the index if it doesn't exist
    pinecone.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine"
    )

# Get the index
index = pinecone.Index(index_name)

async def index_documents(chunks: List[DocumentChunk]) -> bool:
    """
    Index document chunks in the vector database.
    
    Args:
        chunks: List of document chunks to index
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get text from chunks
        texts = [chunk.text for chunk in chunks]
        
        # Generate embeddings
        embeddings = await get_embeddings(texts)
        
        # Prepare vector records
        records = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            records.append({
                "id": chunk.id,
                "values": embedding,
                "metadata": chunk.metadata
            })
        
        # Upsert to Pinecone in batches
        batch_size = 100
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            index.upsert(vectors=batch)
        
        logger.info(f"Indexed {len(chunks)} document chunks")
        return True
    
    except Exception as e:
        logger.error(f"Error indexing documents: {str(e)}")
        return False

async def retrieve_documents(
    query: str,
    top_k: int = 5,
    filter: Optional[Dict[str, Any]] = None
) -> List[RetrievedDocument]:
    """
    Retrieve relevant documents for a query.
    
    Args:
        query: The search query
        top_k: Number of documents to retrieve
        filter: Filter to apply to the search
        
    Returns:
        List of retrieved documents
    """
    try:
        # Generate embedding for the query
        query_embeddings = await get_embeddings([query])
        query_embedding = query_embeddings[0]
        
        # Search Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )
        
        # Convert to RetrievedDocument objects
        retrieved_docs = []
        for match in results.matches:
            retrieved_docs.append(
                RetrievedDocument(
                    id=match.id,
                    text=match.metadata.get("text", ""),
                    metadata=match.metadata,
                    score=match.score
                )
            )
        
        return retrieved_docs
    
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        return []