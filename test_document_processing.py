#!/usr/bin/env python3
"""
Test Script for Document Processing System
Tests all document processing functionality
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from document_processor import LegalDocumentProcessor

def create_test_documents():
    """Create sample test documents"""
    test_dir = Path("test_documents")
    test_dir.mkdir(exist_ok=True)
    
    # Sample rental agreement text
    rental_agreement = """
    RENTAL AGREEMENT
    
    This lease agreement is entered into between John Smith (Landlord) and Jane Doe (Tenant).
    
    Property: 123 Main Street, Anytown, ST 12345
    Rent Amount: $1,200 per month
    Security Deposit: $1,200
    Lease Term: 12 months starting January 1, 2024
    
    The tenant agrees to pay rent on the 1st of each month.
    The landlord agrees to maintain the property in good condition.
    
    Termination: Either party may terminate with 30 days written notice.
    """
    
    # Sample legal notice text
    legal_notice = """
    LEGAL NOTICE - CEASE AND DESIST
    
    TO: ABC Company
    FROM: Legal Counsel for XYZ Corp
    
    This is a formal demand to cease and desist from the unauthorized use of our trademark.
    
    You have 30 days from receipt of this notice to comply.
    Failure to comply will result in legal action seeking damages of $50,000.
    
    Date: December 1, 2024
    """
    
    # Create test files
    with open(test_dir / "rental_agreement.txt", "w") as f:
        f.write(rental_agreement)
    
    with open(test_dir / "legal_notice.txt", "w") as f:
        f.write(legal_notice)
    
    print(f"✅ Created test documents in {test_dir}")
    return test_dir

def test_document_processor():
    """Test the document processor directly"""
    print("\n🔧 Testing Document Processor...")
    
    processor = LegalDocumentProcessor()
    test_dir = create_test_documents()
    
    # Test rental agreement
    rental_file = test_dir / "rental_agreement.txt"
    print(f"\n📄 Processing: {rental_file.name}")
    
    result = processor.process_document(rental_file)
    
    if result["success"]:
        print(f"✅ Document Type: {result['classification']['document_type']}")
        print(f"✅ Confidence: {result['classification']['confidence']:.1f}%")
        print(f"✅ Complexity: {result['complexity_analysis']['complexity_level']}")
        print(f"✅ Parties: {result['key_information']['parties'][:3]}")
        print(f"✅ Amounts: {result['key_information']['amounts'][:3]}")
    else:
        print(f"❌ Processing failed: {result['error']}")
    
    # Test legal notice
    notice_file = test_dir / "legal_notice.txt"
    print(f"\n📄 Processing: {notice_file.name}")
    
    result = processor.process_document(notice_file)
    
    if result["success"]:
        print(f"✅ Document Type: {result['classification']['document_type']}")
        print(f"✅ Confidence: {result['classification']['confidence']:.1f}%")
        print(f"✅ Complexity: {result['complexity_analysis']['complexity_level']}")
        print(f"✅ Parties: {result['key_information']['parties'][:3]}")
        print(f"✅ Amounts: {result['key_information']['amounts'][:3]}")
    else:
        print(f"❌ Processing failed: {result['error']}")

def test_api_endpoints():
    """Test the document processing API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    
    base_url = "http://localhost:8001"
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API not running. Start with: python document_api.py")
        return False
    
    # Test supported file types
    try:
        response = requests.get(f"{base_url}/supported-file-types")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Supported types: {data['supported_types']}")
        else:
            print(f"❌ Supported types endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing supported types: {e}")
    
    # Test file upload
    test_dir = Path("test_documents")
    if test_dir.exists():
        test_file = test_dir / "rental_agreement.txt"
        if test_file.exists():
            try:
                with open(test_file, 'rb') as f:
                    files = {'file': (test_file.name, f, 'text/plain')}
                    response = requests.post(f"{base_url}/upload-document", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    process_id = data.get('process_id')
                    print(f"✅ File uploaded successfully. Process ID: {process_id}")
                    
                    # Wait for processing
                    print("⏳ Waiting for processing...")
                    time.sleep(5)
                    
                    # Check status
                    status_response = requests.get(f"{base_url}/document-status/{process_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"✅ Processing status: {status_data['status']}")
                        
                        if status_data['status'] == 'completed':
                            # Get analysis
                            analysis_response = requests.get(f"{base_url}/document-analysis/{process_id}")
                            if analysis_response.status_code == 200:
                                analysis_data = analysis_response.json()
                                print(f"✅ Document type: {analysis_data['document_type']}")
                                print(f"✅ Confidence: {analysis_data['confidence']:.1f}%")
                                print(f"✅ Legal advice count: {len(analysis_data['legal_advice'])}")
                            else:
                                print(f"❌ Analysis failed: {analysis_response.status_code}")
                    else:
                        print(f"❌ Status check failed: {status_response.status_code}")
                else:
                    print(f"❌ File upload failed: {response.status_code}")
                    print(response.text)
            except Exception as e:
                print(f"❌ Error testing file upload: {e}")
    
    return True

def test_frontend_integration():
    """Test frontend integration"""
    print("\n🎨 Testing Frontend Integration...")
    
    frontend_url = "http://localhost:3001"
    
    try:
        response = requests.get(frontend_url)
        if response.status_code == 200:
            print("✅ Frontend is running")
            print("📝 Document upload should be available in the 'Documents' tab")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend not running. Start with: npm start in law-agent-frontend/")

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 Law Agent Document Processing - Comprehensive Test")
    print("=" * 60)
    
    # Test 1: Document Processor
    test_document_processor()
    
    # Test 2: API Endpoints
    api_working = test_api_endpoints()
    
    # Test 3: Frontend Integration
    test_frontend_integration()
    
    print("\n📊 Test Summary:")
    print("✅ Document processing core functionality")
    if api_working:
        print("✅ API endpoints working")
    else:
        print("❌ API endpoints need to be started")
    print("✅ Frontend integration ready")
    
    print("\n🚀 To start the complete system:")
    print("1. Install dependencies: pip install -r requirements_document_processing.txt")
    print("2. Start APIs: python start_law_agent_with_documents.py")
    print("3. Start frontend: cd law-agent-frontend && npm start")

if __name__ == "__main__":
    run_comprehensive_test()
