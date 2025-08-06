import React, { useState, useRef, useEffect, forwardRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, Mic, MicOff, Paperclip, MoreVertical, Scale, Box } from 'lucide-react';
import Perfect3DLegalVisualization from './3D/Perfect3DLegalVisualization';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Message } from '../types';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const ChatInterface = forwardRef<HTMLDivElement, ChatInterfaceProps>(
  ({ messages, onSendMessage, isLoading }, ref) => {
    const [inputValue, setInputValue] = useState('');
    const [isRecording, setIsRecording] = useState(false);
    const [showSuggestions, setShowSuggestions] = useState(true);
    const [show3DVisualization, setShow3DVisualization] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
      scrollToBottom();
    }, [messages]);

    const handleSendMessage = () => {
      if (!inputValue.trim() || isLoading) return;
      
      onSendMessage(inputValue);
      setInputValue('');
      setShowSuggestions(false);
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
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
      
      // Auto-resize textarea
      const textarea = e.target;
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    };

    const suggestions = [
      "What are my rights in a contract dispute?",
      "How do I file for divorce in California?",
      "Explain criminal defense strategies",
      "What is the statute of limitations for personal injury?",
      "How does bankruptcy work?",
      "What are the steps in a civil lawsuit?"
    ];

    const formatTimestamp = (date: Date) => {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
      <div ref={ref} className="flex flex-col h-full bg-gradient-to-br from-slate-900/50 to-blue-900/30 backdrop-blur-sm">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-dark border-b border-white/10 p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <motion.div
                className="relative"
                whileHover={{ scale: 1.05 }}
              >
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <motion.div
                  className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </motion.div>
              <div>
                <h2 className="text-xl font-bold text-white">AI Legal Assistant</h2>
                <p className="text-sm text-gray-400">Ready to help with legal questions</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              >
                <MoreVertical className="h-5 w-5 text-gray-400" />
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Welcome Message */}
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <motion.div
                className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl"
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                <Scale className="h-10 w-10 text-white" />
              </motion.div>
              <h3 className="text-2xl font-bold text-white mb-4">
                Welcome to Law Agent AI
              </h3>
              <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
                Your advanced AI legal assistant is ready to help with legal questions, 
                document analysis, and expert guidance across all areas of law.
              </p>
              
              {/* Quick Suggestions */}
              {showSuggestions && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl mx-auto"
                >
                  {suggestions.map((suggestion, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * index }}
                      whileHover={{ scale: 1.02, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setInputValue(suggestion)}
                      className="legal-card text-left p-4 hover:border-primary-500/50 group"
                    >
                      <p className="text-white text-sm group-hover:text-primary-300 transition-colors">
                        {suggestion}
                      </p>
                    </motion.button>
                  ))}
                </motion.div>
              )}
            </motion.div>
          )}

          {/* Messages */}
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex max-w-4xl ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} space-x-4`}>
                  {/* Avatar */}
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ${
                      message.type === 'user'
                        ? 'bg-gradient-to-r from-green-500 to-emerald-600'
                        : 'bg-gradient-to-r from-blue-500 to-purple-600'
                    }`}
                  >
                    {message.type === 'user' ? (
                      <User className="h-5 w-5 text-white" />
                    ) : (
                      <Bot className="h-5 w-5 text-white" />
                    )}
                  </motion.div>

                  {/* Message Content */}
                  <div className={`flex-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                    <motion.div
                      whileHover={{ scale: 1.01 }}
                      className={`inline-block max-w-full p-4 rounded-2xl shadow-lg backdrop-blur-sm border transition-all duration-300 ${
                        message.type === 'user'
                          ? 'bg-gradient-to-r from-green-500/20 to-emerald-600/20 border-green-500/30 text-white'
                          : 'glass border-white/20 text-white'
                      }`}
                    >
                      {message.type === 'user' ? (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      ) : (
                        <div className="prose prose-invert prose-sm max-w-none">
                          <ReactMarkdown
                            components={{
                              code({ className, children, ...props }) {
                                const match = /language-(\w+)/.exec(className || '');
                                return match ? (
                                  <SyntaxHighlighter
                                    style={atomDark as any}
                                    language={match[1]}
                                    PreTag="div"
                                  >
                                    {String(children).replace(/\n$/, '')}
                                  </SyntaxHighlighter>
                                ) : (
                                  <code className={className}>
                                    {children}
                                  </code>
                                );
                              },
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-white/10">
                        <span className="text-xs text-gray-400">
                          {formatTimestamp(message.timestamp)}
                        </span>
                        {message.type === 'ai' && (
                          <div className="flex items-center space-x-1">
                            <Sparkles className="h-3 w-3 text-yellow-400" />
                            <span className="text-xs text-yellow-400">AI Response</span>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading Indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex justify-start"
            >
              <div className="flex items-center space-x-4">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg"
                >
                  <Bot className="h-5 w-5 text-white" />
                </motion.div>
                <div className="glass rounded-2xl p-4 border border-white/20">
                  <div className="flex space-x-2 items-center">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        className="w-2 h-2 bg-primary-400 rounded-full"
                        animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                        transition={{
                          duration: 1.5,
                          repeat: Infinity,
                          delay: i * 0.2,
                        }}
                      />
                    ))}
                    <span className="text-gray-400 text-sm ml-3">AI is thinking...</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-dark border-t border-white/10 p-6"
        >
          <div className="flex items-end space-x-4">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about legal matters... ⚖️"
                className="w-full px-4 py-3 pr-12 glass rounded-xl resize-none text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-300 min-h-[48px] max-h-[120px]"
                rows={1}
              />
              
              <div className="absolute right-3 bottom-3 flex items-center space-x-2">
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className="p-1 text-gray-400 hover:text-white transition-colors"
                >
                  <Paperclip className="h-4 w-4" />
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setIsRecording(!isRecording)}
                  className={`p-1 transition-colors ${
                    isRecording ? 'text-red-400' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </motion.button>
              </div>
            </div>
            
            {/* 3D Visualization Toggle */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShow3DVisualization(!show3DVisualization)}
              className={`p-3 rounded-xl transition-all duration-300 flex items-center space-x-2 ${
                show3DVisualization
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'glass hover:bg-white/10 text-gray-300 hover:text-white'
              }`}
              title="Toggle 3D Legal Visualization"
            >
              <Box className="h-5 w-5" />
              <span className="hidden sm:inline">3D</span>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Send className="h-5 w-5" />
              <span>Send</span>
            </motion.button>
          </div>
          
          <p className="text-xs text-gray-500 mt-3 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </motion.div>

        {/* Perfect 3D Legal Visualization Overlay */}
        <AnimatePresence>
          {show3DVisualization && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm"
            >
              <div className="relative w-full h-full">
                {/* Close Button */}
                <button
                  onClick={() => setShow3DVisualization(false)}
                  className="absolute top-4 right-4 z-10 bg-red-600 hover:bg-red-700 text-white p-3 rounded-full transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>

                {/* Perfect 3D Visualization */}
                <Perfect3DLegalVisualization
                  initialView="3d-process"
                  legalDomain={messages.length > 0 ? 'criminal_law' : 'criminal_law'}
                  userLocation="usa"
                  onVisualizationChange={(view, data) => {
                    console.log('3D Visualization:', view, data);
                  }}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

ChatInterface.displayName = 'ChatInterface';

export default ChatInterface;
