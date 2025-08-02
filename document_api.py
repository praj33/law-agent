#!/usr/bin/env python3
"""
Document Upload and Processing API
FastAPI endpoints for legal document analysis
"""

import os
import sys
import json
import uuid
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import our document processor
from document_processor import LegalDocumentProcessor

# Initialize FastAPI app
app = FastAPI(
    title="Law Agent Document Processing API",
    description="Advanced legal document upload, parsing, and classification system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize document processor
doc_processor = LegalDocumentProcessor()

# Pydantic models
class DocumentUploadResponse(BaseModel):
    success: bool
    process_id: Optional[str] = None
    message: str
    file_info: Optional[Dict[str, Any]] = None

class DocumentAnalysisResponse(BaseModel):
    success: bool
    process_id: str
    document_type: str
    confidence: float
    key_information: Dict[str, Any]
    complexity_analysis: Dict[str, Any]
    legal_advice: List[str]

class DocumentSummaryResponse(BaseModel):
    success: bool
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Global storage for processing status
processing_status = {}

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Law Agent Document Processing API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload-document",
            "status": "/document-status/{process_id}",
            "analysis": "/document-analysis/{process_id}",
            "summary": "/document-summary/{process_id}",
            "supported_types": "/supported-file-types"
        }
    }

@app.get("/supported-file-types")
async def get_supported_file_types():
    """Get list of supported file types"""
    return {
        "supported_types": list(doc_processor.supported_types.keys()),
        "mime_types": doc_processor.supported_types,
        "max_file_size": "50MB",
        "features": [
            "PDF text extraction with OCR",
            "DOCX document parsing",
            "Image OCR processing",
            "Legal document classification",
            "Key information extraction",
            "Complexity analysis"
        ]
    }

@app.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process legal document"""
    try:
        # Generate unique process ID
        process_id = str(uuid.uuid4())
        
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in doc_processor.supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported types: {list(doc_processor.supported_types.keys())}"
            )
        
        # Save uploaded file
        upload_path = doc_processor.upload_dir / f"{process_id}_{file.filename}"
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize processing status
        processing_status[process_id] = {
            "status": "uploaded",
            "filename": file.filename,
            "upload_time": datetime.now().isoformat(),
            "file_size": upload_path.stat().st_size
        }
        
        # Start background processing
        background_tasks.add_task(process_document_background, process_id, upload_path)
        
        return DocumentUploadResponse(
            success=True,
            process_id=process_id,
            message="Document uploaded successfully. Processing started.",
            file_info={
                "filename": file.filename,
                "size": upload_path.stat().st_size,
                "type": file_ext
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_document_background(process_id: str, file_path: Path):
    """Background task for document processing"""
    try:
        # Update status
        processing_status[process_id]["status"] = "processing"
        processing_status[process_id]["start_time"] = datetime.now().isoformat()
        
        # Process document
        result = doc_processor.process_document(file_path)
        
        if result["success"]:
            processing_status[process_id]["status"] = "completed"
            processing_status[process_id]["result"] = result
        else:
            processing_status[process_id]["status"] = "failed"
            processing_status[process_id]["error"] = result["error"]
        
        processing_status[process_id]["end_time"] = datetime.now().isoformat()
        
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()
            
    except Exception as e:
        processing_status[process_id]["status"] = "failed"
        processing_status[process_id]["error"] = str(e)
        processing_status[process_id]["end_time"] = datetime.now().isoformat()

@app.get("/document-status/{process_id}")
async def get_document_status(process_id: str):
    """Get document processing status"""
    if process_id not in processing_status:
        raise HTTPException(status_code=404, detail="Process ID not found")
    
    status_info = processing_status[process_id].copy()
    
    # Add progress percentage
    if status_info["status"] == "uploaded":
        status_info["progress"] = 10
    elif status_info["status"] == "processing":
        status_info["progress"] = 50
    elif status_info["status"] == "completed":
        status_info["progress"] = 100
    elif status_info["status"] == "failed":
        status_info["progress"] = 0
    
    return status_info

@app.get("/document-analysis/{process_id}", response_model=DocumentAnalysisResponse)
async def get_document_analysis(process_id: str):
    """Get detailed document analysis"""
    if process_id not in processing_status:
        raise HTTPException(status_code=404, detail="Process ID not found")
    
    status_info = processing_status[process_id]
    
    if status_info["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Document processing not completed. Current status: {status_info['status']}"
        )
    
    result = status_info["result"]
    
    # Generate legal advice based on document type
    legal_advice = generate_legal_advice(
        result["classification"]["document_type"],
        result["key_information"],
        result["complexity_analysis"]
    )
    
    return DocumentAnalysisResponse(
        success=True,
        process_id=process_id,
        document_type=result["classification"]["document_type"],
        confidence=result["classification"]["confidence"],
        key_information=result["key_information"],
        complexity_analysis=result["complexity_analysis"],
        legal_advice=legal_advice
    )

@app.get("/document-summary/{process_id}", response_model=DocumentSummaryResponse)
async def get_document_summary(process_id: str):
    """Get document processing summary"""
    try:
        summary_result = doc_processor.get_processing_summary(process_id)
        
        if summary_result["success"]:
            return DocumentSummaryResponse(
                success=True,
                summary=summary_result["summary"]
            )
        else:
            return DocumentSummaryResponse(
                success=False,
                error=summary_result["error"]
            )
            
    except Exception as e:
        return DocumentSummaryResponse(
            success=False,
            error=str(e)
        )

@app.delete("/document/{process_id}")
async def delete_document(process_id: str):
    """Delete processed document and its data"""
    try:
        # Remove from processing status
        if process_id in processing_status:
            del processing_status[process_id]
        
        # Remove processed file
        result_file = doc_processor.processed_dir / f"{process_id}.json"
        if result_file.exists():
            result_file.unlink()
        
        return {"success": True, "message": "Document data deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/list")
async def list_processed_documents():
    """List all processed documents"""
    try:
        documents = []
        
        for process_id, status_info in processing_status.items():
            if status_info["status"] == "completed":
                summary = doc_processor.get_processing_summary(process_id)
                if summary["success"]:
                    documents.append({
                        "process_id": process_id,
                        "filename": status_info["filename"],
                        "upload_time": status_info["upload_time"],
                        "document_type": summary["summary"]["document_type"],
                        "confidence": summary["summary"]["confidence"]
                    })
        
        return {
            "success": True,
            "count": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_legal_advice(document_type: str, key_info: Dict[str, Any], complexity: Dict[str, Any]) -> List[str]:
    """Generate legal advice based on document analysis"""
    advice = []
    
    # General advice based on document type
    if document_type == "rental_agreement":
        advice.extend([
            "Review the lease term and renewal conditions carefully",
            "Understand your rights regarding security deposits",
            "Check for any unusual clauses or restrictions",
            "Verify the rent amount and payment schedule",
            "Understand the termination and eviction procedures"
        ])
    elif document_type == "employment_contract":
        advice.extend([
            "Review compensation structure and benefits package",
            "Understand termination clauses and severance terms",
            "Check for non-compete and confidentiality agreements",
            "Verify job responsibilities and reporting structure",
            "Review dispute resolution procedures"
        ])
    elif document_type == "legal_notice":
        advice.extend([
            "Take immediate action - legal notices have strict deadlines",
            "Consult with an attorney as soon as possible",
            "Gather all relevant documents and evidence",
            "Do not ignore the notice - respond appropriately",
            "Consider negotiation or settlement options"
        ])
    elif document_type == "contract":
        advice.extend([
            "Review all terms and conditions thoroughly",
            "Understand payment terms and deadlines",
            "Check for termination and breach clauses",
            "Verify the scope of work or services",
            "Consider having an attorney review complex contracts"
        ])
    
    # Advice based on complexity
    if complexity.get("complexity_level") in ["Complex", "Very Complex"]:
        advice.append("This document is complex - consider professional legal review")
    
    # Advice based on key information
    if key_info.get("amounts"):
        advice.append("Pay special attention to all monetary amounts and payment terms")
    
    if key_info.get("dates"):
        advice.append("Note all important dates and deadlines mentioned in the document")
    
    return advice[:10]  # Limit to top 10 pieces of advice

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
