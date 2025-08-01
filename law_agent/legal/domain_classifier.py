"""Legal domain classification system using ML and rule-based approaches."""

import re
import json
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

from ..core.state import LegalDomain, AgentState


class LegalDomainClassifier:
    """Intelligent legal domain classifier with ML and rule-based components."""
    
    def __init__(self):
        """Initialize the domain classifier."""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.domain_keywords = self._load_domain_keywords()
        self.domain_embeddings = self._create_domain_embeddings()
        self.legal_patterns = self._load_legal_patterns()
        
        logger.info("Legal Domain Classifier initialized")
    
    def _load_domain_keywords(self) -> Dict[LegalDomain, List[str]]:
        """Load keywords for each legal domain."""
        return {
            LegalDomain.FAMILY_LAW: [
                "divorce", "custody", "child support", "alimony", "marriage", "adoption",
                "domestic violence", "prenuptial", "separation", "visitation", "paternity",
                "guardianship", "family court", "spousal support", "parental rights"
            ],
            LegalDomain.CRIMINAL_LAW: [
                "arrest", "charges", "felony", "misdemeanor", "bail", "trial", "conviction",
                "sentence", "probation", "parole", "criminal defense", "plea bargain",
                "assault", "theft", "fraud", "DUI", "drug charges", "murder", "robbery"
            ],
            LegalDomain.CORPORATE_LAW: [
                "business", "corporation", "LLC", "partnership", "merger", "acquisition",
                "securities", "compliance", "board of directors", "shareholder", "IPO",
                "corporate governance", "business formation", "commercial law", "contracts"
            ],
            LegalDomain.PROPERTY_LAW: [
                "real estate", "property", "deed", "title", "mortgage", "foreclosure",
                "landlord", "tenant", "lease", "eviction", "zoning", "easement",
                "property tax", "boundary dispute", "homeowners association", "HOA"
            ],
            LegalDomain.EMPLOYMENT_LAW: [
                "workplace", "employee", "employer", "discrimination", "harassment",
                "wrongful termination", "wages", "overtime", "benefits", "workers compensation",
                "union", "collective bargaining", "FMLA", "ADA", "workplace safety"
            ],
            LegalDomain.IMMIGRATION_LAW: [
                "visa", "green card", "citizenship", "deportation", "asylum", "refugee",
                "immigration", "naturalization", "work permit", "student visa",
                "family reunification", "border", "ICE", "USCIS", "immigration court"
            ],
            LegalDomain.INTELLECTUAL_PROPERTY: [
                "patent", "trademark", "copyright", "trade secret", "intellectual property",
                "IP", "infringement", "licensing", "royalty", "DMCA", "fair use",
                "brand protection", "invention", "creative work", "software patent"
            ],
            LegalDomain.TAX_LAW: [
                "tax", "IRS", "audit", "deduction", "tax return", "tax evasion",
                "tax planning", "estate tax", "income tax", "sales tax", "property tax",
                "tax liability", "tax refund", "tax penalty", "tax court"
            ],
            LegalDomain.CONSTITUTIONAL_LAW: [
                "constitutional", "civil rights", "first amendment", "freedom of speech",
                "due process", "equal protection", "constitutional violation",
                "civil liberties", "government", "federal", "state rights", "supreme court"
            ],
            LegalDomain.CONTRACT_LAW: [
                "contract", "agreement", "breach", "terms", "conditions", "obligation",
                "performance", "damages", "remedy", "consideration", "offer", "acceptance",
                "contract dispute", "contract negotiation", "contract review"
            ],
            LegalDomain.TORT_LAW: [
                "personal injury", "negligence", "liability", "damages", "accident",
                "medical malpractice", "slip and fall", "car accident", "product liability",
                "defamation", "invasion of privacy", "emotional distress", "wrongful death"
            ],
            LegalDomain.BANKRUPTCY_LAW: [
                "bankruptcy", "debt", "creditor", "debtor", "chapter 7", "chapter 11",
                "chapter 13", "discharge", "liquidation", "reorganization", "trustee",
                "automatic stay", "debt relief", "insolvency", "financial distress"
            ],
            LegalDomain.ENVIRONMENTAL_LAW: [
                "environmental", "pollution", "EPA", "clean air", "clean water",
                "hazardous waste", "environmental impact", "NEPA", "environmental compliance",
                "climate change", "renewable energy", "environmental protection"
            ],
            LegalDomain.HEALTHCARE_LAW: [
                "healthcare", "medical", "HIPAA", "patient rights", "medical records",
                "healthcare compliance", "medical device", "FDA", "pharmaceutical",
                "healthcare fraud", "medical ethics", "telemedicine", "health insurance"
            ]
        }
    
    def _create_domain_embeddings(self) -> Dict[LegalDomain, np.ndarray]:
        """Create embeddings for each legal domain."""
        domain_embeddings = {}
        
        for domain, keywords in self.domain_keywords.items():
            # Combine keywords into a representative text
            domain_text = " ".join(keywords)
            embedding = self.model.encode([domain_text])[0]
            domain_embeddings[domain] = embedding
        
        return domain_embeddings
    
    def _load_legal_patterns(self) -> Dict[LegalDomain, List[str]]:
        """Load regex patterns for legal domain detection."""
        return {
            LegalDomain.FAMILY_LAW: [
                r"\b(divorce|custody|child support|alimony)\b",
                r"\b(family court|domestic relations)\b",
                r"\b(visitation|parental rights)\b"
            ],
            LegalDomain.CRIMINAL_LAW: [
                r"\b(arrested|charged with|criminal case)\b",
                r"\b(felony|misdemeanor|criminal defense)\b",
                r"\b(bail|bond|criminal court)\b"
            ],
            LegalDomain.CORPORATE_LAW: [
                r"\b(business formation|incorporate|LLC)\b",
                r"\b(merger|acquisition|corporate)\b",
                r"\b(shareholder|board of directors)\b"
            ],
            LegalDomain.PROPERTY_LAW: [
                r"\b(real estate|property|deed|title)\b",
                r"\b(landlord|tenant|lease|eviction)\b",
                r"\b(mortgage|foreclosure)\b"
            ],
            LegalDomain.EMPLOYMENT_LAW: [
                r"\b(workplace|employment|wrongful termination)\b",
                r"\b(discrimination|harassment|wages)\b",
                r"\b(workers compensation|union)\b"
            ],
            LegalDomain.IMMIGRATION_LAW: [
                r"\b(visa|green card|citizenship|immigration)\b",
                r"\b(deportation|asylum|naturalization)\b",
                r"\b(USCIS|immigration court)\b"
            ],
            LegalDomain.INTELLECTUAL_PROPERTY: [
                r"\b(patent|trademark|copyright|IP)\b",
                r"\b(infringement|licensing|trade secret)\b",
                r"\b(intellectual property)\b"
            ],
            LegalDomain.TAX_LAW: [
                r"\b(tax|IRS|audit|tax return)\b",
                r"\b(tax evasion|tax planning)\b",
                r"\b(deduction|tax liability)\b"
            ],
            LegalDomain.CONTRACT_LAW: [
                r"\b(contract|agreement|breach)\b",
                r"\b(contract dispute|contract review)\b",
                r"\b(terms and conditions)\b"
            ],
            LegalDomain.TORT_LAW: [
                r"\b(personal injury|negligence|accident)\b",
                r"\b(medical malpractice|slip and fall)\b",
                r"\b(car accident|product liability)\b"
            ],
            LegalDomain.BANKRUPTCY_LAW: [
                r"\b(bankruptcy|debt|creditor|debtor)\b",
                r"\b(chapter 7|chapter 11|chapter 13)\b",
                r"\b(discharge|liquidation)\b"
            ]
        }
    
    async def classify(self, query: str, agent_state: Optional[AgentState] = None) -> Dict[str, Any]:
        """Classify a query into a legal domain."""
        
        # Normalize query
        query_lower = query.lower().strip()
        
        # Step 1: Rule-based classification using patterns
        pattern_scores = self._classify_by_patterns(query_lower)
        
        # Step 2: Keyword-based classification
        keyword_scores = self._classify_by_keywords(query_lower)
        
        # Step 3: Semantic similarity classification
        semantic_scores = self._classify_by_semantics(query)
        
        # Step 4: Context-based adjustment (if agent state available)
        context_scores = {}
        if agent_state:
            context_scores = self._adjust_by_context(agent_state)
        
        # Combine all scores
        final_scores = self._combine_scores(
            pattern_scores, keyword_scores, semantic_scores, context_scores
        )
        
        # Get top prediction
        top_domain = max(final_scores.items(), key=lambda x: x[1])
        domain = top_domain[0]
        confidence = top_domain[1]
        
        # If confidence is too low, mark as unknown
        if confidence < 0.3:
            domain = LegalDomain.UNKNOWN
            confidence = 0.5
        
        logger.debug(f"Classified query '{query[:50]}...' as {domain} with confidence {confidence:.3f}")
        
        return {
            "domain": domain,
            "confidence": confidence,
            "all_scores": final_scores,
            "classification_details": {
                "pattern_scores": pattern_scores,
                "keyword_scores": keyword_scores,
                "semantic_scores": semantic_scores,
                "context_scores": context_scores
            }
        }
    
    def _classify_by_patterns(self, query: str) -> Dict[LegalDomain, float]:
        """Classify using regex patterns."""
        scores = {domain: 0.0 for domain in LegalDomain}
        
        for domain, patterns in self.legal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    scores[domain] += 0.3  # Each pattern match adds 0.3
        
        # Normalize scores
        max_score = max(scores.values()) if max(scores.values()) > 0 else 1
        return {domain: score / max_score for domain, score in scores.items()}
    
    def _classify_by_keywords(self, query: str) -> Dict[LegalDomain, float]:
        """Classify using keyword matching."""
        scores = {domain: 0.0 for domain in LegalDomain}
        query_words = set(query.split())
        
        for domain, keywords in self.domain_keywords.items():
            keyword_set = set(keywords)
            matches = len(query_words.intersection(keyword_set))
            scores[domain] = matches / len(keyword_set) if keyword_set else 0
        
        return scores
    
    def _classify_by_semantics(self, query: str) -> Dict[LegalDomain, float]:
        """Classify using semantic similarity."""
        query_embedding = self.model.encode([query])[0]
        scores = {}
        
        for domain, domain_embedding in self.domain_embeddings.items():
            similarity = cosine_similarity(
                [query_embedding], [domain_embedding]
            )[0][0]
            scores[domain] = max(0, similarity)  # Ensure non-negative
        
        return scores
    
    def _adjust_by_context(self, agent_state: AgentState) -> Dict[LegalDomain, float]:
        """Adjust scores based on user context and history."""
        scores = {domain: 0.0 for domain in LegalDomain}
        
        # Boost domains from user's history
        domain_history = agent_state.get_domain_history()
        total_interactions = sum(domain_history.values())
        
        if total_interactions > 0:
            for domain, count in domain_history.items():
                # Boost score based on frequency (max 0.2 boost)
                boost = min(0.2, count / total_interactions)
                scores[domain] = boost
        
        # Boost preferred domains
        for domain in agent_state.user_profile.preferred_domains:
            scores[domain] += 0.1
        
        return scores
    
    def _combine_scores(
        self, 
        pattern_scores: Dict[LegalDomain, float],
        keyword_scores: Dict[LegalDomain, float],
        semantic_scores: Dict[LegalDomain, float],
        context_scores: Dict[LegalDomain, float]
    ) -> Dict[LegalDomain, float]:
        """Combine all classification scores with weights."""
        
        # Weights for different classification methods
        weights = {
            "patterns": 0.3,
            "keywords": 0.25,
            "semantics": 0.35,
            "context": 0.1
        }
        
        final_scores = {}
        
        for domain in LegalDomain:
            score = (
                weights["patterns"] * pattern_scores.get(domain, 0) +
                weights["keywords"] * keyword_scores.get(domain, 0) +
                weights["semantics"] * semantic_scores.get(domain, 0) +
                weights["context"] * context_scores.get(domain, 0)
            )
            final_scores[domain] = score
        
        return final_scores
    
    def get_domain_confidence_threshold(self, domain: LegalDomain) -> float:
        """Get confidence threshold for a specific domain."""
        # Some domains require higher confidence due to complexity
        high_confidence_domains = {
            LegalDomain.CRIMINAL_LAW: 0.7,
            LegalDomain.CONSTITUTIONAL_LAW: 0.8,
            LegalDomain.TAX_LAW: 0.6
        }
        
        return high_confidence_domains.get(domain, 0.5)
    
    def explain_classification(self, classification_result: Dict[str, Any]) -> str:
        """Generate human-readable explanation of classification."""
        domain = classification_result["domain"]
        confidence = classification_result["confidence"]
        details = classification_result["classification_details"]
        
        explanation = f"This query was classified as {domain.value.replace('_', ' ')} "
        explanation += f"with {confidence:.1%} confidence.\n\n"
        
        explanation += "Classification was based on:\n"
        
        if max(details["pattern_scores"].values()) > 0:
            explanation += "- Legal terminology patterns detected\n"
        
        if max(details["keyword_scores"].values()) > 0:
            explanation += "- Domain-specific keywords found\n"
        
        if max(details["semantic_scores"].values()) > 0:
            explanation += "- Semantic similarity to legal concepts\n"
        
        if max(details["context_scores"].values()) > 0:
            explanation += "- User's previous interaction history\n"
        
        return explanation
