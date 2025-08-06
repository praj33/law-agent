"""Grok AI Legal Reasoning Engine for Real Legal Solutions."""

import asyncio
import json
import re
import httpx
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from loguru import logger

from ..core.config import settings
from ..core.state import LegalDomain, UserType


class GrokLegalEngine:
    """Grok AI-powered legal reasoning engine for real legal solutions."""
    
    def __init__(self):
        """Initialize the Grok legal engine."""
        self.api_key = settings.grok_api_key
        self.model = settings.grok_model
        self.temperature = settings.grok_temperature
        self.max_tokens = settings.grok_max_tokens
        self.base_url = "https://api.x.ai/v1"
        
        # Legal expertise prompts
        self.legal_system_prompt = """You are an expert legal advisor with deep knowledge of law. 
        Provide specific, actionable legal advice with:
        1. Clear legal analysis
        2. Specific next steps
        3. Relevant laws/precedents
        4. Practical guidance
        5. Timeline expectations
        
        Be concise but comprehensive. Focus on real solutions, not generic advice."""
        
        if self.api_key and self.api_key.strip() and not self.api_key.startswith("your-"):
            logger.info("✅ Grok AI Legal Engine initialized")
        else:
            logger.warning("⚠️ Grok API key not configured - using fallback responses")
            self.api_key = None  # Ensure it's None for proper fallback
    
    async def generate_legal_response(
        self, 
        query: str, 
        domain: LegalDomain, 
        user_type: UserType,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive legal response using Grok AI."""
        
        if not self.api_key:
            return await self._fallback_response(query, domain, user_type)
        
        try:
            # Create domain-specific prompt
            domain_prompt = self._get_domain_specific_prompt(domain, user_type)
            
            # Build the request
            messages = [
                {"role": "system", "content": f"{self.legal_system_prompt}\n\n{domain_prompt}"},
                {"role": "user", "content": f"Legal Query: {query}\n\nProvide specific legal advice with actionable steps."}
            ]
            
            # Call Grok API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    
                    # Structure the response
                    structured_response = self._structure_legal_response(ai_response, domain, query)
                    
                    logger.info(f"✅ Grok AI generated legal response for {domain.value}")
                    return structured_response
                else:
                    logger.error(f"Grok API error: {response.status_code} - {response.text}")
                    return await self._fallback_response(query, domain, user_type)
                    
        except Exception as e:
            logger.error(f"Grok AI request failed: {e}")
            return await self._fallback_response(query, domain, user_type)
    
    def _get_domain_specific_prompt(self, domain: LegalDomain, user_type: UserType) -> str:
        """Get domain-specific legal prompts."""
        
        domain_prompts = {
            LegalDomain.FAMILY_LAW: """
            You are a family law specialist. Focus on:
            - Divorce procedures and grounds
            - Child custody and support
            - Alimony and property division
            - Domestic relations
            - Marriage and adoption laws
            Provide specific steps for family court procedures.
            """,
            
            LegalDomain.CRIMINAL_LAW: """
            You are a criminal law expert. Focus on:
            - Criminal charges and defenses
            - Bail and arrest procedures
            - Court processes and rights
            - Evidence and investigation
            - Sentencing and appeals
            Provide specific guidance on criminal defense strategies.
            """,
            
            LegalDomain.EMPLOYMENT_LAW: """
            You are an employment law specialist. Focus on:
            - Wrongful termination
            - Workplace discrimination
            - Labor rights and wages
            - Employment contracts
            - Workplace harassment
            Provide specific steps for employment disputes.
            """,
            
            LegalDomain.PROPERTY_LAW: """
            You are a property law expert. Focus on:
            - Real estate transactions
            - Landlord-tenant disputes
            - Property ownership rights
            - Zoning and land use
            - Property disputes
            Provide specific guidance on property matters.
            """
        }
        
        base_prompt = domain_prompts.get(domain, "You are a general legal advisor.")
        
        if user_type == UserType.COMMON_PERSON:
            base_prompt += "\n\nExplain legal concepts in simple terms for non-lawyers."
        elif user_type == UserType.LAWYER:
            base_prompt += "\n\nProvide detailed legal analysis with case citations and precedents."
        
        return base_prompt
    
    def _structure_legal_response(self, ai_response: str, domain: LegalDomain, query: str) -> Dict[str, Any]:
        """Structure the AI response into a proper legal format."""
        
        # Try to parse structured response
        sections = self._parse_response_sections(ai_response)
        
        return {
            "text": ai_response,
            "domain": domain.value,
            "analysis": sections.get("analysis", "Legal analysis provided above."),
            "next_steps": sections.get("next_steps", self._extract_action_items(ai_response)),
            "timeline": sections.get("timeline", "Timeline varies by case complexity."),
            "important_notes": sections.get("important", "Consult with a qualified attorney for your specific situation."),
            "confidence": 0.9,  # High confidence for Grok AI responses
            "source": "grok_ai",
            "generated_at": datetime.now().isoformat()
        }
    
    def _parse_response_sections(self, response: str) -> Dict[str, str]:
        """Parse structured sections from AI response."""
        sections = {}
        
        # Common section patterns
        patterns = {
            "analysis": r"(?:Legal Analysis|Analysis):\s*(.*?)(?=\n\n|\n[A-Z]|$)",
            "next_steps": r"(?:Next Steps|Steps|Actions):\s*(.*?)(?=\n\n|\n[A-Z]|$)",
            "timeline": r"(?:Timeline|Timeframe):\s*(.*?)(?=\n\n|\n[A-Z]|$)",
            "important": r"(?:Important|Note|Warning):\s*(.*?)(?=\n\n|\n[A-Z]|$)"
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section] = match.group(1).strip()
        
        return sections
    
    def _extract_action_items(self, response: str) -> List[str]:
        """Extract action items from response."""
        # Look for numbered lists or bullet points
        action_patterns = [
            r"(\d+\.\s+[^\n]+)",  # Numbered lists
            r"(-\s+[^\n]+)",      # Bullet points
            r"(•\s+[^\n]+)"       # Bullet points
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, response)
            actions.extend([match.strip() for match in matches])
        
        return actions[:5]  # Limit to 5 action items
    
    async def _fallback_response(self, query: str, domain: LegalDomain, user_type: UserType) -> Dict[str, Any]:
        """Provide query-specific fallback response when Grok AI is unavailable."""

        # Generate query-specific responses based on keywords
        query_lower = query.lower()

        # Family Law specific responses
        if domain == LegalDomain.FAMILY_LAW:
            if "divorce" in query_lower:
                return self._get_divorce_response()
            elif "custody" in query_lower or "child" in query_lower:
                return self._get_custody_response()
            elif "alimony" in query_lower or "support" in query_lower:
                return self._get_support_response()
            else:
                return self._get_generic_family_response()

        # Criminal Law specific responses
        elif domain == LegalDomain.CRIMINAL_LAW:
            if "arrest" in query_lower or "police" in query_lower:
                return self._get_arrest_response()
            elif "theft" in query_lower or "steal" in query_lower:
                return self._get_theft_response()
            elif "dui" in query_lower or "drunk" in query_lower:
                return self._get_dui_response()
            else:
                return self._get_generic_criminal_response()

        # Employment Law specific responses
        elif domain == LegalDomain.EMPLOYMENT_LAW:
            if "fired" in query_lower or "termination" in query_lower:
                return self._get_termination_response()
            elif "discrimination" in query_lower:
                return self._get_discrimination_response()
            elif "harassment" in query_lower:
                return self._get_harassment_response()
            else:
                return self._get_generic_employment_response()

        # Property Law specific responses
        elif domain == LegalDomain.PROPERTY_LAW:
            if "evict" in query_lower or "landlord" in query_lower:
                return self._get_eviction_response()
            elif "buy" in query_lower or "purchase" in query_lower:
                return self._get_property_purchase_response()
            else:
                return self._get_generic_property_response()

        # Default fallback
        return self._get_default_response(domain)

    def _get_generic_family_response(self) -> Dict[str, Any]:
        """Generic family law response."""
        return {
            "text": """**Legal Analysis:**
Family law matters involve personal relationships and require consideration of state-specific laws and procedures.

**Next Steps:**
1. Identify specific family law issue (divorce, custody, support, etc.)
2. Gather relevant documents and evidence
3. Understand your state's family law requirements
4. Consider mediation or collaborative law approaches
5. Consult with family law attorney

**Timeline:**
Varies widely based on specific matter and cooperation of parties.

**Important:**
Family law has emotional and financial implications. Professional guidance helps protect your interests.""",
            "analysis": "Family law matters require understanding of state-specific procedures and emotional considerations.",
            "next_steps": ["Identify issue", "Gather documents", "Research state law", "Consider mediation", "Consult attorney"],
            "timeline": "Varies by matter type",
            "domain": "family_law",
            "confidence": 0.7,
            "source": "generic_fallback",
            "generated_at": datetime.now().isoformat()
        }

    def _get_generic_criminal_response(self) -> Dict[str, Any]:
        """Generic criminal law response."""
        return {
            "text": """**Legal Analysis:**
Criminal matters involve potential loss of liberty and require immediate professional legal representation.

**Next Steps:**
1. Exercise constitutional rights (remain silent, request attorney)
2. Do not discuss case with anyone except your lawyer
3. Gather evidence and witness information for defense
4. Understand charges and potential penalties
5. Prepare for court proceedings

**Timeline:**
Initial proceedings: days to weeks. Resolution: months to years.

**Important:**
Criminal convictions have lasting consequences. Immediate legal representation is crucial for protecting your rights.""",
            "analysis": "Criminal matters require immediate professional representation to protect constitutional rights.",
            "next_steps": ["Exercise rights", "Remain silent", "Gather evidence", "Understand charges", "Prepare defense"],
            "timeline": "Days to years",
            "domain": "criminal_law",
            "confidence": 0.8,
            "source": "generic_fallback",
            "generated_at": datetime.now().isoformat()
        }

    def _get_generic_employment_response(self) -> Dict[str, Any]:
        """Generic employment law response."""
        return {
            "text": """**Legal Analysis:**
Employment law protects workers from discrimination, unsafe conditions, and unfair practices while balancing employer rights.

**Next Steps:**
1. Review employment contract and company policies
2. Document any violations or discriminatory conduct
3. Follow internal complaint procedures if appropriate
4. Research applicable employment laws and regulations
5. Consider filing complaint with relevant agency (EEOC, DOL, etc.)

**Timeline:**
Administrative complaints: 180-300 days. Legal proceedings: 1-3 years.

**Important:**
Employment law claims often have strict deadlines. Preserve documentation and seek guidance promptly.""",
            "analysis": "Employment law balances worker protections with employer rights under federal and state regulations.",
            "next_steps": ["Review policies", "Document issues", "Follow procedures", "Research laws", "Consider complaints"],
            "timeline": "180 days to 3 years",
            "domain": "employment_law",
            "confidence": 0.7,
            "source": "generic_fallback",
            "generated_at": datetime.now().isoformat()
        }

    def _get_generic_property_response(self) -> Dict[str, Any]:
        """Generic property law response."""
        return {
            "text": """**Legal Analysis:**
Property law governs ownership, use, and transfer of real estate and personal property with complex state and local regulations.

**Next Steps:**
1. Identify specific property law issue (ownership, transfer, disputes, etc.)
2. Gather property documents (deeds, contracts, leases, etc.)
3. Research applicable zoning and land use regulations
4. Understand your property rights and obligations
5. Consider professional legal and real estate guidance

**Timeline:**
Property transactions: 30-90 days. Disputes: months to years.

**Important:**
Property law involves significant financial interests. Professional guidance helps avoid costly mistakes.""",
            "analysis": "Property law involves complex regulations governing ownership, use, and transfer of real estate.",
            "next_steps": ["Identify issue", "Gather documents", "Research regulations", "Understand rights", "Seek guidance"],
            "timeline": "30 days to years",
            "domain": "property_law",
            "confidence": 0.7,
            "source": "generic_fallback",
            "generated_at": datetime.now().isoformat()
        }

    def _get_divorce_response(self) -> Dict[str, Any]:
        """Specific response for divorce queries."""
        return {
            "text": """**Legal Analysis:**
Divorce proceedings require establishing legal grounds and following state-specific procedures. Common grounds include irreconcilable differences, adultery, abandonment, or abuse.

**Next Steps:**
1. Determine your state's divorce grounds and residency requirements
2. Gather financial documents (tax returns, bank statements, property deeds)
3. Consider whether divorce will be contested or uncontested
4. File petition for dissolution of marriage in appropriate court
5. Serve divorce papers to spouse according to state law

**Timeline:**
Uncontested divorce: 2-6 months. Contested divorce: 6 months to 2+ years.

**Important:**
Property division, child custody, and spousal support laws vary significantly by state. Consider legal representation for complex financial situations.""",
            "analysis": "Divorce requires following specific legal procedures and establishing valid grounds under state law.",
            "next_steps": ["Check state requirements", "Gather financial documents", "File petition", "Serve papers", "Consider mediation"],
            "timeline": "2 months to 2+ years depending on complexity",
            "domain": "family_law",
            "confidence": 0.8,
            "source": "query_specific_fallback",
            "generated_at": datetime.now().isoformat()
        }

    def _get_custody_response(self) -> Dict[str, Any]:
        """Specific response for child custody queries."""
        return {
            "text": """**Legal Analysis:**
Child custody decisions are based on the "best interests of the child" standard. Courts consider factors like parental fitness, stability, child's preferences (if age-appropriate), and existing relationships.

**Next Steps:**
1. Document your relationship and involvement with the child
2. Gather evidence of stable housing, income, and lifestyle
3. Consider child's school, medical, and social needs
4. File custody petition in family court
5. Prepare for custody evaluation if ordered by court

**Timeline:**
Temporary custody: 2-4 weeks. Final custody determination: 3-12 months.

**Important:**
Custody modifications require showing substantial change in circumstances. Maintain detailed records of parenting time and child's needs.""",
            "analysis": "Child custody is determined by best interests standard with multiple factors considered.",
            "next_steps": ["Document parental involvement", "Gather stability evidence", "File petition", "Prepare for evaluation"],
            "timeline": "2 weeks to 12 months",
            "domain": "family_law",
            "confidence": 0.8,
            "source": "query_specific_fallback",
            "generated_at": datetime.now().isoformat()
        }

    def _get_arrest_response(self) -> Dict[str, Any]:
        """Specific response for arrest queries."""
        return {
            "text": """**Legal Analysis:**
After arrest, you have constitutional rights including right to remain silent and right to attorney. Anything you say can be used against you in court.

**Next Steps:**
1. Exercise your right to remain silent immediately
2. Request an attorney before any questioning
3. Do not consent to searches without warrant
4. Contact family/friends to arrange bail if applicable
5. Gather witness information and evidence for defense

**Timeline:**
Arraignment: 24-72 hours. Trial: 6 months to 2 years depending on charges.

**Important:**
Criminal charges can result in jail time, fines, and permanent criminal record. Do not discuss case details with anyone except your attorney.""",
            "analysis": "Arrest triggers constitutional protections and requires immediate legal representation.",
            "next_steps": ["Remain silent", "Request attorney", "Refuse searches", "Arrange bail", "Gather evidence"],
            "timeline": "24 hours to 2 years",
            "domain": "criminal_law",
            "confidence": 0.9,
            "source": "query_specific_fallback",
            "generated_at": datetime.now().isoformat()
        }

    def _get_termination_response(self) -> Dict[str, Any]:
        """Specific response for wrongful termination queries."""
        return {
            "text": """**Legal Analysis:**
Wrongful termination occurs when firing violates employment contract, anti-discrimination laws, or public policy. Most employment is "at-will" but exceptions exist.

**Next Steps:**
1. Review employment contract and employee handbook
2. Document circumstances of termination and any discriminatory conduct
3. File for unemployment benefits immediately
4. Gather evidence of policy violations or discrimination
5. Consider filing complaint with EEOC if discrimination involved

**Timeline:**
EEOC complaint: 180-300 days from termination. Lawsuit: 2-4 years.

**Important:**
Employment discrimination claims have strict deadlines. Preserve all employment records and communications.""",
            "analysis": "Wrongful termination claims depend on contract terms and anti-discrimination protections.",
            "next_steps": ["Review contract", "Document termination", "File unemployment", "Gather evidence", "Consider EEOC"],
            "timeline": "180 days to 4 years",
            "domain": "employment_law",
            "confidence": 0.8,
            "source": "query_specific_fallback",
            "generated_at": datetime.now().isoformat()
        }

    def _get_eviction_response(self) -> Dict[str, Any]:
        """Specific response for eviction queries."""
        return {
            "text": """**Legal Analysis:**
Landlords must follow legal eviction procedures including proper notice and court proceedings. Tenants have rights to contest eviction and cure defaults.

**Next Steps:**
1. Review lease agreement and eviction notice for compliance
2. Check if proper notice period was given under state law
3. Determine if eviction is for valid legal cause
4. Respond to eviction lawsuit if filed in court
5. Consider negotiating payment plan or move-out agreement

**Timeline:**
Notice period: 3-30 days. Court proceedings: 2-8 weeks.

**Important:**
Illegal "self-help" evictions (changing locks, shutting utilities) are prohibited. Tenants may have defenses based on habitability issues.""",
            "analysis": "Eviction requires following specific legal procedures with tenant protections available.",
            "next_steps": ["Review notice", "Check compliance", "Determine validity", "Respond to lawsuit", "Consider negotiation"],
            "timeline": "3 days to 8 weeks",
            "domain": "property_law",
            "confidence": 0.8,
            "source": "query_specific_fallback",
            "generated_at": datetime.now().isoformat()
        }

    def _get_default_response(self, domain: LegalDomain) -> Dict[str, Any]:
        """Default fallback response."""
        return {
            "text": f"""**Legal Analysis:**
This {domain.value.replace('_', ' ')} matter requires careful legal evaluation based on specific facts and applicable laws.

**Next Steps:**
1. Document all relevant facts and circumstances
2. Gather supporting evidence and documentation
3. Research applicable laws and regulations
4. Consult with qualified attorney in your jurisdiction
5. Understand deadlines and procedural requirements

**Timeline:**
Varies based on case complexity and legal procedures.

**Important:**
Legal matters often have strict deadlines. Prompt action and professional guidance recommended.""",
            "analysis": f"This {domain.value.replace('_', ' ')} matter requires professional legal evaluation.",
            "next_steps": ["Document facts", "Gather evidence", "Research laws", "Consult attorney", "Check deadlines"],
            "timeline": "Varies by case complexity",
            "domain": domain.value,
            "confidence": 0.6,
            "source": "default_fallback",
            "generated_at": datetime.now().isoformat()
        }
