import os
from datetime import datetime
from typing import Dict, Any

class ReportGenerator:
    """Generate structured markdown reports from pitch deck analysis."""
    
    def __init__(self):
        pass
    
    def generate_report(self, analysis_result: Dict[str, Any], pitch_deck_info: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a structured markdown report from the analysis results.
        
        Args:
            analysis_result (Dict[str, Any]): Results from LLM analysis
            pitch_deck_info (Dict[str, Any]): Information about the pitch deck file
            output_path (str, optional): Path to save the report
            
        Returns:
            str: Path to the generated report file
        """
        
        # Extract company name from pitch deck filename or content
        company_name = self._extract_company_name(pitch_deck_info)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create report filename if not provided
        if not output_path:
            safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_company_name = safe_company_name.replace(' ', '_')
            output_path = f"analysis_{safe_company_name}_{timestamp}.md"
        
        # Generate report content
        report_content = self._create_report_content(analysis_result, pitch_deck_info, company_name, timestamp)
        
        # Write report to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to write report to {output_path}: {str(e)}")
    
    def _extract_company_name(self, pitch_deck_info: Dict[str, Any]) -> str:
        """Extract company name from pitch deck information."""
        filename = pitch_deck_info.get('metadata', {}).get('file_name', 'Unknown_Company')
        
        # Remove file extension and clean up filename
        company_name = os.path.splitext(filename)[0]
        company_name = company_name.replace('_', ' ').replace('-', ' ')
        
        return company_name.title()
    
    def _create_report_content(self, analysis_result: Dict[str, Any], pitch_deck_info: Dict[str, Any], company_name: str, timestamp: str) -> str:
        """Create the formatted markdown report content."""
        
        metadata = pitch_deck_info.get('metadata', {})
        
        report_header = f"""# Investment Analysis Report: {company_name}

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}  
**Analyst:** AI-Powered Pitch Deck Analyzer  
**Document Type:** {metadata.get('file_type', 'Unknown')}  
**Source File:** {metadata.get('file_name', 'Unknown')}  

---

## Executive Summary

This report provides a comprehensive investment analysis of {company_name} based on their pitch deck presentation. The analysis covers business model evaluation, market assessment, team analysis, financial projections, and investment recommendations tailored for early-stage startup evaluation.

---

## Document Information

- **File Name:** {metadata.get('file_name', 'N/A')}
- **File Type:** {metadata.get('file_type', 'N/A')}
- **File Size:** {self._format_file_size(metadata.get('file_size', 0))}
- **Pages/Slides:** {metadata.get('num_pages', metadata.get('num_slides', 'N/A'))}
- **Extraction Status:** {'✅ Successful' if pitch_deck_info.get('extraction_success') else '❌ Failed'}

---

"""
        
        # Add analysis content
        if analysis_result.get('success') and analysis_result.get('analysis'):
            report_content = report_header + analysis_result['analysis']
        else:
            error_message = analysis_result.get('error', 'Unknown error occurred during analysis')
            report_content = report_header + f"""
## Analysis Status: ❌ Failed

**Error:** {error_message}

The pitch deck content could not be analyzed due to the error above. Please check your OpenRouter API key and try again.

### Extracted Content Preview

Below is the raw content that was extracted from the pitch deck:

```
{pitch_deck_info.get('full_text', 'No content extracted')[:1000]}...
```
"""
        
        # Add footer
        report_footer = f"""

---

## Report Metadata

- **Analysis Model:** {analysis_result.get('model_used', 'anthropic/claude-3.5-sonnet')}
- **Generation Time:** {timestamp}
- **Report Version:** 1.0
- **Tool:** Pitch Deck Analyzer

---

*This report was generated using AI analysis and should be used as a starting point for investment evaluation. Always conduct additional due diligence and consult with domain experts before making investment decisions.*
"""
        
        return report_content + report_footer
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
