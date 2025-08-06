"""Advanced Case Law Analysis and Legal Precedent Engine."""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from loguru import logger

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..core.config import settings
from ..core.state import LegalDomain


class CaseLawAnalyzer:
    """Advanced case law analysis and legal precedent engine."""
    
    def __init__(self):
        """Initialize the case law analyzer."""
        self.client = None
        self.case_database = self._load_comprehensive_case_database()
        self.legal_principles = self._load_legal_principles()
        
        if OPENAI_AVAILABLE and settings.openai_api_key:
            try:
                self.client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("✅ Case Law Analyzer initialized with AI")
            except Exception as e:
                logger.warning(f"Case Law Analyzer AI init failed: {e}")
    
    def _load_comprehensive_case_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load comprehensive case law database."""
        return {
            "family_law": [
                {
                    "case": "Troxel v. Granville (2000)",
                    "citation": "530 U.S. 57",
                    "court": "U.S. Supreme Court",
                    "principle": "Fundamental right of parents to make decisions concerning care, custody, and control of their children",
                    "facts": "Grandparents sought visitation rights over parental objection",
                    "holding": "State cannot infringe on fundamental right of parents without compelling state interest",
                    "application": ["Third-party custody", "Grandparent rights", "Parental autonomy"],
                    "keywords": ["parental rights", "visitation", "due process", "fundamental rights"]
                },
                {
                    "case": "Turner v. Rogers (2011)",
                    "citation": "564 U.S. 431",
                    "court": "U.S. Supreme Court", 
                    "principle": "Due process requirements in civil contempt proceedings for child support",
                    "facts": "Father jailed for contempt for failure to pay child support without counsel",
                    "holding": "Due process does not always require counsel in civil contempt proceedings",
                    "application": ["Child support enforcement", "Contempt proceedings", "Right to counsel"],
                    "keywords": ["child support", "contempt", "due process", "counsel"]
                },
                {
                    "case": "Loving v. Virginia (1967)",
                    "citation": "388 U.S. 1",
                    "court": "U.S. Supreme Court",
                    "principle": "Marriage is a fundamental civil right",
                    "facts": "Interracial couple challenged Virginia's Racial Integrity Act",
                    "holding": "Marriage is fundamental liberty interest subject to strict scrutiny",
                    "application": ["Marriage rights", "Equal protection", "Due process"],
                    "keywords": ["marriage", "fundamental rights", "equal protection", "due process"]
                }
            ],
            "criminal_law": [
                {
                    "case": "Miranda v. Arizona (1966)",
                    "citation": "384 U.S. 436",
                    "court": "U.S. Supreme Court",
                    "principle": "Fifth Amendment protection against self-incrimination requires warnings",
                    "facts": "Suspect interrogated without being informed of constitutional rights",
                    "holding": "Custodial interrogation requires Miranda warnings",
                    "application": ["Custodial interrogation", "Self-incrimination", "Right to counsel"],
                    "keywords": ["miranda", "interrogation", "self-incrimination", "counsel"]
                },
                {
                    "case": "Gideon v. Wainwright (1963)",
                    "citation": "372 U.S. 335",
                    "court": "U.S. Supreme Court",
                    "principle": "Sixth Amendment right to counsel in felony cases",
                    "facts": "Defendant charged with felony, denied counsel due to indigence",
                    "holding": "States must provide counsel to indigent defendants in felony cases",
                    "application": ["Right to counsel", "Indigent defense", "Felony prosecution"],
                    "keywords": ["counsel", "indigent", "felony", "sixth amendment"]
                },
                {
                    "case": "Terry v. Ohio (1968)",
                    "citation": "392 U.S. 1",
                    "court": "U.S. Supreme Court",
                    "principle": "Police may conduct limited search based on reasonable suspicion",
                    "facts": "Officer observed suspicious behavior and conducted pat-down search",
                    "holding": "Stop and frisk permitted with reasonable suspicion of criminal activity",
                    "application": ["Stop and frisk", "Reasonable suspicion", "Fourth Amendment"],
                    "keywords": ["terry stop", "reasonable suspicion", "search", "fourth amendment"]
                }
            ],
            "contract_law": [
                {
                    "case": "Hadley v. Baxendale (1854)",
                    "citation": "9 Ex. 341",
                    "court": "English Court of Exchequer",
                    "principle": "Contract damages limited to foreseeable consequences",
                    "facts": "Mill owner sued carrier for lost profits due to delayed delivery",
                    "holding": "Damages must be reasonably foreseeable at time of contract formation",
                    "application": ["Contract damages", "Foreseeability", "Consequential damages"],
                    "keywords": ["damages", "foreseeability", "consequential", "breach"]
                },
                {
                    "case": "Carlill v. Carbolic Smoke Ball Co. (1893)",
                    "citation": "1 Q.B. 256",
                    "court": "English Court of Appeal",
                    "principle": "Unilateral contracts can be formed through performance",
                    "facts": "Company offered reward for using product, customer performed and sued",
                    "holding": "Advertisement constituted valid offer accepted by performance",
                    "application": ["Unilateral contracts", "Offer and acceptance", "Consideration"],
                    "keywords": ["unilateral", "offer", "acceptance", "consideration"]
                }
            ],
            "property_law": [
                {
                    "case": "Kelo v. City of New London (2005)",
                    "citation": "545 U.S. 469",
                    "court": "U.S. Supreme Court",
                    "principle": "Economic development can constitute public use for eminent domain",
                    "facts": "City condemned private property for economic development project",
                    "holding": "Economic development satisfies public use requirement",
                    "application": ["Eminent domain", "Public use", "Economic development"],
                    "keywords": ["eminent domain", "public use", "takings", "economic development"]
                },
                {
                    "case": "Penn Central Transportation Co. v. New York City (1978)",
                    "citation": "438 U.S. 104",
                    "court": "U.S. Supreme Court",
                    "principle": "Regulatory takings analysis requires balancing test",
                    "facts": "Historic preservation law prevented development of Grand Central Terminal",
                    "holding": "Regulatory restrictions do not always constitute takings",
                    "application": ["Regulatory takings", "Historic preservation", "Property rights"],
                    "keywords": ["regulatory taking", "historic preservation", "property rights"]
                }
            ],
            "employment_law": [
                {
                    "case": "McDonnell Douglas Corp. v. Green (1973)",
                    "citation": "411 U.S. 792",
                    "court": "U.S. Supreme Court",
                    "principle": "Burden-shifting framework for employment discrimination",
                    "facts": "Employee alleged racial discrimination in hiring practices",
                    "holding": "Established prima facie case framework for discrimination claims",
                    "application": ["Employment discrimination", "Burden of proof", "Prima facie case"],
                    "keywords": ["discrimination", "burden shifting", "prima facie", "employment"]
                },
                {
                    "case": "Griggs v. Duke Power Co. (1971)",
                    "citation": "401 U.S. 424",
                    "court": "U.S. Supreme Court",
                    "principle": "Employment practices with disparate impact require business justification",
                    "facts": "Company required high school diploma and test scores for promotion",
                    "holding": "Practices with discriminatory effect must be job-related",
                    "application": ["Disparate impact", "Employment testing", "Business necessity"],
                    "keywords": ["disparate impact", "business necessity", "employment testing"]
                }
            ]
        }
    
    def _load_legal_principles(self) -> Dict[str, List[str]]:
        """Load fundamental legal principles by domain."""
        return {
            "family_law": [
                "Best interests of the child standard",
                "Parental rights are fundamental",
                "Marriage is a fundamental right",
                "Equal protection in family relationships"
            ],
            "criminal_law": [
                "Presumption of innocence",
                "Burden of proof beyond reasonable doubt",
                "Right to counsel",
                "Protection against self-incrimination",
                "Due process requirements"
            ],
            "contract_law": [
                "Freedom of contract",
                "Mutual assent requirement",
                "Consideration doctrine",
                "Good faith and fair dealing",
                "Foreseeability of damages"
            ],
            "property_law": [
                "Bundle of rights theory",
                "Public use requirement for takings",
                "Quiet enjoyment",
                "Landlord-tenant relationship duties"
            ],
            "employment_law": [
                "At-will employment presumption",
                "Equal opportunity principles",
                "Workplace safety requirements",
                "Collective bargaining rights"
            ]
        }
    
    async def find_relevant_cases(
        self,
        query: str,
        domain: LegalDomain,
        max_cases: int = 5
    ) -> List[Dict[str, Any]]:
        """Find most relevant cases for a legal query."""
        
        domain_cases = self.case_database.get(domain.value, [])
        if not domain_cases:
            return []
        
        # Score cases based on keyword matching and relevance
        scored_cases = []
        query_lower = query.lower()
        
        for case in domain_cases:
            score = 0
            
            # Check keywords
            for keyword in case.get("keywords", []):
                if keyword.lower() in query_lower:
                    score += 3
            
            # Check application areas
            for app in case.get("application", []):
                if any(word in query_lower for word in app.lower().split()):
                    score += 2
            
            # Check principle relevance
            principle_words = case.get("principle", "").lower().split()
            for word in principle_words:
                if len(word) > 3 and word in query_lower:
                    score += 1
            
            if score > 0:
                case_with_score = case.copy()
                case_with_score["relevance_score"] = score
                scored_cases.append(case_with_score)
        
        # Sort by relevance and return top cases
        scored_cases.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_cases[:max_cases]
    
    async def analyze_legal_precedents(
        self,
        query: str,
        domain: LegalDomain,
        relevant_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze how legal precedents apply to the query."""
        
        if not relevant_cases:
            return {
                "precedent_analysis": "No directly relevant precedents found.",
                "applicable_principles": self.legal_principles.get(domain.value, []),
                "case_citations": []
            }
        
        # Extract key information from relevant cases
        case_citations = []
        applicable_principles = []
        
        for case in relevant_cases:
            case_citations.append({
                "case": case["case"],
                "citation": case.get("citation", ""),
                "principle": case["principle"],
                "relevance": case.get("relevance_score", 0)
            })
            
            if case["principle"] not in applicable_principles:
                applicable_principles.append(case["principle"])
        
        # Generate precedent analysis
        if self.client and settings.case_law_analysis:
            analysis = await self._ai_precedent_analysis(query, relevant_cases)
        else:
            analysis = self._basic_precedent_analysis(query, relevant_cases)
        
        return {
            "precedent_analysis": analysis,
            "applicable_principles": applicable_principles,
            "case_citations": case_citations,
            "domain_principles": self.legal_principles.get(domain.value, [])
        }
    
    async def _ai_precedent_analysis(
        self,
        query: str,
        relevant_cases: List[Dict[str, Any]]
    ) -> str:
        """Use AI to analyze how precedents apply to the query."""
        
        try:
            case_summaries = "\n".join([
                f"- {case['case']}: {case['principle']} (Facts: {case.get('facts', 'N/A')})"
                for case in relevant_cases[:3]
            ])
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a legal expert analyzing case law precedents. Explain how the precedents apply to the user's situation."
                },
                {
                    "role": "user",
                    "content": f"""
                    User Query: {query}
                    
                    Relevant Precedents:
                    {case_summaries}
                    
                    Please analyze how these precedents apply to the user's situation. 
                    Explain the legal principles and their practical implications.
                    """
                }
            ]
            
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI precedent analysis failed: {e}")
            return self._basic_precedent_analysis(query, relevant_cases)
    
    def _basic_precedent_analysis(
        self,
        query: str,
        relevant_cases: List[Dict[str, Any]]
    ) -> str:
        """Basic precedent analysis without AI."""
        
        if not relevant_cases:
            return "No directly applicable precedents found for this query."
        
        top_case = relevant_cases[0]
        analysis = f"The most relevant precedent is {top_case['case']}, which established that {top_case['principle']}. "
        
        if len(relevant_cases) > 1:
            analysis += f"Additional relevant cases include {', '.join([case['case'] for case in relevant_cases[1:3]])}. "
        
        analysis += "These precedents suggest that courts will consider similar legal principles when evaluating your situation."
        
        return analysis
