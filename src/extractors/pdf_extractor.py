import PyPDF2
from typing import Dict, Any
import os

class PDFExtractor:
    """Extract text content from PDF pitch decks."""
    
    def __init__(self):
        pass
    
    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict[str, Any]: Extracted content with metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'file_name': os.path.basename(file_path),
                    'file_type': 'PDF',
                    'num_pages': len(pdf_reader.pages),
                    'file_size': os.path.getsize(file_path)
                }
                
                # Extract text from all pages
                text_content = []
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_content.append({
                                'page': page_num,
                                'content': page_text.strip()
                            })
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {page_num}: {e}")
                
                # Combine all text
                full_text = '\n\n'.join([page['content'] for page in text_content])
                
                return {
                    'metadata': metadata,
                    'pages': text_content,
                    'full_text': full_text,
                    'extraction_success': True
                }
                
        except Exception as e:
            return {
                'metadata': {'file_name': os.path.basename(file_path), 'file_type': 'PDF'},
                'pages': [],
                'full_text': '',
                'extraction_success': False,
                'error': str(e)
            }
