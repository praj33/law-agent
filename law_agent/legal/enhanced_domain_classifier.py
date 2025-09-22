"""
Enhanced ML-Driven Domain Classifier for Integrated Law Agent
============================================================

This module integrates the ML-driven domain classifier from the Grok system
with the current advanced RL law agent system, providing:

- TF-IDF + Naive Bayes classification
- Cosine similarity scoring
- Confidence-based predictions
- Retrainable models with feedback integration
- Seamless integration with existing RL system

Author: Integrated Law Agent Team
Version: 6.0.0 - Integrated ML Classification
Date: 2025-08-04
"""

import pandas as pd
import numpy as np
import json
import pickle
from typing import Dict, List, Optional, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import logging
from pathlib import Path
import re
from datetime import datetime

from ..core.state import LegalDomain, AgentState

# Configure logging
logger = logging.getLogger(__name__)


class EnhancedMLDomainClassifier:
    """Enhanced ML-driven domain classifier integrated with RL system"""
    
    def __init__(self, 
                 training_data_file: str = "enhanced_training_data.json",
                 model_file: str = "enhanced_domain_classifier_model.pkl",
                 vectorizer_file: str = "enhanced_tfidf_vectorizer.pkl"):
        """Initialize enhanced ML domain classifier"""
        
        self.training_data_file = training_data_file
        self.model_file = model_file
        self.vectorizer_file = vectorizer_file
        
        # ML components
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 3),
            max_features=5000,
            min_df=1,
            max_df=0.95,
            lowercase=True
        )
        
        self.nb_classifier = MultinomialNB(alpha=0.1)
        self.cosine_threshold = 0.15
        self.confidence_threshold = 0.25
        
        # Training data and models
        self.training_data = []
        self.X_vectorized = None
        self.y_labels = None
        self.domain_labels = []
        self.is_trained = False
        
        # Performance tracking
        self.classification_history = []
        self.feedback_data = []
        
        # Domain mapping for integration with existing system
        self.domain_mapping = {
            'family_law': LegalDomain.FAMILY_LAW,
            'criminal_law': LegalDomain.CRIMINAL_LAW,
            'contract_law': LegalDomain.CONTRACT_LAW,
            'employment_law': LegalDomain.EMPLOYMENT_LAW,
            'property_law': LegalDomain.PROPERTY_LAW,
            'immigration_law': LegalDomain.IMMIGRATION_LAW,
            'tax_law': LegalDomain.TAX_LAW,
            'intellectual_property': LegalDomain.INTELLECTUAL_PROPERTY,
            'consumer_law': LegalDomain.CONSUMER_LAW,
            'constitutional_law': LegalDomain.CONSTITUTIONAL_LAW,
            'corporate_law': LegalDomain.CORPORATE_LAW,
            'tort_law': LegalDomain.TORT_LAW,
            'bankruptcy_law': LegalDomain.BANKRUPTCY_LAW,
            'environmental_law': LegalDomain.ENVIRONMENTAL_LAW,
            'healthcare_law': LegalDomain.HEALTHCARE_LAW,
            'unknown': LegalDomain.UNKNOWN
        }
        
        # Initialize system
        self.load_or_create_training_data()
        self.load_or_train_models()
    
    def load_or_create_training_data(self):
        """Load existing training data or create comprehensive initial dataset"""
        
        if Path(self.training_data_file).exists():
            try:
                with open(self.training_data_file, 'r', encoding='utf-8') as f:
                    self.training_data = json.load(f)
                logger.info(f"Loaded {len(self.training_data)} training examples")
                return
            except Exception as e:
                logger.warning(f"Error loading training data: {e}")
        
        # Create comprehensive training dataset
        self.training_data = self._create_comprehensive_training_data()
        self.save_training_data()
        logger.info(f"Created {len(self.training_data)} training examples")
    
    def _create_comprehensive_training_data(self) -> List[Dict]:
        """Create comprehensive training dataset for all legal domains"""
        
        training_examples = [
            # Family Law
            {"text": "I want to file for divorce from my spouse", "domain": "family_law"},
            {"text": "Child custody dispute with my ex-husband", "domain": "family_law"},
            {"text": "My wife is asking for alimony after separation", "domain": "family_law"},
            {"text": "Domestic violence case against my partner", "domain": "family_law"},
            {"text": "Adoption process for my stepchild", "domain": "family_law"},
            {"text": "Marriage annulment due to fraud", "domain": "family_law"},
            {"text": "Prenuptial agreement before wedding", "domain": "family_law"},
            
            # Criminal Law
            {"text": "I was arrested for theft charges", "domain": "criminal_law"},
            {"text": "DUI case and license suspension", "domain": "criminal_law"},
            {"text": "Assault charges filed against me", "domain": "criminal_law"},
            {"text": "Drug possession arrest last night", "domain": "criminal_law"},
            {"text": "Fraud allegations by my employer", "domain": "criminal_law"},
            {"text": "Bail hearing for my brother", "domain": "criminal_law"},
            {"text": "Criminal defense for robbery case", "domain": "criminal_law"},
            
            # Contract Law
            {"text": "Breach of contract by my business partner", "domain": "contract_law"},
            {"text": "Vendor not delivering goods as agreed", "domain": "contract_law"},
            {"text": "Employment contract dispute with company", "domain": "contract_law"},
            {"text": "Real estate purchase agreement issues", "domain": "contract_law"},
            {"text": "Service provider violated our contract", "domain": "contract_law"},
            {"text": "Non-disclosure agreement enforcement", "domain": "contract_law"},
            {"text": "Construction contract delays and penalties", "domain": "contract_law"},
            
            # Employment Law
            {"text": "Wrongful termination from my job", "domain": "employment_law"},
            {"text": "Workplace discrimination based on gender", "domain": "employment_law"},
            {"text": "Unpaid overtime wages by employer", "domain": "employment_law"},
            {"text": "Sexual harassment at workplace", "domain": "employment_law"},
            {"text": "Workers compensation claim denied", "domain": "employment_law"},
            {"text": "Non-compete clause in employment contract", "domain": "employment_law"},
            {"text": "Whistleblower protection after reporting", "domain": "employment_law"},
            
            # Property Law
            {"text": "Landlord won't return my security deposit", "domain": "property_law"},
            {"text": "Property boundary dispute with neighbor", "domain": "property_law"},
            {"text": "Eviction notice from my landlord", "domain": "property_law"},
            {"text": "Real estate transaction gone wrong", "domain": "property_law"},
            {"text": "Zoning violation notice from city", "domain": "property_law"},
            {"text": "Property inheritance dispute with siblings", "domain": "property_law"},
            {"text": "Homeowners association fee dispute", "domain": "property_law"},
            
            # Immigration Law
            {"text": "Green card application status", "domain": "immigration_law"},
            {"text": "Deportation proceedings against me", "domain": "immigration_law"},
            {"text": "Visa denial for my spouse", "domain": "immigration_law"},
            {"text": "Citizenship test preparation help", "domain": "immigration_law"},
            {"text": "Work permit extension request", "domain": "immigration_law"},
            {"text": "Asylum application process", "domain": "immigration_law"},
            {"text": "Immigration court hearing scheduled", "domain": "immigration_law"},
            
            # Tax Law
            {"text": "IRS audit of my tax returns", "domain": "tax_law"},
            {"text": "Tax debt settlement with government", "domain": "tax_law"},
            {"text": "Business tax deduction questions", "domain": "tax_law"},
            {"text": "Property tax assessment appeal", "domain": "tax_law"},
            {"text": "Tax lien on my property", "domain": "tax_law"},
            {"text": "Estate tax planning for inheritance", "domain": "tax_law"},
            {"text": "Sales tax compliance for business", "domain": "tax_law"},
            
            # Intellectual Property
            {"text": "Patent application for my invention", "domain": "intellectual_property"},
            {"text": "Trademark infringement by competitor", "domain": "intellectual_property"},
            {"text": "Copyright violation of my artwork", "domain": "intellectual_property"},
            {"text": "Trade secret theft by former employee", "domain": "intellectual_property"},
            {"text": "Software licensing agreement dispute", "domain": "intellectual_property"},
            {"text": "Domain name cybersquatting case", "domain": "intellectual_property"},
            {"text": "DMCA takedown notice received", "domain": "intellectual_property"},
            
            # Consumer Law
            {"text": "Defective product warranty claim", "domain": "consumer_law"},
            {"text": "Credit card fraud charges", "domain": "consumer_law"},
            {"text": "Debt collection harassment", "domain": "consumer_law"},
            {"text": "False advertising by company", "domain": "consumer_law"},
            {"text": "Identity theft protection needed", "domain": "consumer_law"},
            {"text": "Lemon law claim for defective car", "domain": "consumer_law"},
            {"text": "Telemarketing calls violation", "domain": "consumer_law"},
            
            # Constitutional Law
            {"text": "First Amendment free speech violation", "domain": "constitutional_law"},
            {"text": "Fourth Amendment search and seizure", "domain": "constitutional_law"},
            {"text": "Due process rights violation", "domain": "constitutional_law"},
            {"text": "Equal protection under law", "domain": "constitutional_law"},
            {"text": "Religious freedom exercise", "domain": "constitutional_law"},
            {"text": "Government overreach complaint", "domain": "constitutional_law"},
            {"text": "Civil rights violation by police", "domain": "constitutional_law"}
        ]
        
        return training_examples
    
    def save_training_data(self):
        """Save training data to file"""
        try:
            with open(self.training_data_file, 'w', encoding='utf-8') as f:
                json.dump(self.training_data, f, indent=2, ensure_ascii=False)
            logger.info("Training data saved successfully")
        except Exception as e:
            logger.error(f"Error saving training data: {e}")
    
    def load_or_train_models(self):
        """Load existing models or train new ones"""
        
        if Path(self.model_file).exists() and Path(self.vectorizer_file).exists():
            try:
                with open(self.model_file, 'rb') as f:
                    self.nb_classifier = pickle.load(f)
                with open(self.vectorizer_file, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                # Load domain labels and prepare training data for cosine similarity
                self.domain_labels = list(set([item['domain'] for item in self.training_data]))

                # Prepare training data for cosine similarity
                texts = [item['text'] for item in self.training_data]
                domains = [item['domain'] for item in self.training_data]

                # Vectorize training texts with loaded vectorizer
                self.X_vectorized = self.vectorizer.transform(texts)
                self.y_labels = domains

                self.is_trained = True
                logger.info("Loaded pre-trained enhanced models")
                return
            except Exception as e:
                logger.warning(f"Error loading models: {e}")
        
        # Train new models
        self.train_models()
    
    def train_models(self):
        """Train ML models on current training data"""
        
        if not self.training_data:
            logger.error("No training data available")
            return False
        
        # Prepare training data
        texts = [item['text'] for item in self.training_data]
        domains = [item['domain'] for item in self.training_data]
        
        # Vectorize texts
        self.X_vectorized = self.vectorizer.fit_transform(texts)
        self.y_labels = domains
        self.domain_labels = list(set(domains))
        
        # Train Naive Bayes classifier
        self.nb_classifier.fit(self.X_vectorized, self.y_labels)
        
        # Evaluate model
        X_train, X_test, y_train, y_test = train_test_split(
            self.X_vectorized, self.y_labels, test_size=0.2, random_state=42
        )
        
        self.nb_classifier.fit(X_train, y_train)
        y_pred = self.nb_classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Enhanced model trained with accuracy: {accuracy:.3f}")
        
        # Save models
        self.save_models()
        self.is_trained = True
        
        return True
    
    def save_models(self):
        """Save trained models to files"""
        try:
            with open(self.model_file, 'wb') as f:
                pickle.dump(self.nb_classifier, f)
            with open(self.vectorizer_file, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            logger.info("Enhanced models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    async def classify(self, query: str, agent_state: Optional[AgentState] = None) -> Dict[str, Any]:
        """
        Enhanced classification method compatible with existing RL system
        
        Returns classification result in format expected by RL system
        """
        
        if not self.is_trained:
            logger.error("Enhanced models not trained")
            return {
                "domain": LegalDomain.UNKNOWN,
                "confidence": 0.0,
                "all_scores": {},
                "classification_details": {}
            }

        # Check if required components are available
        if self.X_vectorized is None or self.y_labels is None:
            logger.error("Training data not properly loaded for cosine similarity")
            return {
                "domain": LegalDomain.UNKNOWN,
                "confidence": 0.0,
                "all_scores": {},
                "classification_details": {}
            }
        
        # Clean and vectorize query
        cleaned_query = self._clean_query(query)
        query_vector = self.vectorizer.transform([cleaned_query])
        
        # Get Naive Bayes predictions with probabilities
        nb_probabilities = self.nb_classifier.predict_proba(query_vector)[0]
        nb_classes = self.nb_classifier.classes_
        
        # Get cosine similarities
        cosine_similarities = cosine_similarity(query_vector, self.X_vectorized).flatten()
        
        # Combine predictions
        domain_scores = {}
        
        # Add Naive Bayes scores (weighted 0.7)
        for i, domain in enumerate(nb_classes):
            domain_scores[domain] = nb_probabilities[i] * 0.7
        
        # Add cosine similarity scores (weighted 0.3)
        for i, similarity in enumerate(cosine_similarities):
            domain = self.y_labels[i]
            if domain in domain_scores:
                domain_scores[domain] += similarity * 0.3
            else:
                domain_scores[domain] = similarity * 0.3
        
        # Sort by combined score
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get primary prediction
        primary_domain_str, primary_confidence = sorted_domains[0]
        
        # Map to LegalDomain enum
        primary_domain = self.domain_mapping.get(primary_domain_str, LegalDomain.UNKNOWN)
        
        # Check confidence threshold
        if primary_confidence < self.confidence_threshold:
            primary_domain = LegalDomain.UNKNOWN
            primary_confidence = 0.5
        
        # Record classification
        self.classification_history.append({
            'query': query,
            'domain': primary_domain_str,
            'confidence': primary_confidence,
            'timestamp': datetime.now().isoformat()
        })
        
        # Convert all scores to LegalDomain enum format
        all_scores = {}
        for domain_str, score in domain_scores.items():
            domain_enum = self.domain_mapping.get(domain_str, LegalDomain.UNKNOWN)
            all_scores[domain_enum] = score
        
        logger.debug(f"Enhanced ML classified query '{query[:50]}...' as {primary_domain} with confidence {primary_confidence:.3f}")
        
        return {
            "domain": primary_domain,
            "confidence": primary_confidence,
            "all_scores": all_scores,
            "classification_details": {
                "ml_method": "TF-IDF + Naive Bayes + Cosine Similarity",
                "alternatives": sorted_domains[:3],
                "enhanced_features": True
            }
        }
    
    def _clean_query(self, query: str) -> str:
        """Clean and preprocess query text"""
        # Convert to lowercase
        query = query.lower()
        
        # Remove special characters but keep spaces
        query = re.sub(r'[^\w\s]', ' ', query)
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        return query
    
    def add_feedback(self, query: str, predicted_domain: str, actual_domain: str, helpful: bool):
        """Add user feedback for model improvement"""
        
        feedback = {
            'query': query,
            'predicted_domain': predicted_domain,
            'actual_domain': actual_domain,
            'helpful': helpful,
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_data.append(feedback)
        
        # If feedback indicates wrong prediction, add as training example
        if not helpful and actual_domain != predicted_domain and actual_domain != 'unknown':
            self.add_training_example(actual_domain, query)
        
        logger.info(f"Enhanced ML classifier feedback: {predicted_domain} -> {actual_domain} ({'helpful' if helpful else 'not helpful'})")
    
    def add_training_example(self, domain: str, text: str):
        """Add new training example"""
        new_example = {"text": text, "domain": domain}
        if new_example not in self.training_data:
            self.training_data.append(new_example)
            self.save_training_data()
            logger.info(f"Added training example for domain: {domain}")
    
    def retrain_with_feedback(self):
        """Retrain models incorporating user feedback"""
        
        if not self.feedback_data:
            logger.info("No feedback data available for retraining")
            return False
        
        # Add helpful corrections as training examples
        for feedback in self.feedback_data:
            if not feedback['helpful'] and feedback['actual_domain'] != 'unknown':
                # Add corrected example
                new_example = {
                    'text': feedback['query'],
                    'domain': feedback['actual_domain']
                }
                if new_example not in self.training_data:
                    self.training_data.append(new_example)
        
        # Retrain models
        logger.info("Retraining enhanced models with feedback data")
        return self.train_models()
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            "training_examples": len(self.training_data),
            "domains": self.domain_labels,
            "model_type": "Enhanced TF-IDF + Naive Bayes + Cosine Similarity",
            "is_trained": self.is_trained,
            "feedback_count": len(self.feedback_data),
            "classification_count": len(self.classification_history)
        }


def create_enhanced_ml_domain_classifier() -> EnhancedMLDomainClassifier:
    """Factory function to create enhanced ML domain classifier"""
    return EnhancedMLDomainClassifier()


# Test function
if __name__ == "__main__":
    print("🚀 Testing Enhanced ML Domain Classifier")
    print("=" * 50)
    
    classifier = create_enhanced_ml_domain_classifier()
    
    test_queries = [
        "I want to file for divorce from my husband",
        "My employer fired me without cause",
        "Landlord won't return my security deposit",
        "I was arrested for DUI last night",
        "Patent application for my invention"
    ]
    
    print(f"📊 Enhanced Model Stats:")
    stats = classifier.get_model_stats()
    print(f"   Training Examples: {stats['training_examples']}")
    print(f"   Domains: {len(stats['domains'])}")
    print(f"   Model Type: {stats['model_type']}")
    
    print(f"\n🧪 Testing Enhanced ML Classification:")
    print("-" * 40)
    
    import asyncio
    
    async def test_classification():
        for query in test_queries:
            result = await classifier.classify(query)
            
            print(f"\nQuery: \"{query}\"")
            print(f"Domain: {result['domain']} (confidence: {result['confidence']:.3f})")
            print(f"Method: {result['classification_details']['ml_method']}")
    
    asyncio.run(test_classification())
    
    print(f"\n✅ Enhanced ML Domain Classifier ready for integration!")
    print(f"🎯 Advanced ML classification with RL system compatibility")
