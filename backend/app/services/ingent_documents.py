# ingest_documents.py
import asyncio
import os
import json
from app.services.document_processor import chunk_document
from app.services.vector_db_service import index_documents

async def ingest_sample_document():
    """Ingest a sample tax document for testing."""
    # Sample document content
    sample_document = """
    Taxes Consolidation Act 1997
    
    Section 15: Income Tax Rates
    
    (a) 20 per cent on the first €40,000 of taxable income for single persons
    (b) 40 per cent on the balance of taxable income
    For married couples jointly assessed, the 20 per cent rate applies to the first €49,000.
    Additional rate bands may apply for certain categories of taxpayers as defined in Sections 15-18.
    
    Section 121: Benefit-in-Kind Taxation
    
    Section 121 of the Taxes Consolidation Act 1997 covers the general provisions for benefit-in-kind taxation of company vehicles.
    The taxable value of the benefit is calculated based on the original market value of the car and the business mileage.
    
    Section 380K: Electric Vehicle Relief
    
    Section 380K of the Taxes Consolidation Act 1997, as amended by the Finance Act 2023, provides for vehicle registration tax (VRT) relief for certain categories of electric vehicles.
    """
    
    # Create metadata for the document
    metadata = {
        "id": "tca1997",
        "source": "Taxes Consolidation Act 1997",
        "year": 1997,
        "type": "primary_legislation"
    }
    
    # Chunk the document
    chunks = chunk_document(
        text=sample_document,
        metadata=metadata,
        chunk_size=1000,
        chunk_overlap=200
    )
    
    print(f"Created {len(chunks)} chunks from sample document")
    
    # Index the chunks
    success = await index_documents(chunks)
    
    if success:
        print("Successfully indexed sample document")
    else:
        print("Failed to index sample document")

if __name__ == "__main__":
    asyncio.run(ingest_sample_document())