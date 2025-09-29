import os
from typing import Dict, Any, Optional
from .extractors import PDFExtractor, PPTExtractor
from .ai import OpenRouterClient
from .report_generator import ReportGenerator

class PitchDeckAnalyzer:
    """Main orchestrator for pitch deck analysis."""
    
    def __init__(self, openrouter_api_key: Optional[str] = None):
        self.pdf_extractor = PDFExtractor()
        self.ppt_extractor = PPTExtractor()
        self.ai_client = OpenRouterClient(openrouter_api_key)
        self.report_generator = ReportGenerator()
    
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
            if not full_text:
                return {
                    'success': False,
                    'error': "No text content found in the pitch deck. This PDF appears to contain only images/scanned content. Please try:\n" +
                            "   • A PDF with selectable text content\n" +
                            "   • Converting the PDF to text using OCR tools\n" +
                            "   • Using the original PowerPoint file instead",
                    'report_path': None
                }
            
            print(f"✅ Successfully extracted {len(full_text)} characters of content")
            
            # Send content to LLM for analysis
            print("🤖 Sending content to AI for analysis...")
            company_name = self._extract_company_name_from_content(full_text, extraction_result)
            analysis_result = self.ai_client.analyze_pitch_deck(full_text, company_name)
            
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
