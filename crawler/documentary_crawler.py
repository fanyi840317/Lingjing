# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse

from .crawler import Crawler
from rag import Document, MysteryEvent
from config.mystery_config import MysteryEventType, DataSourceType

logger = logging.getLogger(__name__)


class DocumentaryCrawler(Crawler):
    """Specialized crawler for documentary and video content about mysterious events."""
    
    def __init__(self):
        super().__init__()
        self.documentary_patterns = {
            "title": [
                r'<h1[^>]*>([^<]+)</h1>',
                r'<title>([^<]+)</title>',
                r'"title"\s*:\s*"([^"]+)"',
                r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"',
            ],
            "description": [
                r'<meta[^>]*name="description"[^>]*content="([^"]+)"',
                r'<meta[^>]*property="og:description"[^>]*content="([^"]+)"',
                r'"description"\s*:\s*"([^"]+)"',
                r'<p[^>]*class="[^"]*description[^"]*"[^>]*>([^<]+)</p>',
            ],
            "duration": [
                r'"duration"\s*:\s*"([^"]+)"',
                r'Duration:\s*([\d:]+)',
                r'<span[^>]*class="[^"]*duration[^"]*"[^>]*>([^<]+)</span>',
            ],
            "release_date": [
                r'"datePublished"\s*:\s*"([^"]+)"',
                r'Released:\s*([\d\-/]+)',
                r'<time[^>]*datetime="([^"]+)"',
            ],
            "producer": [
                r'"director"\s*:\s*"([^"]+)"',
                r'"producer"\s*:\s*"([^"]+)"',
                r'Produced by:\s*([^\n<]+)',
                r'Director:\s*([^\n<]+)',
            ],
            "genre": [
                r'"genre"\s*:\s*"([^"]+)"',
                r'Genre:\s*([^\n<]+)',
                r'<span[^>]*class="[^"]*genre[^"]*"[^>]*>([^<]+)</span>',
            ],
            "transcript": [
                r'<div[^>]*class="[^"]*transcript[^"]*"[^>]*>([^<]+)</div>',
                r'"transcript"\s*:\s*"([^"]+)"',
            ],
        }
        
        self.mystery_keywords = {
            MysteryEventType.UFO: ["ufo", "alien", "extraterrestrial", "flying saucer", "abduction"],
            MysteryEventType.CRYPTID: ["bigfoot", "sasquatch", "yeti", "loch ness", "chupacabra"],
            MysteryEventType.PARANORMAL: ["ghost", "haunted", "paranormal", "supernatural", "poltergeist"],
            MysteryEventType.ANCIENT_MYSTERY: ["ancient", "pyramid", "stonehenge", "atlantis", "civilization"],
            MysteryEventType.DISAPPEARANCE: ["missing", "disappeared", "vanished", "bermuda triangle"],
            MysteryEventType.NATURAL_ANOMALY: ["anomaly", "phenomenon", "unexplained", "strange weather"]
        }
    
    async def parse_documentary_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse documentary-specific content from HTML."""
        parsed_data = {
            "title": "",
            "description": "",
            "duration": "",
            "release_date": "",
            "producer": "",
            "genre": "",
            "transcript": "",
            "mystery_type": MysteryEventType.UNKNOWN,
            "credibility_score": 0.0,
        }
        
        # Extract basic documentary information
        for field, patterns in self.documentary_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    parsed_data[field] = match.group(1).strip()
                    break
        
        # Determine mystery event type
        content_text = (parsed_data["title"] + " " + parsed_data["description"]).lower()
        for event_type, keywords in self.mystery_keywords.items():
            if any(keyword in content_text for keyword in keywords):
                parsed_data["mystery_type"] = event_type
                break
        
        # Calculate credibility score for documentary content
        parsed_data["credibility_score"] = self._calculate_documentary_credibility(
            parsed_data, url
        )
        
        return parsed_data
    
    def _calculate_documentary_credibility(self, data: Dict[str, Any], url: str) -> float:
        """Calculate credibility score for documentary content."""
        score = 0.6  # Base score for documentary content
        
        # Producer/Director credibility
        if data.get("producer"):
            reputable_producers = [
                "national geographic", "discovery", "history channel", "bbc", "pbs",
                "nova", "smithsonian", "netflix", "amazon prime"
            ]
            producer_lower = data["producer"].lower()
            if any(prod in producer_lower for prod in reputable_producers):
                score += 0.3
        
        # URL domain credibility
        domain = urlparse(url).netloc.lower()
        reputable_domains = [
            "nationalgeographic.com", "discovery.com", "history.com", "bbc.com",
            "pbs.org", "smithsonianmag.com", "netflix.com", "amazon.com"
        ]
        if any(domain.endswith(d) for d in reputable_domains):
            score += 0.2
        
        # Content quality indicators
        if data.get("duration") and ":" in data["duration"]:
            # Longer documentaries tend to be more thorough
            try:
                parts = data["duration"].split(":")
                minutes = int(parts[0]) * 60 + int(parts[1]) if len(parts) >= 2 else int(parts[0])
                if minutes > 30:  # More than 30 minutes
                    score += 0.1
            except ValueError:
                pass
        
        # Release date (more recent might be more credible)
        if data.get("release_date"):
            try:
                # Simple year extraction
                year_match = re.search(r'(\d{4})', data["release_date"])
                if year_match:
                    year = int(year_match.group(1))
                    current_year = datetime.now().year
                    if current_year - year < 5:  # Within last 5 years
                        score += 0.1
            except ValueError:
                pass
        
        return min(1.0, score)  # Cap at 1.0
    
    async def crawl_url(self, url: str) -> Optional[Document]:
        """Crawl a single documentary URL and return a Document."""
        try:
            html = await self.fetch_html(url)
            if not html:
                return None
            
            parsed_data = await self.parse_documentary_html(html, url)
            
            # Create MysteryEvent if applicable
            mystery_event = None
            if parsed_data["mystery_type"] != MysteryEventType.UNKNOWN:
                mystery_event = MysteryEvent(
                    title=parsed_data["title"],
                    description=parsed_data["description"],
                    event_type=parsed_data["mystery_type"].value,
                    location="unknown",  # Documentaries may not specify location
                    date=parsed_data.get("release_date", "unknown"),
                    source_url=url,
                    source_type=DataSourceType.DOCUMENTARY.value,
                    credibility_score=parsed_data["credibility_score"],
                    witnesses=[],
                    evidence=[parsed_data.get("transcript", "")],
                    metadata={
                        "duration": parsed_data.get("duration", ""),
                        "producer": parsed_data.get("producer", ""),
                        "genre": parsed_data.get("genre", ""),
                        "release_date": parsed_data.get("release_date", ""),
                    }
                )
            
            # Create Document
            document = Document(
                url=url,
                title=parsed_data["title"],
                chunks=[],  # Will be populated by content processing
                mystery_event=mystery_event,
                credibility_score=parsed_data["credibility_score"],
                source_type=DataSourceType.DOCUMENTARY.value,
                publication_date=parsed_data.get("release_date", ""),
                author=parsed_data.get("producer", ""),
                metadata={
                    "duration": parsed_data.get("duration", ""),
                    "genre": parsed_data.get("genre", ""),
                    "transcript": parsed_data.get("transcript", ""),
                    "mystery_type": parsed_data["mystery_type"].value,
                }
            )
            
            return document
            
        except Exception as e:
            logger.error(f"Error crawling documentary URL {url}: {e}")
            return None
    
    async def search(self, query: str, max_results: int = 10) -> List[str]:
        """Search for documentary URLs related to the query."""
        # Build documentary-specific search query
        documentary_query = self._build_documentary_search_query(query)
        
        # Mock search results - in real implementation, this would query
        # documentary databases, streaming platforms, etc.
        mock_urls = [
            f"https://www.nationalgeographic.com/documentary/{query.replace(' ', '-')}-{i}"
            for i in range(min(max_results, 5))
        ] + [
            f"https://www.discovery.com/shows/{query.replace(' ', '-')}-documentary-{i}"
            for i in range(min(max_results - 5, 5))
        ]
        
        return mock_urls[:max_results]
    
    def _build_documentary_search_query(self, query: str) -> str:
        """Build a documentary-specific search query."""
        # Add documentary-specific terms
        documentary_terms = ["documentary", "film", "investigation", "evidence"]
        
        # Identify mystery type from query
        query_lower = query.lower()
        mystery_terms = []
        
        for event_type, keywords in self.mystery_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                mystery_terms.extend(keywords[:2])  # Add top 2 keywords
                break
        
        # Combine terms
        all_terms = [query] + documentary_terms + mystery_terms
        return " ".join(all_terms)
    
    def get_supported_domains(self) -> List[str]:
        """Get list of supported documentary domains."""
        return [
            "nationalgeographic.com",
            "discovery.com",
            "history.com",
            "bbc.com",
            "pbs.org",
            "smithsonianmag.com",
            "netflix.com",
            "amazon.com",
            "youtube.com",
            "vimeo.com",
        ]