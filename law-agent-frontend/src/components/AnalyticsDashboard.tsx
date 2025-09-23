import React, { useState, useEffect, useRef } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
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
  Award
} from 'lucide-react';

// Import the ChatMessage interface
import { ChatMessage } from '../services/apiService';

interface AnalyticsData {
  basic_metrics: {
    unique_sessions: number;
    total_events: number;
    avg_response_time: number;
  };
  legal_routes: Array<{
    route_type: string;
    total_suggestions: number;
    accepted: number;
    rejected: number;
    acceptance_rate: number;
    avg_response_time: number;
    avg_satisfaction: number;
  }>;
  popular_glossary_terms: Array<{
    term: string;
    access_count: number;
    unique_sessions: number;
    avg_time_spent: number;
    avg_rating: number;
  }>;
  timeline_analysis: Array<{
    timeline_type: string;
    step_name: string;
    total_interactions: number;
    completed: number;
    completion_rate: number;
    avg_time_spent: number;
  }>;
}

interface AnalyticsDashboardProps {
  messages?: ChatMessage[];
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ messages = [] }) => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30');
  const [activeTab, setActiveTab] = useState('overview');
  const [realTimeData, setRealTimeData] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  // Colors for charts
  const colors = {
    primary: '#3B82F6',
    secondary: '#8B5CF6',
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    info: '#06B6D4'
  };

  const chartColors = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#06B6D4'];

  useEffect(() => {
    fetchAnalyticsData();
    setupWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [selectedTimeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      // For now, we'll use mock data since we don't have a real analytics endpoint
      // In a real implementation, this would fetch from your backend
      const mockData: AnalyticsData = {
        basic_metrics: {
          unique_sessions: messages.length > 0 ? Math.ceil(messages.length / 2) : 1247,
          total_events: messages.length,
          avg_response_time: 2450
        },
        legal_routes: [
          { route_type: 'Contract Law', total_suggestions: 42, accepted: 38, rejected: 4, acceptance_rate: 90.5, avg_response_time: 1.2, avg_satisfaction: 4.2 },
          { route_type: 'Family Law', total_suggestions: 36, accepted: 32, rejected: 4, acceptance_rate: 88.9, avg_response_time: 1.5, avg_satisfaction: 4.0 },
          { route_type: 'Criminal Law', total_suggestions: 28, accepted: 25, rejected: 3, acceptance_rate: 89.3, avg_response_time: 1.8, avg_satisfaction: 3.8 },
          { route_type: 'Property Law', total_suggestions: 22, accepted: 19, rejected: 3, acceptance_rate: 86.4, avg_response_time: 1.4, avg_satisfaction: 4.1 },
          { route_type: 'Employment Law', total_suggestions: 18, accepted: 16, rejected: 2, acceptance_rate: 88.9, avg_response_time: 1.3, avg_satisfaction: 4.3 }
        ],
        popular_glossary_terms: [
          { term: 'Affidavit', access_count: 124, unique_sessions: 98, avg_time_spent: 45, avg_rating: 4.2 },
          { term: 'Breach of Contract', access_count: 98, unique_sessions: 76, avg_time_spent: 62, avg_rating: 4.0 },
          { term: 'Due Process', access_count: 87, unique_sessions: 65, avg_time_spent: 58, avg_rating: 4.5 },
          { term: 'Felony', access_count: 76, unique_sessions: 58, avg_time_spent: 32, avg_rating: 3.8 },
          { term: 'Custody', access_count: 65, unique_sessions: 49, avg_time_spent: 71, avg_rating: 4.1 },
          { term: 'Easement', access_count: 54, unique_sessions: 42, avg_time_spent: 39, avg_rating: 3.9 }
        ],
        timeline_analysis: [
          { timeline_type: 'Civil Case', step_name: 'Filing', total_interactions: 124, completed: 118, completion_rate: 95.2, avg_time_spent: 2.1 },
          { timeline_type: 'Criminal Case', step_name: 'Investigation', total_interactions: 98, completed: 92, completion_rate: 93.9, avg_time_spent: 3.4 },
          { timeline_type: 'Family Case', step_name: 'Mediation', total_interactions: 87, completed: 78, completion_rate: 89.7, avg_time_spent: 4.2 },
          { timeline_type: 'Contract Dispute', step_name: 'Discovery', total_interactions: 76, completed: 72, completion_rate: 94.7, avg_time_spent: 2.8 }
        ]
      };
      
      setAnalyticsData(mockData);
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    try {
      // In a real implementation, you would connect to your WebSocket endpoint
      // For now, we'll simulate real-time data updates
      const interval = setInterval(() => {
        const mockEvent = {
          type: 'message',
          session_id: 'sess_' + Math.random().toString(36).substr(2, 9),
          timestamp: new Date()
        };
        setRealTimeData(prev => [...prev.slice(-50), { ...mockEvent, timestamp: new Date() }]);
      }, 5000);
      
      return () => clearInterval(interval);
    } catch (error) {
      console.error('Error setting up WebSocket:', error);
    }
  };

  const refreshData = () => {
    fetchAnalyticsData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Analytics Dashboard...</p>
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
              <h1 className="text-3xl font-bold text-white">Law Agent Analytics</h1>
              <p className="text-gray-300">Legal Team Dashboard & Performance Insights</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Time Range Selector */}
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
            </select>
            
            {/* Refresh Button */}
            <button
              onClick={refreshData}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Refresh</span>
            </button>
            
            {/* Export Button */}
            <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors">
              <Download className="h-4 w-4" />
              <span>Export</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-1 bg-white/10 rounded-xl p-1">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'legal-routes', label: 'Legal Routes', icon: Target },
            { id: 'glossary', label: 'Glossary', icon: BookOpen },
            { id: 'timeline', label: 'Timeline', icon: Clock },
            { id: 'realtime', label: 'Real-time', icon: Zap }
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
                  <p className="text-gray-300 text-sm">Total Sessions</p>
                  <p className="text-3xl font-bold text-white">{analyticsData.basic_metrics.unique_sessions}</p>
                </div>
                <div className="p-3 bg-blue-500/20 rounded-xl">
                  <Users className="h-6 w-6 text-blue-400" />
                </div>
              </div>
              <div className="flex items-center mt-4 text-green-400">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className="text-sm">+12% from last period</span>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Total Events</p>
                  <p className="text-3xl font-bold text-white">{analyticsData.basic_metrics.total_events}</p>
                </div>
                <div className="p-3 bg-purple-500/20 rounded-xl">
                  <Activity className="h-6 w-6 text-purple-400" />
                </div>
              </div>
              <div className="flex items-center mt-4 text-green-400">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className="text-sm">+8% from last period</span>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Avg Response Time</p>
                  <p className="text-3xl font-bold text-white">{analyticsData.basic_metrics.avg_response_time?.toFixed(0)}ms</p>
                </div>
                <div className="p-3 bg-green-500/20 rounded-xl">
                  <Zap className="h-6 w-6 text-green-400" />
                </div>
              </div>
              <div className="flex items-center mt-4 text-green-400">
                <TrendingDown className="h-4 w-4 mr-1" />
                <span className="text-sm">-5% faster</span>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-300 text-sm">Success Rate</p>
                  <p className="text-3xl font-bold text-white">94.2%</p>
                </div>
                <div className="p-3 bg-yellow-500/20 rounded-xl">
                  <Award className="h-6 w-6 text-yellow-400" />
                </div>
              </div>
              <div className="flex items-center mt-4 text-green-400">
                <TrendingUp className="h-4 w-4 mr-1" />
                <span className="text-sm">+2% improvement</span>
              </div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Legal Routes Acceptance Chart */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <Target className="h-5 w-5 text-blue-400" />
                <span>Legal Routes Performance</span>
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analyticsData.legal_routes}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="route_type" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Bar dataKey="acceptance_rate" fill={colors.primary} name="Acceptance Rate %" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Popular Glossary Terms */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-green-400" />
                <span>Top Glossary Terms</span>
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analyticsData.popular_glossary_terms.slice(0, 6)}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ term, access_count }) => `${term}: ${access_count}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="access_count"
                  >
                    {analyticsData.popular_glossary_terms.slice(0, 6).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Legal Routes Tab */}
      {activeTab === 'legal-routes' && analyticsData && (
        <div className="space-y-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center space-x-2">
              <Target className="h-5 w-5 text-blue-400" />
              <span>Legal Routes Analytics</span>
            </h3>
            
            {/* Legal Routes Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-gray-300 font-medium py-3">Route Type</th>
                    <th className="text-gray-300 font-medium py-3">Suggestions</th>
                    <th className="text-gray-300 font-medium py-3">Accepted</th>
                    <th className="text-gray-300 font-medium py-3">Rejected</th>
                    <th className="text-gray-300 font-medium py-3">Acceptance Rate</th>
                    <th className="text-gray-300 font-medium py-3">Avg Response Time</th>
                    <th className="text-gray-300 font-medium py-3">Satisfaction</th>
                  </tr>
                </thead>
                <tbody>
                  {analyticsData.legal_routes.map((route, index) => (
                    <tr key={index} className="border-b border-white/10 hover:bg-white/5">
                      <td className="text-white py-4 font-medium">{route.route_type.replace('_', ' ').toUpperCase()}</td>
                      <td className="text-gray-300 py-4">{route.total_suggestions}</td>
                      <td className="text-green-400 py-4">{route.accepted}</td>
                      <td className="text-red-400 py-4">{route.rejected}</td>
                      <td className="text-white py-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-16 bg-gray-700 rounded-full h-2">
                            <div 
                              className="bg-blue-500 h-2 rounded-full" 
                              style={{ width: `${route.acceptance_rate}%` }}
                            ></div>
                          </div>
                          <span>{route.acceptance_rate.toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="text-gray-300 py-4">{route.avg_response_time?.toFixed(1)}s</td>
                      <td className="text-yellow-400 py-4">
                        {route.avg_satisfaction ? `${route.avg_satisfaction.toFixed(1)}/5` : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Real-time Tab */}
      {activeTab === 'realtime' && (
        <div className="space-y-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
              <Zap className="h-5 w-5 text-yellow-400" />
              <span>Real-time Activity</span>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </h3>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {realTimeData.slice(-20).reverse().map((event, index) => (
                <div key={index} className="bg-white/5 rounded-lg p-3 border border-white/10">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      <span className="text-white font-medium">{event.type}</span>
                      {event.session_id && (
                        <span className="text-gray-400 text-sm">Session: {event.session_id.slice(-8)}</span>
                      )}
                    </div>
                    <span className="text-gray-400 text-sm">
                      {event.timestamp?.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}
              
              {realTimeData.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  <Activity className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>Waiting for real-time events...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;