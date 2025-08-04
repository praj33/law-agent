import React, { useState, useEffect } from 'react';
import {
  Scale,
  MessageCircle,
  Building,
  Map,
  Clock,
  BookOpen,
  Bot,
  User,
  Send,
  Sparkles,
  Shield,
  Gavel,
  Star,
  Zap,
  Heart,
  Award,
  Crown,
  Upload,
  BarChart3
} from 'lucide-react';
import './LawAgentApp.css';
import DocumentUpload from './DocumentUpload';
import AnalyticsDashboard from './AnalyticsDashboard';

const LawAgentApp: React.FC = () => {
  const [currentView, setCurrentView] = useState('court');
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'ai',
      content: 'Welcome to Law Agent! I\'m your AI legal assistant. Explore the immersive courtroom experience and interact with our advanced legal AI avatar! ⚖️✨',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [backgroundAnimation, setBackgroundAnimation] = useState(0);

  // Background animation effect
  useEffect(() => {
    const interval = setInterval(() => {
      setBackgroundAnimation(prev => (prev + 1) % 360);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const newMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setIsTyping(true);

    setTimeout(() => {
      const responses = [
        'Thank you for your question! I\'m analyzing your legal query using advanced AI algorithms and will provide you with comprehensive information based on current legal precedents and statutes. ⚖️',
        'Excellent question! Let me search through thousands of legal documents and case studies to provide you with the most accurate and up-to-date legal guidance. 📚✨',
        'I\'m processing your legal inquiry with precision. My AI-powered analysis will deliver relevant legal insights, precedents, and actionable advice tailored to your specific situation. 🎯',
        'Great inquiry! I\'m consulting my extensive legal database to provide you with expert-level guidance. This includes relevant case law, statutes, and practical recommendations. 🏛️'
      ];

      const aiResponse = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 2000);

    setInputMessage('');
  };

  const navigationItems = [
    { id: 'chat', label: 'Chat', icon: MessageCircle, color: 'from-blue-500 to-purple-500' },
    { id: 'court', label: '3D Court', icon: Building, color: 'from-green-500 to-blue-500' },
    { id: 'documents', label: 'Documents', icon: Upload, color: 'from-emerald-500 to-teal-500' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, color: 'from-cyan-500 to-blue-500' },
    { id: 'map', label: 'Jurisdiction', icon: Map, color: 'from-purple-500 to-pink-500' },
    { id: 'timeline', label: 'Timeline', icon: Clock, color: 'from-orange-500 to-red-500' },
    { id: 'glossary', label: 'Glossary', icon: BookOpen, color: 'from-indigo-500 to-purple-500' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 p-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse"
          style={{ transform: `rotate(${backgroundAnimation}deg)` }}
        />
        <div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse"
          style={{ transform: `rotate(${-backgroundAnimation}deg)` }}
        />
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl animate-ping" />
      </div>

      {/* Floating Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(15)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white/30 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`
            }}
          />
        ))}
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Enhanced Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur-lg opacity-75 animate-pulse" />
              <div className="relative p-4 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 rounded-full shadow-2xl">
                <Scale className="h-16 w-16 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full animate-ping" />
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full" />
            </div>
          </div>
          <h1 className="law-agent-title text-6xl mb-4 tracking-wide">
            <span className="inline-block">Law</span>{' '}
            <span className="inline-block">Agent</span>
          </h1>
          <div className="flex items-center justify-center space-x-3 mb-4">
            <Sparkles className="h-5 w-5 text-yellow-400 animate-pulse" />
            <p className="text-2xl text-blue-200 font-semibold">AI-Powered Legal Assistant</p>
            <Crown className="h-5 w-5 text-yellow-400 animate-bounce" />
          </div>
          <div className="flex items-center justify-center space-x-6 text-gray-300">
            <div className="flex items-center space-x-2">
              <Shield className="h-4 w-4 text-green-400" />
              <span className="text-sm">Secure & Confidential</span>
            </div>
            <div className="flex items-center space-x-2">
              <Zap className="h-4 w-4 text-yellow-400" />
              <span className="text-sm">AI-Powered</span>
            </div>
            <div className="flex items-center space-x-2">
              <Award className="h-4 w-4 text-purple-400" />
              <span className="text-sm">Expert Legal Guidance</span>
            </div>
          </div>
        </div>

        {/* Enhanced Navigation */}
        <div className="flex flex-wrap justify-center gap-6 mb-12">
          {navigationItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={`group relative flex items-center space-x-3 px-8 py-4 rounded-2xl font-semibold transition-all duration-300 transform hover:scale-110 ${
                  currentView === item.id
                    ? `bg-gradient-to-r ${item.color} text-white shadow-2xl shadow-blue-500/25`
                    : 'bg-white/10 text-gray-300 hover:bg-white/20 hover:text-white backdrop-blur-sm border border-white/20 hover:border-white/40'
                }`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className={`p-2 rounded-lg ${currentView === item.id ? 'bg-white/20' : 'bg-white/10 group-hover:bg-white/20'}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <span className="text-lg">{item.label}</span>

                {/* Hover Effect */}
                <div className="absolute inset-0 bg-white/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                {/* Active Indicator */}
                {currentView === item.id && (
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-white rounded-full animate-pulse" />
                )}

                {/* Sparkle Effect for Active */}
                {currentView === item.id && (
                  <div className="absolute -top-1 -right-1">
                    <Star className="h-4 w-4 text-yellow-400 animate-spin" />
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Enhanced Main Content */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl border border-white/30 overflow-hidden shadow-2xl shadow-black/20 relative">
          {/* Content Glow Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-indigo-500/5 rounded-3xl" />
          {currentView === 'chat' && (
            <div className="h-[600px] flex flex-col relative">
              {/* Chat Header */}
              <div className="p-6 border-b border-white/20 bg-gradient-to-r from-blue-500/10 to-purple-500/10">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-lg">
                      <Bot className="h-6 w-6 text-white" />
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">AI Legal Assistant</h3>
                    <p className="text-sm text-blue-200">Online • Ready to help</p>
                  </div>
                  <div className="ml-auto flex space-x-2">
                    <Sparkles className="h-5 w-5 text-yellow-400 animate-pulse" />
                    <Heart className="h-5 w-5 text-red-400 animate-pulse" />
                  </div>
                </div>
              </div>

              {/* Enhanced Chat Messages */}
              <div className="flex-1 p-6 overflow-y-auto space-y-6 relative">
                {messages.map((message, index) => (
                  <div
                    key={message.id}
                    className={`flex items-start space-x-4 animate-fade-in ${
                      message.type === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    {message.type === 'ai' && (
                      <div className="relative">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-lg">
                          <Bot className="h-5 w-5 text-white" />
                        </div>
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping" />
                      </div>
                    )}
                    <div
                      className={`max-w-md px-6 py-4 rounded-2xl shadow-lg relative ${
                        message.type === 'user'
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                          : 'bg-gradient-to-r from-gray-700 to-gray-800 text-gray-100 border border-white/10'
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      <div className="mt-2 text-xs opacity-70">
                        {message.timestamp.toLocaleTimeString()}
                      </div>

                      {/* Message Glow Effect */}
                      <div className={`absolute inset-0 rounded-2xl blur-lg opacity-20 ${
                        message.type === 'user'
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600'
                          : 'bg-gradient-to-r from-gray-600 to-gray-700'
                      }`} />
                    </div>
                    {message.type === 'user' && (
                      <div className="relative">
                        <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-500 rounded-full flex items-center justify-center shadow-lg">
                          <User className="h-5 w-5 text-white" />
                        </div>
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-400 rounded-full animate-ping" />
                      </div>
                    )}
                  </div>
                ))}

                {/* Typing Indicator */}
                {isTyping && (
                  <div className="flex items-start space-x-4 animate-fade-in">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-lg">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                    <div className="bg-gradient-to-r from-gray-700 to-gray-800 px-6 py-4 rounded-2xl border border-white/10">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Enhanced Input Area */}
              <div className="p-6 border-t border-white/20 bg-gradient-to-r from-gray-800/50 to-gray-900/50 backdrop-blur-sm">
                <div className="flex space-x-4 items-end">
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      placeholder="Ask me anything about law... ⚖️"
                      className="w-full bg-gray-800/80 text-white px-6 py-4 rounded-2xl border border-gray-600/50 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 backdrop-blur-sm transition-all duration-300 text-lg placeholder-gray-400"
                      disabled={isTyping}
                    />
                    <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex space-x-2">
                      <Sparkles className="h-4 w-4 text-yellow-400 animate-pulse" />
                    </div>
                  </div>
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isTyping}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white px-8 py-4 rounded-2xl transition-all duration-300 flex items-center space-x-3 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed"
                  >
                    <Send className="h-5 w-5" />
                    <span className="font-semibold">Send</span>
                  </button>
                </div>

                {/* Quick Suggestions */}
                <div className="mt-4 flex flex-wrap gap-2">
                  {[
                    "Contract law basics",
                    "Employment rights",
                    "Property disputes",
                    "Criminal defense",
                    "Family law"
                  ].map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(suggestion)}
                      className="px-4 py-2 bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white rounded-full text-sm transition-all duration-200 border border-white/10 hover:border-white/30"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {currentView === 'documents' && (
            <div className="min-h-[600px]">
              <DocumentUpload />
            </div>
          )}

          {currentView === 'analytics' && (
            <div className="min-h-[600px]">
              <AnalyticsDashboard />
            </div>
          )}

          {currentView === 'court' && (
            <div className="h-[700px] relative bg-gradient-to-b from-blue-900/30 to-purple-900/30 rounded-3xl overflow-hidden border border-white/20">
              {/* Enhanced Court Background */}
              <div className="absolute inset-0 bg-gradient-to-b from-slate-800 to-slate-900 rounded-3xl">
                <div className="absolute inset-0 opacity-20 rounded-3xl">
                  <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-indigo-500/10 rounded-3xl" />
                  <div className="absolute top-1/4 left-1/4 w-24 h-24 bg-yellow-400/5 rounded-full blur-2xl animate-pulse" />
                  <div className="absolute bottom-1/4 right-1/4 w-24 h-24 bg-blue-400/5 rounded-full blur-2xl animate-pulse" />
                </div>
              </div>

              {/* Professional Courtroom Architecture */}
              <div className="absolute bottom-0 left-0 right-0 h-32 flex items-end justify-center pb-4">
                <div className="flex space-x-4 opacity-40">
                  {/* Judge's Bench */}
                  <div className="relative">
                    <div className="w-12 h-24 bg-gradient-to-t from-amber-800 to-amber-600 rounded-t-lg shadow-lg" />
                    <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-16 h-4 bg-gradient-to-r from-amber-700 to-amber-500 rounded-lg" />
                  </div>
                  {/* Columns */}
                  <div className="w-8 h-28 bg-gradient-to-t from-gray-600 to-gray-400 rounded-t-lg shadow-lg" />
                  <div className="w-8 h-32 bg-gradient-to-t from-gray-600 to-gray-400 rounded-t-lg shadow-lg" />
                  <div className="w-8 h-30 bg-gradient-to-t from-gray-600 to-gray-400 rounded-t-lg shadow-lg" />
                  <div className="w-8 h-28 bg-gradient-to-t from-gray-600 to-gray-400 rounded-t-lg shadow-lg" />
                  {/* Witness Stand */}
                  <div className="w-10 h-20 bg-gradient-to-t from-amber-800 to-amber-600 rounded-t-lg shadow-lg" />
                </div>
              </div>

              {/* Court Layout - Properly Contained */}
              <div className="relative z-10 h-full flex flex-col p-6">
                {/* Court Header */}
                <div className="text-center mb-6">
                  <div className="relative inline-block mb-4">
                    <div className="text-6xl animate-pulse">🏛️</div>
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full animate-ping" />
                    <div className="absolute -bottom-1 -left-1 w-3 h-3 bg-blue-400 rounded-full animate-bounce" />
                  </div>
                  <h3 className="text-3xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent mb-2">
                    Virtual Courtroom
                  </h3>
                  <div className="flex items-center justify-center space-x-3 mb-4">
                    <Gavel className="h-4 w-4 text-yellow-400 animate-pulse" />
                    <p className="text-lg text-blue-200 font-semibold">Interactive Legal Environment</p>
                    <Scale className="h-4 w-4 text-blue-400 animate-pulse" />
                  </div>
                </div>

                {/* Main Court Content Area */}
                <div className="flex-1 flex items-center justify-center">
                  <div className="w-full max-w-4xl">
                    {/* Enhanced Talking Avatar Section */}
                    <div className="flex justify-center mb-6">
                      <TalkingAvatarComponent />
                    </div>

                    {/* Court Features - Properly Sized */}
                    <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
                      <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 border border-white/20 hover:bg-white/15 transition-all duration-300">
                        <Shield className="h-6 w-6 text-green-400 mx-auto mb-2" />
                        <p className="text-white font-semibold text-sm">Legal Protection</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 border border-white/20 hover:bg-white/15 transition-all duration-300">
                        <Award className="h-6 w-6 text-yellow-400 mx-auto mb-2" />
                        <p className="text-white font-semibold text-sm">Expert Guidance</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3 border border-white/20 hover:bg-white/15 transition-all duration-300">
                        <Zap className="h-6 w-6 text-purple-400 mx-auto mb-2" />
                        <p className="text-white font-semibold text-sm">AI-Powered</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentView !== 'chat' && currentView !== 'court' && (
            <div className="h-96 flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4">
                  {currentView === 'map' ? '🗺️' : 
                   currentView === 'timeline' ? '📅' : '📚'}
                </div>
                <p className="text-white text-xl">
                  {currentView.charAt(0).toUpperCase() + currentView.slice(1)} Module
                </p>
                <p className="text-gray-300 mt-2">Feature coming soon...</p>
              </div>
            </div>
          )}
        </div>

        {/* Enhanced Instructions */}
        <div className="text-center mt-12">
          <div className="bg-gradient-to-r from-white/10 to-white/5 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl">
            <div className="flex items-center justify-center space-x-3 mb-6">
              <Sparkles className="h-6 w-6 text-yellow-400 animate-pulse" />
              <h3 className="law-agent-welcome text-2xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-200 bg-clip-text text-transparent tracking-wide">
                Welcome to <span className="inline-block">Law</span>{' '}<span className="inline-block">Agent</span>
              </h3>
              <Crown className="h-6 w-6 text-yellow-400 animate-bounce" />
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="text-4xl mb-3">🎯</div>
                <h4 className="text-white font-semibold mb-2">Interactive Court</h4>
                <p className="text-gray-300 text-sm">Click on Sophia, our AI legal assistant, to start an interactive conversation!</p>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="text-4xl mb-3">💬</div>
                <h4 className="text-white font-semibold mb-2">AI Chat</h4>
                <p className="text-gray-300 text-sm">Ask legal questions and get expert AI-powered responses instantly.</p>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                <div className="text-4xl mb-3">⚖️</div>
                <h4 className="text-white font-semibold mb-2">Legal Guidance</h4>
                <p className="text-gray-300 text-sm">Navigate complex legal matters with confidence and precision.</p>
              </div>
            </div>

            <div className="flex items-center justify-center space-x-6 text-sm text-gray-300">
              <div className="flex items-center space-x-2">
                <Shield className="h-4 w-4 text-green-400" />
                <span>Secure & Confidential</span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4 text-yellow-400" />
                <span>AI-Powered Intelligence</span>
              </div>
              <div className="flex items-center space-x-2">
                <Award className="h-4 w-4 text-purple-400" />
                <span>Expert Legal Knowledge</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Simple 2D Talking Avatar Component
const TalkingAvatarComponent: React.FC = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isHovered, setIsHovered] = useState(false);

  const legalMessages = [
    "⚖️ Welcome to the virtual courtroom! I'm Attorney Marcus, your AI legal counsel.",
    "🏛️ With over 20 years of legal expertise, I can guide you through complex legal matters.",
    "📚 I specialize in constitutional law, corporate litigation, and civil rights cases.",
    "🎯 The courtroom behind me represents the foundation of our justice system.",
    "📋 Legal proceedings require precise understanding of statutes and precedents.",
    "🔍 I'm here to provide expert legal analysis and strategic counsel.",
    "💼 Each case requires careful examination of facts, law, and procedural requirements.",
    "⭐ My AI-powered legal database contains millions of case precedents and statutes.",
    "🛡️ Your constitutional rights are paramount, and I'll ensure they're protected.",
    "🌟 Together, we'll build a strong legal strategy based on sound jurisprudence.",
    "📖 The law is complex, but with proper guidance, justice can be achieved."
  ];

  const speakMessage = (message: string) => {
    setCurrentMessage(message);
    setIsSpeaking(true);

    // Text-to-speech
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(message);
      const voices = speechSynthesis.getVoices();
      utterance.voice = voices.find(voice =>
        voice.name.includes('Female') || voice.name.includes('female')
      ) || voices[0];
      utterance.rate = 0.9;
      utterance.pitch = 1.1;
      speechSynthesis.speak(utterance);
    }

    // Stop speaking after duration
    setTimeout(() => {
      setIsSpeaking(false);
      setCurrentMessage('');
    }, 4000 + message.length * 50);
  };

  // Auto-speak every 8 seconds
  React.useEffect(() => {
    const interval = setInterval(() => {
      if (!isSpeaking) {
        const randomMessage = legalMessages[Math.floor(Math.random() * legalMessages.length)];
        speakMessage(randomMessage);
      }
    }, 8000);

    return () => clearInterval(interval);
  }, [isSpeaking]);

  const handleClick = () => {
    if (!isSpeaking) {
      const randomMessage = legalMessages[Math.floor(Math.random() * legalMessages.length)];
      speakMessage(randomMessage);
    }
  };

  return (
    <div className="relative">
      {/* Professional Male Lawyer Avatar */}
      <div
        className={`relative cursor-pointer transition-all duration-500 ${
          isHovered ? 'scale-110 rotate-1' : 'scale-100'
        } ${isSpeaking ? 'animate-pulse' : ''}`}
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Professional Glow Effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-amber-500 to-blue-600 rounded-full blur-xl opacity-40 animate-pulse" />

        {/* Lawyer Body - Professional Suit */}
        <div className="relative mx-auto w-36 h-44 bg-gradient-to-b from-gray-800 via-gray-900 to-black rounded-t-full rounded-b-3xl shadow-2xl border-2 border-white/30">
          {/* Suit Jacket Details */}
          <div className="absolute top-6 left-1/2 transform -translate-x-1/2 w-8 h-12 bg-white/95 rounded-sm shadow-lg" />
          <div className="absolute top-8 left-1/2 transform -translate-x-1/2 w-3 h-8 bg-gradient-to-b from-red-700 to-red-800 rounded-sm shadow-md" />

          {/* Suit Lapels */}
          <div className="absolute top-4 left-3 w-6 h-8 bg-gradient-to-br from-gray-700 to-gray-800 transform rotate-12 rounded-sm" />
          <div className="absolute top-4 right-3 w-6 h-8 bg-gradient-to-bl from-gray-700 to-gray-800 transform -rotate-12 rounded-sm" />

          {/* Suit Buttons */}
          <div className="absolute top-12 left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 bg-yellow-400 rounded-full shadow-sm" />
          <div className="absolute top-16 left-1/2 transform -translate-x-1/2 w-1.5 h-1.5 bg-yellow-400 rounded-full shadow-sm" />

          {/* Professional Head */}
          <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 w-22 h-22 bg-gradient-to-b from-orange-100 to-orange-200 rounded-full shadow-xl border-2 border-white/40">
            {/* Professional Hair - Short and Neat */}
            <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-20 h-12 bg-gradient-to-b from-gray-800 to-gray-900 rounded-full shadow-lg"></div>
            <div className="absolute -top-1 left-3 w-3 h-6 bg-gradient-to-b from-gray-800 to-gray-900 rounded-full transform rotate-15"></div>
            <div className="absolute -top-1 right-3 w-3 h-6 bg-gradient-to-b from-gray-800 to-gray-900 rounded-full transform -rotate-15"></div>

            {/* Professional Eyes */}
            <div className="absolute top-6 left-5 w-3 h-3 bg-white rounded-full shadow-sm">
              <div className="absolute top-0.5 left-0.5 w-2 h-2 bg-gray-800 rounded-full">
                <div className="absolute top-0.5 left-0.5 w-1 h-1 bg-white rounded-full"></div>
              </div>
            </div>
            <div className="absolute top-6 right-5 w-3 h-3 bg-white rounded-full shadow-sm">
              <div className="absolute top-0.5 left-0.5 w-2 h-2 bg-gray-800 rounded-full">
                <div className="absolute top-0.5 left-0.5 w-1 h-1 bg-white rounded-full"></div>
              </div>
            </div>

            {/* Strong Eyebrows */}
            <div className="absolute top-4 left-5 w-3 h-1.5 bg-gray-800 rounded-full"></div>
            <div className="absolute top-4 right-5 w-3 h-1.5 bg-gray-800 rounded-full"></div>

            {/* Professional Nose */}
            <div className="absolute top-8 left-1/2 transform -translate-x-1/2 w-1.5 h-3 bg-orange-300 rounded-full shadow-sm"></div>

            {/* Professional Mouth */}
            <div className={`absolute top-12 left-1/2 transform -translate-x-1/2 w-5 h-2 rounded-full transition-all duration-300 ${
              isSpeaking ? 'bg-red-600 animate-pulse scale-110' : 'bg-red-400'
            }`}>
              {isSpeaking && (
                <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-red-500 rounded-full animate-ping"></div>
              )}
            </div>

            {/* Glasses (Professional Touch) */}
            <div className="absolute top-5 left-4 w-4 h-4 border-2 border-gray-700 rounded-full bg-white/20"></div>
            <div className="absolute top-5 right-4 w-4 h-4 border-2 border-gray-700 rounded-full bg-white/20"></div>
            <div className="absolute top-6 left-1/2 transform -translate-x-1/2 w-2 h-0.5 bg-gray-700"></div>
          </div>

          {/* Professional Badge */}
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-amber-500 to-amber-600 text-black text-xs px-4 py-2 rounded-full font-bold shadow-xl border-2 border-amber-400">
            <div className="flex items-center space-x-2">
              <Gavel className="h-3 w-3" />
              <span>Attorney Marcus</span>
              <Scale className="h-3 w-3" />
            </div>
          </div>

          {/* Professional Status Indicator */}
          <div className="absolute -top-3 -right-3 w-5 h-5 bg-green-500 rounded-full border-3 border-white animate-pulse shadow-xl">
            <div className="absolute inset-0 bg-green-500 rounded-full animate-ping"></div>
          </div>

          {/* Law Firm Pin */}
          <div className="absolute top-6 left-4 w-2 h-2 bg-yellow-500 rounded-full shadow-lg"></div>
        </div>

        {/* Enhanced Speaking Animation */}
        {isSpeaking && (
          <div className="absolute -top-6 left-1/2 transform -translate-x-1/2">
            <div className="flex space-x-1">
              <div className="w-3 h-3 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full animate-bounce shadow-lg"></div>
              <div className="w-3 h-3 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-3 h-3 bg-gradient-to-r from-pink-400 to-blue-400 rounded-full animate-bounce shadow-lg" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Speech Bubble */}
      {isSpeaking && currentMessage && (
        <div className="absolute -top-32 left-1/2 transform -translate-x-1/2 w-80 bg-gradient-to-r from-white/95 to-blue-50/95 backdrop-blur-lg rounded-2xl p-4 border-2 border-blue-200/50 shadow-2xl animate-fade-in">
          <div className="flex items-start space-x-3">
            <div className="flex space-x-1 mt-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-pink-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-800 font-semibold leading-relaxed">
                {currentMessage}
              </p>
              <div className="flex items-center space-x-2 mt-2">
                <div className="w-1 h-1 bg-green-500 rounded-full animate-ping"></div>
                <span className="text-xs text-gray-600 font-medium">Sophia speaking...</span>
              </div>
            </div>
          </div>
          {/* Enhanced Speech bubble tail */}
          <div className="absolute bottom-[-12px] left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-12 border-r-12 border-t-12 border-l-transparent border-r-transparent border-t-white/95 drop-shadow-lg"></div>
        </div>
      )}

      {/* Enhanced Hover Tooltip */}
      {isHovered && !isSpeaking && (
        <div className="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-black/90 to-gray-800/90 text-white px-4 py-3 rounded-xl text-sm whitespace-nowrap shadow-xl border border-white/20 backdrop-blur-sm">
          <div className="flex items-center space-x-2">
            <Gavel className="h-4 w-4 text-amber-400 animate-pulse" />
            <span className="font-semibold">Click for legal consultation!</span>
          </div>
        </div>
      )}

      {/* Enhanced Name Section */}
      <div className="text-center mt-6">
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20 shadow-lg">
          <div className="flex items-center justify-center space-x-2 mb-2">
            <Gavel className="h-5 w-5 text-amber-400" />
            <p className="text-white font-bold text-lg">Attorney Marcus</p>
            <Scale className="h-5 w-5 text-amber-400 animate-pulse" />
          </div>
          <p className="text-blue-200 text-sm font-semibold">Senior Legal Counsel AI</p>
          <div className="flex items-center justify-center space-x-4 mt-3 text-xs text-gray-300">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Available</span>
            </div>
            <div className="flex items-center space-x-1">
              <Award className="h-3 w-3 text-amber-400" />
              <span>20+ Years Experience</span>
            </div>
            <div className="flex items-center space-x-1">
              <Shield className="h-3 w-3 text-blue-400" />
              <span>Licensed Attorney</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LawAgentApp;
