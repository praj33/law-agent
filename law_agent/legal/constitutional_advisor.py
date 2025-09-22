"""
Constitutional Articles Integration for Integrated Law Agent
===========================================================

This module integrates Indian Constitutional articles with the advanced RL law agent
to provide constitutional backing for legal advice and enhance system credibility.

Features:
- Constitutional article search and retrieval
- Domain-specific constitutional references
- Article-based legal precedent support
- Enhanced legal advice with constitutional backing
- Integration with RL learning system

Author: Integrated Law Agent Team
Version: 6.0.0 - Integrated Constitutional Support
Date: 2025-08-04
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from pathlib import Path

from ..core.state import LegalDomain

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalArticle:
    """Data structure for constitutional articles"""
    article_number: str
    title: str
    content: str
    
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
    
    def __init__(self, articles_file: str = "expanded_constitutional_articles.json"):
        """Initialize with constitutional articles"""
        self.articles_file = articles_file
        self.articles: Dict[str, ConstitutionalArticle] = {}
        self.domain_mappings: Dict[LegalDomain, List[str]] = {}
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
                    content=article_data.get('content', '')
                )
                self.articles[article.article_number] = article
            
            logger.info(f"Loaded {len(self.articles)} constitutional articles")
            
        except FileNotFoundError:
            logger.warning(f"Constitutional articles file {self.articles_file} not found")
            self.articles = {}
            self._create_default_articles()
        except Exception as e:
            logger.error(f"Error loading constitutional articles: {e}")
            self.articles = {}
            self._create_default_articles()
    
    def _create_default_articles(self):
        """Create default constitutional articles if file not found"""
        default_articles = [
            {
                "article_number": "14",
                "title": "Equality before law",
                "content": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India."
            },
            {
                "article_number": "19",
                "title": "Protection of certain rights regarding freedom of speech etc.",
                "content": "All citizens shall have the right to freedom of speech and expression, to assemble peaceably and without arms, to form associations or unions, to move freely throughout the territory of India, to reside and settle in any part of the territory of India, and to practice any profession, or to carry on any occupation, trade or business."
            },
            {
                "article_number": "21",
                "title": "Protection of life and personal liberty",
                "content": "No person shall be deprived of his life or personal liberty except according to procedure established by law."
            },
            {
                "article_number": "15",
                "title": "Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth",
                "content": "The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, place of birth or any of them."
            },
            {
                "article_number": "20",
                "title": "Protection in respect of conviction for offences",
                "content": "No person shall be convicted of any offence except for violation of a law in force at the time of the commission of the act charged as an offence, nor be subjected to a penalty greater than that which might have been inflicted under the law in force at the time of the commission of the offence."
            }
        ]
        
        for article_data in default_articles:
            article = ConstitutionalArticle(
                article_number=article_data['article_number'],
                title=article_data['title'],
                content=article_data['content']
            )
            self.articles[article.article_number] = article
        
        logger.info(f"Created {len(self.articles)} default constitutional articles")
    
    def create_domain_mappings(self):
        """Create mappings between legal domains and constitutional articles"""
        
        # Define domain-specific constitutional mappings
        self.domain_mappings = {
            LegalDomain.FAMILY_LAW: ['15', '16', '21', '25'],  # Equality, marriage, personal liberty, religion
            LegalDomain.CRIMINAL_LAW: ['14', '20', '21', '22'],  # Equality, protection from crimes, liberty, arrest
            LegalDomain.EMPLOYMENT_LAW: ['14', '15', '16', '19', '21', '23', '24'],  # Equality, non-discrimination, work
            LegalDomain.CONTRACT_LAW: ['19', '21', '300'],  # Freedom of trade, liberty, property
            LegalDomain.PROPERTY_LAW: ['19', '21', '300'],  # Property rights, life & liberty
            LegalDomain.IMMIGRATION_LAW: ['5', '6', '7', '8', '9', '10'],  # Citizenship articles
            LegalDomain.TAX_LAW: ['19', '265', '266'],  # Trade, taxation
            LegalDomain.INTELLECTUAL_PROPERTY: ['19', '21'],  # Freedom of expression, liberty
            LegalDomain.CONSUMER_LAW: ['19', '21'],  # Trade & commerce, consumer protection
            LegalDomain.CONSTITUTIONAL_LAW: ['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25'],  # Fundamental rights
            LegalDomain.CORPORATE_LAW: ['19', '21', '300'],  # Trade, liberty, property
            LegalDomain.TORT_LAW: ['14', '21'],  # Equality, personal liberty
            LegalDomain.BANKRUPTCY_LAW: ['19', '21'],  # Trade, liberty
            LegalDomain.ENVIRONMENTAL_LAW: ['21', '48A'],  # Life, environment
            LegalDomain.HEALTHCARE_LAW: ['21'],  # Right to life and health
            LegalDomain.UNKNOWN: ['14', '19', '21']  # Basic rights
        }
    
    def get_articles_for_domain(self, domain: LegalDomain) -> List[ConstitutionalArticle]:
        """Get constitutional articles relevant to a legal domain"""
        
        article_numbers = self.domain_mappings.get(domain, [])
        articles = []
        
        for number in article_numbers:
            if number in self.articles:
                articles.append(self.articles[number])
        
        return articles
    
    def search_articles(self, query: str, limit: int = 5) -> List[ConstitutionalArticle]:
        """Search constitutional articles by query text"""
        
        query_lower = query.lower()
        scored_articles = []
        
        for article in self.articles.values():
            score = 0
            
            # Check title match
            if query_lower in article.clean_title.lower():
                score += 3
            
            # Check content match
            if article.has_content and query_lower in article.content.lower():
                score += 2
            
            # Check for keyword matches
            keywords = query_lower.split()
            for keyword in keywords:
                if keyword in article.clean_title.lower():
                    score += 1
                if article.has_content and keyword in article.content.lower():
                    score += 1
            
            if score > 0:
                scored_articles.append((article, score))
        
        # Sort by score and return top results
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        return [article for article, score in scored_articles[:limit]]


class IntegratedConstitutionalAdvisor:
    """Provides constitutional backing for legal advice in integrated RL system"""
    
    def __init__(self, articles_file: str = "expanded_constitutional_articles.json"):
        """Initialize constitutional advisor"""
        self.db = ConstitutionalDatabase(articles_file)
    
    def get_constitutional_backing(self, domain: LegalDomain, query: str) -> Dict[str, Any]:
        """Get constitutional articles relevant to a legal query"""

        # Get query-specific articles first (more relevant)
        query_articles = self.db.search_articles(query, limit=4)

        # Get domain-specific articles as backup
        domain_articles = self.db.get_articles_for_domain(domain)

        # Prioritize query-specific articles
        all_articles = query_articles + domain_articles
        unique_articles = {}
        for article in all_articles:
            unique_articles[article.article_number] = article

        relevant_articles = list(unique_articles.values())[:3]  # Limit to top 3 for variety

        # If no query-specific articles found, use different domain articles based on query keywords
        if not query_articles:
            relevant_articles = self._get_keyword_specific_articles(query, domain)

        return {
            'relevant_articles': relevant_articles,
            'constitutional_basis': self._generate_constitutional_basis(relevant_articles, domain),
            'article_count': len(relevant_articles),
            'domain': domain,
            'enhanced_credibility': True,
            'query_specific': len(query_articles) > 0
        }

    def _get_keyword_specific_articles(self, query: str, domain: LegalDomain) -> List[ConstitutionalArticle]:
        """Get articles based on specific keywords in the query."""
        query_lower = query.lower()

        # Define keyword to article mappings for more variety
        keyword_mappings = {
            # Family law keywords
            "divorce": [14, 19, 21],
            "custody": [14, 19, 20],
            "marriage": [14, 15, 21],
            "child": [19, 20, 24],

            # Criminal law keywords
            "arrest": [20, 22, 23],
            "police": [20, 21, 22],
            "theft": [20, 22, 31],
            "criminal": [20, 21, 22],

            # Employment keywords
            "fired": [14, 16, 19],
            "discrimination": [14, 15, 16],
            "work": [16, 19, 23],
            "job": [14, 16, 19],

            # Property keywords
            "evict": [19, 25, 300],
            "landlord": [19, 25, 26],
            "property": [25, 26, 31],
            "house": [25, 26, 19]
        }

        # Find matching articles based on keywords
        matching_articles = []
        for keyword, article_numbers in keyword_mappings.items():
            if keyword in query_lower:
                for article_num in article_numbers[:2]:  # Limit to 2 per keyword
                    article = self.db.get_article_by_number(article_num)
                    if article:
                        matching_articles.append(article)

        # If no keyword matches, return domain-specific articles
        if not matching_articles:
            domain_articles = self.db.get_articles_for_domain(domain)
            return domain_articles[:3]

        # Remove duplicates and limit
        unique_articles = {}
        for article in matching_articles:
            unique_articles[article.article_number] = article

        return list(unique_articles.values())[:3]

    def _generate_constitutional_basis(self, articles: List[ConstitutionalArticle], domain: LegalDomain) -> str:
        """Generate constitutional basis text for legal advice"""
        
        if not articles:
            return "Constitutional provisions may apply to this matter. Consult legal expert for specific constitutional references."
        
        basis_parts = []
        
        # Add domain-specific constitutional context
        domain_contexts = {
            LegalDomain.CRIMINAL_LAW: "Under the Constitution, you have fundamental rights including protection from arbitrary arrest and fair trial guarantees.",
            LegalDomain.EMPLOYMENT_LAW: "The Constitution guarantees equality and prohibits discrimination in employment matters.",
            LegalDomain.FAMILY_LAW: "Constitutional provisions protect personal liberty and family rights while ensuring gender equality.",
            LegalDomain.IMMIGRATION_LAW: "Constitutional citizenship provisions define rights and procedures for Indian citizenship.",
            LegalDomain.PROPERTY_LAW: "The Constitution protects property rights and ensures due process in property matters.",
            LegalDomain.CONSUMER_LAW: "Constitutional provisions protect citizens' rights in commercial transactions and consumer protection.",
            LegalDomain.CONTRACT_LAW: "The Constitution guarantees freedom of trade and commerce, supporting contractual rights.",
            LegalDomain.TAX_LAW: "Constitutional provisions govern taxation powers and taxpayer rights.",
            LegalDomain.INTELLECTUAL_PROPERTY: "Constitutional freedom of expression and trade support intellectual property rights.",
            LegalDomain.CONSTITUTIONAL_LAW: "Fundamental rights and constitutional provisions directly apply to this matter."
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
    
    def enhance_legal_response(self, response: str, domain: LegalDomain, query: str) -> Dict[str, Any]:
        """Enhance legal response with constitutional backing"""
        
        constitutional_backing = self.get_constitutional_backing(domain, query)
        
        enhanced_response = {
            'original_response': response,
            'constitutional_backing': constitutional_backing['constitutional_basis'],
            'relevant_articles': constitutional_backing['relevant_articles'],
            'enhanced_response': f"{response}\n\nConstitutional Basis: {constitutional_backing['constitutional_basis']}",
            'credibility_enhanced': True,
            'article_count': constitutional_backing['article_count']
        }
        
        return enhanced_response
    
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Get constitutional advisor statistics"""
        return {
            'total_articles': len(self.db.articles),
            'domain_mappings': len(self.db.domain_mappings),
            'supported_domains': list(self.db.domain_mappings.keys()),
            'integration_status': 'active'
        }


def create_integrated_constitutional_advisor(articles_file: str = "expanded_constitutional_articles.json") -> IntegratedConstitutionalAdvisor:
    """Factory function to create integrated constitutional advisor"""
    return IntegratedConstitutionalAdvisor(articles_file)


# Test function
if __name__ == "__main__":
    print("🏛️ Testing Integrated Constitutional Advisor")
    print("=" * 50)
    
    advisor = create_integrated_constitutional_advisor()
    
    # Test domain-specific constitutional backing
    test_cases = [
        (LegalDomain.CRIMINAL_LAW, "I was arrested without warrant"),
        (LegalDomain.EMPLOYMENT_LAW, "I'm facing workplace discrimination"),
        (LegalDomain.FAMILY_LAW, "I want to file for divorce"),
        (LegalDomain.PROPERTY_LAW, "Landlord won't return my deposit"),
        (LegalDomain.CONSUMER_LAW, "I received a defective product")
    ]
    
    for domain, query in test_cases:
        print(f"\n📋 Domain: {domain}")
        print(f"Query: \"{query}\"")
        print("-" * 40)
        
        backing = advisor.get_constitutional_backing(domain, query)
        
        print(f"Constitutional Articles Found: {backing['article_count']}")
        print(f"Constitutional Basis: {backing['constitutional_basis'][:150]}...")
        
        if backing['relevant_articles']:
            print("Relevant Articles:")
            for article in backing['relevant_articles'][:2]:
                print(f"  • Article {article.article_number}: {article.clean_title[:60]}...")
    
    # Test enhanced response
    print(f"\n🔍 Testing Enhanced Response:")
    print("-" * 30)
    
    sample_response = "You have the right to file a complaint with the consumer protection forum."
    enhanced = advisor.enhance_legal_response(sample_response, LegalDomain.CONSUMER_LAW, "defective product")
    
    print(f"Original: {enhanced['original_response']}")
    print(f"Enhanced: {enhanced['enhanced_response'][:200]}...")
    print(f"Articles Referenced: {enhanced['article_count']}")
    
    # Get stats
    stats = advisor.get_stats()
    print(f"\n📊 Constitutional Advisor Stats:")
    print(f"   Total Articles: {stats['total_articles']}")
    print(f"   Domain Mappings: {stats['domain_mappings']}")
    print(f"   Integration Status: {stats['integration_status']}")
    
    print(f"\n✅ Integrated Constitutional Advisor ready!")
    print(f"🎯 Enhanced legal responses with constitutional backing")
