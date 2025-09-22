/**
 * Analytics Service for Law Agent
 * Handles all analytics tracking and communication with analytics API
 */

interface AnalyticsEvent {
  event_type: string;
  session_id: string;
  user_id?: string;
  data?: Record<string, any>;
  page_url?: string;
  user_agent?: string;
  response_time_ms?: number;
}

interface LegalRouteData {
  session_id: string;
  route_type: string;
  route_description: string;
  suggested_context?: Record<string, any>;
}

interface LegalRouteResponse {
  session_id: string;
  route_id: string;
  user_response: 'accepted' | 'rejected' | 'ignored';
  response_time_seconds?: number;
  additional_data?: Record<string, any>;
}

interface GlossaryAccess {
  session_id: string;
  term: string;
  definition: string;
  access_method: 'search' | 'click' | 'hover' | 'voice';
  context?: string;
  additional_data?: Record<string, any>;
}

interface TimelineInteraction {
  session_id: string;
  timeline_type: string;
  step_id: string;
  step_name: string;
  interaction_type?: 'view' | 'click' | 'hover';
  additional_data?: Record<string, any>;
}

class AnalyticsService {
  private baseUrl: string;
  private sessionId: string | null = null;
  private userId: string | null = null;
  private websocket: WebSocket | null = null;
  private eventQueue: AnalyticsEvent[] = [];
  private isOnline: boolean = true;

  constructor(baseUrl: string = 'http://localhost:8002') {
    this.baseUrl = baseUrl;
    this.initializeSession();
    this.setupWebSocket();
    this.setupOfflineHandling();
  }

  /**
   * Initialize analytics session
   */
  private async initializeSession(context?: Record<string, any>): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/sessions/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          context: {
            user_agent: navigator.userAgent,
            page_url: window.location.href,
            timestamp: new Date().toISOString(),
            ...context
          }
        })
      });

      const result = await response.json();
      if (result.success) {
        this.sessionId = result.data.session_id;
        console.log('Analytics session started:', this.sessionId);
      }
    } catch (error) {
      console.error('Failed to start analytics session:', error);
    }
  }

  /**
   * Setup WebSocket for real-time analytics
   */
  private setupWebSocket(): void {
    try {
      this.websocket = new WebSocket(`ws://localhost:8002/ws`);
      
      this.websocket.onopen = () => {
        console.log('Analytics WebSocket connected');
      };

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // Handle real-time analytics updates
        this.handleRealTimeUpdate(data);
      };

      this.websocket.onerror = (error) => {
        console.error('Analytics WebSocket error:', error);
      };

      this.websocket.onclose = () => {
        console.log('Analytics WebSocket disconnected');
        // Attempt to reconnect after 5 seconds
        setTimeout(() => this.setupWebSocket(), 5000);
      };
    } catch (error) {
      console.error('Failed to setup WebSocket:', error);
    }
  }

  /**
   * Setup offline handling
   */
  private setupOfflineHandling(): void {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.flushEventQueue();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  /**
   * Handle real-time analytics updates
   */
  private handleRealTimeUpdate(data: any): void {
    // Emit custom event for components to listen to
    window.dispatchEvent(new CustomEvent('analytics-update', { detail: data }));
  }

  /**
   * Track a general analytics event
   */
  async trackEvent(eventType: string, data?: Record<string, any>, responseTime?: number): Promise<void> {
    if (!this.sessionId) {
      console.warn('No analytics session available');
      return;
    }

    const event: AnalyticsEvent = {
      event_type: eventType,
      session_id: this.sessionId,
      user_id: this.userId || undefined,
      data,
      page_url: window.location.href,
      user_agent: navigator.userAgent,
      response_time_ms: responseTime
    };

    if (!this.isOnline) {
      this.eventQueue.push(event);
      return;
    }

    try {
      await fetch(`${this.baseUrl}/events/track`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(event)
      });
    } catch (error) {
      console.error('Failed to track event:', error);
      this.eventQueue.push(event);
    }
  }

  /**
   * Track legal route suggestion
   */
  async trackLegalRouteSuggestion(routeType: string, routeDescription: string, context?: Record<string, any>): Promise<string | null> {
    if (!this.sessionId) return null;

    try {
      const response = await fetch(`${this.baseUrl}/legal-routes/suggest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          route_type: routeType,
          route_description: routeDescription,
          suggested_context: context
        })
      });

      const result = await response.json();
      return result.success ? result.data.route_id : null;
    } catch (error) {
      console.error('Failed to track legal route suggestion:', error);
      return null;
    }
  }

  /**
   * Track legal route response
   */
  async trackLegalRouteResponse(routeId: string, userResponse: 'accepted' | 'rejected' | 'ignored', responseTime?: number, additionalData?: Record<string, any>): Promise<void> {
    if (!this.sessionId) return;

    try {
      await fetch(`${this.baseUrl}/legal-routes/response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          route_id: routeId,
          user_response: userResponse,
          response_time_seconds: responseTime,
          additional_data: additionalData
        })
      });
    } catch (error) {
      console.error('Failed to track legal route response:', error);
    }
  }

  /**
   * Track glossary term access
   */
  async trackGlossaryAccess(term: string, definition: string, accessMethod: 'search' | 'click' | 'hover' | 'voice', context?: string, additionalData?: Record<string, any>): Promise<void> {
    if (!this.sessionId) return;

    try {
      await fetch(`${this.baseUrl}/glossary/access`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          term,
          definition,
          access_method: accessMethod,
          context: context || '',
          additional_data: additionalData
        })
      });
    } catch (error) {
      console.error('Failed to track glossary access:', error);
    }
  }

  /**
   * Track timeline interaction
   */
  async trackTimelineInteraction(timelineType: string, stepId: string, stepName: string, interactionType: 'view' | 'click' | 'hover' = 'view', additionalData?: Record<string, any>): Promise<void> {
    if (!this.sessionId) return;

    try {
      await fetch(`${this.baseUrl}/timeline/interaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          timeline_type: timelineType,
          step_id: stepId,
          step_name: stepName,
          interaction_type: interactionType,
          additional_data: additionalData
        })
      });
    } catch (error) {
      console.error('Failed to track timeline interaction:', error);
    }
  }

  /**
   * Track chat message
   */
  async trackChatMessage(messageType: 'sent' | 'received', message: string, responseTime?: number): Promise<void> {
    await this.trackEvent(
      messageType === 'sent' ? 'chat_message_sent' : 'chat_response_received',
      {
        message_length: message.length,
        message_type: messageType,
        timestamp: new Date().toISOString()
      },
      responseTime
    );
  }

  /**
   * Track document upload
   */
  async trackDocumentUpload(fileName: string, fileSize: number, fileType: string): Promise<void> {
    await this.trackEvent('document_uploaded', {
      file_name: fileName,
      file_size: fileSize,
      file_type: fileType,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Track page view
   */
  async trackPageView(pageName: string, additionalData?: Record<string, any>): Promise<void> {
    await this.trackEvent('page_view', {
      page_name: pageName,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      ...additionalData
    });
  }

  /**
   * Track user feedback
   */
  async trackFeedback(feedbackType: string, rating?: number, comment?: string, category?: string, component?: string): Promise<void> {
    await this.trackEvent('feedback_provided', {
      feedback_type: feedbackType,
      rating,
      comment,
      category,
      component,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Track performance metric
   */
  async trackPerformance(metricName: string, metricValue: number, metricUnit: string, component: string): Promise<void> {
    await this.trackEvent('performance_metric', {
      metric_name: metricName,
      metric_value: metricValue,
      metric_unit: metricUnit,
      component,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Flush queued events when back online
   */
  private async flushEventQueue(): Promise<void> {
    if (this.eventQueue.length === 0) return;

    console.log(`Flushing ${this.eventQueue.length} queued analytics events`);

    const events = [...this.eventQueue];
    this.eventQueue = [];

    for (const event of events) {
      try {
        await fetch(`${this.baseUrl}/events/track`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(event)
        });
      } catch (error) {
        console.error('Failed to flush event:', error);
        // Re-queue failed events
        this.eventQueue.push(event);
      }
    }
  }

  /**
   * End analytics session
   */
  async endSession(summaryData?: Record<string, any>): Promise<void> {
    if (!this.sessionId) return;

    try {
      await fetch(`${this.baseUrl}/sessions/${this.sessionId}/end`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(summaryData || {})
      });

      console.log('Analytics session ended:', this.sessionId);
    } catch (error) {
      console.error('Failed to end analytics session:', error);
    } finally {
      this.sessionId = null;
      if (this.websocket) {
        this.websocket.close();
      }
    }
  }

  /**
   * Set user ID for tracking
   */
  setUserId(userId: string): void {
    this.userId = userId;
  }

  /**
   * Get current session ID
   */
  getSessionId(): string | null {
    return this.sessionId;
  }
}

// Create and export singleton instance
export const analyticsService = new AnalyticsService();

// Export types for use in components
export type {
  AnalyticsEvent,
  LegalRouteData,
  LegalRouteResponse,
  GlossaryAccess,
  TimelineInteraction
};
