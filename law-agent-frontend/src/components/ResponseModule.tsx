import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown,
  ChevronRight,
  CheckCircle,
  Clock,
  AlertCircle,
  BookOpen,
  FileText,
  Scale,
  Lightbulb,
  Target,
  TrendingUp
} from 'lucide-react';
import { Message, TimelineEvent, GlossaryTerm } from '../types';

interface ResponseModuleProps {
  message: Message;
}

const ResponseModule: React.FC<ResponseModuleProps> = ({ message }) => {
  const [activeTab, setActiveTab] = useState<'steps' | 'timeline' | 'glossary' | 'insights'>('steps');
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());
  const [expandedTerms, setExpandedTerms] = useState<Set<string>>(new Set());

  const toggleStep = (index: number) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSteps(newExpanded);
  };

  const toggleTerm = (term: string) => {
    const newExpanded = new Set(expandedTerms);
    if (newExpanded.has(term)) {
      newExpanded.delete(term);
    } else {
      newExpanded.add(term);
    }
    setExpandedTerms(newExpanded);
  };

  const getTimelineIcon = (type: string) => {
    switch (type) {
      case 'filing': return FileText;
      case 'hearing': return Scale;
      case 'decision': return CheckCircle;
      case 'deadline': return Clock;
      default: return AlertCircle;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-400/20';
      case 'pending': return 'text-yellow-400 bg-yellow-400/20';
      case 'upcoming': return 'text-blue-400 bg-blue-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
  };

  const tabs = [
    { id: 'steps', label: 'Steps', icon: Target, count: message.steps?.length || 0 },
    { id: 'timeline', label: 'Timeline', icon: Clock, count: message.timeline?.length || 0 },
    { id: 'glossary', label: 'Terms', icon: BookOpen, count: message.glossaryTerms?.length || 0 },
    { id: 'insights', label: 'Insights', icon: Lightbulb, count: 0 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="h-full glass-dark border-l border-white/10 flex flex-col"
    >
      {/* Header */}
      <div className="p-6 border-b border-white/10">
        <h3 className="text-lg font-semibold text-white mb-2">Response Analysis</h3>
        <p className="text-sm text-gray-400">
          Detailed breakdown and supporting information
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/10">
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex-1 flex items-center justify-center space-x-2 p-4 transition-all duration-300 ${
              activeTab === tab.id
                ? 'bg-primary-600/20 border-b-2 border-primary-500 text-primary-400'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            <span className="text-sm font-medium">{tab.label}</span>
            {tab.count > 0 && (
              <span className={`text-xs px-2 py-1 rounded-full ${
                activeTab === tab.id ? 'bg-primary-500 text-white' : 'bg-gray-600 text-gray-300'
              }`}>
                {tab.count}
              </span>
            )}
          </motion.button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <AnimatePresence mode="wait">
          {/* Steps Tab */}
          {activeTab === 'steps' && (
            <motion.div
              key="steps"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {message.steps && message.steps.length > 0 ? (
                message.steps.map((step, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="glass rounded-lg border border-white/10"
                  >
                    <button
                      onClick={() => toggleStep(index)}
                      className="w-full flex items-center justify-between p-4 text-left hover:bg-white/5 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                          {index + 1}
                        </div>
                        <span className="text-white font-medium">
                          Step {index + 1}
                        </span>
                      </div>
                      {expandedSteps.has(index) ? (
                        <ChevronDown className="h-5 w-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                    
                    <AnimatePresence>
                      {expandedSteps.has(index) && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="px-4 pb-4"
                        >
                          <div className="pl-11 text-gray-300 text-sm leading-relaxed">
                            {step}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12">
                  <Target className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No steps available for this response</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Timeline Tab */}
          {activeTab === 'timeline' && (
            <motion.div
              key="timeline"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {message.timeline && message.timeline.length > 0 ? (
                <div className="relative">
                  <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary-500 to-purple-500"></div>
                  {message.timeline.map((event, index) => {
                    const Icon = getTimelineIcon(event.type);
                    return (
                      <motion.div
                        key={event.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="relative flex items-start space-x-4"
                      >
                        <div className={`relative z-10 w-12 h-12 rounded-full flex items-center justify-center ${getStatusColor(event.status)}`}>
                          <Icon className="h-5 w-5" />
                        </div>
                        <div className="flex-1 glass rounded-lg p-4 border border-white/10">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="text-white font-medium">{event.title}</h4>
                            <span className="text-xs text-gray-400">{event.date}</span>
                          </div>
                          <p className="text-gray-300 text-sm">{event.description}</p>
                          <div className="mt-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(event.status)}`}>
                              {event.status.charAt(0).toUpperCase() + event.status.slice(1)}
                            </span>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Clock className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No timeline events available</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Glossary Tab */}
          {activeTab === 'glossary' && (
            <motion.div
              key="glossary"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-3"
            >
              {message.glossaryTerms && message.glossaryTerms.length > 0 ? (
                message.glossaryTerms.map((term, index) => (
                  <motion.div
                    key={term.term}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="glass rounded-lg border border-white/10"
                  >
                    <button
                      onClick={() => toggleTerm(term.term)}
                      className="w-full flex items-center justify-between p-4 text-left hover:bg-white/5 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                        <span className="text-white font-medium">{term.term}</span>
                        <span className="text-xs px-2 py-1 bg-primary-500/20 text-primary-400 rounded-full">
                          {term.category}
                        </span>
                      </div>
                      {expandedTerms.has(term.term) ? (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronRight className="h-4 w-4 text-gray-400" />
                      )}
                    </button>
                    
                    <AnimatePresence>
                      {expandedTerms.has(term.term) && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="px-4 pb-4"
                        >
                          <div className="pl-5 text-gray-300 text-sm leading-relaxed">
                            {term.definition}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12">
                  <BookOpen className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">No glossary terms available</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Insights Tab */}
          {activeTab === 'insights' && (
            <motion.div
              key="insights"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              <div className="glass rounded-lg p-6 border border-white/10">
                <div className="flex items-center space-x-3 mb-4">
                  <TrendingUp className="h-6 w-6 text-green-400" />
                  <h4 className="text-lg font-semibold text-white">Key Insights</h4>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                    <div>
                      <p className="text-white font-medium">Response Confidence</p>
                      <p className="text-gray-400 text-sm">High confidence based on legal precedents</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2"></div>
                    <div>
                      <p className="text-white font-medium">Complexity Level</p>
                      <p className="text-gray-400 text-sm">Moderate - may require professional consultation</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                    <div>
                      <p className="text-white font-medium">Jurisdiction</p>
                      <p className="text-gray-400 text-sm">Federal and state law applicable</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="glass rounded-lg p-6 border border-white/10">
                <div className="flex items-center space-x-3 mb-4">
                  <Lightbulb className="h-6 w-6 text-yellow-400" />
                  <h4 className="text-lg font-semibold text-white">Recommendations</h4>
                </div>
                
                <ul className="space-y-2 text-gray-300 text-sm">
                  <li className="flex items-start space-x-2">
                    <span className="text-primary-400">•</span>
                    <span>Consider consulting with a qualified attorney</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-primary-400">•</span>
                    <span>Document all relevant communications and evidence</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-primary-400">•</span>
                    <span>Review applicable statutes of limitations</span>
                  </li>
                </ul>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default ResponseModule;
