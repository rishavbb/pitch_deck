from pptx import Presentation
from typing import Dict, Any
import os

class PPTExtractor:
    """Extract text content from PowerPoint pitch decks."""
    
    def __init__(self):
        pass
    
    def extract_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text content from a PowerPoint file.
        
        Args:
            file_path (str): Path to the PPT/PPTX file
            
        Returns:
            Dict[str, Any]: Extracted content with metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PowerPoint file not found: {file_path}")
        
        if not file_path.lower().endswith(('.ppt', '.pptx')):
            raise ValueError("File must be a PowerPoint file (.ppt or .pptx)")
        
        try:
            presentation = Presentation(file_path)
            
            # Extract metadata
            metadata = {
                'file_name': os.path.basename(file_path),
                'file_type': 'PowerPoint',
                'num_slides': len(presentation.slides),
                'file_size': os.path.getsize(file_path)
            }
            
            # Extract text from all slides
            slide_content = []
            for slide_num, slide in enumerate(presentation.slides, 1):
                slide_text = []
                
                # Extract text from all shapes in the slide
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text.append(shape.text.strip())
                
                if slide_text:
                    slide_content.append({
                        'slide': slide_num,
                        'content': '\n'.join(slide_text)
                    })
            
            # Combine all text
            full_text = '\n\n'.join([slide['content'] for slide in slide_content])
            
            return {
                'metadata': metadata,
                'slides': slide_content,
                'full_text': full_text,
                'extraction_success': True
            }
            
        except Exception as e:
            return {
                'metadata': {'file_name': os.path.basename(file_path), 'file_type': 'PowerPoint'},
                'slides': [],
                'full_text': '',
                'extraction_success': False,
                'error': str(e)
            }
