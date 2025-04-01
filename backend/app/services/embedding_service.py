from __future__ import annotations  # This allows forward references in type hints

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import numpy as np
import google.generativeai as genai
import pinecone
from dataclasses import dataclass, field
from tqdm import tqdm
import hashlib
from datetime import datetime
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# Add testing code
if __name__ == "__main__":
    # This will allow running this file directly for testing
    import sys
    sys.path.append(".")  # Add the current directory to the path
    
# Import our DocumentChunk class
from app.services.document_processor import DocumentChunk

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Result of embedding generation."""
    chunk_id: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "chunk_id": self.chunk_id,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def to_pinecone_format(self) -> Dict[str, Any]:
        """Convert to Pinecone upsert format."""
        return {
            "id": self.chunk_id,
            "values": self.embedding,
            "metadata": self.metadata
        }


class EmbeddingService:
    """Service for generating and storing embeddings."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        pinecone_api_key: Optional[str] = None,
        pinecone_index_name: str = "taxpal-embeddings",
        pinecone_namespace: str = "tax-legislation",
        batch_size: int = 10,
        cache_dir: Optional[Path] = None
    ):
        """Initialize the embedding service.
        
        Args:
            api_key: Google AI API key (will try to read from env if not provided)
            pinecone_api_key: Pinecone API key (will try to read from env if not provided)
            pinecone_index_name: Name of the Pinecone index to use
            pinecone_namespace: Namespace within the Pinecone index
            batch_size: Number of documents to process in each batch
            cache_dir: Directory to cache embeddings (if None, no caching)
        """
        # Set up Google AI API
        self.api_key = api_key or os.environ.get("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("Google AI API key is required.")
        
        genai.configure(api_key=self.api_key)
        self.embedding_model = "models/embedding-001"
        
        # Set up Pinecone
        self.pinecone_api_key = pinecone_api_key or os.environ.get("PINECONE_API_KEY")
        if not self.pinecone_api_key:
            raise ValueError("Pinecone API key is required.")
            
        self.pinecone_index_name = pinecone_index_name
        self.pinecone_namespace = pinecone_namespace
        
        # Initialize Pinecone
        pinecone.init(api_key=self.pinecone_api_key, environment="gcp-starter")
        
        # Check if the index exists, create it if not
        if self.pinecone_index_name not in pinecone.list_indexes():
            logger.info(f"Creating Pinecone index: {self.pinecone_index_name}")
            # Gemini embedding dimension is 768
            pinecone.create_index(
                name=self.pinecone_index_name,
                dimension=768,
                metric="cosine"
            )
        
        self.index = pinecone.Index(self.pinecone_index_name)
        
        # Batch processing settings
        self.batch_size = batch_size
        
        # Caching
        self.cache_dir = cache_dir
        if self.cache_dir and not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            # Use Google's Gemini embedding model
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document",
            )
            
            # Return embedding values
            return result["embedding"]
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def generate_embedding_async(self, text: str, session: aiohttp.ClientSession) -> List[float]:
        """Generate an embedding asynchronously.
        
        Args:
            text: Text to embed
            session: aiohttp session to use
            
        Returns:
            List of embedding values
        """
        # This requires an asynchronous implementation for the Google API
        # We'll use ThreadPoolExecutor to run the synchronous method in a separate thread
        with ThreadPoolExecutor() as executor:
            embedding = await asyncio.get_event_loop().run_in_executor(
                executor, self.generate_embedding, text
            )
            return embedding
    
    def _get_cache_path(self, chunk_id: str) -> Optional[Path]:
        """Get the cache file path for a chunk ID."""
        if not self.cache_dir:
            return None
            
        # Use a hash of the chunk ID as the filename
        chunk_hash = hashlib.md5(chunk_id.encode()).hexdigest()
        return self.cache_dir / f"{chunk_hash}.json"
    
    def _get_from_cache(self, chunk_id: str) -> Optional[EmbeddingResult]:
        """Try to get an embedding from the cache."""
        if not self.cache_dir:
            return None
            
        cache_path = self._get_cache_path(chunk_id)
        if cache_path and cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                return EmbeddingResult(**data)
            except Exception as e:
                logger.warning(f"Error reading from cache for {chunk_id}: {e}")
                return None
        return None
    
    def _save_to_cache(self, result: EmbeddingResult) -> None:
        """Save an embedding result to the cache."""
        if not self.cache_dir:
            return
            
        cache_path = self._get_cache_path(result.chunk_id)
        if cache_path:
            try:
                with open(cache_path, 'w') as f:
                    json.dump(result.to_dict(), f)
            except Exception as e:
                logger.warning(f"Error saving to cache for {result.chunk_id}: {e}")
    
    def process_chunks(self, chunks: List[DocumentChunk]) -> List[EmbeddingResult]:
        """Process a list of document chunks, generating embeddings and storing them.
        
        Args:
            chunks: List of DocumentChunk objects
            
        Returns:
            List of EmbeddingResult objects
        """
        results = []
        
        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i+self.batch_size]
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            
            # Store in Pinecone
            self._store_in_pinecone(batch_results)
            
            # Sleep to avoid rate limiting
            if i + self.batch_size < len(chunks):
                time.sleep(1)
        
        return results
    
    def _process_batch(self, chunks: List[DocumentChunk]) -> List[EmbeddingResult]:
        """Process a batch of document chunks."""
        results = []
        
        for chunk in tqdm(chunks, desc="Generating embeddings"):
            # Try to get from cache first
            cached_result = self._get_from_cache(chunk.chunk_id)
            if cached_result:
                logger.info(f"Using cached embedding for {chunk.chunk_id}")
                results.append(cached_result)
                continue
            
            # Generate embedding
            try:
                embedding = self.generate_embedding(chunk.content)
                
                # Create result
                result = EmbeddingResult(
                    chunk_id=chunk.chunk_id,
                    embedding=embedding,
                    metadata={
                        "content": chunk.content,
                        **chunk.metadata
                    }
                )
                
                # Save to cache
                self._save_to_cache(result)
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing chunk {chunk.chunk_id}: {e}")
        
        return results
    
    async def process_chunks_async(self, chunks: List[DocumentChunk]) -> List[EmbeddingResult]:
        """Process chunks asynchronously for better performance."""
        results = []
        
        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i+self.batch_size]
            batch_results = await self._process_batch_async(batch)
            results.extend(batch_results)
            
            # Store in Pinecone
            self._store_in_pinecone(batch_results)
            
            # Sleep to avoid rate limiting
            if i + self.batch_size < len(chunks):
                await asyncio.sleep(1)
        
        return results
    
    async def _process_batch_async(self, chunks: List[DocumentChunk]) -> List[EmbeddingResult]:
        """Process a batch of document chunks asynchronously."""
        results = []
        
        # Create a client session to reuse for all requests
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for chunk in chunks:
                # Try to get from cache first
                cached_result = self._get_from_cache(chunk.chunk_id)
                if cached_result:
                    logger.info(f"Using cached embedding for {chunk.chunk_id}")
                    results.append(cached_result)
                    continue
                
                # Create a task for this chunk
                task = self._process_chunk_async(chunk, session)
                tasks.append(task)
            
            # Wait for all tasks to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and add to results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Error in async processing: {result}")
                else:
                    results.append(result)
        
        return results
    
    async def _process_chunk_async(
        self, chunk: DocumentChunk, session: aiohttp.ClientSession
    ) -> EmbeddingResult:
        """Process a single chunk asynchronously."""
        try:
            # Generate embedding
            embedding = await self.generate_embedding_async(chunk.content, session)
            
            # Create result
            result = EmbeddingResult(
                chunk_id=chunk.chunk_id,
                embedding=embedding,
                metadata={
                    "content": chunk.content,
                    **chunk.metadata
                }
            )
            
            # Save to cache
            self._save_to_cache(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk.chunk_id}: {e}")
            raise
    
    def _store_in_pinecone(self, results: List[EmbeddingResult]) -> None:
        """Store embedding results in Pinecone."""
        if not results:
            return
            
        try:
            # Convert to Pinecone format
            vectors = [result.to_pinecone_format() for result in results]
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=vectors,
                namespace=self.pinecone_namespace
            )
            
            logger.info(f"Successfully stored {len(vectors)} vectors in Pinecone")
            
        except Exception as e:
            logger.error(f"Error storing in Pinecone: {e}")
            raise
    
    def query_similar(
        self, 
        query_text: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query for similar documents.
        
        Args:
            query_text: Text to find similar documents for
            top_k: Number of results to return
            filters: Metadata filters to apply
            
        Returns:
            List of similar documents with scores
        """
        try:
            # Generate embedding for the query
            query_embedding = self.generate_embedding(query_text)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=self.pinecone_namespace,
                filter=filters,
                include_metadata=True
            )
            
            return results.matches
            
        except Exception as e:
            logger.error(f"Error querying similar documents: {e}")
            raise
    
    def delete_by_filter(self, filter: Dict[str, Any]) -> int:
        """Delete embeddings by filter.
        
        Args:
            filter: Metadata filter to apply
            
        Returns:
            Number of deleted items
        """
        try:
            # Get matching IDs
            query_response = self.index.query(
                vector=[0] * 768,  # Dummy vector
                top_k=10000,  # Get as many as possible
                namespace=self.pinecone_namespace,
                filter=filter,
                include_metadata=False
            )
            
            # Extract IDs
            ids = [match.id for match in query_response.matches]
            
            if not ids:
                logger.info(f"No matches found for filter: {filter}")
                return 0
            
            # Delete by IDs in batches
            deleted_count = 0
            batch_size = 100
            
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i+batch_size]
                self.index.delete(ids=batch_ids, namespace=self.pinecone_namespace)
                deleted_count += len(batch_ids)
            
            logger.info(f"Deleted {deleted_count} embeddings with filter: {filter}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting embeddings: {e}")
            raise


# Testing code
if __name__ == "__main__":
    # Sample testing code
    from app.services.document_processor import DocumentProcessor, DocumentChunk
    import os
    
    # Set up test environment
    os.environ["GOOGLE_AI_API_KEY"] = "your-api-key-here"  # Replace with actual key for testing
    os.environ["PINECONE_API_KEY"] = "your-pinecone-key-here"  # Replace with actual key for testing
    
    # Create a cache directory
    cache_dir = Path("embedding_cache")
    if not cache_dir.exists():
        cache_dir.mkdir()
    
    # Initialize services
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
    embedding_service = EmbeddingService(
        pinecone_index_name="taxpal-test",
        pinecone_namespace="test-namespace",
        batch_size=5,
        cache_dir=cache_dir
    )
    
    # Test processing and embedding
    test_dir = Path("test_docs")
    if test_dir.exists():
        test_file = test_dir / "sample_tax_legislation.txt"
        if test_file.exists():
            print(f"Processing test file: {test_file}")
            
            # Process into chunks
            metadata = {
                "document_type": "legislation",
                "jurisdiction": "Ireland",
                "year": 2023,
                "title": "Sample Tax Legislation"
            }
            chunks = processor.process_document(test_file, metadata)
            print(f"Generated {len(chunks)} chunks")
            
            # Generate embeddings (just for a few chunks to avoid API costs in testing)
            test_chunks = chunks[:2]  # Just test with 2 chunks
            results = embedding_service.process_chunks(test_chunks)
            
            print(f"\nGenerated {len(results)} embeddings")
            for result in results:
                print(f"Chunk ID: {result.chunk_id}")
                print(f"Embedding dimensions: {len(result.embedding)}")
                print(f"First 5 values: {result.embedding[:5]}")
                print()
            
            # Test query
            print("Testing query...")
            query_text = "What is the corporate tax rate in Ireland?"
            similar_docs = embedding_service.query_similar(query_text, top_k=2)
            
            print(f"Found {len(similar_docs)} similar documents:")
            for i, doc in enumerate(similar_docs):
                print(f"Match {i+1} - ID: {doc.id}")
                print(f"Score: {doc.score}")
                print(f"Text: {doc.metadata.get('content', '')[:100]}...")
                print()
        else:
            print(f"Test file not found: {test_file}")
    else:
        print(f"Test directory not found: {test_dir}")
        print("Please run the document_processor.py file first to create test data")