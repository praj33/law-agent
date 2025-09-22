import React, { useState, useCallback, useRef } from 'react';
import {
  Upload,
  File,
  FileText,
  Image,
  CheckCircle,
  XCircle,
  Eye,
  Trash2,
  Clock,
  FileCheck,
  Loader,
  Sparkles,
  Scale,
  Shield
} from 'lucide-react';

interface UploadedFile {
  id: string;
  file: File;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  processId?: string;
  analysis?: DocumentAnalysis;
  error?: string;
}

interface DocumentAnalysis {
  document_type: string;
  confidence: number;
  key_information: {
    parties: string[];
    dates: string[];
    amounts: string[];
    key_sections: Record<string, string>;
  };
  complexity_analysis: {
    complexity_level: string;
    word_count: number;
    flesch_reading_ease: number;
  };
  legal_advice: string[];
}

const DocumentUpload: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const supportedTypes = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg'];
  const maxFileSize = 50 * 1024 * 1024; // 50MB

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    handleFiles(files);
  }, []);

  const handleFiles = async (files: File[]) => {
    for (const file of files) {
      // Validate file
      const validation = validateFile(file);
      if (!validation.valid) {
        alert(`Error with ${file.name}: ${validation.error}`);
        continue;
      }

      // Create upload entry
      const uploadId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
      const uploadedFile: UploadedFile = {
        id: uploadId,
        file,
        status: 'uploading',
        progress: 0
      };

      setUploadedFiles(prev => [...prev, uploadedFile]);

      // Upload file
      try {
        await uploadFile(uploadedFile);
      } catch (error) {
        console.error('Upload error:', error);
        updateFileStatus(uploadId, 'failed', 0, undefined, String(error));
      }
    }
  };

  const validateFile = (file: File): { valid: boolean; error?: string } => {
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!supportedTypes.includes(fileExt)) {
      return { valid: false, error: `Unsupported file type. Supported: ${supportedTypes.join(', ')}` };
    }
    
    if (file.size > maxFileSize) {
      return { valid: false, error: 'File too large (max 50MB)' };
    }
    
    return { valid: true };
  };

  const uploadFile = async (uploadedFile: UploadedFile) => {
    const formData = new FormData();
    formData.append('file', uploadedFile.file);

    try {
      // Upload file
      const uploadResponse = await fetch('http://localhost:8001/upload-document', {
        method: 'POST',
        body: formData
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.statusText}`);
      }

      const uploadResult = await uploadResponse.json();
      const processId = uploadResult.process_id;

      updateFileStatus(uploadedFile.id, 'processing', 50, processId);

      // Poll for processing completion
      await pollProcessingStatus(uploadedFile.id, processId);

    } catch (error) {
      throw error;
    }
  };

  const pollProcessingStatus = async (fileId: string, processId: string) => {
    const maxAttempts = 60; // 5 minutes max
    let attempts = 0;

    const poll = async () => {
      try {
        const statusResponse = await fetch(`http://localhost:8001/document-status/${processId}`);
        const status = await statusResponse.json();

        updateFileStatus(fileId, status.status, status.progress);

        if (status.status === 'completed') {
          // Get detailed analysis
          const analysisResponse = await fetch(`http://localhost:8001/document-analysis/${processId}`);
          const analysis = await analysisResponse.json();
          
          updateFileStatus(fileId, 'completed', 100, processId, undefined, analysis);
        } else if (status.status === 'failed') {
          updateFileStatus(fileId, 'failed', 0, processId, status.error);
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          updateFileStatus(fileId, 'failed', 0, processId, 'Processing timeout');
        }
      } catch (error) {
        updateFileStatus(fileId, 'failed', 0, processId, String(error));
      }
    };

    poll();
  };

  const updateFileStatus = (
    fileId: string, 
    status: UploadedFile['status'], 
    progress: number, 
    processId?: string, 
    error?: string,
    analysis?: DocumentAnalysis
  ) => {
    setUploadedFiles(prev => prev.map(file => 
      file.id === fileId 
        ? { ...file, status, progress, processId, error, analysis }
        : file
    ));
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
    if (selectedFile?.id === fileId) {
      setSelectedFile(null);
    }
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf':
        return <FileText className="h-6 w-6 text-red-500" />;
      case 'docx':
      case 'doc':
        return <FileText className="h-6 w-6 text-blue-500" />;
      case 'png':
      case 'jpg':
      case 'jpeg':
        return <Image className="h-6 w-6 text-green-500" />;
      default:
        return <File className="h-6 w-6 text-gray-500" />;
    }
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getDocumentTypeColor = (docType: string) => {
    const colors = {
      'rental_agreement': 'bg-blue-100 text-blue-800',
      'employment_contract': 'bg-green-100 text-green-800',
      'legal_notice': 'bg-red-100 text-red-800',
      'contract': 'bg-purple-100 text-purple-800',
      'court_document': 'bg-yellow-100 text-yellow-800',
      'will_testament': 'bg-indigo-100 text-indigo-800'
    };
    return colors[docType as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <Upload className="h-8 w-8 text-blue-500" />
          <h2 className="text-3xl font-bold text-white">Document Analysis</h2>
          <Scale className="h-8 w-8 text-blue-500" />
        </div>
        <p className="text-gray-300 text-lg">Upload legal documents for AI-powered analysis and classification</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Area */}
        <div className="space-y-6">
          {/* Drag & Drop Zone */}
          <div
            className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
              isDragOver
                ? 'border-blue-400 bg-blue-50/10 scale-105'
                : 'border-gray-600 bg-white/5 hover:border-gray-500'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept={supportedTypes.join(',')}
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="p-4 bg-blue-500/20 rounded-full">
                  <Upload className="h-12 w-12 text-blue-400" />
                </div>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  Drop files here or click to browse
                </h3>
                <p className="text-gray-400 mb-4">
                  Supported: PDF, DOCX, DOC, TXT, PNG, JPG (Max 50MB)
                </p>
                
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105"
                >
                  Select Files
                </button>
              </div>
            </div>
          </div>

          {/* File List */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
              <FileCheck className="h-5 w-5" />
              <span>Uploaded Documents ({uploadedFiles.length})</span>
            </h3>
            
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  className={`bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20 transition-all duration-300 ${
                    selectedFile?.id === file.id ? 'ring-2 ring-blue-500' : 'hover:bg-white/15'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    {getFileIcon(file.file.name)}
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-white font-medium truncate">
                          {file.file.name}
                        </p>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(file.status)}
                          <button
                            onClick={() => removeFile(file.id)}
                            className="text-gray-400 hover:text-red-400 transition-colors"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-sm text-gray-400">
                          {(file.file.size / 1024 / 1024).toFixed(2)} MB
                        </span>
                        
                        {file.analysis && (
                          <button
                            onClick={() => setSelectedFile(file)}
                            className="text-blue-400 hover:text-blue-300 text-sm font-medium"
                          >
                            View Analysis
                          </button>
                        )}
                      </div>
                      
                      {/* Progress Bar */}
                      {file.status !== 'completed' && file.status !== 'failed' && (
                        <div className="mt-2">
                          <div className="bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${file.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                      
                      {/* Status Message */}
                      {file.error && (
                        <p className="text-red-400 text-sm mt-2">{file.error}</p>
                      )}
                      
                      {file.analysis && (
                        <div className="mt-2 flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDocumentTypeColor(file.analysis.document_type)}`}>
                            {file.analysis.document_type.replace('_', ' ').toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-400">
                            {file.analysis.confidence.toFixed(1)}% confidence
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              {uploadedFiles.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No documents uploaded yet</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Analysis Panel */}
        <div className="space-y-6">
          {selectedFile && selectedFile.analysis ? (
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              {/* Analysis Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <Eye className="h-6 w-6 text-blue-400" />
                  <h3 className="text-xl font-semibold text-white">Document Analysis</h3>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <XCircle className="h-5 w-5" />
                </button>
              </div>

              {/* Document Info */}
              <div className="mb-6">
                <div className="flex items-center space-x-3 mb-3">
                  {getFileIcon(selectedFile.file.name)}
                  <div>
                    <h4 className="text-white font-medium">{selectedFile.file.name}</h4>
                    <p className="text-gray-400 text-sm">
                      {(selectedFile.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDocumentTypeColor(selectedFile.analysis.document_type)}`}>
                    {selectedFile.analysis.document_type.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-300">
                    Confidence: {selectedFile.analysis.confidence.toFixed(1)}%
                  </span>
                  <span className="text-sm text-gray-300">
                    Complexity: {selectedFile.analysis.complexity_analysis.complexity_level}
                  </span>
                </div>
              </div>

              {/* Key Information */}
              <div className="space-y-4">
                {/* Parties */}
                {selectedFile.analysis.key_information.parties.length > 0 && (
                  <div>
                    <h5 className="text-white font-medium mb-2 flex items-center space-x-2">
                      <Shield className="h-4 w-4 text-blue-400" />
                      <span>Parties Involved</span>
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {selectedFile.analysis.key_information.parties.slice(0, 5).map((party, index) => (
                        <span key={index} className="bg-blue-500/20 text-blue-200 px-2 py-1 rounded-lg text-sm">
                          {party}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Important Dates */}
                {selectedFile.analysis.key_information.dates.length > 0 && (
                  <div>
                    <h5 className="text-white font-medium mb-2 flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-green-400" />
                      <span>Important Dates</span>
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {selectedFile.analysis.key_information.dates.slice(0, 5).map((date, index) => (
                        <span key={index} className="bg-green-500/20 text-green-200 px-2 py-1 rounded-lg text-sm">
                          {date}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Monetary Amounts */}
                {selectedFile.analysis.key_information.amounts.length > 0 && (
                  <div>
                    <h5 className="text-white font-medium mb-2 flex items-center space-x-2">
                      <Sparkles className="h-4 w-4 text-yellow-400" />
                      <span>Monetary Amounts</span>
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {selectedFile.analysis.key_information.amounts.slice(0, 5).map((amount, index) => (
                        <span key={index} className="bg-yellow-500/20 text-yellow-200 px-2 py-1 rounded-lg text-sm">
                          {amount}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Document Stats */}
                <div className="bg-white/5 rounded-xl p-4">
                  <h5 className="text-white font-medium mb-3">Document Statistics</h5>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Word Count:</span>
                      <span className="text-white ml-2">{selectedFile.analysis.complexity_analysis.word_count}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Reading Ease:</span>
                      <span className="text-white ml-2">{selectedFile.analysis.complexity_analysis.flesch_reading_ease.toFixed(1)}</span>
                    </div>
                  </div>
                </div>

                {/* Legal Advice */}
                <div>
                  <h5 className="text-white font-medium mb-3 flex items-center space-x-2">
                    <Scale className="h-4 w-4 text-purple-400" />
                    <span>Legal Recommendations</span>
                  </h5>
                  <div className="space-y-2">
                    {selectedFile.analysis.legal_advice.slice(0, 5).map((advice, index) => (
                      <div key={index} className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3">
                        <p className="text-purple-200 text-sm">{advice}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Empty State */
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 text-center">
              <div className="space-y-4">
                <div className="flex justify-center">
                  <div className="p-4 bg-gray-500/20 rounded-full">
                    <FileText className="h-12 w-12 text-gray-400" />
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">No Document Selected</h3>
                  <p className="text-gray-400">
                    Upload and process a document to see detailed analysis here
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Features Info */}
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-yellow-400" />
              <span>AI Analysis Features</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">Document Classification</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">Key Information Extraction</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">Legal Advice Generation</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">Complexity Analysis</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">OCR Text Extraction</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-indigo-400 rounded-full"></div>
                <span className="text-gray-300 text-sm">Multi-format Support</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;
