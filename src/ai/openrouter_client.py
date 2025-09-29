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
    
    def analyze_pitch_deck(self, content: str, images: List[Image.Image] = None, company_name: str = "Unknown Company") -> Dict[str, Any]:
        """
        Send pitch deck content and images to LLM for comprehensive analysis.
        
        Args:
            content (str): Extracted text content from pitch deck
            images (List[Image.Image]): List of extracted images from pitch deck
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

4. **PRODUCT/SERVICE EVALUATION**
   - Product description and unique value proposition
   - Technology stack and innovation level
   - Product-market fit evidence
   - Competitive advantages and moats

5. **TEAM ASSESSMENT**
   - Founder backgrounds and expertise
   - Team composition and key personnel
   - Advisory board and investors
   - Execution capability assessment

6. **FINANCIAL ANALYSIS**
   - Current financial status
   - Revenue projections and growth trajectory
   - Funding requirements and use of funds
   - Key financial metrics and assumptions

7. **TRACTION AND MILESTONES**
   - Customer traction and user metrics
   - Revenue growth and key achievements
   - Partnerships and strategic relationships
   - Product development milestones

8. **RISK ASSESSMENT**
   - Market risks and competitive threats
   - Execution risks and operational challenges
   - Financial risks and funding concerns
   - Regulatory and compliance risks

9. **INVESTMENT RECOMMENDATION**
   - Overall investment attractiveness (1-10 scale)
   - Key strengths and opportunities
   - Major concerns and red flags
   - Recommended due diligence areas

10. **ADDITIONAL RESEARCH SUGGESTIONS**
    - Key questions for management team
    - Areas requiring deeper investigation
    - Comparable companies for benchmarking
    - Industry experts to consult

**OUTPUT FORMAT:**
Please structure your response as a well-formatted markdown document suitable for an investment manager. Use clear headings, bullet points, and professional language. Be specific and actionable in your recommendations.

If any information is missing from the pitch deck, clearly indicate what additional information would be valuable for a complete assessment.
"""
        
        # Add text content to message
        message_content.append({
            "type": "text",
            "text": full_prompt
        })
        
        # Add images if available
        if images and len(images) > 0:
            # Filter and prepare images
            filtered_images = self.image_processor.filter_relevant_images(images, max_images=8)
            prepared_images = self.image_processor.prepare_images_for_llm(filtered_images)
            
            # Add each image to message content
            for img_data in prepared_images:
                message_content.append(img_data)
            
            print(f"📸 Added {len(prepared_images)} images for analysis")
        
        # Choose model based on whether we have images
        model = "anthropic/claude-3.5-sonnet" if not images or len(images) == 0 else "anthropic/claude-3-5-sonnet-20241022"
        
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
