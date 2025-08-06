"""
Dynamic Glossary and Process Engine
==================================

This module provides dynamic legal jargon detection, glossary management,
and court-specific process explanations for enhanced user understanding.

Features:
- Dynamic legal jargon detection using NER and keyword spotting
- Modular glossary system with external JSON storage
- Court-specific process explanations (civil, criminal, consumer)
- Automatic term extraction from legal documents
- Context-aware definitions

Author: Legal Agent Team
Version: 5.0.0 - Dynamic Glossary Engine
Date: 2025-07-22
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from pathlib import Path
import logging
from collections import defaultdict, Counter

# Try to import spaCy, make it optional
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GlossaryTerm:
    """Enhanced glossary term with context"""
    term: str
    definition: str
    category: str
    context: List[str]
    synonyms: List[str]
    related_terms: List[str]
    complexity_level: int  # 1-5 scale
    usage_frequency: int = 0


@dataclass
class ProcessStep:
    """Enhanced process step with court-specific details"""
    step_number: int
    title: str
    description: str
    court_type: str
    estimated_duration: str
    required_documents: List[str]
    cost_estimate: Optional[str] = None
    tips: List[str] = None


class DynamicGlossaryEngine:
    """Dynamic glossary engine with NER and context-aware definitions"""
    
    def __init__(self, 
                 glossary_file: str = "dynamic_glossary.json",
                 process_file: str = "court_processes.json"):
        """Initialize dynamic glossary engine"""
        
        self.glossary_file = glossary_file
        self.process_file = process_file
        
        # Load or initialize NLP model
        self.nlp = self.load_nlp_model()
        
        # Load glossary and processes
        self.glossary_terms = self.load_or_create_glossary()
        self.court_processes = self.load_or_create_processes()
        
        # Legal jargon patterns
        self.legal_patterns = self.compile_legal_patterns()
        
        # Term extraction cache
        self.extraction_cache = {}
        
        logger.info(f"Dynamic glossary engine initialized with {len(self.glossary_terms)} terms")
    
    def load_nlp_model(self):
        """Load spaCy NLP model for NER"""

        if not SPACY_AVAILABLE:
            logger.info("spaCy not available. Using basic pattern matching.")
            return None

        try:
            # Try to load English model
            nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy English model for NER")
            return nlp
        except (OSError, ImportError):
            logger.warning("spaCy English model not found. Using basic pattern matching.")
            return None
    
    def load_or_create_glossary(self) -> Dict[str, GlossaryTerm]:
        """Load existing glossary or create comprehensive one"""
        
        if Path(self.glossary_file).exists():
            try:
                with open(self.glossary_file, 'r', encoding='utf-8') as f:
                    glossary_data = json.load(f)
                
                # Convert to GlossaryTerm objects
                glossary_terms = {}
                for term_data in glossary_data:
                    term = GlossaryTerm(**term_data)
                    glossary_terms[term.term.lower()] = term
                
                logger.info(f"Loaded {len(glossary_terms)} glossary terms")
                return glossary_terms
                
            except Exception as e:
                logger.warning(f"Error loading glossary: {e}")
        
        # Create comprehensive glossary
        glossary_terms = self._create_comprehensive_glossary()

        # Set the attribute before saving
        self.glossary_terms = glossary_terms
        self.save_glossary()
        return glossary_terms
    
    def _create_comprehensive_glossary(self) -> Dict[str, GlossaryTerm]:
        """Create comprehensive legal glossary"""
        
        terms_data = [
            # Basic Legal Terms
            {
                "term": "Affidavit",
                "definition": "A written statement confirmed by oath or affirmation, for use as evidence in court",
                "category": "legal_document",
                "context": ["court_filing", "evidence", "sworn_statement"],
                "synonyms": ["sworn statement", "declaration"],
                "related_terms": ["oath", "testimony", "evidence"],
                "complexity_level": 3
            },
            {
                "term": "Plaintiff",
                "definition": "The person who brings a case against another in a court of law",
                "category": "court_party",
                "context": ["civil_case", "lawsuit", "litigation"],
                "synonyms": ["complainant", "petitioner"],
                "related_terms": ["defendant", "lawsuit", "civil_case"],
                "complexity_level": 2
            },
            {
                "term": "Defendant",
                "definition": "An individual, company, or institution sued or accused in a court of law",
                "category": "court_party",
                "context": ["civil_case", "criminal_case", "lawsuit"],
                "synonyms": ["respondent", "accused"],
                "related_terms": ["plaintiff", "lawsuit", "charges"],
                "complexity_level": 2
            },
            
            # Tenant Rights Terms
            {
                "term": "Security Deposit",
                "definition": "Money paid by a tenant to a landlord to cover potential damages or unpaid rent",
                "category": "tenant_rights",
                "context": ["rental_agreement", "lease", "housing"],
                "synonyms": ["damage deposit", "rental deposit"],
                "related_terms": ["lease", "landlord", "tenant"],
                "complexity_level": 1
            },
            {
                "term": "Eviction Notice",
                "definition": "Legal notice given by landlord to tenant to vacate the rental property",
                "category": "tenant_rights",
                "context": ["housing", "rental_termination", "landlord_tenant"],
                "synonyms": ["notice to quit", "termination notice"],
                "related_terms": ["eviction", "landlord", "lease_termination"],
                "complexity_level": 2
            },
            
            # Consumer Law Terms
            {
                "term": "Warranty",
                "definition": "A written guarantee promising to repair or replace a product if necessary within a specified period",
                "category": "consumer_law",
                "context": ["product_purchase", "consumer_protection", "defective_goods"],
                "synonyms": ["guarantee", "assurance"],
                "related_terms": ["consumer_rights", "defective_product", "refund"],
                "complexity_level": 1
            },
            {
                "term": "Consumer Forum",
                "definition": "Quasi-judicial body established to resolve consumer disputes quickly and inexpensively",
                "category": "consumer_law",
                "context": ["consumer_complaint", "dispute_resolution", "consumer_protection"],
                "synonyms": ["consumer court", "consumer commission"],
                "related_terms": ["consumer_rights", "complaint", "redressal"],
                "complexity_level": 3
            },
            
            # Family Law Terms
            {
                "term": "Alimony",
                "definition": "Financial support paid by one spouse to another after separation or divorce",
                "category": "family_law",
                "context": ["divorce", "separation", "spousal_support"],
                "synonyms": ["spousal support", "maintenance"],
                "related_terms": ["divorce", "child_support", "separation"],
                "complexity_level": 2
            },
            {
                "term": "Custody",
                "definition": "The legal right to care for and make decisions about a child",
                "category": "family_law",
                "context": ["child_custody", "divorce", "parental_rights"],
                "synonyms": ["guardianship", "parental_custody"],
                "related_terms": ["visitation", "child_support", "parental_rights"],
                "complexity_level": 2
            },
            
            # Employment Law Terms
            {
                "term": "Wrongful Termination",
                "definition": "Illegal dismissal of an employee in violation of employment laws or contracts",
                "category": "employment_law",
                "context": ["employment", "job_termination", "workplace_rights"],
                "synonyms": ["unlawful dismissal", "illegal firing"],
                "related_terms": ["employment_contract", "severance", "labor_rights"],
                "complexity_level": 3
            },
            {
                "term": "Sexual Harassment",
                "definition": "Unwelcome sexual advances, requests for sexual favors, or other verbal/physical conduct of sexual nature",
                "category": "employment_law",
                "context": ["workplace", "discrimination", "employee_rights"],
                "synonyms": ["workplace harassment", "sexual misconduct"],
                "related_terms": ["discrimination", "hostile_work_environment", "POSH_Act"],
                "complexity_level": 2
            },
            
            # Criminal Law Terms
            {
                "term": "Bail",
                "definition": "Money or property given as security to ensure an accused person returns for trial",
                "category": "criminal_law",
                "context": ["arrest", "criminal_case", "court_proceedings"],
                "synonyms": ["bond", "surety"],
                "related_terms": ["arrest", "custody", "trial"],
                "complexity_level": 2
            },
            {
                "term": "FIR",
                "definition": "First Information Report - initial complaint filed with police about a cognizable offense",
                "category": "criminal_law",
                "context": ["police_complaint", "criminal_case", "investigation"],
                "synonyms": ["First Information Report", "police_complaint"],
                "related_terms": ["police", "investigation", "criminal_case"],
                "complexity_level": 2
            },
            
            # Contract Law Terms
            {
                "term": "Breach of Contract",
                "definition": "Failure to perform any duty or obligation specified in a contract",
                "category": "contract_law",
                "context": ["contract_dispute", "business_agreement", "legal_obligation"],
                "synonyms": ["contract_violation", "default"],
                "related_terms": ["contract", "damages", "remedy"],
                "complexity_level": 3
            },
            
            # Constitutional Law Terms
            {
                "term": "Fundamental Rights",
                "definition": "Basic human rights guaranteed by the Constitution that cannot be taken away",
                "category": "constitutional_law",
                "context": ["constitution", "civil_rights", "legal_protection"],
                "synonyms": ["constitutional_rights", "basic_rights"],
                "related_terms": ["constitution", "civil_liberties", "legal_protection"],
                "complexity_level": 3
            },
            
            # Cyber Crime Terms
            {
                "term": "Identity Theft",
                "definition": "Fraudulent acquisition and use of someone's personal information for financial gain",
                "category": "cyber_crime",
                "context": ["online_fraud", "cybercrime", "personal_data"],
                "synonyms": ["identity_fraud", "personal_data_theft"],
                "related_terms": ["cybercrime", "fraud", "personal_data"],
                "complexity_level": 2
            }
        ]
        
        # Convert to GlossaryTerm objects
        glossary_terms = {}
        for term_data in terms_data:
            term = GlossaryTerm(**term_data)
            glossary_terms[term.term.lower()] = term
        
        return glossary_terms
    
    def save_glossary(self):
        """Save glossary to JSON file"""
        
        try:
            # Convert GlossaryTerm objects to dictionaries
            glossary_data = []
            for term in self.glossary_terms.values():
                glossary_data.append({
                    "term": term.term,
                    "definition": term.definition,
                    "category": term.category,
                    "context": term.context,
                    "synonyms": term.synonyms,
                    "related_terms": term.related_terms,
                    "complexity_level": term.complexity_level,
                    "usage_frequency": term.usage_frequency
                })
            
            with open(self.glossary_file, 'w', encoding='utf-8') as f:
                json.dump(glossary_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(glossary_data)} glossary terms")
            
        except Exception as e:
            logger.error(f"Error saving glossary: {e}")
    
    def load_or_create_processes(self) -> Dict[str, List[ProcessStep]]:
        """Load court-specific processes"""
        
        if Path(self.process_file).exists():
            try:
                with open(self.process_file, 'r', encoding='utf-8') as f:
                    process_data = json.load(f)
                
                # Convert to ProcessStep objects
                court_processes = {}
                for court_type, steps_data in process_data.items():
                    steps = []
                    for step_data in steps_data:
                        step = ProcessStep(**step_data)
                        steps.append(step)
                    court_processes[court_type] = steps
                
                logger.info(f"Loaded processes for {len(court_processes)} court types")
                return court_processes
                
            except Exception as e:
                logger.warning(f"Error loading processes: {e}")
        
        # Create court processes
        court_processes = self._create_court_processes()

        # Set the attribute before saving
        self.court_processes = court_processes
        self.save_processes()
        return court_processes
    
    def _create_court_processes(self) -> Dict[str, List[ProcessStep]]:
        """Create court-specific process explanations"""
        
        processes = {
            "civil_court": [
                ProcessStep(
                    step_number=1,
                    title="File Complaint/Petition",
                    description="Submit formal complaint with court registry along with required documents and fees",
                    court_type="civil_court",
                    estimated_duration="1-2 days",
                    required_documents=["complaint", "affidavit", "supporting_documents"],
                    cost_estimate="₹5,000-₹15,000",
                    tips=["Ensure all documents are properly notarized", "Keep multiple copies"]
                ),
                ProcessStep(
                    step_number=2,
                    title="Service of Summons",
                    description="Court issues summons to defendant, who must respond within specified time",
                    court_type="civil_court",
                    estimated_duration="15-30 days",
                    required_documents=["summons", "copy_of_complaint"],
                    tips=["Ensure proper service address", "Track service status"]
                ),
                ProcessStep(
                    step_number=3,
                    title="Written Statement/Defense",
                    description="Defendant files written statement responding to allegations",
                    court_type="civil_court",
                    estimated_duration="30 days from service",
                    required_documents=["written_statement", "counter_affidavit"],
                    tips=["File within time limit", "Address all allegations"]
                ),
                ProcessStep(
                    step_number=4,
                    title="Evidence and Arguments",
                    description="Both parties present evidence and legal arguments before the court",
                    court_type="civil_court",
                    estimated_duration="3-12 months",
                    required_documents=["evidence", "witness_statements", "expert_reports"],
                    tips=["Organize evidence systematically", "Prepare witness testimony"]
                ),
                ProcessStep(
                    step_number=5,
                    title="Judgment and Decree",
                    description="Court delivers judgment and issues decree for enforcement",
                    court_type="civil_court",
                    estimated_duration="1-2 months after arguments",
                    required_documents=["judgment_copy", "decree"],
                    tips=["Understand judgment implications", "Plan for enforcement if needed"]
                )
            ],
            
            "family_court": [
                ProcessStep(
                    step_number=1,
                    title="File Petition",
                    description="Submit family court petition with marriage certificate and supporting documents",
                    court_type="family_court",
                    estimated_duration="1-2 days",
                    required_documents=["petition", "marriage_certificate", "financial_documents"],
                    cost_estimate="₹3,000-₹10,000",
                    tips=["Include all relevant family details", "Attach financial disclosures"]
                ),
                ProcessStep(
                    step_number=2,
                    title="Mediation/Counseling",
                    description="Court-mandated mediation to explore reconciliation possibilities",
                    court_type="family_court",
                    estimated_duration="2-6 months",
                    required_documents=["mediation_report"],
                    tips=["Participate in good faith", "Consider family welfare"]
                ),
                ProcessStep(
                    step_number=3,
                    title="Evidence Recording",
                    description="Recording of evidence including financial records and custody evaluations",
                    court_type="family_court",
                    estimated_duration="6-12 months",
                    required_documents=["financial_records", "custody_evaluation", "character_references"],
                    tips=["Maintain detailed financial records", "Focus on child welfare"]
                )
            ],
            
            "consumer_forum": [
                ProcessStep(
                    step_number=1,
                    title="File Consumer Complaint",
                    description="Submit complaint with consumer forum along with purchase proof and defect evidence",
                    court_type="consumer_forum",
                    estimated_duration="1 day",
                    required_documents=["complaint", "purchase_receipt", "warranty_card", "defect_evidence"],
                    cost_estimate="₹1,000-₹5,000",
                    tips=["Include all purchase details", "Document defects with photos"]
                ),
                ProcessStep(
                    step_number=2,
                    title="Notice to Opposite Party",
                    description="Forum issues notice to company/service provider to respond",
                    court_type="consumer_forum",
                    estimated_duration="15-30 days",
                    required_documents=["notice", "complaint_copy"],
                    tips=["Ensure correct company address", "Track notice delivery"]
                ),
                ProcessStep(
                    step_number=3,
                    title="Hearing and Evidence",
                    description="Both parties present their case with evidence and arguments",
                    court_type="consumer_forum",
                    estimated_duration="3-6 months",
                    required_documents=["evidence", "expert_reports", "witness_statements"],
                    tips=["Bring original documents", "Prepare clear arguments"]
                )
            ],
            
            "labor_court": [
                ProcessStep(
                    step_number=1,
                    title="File Labor Complaint",
                    description="Submit complaint with labor court or tribunal with employment records",
                    court_type="labor_court",
                    estimated_duration="1-2 days",
                    required_documents=["complaint", "employment_contract", "salary_records"],
                    cost_estimate="₹2,000-₹8,000",
                    tips=["Include complete employment history", "Document workplace incidents"]
                ),
                ProcessStep(
                    step_number=2,
                    title="Conciliation Process",
                    description="Mandatory conciliation attempt between employee and employer",
                    court_type="labor_court",
                    estimated_duration="1-3 months",
                    required_documents=["conciliation_report"],
                    tips=["Participate constructively", "Document all discussions"]
                ),
                ProcessStep(
                    step_number=3,
                    title="Tribunal Hearing",
                    description="Formal hearing before labor tribunal with evidence presentation",
                    court_type="labor_court",
                    estimated_duration="6-18 months",
                    required_documents=["evidence", "witness_statements", "employment_records"],
                    tips=["Organize employment documentation", "Prepare witness testimony"]
                )
            ]
        }
        
        return processes
    
    def save_processes(self):
        """Save court processes to JSON file"""
        
        try:
            # Convert ProcessStep objects to dictionaries
            process_data = {}
            for court_type, steps in self.court_processes.items():
                steps_data = []
                for step in steps:
                    step_dict = {
                        "step_number": step.step_number,
                        "title": step.title,
                        "description": step.description,
                        "court_type": step.court_type,
                        "estimated_duration": step.estimated_duration,
                        "required_documents": step.required_documents
                    }
                    if step.cost_estimate:
                        step_dict["cost_estimate"] = step.cost_estimate
                    if step.tips:
                        step_dict["tips"] = step.tips
                    
                    steps_data.append(step_dict)
                
                process_data[court_type] = steps_data
            
            with open(self.process_file, 'w', encoding='utf-8') as f:
                json.dump(process_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved processes for {len(process_data)} court types")
            
        except Exception as e:
            logger.error(f"Error saving processes: {e}")
    
    def compile_legal_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for legal jargon detection"""
        
        patterns = [
            # Legal document patterns
            re.compile(r'\b(?:affidavit|petition|complaint|summons|decree|judgment|order)\b', re.IGNORECASE),
            
            # Court-related patterns
            re.compile(r'\b(?:plaintiff|defendant|respondent|petitioner|appellant|appellee)\b', re.IGNORECASE),
            
            # Legal procedure patterns
            re.compile(r'\b(?:hearing|trial|litigation|arbitration|mediation|conciliation)\b', re.IGNORECASE),
            
            # Legal concepts patterns
            re.compile(r'\b(?:liability|damages|compensation|injunction|restraint|interim)\b', re.IGNORECASE),
            
            # Specific legal terms
            re.compile(r'\b(?:bail|custody|alimony|maintenance|eviction|foreclosure)\b', re.IGNORECASE)
        ]
        
        return patterns
    
    def detect_legal_jargon(self, text: str) -> Set[str]:
        """Detect legal jargon in text using NER and pattern matching"""
        
        detected_terms = set()
        text_lower = text.lower()
        
        # Method 1: Direct glossary term matching
        for term in self.glossary_terms.keys():
            if term in text_lower:
                detected_terms.add(term)
                # Update usage frequency
                self.glossary_terms[term].usage_frequency += 1
        
        # Method 2: Pattern-based detection
        for pattern in self.legal_patterns:
            matches = pattern.findall(text)
            for match in matches:
                match_lower = match.lower()
                if match_lower in self.glossary_terms:
                    detected_terms.add(match_lower)
        
        # Method 3: NER-based detection (if spaCy available)
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PERSON', 'LAW']:  # Legal entities
                    ent_lower = ent.text.lower()
                    if ent_lower in self.glossary_terms:
                        detected_terms.add(ent_lower)
        
        return detected_terms
    
    def get_contextual_definitions(self, terms: Set[str], domain: str) -> Dict[str, str]:
        """Get context-aware definitions for detected terms"""
        
        definitions = {}
        
        for term in terms:
            if term in self.glossary_terms:
                glossary_term = self.glossary_terms[term]
                
                # Check if term is relevant to current domain
                if domain in glossary_term.context or glossary_term.category == domain:
                    definitions[glossary_term.term] = glossary_term.definition
                else:
                    # Provide general definition
                    definitions[glossary_term.term] = glossary_term.definition
        
        return definitions
    
    def get_court_specific_process(self, domain: str, court_type: Optional[str] = None) -> List[ProcessStep]:
        """Get court-specific process steps for a legal domain"""
        
        # Map domains to court types
        domain_court_mapping = {
            "tenant_rights": "civil_court",
            "consumer_complaint": "consumer_forum",
            "family_law": "family_court",
            "employment_law": "labor_court",
            "contract_dispute": "civil_court",
            "personal_injury": "civil_court",
            "criminal_law": "criminal_court",
            "immigration_law": "immigration_court",
            "elder_abuse": "civil_court",
            "cyber_crime": "cyber_court"
        }
        
        # Determine court type
        if not court_type:
            court_type = domain_court_mapping.get(domain, "civil_court")
        
        # Get process steps
        if court_type in self.court_processes:
            return self.court_processes[court_type]
        else:
            # Return generic civil court process
            return self.court_processes.get("civil_court", [])
    
    def add_term(self, term: str, definition: str, category: str, context: List[str] = None):
        """Add new term to glossary"""
        
        new_term = GlossaryTerm(
            term=term,
            definition=definition,
            category=category,
            context=context or [],
            synonyms=[],
            related_terms=[],
            complexity_level=2,
            usage_frequency=0
        )
        
        self.glossary_terms[term.lower()] = new_term
        self.save_glossary()
        
        logger.info(f"Added new glossary term: {term}")
    
    def get_glossary_stats(self) -> Dict[str, Any]:
        """Get glossary statistics"""
        
        categories = defaultdict(int)
        complexity_distribution = defaultdict(int)
        total_usage = 0
        
        for term in self.glossary_terms.values():
            categories[term.category] += 1
            complexity_distribution[term.complexity_level] += 1
            total_usage += term.usage_frequency
        
        return {
            'total_terms': len(self.glossary_terms),
            'categories': dict(categories),
            'complexity_distribution': dict(complexity_distribution),
            'total_usage': total_usage,
            'court_processes': len(self.court_processes),
            'nlp_enabled': self.nlp is not None
        }


def create_dynamic_glossary_engine() -> DynamicGlossaryEngine:
    """Factory function to create dynamic glossary engine"""
    return DynamicGlossaryEngine()


# Test the glossary engine
if __name__ == "__main__":
    print("📚 DYNAMIC GLOSSARY ENGINE TEST")
    print("=" * 50)
    
    engine = create_dynamic_glossary_engine()
    
    # Test jargon detection
    test_text = "I need to file an affidavit for my custody case. The plaintiff wants alimony and the defendant filed a counter-petition."
    
    detected_terms = engine.detect_legal_jargon(test_text)
    definitions = engine.get_contextual_definitions(detected_terms, "family_law")
    
    print(f"🔍 Test Text: \"{test_text}\"")
    print(f"\n📋 Detected Legal Terms:")
    for term in detected_terms:
        print(f"   • {term.title()}")
    
    print(f"\n📚 Definitions:")
    for term, definition in definitions.items():
        print(f"   • {term}: {definition[:60]}...")
    
    # Test court processes
    print(f"\n⚖️ Family Court Process:")
    family_process = engine.get_court_specific_process("family_law")
    for step in family_process[:3]:
        print(f"   {step.step_number}. {step.title} ({step.estimated_duration})")
    
    # Get statistics
    stats = engine.get_glossary_stats()
    print(f"\n📊 Glossary Statistics:")
    print(f"   Total Terms: {stats['total_terms']}")
    print(f"   Categories: {len(stats['categories'])}")
    print(f"   Court Processes: {stats['court_processes']}")
    print(f"   NLP Enabled: {stats['nlp_enabled']}")
    
    print(f"\n✅ Dynamic glossary engine ready!")
    print(f"🎯 Context-aware legal jargon detection and court-specific processes")
