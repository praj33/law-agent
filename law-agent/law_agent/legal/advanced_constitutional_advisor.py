"""
Constitutional Articles Integration Module
=========================================

This module integrates Indian Constitutional articles with the Legal Agent system
to provide constitutional backing for legal advice and enhance system credibility.

Features:
- Constitutional article search and retrieval
- Domain-specific constitutional references
- Article-based legal precedent support
- Enhanced legal advice with constitutional backing

Author: Legal Agent Team
Version: 4.0.0 - Constitutional Integration
Date: 2025-07-22
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalArticle:
    """Data structure for constitutional articles"""
    article_number: str
    title: str
    content: str
    keywords: List[str] = None
    legal_domains: List[str] = None
    
    @property
    def clean_title(self) -> str:
        """Get cleaned title without quotes and extra formatting"""
        return self.title.strip('"').strip()
    
    @property
    def has_content(self) -> bool:
        """Check if article has substantial content"""
        return bool(self.content and self.content.strip())
    
    @property
    def summary(self) -> str:
        """Get a brief summary of the article"""
        if not self.has_content:
            return self.clean_title
        
        # Extract first sentence or first 100 characters
        content = self.content.strip()
        first_sentence = content.split('.')[0] if '.' in content else content
        
        if len(first_sentence) > 100:
            return first_sentence[:100] + "..."
        return first_sentence


class ConstitutionalDatabase:
    """Database of constitutional articles with search capabilities"""
    
    def __init__(self, articles_file: str = "article.json"):
        """Initialize with constitutional articles"""
        self.articles_file = articles_file
        self.articles: Dict[str, ConstitutionalArticle] = {}
        self.domain_mappings: Dict[str, List[str]] = {}
        self.load_articles()
        self.create_domain_mappings()
    
    def load_articles(self):
        """Load constitutional articles from JSON file"""
        try:
            with open(self.articles_file, 'r', encoding='utf-8') as f:
                articles_data = json.load(f)
            
            for article_data in articles_data:
                article = ConstitutionalArticle(
                    article_number=article_data['article_number'],
                    title=article_data['title'],
                    content=article_data.get('content', ''),
                    keywords=article_data.get('keywords', []),
                    legal_domains=article_data.get('legal_domains', [])
                )
                self.articles[article.article_number] = article
            
            logger.info(f"Loaded {len(self.articles)} constitutional articles")
            
        except FileNotFoundError:
            logger.warning(f"Constitutional articles file {self.articles_file} not found")
            self.articles = {}
        except Exception as e:
            logger.error(f"Error loading constitutional articles: {e}")
            self.articles = {}
    
    def create_domain_mappings(self):
        """Create mappings between legal domains and relevant constitutional articles"""
        
        # Define domain-specific constitutional mappings
        self.domain_mappings = {
            'tenant rights': ['19', '21', '300'],  # Property rights, life & liberty
            'consumer complaint': ['19', '21'],     # Trade & commerce, consumer protection
            'family law': ['15', '16', '21', '25'], # Equality, marriage, personal liberty, religion
            'employment law': ['14', '15', '16', '19', '21', '23', '24'], # Equality, non-discrimination, work
            'contract dispute': ['19', '21', '300'], # Freedom of trade, liberty, property
            'personal injury': ['21'],              # Right to life and personal liberty
            'criminal law': ['14', '20', '21', '22'], # Equality, protection from crimes, liberty, arrest
            'immigration law': ['5', '6', '7', '8', '9', '10'], # Citizenship articles
            'elder abuse': ['21', '41'],            # Right to life, elderly care
            'cyber crime': ['19', '21'],            # Freedom of expression, privacy
            
            # Additional mappings for comprehensive coverage
            'fundamental_rights': ['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '35'],
            'citizenship': ['5', '6', '7', '8', '9', '10', '11'],
            'union_territory': ['1', '2', '3', '4'],
            'constitutional_structure': ['1', '2', '3', '4']
        }
    
    def search_articles(self, query: str, limit: int = 5) -> List[ConstitutionalArticle]:
        """Search articles by content and title"""
        query_lower = query.lower()
        matches = []
        
        for article in self.articles.values():
            score = 0

            # Check keyword matches (highest priority for new comprehensive articles)
            if hasattr(article, 'keywords') and article.keywords:
                for keyword in article.keywords:
                    if keyword.lower() in query_lower:
                        score += 5  # High weight for keyword matches

            # Check legal domain matches
            if hasattr(article, 'legal_domains') and article.legal_domains:
                query_domain = self._infer_domain_from_query(query_lower)
                if query_domain in article.legal_domains:
                    score += 4  # High weight for domain matches

            # Check title match
            if query_lower in article.clean_title.lower():
                score += 3

            # Check content match
            if article.has_content and query_lower in article.content.lower():
                score += 2

            # Check for keyword matches in title/content
            keywords = query_lower.split()
            for keyword in keywords:
                if keyword in article.clean_title.lower():
                    score += 1
                if article.has_content and keyword in article.content.lower():
                    score += 1

            if score > 0:
                matches.append((score, article))
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x[0], reverse=True)
        return [article for score, article in matches[:limit]]

    def _infer_domain_from_query(self, query_lower: str) -> str:
        """Infer legal domain from query text"""
        domain_keywords = {
            "criminal_law": ["arrest", "police", "theft", "crime", "criminal", "custody", "warrant", "detention"],
            "family_law": ["divorce", "marriage", "family", "spouse", "husband", "wife", "child", "custody", "abuse"],
            "employment_law": ["job", "work", "employment", "fired", "termination", "salary", "workplace", "boss", "company", "pregnant", "pregnancy"],
            "property_law": ["property", "landlord", "tenant", "eviction", "rent", "house", "land", "real estate"],
            "constitutional_law": ["rights", "freedom", "constitution", "fundamental", "liberty", "equality"],
            "civil_rights": ["discrimination", "equality", "rights", "freedom", "liberty", "justice"]
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain

        return "constitutional_law"  # Default domain
    
    def get_articles_for_domain(self, domain: str) -> List[ConstitutionalArticle]:
        """Get relevant constitutional articles for a legal domain"""
        article_numbers = self.domain_mappings.get(domain, [])
        
        relevant_articles = []
        for article_num in article_numbers:
            if article_num in self.articles:
                relevant_articles.append(self.articles[article_num])
        
        return relevant_articles
    
    def get_article(self, article_number: str) -> Optional[ConstitutionalArticle]:
        """Get specific article by number"""
        return self.articles.get(article_number)
    
    def get_citizenship_articles(self) -> List[ConstitutionalArticle]:
        """Get all citizenship-related articles"""
        return self.get_articles_for_domain('citizenship')
    
    def get_fundamental_rights_articles(self) -> List[ConstitutionalArticle]:
        """Get fundamental rights articles"""
        return self.get_articles_for_domain('fundamental_rights')


class ConstitutionalAdvisor:
    """Provides constitutional backing for legal advice"""
    
    def __init__(self, articles_file: str = "comprehensive_articles.json"):
        """Initialize constitutional advisor with comprehensive articles"""
        # Try different paths for the articles file
        import os
        possible_paths = [
            articles_file,
            f"law_agent/data/{articles_file}",
            f"data/{articles_file}",
            os.path.join(os.path.dirname(__file__), "..", "data", articles_file),
            # Fallback to basic articles
            "article.json",
            f"law_agent/data/article.json",
            f"data/article.json",
            os.path.join(os.path.dirname(__file__), "..", "data", "article.json")
        ]

        articles_path = None
        for path in possible_paths:
            if os.path.exists(path):
                articles_path = path
                logger.info(f"Using constitutional articles from: {path}")
                break

        if not articles_path:
            logger.warning(f"Constitutional articles file not found in any of: {possible_paths}")
            articles_path = articles_file  # Use original path as fallback

        self.db = ConstitutionalDatabase(articles_path)
    
    def get_constitutional_backing(self, domain: str, query: str) -> Dict[str, Any]:
        """Get constitutional articles relevant to a legal query"""
        
        # Get domain-specific articles
        domain_articles = self.db.get_articles_for_domain(domain)
        
        # Search for query-specific articles
        query_articles = self.db.search_articles(query, limit=3)
        
        # Combine and deduplicate
        all_articles = domain_articles + query_articles
        unique_articles = {}
        for article in all_articles:
            if hasattr(article, 'article_number'):
                unique_articles[article.article_number] = article

        relevant_articles = list(unique_articles.values())
        if len(relevant_articles) > 5:
            relevant_articles = relevant_articles[:5]  # Limit to top 5
        
        return {
            'relevant_articles': relevant_articles,
            'constitutional_basis': self._generate_constitutional_basis(relevant_articles, domain),
            'article_count': len(relevant_articles),
            'domain': domain
        }
    
    def _generate_constitutional_basis(self, articles: List[ConstitutionalArticle], domain: str) -> str:
        """Generate constitutional basis text for legal advice"""
        
        if not articles:
            return "Constitutional provisions may apply to this matter. Consult legal expert for specific constitutional references."
        
        basis_parts = []
        
        # Add domain-specific constitutional context
        domain_contexts = {
            'criminal law': "Under the Constitution, you have fundamental rights including protection from arbitrary arrest and fair trial guarantees.",
            'employment law': "The Constitution guarantees equality and prohibits discrimination in employment matters.",
            'family law': "Constitutional provisions protect personal liberty and family rights while ensuring gender equality.",
            'immigration law': "Constitutional citizenship provisions define rights and procedures for Indian citizenship.",
            'elder abuse': "The Constitution's right to life and dignity extends special protection to vulnerable populations including elderly citizens.",
            'cyber crime': "Constitutional rights to privacy and freedom of expression apply to digital spaces and cyber crimes."
        }
        
        if domain in domain_contexts:
            basis_parts.append(domain_contexts[domain])
        
        # Add specific article references
        if len(articles) <= 2:
            for article in articles:
                if article.has_content:
                    basis_parts.append(f"Article {article.article_number}: {article.summary}")
                else:
                    basis_parts.append(f"Article {article.article_number}: {article.clean_title}")
        else:
            article_numbers = [f"Article {a.article_number}" for a in articles[:3]]
            basis_parts.append(f"Relevant constitutional provisions include {', '.join(article_numbers)}.")
        
        return " ".join(basis_parts)
    
    def get_article_details(self, article_number: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific article"""
        article = self.db.get_article(article_number)
        
        if not article:
            return None
        
        return {
            'article_number': article.article_number,
            'title': article.clean_title,
            'content': article.content,
            'summary': article.summary,
            'has_content': article.has_content
        }
    
    def search_constitutional_provisions(self, query: str) -> List[Dict[str, Any]]:
        """Search constitutional provisions by query"""
        articles = self.db.search_articles(query)
        
        return [
            {
                'article_number': article.article_number,
                'title': article.clean_title,
                'summary': article.summary,
                'relevance': 'high' if query.lower() in article.clean_title.lower() else 'medium'
            }
            for article in articles
        ]


def create_constitutional_advisor(articles_file: str = "article.json") -> ConstitutionalAdvisor:
    """Factory function to create constitutional advisor"""
    return ConstitutionalAdvisor(articles_file)


# Test the constitutional integration
if __name__ == "__main__":
    print("🏛️ CONSTITUTIONAL INTEGRATION TEST")
    print("=" * 50)
    
    advisor = create_constitutional_advisor()
    
    # Test domain-specific constitutional backing
    test_cases = [
        ("criminal law", "I was arrested without warrant"),
        ("employment law", "I'm facing workplace discrimination"),
        ("immigration law", "I need help with citizenship application"),
        ("elder abuse", "My elderly father is being mistreated"),
        ("cyber crime", "My privacy was violated online")
    ]
    
    for domain, query in test_cases:
        print(f"\n📋 Domain: {domain.title()}")
        print(f"Query: \"{query}\"")
        print("-" * 40)
        
        backing = advisor.get_constitutional_backing(domain, query)
        
        print(f"Constitutional Articles Found: {backing['article_count']}")
        print(f"Constitutional Basis: {backing['constitutional_basis'][:150]}...")
        
        if backing['relevant_articles']:
            print("Relevant Articles:")
            for article in backing['relevant_articles'][:2]:
                print(f"  • Article {article.article_number}: {article.clean_title[:60]}...")
    
    # Test article search
    print(f"\n🔍 Testing Article Search:")
    print("-" * 30)
    
    search_results = advisor.search_constitutional_provisions("citizenship")
    print(f"Search for 'citizenship' found {len(search_results)} articles:")
    for result in search_results[:3]:
        print(f"  • Article {result['article_number']}: {result['title'][:50]}...")
    
    print(f"\n✅ Constitutional integration ready for Legal Agent!")
    print(f"📊 Database contains {len(advisor.db.articles)} constitutional articles")
    print(f"🎯 Supports {len(advisor.db.domain_mappings)} legal domains")
