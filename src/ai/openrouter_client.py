import requests
import json
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
from PIL import Image
from ..utils.image_processor import ImageProcessor

load_dotenv()

class OpenRouterClient:
    """Client for interacting with OpenRouter API with multimodal support."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pitch-deck-analyzer",
            "X-Title": "Pitch Deck Analyzer"
        }
        self.image_processor = ImageProcessor()
    
    def analyze_pitch_deck(self, content: str, images: List[bytes] = None, company_name: str = None, urls_info: str = None, scraped_content: str = None) -> Dict[str, Any]:
        """
        Send pitch deck content and images to LLM for comprehensive analysis.
        
        Args:
            content (str): Extracted text content from pitch deck
            images (List[bytes]): List of extracted images from pitch deck
            company_name (str): Name of the company (if known)
            
        Returns:
            Dict[str, Any]: Analysis results from the LLM
        """
        
        # Prepare message content
        message_content = []
        
        # Create comprehensive analysis prompt
        full_prompt = f"""
You are an expert investment analyst specializing in early-stage startup evaluation. Analyze the following pitch deck content and provide a comprehensive investment analysis report.

**PITCH DECK TEXT CONTENT:**
{content}

**VISUAL CONTENT:**
{"I will also analyze the accompanying images/charts/graphs from the pitch deck to provide insights on visual elements like financial projections, market data, product screenshots, team photos, and business model diagrams." if images and len(images) > 0 else "No visual content available for analysis."}

{urls_info if urls_info else ""}

{scraped_content if scraped_content else ""}

**URL EXTRACTION FROM IMAGES:**
{"IMPORTANT: Please carefully examine all images for any URLs, website addresses, social media handles, email addresses, or company links that appear in the visual content. Extract all visible URLs and links from the images and include them in your analysis." if images and len(images) > 0 else ""}

**ONLINE RESEARCH INSTRUCTIONS:**
{'''Based on the URLs found and the detailed web scraping results provided above, please analyze this information and provide comprehensive insights about:
- Company background and recent developments
- Market position and competitive landscape
- Financial performance (if publicly available)
- Leadership team and key personnel
- Recent news, partnerships, or funding rounds
- Social media presence and customer engagement
- Product offerings and business model details
- Any other relevant information that would be valuable for investment analysis

Please include this research in a separate section titled "Information Available Online from the Links in the Document" at the end of your analysis. Use both the scraped content and your knowledge base to provide the most comprehensive analysis possible.''' if scraped_content or urls_info else ""}

**ANALYSIS REQUIREMENTS:**
Please provide a detailed analysis covering the following areas:

1. **COMPANY OVERVIEW**
   - Company name, mission, and vision
   - Industry and market sector
   - Stage of development (pre-seed, seed, Series A, etc.)
   - Geographic location and target markets

2. **BUSINESS MODEL ANALYSIS**
   - Revenue model and monetization strategy
   - Unit economics and pricing strategy
   - Customer acquisition strategy
   - Scalability potential

3. **MARKET ANALYSIS**
   - Total Addressable Market (TAM), Serviceable Addressable Market (SAM), Serviceable Obtainable Market (SOM)
   - Market trends and growth potential
   - Competitive landscape
   - Market timing and opportunity

4. **FINANCIAL ANALYSIS**
   - Current financial status
   - Revenue projections and growth trajectory
   - Funding requirements and use of funds
   - Key financial metrics and assumptions


5. **INFORMATION AVAILABLE ONLINE FROM THE LINKS IN THE DOCUMENT**
    - Detailed analysis of scraped web content
    - Company background from official websites
    - Social media presence and engagement
    - Product/service offerings and business model validation
    - Market positioning and competitive analysis
    - Contact information and professional networks

**OUTPUT FORMAT:**
Please structure your response as a well-formatted markdown document suitable for an investment manager. Use clear headings, bullet points, and professional language. Be specific and actionable in your recommendations.
Also, make sure INFORMATION AVAILABLE ONLINE FROM THE LINKS IN THE DOCUMENT is included in the analysis. I want to have a very detailed opinion on this.
"""
        
        # Add text content to message
        message_content.append({
            "type": "text",
            "text": full_prompt
        })
        
        # Add images if available
        if images and len(images) > 0:
            # Filter and prepare images
            filtered_images = self.image_processor.filter_relevant_images(images)
            prepared_images = self.image_processor.prepare_images_for_llm(filtered_images)
            
            # Add each image to message content
            for img_data in prepared_images:
                message_content.append(img_data)
            
            print(f"📸 Added {len(prepared_images)} images for analysis")
        
        # Choose model based on whether we have images
        model = "anthropic/claude-3.5-sonnet" if not images or len(images) == 0 else "anthropic/claude-3.5-sonnet"
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "user",
                            "content": message_content
                        }
                    ],
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'success': True,
                'analysis': result['choices'][0]['message']['content'],
                'model_used': result.get('model', model),
                'usage': result.get('usage', {}),
                'images_analyzed': len(images) if images else 0
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"API request failed: {str(e)}",
                'analysis': None
            }
        except KeyError as e:
            return {
                'success': False,
                'error': f"Unexpected API response format: {str(e)}",
                'analysis': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}",
                'analysis': None
            }
