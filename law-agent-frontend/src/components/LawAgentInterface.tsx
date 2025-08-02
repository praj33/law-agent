import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatInterface from './ChatInterface';
import ResponseModule from './ResponseModule';
import LegalTimeline from './LegalTimeline';
import LegalGlossary from './LegalGlossary';
import { Scale, MessageSquare, Map, Clock, BookOpen, Gavel } from 'lucide-react';
import toast from 'react-hot-toast';
import { Message, TimelineEvent, GlossaryTerm } from '../types';

const LawAgentInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentView, setCurrentView] = useState<'chat' | 'court' | 'map' | 'timeline' | 'glossary'>('chat');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      const response = await fetch('http://localhost:8000/chat/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      setSessionId(data.session_id);
      toast.success('🚀 Connected to Law Agent AI!');
    } catch (error) {
      console.error('Failed to initialize session:', error);
      toast.error('Failed to connect to Law Agent');
    }
  };

  const sendMessage = async (content: string) => {
    if (!content.trim() || !sessionId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: content,
        }),
      });

      const data = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: data.response,
        timestamp: new Date(),
        steps: data.steps || [],
        timeline: data.timeline || [],
        glossaryTerms: data.glossary_terms || [],
        visualData: data.visual_data || null,
      };

      setMessages(prev => [...prev, aiMessage]);
      setSelectedMessage(aiMessage);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const navigationItems = [
    { id: 'chat', label: 'Chat', icon: MessageSquare, description: 'AI Legal Assistant' },
    { id: 'court', label: 'Court Process', icon: Gavel, description: '3D Court Visualization' },
    { id: 'map', label: 'Jurisdiction', icon: Map, description: 'Legal Jurisdictions Map' },
    { id: 'timeline', label: 'Timeline', icon: Clock, description: 'Case Timeline' },
    { id: 'glossary', label: 'Glossary', icon: BookOpen, description: 'Legal Terms' },
  ];

  return (
    <div className="min-h-screen flex flex-col lg:flex-row relative">
      {/* Sidebar Navigation */}
      <motion.div
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        className="w-full lg:w-80 glass-dark border-r border-white/10 p-6 relative z-10"
      >
        {/* Logo and Title */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center space-x-4 mb-8"
        >
          <div className="relative">
            <motion.div
              className="w-16 h-16 legal-gradient rounded-2xl flex items-center justify-center shadow-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
            >
              <Scale className="h-8 w-8 text-white" />
            </motion.div>
            <motion.div
              className="absolute -top-1 -right-1 w-5 h-5 bg-green-500 rounded-full border-2 border-white"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
          <div>
            <h1 className="text-2xl font-bold legal-text-gradient">
              Law Agent AI
            </h1>
            <p className="text-sm text-gray-400">Advanced Legal Assistant</p>
          </div>
        </motion.div>

        {/* Navigation */}
        <nav className="space-y-2">
          {navigationItems.map((item, index) => (
            <motion.button
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => setCurrentView(item.id as any)}
              className={`w-full flex items-center space-x-4 p-4 rounded-xl transition-all duration-300 group ${
                currentView === item.id
                  ? 'bg-gradient-to-r from-primary-600/20 to-purple-600/20 border border-primary-500/30 shadow-lg'
                  : 'hover:bg-white/5 hover:border-white/10 border border-transparent'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <item.icon className={`h-6 w-6 transition-colors ${
                currentView === item.id ? 'text-primary-400' : 'text-gray-400 group-hover:text-white'
              }`} />
              <div className="text-left">
                <p className={`font-medium ${
                  currentView === item.id ? 'text-white' : 'text-gray-300 group-hover:text-white'
                }`}>
                  {item.label}
                </p>
                <p className="text-xs text-gray-500 group-hover:text-gray-400">
                  {item.description}
                </p>
              </div>
            </motion.button>
          ))}
        </nav>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8 space-y-4"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Session Stats</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="glass rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-primary-400">{messages.length}</div>
              <div className="text-xs text-gray-400">Messages</div>
            </div>
            <div className="glass rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-400">
                {messages.filter(m => m.type === 'ai').length}
              </div>
              <div className="text-xs text-gray-400">AI Responses</div>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col relative">
        <AnimatePresence mode="wait">
          {currentView === 'chat' && (
            <motion.div
              key="chat"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex-1 flex"
            >
              <div className="flex-1">
                <ChatInterface
                  messages={messages}
                  onSendMessage={sendMessage}
                  isLoading={isLoading}
                  ref={chatRef}
                />
              </div>
              {selectedMessage && (
                <div className="w-96 border-l border-white/10">
                  <ResponseModule message={selectedMessage} />
                </div>
              )}
            </motion.div>
          )}

          {currentView === 'court' && (
            <motion.div
              key="court"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex-1 relative bg-gradient-to-br from-slate-900/50 to-blue-900/30 backdrop-blur-sm"
            >
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Gavel className="h-24 w-24 text-primary-400 mx-auto mb-6 animate-pulse" />
                  <h2 className="text-3xl font-bold text-white mb-4">3D Court Visualization</h2>
                  <p className="text-gray-300 text-lg max-w-2xl">
                    Interactive 3D courtroom with legal process flow visualization.
                    Experience the complete court proceedings in immersive 3D.
                  </p>
                  <div className="mt-8 grid grid-cols-2 md:grid-cols-5 gap-4 max-w-4xl mx-auto">
                    {['Filing', 'Discovery', 'Motions', 'Trial', 'Verdict'].map((step, index) => (
                      <div key={step} className="legal-card p-4 text-center">
                        <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-purple-500 rounded-full mx-auto mb-2 flex items-center justify-center text-white text-sm font-bold">
                          {index + 1}
                        </div>
                        <p className="text-white font-medium text-sm">{step}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {currentView === 'map' && (
            <motion.div
              key="map"
              initial={{ opacity: 0, rotateY: 90 }}
              animate={{ opacity: 1, rotateY: 0 }}
              exit={{ opacity: 0, rotateY: -90 }}
              className="flex-1 relative bg-gradient-to-br from-slate-900/50 to-blue-900/30 backdrop-blur-sm"
            >
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Map className="h-24 w-24 text-primary-400 mx-auto mb-6 animate-pulse" />
                  <h2 className="text-3xl font-bold text-white mb-4">Jurisdictional Map</h2>
                  <p className="text-gray-300 text-lg max-w-2xl mb-8">
                    Interactive 3D visualization of the US court system hierarchy.
                    Explore federal, state, and local court jurisdictions.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
                    {[
                      { name: 'Supreme Court', cases: '150', color: 'from-red-500 to-pink-500' },
                      { name: 'Federal Courts', cases: '4,700', color: 'from-blue-500 to-cyan-500' },
                      { name: 'State Courts', cases: '8,100', color: 'from-green-500 to-emerald-500' },
                      { name: 'Local Courts', cases: '12,300', color: 'from-yellow-500 to-orange-500' }
                    ].map((court) => (
                      <div key={court.name} className="legal-card p-6 text-center">
                        <div className={`w-16 h-16 bg-gradient-to-r ${court.color} rounded-full mx-auto mb-4 flex items-center justify-center`}>
                          <Scale className="h-8 w-8 text-white" />
                        </div>
                        <h3 className="text-white font-bold text-lg mb-2">{court.name}</h3>
                        <p className="text-primary-400 font-semibold">{court.cases} cases</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {currentView === 'timeline' && (
            <motion.div
              key="timeline"
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              className="flex-1 p-6"
            >
              <LegalTimeline
                events={selectedMessage?.timeline || []}
                title="Case Timeline"
              />
            </motion.div>
          )}

          {currentView === 'glossary' && (
            <motion.div
              key="glossary"
              initial={{ opacity: 0, y: 100 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -100 }}
              className="flex-1 p-6"
            >
              <LegalGlossary
                terms={selectedMessage?.glossaryTerms || []}
                title="Legal Glossary"
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default LawAgentInterface;
