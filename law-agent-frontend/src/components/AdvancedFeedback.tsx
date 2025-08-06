import React, { useState, useEffect } from 'react';
import './AdvancedFeedback.css';

interface FeedbackData {
  interaction_id: string;
  session_id: string;
  response_quality: number;
  legal_accuracy: number;
  helpfulness: number;
  clarity: number;
  completeness: number;
  time_spent: number;
  overall_satisfaction: 'upvote' | 'downvote' | 'neutral';
  specific_feedback: string;
  improvement_suggestions: string;
  would_recommend: boolean;
}

interface AdvancedFeedbackProps {
  interactionId: string;
  sessionId: string;
  onFeedbackSubmitted: (feedback: FeedbackData) => void;
  onClose: () => void;
}

const AdvancedFeedback: React.FC<AdvancedFeedbackProps> = ({
  interactionId,
  sessionId,
  onFeedbackSubmitted,
  onClose
}) => {
  const [feedback, setFeedback] = useState<FeedbackData>({
    interaction_id: interactionId,
    session_id: sessionId,
    response_quality: 3,
    legal_accuracy: 3,
    helpfulness: 3,
    clarity: 3,
    completeness: 3,
    time_spent: 0,
    overall_satisfaction: 'neutral',
    specific_feedback: '',
    improvement_suggestions: '',
    would_recommend: true
  });

  const [startTime] = useState(Date.now());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 3;

  useEffect(() => {
    // Update time spent every second
    const interval = setInterval(() => {
      setFeedback(prev => ({
        ...prev,
        time_spent: (Date.now() - startTime) / 1000
      }));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const handleRatingChange = (category: keyof FeedbackData, value: number) => {
    setFeedback(prev => ({
      ...prev,
      [category]: value
    }));
  };

  const handleTextChange = (field: keyof FeedbackData, value: string) => {
    setFeedback(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleOverallSatisfaction = (satisfaction: 'upvote' | 'downvote' | 'neutral') => {
    setFeedback(prev => ({
      ...prev,
      overall_satisfaction: satisfaction
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      // Submit to backend
      const response = await fetch('http://localhost:8000/api/v1/feedback/advanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedback),
      });

      if (response.ok) {
        onFeedbackSubmitted(feedback);
        onClose();
      } else {
        console.error('Failed to submit feedback');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStarRating = (
    label: string,
    category: keyof FeedbackData,
    description: string
  ) => {
    const value = feedback[category] as number;
    
    return (
      <div className="rating-group">
        <label className="rating-label">
          {label}
          <span className="rating-description">{description}</span>
        </label>
        <div className="star-rating">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className={`star ${star <= value ? 'active' : ''}`}
              onClick={() => handleRatingChange(category, star)}
            >
              ⭐
            </button>
          ))}
        </div>
        <span className="rating-text">
          {value === 1 && 'Poor'}
          {value === 2 && 'Fair'}
          {value === 3 && 'Good'}
          {value === 4 && 'Very Good'}
          {value === 5 && 'Excellent'}
        </span>
      </div>
    );
  };

  const renderStep1 = () => (
    <div className="feedback-step">
      <h3>Rate the Response Quality</h3>
      <p>Please rate different aspects of the legal response you received:</p>
      
      {renderStarRating(
        'Legal Accuracy',
        'legal_accuracy',
        'How accurate and legally sound was the information?'
      )}
      
      {renderStarRating(
        'Helpfulness',
        'helpfulness',
        'How helpful was the response for your situation?'
      )}
      
      {renderStarRating(
        'Clarity',
        'clarity',
        'How clear and understandable was the explanation?'
      )}
      
      {renderStarRating(
        'Completeness',
        'completeness',
        'How complete and comprehensive was the response?'
      )}
    </div>
  );

  const renderStep2 = () => (
    <div className="feedback-step">
      <h3>Overall Satisfaction</h3>
      
      <div className="satisfaction-buttons">
        <button
          className={`satisfaction-btn upvote ${feedback.overall_satisfaction === 'upvote' ? 'active' : ''}`}
          onClick={() => handleOverallSatisfaction('upvote')}
        >
          👍 Helpful
        </button>
        <button
          className={`satisfaction-btn neutral ${feedback.overall_satisfaction === 'neutral' ? 'active' : ''}`}
          onClick={() => handleOverallSatisfaction('neutral')}
        >
          😐 Neutral
        </button>
        <button
          className={`satisfaction-btn downvote ${feedback.overall_satisfaction === 'downvote' ? 'active' : ''}`}
          onClick={() => handleOverallSatisfaction('downvote')}
        >
          👎 Not Helpful
        </button>
      </div>

      <div className="recommendation-section">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={feedback.would_recommend}
            onChange={(e) => setFeedback(prev => ({
              ...prev,
              would_recommend: e.target.checked
            }))}
          />
          I would recommend this AI legal assistant to others
        </label>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="feedback-step">
      <h3>Additional Comments</h3>
      
      <div className="text-feedback-group">
        <label htmlFor="specific-feedback">
          What did you like or dislike about the response?
        </label>
        <textarea
          id="specific-feedback"
          value={feedback.specific_feedback}
          onChange={(e) => handleTextChange('specific_feedback', e.target.value)}
          placeholder="Please share your specific thoughts about the legal advice provided..."
          rows={4}
        />
      </div>

      <div className="text-feedback-group">
        <label htmlFor="improvement-suggestions">
          How could we improve the response?
        </label>
        <textarea
          id="improvement-suggestions"
          value={feedback.improvement_suggestions}
          onChange={(e) => handleTextChange('improvement_suggestions', e.target.value)}
          placeholder="Any suggestions for making the legal guidance more helpful..."
          rows={3}
        />
      </div>

      <div className="feedback-summary">
        <h4>Feedback Summary:</h4>
        <div className="summary-grid">
          <div>Legal Accuracy: {feedback.legal_accuracy}/5</div>
          <div>Helpfulness: {feedback.helpfulness}/5</div>
          <div>Clarity: {feedback.clarity}/5</div>
          <div>Completeness: {feedback.completeness}/5</div>
          <div>Overall: {feedback.overall_satisfaction}</div>
          <div>Time Spent: {Math.round(feedback.time_spent)}s</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="advanced-feedback-overlay">
      <div className="advanced-feedback-modal">
        <div className="feedback-header">
          <h2>Help Us Improve</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${(currentStep / totalSteps) * 100}%` }}
          />
        </div>

        <div className="step-indicator">
          Step {currentStep} of {totalSteps}
        </div>

        <div className="feedback-content">
          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
        </div>

        <div className="feedback-actions">
          {currentStep > 1 && (
            <button 
              className="btn-secondary"
              onClick={() => setCurrentStep(currentStep - 1)}
            >
              Previous
            </button>
          )}
          
          {currentStep < totalSteps ? (
            <button 
              className="btn-primary"
              onClick={() => setCurrentStep(currentStep + 1)}
            >
              Next
            </button>
          ) : (
            <button 
              className="btn-primary"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          )}
        </div>

        <div className="feedback-footer">
          <small>
            Your feedback helps our AI learn and provide better legal guidance. 
            Time spent: {Math.round(feedback.time_spent)}s
          </small>
        </div>
      </div>
    </div>
  );
};

export default AdvancedFeedback;
