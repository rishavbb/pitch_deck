"""
Web scraping utility for extracting content from URLs found in pitch decks.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time
import re
from urllib.parse import urljoin, urlparse
import logging

class WebScraper:
    """Web scraper for extracting content from URLs."""
    
    def __init__(self, timeout: int = 10, delay: float = 1.0):
        self.timeout = timeout
        self.delay = delay  # Delay between requests to be respectful
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def scrape_url(self, url: str) -> Dict[str, str]:
        """
        Scrape content from a single URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with scraped content
        """
        try:
            # Clean and validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            self.logger.info(f"Scraping URL: {url}")
            
            # Make request
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract various content types
            content = {
                'url': url,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'main_content': self._extract_main_content(soup),
                'company_info': self._extract_company_info(soup),
                'contact_info': self._extract_contact_info(soup),
                'social_links': self._extract_social_links(soup, url),
                'status': 'success'
            }
            
            # Add delay to be respectful
            time.sleep(self.delay)
            
            return content
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            return {
                'url': url,
                'status': 'error',
                'error': f"Request failed: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Scraping failed for {url}: {str(e)}")
            return {
                'url': url,
                'status': 'error',
                'error': f"Scraping failed: {str(e)}"
            }
    
    def scrape_multiple_urls(self, urls: List[str]) -> Dict[str, Dict]:
        """
        Scrape content from multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            Dictionary mapping URLs to their scraped content
        """
        results = {}
        
        for url in urls:
            try:
                results[url] = self.scrape_url(url)
            except Exception as e:
                self.logger.error(f"Failed to scrape {url}: {str(e)}")
                results[url] = {
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try h1 as fallback
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "No title found"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description from meta tags."""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p:
            text = first_p.get_text().strip()
            return text[:200] + "..." if len(text) > 200 else text
        
        return "No description found"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content areas
        main_selectors = [
            'main', 'article', '.content', '#content', 
            '.main-content', '.post-content', '.entry-content'
        ]
        
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                text = main_content.get_text()
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                return text[:1000] + "..." if len(text) > 1000 else text
        
        # Fallback: get all paragraph text
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = ' '.join([p.get_text().strip() for p in paragraphs[:5]])
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:1000] + "..." if len(text) > 1000 else text
        
        return "No main content found"
    
    def _extract_company_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract company-specific information."""
        info = {}
        
        # Try to find company name
        company_selectors = [
            '.company-name', '.brand-name', '.logo-text',
            'h1', '.site-title', '.navbar-brand'
        ]
        
        for selector in company_selectors:
            element = soup.select_one(selector)
            if element:
                info['company_name'] = element.get_text().strip()
                break
        
        # Try to find about section
        about_selectors = [
            '.about', '#about', '.company-info', '.about-us'
        ]
        
        for selector in about_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                info['about'] = text[:500] + "..." if len(text) > 500 else text
                break
        
        return info
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information."""
        contact = {}
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        page_text = soup.get_text()
        emails = re.findall(email_pattern, page_text)
        if emails:
            contact['emails'] = list(set(emails))
        
        # Extract phone numbers (basic pattern)
        phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
        phones = re.findall(phone_pattern, page_text)
        if phones:
            contact['phones'] = list(set(phones))
        
        return contact
    
    def _extract_social_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract social media links."""
        social_domains = [
            'facebook.com', 'twitter.com', 'x.com', 'linkedin.com',
            'instagram.com', 'youtube.com', 'github.com', 'tiktok.com'
        ]
        
        social_links = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = urljoin(base_url, href)
            
            # Check if it's a social media link
            for domain in social_domains:
                if domain in href.lower():
                    social_links.append(href)
                    break
        
        return list(set(social_links))
    
    def format_scraped_content_for_llm(self, scraped_data: Dict[str, Dict]) -> str:
        """Format scraped content for LLM analysis."""
        if not scraped_data:
            return ""
        
        formatted = "\n**Detailed Information Extracted from Web Scraping:**\n\n"
        
        for url, data in scraped_data.items():
            if data.get('status') == 'error':
                formatted += f"**URL: {url}**\n"
                formatted += f"❌ **Scraping Status**: Failed\n"
                formatted += f"🚫 **Error Details**: {data.get('error', 'Unknown error')}\n"
                formatted += f"📝 **Impact**: Unable to gather additional information from this source\n\n"
                formatted += "---\n\n"
                continue
            
            formatted += f"**URL: {url}**\n"
            formatted += f"✅ **Scraping Status**: Successfully scraped\n\n"
            
            # Page Information
            formatted += f"📄 **Page Title**: {data.get('title', 'Not found')}\n"
            formatted += f"📝 **Meta Description**: {data.get('description', 'Not found')}\n\n"
            
            # Company Information
            if data.get('company_info'):
                company_info = data['company_info']
                formatted += f"**🏢 Company Information:**\n"
                if company_info.get('company_name'):
                    formatted += f"- **Company Name**: {company_info['company_name']}\n"
                if company_info.get('about'):
                    formatted += f"- **About Company**: {company_info['about']}\n"
                formatted += "\n"
            
            # Main Content
            if data.get('main_content'):
                formatted += f"**📖 Main Content Extracted:**\n"
                formatted += f"{data['main_content']}\n\n"
            
            # Contact Information
            if data.get('contact_info'):
                contact = data['contact_info']
                formatted += f"**📞 Contact Information:**\n"
                if contact.get('emails'):
                    formatted += f"- **Email Addresses**: {', '.join(contact['emails'])}\n"
                if contact.get('phones'):
                    formatted += f"- **Phone Numbers**: {', '.join(contact['phones'])}\n"
                formatted += "\n"
            
            # Social Media Links
            if data.get('social_links'):
                formatted += f"**🔗 Social Media & External Links:**\n"
                for link in data['social_links']:
                    formatted += f"- {link}\n"
                formatted += "\n"
            
            # Business Intelligence
            formatted += f"**🧠 Key Business Insights from {url}:**\n"
            formatted += f"- **Website Type**: {'Corporate/Business' if any(keyword in data.get('main_content', '').lower() for keyword in ['business', 'company', 'services', 'products']) else 'Information/Resource'}\n"
            formatted += f"- **Content Focus**: {'Educational/Resource' if any(keyword in data.get('main_content', '').lower() for keyword in ['guide', 'tutorial', 'example', 'template']) else 'Commercial/Business'}\n"
            formatted += f"- **Professional Level**: {'High' if data.get('social_links') or data.get('contact_info', {}).get('emails') else 'Medium'}\n"
            
            formatted += "\n---\n\n"
        
        return formatted
