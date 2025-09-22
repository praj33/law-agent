"""Legal route mapping system for guiding users through legal procedures."""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger

from ..core.state import LegalDomain, UserType


@dataclass
class LegalRoute:
    """Represents a legal route with procedures and guidance."""
    domain: LegalDomain
    title: str
    summary: str
    procedures: List[str]
    next_steps: List[str]
    forms: List[Dict[str, str]]
    resources: List[Dict[str, str]]
    timeline: str
    costs: str
    complexity: str  # "low", "medium", "high"
    user_type_specific: Dict[UserType, Dict[str, Any]]


class LegalRouteMapper:
    """Maps legal domains to appropriate procedures and guidance."""
    
    def __init__(self):
        """Initialize the route mapper with predefined routes."""
        self.routes = self._load_legal_routes()
        logger.info("Legal Route Mapper initialized")
    
    def _load_legal_routes(self) -> Dict[LegalDomain, List[LegalRoute]]:
        """Load predefined legal routes for each domain."""
        routes = {}
        
        # Family Law Routes
        routes[LegalDomain.FAMILY_LAW] = [
            LegalRoute(
                domain=LegalDomain.FAMILY_LAW,
                title="Divorce Proceedings",
                summary="Guide through divorce process including asset division and custody arrangements.",
                procedures=[
                    "File petition for divorce in appropriate court",
                    "Serve divorce papers to spouse",
                    "Complete financial disclosure forms",
                    "Negotiate settlement or proceed to trial",
                    "Finalize divorce decree"
                ],
                next_steps=[
                    "Gather financial documents",
                    "Consider mediation",
                    "Consult with family law attorney",
                    "File initial paperwork"
                ],
                forms=[
                    {"name": "Petition for Divorce", "url": "/forms/divorce-petition"},
                    {"name": "Financial Affidavit", "url": "/forms/financial-affidavit"},
                    {"name": "Parenting Plan", "url": "/forms/parenting-plan"}
                ],
                resources=[
                    {"name": "Family Court Self-Help Center", "url": "/resources/family-court"},
                    {"name": "Divorce Mediation Services", "url": "/resources/mediation"},
                    {"name": "Child Support Calculator", "url": "/tools/child-support"}
                ],
                timeline="3-12 months depending on complexity",
                costs="$500-$5,000+ depending on attorney involvement",
                complexity="medium",
                user_type_specific={
                    UserType.COMMON_PERSON: {
                        "simplified_steps": True,
                        "self_help_resources": True,
                        "cost_warnings": True
                    },
                    UserType.LAW_FIRM: {
                        "detailed_procedures": True,
                        "precedent_cases": True,
                        "billing_considerations": True
                    }
                }
            ),
            LegalRoute(
                domain=LegalDomain.FAMILY_LAW,
                title="Child Custody Modification",
                summary="Process for modifying existing child custody arrangements.",
                procedures=[
                    "Demonstrate substantial change in circumstances",
                    "File motion to modify custody",
                    "Attend mediation if required",
                    "Present evidence at hearing",
                    "Obtain modified custody order"
                ],
                next_steps=[
                    "Document changed circumstances",
                    "File motion with court",
                    "Prepare for mediation",
                    "Gather supporting evidence"
                ],
                forms=[
                    {"name": "Motion to Modify Custody", "url": "/forms/modify-custody"},
                    {"name": "Affidavit of Changed Circumstances", "url": "/forms/changed-circumstances"}
                ],
                resources=[
                    {"name": "Custody Modification Guide", "url": "/guides/custody-modification"},
                    {"name": "Best Interest Factors", "url": "/resources/best-interest"}
                ],
                timeline="2-6 months",
                costs="$1,000-$3,000",
                complexity="medium",
                user_type_specific={
                    UserType.COMMON_PERSON: {
                        "emphasis_on_child_welfare": True,
                        "emotional_support_resources": True
                    },
                    UserType.LAW_FIRM: {
                        "case_law_references": True,
                        "strategic_considerations": True
                    }
                }
            )
        ]
        
        # Criminal Law Routes
        routes[LegalDomain.CRIMINAL_LAW] = [
            LegalRoute(
                domain=LegalDomain.CRIMINAL_LAW,
                title="Criminal Defense Process",
                summary="Navigate criminal charges from arrest through trial or plea.",
                procedures=[
                    "Arraignment and plea entry",
                    "Discovery and evidence review",
                    "Pre-trial motions",
                    "Plea negotiations or trial preparation",
                    "Sentencing or appeal"
                ],
                next_steps=[
                    "Contact criminal defense attorney immediately",
                    "Exercise right to remain silent",
                    "Gather character references",
                    "Prepare for arraignment"
                ],
                forms=[
                    {"name": "Public Defender Application", "url": "/forms/public-defender"},
                    {"name": "Bail Application", "url": "/forms/bail-application"}
                ],
                resources=[
                    {"name": "Criminal Defense Lawyers", "url": "/directory/criminal-lawyers"},
                    {"name": "Bail Bond Services", "url": "/directory/bail-bonds"},
                    {"name": "Know Your Rights Guide", "url": "/guides/criminal-rights"}
                ],
                timeline="3-18 months depending on charges",
                costs="$2,000-$50,000+ for private attorney",
                complexity="high",
                user_type_specific={
                    UserType.COMMON_PERSON: {
                        "rights_education": True,
                        "urgent_actions": True,
                        "support_services": True
                    },
                    UserType.LAW_FIRM: {
                        "defense_strategies": True,
                        "sentencing_guidelines": True,
                        "appeal_procedures": True
                    }
                }
            )
        ]
        
        # Corporate Law Routes
        routes[LegalDomain.CORPORATE_LAW] = [
            LegalRoute(
                domain=LegalDomain.CORPORATE_LAW,
                title="Business Formation",
                summary="Guide through choosing and forming business entity.",
                procedures=[
                    "Choose business structure (LLC, Corp, etc.)",
                    "File formation documents with state",
                    "Obtain EIN from IRS",
                    "Create operating agreements/bylaws",
                    "Comply with ongoing requirements"
                ],
                next_steps=[
                    "Determine business structure needs",
                    "Choose business name and check availability",
                    "Prepare formation documents",
                    "File with Secretary of State"
                ],
                forms=[
                    {"name": "Articles of Incorporation", "url": "/forms/articles-incorporation"},
                    {"name": "LLC Operating Agreement", "url": "/forms/llc-operating"},
                    {"name": "EIN Application", "url": "/forms/ein-application"}
                ],
                resources=[
                    {"name": "Business Structure Comparison", "url": "/guides/business-structures"},
                    {"name": "State Filing Requirements", "url": "/resources/state-filing"},
                    {"name": "Business License Guide", "url": "/guides/business-licenses"}
                ],
                timeline="2-8 weeks",
                costs="$100-$2,000 depending on structure",
                complexity="low",
                user_type_specific={
                    UserType.COMMON_PERSON: {
                        "simplified_explanations": True,
                        "cost_comparisons": True,
                        "diy_options": True
                    },
                    UserType.LAW_FIRM: {
                        "tax_implications": True,
                        "liability_considerations": True,
                        "compliance_requirements": True
                    }
                }
            )
        ]
        
        # Property Law Routes
        routes[LegalDomain.PROPERTY_LAW] = [
            LegalRoute(
                domain=LegalDomain.PROPERTY_LAW,
                title="Real Estate Purchase",
                summary="Navigate the home buying process and legal requirements.",
                procedures=[
                    "Make offer and negotiate terms",
                    "Conduct property inspection",
                    "Secure financing and title search",
                    "Review and sign closing documents",
                    "Complete property transfer"
                ],
                next_steps=[
                    "Get pre-approved for mortgage",
                    "Hire real estate attorney",
                    "Schedule property inspection",
                    "Review purchase agreement"
                ],
                forms=[
                    {"name": "Purchase Agreement", "url": "/forms/purchase-agreement"},
                    {"name": "Property Disclosure", "url": "/forms/property-disclosure"},
                    {"name": "Title Insurance Application", "url": "/forms/title-insurance"}
                ],
                resources=[
                    {"name": "Home Buying Checklist", "url": "/guides/home-buying"},
                    {"name": "Real Estate Attorneys", "url": "/directory/real-estate-lawyers"},
                    {"name": "Property Records Search", "url": "/tools/property-search"}
                ],
                timeline="30-60 days",
                costs="1-3% of purchase price in closing costs",
                complexity="medium",
                user_type_specific={
                    UserType.COMMON_PERSON: {
                        "first_time_buyer_tips": True,
                        "financing_options": True,
                        "inspection_importance": True
                    },
                    UserType.LAW_FIRM: {
                        "title_issues": True,
                        "contract_negotiations": True,
                        "closing_procedures": True
                    }
                }
            )
        ]
        
        # Employment Law Routes
        routes[LegalDomain.EMPLOYMENT_LAW] = [
            LegalRoute(
                domain=LegalDomain.EMPLOYMENT_LAW,
                title="Workplace Discrimination Claim",
                summary="Process for filing discrimination complaint with EEOC.",
                procedures=[
                    "Document discriminatory incidents",
                    "File complaint with EEOC",
                    "Participate in EEOC investigation",
                    "Receive right-to-sue letter",
                    "File lawsuit if necessary"
                ],
                next_steps=[
                    "Gather evidence of discrimination",
                    "File EEOC complaint within 180/300 days",
                    "Consult with employment attorney",
                    "Preserve relevant documents"
                ],
                forms=[
                    {"name": "EEOC Complaint Form", "url": "/forms/eeoc-complaint"},
                    {"name": "Discrimination Incident Log", "url": "/forms/incident-log"}
                ],
                resources=[
                    {"name": "EEOC Office Locator", "url": "/directory/eeoc-offices"},
                    {"name": "Employment Rights Guide", "url": "/guides/employment-rights"},
                    {"name": "Discrimination Lawyers", "url": "/directory/employment-lawyers"}
                ],
                timeline="6-18 months",
                costs="Free for EEOC filing, attorney fees vary",
                complexity="medium",
                user_type_specific={
                    UserType.COMMON_PERSON: {
                        "emotional_support": True,
                        "retaliation_protection": True,
                        "free_resources": True
                    },
                    UserType.LAW_FIRM: {
                        "damages_calculation": True,
                        "litigation_strategy": True,
                        "settlement_considerations": True
                    }
                }
            )
        ]
        
        return routes
    
    async def get_route(
        self,
        domain: LegalDomain,
        query: str,
        user_type: UserType,
        rl_recommendation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get appropriate legal route for the given domain and context."""
        
        if domain not in self.routes:
            return self._get_default_route(domain, user_type)
        
        available_routes = self.routes[domain]
        
        # Select best route based on query content and RL recommendation
        selected_route = self._select_best_route(
            available_routes, query, user_type, rl_recommendation
        )
        
        # Customize route for user type
        customized_route = self._customize_for_user_type(selected_route, user_type)
        
        logger.debug(f"Selected route '{selected_route.title}' for domain {domain}")
        
        return customized_route
    
    def _select_best_route(
        self,
        routes: List[LegalRoute],
        query: str,
        user_type: UserType,
        rl_recommendation: Optional[Dict[str, Any]] = None
    ) -> LegalRoute:
        """Select the most appropriate route from available options."""
        
        if len(routes) == 1:
            return routes[0]
        
        # Score routes based on query content
        scored_routes = []
        query_lower = query.lower()
        
        for route in routes:
            score = 0
            
            # Check if query mentions route-specific terms
            route_terms = route.title.lower().split() + route.summary.lower().split()
            for term in route_terms:
                if term in query_lower:
                    score += 1
            
            # Consider complexity preference
            if user_type == UserType.COMMON_PERSON and route.complexity == "low":
                score += 2
            elif user_type == UserType.LAW_FIRM and route.complexity == "high":
                score += 1
            
            # Apply RL recommendation if available
            if rl_recommendation and "route_preference" in rl_recommendation:
                if route.title in rl_recommendation["route_preference"]:
                    score += 3
            
            scored_routes.append((route, score))
        
        # Return route with highest score
        best_route = max(scored_routes, key=lambda x: x[1])[0]
        return best_route
    
    def _customize_for_user_type(self, route: LegalRoute, user_type: UserType) -> Dict[str, Any]:
        """Customize route information for specific user type."""
        
        base_info = {
            "title": route.title,
            "summary": route.summary,
            "procedures": route.procedures,
            "next_steps": route.next_steps,
            "forms": route.forms,
            "resources": route.resources,
            "timeline": route.timeline,
            "costs": route.costs,
            "complexity": route.complexity
        }
        
        # Add user-type specific customizations
        if user_type in route.user_type_specific:
            customizations = route.user_type_specific[user_type]
            
            if customizations.get("simplified_steps"):
                base_info["procedures"] = [
                    f"Step {i+1}: {proc}" for i, proc in enumerate(route.procedures)
                ]
            
            if customizations.get("urgent_actions"):
                base_info["urgent_notice"] = "Time-sensitive: Contact an attorney immediately"
            
            if customizations.get("cost_warnings") and user_type == UserType.COMMON_PERSON:
                base_info["cost_warning"] = "Consider legal aid if you cannot afford an attorney"
            
            if customizations.get("detailed_procedures") and user_type == UserType.LAW_FIRM:
                base_info["professional_notes"] = "Detailed procedural requirements available in practice guides"
        
        return base_info
    
    def _get_default_route(self, domain: LegalDomain, user_type: UserType) -> Dict[str, Any]:
        """Get default route information for domains without specific routes."""
        
        return {
            "title": f"General {domain.value.replace('_', ' ').title()} Guidance",
            "summary": f"General information and next steps for {domain.value.replace('_', ' ')} matters.",
            "procedures": [
                "Consult with a qualified attorney",
                "Gather relevant documents",
                "Understand your legal rights",
                "Consider alternative dispute resolution"
            ],
            "next_steps": [
                "Schedule consultation with specialist attorney",
                "Organize relevant documentation",
                "Research applicable laws",
                "Consider time limitations"
            ],
            "forms": [],
            "resources": [
                {"name": "Legal Aid Directory", "url": "/directory/legal-aid"},
                {"name": "Attorney Referral Service", "url": "/directory/attorney-referral"},
                {"name": "Self-Help Legal Resources", "url": "/resources/self-help"}
            ],
            "timeline": "Varies by specific matter",
            "costs": "Consultation fees typically $100-$500",
            "complexity": "medium"
        }
    
    def get_available_routes(self, domain: LegalDomain) -> List[str]:
        """Get list of available route titles for a domain."""
        if domain not in self.routes:
            return []
        
        return [route.title for route in self.routes[domain]]
    
    def search_routes(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for routes containing specific terms."""
        results = []
        search_lower = search_term.lower()
        
        for domain, routes in self.routes.items():
            for route in routes:
                if (search_lower in route.title.lower() or 
                    search_lower in route.summary.lower()):
                    results.append({
                        "domain": domain,
                        "title": route.title,
                        "summary": route.summary,
                        "complexity": route.complexity
                    })
        
        return results
