import re
import nltk
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import PyPDF2
import logging
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document with metadata."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    section_id: Optional[str] = None
    section_title: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "metadata": self.metadata,
            "section_id": self.section_id,
            "section_title": self.section_title
        }

class DocumentProcessor:
    """Service for processing documents into chunks for the RAG pipeline."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize the document processor.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Try to download NLTK data, but handle if already present
        try:
            nltk.download('punkt', quiet=True)
        except:
            logger.info("NLTK punkt already downloaded")
    
    def process_document(self, file_path: Path, metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """Process a document into chunks.
        
        Args:
            file_path: Path to the document file
            metadata: Optional metadata about the document
            
        Returns:
            List of DocumentChunk objects
        """
        if metadata is None:
            metadata = {}
            
        # Add basic file metadata
        metadata.update({
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_type": file_path.suffix.lower(),
        })
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = self._extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.txt', '.md']:
            text = file_path.read_text(encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Detect if this is a legislative document
        is_legislative = self._is_legislative_document(text, file_path.name)
        
        if is_legislative:
            logger.info(f"Processing {file_path.name} as a legislative document")
            return self._process_legislative_document(text, metadata)
        else:
            logger.info(f"Processing {file_path.name} with standard chunking")
            return self._process_standard_document(text, metadata)
    
    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from a PDF file."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def _is_legislative_document(self, text: str, filename: str) -> bool:
        """Determine if a document is legislative in nature."""
        # Check filename for indicators
        legislative_indicators = ['act', 'regulation', 'statutory', 'law', 'legislation', 'tax_code']
        if any(indicator in filename.lower() for indicator in legislative_indicators):
            return True
        
        # Check content for legislative patterns
        legislative_patterns = [
            r'section \d+',
            r'§ \d+',
            r'article \d+',
            r'chapter \d+',
            r'part \d+',
            r'amendment \d+',
            r'schedule \d+'
        ]
        
        # Sample the first 5000 characters for efficiency
        sample_text = text[:5000].lower()
        for pattern in legislative_patterns:
            if re.search(pattern, sample_text):
                return True
        
        return False
    
    def _process_standard_document(self, text: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Process a standard document using fixed-size chunking with overlap."""
        chunks = []
        sentences = nltk.sent_tokenize(text)
        
        current_chunk = []
        current_size = 0
        chunk_id = 1
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            # If adding this sentence would exceed chunk size and we have content,
            # create a new chunk
            if current_size + sentence_len > self.chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_id": chunk_id,
                    "chunk_type": "standard",
                    "char_length": len(chunk_text)
                })
                
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    metadata=chunk_metadata,
                    chunk_id=f"{metadata.get('file_name', 'doc')}_{chunk_id}"
                ))
                
                # Keep some sentences for overlap
                overlap_tokens = []
                overlap_size = 0
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= self.chunk_overlap:
                        overlap_tokens.insert(0, s)
                        overlap_size += len(s) + 1  # +1 for space
                    else:
                        break
                
                current_chunk = overlap_tokens
                current_size = overlap_size
                chunk_id += 1
            
            current_chunk.append(sentence)
            current_size += sentence_len + 1  # +1 for space
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": chunk_id,
                "chunk_type": "standard",
                "char_length": len(chunk_text)
            })
            
            chunks.append(DocumentChunk(
                content=chunk_text,
                metadata=chunk_metadata,
                chunk_id=f"{metadata.get('file_name', 'doc')}_{chunk_id}"
            ))
        
        return chunks
    
    def _process_legislative_document(self, text: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Process a legislative document using semantic chunking by sections."""
        # Common patterns for section headers in Irish tax legislation
        section_patterns = [
            # Match "Section X. Title" format
            r'(?:Section|SECTION|Sec\.|SEC\.) (\d+[A-Z]?)\.\s+(.*?)(?=\n)',
            # Match "X. Title" format
            r'(?<!\w)(\d+[A-Z]?)\.\s+(.*?)(?=\n)',
            # Match "Article X - Title" format
            r'(?:Article|ARTICLE) (\d+[A-Z]?)\s*[\-–—]\s*(.*?)(?=\n)',
            # Match "Part X - Title" format
            r'(?:Part|PART) (\d+[A-Z]?)\s*[\-–—]\s*(.*?)(?=\n)',
            # Match "Chapter X. Title" format
            r'(?:Chapter|CHAPTER) (\d+[A-Z]?)\.\s+(.*?)(?=\n)'
        ]
        
        # Find all section matches
        sections = []
        for pattern in section_patterns:
            for match in re.finditer(pattern, text):
                section_id = match.group(1)
                section_title = match.group(2).strip()
                start_pos = match.start()
                sections.append((section_id, section_title, start_pos))
        
        # Sort sections by their position in the text
        sections.sort(key=lambda x: x[2])
        
        # If no sections found, fall back to standard chunking
        if not sections:
            logger.info("No sections detected, falling back to standard chunking")
            return self._process_standard_document(text, metadata)
        
        chunks = []
        for i, (section_id, section_title, start_pos) in enumerate(sections):
            # Determine section end
            if i < len(sections) - 1:
                end_pos = sections[i + 1][2]
            else:
                end_pos = len(text)
            
            # Extract section text (including the header)
            section_text = text[start_pos:end_pos].strip()
            
            # Skip empty sections
            if not section_text:
                continue
                
            # If section is very long, apply sub-chunking
            if len(section_text) > self.chunk_size * 2:
                sub_chunks = self._chunk_large_section(section_text, section_id, section_title, metadata)
                chunks.extend(sub_chunks)
            else:
                # Create a single chunk for this section
                section_metadata = metadata.copy()
                section_metadata.update({
                    "chunk_type": "legislative_section",
                    "section_id": section_id,
                    "section_title": section_title,
                    "char_length": len(section_text)
                })
                
                chunk_id = f"{metadata.get('file_name', 'doc')}_S{section_id}"
                chunks.append(DocumentChunk(
                    content=section_text,
                    metadata=section_metadata,
                    chunk_id=chunk_id,
                    section_id=section_id,
                    section_title=section_title
                ))
        
        # If we couldn't extract any chunks, fall back to standard method
        if not chunks:
            logger.warning("Section chunking produced no results, falling back to standard chunking")
            return self._process_standard_document(text, metadata)
            
        return chunks
    
    def _chunk_large_section(
        self, section_text: str, section_id: str, section_title: str, metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """Break a large section into multiple chunks while preserving context."""
        sentences = nltk.sent_tokenize(section_text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        sub_chunk_id = 1
        
        # Always include the section header in each chunk for context
        section_header = f"Section {section_id}. {section_title}"
        header_size = len(section_header)
        
        for sentence in sentences:
            # Skip the sentence if it's part of the header we're manually adding
            if section_header in sentence and len(current_chunk) == 0:
                continue
                
            sentence_len = len(sentence)
            
            # If this sentence would make the chunk too big and we already have content
            if current_size + sentence_len > (self.chunk_size - header_size) and current_chunk:
                # Combine the header with the chunk content
                chunk_text = f"{section_header}\n\n" + " ".join(current_chunk)
                
                # Create metadata for this sub-chunk
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_type": "legislative_subsection",
                    "section_id": section_id,
                    "section_title": section_title,
                    "sub_chunk_id": sub_chunk_id,
                    "char_length": len(chunk_text)
                })
                
                # Create the chunk
                chunk_id = f"{metadata.get('file_name', 'doc')}_S{section_id}_{sub_chunk_id}"
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    metadata=chunk_metadata,
                    chunk_id=chunk_id,
                    section_id=section_id,
                    section_title=section_title
                ))
                
                # Reset for next chunk
                current_chunk = []
                current_size = 0
                sub_chunk_id += 1
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_size += sentence_len + 1  # +1 for space
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = f"{section_header}\n\n" + " ".join(current_chunk)
            
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_type": "legislative_subsection",
                "section_id": section_id,
                "section_title": section_title,
                "sub_chunk_id": sub_chunk_id,
                "char_length": len(chunk_text)
            })
            
            chunk_id = f"{metadata.get('file_name', 'doc')}_S{section_id}_{sub_chunk_id}"
            chunks.append(DocumentChunk(
                content=chunk_text,
                metadata=chunk_metadata,
                chunk_id=chunk_id,
                section_id=section_id,
                section_title=section_title
            ))
        
        return chunks


# Testing code
if __name__ == "__main__":
    # Set up test directory
    test_dir = Path("test_docs")
    if not test_dir.exists():
        test_dir.mkdir()
        
    # Create a sample text file for testing
    test_file = test_dir / "sample_tax_legislation.txt"
    with open(test_file, "w") as f:
        f.write("""
Section 1. Income Tax Provisions

1.1 For the purposes of this Act, "taxable income" means the aggregate of:
(a) income from employment, profession, or vocation;
(b) income from property or investments; and
(c) any other income not specifically exempted.

1.2 The rate of tax for individuals shall be:
(a) 20% on the first €35,300 of taxable income; and
(b) 40% on the balance.

Section 2. Corporate Tax Provisions

2.1 The standard rate of corporation tax shall be 12.5% on trading income.

2.2 A rate of 25% shall apply to non-trading income, including:
(a) rental income from land and buildings;
(b) income from foreign trades; and
(c) dividend income.

Section 3. Capital Gains Tax

3.1 Capital gains tax shall be charged at 33% on the disposal of assets.

3.2 The following exemptions shall apply:
(a) the principal private residence of an individual;
(b) agricultural land in certain circumstances;
(c) transfers on death.

Section 4. Value Added Tax

4.1 The standard rate of value added tax shall be 23%.

4.2 Reduced rates shall apply to the following:
(a) 13.5% for fuel, electricity, and certain services;
(b) 9% for newspapers, hotels, and certain foods;
(c) 0% for exports, children's clothing, and certain foods.
""")
    
    # Initialize the processor
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
    
    # Test processing
    metadata = {
        "document_type": "legislation",
        "jurisdiction": "Ireland",
        "year": 2023,
        "title": "Sample Tax Legislation"
    }
    
    chunks = processor.process_document(test_file, metadata)
    
    # Print results
    print(f"\nProcessed {test_file.name} into {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1} - ID: {chunk.chunk_id}")
        print(f"Section: {chunk.section_id} - {chunk.section_title}")
        print(f"Metadata: {chunk.metadata}")
        print(f"Content ({len(chunk.content)} chars): {chunk.content[:100]}...\n")