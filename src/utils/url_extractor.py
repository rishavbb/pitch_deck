"""
URL extraction utility for pitch deck analyzer.
Extracts URLs and social media links from text content.
"""

import re
from typing import List, Dict, Set
from urllib.parse import urlparse

class URLExtractor:
    """Extracts and categorizes URLs from text content."""
    
    def __init__(self):
        # Common URL patterns
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Domain patterns for common platforms
        self.domain_patterns = {
            'website': re.compile(r'(?:www\.)?([a-zA-Z0-9-]+\.(?:com|org|net|io|co|ai|tech|app))', re.IGNORECASE),
            'linkedin': re.compile(r'(?:www\.)?linkedin\.com/(?:in/|company/)([a-zA-Z0-9-]+)', re.IGNORECASE),
            'twitter': re.compile(r'(?:www\.)?(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)', re.IGNORECASE),
            'facebook': re.compile(r'(?:www\.)?facebook\.com/([a-zA-Z0-9.]+)', re.IGNORECASE),
            'instagram': re.compile(r'(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)', re.IGNORECASE),
            'github': re.compile(r'(?:www\.)?github\.com/([a-zA-Z0-9-]+)', re.IGNORECASE),
            'youtube': re.compile(r'(?:www\.)?youtube\.com/(?:c/|channel/|user/)?([a-zA-Z0-9_-]+)', re.IGNORECASE),
            'crunchbase': re.compile(r'(?:www\.)?crunchbase\.com/organization/([a-zA-Z0-9-]+)', re.IGNORECASE)
        }
        
        # Email pattern
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    def extract_urls_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extract and categorize URLs from text content.
        
        Args:
            text: Text content to extract URLs from
            
        Returns:
            Dictionary with categorized URLs
        """
        if not text:
            return {}
        
        # Find all URLs
        urls = list(set(self.url_pattern.findall(text)))
        
        # Also look for domain mentions without http/https
        domain_mentions = []
        for platform, pattern in self.domain_patterns.items():
            matches = list(set(pattern.findall(text)))
            for match in matches:
                if platform == 'website':
                    domain_mentions.append(f"https://{match}")
                else:
                    # Reconstruct full URL for social platforms
                    if platform == 'linkedin':
                        domain_mentions.append(f"https://linkedin.com/company/{match}")
                    elif platform == 'twitter':
                        domain_mentions.append(f"https://twitter.com/{match}")
                    elif platform == 'facebook':
                        domain_mentions.append(f"https://facebook.com/{match}")
                    elif platform == 'instagram':
                        domain_mentions.append(f"https://instagram.com/{match}")
                    elif platform == 'github':
                        domain_mentions.append(f"https://github.com/{match}")
                    elif platform == 'youtube':
                        domain_mentions.append(f"https://youtube.com/c/{match}")
                    elif platform == 'crunchbase':
                        domain_mentions.append(f"https://crunchbase.com/organization/{match}")
        
        # Combine and deduplicate
        all_urls = list(set(urls + domain_mentions))
        
        # Categorize URLs
        categorized = {
            'websites': [],
            'social_media': [],
            'professional': [],
            'repositories': [],
            'other': []
        }
        
        for url in all_urls:
            domain = self._get_domain(url)
            category = self._categorize_url(domain)
            categorized[category].append(url)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text."""
        if not text:
            return []
        return list(set(self.email_pattern.findall(text)))
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return url.lower()
    
    def _categorize_url(self, domain: str) -> str:
        """Categorize URL by domain."""
        domain = domain.replace('www.', '')
        
        social_platforms = ['twitter.com', 'x.com', 'facebook.com', 'instagram.com', 'youtube.com', 'tiktok.com']
        professional_platforms = ['linkedin.com', 'crunchbase.com', 'angellist.com', 'pitchbook.com']
        repository_platforms = ['github.com', 'gitlab.com', 'bitbucket.org']
        
        if any(platform in domain for platform in social_platforms):
            return 'social_media'
        elif any(platform in domain for platform in professional_platforms):
            return 'professional'
        elif any(platform in domain for platform in repository_platforms):
            return 'repositories'
        else:
            return 'websites'
    
    def format_urls_for_research(self, categorized_urls: Dict[str, List[str]]) -> str:
        """Format extracted URLs for LLM research prompt."""
        if not categorized_urls:
            return ""
        
        formatted = "\n**URLs and Links Found in Pitch Deck:**\n"
        
        for category, urls in categorized_urls.items():
            if urls:
                category_name = category.replace('_', ' ').title()
                formatted += f"\n{category_name}:\n"
                for url in urls:
                    formatted += f"- {url}\n"
        
        return formatted
