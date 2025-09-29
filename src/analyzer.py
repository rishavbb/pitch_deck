import os
from typing import Dict, Any, Optional
from .extractors.pdf_extractor import PDFExtractor
from .extractors.ppt_extractor import PPTExtractor
from .ai.openrouter_client import OpenRouterClient
from .report_generator import ReportGenerator
from .utils.url_extractor import URLExtractor
from .utils.web_scraper import WebScraper
from .utils.image_url_extractor import ImageURLExtractor
import os
from pathlib import Path

class PitchDeckAnalyzer:
    """Main orchestrator for pitch deck analysis."""
    
    def __init__(self, openrouter_api_key: Optional[str] = None):
        self.pdf_extractor = PDFExtractor()
        self.ppt_extractor = PPTExtractor()
        self.ai_client = OpenRouterClient(openrouter_api_key)
        self.report_generator = ReportGenerator()
        self.url_extractor = URLExtractor()
        self.web_scraper = WebScraper()
        self.image_url_extractor = ImageURLExtractor(openrouter_api_key)
    
    def analyze_pitch_deck(self, file_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a pitch deck file and generate a comprehensive report.
        
        Args:
            file_path (str): Path to the pitch deck file (PDF or PPT/PPTX)
            output_path (str, optional): Path for the output report
            
        Returns:
            Dict[str, Any]: Analysis results and report information
        """
        
        # Validate file exists
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f"File not found: {file_path}",
                'report_path': None
            }
        
        # Determine file type and extract content
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                print("📄 Extracting content from PDF...")
                extraction_result = self.pdf_extractor.extract_content(file_path)
            elif file_extension in ['.ppt', '.pptx']:
                print("📊 Extracting content from PowerPoint...")
                extraction_result = self.ppt_extractor.extract_content(file_path)
            else:
                return {
                    'success': False,
                    'error': f"Unsupported file type: {file_extension}. Supported formats: PDF, PPT, PPTX",
                    'report_path': None
                }
            
            # Check if extraction was successful
            if not extraction_result.get('extraction_success'):
                return {
                    'success': False,
                    'error': f"Content extraction failed: {extraction_result.get('error', 'Unknown error')}",
                    'report_path': None
                }
            
            # Check if we have content to analyze
            full_text = extraction_result.get('full_text', '').strip()
            images = extraction_result.get('images', [])
            
            if not full_text and not images:
                return {
                    'success': False,
                    'error': "No text or image content found in the pitch deck. The file may be corrupted or empty.",
                    'report_path': None
                }
            
            # Handle image-only PDFs
            if not full_text and images:
                print(f"📄 No text content found, but found {len(images)} images")
                print("🖼️ Proceeding with image-only analysis...")
                full_text = "This pitch deck contains only visual content (images/charts/diagrams). Please analyze the visual elements to extract all relevant information about the company, business model, market opportunity, team, financials, and investment potential."
            
            print(f"✅ Successfully extracted {len(full_text)} characters of content")
            
            # Extract URLs from content for LLM research
            print("🔍 Extracting URLs and links...")
            categorized_urls = self.url_extractor.extract_urls_from_text(full_text)
            all_urls = []
            
            # For text-based URLs
            if categorized_urls:
                for url_list in categorized_urls.values():
                    all_urls.extend(url_list)
                print(f"🌐 Found {len(all_urls)} URLs from text content")
            
            # For image-only PDFs, extract URLs from images
            if images and len(images) > 0 and not categorized_urls:
                print("🖼️ Extracting URLs from images...")
                image_urls = self.image_url_extractor.extract_urls_from_images(images)
                all_urls.extend(image_urls)
                print(f"🌐 Found {len(image_urls)} URLs from images")
            
            urls_info = None
            scraped_content = None
            
            if all_urls:
                # Format URLs for research
                if categorized_urls:
                    urls_info = self.url_extractor.format_urls_for_research(categorized_urls)
                else:
                    # Create simple format for image-extracted URLs
                    urls_info = "\n**URLs Found in Images:**\n" + "\n".join([f"- {url}" for url in all_urls]) + "\n"
                
                # Perform web scraping on found URLs
                print("🕷️ Scraping URLs for detailed content...")
                scraped_data = self.web_scraper.scrape_multiple_urls(all_urls)
                scraped_content = self.web_scraper.format_scraped_content_for_llm(scraped_data)
                print(f"✅ Scraped {len([d for d in scraped_data.values() if d.get('status') == 'success'])} URLs successfully")
            
            # Send content to LLM for analysis
            print("🤖 Sending content to AI for analysis...")
            company_name = self._extract_company_name_from_content(full_text, extraction_result)
            
            if images:
                print(f"🖼️ Found {len(images)} images in pitch deck")
            
            analysis_result = self.ai_client.analyze_pitch_deck(full_text, images, company_name, urls_info, scraped_content)
            
            # Generate report
            print("📝 Generating analysis report...")
            try:
                report_path = self.report_generator.generate_report(
                    analysis_result, 
                    extraction_result, 
                    output_path
                )
                
                return {
                    'success': True,
                    'report_path': report_path,
                    'extraction_info': {
                        'file_type': extraction_result['metadata']['file_type'],
                        'content_length': len(full_text),
                        'pages_slides': extraction_result['metadata'].get('num_pages', extraction_result['metadata'].get('num_slides'))
                    },
                    'analysis_info': {
                        'model_used': analysis_result.get('model_used'),
                        'analysis_success': analysis_result.get('success', False)
                    }
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Report generation failed: {str(e)}",
                    'report_path': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}",
                'report_path': None
            }
    
    def _extract_company_name_from_content(self, content: str, extraction_result: Dict[str, Any]) -> str:
        """Extract company name from content or filename."""
        
        # Try to find company name in the first few lines of content
        lines = content.split('\n')[:10]
        for line in lines:
            line = line.strip()
            if line and len(line) < 50 and not line.lower().startswith(('pitch', 'deck', 'presentation')):
                # This might be a company name
                return line
        
        # Fallback to filename
        filename = extraction_result.get('metadata', {}).get('file_name', 'Unknown Company')
        return os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
