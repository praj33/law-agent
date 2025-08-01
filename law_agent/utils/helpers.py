"""Helper utility functions."""

import re
import html
from typing import Dict, List, Any, Optional
from datetime import datetime


def format_legal_text(text: str, user_type: str = "common") -> str:
    """Format legal text based on user type."""
    if not text:
        return ""
    
    # Basic formatting
    text = text.strip()
    
    # For common users, simplify language
    if user_type == "common":
        # Replace complex legal terms with simpler alternatives
        replacements = {
            "pursuant to": "according to",
            "heretofore": "before this",
            "hereinafter": "from now on",
            "whereas": "since",
            "therefore": "so",
            "notwithstanding": "despite",
            "aforementioned": "mentioned above"
        }
        
        for complex_term, simple_term in replacements.items():
            text = re.sub(rf"\b{complex_term}\b", simple_term, text, flags=re.IGNORECASE)
    
    return text


def validate_user_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize user input."""
    errors = []
    cleaned_data = {}
    
    # Validate session_id
    if "session_id" in input_data:
        session_id = input_data["session_id"]
        if not session_id or not isinstance(session_id, str):
            errors.append("Invalid session ID")
        else:
            cleaned_data["session_id"] = session_id.strip()
    
    # Validate query
    if "query" in input_data:
        query = input_data["query"]
        if not query or not isinstance(query, str):
            errors.append("Query is required")
        elif len(query.strip()) < 3:
            errors.append("Query must be at least 3 characters")
        elif len(query) > 5000:
            errors.append("Query is too long (max 5000 characters)")
        else:
            cleaned_data["query"] = sanitize_query(query)
    
    # Validate user_id
    if "user_id" in input_data:
        user_id = input_data["user_id"]
        if not user_id or not isinstance(user_id, str):
            errors.append("Invalid user ID")
        else:
            cleaned_data["user_id"] = user_id.strip()
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "data": cleaned_data
    }


def sanitize_query(query: str) -> str:
    """Sanitize user query to prevent injection attacks."""
    if not query:
        return ""
    
    # HTML escape
    query = html.escape(query)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r"<script.*?>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload=",
        r"onerror=",
        r"onclick="
    ]
    
    for pattern in dangerous_patterns:
        query = re.sub(pattern, "", query, flags=re.IGNORECASE | re.DOTALL)
    
    # Limit length and clean whitespace
    query = query.strip()[:5000]
    query = re.sub(r'\s+', ' ', query)  # Normalize whitespace
    
    return query


def extract_legal_entities(text: str) -> Dict[str, List[str]]:
    """Extract legal entities from text."""
    entities = {
        "case_citations": [],
        "statutes": [],
        "courts": [],
        "dates": [],
        "monetary_amounts": []
    }
    
    # Case citations (simplified pattern)
    case_pattern = r'\b\d+\s+[A-Z][a-z]+\.?\s+\d+\b'
    entities["case_citations"] = re.findall(case_pattern, text)
    
    # Statute references
    statute_pattern = r'\b\d+\s+U\.?S\.?C\.?\s+§?\s*\d+\b'
    entities["statutes"] = re.findall(statute_pattern, text)
    
    # Court names
    court_pattern = r'\b(?:Supreme Court|District Court|Court of Appeals|Circuit Court)\b'
    entities["courts"] = re.findall(court_pattern, text, re.IGNORECASE)
    
    # Dates
    date_pattern = r'\b(?:\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b'
    entities["dates"] = re.findall(date_pattern, text, re.IGNORECASE)
    
    # Monetary amounts
    money_pattern = r'\$[\d,]+(?:\.\d{2})?'
    entities["monetary_amounts"] = re.findall(money_pattern, text)
    
    return entities


def format_response_for_user_type(response: Dict[str, Any], user_type: str) -> Dict[str, Any]:
    """Format response based on user type."""
    formatted_response = response.copy()
    
    if user_type == "common_person":
        # Simplify language and add explanations
        if "text" in formatted_response:
            formatted_response["text"] = format_legal_text(formatted_response["text"], "common")
        
        # Add helpful explanations
        if "sections" in formatted_response:
            for section in formatted_response["sections"]:
                if "content" in section:
                    section["content"] = format_legal_text(section["content"], "common")
        
        # Emphasize next steps
        if "next_steps" in formatted_response:
            formatted_response["priority_message"] = "Here are the most important steps you should take:"
    
    elif user_type == "law_firm":
        # Add professional details
        formatted_response["professional_notes"] = "Detailed procedural requirements and case law references available upon request."
        
        # Add billing considerations
        if "costs" in formatted_response:
            formatted_response["billing_notes"] = "Consider client budget and case complexity when recommending procedures."
    
    return formatted_response


def calculate_complexity_score(query: str, domain: str) -> float:
    """Calculate complexity score for a legal query."""
    score = 0.0
    
    # Length factor
    word_count = len(query.split())
    if word_count > 100:
        score += 0.3
    elif word_count > 50:
        score += 0.2
    elif word_count > 20:
        score += 0.1
    
    # Legal terminology density
    legal_terms = [
        "pursuant", "heretofore", "whereas", "notwithstanding", "jurisdiction",
        "precedent", "statute", "regulation", "compliance", "liability",
        "damages", "injunction", "discovery", "deposition", "motion"
    ]
    
    term_count = sum(1 for term in legal_terms if term.lower() in query.lower())
    score += min(0.4, term_count * 0.05)
    
    # Domain-specific complexity
    complex_domains = ["constitutional_law", "tax_law", "intellectual_property"]
    if domain in complex_domains:
        score += 0.2
    
    # Normalize to 0-1 range
    return min(1.0, score)


def generate_session_summary(interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary of user session."""
    if not interactions:
        return {"total_interactions": 0, "summary": "No interactions yet"}
    
    total_interactions = len(interactions)
    domains = [i.get("predicted_domain") for i in interactions if i.get("predicted_domain")]
    
    # Count domain distribution
    domain_counts = {}
    for domain in domains:
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Calculate average confidence
    confidences = [i.get("confidence_score", 0) for i in interactions if i.get("confidence_score")]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # Count feedback
    feedback_counts = {"upvote": 0, "downvote": 0, "neutral": 0}
    for interaction in interactions:
        feedback = interaction.get("feedback")
        if feedback:
            feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1
    
    return {
        "total_interactions": total_interactions,
        "domain_distribution": domain_counts,
        "average_confidence": avg_confidence,
        "feedback_summary": feedback_counts,
        "most_common_domain": max(domain_counts.items(), key=lambda x: x[1])[0] if domain_counts else None,
        "satisfaction_rate": feedback_counts["upvote"] / max(1, sum(feedback_counts.values()))
    }


def format_time_duration(seconds: float) -> str:
    """Format time duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def create_user_preferences(user_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create user preferences based on interaction history."""
    preferences = {
        "preferred_response_style": "balanced",
        "preferred_complexity": "medium",
        "preferred_domains": [],
        "response_length_preference": "medium"
    }
    
    if not user_history:
        return preferences
    
    # Analyze response length preferences based on time spent
    time_spent_data = [i.get("time_spent", 0) for i in user_history if i.get("time_spent")]
    if time_spent_data:
        avg_time = sum(time_spent_data) / len(time_spent_data)
        if avg_time > 300:  # 5 minutes
            preferences["response_length_preference"] = "detailed"
        elif avg_time < 60:  # 1 minute
            preferences["response_length_preference"] = "concise"
    
    # Analyze domain preferences
    domains = [i.get("predicted_domain") for i in user_history if i.get("predicted_domain")]
    domain_counts = {}
    for domain in domains:
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Top 3 domains
    sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    preferences["preferred_domains"] = [domain for domain, _ in sorted_domains[:3]]
    
    return preferences
