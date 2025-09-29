"""
Image URL extraction utility that uses LLM to extract URLs from images.
"""

import requests
import json
from typing import List, Dict, Optional
import os
import time
from dotenv import load_dotenv
from ..utils.image_processor import ImageProcessor

load_dotenv()

class ImageURLExtractor:
    """Extracts URLs from images using LLM vision capabilities."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required.")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pitch-deck-analyzer",
            "X-Title": "Pitch Deck Analyzer"
        }
        self.image_processor = ImageProcessor()
    
    def extract_urls_from_images(self, images: List[bytes]) -> List[str]:
        """
        Extract URLs from images using LLM vision.
        
        Args:
            images: List of image bytes
            
        Returns:
            List of extracted URLs
        """
        if not images:
            return []
        
        # Prepare images for LLM
        filtered_images = self.image_processor.filter_relevant_images(images, max_images=8)
        prepared_images = self.image_processor.prepare_images_for_llm(filtered_images)
        
        # Create message content
        message_content = []
        
        # Add instruction text
        instruction = """Please carefully examine all the images and extract any URLs, website addresses, social media handles, email addresses, or company links that you can see in the visual content.

Return ONLY a JSON list of URLs in this exact format:
["url1", "url2", "url3"]

Include:
- Complete website URLs (http/https)
- Social media profiles (LinkedIn, Twitter, Facebook, Instagram, etc.)
- Company websites
- Email addresses
- Any other web links visible in the images

If no URLs are found, return an empty list: []"""
        
        message_content.append({
            "type": "text",
            "text": instruction
        })
        
        # Add images
        for img_data in prepared_images:
            message_content.append(img_data)
        
        # Retry logic for API calls
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Create a new session for each attempt
                session = requests.Session()
                session.headers.update(self.headers)
                
                response = session.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [
                            {
                                "role": "user",
                                "content": message_content
                            }
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.1
                    },
                    timeout=30
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract and parse the response
                content = result['choices'][0]['message']['content'].strip()
                
                # Try to parse JSON response
                try:
                    # Clean the response - remove any markdown formatting
                    if content.startswith('```json'):
                        content = content.replace('```json', '').replace('```', '').strip()
                    elif content.startswith('```'):
                        content = content.replace('```', '').strip()
                    
                    urls = json.loads(content)
                    if isinstance(urls, list):
                        return [url for url in urls if isinstance(url, str) and url.strip()]
                    else:
                        return []
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract URLs using regex
                    import re
                    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                    urls = re.findall(url_pattern, content)
                    return urls
                    
            except requests.exceptions.SSLError as e:
                print(f"SSL error on attempt {attempt + 1}/{max_retries}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    print("Failed to extract URLs from images due to SSL issues. Skipping URL extraction.")
                    return []
            except Exception as e:
                print(f"Error extracting URLs from images (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return []
        
        return []
