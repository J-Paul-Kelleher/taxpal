import os
import re
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import pinecone
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from tqdm import tqdm

# Import our services
from app.services.embedding_service import EmbeddingService

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to download NLTK data, but handle if already present
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    logger.info("NLTK data already downloaded")

@dataclass
class RetrievalResult:
    """Result of a retrieval operation."""
    content: str
    metadata: Dict[str, Any]
    score: float
    document_id: str
    retrieval_method: str = "hybrid"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "score": self.score,
            "document_id": self.document_id,
            "retrieval_method": self.retrieval_method
        }

class RetrievalService:
    """Service for retrieving relevant documents using hybrid search."""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        cache_dir: Optional[Path] = None,
        pinecone_namespace: str = "tax-legislation",
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7
    ):
        """Initialize the retrieval service.
        
        Args:
            embedding_service: Service for generating and retrieving embeddings
            cache_dir: Directory to cache retrieval results
            pinecone_namespace: Namespace within the Pinecone index
            bm25_weight: Weight for BM25 scores in hybrid search (0-1)
            vector_weight: Weight for vector scores in hybrid search (0-1)
        """
        self.embedding_service = embedding_service
        self.pinecone_namespace = pinecone_namespace
        
        # Weights for hybrid search
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        
        # Normalize weights
        total_weight = self.bm25_weight + self.vector_weight
        self.bm25_weight /= total_weight
        self.vector_weight /= total_weight
        
        # Cache directory
        self.cache_dir = cache_dir
        if self.cache_dir and not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
        
        # BM25 index (built lazily)
        self.bm25_index = None
        self.bm25_docs = []
        self.doc_mapping = {}  # Map from BM25 index to document ID
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Preprocess text for BM25 indexing."""
        # Lowercase and tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphanumeric tokens
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token not in stop_words and token.isalnum()]
        
        return tokens
    
    def _build_bm25_index(self, force_rebuild: bool = False) -> None:
        """Build or rebuild the BM25 index."""
        if self.bm25_index is not None and not force_rebuild:
            return
            
        logger.info("Building BM25 index...")
        
        # Fetch all documents from Pinecone
        try:
            # Using a dummy vector to query all documents
            results = self.embedding_service.index.query(
                vector=[0] * 768,  # Dummy vector
                top_k=10000,  # Get as many as possible
                namespace=self.pinecone_namespace,
                include_metadata=True
            )
            
            # Extract documents and preprocess
            self.bm25_docs = []
            self.doc_mapping = {}
            
            for i, match in enumerate(tqdm(results.matches, desc="Processing documents for BM25")):
                if "content" in match.metadata:
                    processed_text = self._preprocess_text(match.metadata["content"])
                    self.bm25_docs.append(processed_text)
                    self.doc_mapping[i] = match.id
            
            # Build BM25 index
            self.bm25_index = BM25Okapi(self.bm25_docs)
            logger.info(f"BM25 index built with {len(self.bm25_docs)} documents")
            
        except Exception as e:
            logger.error(f"Error building BM25 index: {e}")
            raise
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        rebuild_bm25: bool = False
    ) -> List[RetrievalResult]:
        """Retrieve relevant documents using hybrid search.
        
        Args:
            query: Query text to find relevant documents for
            top_k: Number of results to return
            filters: Metadata filters to apply
            rebuild_bm25: Whether to force rebuild the BM25 index
            
        Returns:
            List of retrieval results
        """
        # Build BM25 index if needed
        self._build_bm25_index(force_rebuild=rebuild_bm25)
        
        # Get vector search results
        vector_results = self._vector_search(query, top_k=top_k, filters=filters)
        
        # Get BM25 search results
        bm25_results = self._bm25_search(query, top_k=top_k)
        
        # Combine results using hybrid ranking
        combined_results = self._hybrid_ranking(
            query, vector_results, bm25_results, top_k=top_k
        )
        
        return combined_results
    
    def _vector_search(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Perform vector search.
        
        Returns a dictionary mapping document ID to result data.
        """
        try:
            # Get similar documents from embedding service
            matches = self.embedding_service.query_similar(
                query_text=query,
                top_k=top_k * 2,  # Get more to ensure we have enough after filtering
                filters=filters
            )
            
            # Convert to dictionary for easier lookup
            results = {}
            for match in matches:
                # Skip if no content
                if "content" not in match.metadata:
                    continue
                    
                results[match.id] = {
                    "content": match.metadata["content"],
                    "metadata": {k: v for k, v in match.metadata.items() if k != "content"},
                    "score": match.score,
                    "document_id": match.id,
                    "retrieval_method": "vector"
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return {}
    
    def _bm25_search(self, query: str, top_k: int = 5) -> Dict[str, Dict[str, Any]]:
        """Perform BM25 search.
        
        Returns a dictionary mapping document ID to result data.
        """
        if self.bm25_index is None:
            logger.warning("BM25 index not built, returning empty results")
            return {}
            
        try:
            # Preprocess query
            query_tokens = self._preprocess_text(query)
            
            # Get BM25 scores
            bm25_scores = self.bm25_index.get_scores(query_tokens)
            
            # Get top-k indices
            top_indices = np.argsort(bm25_scores)[-top_k * 2:][::-1]  # Get more to ensure we have enough after filtering
            
            # Convert to dictionary for easier lookup
            results = {}
            for idx in top_indices:
                # Skip if score is 0
                if bm25_scores[idx] == 0:
                    continue
                    
                doc_id = self.doc_mapping.get(idx)
                if doc_id is None:
                    continue
                
                # Query Pinecone to get the document content and metadata
                pinecone_result = self.embedding_service.index.fetch(
                    ids=[doc_id],
                    namespace=self.pinecone_namespace
                )
                
                if doc_id not in pinecone_result.vectors:
                    continue
                    
                vector_data = pinecone_result.vectors[doc_id]
                metadata = vector_data.metadata
                
                # Skip if no content
                if "content" not in metadata:
                    continue
                
                # Normalize BM25 score to 0-1 range for the current batch
                # Max BM25 score in this batch
                max_score = bm25_scores[top_indices[0]]
                normalized_score = bm25_scores[idx] / max_score if max_score > 0 else 0
                
                results[doc_id] = {
                    "content": metadata["content"],
                    "metadata": {k: v for k, v in metadata.items() if k != "content"},
                    "score": normalized_score,
                    "document_id": doc_id,
                    "retrieval_method": "bm25"
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in BM25 search: {e}")
            return {}
    
    def _hybrid_ranking(
        self,
        query: str,
        vector_results: Dict[str, Dict[str, Any]],
        bm25_results: Dict[str, Dict[str, Any]],
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """Combine vector and BM25 results with weighted scores."""
        # Combine results
        combined = {}
        
        # Add vector results
        for doc_id, result in vector_results.items():
            combined[doc_id] = {
                "content": result["content"],
                "metadata": result["metadata"],
                "score": result["score"] * self.vector_weight,  # Apply vector weight
                "document_id": doc_id,
                "vector_score": result["score"],
                "bm25_score": 0,
                "retrieval_method": "hybrid"
            }
        
        # Add or update with BM25 results
        for doc_id, result in bm25_results.items():
            if doc_id in combined:
                # Update existing entry
                combined[doc_id]["score"] += result["score"] * self.bm25_weight
                combined[doc_id]["bm25_score"] = result["score"]
            else:
                # Add new entry
                combined[doc_id] = {
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "score": result["score"] * self.bm25_weight,  # Apply BM25 weight
                    "document_id": doc_id,
                    "vector_score": 0,
                    "bm25_score": result["score"],
                    "retrieval_method": "hybrid"
                }
        
        # Sort by combined score and take top_k
        sorted_results = sorted(
            combined.values(), 
            key=lambda x: x["score"], 
            reverse=True
        )[:top_k]
        
        # Convert to RetrievalResult objects
        return [
            RetrievalResult(
                content=result["content"],
                metadata=result["metadata"],
                score=result["score"],
                document_id=result["document_id"],
                retrieval_method=result["retrieval_method"]
            )
            for result in sorted_results
        ]
    
    def retrieve_with_rerank(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        rebuild_bm25: bool = False,
        rerank_top_k: int = 20
    ) -> List[RetrievalResult]:
        """Retrieve with an additional reranking step to improve relevance.
        
        First retrieves a larger set of documents, then reranks them
        based on relevance to the query.
        """
        # Retrieve more documents than needed for reranking
        initial_results = self.retrieve(
            query=query,
            top_k=rerank_top_k,  # Get more documents for reranking
            filters=filters,
            rebuild_bm25=rebuild_bm25
        )
        
        if not initial_results:
            return []
            
        # Simple reranking based on lexical overlap with query
        # (A more sophisticated reranker would use a model, but this is a simpler approach)
        reranked = self._simple_rerank(query, initial_results)
        
        # Take top_k from reranked results
        return reranked[:top_k]
    
    def _simple_rerank(
        self, query: str, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """Simple reranking based on lexical overlap with query."""
        # Preprocess query
        query_terms = set(self._preprocess_text(query))
        
        # Calculate overlap scores
        scored_results = []
        for result in results:
            # Preprocess content
            content_terms = set(self._preprocess_text(result.content))
            
            # Calculate overlap
            overlap = len(query_terms.intersection(content_terms)) / max(1, len(query_terms))
            
            # Combine with original score (weighted average)
            new_score = (result.score * 0.7) + (overlap * 0.3)
            
            # Create new result with updated score
            scored_results.append(
                RetrievalResult(
                    content=result.content,
                    metadata=result.metadata,
                    score=new_score,
                    document_id=result.document_id,
                    retrieval_method="reranked"
                )
            )
        
        # Sort by new score
        return sorted(scored_results, key=lambda x: x.score, reverse=True)
    
    def retrieve_by_id(self, document_id: str) -> Optional[RetrievalResult]:
        """Retrieve a document by ID.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            RetrievalResult if found, None otherwise
        """
        try:
            # Query Pinecone to get the document
            pinecone_result = self.embedding_service.index.fetch(
                ids=[document_id],
                namespace=self.pinecone_namespace
            )
            
            if document_id not in pinecone_result.vectors:
                logger.warning(f"Document not found: {document_id}")
                return None
                
            vector_data = pinecone_result.vectors[document_id]
            metadata = vector_data.metadata
            
            # Skip if no content
            if "content" not in metadata:
                logger.warning(f"Document has no content: {document_id}")
                return None
            
            return RetrievalResult(
                content=metadata["content"],
                metadata={k: v for k, v in metadata.items() if k != "content"},
                score=1.0,  # Default score for direct retrieval
                document_id=document_id,
                retrieval_method="direct"
            )
            
        except Exception as e:
            logger.error(f"Error retrieving document by ID: {e}")
            return None


# Testing code
if __name__ == "__main__":
    # This will allow running this file directly for testing
    import sys
    sys.path.append(".")  # Add the current directory to the path
    
    # Sample testing code
    from app.services.document_processor import DocumentProcessor
    from app.services.embedding_service import EmbeddingService
    import os
    from pathlib import Path
    
    # Set up test environment
    os.environ["GOOGLE_AI_API_KEY"] = "your-api-key-here"  # Replace with actual key for testing
    os.environ["PINECONE_API_KEY"] = "your-pinecone-key-here"  # Replace with actual key for testing
    
    # Create cache directories
    cache_dir = Path("embedding_cache")
    if not cache_dir.exists():
        cache_dir.mkdir()
        
    retrieval_cache_dir = Path("retrieval_cache")
    if not retrieval_cache_dir.exists():
        retrieval_cache_dir.mkdir()
    
    # Initialize services
    embedding_service = EmbeddingService(
        pinecone_index_name="taxpal-test",
        pinecone_namespace="test-namespace",
        batch_size=5,
        cache_dir=cache_dir
    )
    
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        cache_dir=retrieval_cache_dir,
        pinecone_namespace="test-namespace",
        bm25_weight=0.3,
        vector_weight=0.7
    )
    
    # Test queries
    test_queries = [
        "What is the corporate tax rate in Ireland?",
        "How are capital gains taxed?",
        "What are the VAT rates?",
        "Income tax brackets for individuals"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Get results
        results = retrieval_service.retrieve_with_rerank(
            query=query,
            top_k=3,
            rebuild_bm25=True  # Force rebuild for testing
        )
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results):
            print(f"Result {i+1} - ID: {result.document_id}")
            print(f"Score: {result.score:.4f}")
            print(f"Method: {result.retrieval_method}")
            
            # Print section information if available
            section_id = result.metadata.get("section_id")
            section_title = result.metadata.get("section_title")
            if section_id and section_title:
                print(f"Section: {section_id} - {section_title}")
            
            # Print a snippet of the content
            content_snippet = result.content[:200] + "..." if len(result.content) > 200 else result.content
            print(f"Content: {content_snippet}")
            print()