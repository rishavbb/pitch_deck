import PyPDF2
import fitz  # PyMuPDF
from PIL import Image
from typing import Dict, Any, List
import os
import io

class PDFExtractor:
    """Extract text content from PDF pitch decks."""
    
    def __init__(self):
        pass
    
    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text content and images from a PDF file.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict[str, Any]: Extracted content with metadata, text, and images
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
        
        try:
            # Extract text using PyPDF2
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
            
            # Extract images using PyMuPDF
            images = self._extract_images_from_pdf(file_path)
            
            return {
                'metadata': metadata,
                'pages': text_content,
                'full_text': full_text,
                'images': images,
                'extraction_success': True
            }
                
        except Exception as e:
            return {
                'metadata': {'file_name': os.path.basename(file_path), 'file_type': 'PDF'},
                'pages': [],
                'full_text': '',
                'images': [],
                'extraction_success': False,
                'error': str(e)
            }
    
    def _extract_images_from_pdf(self, file_path: str) -> List[Image.Image]:
        """
        Extract images from PDF using PyMuPDF.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            List[Image.Image]: List of PIL Image objects
        """
        images = []
        
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(file_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                
                # Get list of images on the page
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        pix = fitz.Pixmap(pdf_document, xref)
                        
                        # Convert to PIL Image
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            img_io = io.BytesIO(img_data)
                            pil_image = Image.open(img_io)
                            
                            # Filter out very small images (likely icons/decorations)
                            if pil_image.size[0] > 50 and pil_image.size[1] > 50:
                                images.append(pil_image)
                        
                        pix = None  # Free memory
                        
                    except Exception as e:
                        print(f"Warning: Could not extract image {img_index+1} from page {page_num+1}: {e}")
                        continue
            
            pdf_document.close()
            
        except Exception as e:
            print(f"Warning: Could not extract images from PDF: {e}")
        
        return images
