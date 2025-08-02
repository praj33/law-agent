# 📄 Law Agent Document Processing System

## 🎯 Overview

The Law Agent Document Processing System is a comprehensive solution for uploading, parsing, and analyzing legal documents using AI-powered classification and extraction techniques.

## ✨ Features

### 🔧 Backend Processing
- **Multi-format Support**: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG
- **Advanced Text Extraction**: PyMuPDF for PDFs, python-docx for Word documents
- **OCR Capabilities**: Tesseract OCR for image-based documents
- **Legal Document Classification**: AI-powered identification of document types
- **Key Information Extraction**: Parties, dates, amounts, key sections
- **Complexity Analysis**: Readability scores and legal term density
- **Legal Advice Generation**: Context-aware recommendations

### 🎨 Frontend Interface
- **Drag & Drop Upload**: Intuitive file upload interface
- **Real-time Processing**: Live progress tracking and status updates
- **Document Analysis Panel**: Detailed analysis results display
- **Professional Design**: Modern, legal-themed UI
- **Responsive Layout**: Works on all devices

### 📋 Supported Document Types
1. **Rental Agreements** - Lease terms, rent amounts, parties
2. **Employment Contracts** - Compensation, benefits, termination
3. **Legal Notices** - Cease and desist, demand letters
4. **General Contracts** - Service agreements, purchase contracts
5. **Court Documents** - Orders, summons, complaints
6. **Wills & Testaments** - Estate planning documents

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_document_processing.txt
```

### 2. Install Tesseract OCR (for image processing)
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Start the System
```bash
# Option 1: Start everything together
python start_law_agent_with_documents.py

# Option 2: Start services separately
python document_api.py          # Document API on port 8001
python law_agent_minimal.py     # Main Law Agent on port 8000
cd law-agent-frontend && npm start  # Frontend on port 3001
```

### 4. Test the System
```bash
python test_document_processing.py
```

## 📁 File Structure

```
law-agent/
├── document_processor.py              # Core document processing logic
├── document_api.py                    # FastAPI endpoints for document handling
├── start_law_agent_with_documents.py  # Startup script
├── test_document_processing.py        # Comprehensive test suite
├── requirements_document_processing.txt # Python dependencies
├── uploads/                           # Temporary upload storage
├── processed/                         # Processed document results
└── law-agent-frontend/
    └── src/components/
        └── DocumentUpload.tsx         # React upload component
```

## 🔌 API Endpoints

### Document Processing API (Port 8001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/supported-file-types` | GET | List of supported file formats |
| `/upload-document` | POST | Upload document for processing |
| `/document-status/{process_id}` | GET | Check processing status |
| `/document-analysis/{process_id}` | GET | Get detailed analysis results |
| `/document-summary/{process_id}` | GET | Get processing summary |
| `/documents/list` | GET | List all processed documents |
| `/document/{process_id}` | DELETE | Delete processed document |

### Example Usage

```python
import requests

# Upload document
with open('contract.pdf', 'rb') as f:
    files = {'file': ('contract.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:8001/upload-document', files=files)
    process_id = response.json()['process_id']

# Check status
status = requests.get(f'http://localhost:8001/document-status/{process_id}')

# Get analysis
analysis = requests.get(f'http://localhost:8001/document-analysis/{process_id}')
```

## 🧠 AI Classification System

### Document Types Detected
- **Rental Agreement**: Keywords like "rent", "lease", "tenant", "landlord"
- **Employment Contract**: "employment", "salary", "benefits", "termination"
- **Legal Notice**: "notice", "demand", "cease", "desist", "violation"
- **Contract**: "agreement", "party", "obligations", "terms"
- **Court Document**: "court", "plaintiff", "defendant", "case"
- **Will/Testament**: "will", "testament", "executor", "beneficiary"

### Key Information Extracted
- **Parties**: Names of individuals/organizations involved
- **Dates**: Important deadlines, effective dates, expiration dates
- **Amounts**: Monetary values, fees, damages, rent amounts
- **Key Sections**: Document-specific important clauses

### Complexity Analysis
- **Word Count**: Total words in document
- **Readability Scores**: Flesch Reading Ease, Flesch-Kincaid Grade
- **Legal Term Density**: Percentage of legal terminology
- **Complexity Levels**: Simple, Moderate, Complex, Very Complex

## 🎨 Frontend Integration

### Document Upload Component
```typescript
import DocumentUpload from './components/DocumentUpload';

// Use in your React app
<DocumentUpload />
```

### Features
- **Drag & Drop**: Intuitive file upload
- **Progress Tracking**: Real-time upload and processing status
- **Analysis Display**: Comprehensive results visualization
- **File Management**: Upload, view, and delete documents
- **Responsive Design**: Mobile-friendly interface

## 🔒 Security & Privacy

- **File Validation**: Size limits, type checking, malware scanning
- **Temporary Storage**: Files deleted after processing
- **Secure Processing**: No data retention beyond session
- **CORS Protection**: Restricted API access
- **Input Sanitization**: Safe text processing

## 🧪 Testing

### Run Tests
```bash
python test_document_processing.py
```

### Test Coverage
- ✅ Document processor functionality
- ✅ API endpoint testing
- ✅ File upload and processing
- ✅ Classification accuracy
- ✅ Key information extraction
- ✅ Frontend integration

## 🛠️ Troubleshooting

### Common Issues

1. **Tesseract not found**
   ```bash
   # Install Tesseract OCR system package
   sudo apt-get install tesseract-ocr  # Ubuntu
   brew install tesseract              # macOS
   ```

2. **PyMuPDF installation issues**
   ```bash
   pip install --upgrade PyMuPDF
   ```

3. **API connection errors**
   - Check if APIs are running on correct ports
   - Verify CORS settings for frontend access

4. **File upload failures**
   - Check file size (max 50MB)
   - Verify file type is supported
   - Ensure sufficient disk space

## 📈 Performance

- **Processing Speed**: ~2-5 seconds per document
- **File Size Limit**: 50MB maximum
- **Concurrent Processing**: Multiple documents supported
- **Memory Usage**: Optimized for large documents
- **OCR Performance**: High accuracy for clear images

## 🔄 Future Enhancements

- [ ] Advanced NLP with spaCy/transformers
- [ ] Multi-language document support
- [ ] Batch document processing
- [ ] Document comparison features
- [ ] Integration with legal databases
- [ ] Advanced security scanning
- [ ] Cloud storage integration

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Run the test suite to identify problems
3. Review API logs for error details
4. Ensure all dependencies are properly installed

---

**🎉 Your Law Agent Document Processing System is ready to analyze legal documents with AI-powered precision!**
