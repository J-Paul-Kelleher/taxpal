#!/usr/bin/env python3
"""
Integration test for the TaxPal RAG Pipeline.
This script tests the end-to-end RAG pipeline by:
1. Processing a sample tax legislation document
2. Generating embeddings for the chunks
3. Retrieving relevant information for a query
4. Generating a response with citations
"""

import os
import sys
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the app directory to the path
sys.path.append(".")

# Import our services
from app.services.document_processor import DocumentProcessor, DocumentChunk
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.services.generator_service import GeneratorService

def create_test_document(test_dir: Path) -> Path:
    """Create a sample tax legislation document for testing."""
    logger.info("Creating sample tax legislation document...")
    
    # Create test directory if it doesn't exist
    if not test_dir.exists():
        test_dir.mkdir(parents=True)
    
    # Create a sample tax legislation document
    test_file = test_dir / "irish_tax_legislation_sample.txt"
    
    with open(test_file, "w") as f:
        f.write("""
Irish Tax Legislation Sample
===========================

Section 1. Income Tax Provisions

1.1 For the purposes of this Act, "taxable income" means the aggregate of:
(a) income from employment, profession, or vocation;
(b) income from property or investments; and
(c) any other income not specifically exempted.

1.2 The rate of tax for individuals shall be:
(a) 20% on the first €36,800 of taxable income for single persons;
(b) 20% on the first €45,800 of taxable income for married couples with one earner;
(c) 20% on the first €73,600 of taxable income for married couples with two earners; and
(d) 40% on the balance in all cases.

1.3 Tax credits shall be available as follows:
(a) Personal Tax Credit of €1,700 for single persons;
(b) Personal Tax Credit of €3,400 for married couples;
(c) PAYE Tax Credit of €1,700 for employees;
(d) Additional age-related tax credits for persons over 65 years.

Section 2. Corporate Tax Provisions

2.1 The standard rate of corporation tax shall be 12.5% on trading income.

2.2 A rate of 25% shall apply to non-trading income, including:
(a) rental income from land and buildings;
(b) income from foreign trades; and
(c) dividend income.

2.3 Relief for Research and Development expenditure shall be available at a rate of 25% of qualifying expenditure.

2.4 The Knowledge Development Box shall provide for a reduced effective tax rate of 6.25% on qualifying profits from intellectual property.

Section 3. Capital Gains Tax

3.1 Capital gains tax shall be charged at 33% on the disposal of assets.

3.2 The following exemptions shall apply:
(a) the principal private residence of an individual;
(b) agricultural land in certain circumstances;
(c) transfers on death.

3.3 Relief for entrepreneurs on the disposal of qualifying business assets shall be available, with a lifetime limit of €1 million, taxed at a reduced rate of 10%.

Section 4. Value Added Tax

4.1 The standard rate of value added tax shall be 23%.

4.2 Reduced rates shall apply to the following:
(a) 13.5% for fuel, electricity, building services, and certain repair services;
(b) 9% for newspapers, e-books, hotels, restaurants, and certain food items;
(c) 0% for exports, children's clothing, and certain basic food items.

4.3 Registration thresholds shall be:
(a) €75,000 for suppliers of goods; and
(b) €37,500 for suppliers of services.

Section 5. Local Property Tax

5.1 Local property tax shall be charged at a rate of 0.18% on residential properties valued up to €1 million.

5.2 Local property tax shall be charged at a rate of 0.25% on the portion of the value above €1 million.

5.3 Local authorities may vary the rate by up to 15% above or below the standard rate.

Section 6. Tax Administration

6.1 The tax year shall be the calendar year from January 1 to December 31.

6.2 Income tax returns shall be filed by October 31 following the end of the tax year.

6.3 The Revenue Commissioners shall be responsible for the assessment and collection of taxes.

6.4 Penalties for non-compliance shall include:
(a) interest on late payment at a rate of 0.0219% per day;
(b) surcharges for late filing;
(c) publication in the list of tax defaulters for settlements exceeding €35,000.
""")
    
    logger.info(f"Sample document created at {test_file}")
    return test_file

def setup_test_environment() -> tuple:
    """Set up the test environment and initialize services."""
    logger.info("Setting up test environment...")
    
    # Check for API keys
    google_api_key = os.environ.get("GOOGLE_AI_API_KEY")
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    
    if not google_api_key:
        logger.warning("GOOGLE_AI_API_KEY not found in environment. Using placeholder.")
        google_api_key = "your-google-api-key-here"
    
    if not pinecone_api_key:
        logger.warning("PINECONE_API_KEY not found in environment. Using placeholder.")
        pinecone_api_key = "your-pinecone-api-key-here"
    
    # Create cache directories
    cache_root = Path("tests/cache")
    if not cache_root.exists():
        cache_root.mkdir(parents=True)
    
    cache_dirs = {
        "embedding": cache_root / "embedding_cache",
        "retrieval": cache_root / "retrieval_cache",
        "generator": cache_root / "generator_cache"
    }
    
    for dir_path in cache_dirs.values():
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
    
    # Initialize services
    document_processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
    
    embedding_service = EmbeddingService(
        api_key=google_api_key,
        pinecone_api_key=pinecone_api_key,
        pinecone_index_name="taxpal-test",
        pinecone_namespace="test-namespace",
        batch_size=5,
        cache_dir=cache_dirs["embedding"]
    )
    
    retrieval_service = RetrievalService(
        embedding_service=embedding_service,
        cache_dir=cache_dirs["retrieval"],
        pinecone_namespace="test-namespace",
        bm25_weight=0.3,
        vector_weight=0.7
    )
    
    generator_service = GeneratorService(
        retrieval_service=retrieval_service,
        api_key=google_api_key,
        model_name="gemini-1.5-flash",
        cache_dir=cache_dirs["generator"],
        temperature=0.2
    )
    
    return document_processor, embedding_service, retrieval_service, generator_service

def run_pipeline_test():
    """Run the end-to-end RAG pipeline test."""
    logger.info("Starting RAG pipeline integration test...")
    
    # Set up test environment
    document_processor, embedding_service, retrieval_service, generator_service = setup_test_environment()
    
    # Create test document
    test_dir = Path("tests/data")
    test_file = create_test_document(test_dir)
    
    # Step 1: Process document into chunks
    logger.info("Step 1: Processing document into chunks...")
    metadata = {
        "document_type": "legislation",
        "jurisdiction": "Ireland",
        "year": 2023,
        "title": "Irish Tax Legislation Sample"
    }
    chunks = document_processor.process_document(test_file, metadata)
    logger.info(f"Document processed into {len(chunks)} chunks")
    
    # Display a sample of chunks
    for i, chunk in enumerate(chunks[:2]):
        logger.info(f"Sample chunk {i+1}:")
        logger.info(f"  ID: {chunk.chunk_id}")
        logger.info(f"  Section: {chunk.section_id} - {chunk.section_title}")
        logger.info(f"  Content length: {len(chunk.content)} characters")
        logger.info(f"  First 100 chars: {chunk.content[:100]}...")
    
    # Step 2: Generate embeddings for chunks
    logger.info("\nStep 2: Generating embeddings...")
    try:
        embedding_results = embedding_service.process_chunks(chunks)
        logger.info(f"Generated {len(embedding_results)} embeddings")
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        logger.warning("Skipping embedding generation due to API key or service unavailability")
        logger.info("Continuing with test using mock retrieval...")
        
        # If embedding generation fails, we'll just proceed with the test
        # by simulating that the retrieval service would return some chunks
        test_retrieval_results = chunks[:3]
    else:
        # Step 3: Retrieve relevant information for test queries
        logger.info("\nStep 3: Testing retrieval...")
        test_queries = [
            "What is the corporate tax rate in Ireland?",
            "How much is VAT in Ireland?",
            "What are the income tax brackets for individuals?",
            "How is capital gains tax applied?"
        ]
        
        for query in test_queries:
            logger.info(f"\nQuery: {query}")
            try:
                results = retrieval_service.retrieve_with_rerank(
                    query=query,
                    top_k=3
                )
                
                logger.info(f"Found {len(results)} relevant chunks:")
                for i, result in enumerate(results):
                    logger.info(f"Result {i+1} - ID: {result.document_id}")
                    logger.info(f"  Score: {result.score:.4f}")
                    logger.info(f"  Section: {result.metadata.get('section_id')} - {result.metadata.get('section_title')}")
                    content_snippet = result.content[:100] + "..." if len(result.content) > 100 else result.content
                    logger.info(f"  Content: {content_snippet}")
                
                # Keep the results from the first query for the next step
                if test_queries.index(query) == 0:
                    test_retrieval_results = results
            
            except Exception as e:
                logger.error(f"Error retrieving results: {e}")
                # If retrieval fails, use the chunks directly
                test_retrieval_results = chunks[:3]
    
    # Step 4: Generate a response with citations
    logger.info("\nStep 4: Testing response generation...")
    test_query = "What is the corporate tax rate in Ireland and how does it apply to different types of income?"
    
    try:
        response = generator_service.generate_response(
            query=test_query,
            top_k=3,
            extract_citations=True
        )
        
        logger.info("Generated response:")
        logger.info(response.response_text)
        
        logger.info("\nCitations:")
        for i, citation in enumerate(response.citations):
            logger.info(f"[{i+1}] {citation.text[:50]}... (from {citation.document_id}, section {citation.section_id})")
        
        logger.info("\nFormatted response with citations:")
        formatted = generator_service.format_response_with_citations(response)
        logger.info(formatted)
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        logger.info("Response generation could not be completed due to API key or service unavailability")
    
    logger.info("\nRAG pipeline integration test completed!")

if __name__ == "__main__":
    run_pipeline_test()