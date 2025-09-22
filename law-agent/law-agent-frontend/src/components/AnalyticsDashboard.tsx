import React, { useState, useEffect, useMemo } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Users,
  BookOpen,
  Clock,
  Activity,
  BarChart3,
  Download,
  RefreshCw,
  Target,
  Zap,
  Award,
  FileText,
  Scale,
  Gavel,
  Home,
  Briefcase
} from 'lucide-react';
import { Message, GlossaryTerm, TimelineEvent } from '../types';

interface AnalyticsDashboardProps {
  messages?: Message[];
}

interface AnalyticsData {
  basic_metrics: {
    total_chats: number;
    total_messages: number;
    avg_response_length: number;
    legal_domains: Record<string, number>;
  };
  legal_routes: Array<{
    domain: string;
    count: number;
    avg_terms: number;
  }>;
  popular_glossary_terms: Array<{
    term: string;
    count: number;
    domain: string;
  }>;
  timeline_analysis: Array<{
    event_type: string;
    count: number;
    avg_duration: number;
  }>;
}

// Simple chart components for demonstration
const SimpleBarChart: React.FC<{ data: any[]; dataKey: string; nameKey: string }> = ({ data, dataKey, nameKey }) => {
  const maxValue = Math.max(...data.map(item => item[dataKey]), 0);
  
  return (
    <div className="space-y-2">
      {data.map((item, index) => (
        <div key={index} className="flex items-center">
          <div className="w-24 text-sm text-gray-300 truncate">{item[nameKey]}</div>
          <div className="flex-1 ml-2">
            <div 
              className="h-6 bg-blue-500 rounded-md flex items-center justify-end pr-2 text-white text-xs"
              style={{ width: `${maxValue ? (item[dataKey] / maxValue) * 100 : 0}%` }}
            >
              {item[dataKey]}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

const SimplePieChart: React.FC<{ data: any[]; dataKey: string; nameKey: string; colors: string[] }> = ({ 
  data, 
  dataKey, 
  nameKey,
  colors
}) => {
  const total = data.reduce((sum, item) => sum + item[dataKey], 0);
  
  return (
    <div className="space-y-3">
      {data.map((item, index) => {
        const percentage = total ? Math.round((item[dataKey] / total) * 100) : 0;
        return (
          <div key={index} className="flex items-center">
            <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: colors[index % colors.length] }}></div>
            <div className="w-24 text-sm text-gray-300 truncate">{item[nameKey]}</div>
            <div className="flex-1 ml-2">
              <div className="text-xs text-gray-400">{percentage}% ({item[dataKey]})</div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ messages = [] }) => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('all');

  // Colors for charts
  const chartColors = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#06B6D4'];

  // Process messages to generate analytics data
  const processAnalyticsData = useMemo(() => {
    if (!messages || messages.length === 0) {
      return null;
    }

    // Filter AI messages
    const aiMessages = messages.filter(msg => msg.type === 'ai');
    
    // Basic metrics
    const totalChats = 1; // Since we're looking at one chat session
    const totalMessages = messages.length;
    const avgResponseLength = aiMessages.reduce((sum, msg) => sum + msg.content.length, 0) / aiMessages.length || 0;
    
    // Legal domains
    const legalDomains: Record<string, number> = {};
    aiMessages.forEach(msg => {
      if (msg.structuredData?.domain) {
        const domain = msg.structuredData.domain;
        legalDomains[domain] = (legalDomains[domain] || 0) + 1;
      }
    });

    // Legal routes analysis
    const legalRoutes: Record<string, { count: number; terms: number }> = {};
    let totalGlossaryTerms = 0;
    
    aiMessages.forEach(msg => {
      if (msg.structuredData?.domain) {
        const domain = msg.structuredData.domain;
        if (!legalRoutes[domain]) {
          legalRoutes[domain] = { count: 0, terms: 0 };
        }
        legalRoutes[domain].count += 1;
        
        if (msg.glossaryTerms) {
          legalRoutes[domain].terms += msg.glossaryTerms.length;
          totalGlossaryTerms += msg.glossaryTerms.length;
        }
      }
    });

    // Popular glossary terms
    const termCount: Record<string, { count: number; domain: string }> = {};
    aiMessages.forEach(msg => {
      if (msg.glossaryTerms) {
        const domain = msg.structuredData?.domain || 'general';
        msg.glossaryTerms.forEach(term => {
          if (!termCount[term.term]) {
            termCount[term.term] = { count: 0, domain };
          }
          termCount[term.term].count += 1;
        });
      }
    });

    const popularTerms = Object.entries(termCount)
      .map(([term, data]) => ({
        term,
        count: data.count,
        domain: data.domain
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Timeline analysis
    const eventTypeCount: Record<string, { count: number; duration: number }> = {};
    let totalTimelineEvents = 0;
    
    aiMessages.forEach(msg => {
      if (msg.timeline) {
        msg.timeline.forEach(event => {
          if (!eventTypeCount[event.type]) {
            eventTypeCount[event.type] = { count: 0, duration: 0 };
          }
          eventTypeCount[event.type].count += 1;
          totalTimelineEvents += 1;
        });
      }
    });

    const timelineAnalysis = Object.entries(eventTypeCount)
      .map(([type, data]) => ({
        event_type: type,
        count: data.count,
        avg_duration: 0 // Simplified for now
      }));

    return {
      basic_metrics: {
        total_chats: totalChats,
        total_messages: totalMessages,
        avg_response_length: Math.round(avgResponseLength),
        legal_domains: legalDomains
      },
      legal_routes: Object.entries(legalRoutes).map(([domain, data]) => ({
        domain,
        count: data.count,
        avg_terms: data.terms / data.count || 0
      })),
      popular_glossary_terms: popularTerms,
      timeline_analysis: timelineAnalysis
    };
  }, [messages]);

  useEffect(() => {
    if (processAnalyticsData) {
      setAnalyticsData(processAnalyticsData);
      setLoading(false);
    } else {
      // Set default data if no messages
      setAnalyticsData({
        basic_metrics: {
          total_chats: 0,
          total_messages: 0,
          avg_response_length: 0,
          legal_domains: {}
        },
        legal_routes: [],
        popular_glossary_terms: [],
        timeline_analysis: []
      });
      setLoading(false);
    }
  }, [processAnalyticsData]);

  const refreshData = () => {
    // In a real app, this would fetch new data
    // For now, we'll just reprocess the existing data
  };

  // Get domain icon
  const getDomainIcon = (domain: string) => {
    switch (domain.toLowerCase()) {
      case 'criminal_law': return <Gavel className="h-4 w-4" />;
      case 'civil_law': return <Scale className="h-4 w-4" />;
      case 'family_law': return <Users className="h-4 w-4" />;
      case 'employment_law': return <Briefcase className="h-4 w-4" />;
      case 'property_law': return <Home className="h-4 w-4" />;
      case 'contract_law': return <FileText className="h-4 w-4" />;
      default: return <BookOpen className="h-4 w-4" />;
    }
  };

  // Get domain color
  const getDomainColor = (domain: string) => {
    switch (domain.toLowerCase()) {
      case 'criminal_law': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'civil_law': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'family_law': return 'bg-pink-500/20 text-pink-400 border-pink-500/30';
      case 'employment_law': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'property_law': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'contract_law': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Analyzing Legal Interactions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-blue-500/20 rounded-xl">
              <BarChart3 className="h-8 w-8 text-blue-400" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Legal Analytics Dashboard</h1>
              <p className="text-gray-300">Insights from your legal interactions</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="session">Current Session</option>
              <option value="all">All Time</option>
            </select>
            
            {/* Refresh Button */}
            <button
              onClick={refreshData}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-1 bg-white/10 rounded-xl p-1">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'legal-routes', label: 'Legal Domains', icon: Target },
            { id: 'glossary', label: 'Glossary', icon: BookOpen },
            { id: 'timeline', label: 'Timeline', icon: Clock }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-white/10'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && analyticsData && (
        <div className="space-y-6">
          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Total Messages</p>
                  <p className="text-3xl font-bold text-white">{analyticsData.basic_metrics.total_messages}</p>
                </div>
                <div className="p-3 bg-blue-500/20 rounded-xl">
                  <Activity className="h-6 w-6 text-blue-400" />
                </div>
              </div>
              <div className="flex items-center mt-4 text-green-400">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className="text-sm">Active Session</span>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Avg. Response Length</p>
                  <p className="text-3xl font-bold text-white">{analyticsData.basic_metrics.avg_response_length}</p>
                </div>
                <div className="p-3 bg-purple-500/20 rounded-xl">
                  <FileText className="h-6 w-6 text-purple-400" />
                </div>
              </div>
              <div className="flex items-center mt-4 text-green-400">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className="text-sm">Characters</span>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Glossary Terms</p>
                  <p className="text-3xl font-bold text-white">{analyticsData.popular_glossary_terms.length}</p>
                </div>
                <div className="p-3 bg-green-500/20 rounded-xl">
                  <BookOpen className="h-6 w-6 text-green-400" />
                </div>
              </div>
              <div className="flex items-center mt-4 text-green-400">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className="text-sm">Terms</span>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Legal Domains</p>
                  <p className="text-3xl font-bold text-white">{Object.keys(analyticsData.basic_metrics.legal_domains).length}</p>
                </div>
                <div className="p-3 bg-yellow-500/20 rounded-xl">
                  <Target className="h-6 w-6 text-yellow-400" />
                </div>
              </div>
              <div className="flex items-center mt-4 text-green-400">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className="text-sm">Domains</span>
              </div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Legal Domains Distribution */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Target className="h-5 w-5 text-blue-400" />
                <span>Legal Domains Distribution</span>
              </h3>
              {Object.keys(analyticsData.basic_metrics.legal_domains).length > 0 ? (
                <div className="h-80">
                  <SimpleBarChart 
                    data={Object.entries(analyticsData.basic_metrics.legal_domains).map(([domain, count]) => ({
                      domain: domain.replace('_', ' '),
                      count
                    }))}
                    dataKey="count"
                    nameKey="domain"
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  <p>No legal domain data available</p>
                </div>
              )}
            </div>

            {/* Popular Glossary Terms */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-green-400" />
                <span>Popular Glossary Terms</span>
              </h3>
              {analyticsData.popular_glossary_terms.length > 0 ? (
                <div className="h-80">
                  <SimplePieChart 
                    data={analyticsData.popular_glossary_terms}
                    dataKey="count"
                    nameKey="term"
                    colors={chartColors}
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-500">
                  <p>No glossary terms data available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Legal Domains Tab */}
      {activeTab === 'legal-routes' && analyticsData && (
        <div className="space-y-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
              <Target className="h-5 w-5 text-blue-400" />
              <span>Legal Domains Analysis</span>
            </h3>
            
            {analyticsData.legal_routes.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-white/20">
                      <th className="text-gray-300 font-medium py-3">Legal Domain</th>
                      <th className="text-gray-300 font-medium py-3">Messages</th>
                      <th className="text-gray-300 font-medium py-3">Avg. Glossary Terms</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analyticsData.legal_routes.map((route, index) => (
                      <tr key={index} className="border-b border-white/10 hover:bg-white/5">
                        <td className="text-white py-4 font-medium flex items-center space-x-2">
                          <span className={`p-2 rounded-lg ${getDomainColor(route.domain)}`}>
                            {getDomainIcon(route.domain)}
                          </span>
                          <span>{route.domain.replace('_', ' ')}</span>
                        </td>
                        <td className="text-gray-300 py-4">{route.count}</td>
                        <td className="text-gray-300 py-4">{route.avg_terms.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Target className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No legal domain data available</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Glossary Tab */}
      {activeTab === 'glossary' && analyticsData && (
        <div className="space-y-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
              <BookOpen className="h-5 w-5 text-green-400" />
              <span>Popular Glossary Terms</span>
            </h3>
            
            {analyticsData.popular_glossary_terms.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analyticsData.popular_glossary_terms.map((term, index) => (
                  <div 
                    key={index} 
                    className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium">{term.term}</h4>
                      <span className={`text-xs px-2 py-1 rounded ${getDomainColor(term.domain)}`}>
                        {term.domain.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-blue-400">{term.count}</p>
                    <p className="text-gray-400 text-sm">mentions</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <BookOpen className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No glossary terms data available</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Timeline Tab */}
      {activeTab === 'timeline' && analyticsData && (
        <div className="space-y-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
              <Clock className="h-5 w-5 text-yellow-400" />
              <span>Timeline Event Analysis</span>
            </h3>
            
            {analyticsData.timeline_analysis.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-white/20">
                      <th className="text-gray-300 font-medium py-3">Event Type</th>
                      <th className="text-gray-300 font-medium py-3">Count</th>
                      <th className="text-gray-300 font-medium py-3">Avg. Duration</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analyticsData.timeline_analysis.map((event, index) => (
                      <tr key={index} className="border-b border-white/10 hover:bg-white/5">
                        <td className="text-white py-4 font-medium capitalize">{event.event_type.replace('_', ' ')}</td>
                        <td className="text-gray-300 py-4">{event.count}</td>
                        <td className="text-gray-300 py-4">{event.avg_duration} days</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Clock className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No timeline data available</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;