import React, { useState, useRef, useEffect, forwardRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Scale } from 'lucide-react';
import Perfect3DLegalVisualization from './3D/Perfect3DLegalVisualization';
import { Message } from '../types';
import { sendMessage, submitFeedback } from '../api';

const ChatInterface = forwardRef<HTMLDivElement>((props, ref) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [show3DVisualization, setShow3DVisualization] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  useEffect(() => scrollToBottom(), [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    try {
      const response = await sendMessage(userMessage.content);

      const aiMessage: Message = {
        id: Date.now().toString() + '-ai',
        type: 'ai',
        content: response.formatted_response || response.response || 'No response content',
        timestamp: new Date(),
        structuredData: {
          domain: response.domain || 'General',
          legal_route: response.legal_guidance?.legal_procedures?.join(', ') || response.analysis?.summary || 'Legal guidance provided',
          timeline: response.legal_guidance?.timeline || 'Varies by case',
          outcome: response.analysis?.key_points?.join(', ') || 'Case-specific outcome',
          process_steps: response.legal_guidance?.legal_procedures?.join(', ') || 'Standard legal process',
          glossary: {} // Will be populated if available
        },
        rawData: response // Keep full data for feedback
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString() + '-error',
          type: 'ai',
          content: '⚠️ Sorry, could not connect to backend.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  const handleFeedback = async (message: Message, feedback: 'helpful' | 'not_helpful', rating: number) => {
    if (!message.rawData) return;
    
    try {
      await submitFeedback(
        message.rawData.query,
        message.rawData.domain,
        message.rawData.subdomain,
        message.rawData.domain_confidence,
        feedback,
        rating
      );
      
      // Update message to show feedback was submitted
      setMessages(prev => prev.map(msg => {
        if (msg.id === message.id) {
          return {
            ...msg,
            feedbackSubmitted: true,
            feedbackType: feedback
          };
        }
        return msg;
      }));
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const formatTimestamp = (date: Date) =>
    date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div ref={ref} className="flex flex-col h-full bg-gradient-to-br from-slate-900/50 to-blue-900/30 backdrop-blur-sm p-4">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`mb-3 flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.type === 'user' ? (
                <div className="max-w-[80%] p-3 rounded-xl shadow-md bg-blue-600 text-white">
                  {msg.content}
                  <div className="text-xs text-gray-200 mt-1 text-right">{formatTimestamp(msg.timestamp)}</div>
                </div>
              ) : msg.structuredData ? (
                <div className="max-w-[80%] space-y-2">
                  <div className="p-3 rounded-xl shadow-md bg-gray-800 text-gray-100">
                    <strong>Domain:</strong> {msg.structuredData.domain}
                  </div>
                  <div className="p-3 rounded-xl shadow-md bg-gray-800 text-gray-100">
                    <strong>Legal Route:</strong> {msg.structuredData.legal_route}
                  </div>
                  <div className="p-3 rounded-xl shadow-md bg-gray-800 text-gray-100">
                    <strong>Timeline:</strong> {msg.structuredData.timeline}
                  </div>
                  <div className="p-3 rounded-xl shadow-md bg-gray-800 text-gray-100">
                    <strong>Outcome:</strong> {msg.structuredData.outcome}
                  </div>
                  <div className="p-3 rounded-xl shadow-md bg-gray-800 text-gray-100">
                    <strong>Process Steps:</strong> {msg.structuredData.process_steps}
                  </div>
                  
                  {/* Feedback section */}
                  {!msg.feedbackSubmitted ? (
                    <div className="p-3 rounded-xl shadow-md bg-gray-700 text-gray-100">
                      <strong>Was this helpful?</strong>
                      <div className="flex gap-2 mt-2">
                        <button 
                          onClick={() => handleFeedback(msg, 'helpful', 5)}
                          className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded"
                        >
                          👍 Yes
                        </button>
                        <button 
                          onClick={() => handleFeedback(msg, 'not_helpful', 1)}
                          className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded"
                        >
                          👎 No
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="p-3 rounded-xl shadow-md bg-gray-700 text-gray-100">
                      <strong>Thank you for your feedback!</strong>
                      <div className="text-sm mt-1">
                        {msg.feedbackType === 'helpful' ? '👍 We\'re glad this was helpful!' : '📝 Thanks for the feedback. We\'ll use it to improve.'}
                      </div>
                    </div>
                  )}
                  
                  <div className="text-xs text-gray-400 mt-1 text-right">{formatTimestamp(msg.timestamp)}</div>
                </div>
              ) : (
                <div className="max-w-[80%] p-3 rounded-xl shadow-md bg-gray-800 text-gray-100">
                  {msg.content}
                  <div className="text-xs text-gray-400 mt-1 text-right">{formatTimestamp(msg.timestamp)}</div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef}></div>
      </div>

      {/* Input */}
      <div className="flex flex-col gap-2">
        {show3DVisualization && <Perfect3DLegalVisualization />}

        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyPress}
          placeholder="Type your legal question..."
          className="w-full resize-none p-3 rounded-lg bg-gray-900 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={1}
        />

        <div className="flex justify-between items-center">
          <button
            onClick={handleSendMessage}
            disabled={isLoading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50"
          >
            <Send size={18} /> {isLoading ? 'Sending...' : 'Send'}
          </button>

          <button
            onClick={() => setShow3DVisualization((prev) => !prev)}
            className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded-lg"
          >
            <Scale size={18} /> 3D View
          </button>
        </div>
      </div>
    </div>
  );
});

ChatInterface.displayName = 'ChatInterface';
export default ChatInterface;