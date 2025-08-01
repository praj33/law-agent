"""Legal glossary and knowledge base system."""

import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from loguru import logger

from ..core.state import LegalDomain


@dataclass
class LegalTerm:
    """Represents a legal term with definition and metadata."""
    term: str
    definition: str
    domain: LegalDomain
    complexity: str  # "basic", "intermediate", "advanced"
    related_terms: List[str]
    examples: List[str]
    synonyms: List[str]
    see_also: List[str]
    common_usage: str
    professional_usage: str


class LegalGlossary:
    """Comprehensive legal glossary with contextual definitions."""
    
    def __init__(self):
        """Initialize the legal glossary."""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.terms = self._load_legal_terms()
        self.term_embeddings = self._create_term_embeddings()
        self.term_index = self._create_term_index()
        
        logger.info(f"Legal Glossary initialized with {len(self.terms)} terms")
    
    def _load_legal_terms(self) -> Dict[str, LegalTerm]:
        """Load comprehensive legal terminology."""
        terms = {}
        
        # Family Law Terms
        family_terms = [
            LegalTerm(
                term="custody",
                definition="Legal responsibility for the care and control of a child, including physical custody (where the child lives) and legal custody (decision-making authority).",
                domain=LegalDomain.FAMILY_LAW,
                complexity="basic",
                related_terms=["visitation", "parental rights", "best interest"],
                examples=[
                    "Joint custody allows both parents to make decisions about the child's welfare.",
                    "Physical custody determines where the child primarily resides."
                ],
                synonyms=["child custody", "parental custody"],
                see_also=["guardianship", "parenting plan"],
                common_usage="Who gets to keep the children and make decisions about their lives.",
                professional_usage="Legal and physical custody arrangements as determined by court order or agreement."
            ),
            LegalTerm(
                term="alimony",
                definition="Financial support paid by one spouse to another after separation or divorce, also known as spousal support or maintenance.",
                domain=LegalDomain.FAMILY_LAW,
                complexity="basic",
                related_terms=["divorce", "spousal support", "maintenance"],
                examples=[
                    "Temporary alimony may be awarded during divorce proceedings.",
                    "Permanent alimony is less common in modern divorce cases."
                ],
                synonyms=["spousal support", "maintenance", "spousal maintenance"],
                see_also=["child support", "property division"],
                common_usage="Money one ex-spouse pays to the other after divorce.",
                professional_usage="Court-ordered financial support based on factors including marriage duration, earning capacity, and standard of living."
            ),
            LegalTerm(
                term="best interest of the child",
                definition="Legal standard used by courts to determine custody and visitation arrangements, focusing on what arrangement will best serve the child's physical, emotional, and developmental needs.",
                domain=LegalDomain.FAMILY_LAW,
                complexity="intermediate",
                related_terms=["custody", "parenting plan", "child welfare"],
                examples=[
                    "Courts consider the child's relationship with each parent when determining best interest.",
                    "The best interest standard may prioritize stability and continuity in the child's life."
                ],
                synonyms=["child's best interest", "best interest standard"],
                see_also=["parental fitness", "child advocacy"],
                common_usage="What's best for the child in custody decisions.",
                professional_usage="Multi-factor legal test examining child's physical, emotional, educational, and social needs."
            )
        ]
        
        # Criminal Law Terms
        criminal_terms = [
            LegalTerm(
                term="arraignment",
                definition="Initial court appearance where the defendant is formally charged and enters a plea of guilty, not guilty, or no contest.",
                domain=LegalDomain.CRIMINAL_LAW,
                complexity="basic",
                related_terms=["plea", "charges", "bail"],
                examples=[
                    "At arraignment, the defendant was informed of the charges and entered a not guilty plea.",
                    "Bail was set at $10,000 during the arraignment hearing."
                ],
                synonyms=["initial appearance", "first appearance"],
                see_also=["indictment", "preliminary hearing"],
                common_usage="First court appearance where you're told what you're charged with.",
                professional_usage="Formal reading of charges and entry of plea, with determination of bail and future court dates."
            ),
            LegalTerm(
                term="probable cause",
                definition="Reasonable belief that a crime has been committed and that a specific person committed it, required for arrests and search warrants.",
                domain=LegalDomain.CRIMINAL_LAW,
                complexity="intermediate",
                related_terms=["search warrant", "arrest", "evidence"],
                examples=[
                    "Police must have probable cause before making an arrest.",
                    "The judge found probable cause to issue a search warrant."
                ],
                synonyms=["reasonable suspicion", "reasonable belief"],
                see_also=["Fourth Amendment", "search and seizure"],
                common_usage="Good reason to believe someone committed a crime.",
                professional_usage="Constitutional standard requiring more than mere suspicion but less than proof beyond reasonable doubt."
            ),
            LegalTerm(
                term="plea bargain",
                definition="Agreement between prosecutor and defendant where defendant pleads guilty to lesser charge or receives reduced sentence in exchange for cooperation or avoiding trial.",
                domain=LegalDomain.CRIMINAL_LAW,
                complexity="basic",
                related_terms=["plea", "sentencing", "prosecution"],
                examples=[
                    "The defendant accepted a plea bargain to avoid the risk of a longer sentence at trial.",
                    "Plea bargains resolve the majority of criminal cases without going to trial."
                ],
                synonyms=["plea agreement", "plea deal"],
                see_also=["sentencing", "trial"],
                common_usage="Deal where you plead guilty to a lesser charge to avoid worse punishment.",
                professional_usage="Negotiated resolution involving guilty plea in exchange for prosecutorial concessions."
            )
        ]
        
        # Corporate Law Terms
        corporate_terms = [
            LegalTerm(
                term="LLC",
                definition="Limited Liability Company - a business structure that combines elements of corporations and partnerships, providing limited liability protection with flexible management structure.",
                domain=LegalDomain.CORPORATE_LAW,
                complexity="basic",
                related_terms=["corporation", "partnership", "limited liability"],
                examples=[
                    "An LLC protects personal assets from business debts.",
                    "LLCs offer tax flexibility not available to corporations."
                ],
                synonyms=["Limited Liability Company"],
                see_also=["corporation", "partnership", "sole proprietorship"],
                common_usage="Business structure that protects your personal assets from business problems.",
                professional_usage="Hybrid entity providing corporate liability protection with partnership tax treatment and operational flexibility."
            ),
            LegalTerm(
                term="fiduciary duty",
                definition="Legal obligation to act in the best interest of another party, requiring loyalty, care, and good faith in business relationships.",
                domain=LegalDomain.CORPORATE_LAW,
                complexity="advanced",
                related_terms=["board of directors", "corporate governance", "breach of duty"],
                examples=[
                    "Corporate directors owe fiduciary duties to shareholders.",
                    "Breach of fiduciary duty can result in personal liability."
                ],
                synonyms=["fiduciary obligation", "duty of loyalty"],
                see_also=["corporate governance", "business judgment rule"],
                common_usage="Legal duty to put someone else's interests first.",
                professional_usage="Highest standard of care requiring undivided loyalty and exercise of reasonable care in decision-making."
            )
        ]
        
        # Property Law Terms
        property_terms = [
            LegalTerm(
                term="deed",
                definition="Legal document that transfers ownership of real property from one party to another, containing description of property and signatures of parties.",
                domain=LegalDomain.PROPERTY_LAW,
                complexity="basic",
                related_terms=["title", "property transfer", "real estate"],
                examples=[
                    "The warranty deed guarantees clear title to the property.",
                    "A quitclaim deed transfers only the interest the grantor has in the property."
                ],
                synonyms=["property deed", "title deed"],
                see_also=["title insurance", "closing"],
                common_usage="Document that proves you own property.",
                professional_usage="Formal instrument of conveyance transferring legal title with specific warranties and covenants."
            ),
            LegalTerm(
                term="easement",
                definition="Legal right to use another person's property for a specific purpose, such as access or utilities, without owning the property.",
                domain=LegalDomain.PROPERTY_LAW,
                complexity="intermediate",
                related_terms=["property rights", "access", "utilities"],
                examples=[
                    "The utility company has an easement to maintain power lines across the property.",
                    "A driveway easement allows access to a landlocked parcel."
                ],
                synonyms=["right of way", "property easement"],
                see_also=["covenant", "property rights"],
                common_usage="Right to use someone else's property for a specific purpose.",
                professional_usage="Non-possessory interest in land granting specific use rights while ownership remains with another party."
            )
        ]
        
        # Employment Law Terms
        employment_terms = [
            LegalTerm(
                term="at-will employment",
                definition="Employment relationship where either employer or employee can terminate the relationship at any time, for any reason, or no reason, without advance notice.",
                domain=LegalDomain.EMPLOYMENT_LAW,
                complexity="basic",
                related_terms=["wrongful termination", "employment contract", "termination"],
                examples=[
                    "At-will employment allows employers to fire employees without cause.",
                    "Exceptions to at-will employment include discrimination and retaliation."
                ],
                synonyms=["employment at will"],
                see_also=["wrongful termination", "employment contract"],
                common_usage="Either you or your employer can end the job at any time for any reason.",
                professional_usage="Default employment relationship absent contractual or statutory limitations on termination."
            ),
            LegalTerm(
                term="hostile work environment",
                definition="Form of workplace harassment where discriminatory conduct creates an intimidating, hostile, or offensive work environment that interferes with work performance.",
                domain=LegalDomain.EMPLOYMENT_LAW,
                complexity="intermediate",
                related_terms=["harassment", "discrimination", "workplace"],
                examples=[
                    "Repeated offensive jokes based on race can create a hostile work environment.",
                    "A hostile work environment claim requires showing the conduct was severe or pervasive."
                ],
                synonyms=["workplace harassment", "discriminatory work environment"],
                see_also=["sexual harassment", "discrimination"],
                common_usage="Workplace where harassment makes it difficult or unpleasant to do your job.",
                professional_usage="Actionable harassment claim requiring severe or pervasive conduct affecting terms and conditions of employment."
            )
        ]
        
        # Combine all terms
        all_terms = family_terms + criminal_terms + corporate_terms + property_terms + employment_terms
        
        for term in all_terms:
            terms[term.term.lower()] = term
        
        return terms
    
    def _create_term_embeddings(self) -> Dict[str, np.ndarray]:
        """Create embeddings for all legal terms."""
        embeddings = {}
        
        for term_key, term_obj in self.terms.items():
            # Combine term, definition, and examples for embedding
            text = f"{term_obj.term} {term_obj.definition} {' '.join(term_obj.examples)}"
            embedding = self.model.encode([text])[0]
            embeddings[term_key] = embedding
        
        return embeddings
    
    def _create_term_index(self) -> Dict[str, Set[str]]:
        """Create index for fast term lookup."""
        index = {}
        
        for term_key, term_obj in self.terms.items():
            # Index by term itself
            words = term_obj.term.lower().split()
            for word in words:
                if word not in index:
                    index[word] = set()
                index[word].add(term_key)
            
            # Index by synonyms
            for synonym in term_obj.synonyms:
                syn_words = synonym.lower().split()
                for word in syn_words:
                    if word not in index:
                        index[word] = set()
                    index[word].add(term_key)
        
        return index
    
    async def get_relevant_terms(
        self, 
        query: str, 
        domain: Optional[LegalDomain] = None,
        max_terms: int = 10
    ) -> List[Dict[str, Any]]:
        """Get relevant legal terms for a query."""
        
        # Step 1: Find terms mentioned in query
        mentioned_terms = self._find_mentioned_terms(query)
        
        # Step 2: Find semantically similar terms
        similar_terms = self._find_similar_terms(query, max_terms * 2)
        
        # Step 3: Combine and rank terms
        all_candidates = set(mentioned_terms + similar_terms)
        
        # Filter by domain if specified
        if domain:
            all_candidates = {
                term for term in all_candidates 
                if self.terms[term].domain == domain
            }
        
        # Rank terms by relevance
        ranked_terms = self._rank_terms(query, list(all_candidates))
        
        # Format results
        results = []
        for term_key in ranked_terms[:max_terms]:
            term_obj = self.terms[term_key]
            results.append({
                "term": term_obj.term,
                "definition": term_obj.definition,
                "domain": term_obj.domain.value,
                "complexity": term_obj.complexity,
                "examples": term_obj.examples[:2],  # Limit examples
                "related_terms": term_obj.related_terms[:3],  # Limit related terms
                "common_usage": term_obj.common_usage,
                "professional_usage": term_obj.professional_usage
            })
        
        logger.debug(f"Found {len(results)} relevant terms for query")
        return results
    
    def _find_mentioned_terms(self, query: str) -> List[str]:
        """Find legal terms explicitly mentioned in the query."""
        mentioned = []
        query_lower = query.lower()
        
        # Check for exact term matches
        for term_key, term_obj in self.terms.items():
            if term_obj.term.lower() in query_lower:
                mentioned.append(term_key)
                continue
            
            # Check synonyms
            for synonym in term_obj.synonyms:
                if synonym.lower() in query_lower:
                    mentioned.append(term_key)
                    break
        
        return mentioned
    
    def _find_similar_terms(self, query: str, max_terms: int) -> List[str]:
        """Find terms semantically similar to the query."""
        query_embedding = self.model.encode([query])[0]
        
        similarities = []
        for term_key, term_embedding in self.term_embeddings.items():
            similarity = cosine_similarity([query_embedding], [term_embedding])[0][0]
            similarities.append((term_key, similarity))
        
        # Sort by similarity and return top terms
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [term for term, _ in similarities[:max_terms]]
    
    def _rank_terms(self, query: str, term_candidates: List[str]) -> List[str]:
        """Rank terms by relevance to query."""
        scored_terms = []
        query_lower = query.lower()
        
        for term_key in term_candidates:
            term_obj = self.terms[term_key]
            score = 0
            
            # Exact mention gets highest score
            if term_obj.term.lower() in query_lower:
                score += 10
            
            # Synonym mention
            for synonym in term_obj.synonyms:
                if synonym.lower() in query_lower:
                    score += 8
                    break
            
            # Related term mention
            for related in term_obj.related_terms:
                if related.lower() in query_lower:
                    score += 3
            
            # Complexity preference (basic terms get slight boost)
            if term_obj.complexity == "basic":
                score += 1
            
            scored_terms.append((term_key, score))
        
        # Sort by score
        scored_terms.sort(key=lambda x: x[1], reverse=True)
        return [term for term, _ in scored_terms]
    
    def get_term_definition(self, term: str, user_type: str = "common") -> Optional[Dict[str, Any]]:
        """Get definition for a specific term."""
        term_key = term.lower()
        
        if term_key not in self.terms:
            # Try to find by synonym
            for key, term_obj in self.terms.items():
                if term.lower() in [syn.lower() for syn in term_obj.synonyms]:
                    term_key = key
                    break
            else:
                return None
        
        term_obj = self.terms[term_key]
        
        # Choose appropriate definition based on user type
        if user_type == "professional":
            definition = term_obj.professional_usage
        else:
            definition = term_obj.common_usage
        
        return {
            "term": term_obj.term,
            "definition": definition,
            "detailed_definition": term_obj.definition,
            "domain": term_obj.domain.value,
            "complexity": term_obj.complexity,
            "examples": term_obj.examples,
            "related_terms": term_obj.related_terms,
            "synonyms": term_obj.synonyms,
            "see_also": term_obj.see_also
        }
    
    def search_terms(self, search_query: str, domain: Optional[LegalDomain] = None) -> List[Dict[str, Any]]:
        """Search for terms matching a query."""
        results = []
        search_lower = search_query.lower()
        
        for term_key, term_obj in self.terms.items():
            # Skip if domain filter doesn't match
            if domain and term_obj.domain != domain:
                continue
            
            # Check if search query matches term, definition, or examples
            if (search_lower in term_obj.term.lower() or
                search_lower in term_obj.definition.lower() or
                any(search_lower in example.lower() for example in term_obj.examples)):
                
                results.append({
                    "term": term_obj.term,
                    "definition": term_obj.common_usage,
                    "domain": term_obj.domain.value,
                    "complexity": term_obj.complexity
                })
        
        return results[:20]  # Limit results
    
    def get_domain_terms(self, domain: LegalDomain) -> List[Dict[str, Any]]:
        """Get all terms for a specific legal domain."""
        domain_terms = []
        
        for term_obj in self.terms.values():
            if term_obj.domain == domain:
                domain_terms.append({
                    "term": term_obj.term,
                    "definition": term_obj.common_usage,
                    "complexity": term_obj.complexity
                })
        
        # Sort by complexity (basic first)
        complexity_order = {"basic": 0, "intermediate": 1, "advanced": 2}
        domain_terms.sort(key=lambda x: complexity_order.get(x["complexity"], 3))
        
        return domain_terms
