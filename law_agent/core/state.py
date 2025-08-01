"""Agent state management for the Law Agent system."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class UserType(str, Enum):
    """Types of users in the system."""
    COMMON_PERSON = "common_person"
    LAW_FIRM = "law_firm"
    LEGAL_PROFESSIONAL = "legal_professional"


class LegalDomain(str, Enum):
    """Legal domains for classification."""
    FAMILY_LAW = "family_law"
    CRIMINAL_LAW = "criminal_law"
    CORPORATE_LAW = "corporate_law"
    PROPERTY_LAW = "property_law"
    EMPLOYMENT_LAW = "employment_law"
    IMMIGRATION_LAW = "immigration_law"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    TAX_LAW = "tax_law"
    CONSTITUTIONAL_LAW = "constitutional_law"
    CONTRACT_LAW = "contract_law"
    TORT_LAW = "tort_law"
    BANKRUPTCY_LAW = "bankruptcy_law"
    ENVIRONMENTAL_LAW = "environmental_law"
    HEALTHCARE_LAW = "healthcare_law"
    UNKNOWN = "unknown"


class InteractionType(str, Enum):
    """Types of user interactions."""
    QUERY = "query"
    FEEDBACK = "feedback"
    DOCUMENT_REVIEW = "document_review"
    LEGAL_ADVICE = "legal_advice"
    FORM_ASSISTANCE = "form_assistance"


class FeedbackType(str, Enum):
    """Types of user feedback."""
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"
    NEUTRAL = "neutral"


class UserInteraction(BaseModel):
    """Model for user interaction data."""
    interaction_id: str = Field(..., description="Unique interaction identifier")
    user_id: str = Field(..., description="User identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    interaction_type: InteractionType
    query: str = Field(..., description="User query or input")
    predicted_domain: Optional[LegalDomain] = None
    confidence_score: Optional[float] = None
    response: Optional[str] = None
    feedback: Optional[FeedbackType] = None
    time_spent: Optional[float] = None  # in seconds
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UserProfile(BaseModel):
    """Model for user profile and preferences."""
    user_id: str = Field(..., description="Unique user identifier")
    user_type: UserType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    preferred_domains: List[LegalDomain] = Field(default_factory=list)
    interaction_count: int = Field(default=0)
    total_time_spent: float = Field(default=0.0)  # in seconds
    satisfaction_score: float = Field(default=0.0)  # -1 to 1
    preferences: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """Current state of the agent for a user session."""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    user_profile: UserProfile
    current_domain: Optional[LegalDomain] = None
    conversation_history: List[UserInteraction] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    active_tasks: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def add_interaction(self, interaction: UserInteraction) -> None:
        """Add a new interaction to the conversation history."""
        self.conversation_history.append(interaction)
        self.updated_at = datetime.utcnow()
        
        # Update user profile
        self.user_profile.interaction_count += 1
        self.user_profile.last_active = datetime.utcnow()
        
        if interaction.time_spent:
            self.user_profile.total_time_spent += interaction.time_spent
            
        if interaction.feedback:
            # Update satisfaction score based on feedback
            feedback_weight = 0.1  # How much each feedback affects the score
            if interaction.feedback == FeedbackType.UPVOTE:
                self.user_profile.satisfaction_score = min(1.0, 
                    self.user_profile.satisfaction_score + feedback_weight)
            elif interaction.feedback == FeedbackType.DOWNVOTE:
                self.user_profile.satisfaction_score = max(-1.0, 
                    self.user_profile.satisfaction_score - feedback_weight)
    
    def get_recent_interactions(self, limit: int = 10) -> List[UserInteraction]:
        """Get the most recent interactions."""
        return self.conversation_history[-limit:]
    
    def get_domain_history(self) -> Dict[LegalDomain, int]:
        """Get count of interactions by legal domain."""
        domain_counts = {}
        for interaction in self.conversation_history:
            if interaction.predicted_domain:
                domain = interaction.predicted_domain
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        return domain_counts
    
    def get_average_confidence(self) -> float:
        """Get average confidence score for predictions."""
        scores = [i.confidence_score for i in self.conversation_history 
                 if i.confidence_score is not None]
        return sum(scores) / len(scores) if scores else 0.0
    
    def update_context(self, key: str, value: Any) -> None:
        """Update context information."""
        self.context[key] = value
        self.updated_at = datetime.utcnow()
