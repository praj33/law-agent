"""Data processing utilities for legal documents and text."""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


def process_legal_document(document_text: str) -> Dict[str, Any]:
    """Process a legal document and extract key information."""
    
    result = {
        "document_type": detect_document_type(document_text),
        "entities": extract_entities(document_text),
        "key_sections": extract_key_sections(document_text),
        "dates": extract_dates(document_text),
        "parties": extract_parties(document_text),
        "monetary_amounts": extract_monetary_amounts(document_text),
        "legal_citations": extract_legal_citations(document_text),
        "summary": generate_document_summary(document_text)
    }
    
    return result


def detect_document_type(text: str) -> str:
    """Detect the type of legal document."""
    
    text_lower = text.lower()
    
    # Contract indicators
    if any(term in text_lower for term in ["agreement", "contract", "party", "consideration", "terms"]):
        return "contract"
    
    # Court document indicators
    if any(term in text_lower for term in ["plaintiff", "defendant", "court", "motion", "order"]):
        return "court_document"
    
    # Will/Estate indicators
    if any(term in text_lower for term in ["will", "testament", "executor", "beneficiary", "estate"]):
        return "will_estate"
    
    # Corporate indicators
    if any(term in text_lower for term in ["corporation", "llc", "articles", "bylaws", "shareholder"]):
        return "corporate_document"
    
    # Real estate indicators
    if any(term in text_lower for term in ["deed", "property", "real estate", "mortgage", "lease"]):
        return "real_estate"
    
    return "unknown"


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract various legal entities from text."""
    
    entities = {
        "people": [],
        "organizations": [],
        "locations": [],
        "case_citations": [],
        "statutes": [],
        "dates": [],
        "monetary_amounts": []
    }
    
    # Extract people (simplified pattern)
    people_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
    entities["people"] = list(set(re.findall(people_pattern, text)))
    
    # Extract organizations
    org_patterns = [
        r'\b[A-Z][a-z]+ (?:Inc\.|LLC|Corp\.|Corporation|Company)\b',
        r'\b[A-Z][A-Z]+ [A-Z][a-z]+\b'  # Acronyms
    ]
    for pattern in org_patterns:
        entities["organizations"].extend(re.findall(pattern, text))
    
    # Extract locations (states, cities)
    location_pattern = r'\b(?:Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming)\b'
    entities["locations"] = re.findall(location_pattern, text)
    
    # Extract case citations
    citation_patterns = [
        r'\b\d+\s+[A-Z][a-z]+\.?\s+\d+\b',  # Basic citation format
        r'\b\d+\s+U\.S\.\s+\d+\b',          # US Supreme Court
        r'\b\d+\s+F\.\d+d\s+\d+\b'          # Federal courts
    ]
    for pattern in citation_patterns:
        entities["case_citations"].extend(re.findall(pattern, text))
    
    # Extract statute references
    statute_patterns = [
        r'\b\d+\s+U\.?S\.?C\.?\s+§?\s*\d+\b',
        r'\bSection\s+\d+\b',
        r'\b§\s*\d+\b'
    ]
    for pattern in statute_patterns:
        entities["statutes"].extend(re.findall(pattern, text, re.IGNORECASE))
    
    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))
    
    return entities


def extract_key_sections(text: str) -> List[Dict[str, str]]:
    """Extract key sections from legal document."""
    
    sections = []
    
    # Common section headers
    section_patterns = [
        r'(?:WHEREAS|THEREFORE|NOW THEREFORE|ARTICLE|SECTION|CLAUSE)\s+[IVX\d]+[\.:]?\s*([^\n]+)',
        r'^\d+\.\s*([^\n]+)',  # Numbered sections
        r'^[A-Z\s]{3,}:',      # All caps headers
    ]
    
    for pattern in section_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            section_title = match.group(1) if match.groups() else match.group(0)
            
            # Find section content (next 200 characters)
            start_pos = match.end()
            content = text[start_pos:start_pos + 200].strip()
            
            sections.append({
                "title": section_title.strip(),
                "content": content,
                "position": match.start()
            })
    
    return sections[:10]  # Limit to first 10 sections


def extract_dates(text: str) -> List[str]:
    """Extract dates from text."""
    
    date_patterns = [
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
        r'\b\d{4}-\d{2}-\d{2}\b',      # YYYY-MM-DD
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
    ]
    
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))
    
    return list(set(dates))


def extract_parties(text: str) -> List[str]:
    """Extract parties from legal document."""
    
    party_patterns = [
        r'(?:Plaintiff|Defendant|Petitioner|Respondent|Grantor|Grantee|Lessor|Lessee|Buyer|Seller|Party|Client):\s*([^\n,]+)',
        r'between\s+([^,\n]+)\s+and\s+([^,\n]+)',
        r'(?:Party A|Party B|First Party|Second Party):\s*([^\n,]+)'
    ]
    
    parties = []
    for pattern in party_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                parties.extend(match)
            else:
                parties.append(match)
    
    # Clean up party names
    cleaned_parties = []
    for party in parties:
        party = party.strip().strip(',').strip()
        if len(party) > 2 and len(party) < 100:  # Reasonable length
            cleaned_parties.append(party)
    
    return list(set(cleaned_parties))


def extract_monetary_amounts(text: str) -> List[str]:
    """Extract monetary amounts from text."""
    
    money_patterns = [
        r'\$[\d,]+(?:\.\d{2})?',           # $1,000.00
        r'\b\d+\s+dollars?\b',             # 100 dollars
        r'\b(?:USD|US\$)\s*[\d,]+(?:\.\d{2})?\b'  # USD 1,000.00
    ]
    
    amounts = []
    for pattern in money_patterns:
        amounts.extend(re.findall(pattern, text, re.IGNORECASE))
    
    return list(set(amounts))


def extract_legal_citations(text: str) -> List[Dict[str, str]]:
    """Extract and parse legal citations."""
    
    citations = []
    
    # US Supreme Court citations
    scotus_pattern = r'(\d+)\s+U\.S\.\s+(\d+)\s*\((\d{4})\)'
    for match in re.finditer(scotus_pattern, text):
        citations.append({
            "type": "US Supreme Court",
            "volume": match.group(1),
            "page": match.group(2),
            "year": match.group(3),
            "full_citation": match.group(0)
        })
    
    # Federal court citations
    federal_pattern = r'(\d+)\s+F\.(\d+)d\s+(\d+)\s*\(([^)]+)\s+(\d{4})\)'
    for match in re.finditer(federal_pattern, text):
        citations.append({
            "type": "Federal Court",
            "volume": match.group(1),
            "series": f"F.{match.group(2)}d",
            "page": match.group(3),
            "court": match.group(4),
            "year": match.group(5),
            "full_citation": match.group(0)
        })
    
    return citations


def generate_document_summary(text: str) -> str:
    """Generate a brief summary of the document."""
    
    # Simple extractive summary - take first and last sentences of first few paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
    
    if not paragraphs:
        return "Unable to generate summary - insufficient content."
    
    summary_sentences = []
    
    # Take first sentence of first paragraph
    first_para = paragraphs[0]
    first_sentence = first_para.split('.')[0] + '.'
    summary_sentences.append(first_sentence)
    
    # Take key sentences from middle paragraphs
    for para in paragraphs[1:3]:  # Middle paragraphs
        sentences = para.split('.')
        if sentences:
            # Take sentence with legal keywords
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in 
                      ['agreement', 'contract', 'party', 'shall', 'court', 'law']):
                    summary_sentences.append(sentence.strip() + '.')
                    break
    
    # Take last sentence if document is long enough
    if len(paragraphs) > 2:
        last_para = paragraphs[-1]
        last_sentence = last_para.split('.')[-2] + '.' if '.' in last_para else last_para
        summary_sentences.append(last_sentence)
    
    summary = ' '.join(summary_sentences)
    
    # Limit summary length
    if len(summary) > 500:
        summary = summary[:497] + '...'
    
    return summary


def normalize_legal_text(text: str) -> str:
    """Normalize legal text for processing."""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Normalize dashes
    text = text.replace('—', '--').replace('–', '--')
    
    # Remove page numbers and headers/footers (simple patterns)
    text = re.sub(r'\n\s*Page\s+\d+\s*\n', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    return text.strip()


def validate_legal_document(text: str) -> Dict[str, Any]:
    """Validate legal document structure and content."""
    
    validation_result = {
        "is_valid": True,
        "warnings": [],
        "errors": [],
        "score": 100
    }
    
    # Check minimum length
    if len(text) < 100:
        validation_result["errors"].append("Document too short")
        validation_result["is_valid"] = False
        validation_result["score"] -= 30
    
    # Check for basic legal structure
    has_parties = bool(re.search(r'(?:party|plaintiff|defendant|grantor|grantee)', text, re.IGNORECASE))
    if not has_parties:
        validation_result["warnings"].append("No parties identified")
        validation_result["score"] -= 10
    
    # Check for dates
    dates = extract_dates(text)
    if not dates:
        validation_result["warnings"].append("No dates found")
        validation_result["score"] -= 5
    
    # Check for signatures or execution
    has_signature = bool(re.search(r'(?:signature|signed|executed|witness)', text, re.IGNORECASE))
    if not has_signature:
        validation_result["warnings"].append("No signature/execution references found")
        validation_result["score"] -= 10
    
    return validation_result
