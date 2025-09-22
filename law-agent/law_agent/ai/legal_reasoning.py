"""Advanced AI Legal Reasoning Engine with OpenAI GPT integration."""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from loguru import logger

try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")

from ..core.config import settings
from ..core.state import LegalDomain, UserType


class LegalReasoningEngine:
    """Advanced AI-powered legal reasoning engine."""
    
    def __init__(self):
        """Initialize the legal reasoning engine."""
        self.client = None
        self.legal_prompts = self._load_legal_prompts()
        self.case_law_database = self._initialize_case_law_db()
        
        if OPENAI_AVAILABLE and settings.openai_api_key and settings.use_advanced_ai:
            try:
                self.client = AsyncOpenAI(api_key=settings.openai_api_key)
                logger.info("✅ OpenAI Legal Reasoning Engine initialized")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
                self.client = None
        else:
            logger.info("Using fallback legal reasoning (no OpenAI)")
    
    def _load_legal_prompts(self) -> Dict[str, str]:
        """Load specialized legal prompts for different domains."""
        return {
            "system_prompt": """You are an expert AI legal assistant with comprehensive knowledge of law. 
            You provide accurate, detailed legal guidance while being clear about limitations. 
            Always include relevant legal precedents, statutes, and practical next steps.
            Structure your responses with clear sections: Analysis, Legal Basis, Next Steps, and Warnings.""",
            
            "family_law": """You are a family law specialist. Focus on divorce, custody, alimony, 
            child support, adoption, and domestic relations. Consider emotional aspects while 
            providing practical legal guidance. Always mention mediation options and child welfare.""",
            
            "criminal_law": """You are a criminal law expert. Focus on constitutional rights, 
            criminal procedure, evidence, sentencing, and defense strategies. Always emphasize 
            the right to counsel and presumption of innocence.""",
            
            "contract_law": """You are a contracts specialist. Analyze contract formation, 
            performance, breach, and remedies. Focus on UCC, common law, and practical 
            business implications.""",
            
            "property_law": """You are a property law expert. Cover real estate, landlord-tenant, 
            zoning, easements, and property rights. Include practical steps for property disputes.""",
            
            "employment_law": """You are an employment law specialist. Focus on workplace rights, 
            discrimination, wrongful termination, wage issues, and labor relations. Include 
            federal and state law considerations."""
        }
    
    def _initialize_case_law_db(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize a basic case law database for legal precedents."""
        return {
            "family_law": [
                {
                    "case": "Troxel v. Granville (2000)",
                    "principle": "Parental rights are fundamental liberty interests",
                    "application": "Third-party custody and visitation rights"
                },
                {
                    "case": "Turner v. Rogers (2011)", 
                    "principle": "Due process in civil contempt proceedings",
                    "application": "Child support enforcement"
                }
            ],
            "criminal_law": [
                {
                    "case": "Miranda v. Arizona (1966)",
                    "principle": "Right to remain silent and right to counsel",
                    "application": "Custodial interrogation"
                },
                {
                    "case": "Gideon v. Wainwright (1963)",
                    "principle": "Right to counsel in felony cases",
                    "application": "Indigent defense"
                }
            ],
            "contract_law": [
                {
                    "case": "Hadley v. Baxendale (1854)",
                    "principle": "Foreseeability rule for contract damages",
                    "application": "Consequential damages"
                }
            ],
            "property_law": [
                {
                    "case": "Kelo v. City of New London (2005)",
                    "principle": "Eminent domain for economic development",
                    "application": "Public use requirement"
                }
            ],
            "employment_law": [
                {
                    "case": "McDonnell Douglas Corp. v. Green (1973)",
                    "principle": "Burden-shifting framework for discrimination",
                    "application": "Employment discrimination claims"
                }
            ]
        }
    
    async def analyze_legal_query(
        self,
        query: str,
        domain: LegalDomain,
        user_type: UserType,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive legal analysis of a query."""
        
        if self.client and settings.use_advanced_ai:
            return await self._ai_powered_analysis(query, domain, user_type, context)
        else:
            return await self._fallback_analysis(query, domain, user_type, context)
    
    async def _ai_powered_analysis(
        self,
        query: str,
        domain: LegalDomain,
        user_type: UserType,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Use OpenAI GPT for advanced legal analysis."""
        
        try:
            # Get domain-specific prompt
            domain_prompt = self.legal_prompts.get(domain.value, self.legal_prompts["system_prompt"])
            
            # Get relevant case law
            relevant_cases = self.case_law_database.get(domain.value, [])
            case_law_text = "\n".join([
                f"- {case['case']}: {case['principle']} (applies to {case['application']})"
                for case in relevant_cases[:3]  # Top 3 relevant cases
            ])
            
            # Construct comprehensive prompt
            messages = [
                {
                    "role": "system",
                    "content": f"{domain_prompt}\n\nRelevant Case Law:\n{case_law_text}"
                },
                {
                    "role": "user",
                    "content": f"""
                    Legal Query: {query}
                    
                    User Type: {user_type.value}
                    Legal Domain: {domain.value}
                    
                    Please provide a comprehensive legal analysis including:
                    1. Legal Analysis - detailed explanation of the legal issues
                    2. Applicable Law - relevant statutes, regulations, and case law
                    3. Practical Steps - specific actionable next steps
                    4. Potential Outcomes - likely scenarios and their implications
                    5. Warnings - important limitations and risks
                    6. Resources - where to get additional help
                    
                    Tailor the complexity and language to the user type.
                    """
                }
            ]
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=settings.legal_reasoning_model,
                messages=messages,
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse and structure the response
            structured_response = self._parse_ai_response(ai_response, domain, query)
            
            logger.info(f"✅ AI legal analysis completed for {domain.value} query")
            return structured_response
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return await self._fallback_analysis(query, domain, user_type, context)
    
    def _parse_ai_response(self, ai_response: str, domain: LegalDomain, query: str) -> Dict[str, Any]:
        """Parse AI response into structured format."""
        
        sections = {
            "analysis": "",
            "applicable_law": "",
            "next_steps": [],
            "outcomes": "",
            "warnings": "",
            "resources": []
        }
        
        # Try to extract sections using regex
        section_patterns = {
            "analysis": r"(?:Legal Analysis|Analysis)[:\-\s]*(.*?)(?=\n\d+\.|Applicable Law|$)",
            "applicable_law": r"(?:Applicable Law|Legal Basis)[:\-\s]*(.*?)(?=\n\d+\.|Practical Steps|$)",
            "next_steps": r"(?:Practical Steps|Next Steps)[:\-\s]*(.*?)(?=\n\d+\.|Potential Outcomes|$)",
            "outcomes": r"(?:Potential Outcomes|Outcomes)[:\-\s]*(.*?)(?=\n\d+\.|Warnings|$)",
            "warnings": r"(?:Warnings|Important)[:\-\s]*(.*?)(?=\n\d+\.|Resources|$)",
            "resources": r"(?:Resources|Additional Help)[:\-\s]*(.*?)(?=\n\d+\.|$)"
        }
        
        for section, pattern in section_patterns.items():
            match = re.search(pattern, ai_response, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if section in ["next_steps", "resources"]:
                    # Convert to list
                    items = [item.strip() for item in re.split(r'[-•\n]', content) if item.strip()]
                    sections[section] = items[:5]  # Limit to 5 items
                else:
                    sections[section] = content
        
        # If parsing failed, use the full response as analysis
        if not any(sections.values()):
            sections["analysis"] = ai_response
        
        return {
            "text": ai_response,
            "sections": sections,
            "confidence": 0.9,  # High confidence for AI responses
            "source": "ai_powered",
            "domain": domain.value,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _fallback_analysis(
        self,
        query: str,
        domain: LegalDomain,
        user_type: UserType,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Advanced legal analysis using comprehensive knowledge base."""

        # Get comprehensive legal guidance
        legal_guidance = self._get_comprehensive_legal_guidance(query, domain, user_type)

        return {
            "text": legal_guidance["full_response"],
            "sections": legal_guidance["sections"],
            "confidence": legal_guidance["confidence"],
            "source": "advanced_knowledge_base",
            "domain": domain.value,
            "timestamp": datetime.now().isoformat()
        }

    def _get_comprehensive_legal_guidance(self, query: str, domain: LegalDomain, user_type: UserType) -> Dict[str, Any]:
        """Generate comprehensive legal guidance based on domain and query analysis."""

        # Analyze query for specific legal issues
        query_lower = query.lower()
        legal_issues = self._identify_legal_issues(query_lower, domain)

        # Get domain-specific guidance
        guidance = self._get_domain_specific_guidance(domain, legal_issues, user_type)

        # Get relevant case law and statutes
        relevant_cases = self.case_law_database.get(domain.value, [])

        # Build comprehensive response
        sections = {
            "analysis": guidance["analysis"],
            "applicable_law": guidance["applicable_law"],
            "next_steps": guidance["next_steps"],
            "outcomes": guidance["potential_outcomes"],
            "warnings": guidance["warnings"],
            "resources": guidance["resources"]
        }

        # Create full response text
        full_response = self._format_comprehensive_response(sections, relevant_cases)

        return {
            "full_response": full_response,
            "sections": sections,
            "confidence": guidance["confidence"]
        }

    def _identify_legal_issues(self, query: str, domain: LegalDomain) -> List[str]:
        """Identify specific legal issues from the query."""

        issue_keywords = {
            "family_law": {
                "divorce": ["divorce", "separation", "marriage dissolution", "split up"],
                "custody": ["custody", "child custody", "visitation", "parenting time"],
                "alimony": ["alimony", "spousal support", "maintenance", "financial support"],
                "child_support": ["child support", "support payment", "child maintenance"],
                "adoption": ["adoption", "adopt", "legal guardian", "guardianship"],
                "domestic_violence": ["domestic violence", "abuse", "restraining order", "protection order"]
            },
            "criminal_law": {
                "arrest": ["arrested", "arrest", "police custody", "detained"],
                "charges": ["charged", "criminal charges", "accused", "prosecution"],
                "bail": ["bail", "bond", "release", "custody"],
                "trial": ["trial", "court", "hearing", "judge"],
                "sentencing": ["sentence", "punishment", "jail", "prison", "fine"],
                "appeal": ["appeal", "appellate", "higher court", "review"]
            },
            "employment_law": {
                "termination": ["fired", "terminated", "dismissed", "laid off"],
                "discrimination": ["discrimination", "harassment", "bias", "unfair treatment"],
                "wages": ["wages", "salary", "overtime", "payment", "unpaid"],
                "workplace_safety": ["safety", "injury", "accident", "hazard", "workers comp"],
                "contract": ["contract", "agreement", "terms", "employment terms"]
            },
            "property_law": {
                "purchase": ["buy", "purchase", "buying property", "real estate"],
                "sale": ["sell", "selling", "sale", "property sale"],
                "lease": ["lease", "rent", "rental", "tenant", "landlord"],
                "disputes": ["dispute", "boundary", "neighbor", "property line"],
                "title": ["title", "deed", "ownership", "property rights"]
            }
        }

        identified_issues = []
        domain_keywords = issue_keywords.get(domain.value, {})

        for issue, keywords in domain_keywords.items():
            if any(keyword in query for keyword in keywords):
                identified_issues.append(issue)

        return identified_issues if identified_issues else ["general"]

    def _classify_unknown_query(self, issues: List[str]) -> LegalDomain:
        """Try to classify unknown queries based on common legal keywords."""

        # Common legal keywords that indicate specific domains
        family_keywords = ["divorce", "marriage", "custody", "child", "spouse", "alimony", "separation"]
        criminal_keywords = ["arrest", "police", "crime", "criminal", "bail", "court", "charges"]
        employment_keywords = ["job", "work", "fired", "terminated", "salary", "employer", "workplace"]
        property_keywords = ["property", "house", "land", "rent", "lease", "tenant", "landlord"]

        # Check if any issues contain domain-specific keywords
        issue_text = " ".join(issues).lower()

        if any(keyword in issue_text for keyword in family_keywords):
            return LegalDomain.FAMILY_LAW
        elif any(keyword in issue_text for keyword in criminal_keywords):
            return LegalDomain.CRIMINAL_LAW
        elif any(keyword in issue_text for keyword in employment_keywords):
            return LegalDomain.EMPLOYMENT_LAW
        elif any(keyword in issue_text for keyword in property_keywords):
            return LegalDomain.PROPERTY_LAW

        # Default to family law for general legal queries
        return LegalDomain.FAMILY_LAW

    def _get_domain_specific_guidance(self, domain: LegalDomain, issues: List[str], user_type: UserType) -> Dict[str, Any]:
        """Get detailed guidance for specific legal domain and issues."""

        # Handle unknown domain by trying to classify based on keywords
        if domain == LegalDomain.UNKNOWN:
            domain = self._classify_unknown_query(issues)

        guidance_database = {
            "family_law": {
                "divorce": {
                    "analysis": "Divorce requires valid grounds like cruelty or desertion. File petition in family court, serve notice to spouse, attend hearings. Mutual consent is faster.",
                    "applicable_law": "Hindu Marriage Act 1955, Indian Divorce Act 1869",
                    "next_steps": [
                        "Collect marriage certificate and evidence",
                        "Consult family lawyer for strategy",
                        "File divorce petition in family court"
                    ],
                    "potential_outcomes": "Mutual consent: 6-18 months. Contested: 2-5 years.",
                    "warnings": "Consider counseling first. Affects children and finances.",
                    "resources": ["Family Court", "Legal Aid", "Counselors"]
                },
                "custody": {
                    "analysis": "Custody follows 'best interest of child' principle. Courts consider age, financial stability, character. Mothers typically get custody of children under 5.",
                    "applicable_law": "Hindu Minority and Guardianship Act 1956",
                    "next_steps": [
                        "File custody petition in family court",
                        "Gather financial stability evidence",
                        "Submit child's school/medical records"
                    ],
                    "potential_outcomes": "Court grants sole/joint custody or visitation rights.",
                    "warnings": "Child's welfare comes first. Keep detailed records.",
                    "resources": ["Family Court", "Child Welfare Committee", "Legal Aid"]
                }
            },
            "criminal_law": {
                "arrest": {
                    "analysis": """Arrest procedures in India are governed by CrPC. Police can arrest without warrant for cognizable offenses. You have fundamental rights during arrest including right to know grounds of arrest, right to legal representation, and right against self-incrimination.""",
                    "applicable_law": "Code of Criminal Procedure 1973 (Sections 41, 50, 57), Indian Constitution (Articles 20, 21, 22)",
                    "next_steps": [
                        "Remain calm and cooperate with police procedures",
                        "Ask for grounds of arrest in writing",
                        "Inform family member or friend about arrest",
                        "Request for legal representation immediately",
                        "Do not sign any document without lawyer present",
                        "Apply for bail at earliest opportunity"
                    ],
                    "potential_outcomes": "May be released on bail, remanded to judicial custody, or police custody. Case will proceed to trial if charges are framed.",
                    "warnings": "Anything you say can be used against you. Exercise right to remain silent until lawyer arrives.",
                    "resources": ["Legal Aid Services", "District Legal Services Authority", "Human Rights Commission", "Police Complaint Authority"]
                }
            },
            "employment_law": {
                "termination": {
                    "analysis": "Employment termination requires proper notice and due process. Wrongful termination without cause or notice may entitle you to compensation and reinstatement through labor courts.",
                    "applicable_law": "Industrial Disputes Act 1947, Contract Act 1872, Payment of Wages Act 1936",
                    "next_steps": [
                        "Review employment contract and company policies",
                        "Collect all employment documents and communications",
                        "File complaint with Labour Commissioner if applicable",
                        "Send legal notice demanding reinstatement/compensation",
                        "Approach Industrial Tribunal or Labour Court",
                        "Document financial losses due to termination"
                    ],
                    "potential_outcomes": "May get reinstatement, compensation for wrongful termination, or settlement. Process can take 1-3 years.",
                    "warnings": "Time limits apply for filing complaints. Maintain all employment records and communications.",
                    "resources": ["Labour Commissioner", "Industrial Tribunal", "Trade Unions", "Legal Aid Services"]
                }
            }
        }

        # Get guidance for the primary issue
        primary_issue = issues[0] if issues else "general"
        domain_guidance = guidance_database.get(domain.value, {})
        issue_guidance = domain_guidance.get(primary_issue, self._get_general_guidance(domain))

        # Adjust language complexity based on user type
        if user_type == UserType.COMMON_PERSON:
            issue_guidance = self._simplify_legal_language(issue_guidance)

        issue_guidance["confidence"] = 0.85  # High confidence for knowledge-based responses
        return issue_guidance

    def _get_general_guidance(self, domain: LegalDomain) -> Dict[str, Any]:
        """Provide general guidance when specific issue is not identified."""

        general_guidance = {
            "family_law": {
                "analysis": "Family law matters involve personal relationships and require careful consideration of emotional and legal aspects. Common issues include marriage, divorce, child custody, adoption, and domestic relations.",
                "applicable_law": "Hindu Marriage Act 1955, Muslim Personal Law, Indian Christian Marriage Act, Parsi Marriage and Divorce Act",
                "next_steps": ["Identify specific legal issue", "Gather relevant documents", "Consult family law specialist", "Consider mediation options"],
                "potential_outcomes": "Outcomes vary based on specific circumstances and applicable personal laws.",
                "warnings": "Family matters have long-term consequences. Consider all options before proceeding.",
                "resources": ["Family Court", "Mediation Centers", "Legal Aid Services", "Counseling Services"]
            },
            "criminal_law": {
                "analysis": "Criminal law involves offenses against the state. Understanding your rights and the legal process is crucial for proper defense or prosecution.",
                "applicable_law": "Indian Penal Code 1860, Code of Criminal Procedure 1973, Indian Evidence Act 1872",
                "next_steps": ["Understand the charges", "Secure legal representation", "Gather evidence", "Know your constitutional rights"],
                "potential_outcomes": "May result in acquittal, conviction, plea bargain, or case dismissal.",
                "warnings": "Criminal cases have serious consequences including imprisonment. Seek immediate legal help.",
                "resources": ["Criminal Courts", "Legal Aid Services", "Police", "Public Prosecutors"]
            },
            "employment_law": {
                "analysis": "Employment law governs the relationship between employers and employees, covering hiring, working conditions, termination, and workplace rights.",
                "applicable_law": "Industrial Disputes Act 1947, Factories Act 1948, Contract Labour Act 1970, various Labour Laws",
                "next_steps": ["Review employment contract", "Document workplace issues", "Approach HR department", "File complaint with labour authorities"],
                "potential_outcomes": "May result in reinstatement, compensation, settlement, or policy changes.",
                "warnings": "Employment disputes can affect career prospects. Document everything and follow proper procedures.",
                "resources": ["Labour Commissioner", "Industrial Tribunals", "Trade Unions", "HR Departments"]
            }
        }

        # Provide comprehensive general guidance for unknown domains
        default_guidance = {
            "analysis": "Legal matters require careful analysis of facts and applicable laws. Most legal issues can be resolved through proper legal procedures and professional guidance.",
            "applicable_law": "Indian Constitution, relevant statutes, and case law",
            "next_steps": [
                "Identify the specific legal issue",
                "Gather all relevant documents",
                "Consult with a qualified lawyer"
            ],
            "potential_outcomes": "Resolution depends on facts, evidence, and applicable law.",
            "warnings": "Seek professional legal advice for your specific situation.",
            "resources": ["Legal Aid Services", "Bar Association", "District Courts"]
        }

        return general_guidance.get(domain.value, default_guidance)

    def _simplify_legal_language(self, guidance: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify legal language for common persons."""

        # Simplification mappings
        simplifications = {
            "petition": "application",
            "jurisdiction": "authority",
            "cognizable": "serious",
            "non-cognizable": "less serious",
            "remanded": "sent back",
            "appellant": "person appealing",
            "respondent": "other party",
            "plaintiff": "person filing case",
            "defendant": "person being sued"
        }

        simplified_guidance = {}
        for key, value in guidance.items():
            if isinstance(value, str):
                simplified_value = value
                for legal_term, simple_term in simplifications.items():
                    simplified_value = simplified_value.replace(legal_term, simple_term)
                simplified_guidance[key] = simplified_value
            elif isinstance(value, list):
                # Fix: Properly simplify each item without creating duplicates
                simplified_list = []
                for item in value:
                    simplified_item = item
                    for legal_term, simple_term in simplifications.items():
                        simplified_item = simplified_item.replace(legal_term, simple_term)
                    simplified_list.append(simplified_item)
                simplified_guidance[key] = simplified_list
            else:
                simplified_guidance[key] = value

        return simplified_guidance

    def _format_comprehensive_response(self, sections: Dict[str, Any], relevant_cases: List[Dict]) -> str:
        """Format sections into a concise, user-friendly response."""

        response_parts = []

        # Legal Analysis - Keep it very concise
        if sections.get("analysis"):
            analysis = sections['analysis'][:200] + "..." if len(sections['analysis']) > 200 else sections['analysis']
            response_parts.append(f"**Legal Analysis:**\n{analysis}\n")

        # Next Steps - Limit to top 3 most important
        if sections.get("next_steps"):
            # Remove duplicates and limit to 3 steps
            unique_steps = []
            seen = set()
            for step in sections['next_steps']:
                if step not in seen and len(unique_steps) < 3:
                    unique_steps.append(step)
                    seen.add(step)

            steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(unique_steps)])
            response_parts.append(f"**Next Steps:**\n{steps_text}\n")

        # Potential Outcomes - Very concise
        if sections.get("outcomes"):
            outcomes = sections['outcomes'][:150] + "..." if len(sections['outcomes']) > 150 else sections['outcomes']
            response_parts.append(f"**Timeline:**\n{outcomes}\n")

        # Important Warnings - Essential only
        if sections.get("warnings"):
            warnings = sections['warnings'][:100] + "..." if len(sections['warnings']) > 100 else sections['warnings']
            response_parts.append(f"**Important:**\n{warnings}")

        return "\n".join(response_parts)
