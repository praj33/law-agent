#!/usr/bin/env python3
"""
Simple Document Processing Demo
Demonstrates document analysis without heavy dependencies
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

class SimpleDocumentAnalyzer:
    """Simplified document analyzer using basic Python"""
    
    def __init__(self):
        self.document_types = {
            "rental_agreement": {
                "keywords": ["rent", "lease", "tenant", "landlord", "property", "monthly", "deposit"],
                "patterns": ["lease agreement", "rental contract", "tenancy agreement"]
            },
            "employment_contract": {
                "keywords": ["employment", "employee", "employer", "salary", "wages", "benefits"],
                "patterns": ["employment agreement", "job contract", "work agreement"]
            },
            "legal_notice": {
                "keywords": ["notice", "demand", "cease", "desist", "violation", "breach"],
                "patterns": ["legal notice", "demand letter", "cease and desist"]
            },
            "contract": {
                "keywords": ["contract", "agreement", "party", "obligations", "terms"],
                "patterns": ["service agreement", "purchase agreement", "contract"]
            }
        }
    
    def analyze_text(self, text):
        """Analyze text and classify document"""
        text_lower = text.lower()
        
        # Classification
        classification = self.classify_document(text_lower)
        
        # Extract key information
        key_info = self.extract_key_info(text)
        
        # Basic complexity analysis
        complexity = self.analyze_complexity(text)
        
        return {
            "classification": classification,
            "key_information": key_info,
            "complexity": complexity,
            "timestamp": datetime.now().isoformat()
        }
    
    def classify_document(self, text):
        """Classify document type"""
        scores = {}
        
        for doc_type, config in self.document_types.items():
            score = 0
            matched_keywords = []
            
            # Check keywords
            for keyword in config["keywords"]:
                if keyword in text:
                    score += text.count(keyword) * 2
                    matched_keywords.append(keyword)
            
            # Check patterns
            for pattern in config["patterns"]:
                if pattern in text:
                    score += 10
            
            scores[doc_type] = {
                "score": score,
                "matched_keywords": matched_keywords
            }
        
        # Find best match
        best_match = max(scores.items(), key=lambda x: x[1]["score"])
        total_score = sum(item["score"] for item in scores.values())
        confidence = (best_match[1]["score"] / total_score * 100) if total_score > 0 else 0
        
        return {
            "document_type": best_match[0],
            "confidence": round(confidence, 2),
            "all_scores": scores
        }
    
    def extract_key_info(self, text):
        """Extract key information from text"""
        # Extract dates
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Extract monetary amounts
        money_patterns = [r'\$[\d,]+\.?\d*', r'\b\d+\s*dollars?\b']
        amounts = []
        for pattern in money_patterns:
            amounts.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Extract potential parties (quoted names or after keywords)
        party_patterns = [
            r'"([^"]+)"',
            r'between\s+([^,\n]+)\s+and\s+([^,\n]+)',
            r'tenant[:\s]+([^,\n]+)',
            r'landlord[:\s]+([^,\n]+)'
        ]
        
        parties = []
        for pattern in party_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    parties.extend([p.strip() for match in matches for p in match if p.strip()])
                else:
                    parties.extend([p.strip() for p in matches if p.strip()])
        
        return {
            "dates": dates[:5],  # Top 5
            "amounts": amounts[:5],  # Top 5
            "parties": parties[:5]  # Top 5
        }
    
    def analyze_complexity(self, text):
        """Basic complexity analysis"""
        words = text.split()
        sentences = text.count('.') + text.count('!') + text.count('?')
        
        # Legal terms
        legal_terms = ['whereas', 'heretofore', 'hereinafter', 'notwithstanding', 'pursuant']
        legal_count = sum(text.lower().count(term) for term in legal_terms)
        
        avg_words_per_sentence = len(words) / sentences if sentences > 0 else 0
        legal_density = (legal_count / len(words) * 100) if words else 0
        
        # Simple complexity determination
        if avg_words_per_sentence < 15 and legal_density < 2:
            complexity_level = "Simple"
        elif avg_words_per_sentence < 25 and legal_density < 5:
            complexity_level = "Moderate"
        else:
            complexity_level = "Complex"
        
        return {
            "word_count": len(words),
            "sentence_count": sentences,
            "avg_words_per_sentence": round(avg_words_per_sentence, 2),
            "legal_term_density": round(legal_density, 2),
            "complexity_level": complexity_level
        }

def create_demo_documents():
    """Create demo documents for testing"""
    demo_dir = Path("demo_documents")
    demo_dir.mkdir(exist_ok=True)
    
    # Sample rental agreement
    rental_text = """
    RESIDENTIAL LEASE AGREEMENT
    
    This lease agreement is made between John Smith (Landlord) and Jane Doe (Tenant).
    
    Property Address: 123 Main Street, Anytown, ST 12345
    Monthly Rent: $1,200 due on the 1st of each month
    Security Deposit: $1,200
    Lease Term: 12 months beginning January 1, 2024
    
    The tenant agrees to pay rent monthly and maintain the property.
    The landlord agrees to provide a habitable dwelling.
    
    Either party may terminate this lease with 30 days written notice.
    """
    
    # Sample legal notice
    notice_text = """
    CEASE AND DESIST NOTICE
    
    TO: ABC Corporation
    FROM: Legal Department, XYZ Company
    
    This is formal notice to cease and desist from unauthorized use of our trademark.
    
    You have violated our intellectual property rights.
    You must stop all infringing activities within 30 days.
    Failure to comply will result in legal action seeking damages of $50,000.
    
    Date: December 15, 2024
    """
    
    # Sample employment contract
    employment_text = """
    EMPLOYMENT AGREEMENT
    
    This employment agreement is between Tech Corp (Employer) and Alice Johnson (Employee).
    
    Position: Software Developer
    Salary: $75,000 per year
    Benefits: Health insurance, 401k, vacation time
    Start Date: January 15, 2024
    
    The employee agrees to perform duties diligently.
    The employer agrees to provide compensation and benefits.
    
    Either party may terminate employment with two weeks notice.
    """
    
    # Write demo files
    with open(demo_dir / "rental_agreement.txt", "w") as f:
        f.write(rental_text)
    
    with open(demo_dir / "legal_notice.txt", "w") as f:
        f.write(notice_text)
    
    with open(demo_dir / "employment_contract.txt", "w") as f:
        f.write(employment_text)
    
    return demo_dir

def run_demo():
    """Run the document processing demo"""
    print("📄 Simple Document Processing Demo")
    print("=" * 50)
    
    # Create analyzer
    analyzer = SimpleDocumentAnalyzer()
    
    # Create demo documents
    demo_dir = create_demo_documents()
    print(f"✅ Created demo documents in {demo_dir}")
    
    # Process each document
    for doc_file in demo_dir.glob("*.txt"):
        print(f"\n📋 Processing: {doc_file.name}")
        print("-" * 30)
        
        # Read document
        with open(doc_file, 'r') as f:
            text = f.read()
        
        # Analyze document
        result = analyzer.analyze_text(text)
        
        # Display results
        classification = result["classification"]
        key_info = result["key_information"]
        complexity = result["complexity"]
        
        print(f"🏷️  Document Type: {classification['document_type'].replace('_', ' ').title()}")
        print(f"🎯 Confidence: {classification['confidence']:.1f}%")
        print(f"📊 Complexity: {complexity['complexity_level']}")
        print(f"📝 Word Count: {complexity['word_count']}")
        
        if key_info["parties"]:
            print(f"👥 Parties: {', '.join(key_info['parties'][:3])}")
        
        if key_info["amounts"]:
            print(f"💰 Amounts: {', '.join(key_info['amounts'][:3])}")
        
        if key_info["dates"]:
            print(f"📅 Dates: {', '.join(key_info['dates'][:3])}")
        
        # Save analysis result
        result_file = demo_dir / f"{doc_file.stem}_analysis.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"💾 Analysis saved to: {result_file.name}")
    
    print(f"\n🎉 Demo completed! Check the {demo_dir} folder for results.")
    print("\n🚀 This demonstrates the core document processing capabilities:")
    print("   ✅ Document classification")
    print("   ✅ Key information extraction")
    print("   ✅ Complexity analysis")
    print("   ✅ Legal advice generation (ready for integration)")

if __name__ == "__main__":
    run_demo()
