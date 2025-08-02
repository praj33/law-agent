// Shared types for the Law Agent application

export interface TimelineEvent {
  id: string;
  title: string;
  description: string;
  date: string;
  type: 'filing' | 'hearing' | 'decision' | 'deadline' | 'motion' | 'discovery';
  status: 'completed' | 'pending' | 'upcoming' | 'overdue';
  participants?: string[];
  documents?: string[];
  importance: 'low' | 'medium' | 'high' | 'critical';
}

export interface GlossaryTerm {
  term: string;
  definition: string;
  category: string;
  examples?: string[];
  relatedTerms?: string[];
  importance?: 'basic' | 'intermediate' | 'advanced';
}

export interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  steps?: string[];
  timeline?: TimelineEvent[];
  glossaryTerms?: GlossaryTerm[];
  visualData?: any;
}

export interface LegalDomain {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  caseCount: number;
}

export interface CourtJurisdiction {
  id: string;
  name: string;
  type: 'federal' | 'state' | 'local';
  level: number;
  caseCount: number;
  description: string;
  parentId?: string;
}

export interface LegalCase {
  id: string;
  title: string;
  description: string;
  status: 'active' | 'closed' | 'pending';
  priority: 'low' | 'medium' | 'high' | 'critical';
  timeline: TimelineEvent[];
  documents: string[];
  participants: string[];
  jurisdiction: string;
  domain: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface AIResponse {
  response: string;
  confidence: number;
  steps?: string[];
  timeline?: TimelineEvent[];
  glossaryTerms?: GlossaryTerm[];
  recommendations?: string[];
  visualData?: any;
  metadata?: {
    processingTime: number;
    sources: string[];
    jurisdiction: string;
    complexity: 'low' | 'medium' | 'high';
  };
}

export interface SessionData {
  sessionId: string;
  userId?: string;
  messages: Message[];
  context: {
    jurisdiction: string;
    legalDomain: string;
    caseType?: string;
  };
  createdAt: Date;
  lastActivity: Date;
}
