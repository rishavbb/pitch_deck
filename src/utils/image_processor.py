import base64
import io
from PIL import Image
from typing import List, Dict, Any, Optional

class ImageProcessor:
    """Utility class for processing and encoding images for LLM analysis."""
    
    def __init__(self):
        self.max_image_size = (1024, 1024)  # Max dimensions for images
        self.supported_formats = ['PNG', 'JPEG', 'JPG', 'WEBP']
    
    def resize_image(self, image: Image.Image, max_size: tuple = None) -> Image.Image:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image (Image.Image): PIL Image object
            max_size (tuple): Maximum (width, height) dimensions
            
        Returns:
            Image.Image: Resized image
        """
        if max_size is None:
            max_size = self.max_image_size
        
        # Calculate new size maintaining aspect ratio
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    def image_to_base64(self, image: Image.Image, format: str = 'PNG') -> str:
        """
        Convert PIL Image to base64 string.
        
        Args:
            image (Image.Image): PIL Image object
            format (str): Output format (PNG, JPEG, etc.)
            
        Returns:
            str: Base64 encoded image string
        """
        buffer = io.BytesIO()
        
        # Convert RGBA to RGB for JPEG format
        if format.upper() == 'JPEG' and image.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
            image = background
        
        image.save(buffer, format=format, quality=85, optimize=True)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    def prepare_images_for_llm(self, images: List[Image.Image]) -> List[Dict[str, Any]]:
        """
        Prepare a list of images for LLM analysis by resizing and encoding.
        
        Args:
            images (List[Image.Image]): List of PIL Image objects
            
        Returns:
            List[Dict[str, Any]]: List of image data dictionaries for LLM
        """
        prepared_images = []
        
        for i, image in enumerate(images):
            try:
                # Resize image
                resized_image = self.resize_image(image)
                
                # Convert to base64
                base64_string = self.image_to_base64(resized_image, 'PNG')
                
                prepared_images.append({
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:image/png;base64,{base64_string}",
                        'detail': 'high'
                    }
                })
                
            except Exception as e:
                print(f"Warning: Failed to process image {i+1}: {e}")
                continue
        
        return prepared_images
    
    def filter_relevant_images(self, images: List[Image.Image], max_images: int = None) -> List[Image.Image]:
        """
        Filter and select images for analysis. Now processes all images by default.
        
        Args:
            images (List[Image.Image]): List of extracted images
            max_images (int, optional): Maximum number of images to return (None = all images)
            
        Returns:
            List[Image.Image]: Filtered list of images
        """
        # If no limit specified, return all images
        if max_images is None:
            return images
            
        if len(images) <= max_images:
            return images
        
        # Simple filtering: prefer larger images (likely to contain more content)
        images_with_size = [(img, img.size[0] * img.size[1]) for img in images]
        images_with_size.sort(key=lambda x: x[1], reverse=True)
        
        return [img for img, _ in images_with_size[:max_images]]
