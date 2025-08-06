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

const AnalyticsDashboard: React.FC = () => {
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
      const response = await fetch(`http://localhost:8002/analytics/summary?days=${selectedTimeRange}`);
      const result = await response.json();
      
      if (result.success) {
        setAnalyticsData(result.data);
      }
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    try {
      wsRef.current = new WebSocket('ws://localhost:8002/ws');
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setRealTimeData(prev => [...prev.slice(-50), { ...data, timestamp: new Date() }]);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
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
