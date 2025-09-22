import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Calendar,
  Clock,
  AlertCircle,
  FileText,
  Scale,
  Gavel,
  Users,
  ChevronDown,
  ChevronRight,
  Filter,
  Search,
  Download,
  Printer,
  Share2,
  Bookmark,
  Star,
  Info
} from 'lucide-react';
import { TimelineEvent } from '../types';

interface LegalTimelineProps {
  events: TimelineEvent[];
  title: string;
}

const LegalTimeline: React.FC<LegalTimelineProps> = ({ events, title }) => {
  const [filteredEvents, setFilteredEvents] = useState<TimelineEvent[]>(events);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedEvents, setExpandedEvents] = useState<Set<string>>(new Set());
  const [bookmarkedEvents, setBookmarkedEvents] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<'date' | 'importance'>('date');

  // Get unique event types for filter dropdown
  const eventTypes = useMemo(() => {
    const types = Array.from(new Set(events.map(event => event.type)));
    return types.sort();
  }, [events]);

  // Get unique statuses for filter dropdown
  const statuses = useMemo(() => {
    const statuses = Array.from(new Set(events.map(event => event.status)));
    return statuses.sort();
  }, [events]);

  useEffect(() => {
    let filtered = [...events];

    // Filter by type
    if (filterType !== 'all') {
      filtered = filtered.filter(event => event.type === filterType);
    }

    // Filter by status
    if (filterStatus !== 'all') {
      filtered = filtered.filter(event => event.status === filterStatus);
    }

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(event =>
        event.title.toLowerCase().includes(term) ||
        event.description.toLowerCase().includes(term) ||
        (event.participants && event.participants.some(p => p.toLowerCase().includes(term))) ||
        (event.documents && event.documents.some(d => d.toLowerCase().includes(term)))
      );
    }

    // Sort events
    filtered.sort((a, b) => {
      if (sortBy === 'importance') {
        const importanceOrder: Record<string, number> = { 
          'critical': 4, 
          'high': 3, 
          'medium': 2, 
          'low': 1 
        };
        return (importanceOrder[b.importance] || 0) - (importanceOrder[a.importance] || 0);
      } else {
        return new Date(a.date).getTime() - new Date(b.date).getTime();
      }
    });

    setFilteredEvents(filtered);
  }, [events, filterType, filterStatus, searchTerm, sortBy]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'filing': return FileText;
      case 'hearing': return Scale;
      case 'decision': return Gavel;
      case 'deadline': return Clock;
      case 'motion': return FileText;
      case 'discovery': return Search;
      default: return AlertCircle;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-400/20 border-green-400/30';
      case 'pending': return 'text-yellow-400 bg-yellow-400/20 border-yellow-400/30';
      case 'upcoming': return 'text-blue-400 bg-blue-400/20 border-blue-400/30';
      case 'overdue': return 'text-red-400 bg-red-400/20 border-red-400/30';
      default: return 'text-gray-400 bg-gray-400/20 border-gray-400/30';
    }
  };

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'critical': return 'border-l-red-500';
      case 'high': return 'border-l-orange-500';
      case 'medium': return 'border-l-yellow-500';
      case 'low': return 'border-l-blue-500';
      default: return 'border-l-gray-500';
    }
  };

  const getImportanceBadgeColor = (importance: string) => {
    switch (importance) {
      case 'critical': return 'bg-red-500/20 text-red-400';
      case 'high': return 'bg-orange-500/20 text-orange-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      case 'low': return 'bg-blue-500/20 text-blue-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const toggleEventExpansion = (eventId: string) => {
    const newExpanded = new Set(expandedEvents);
    if (newExpanded.has(eventId)) {
      newExpanded.delete(eventId);
    } else {
      newExpanded.add(eventId);
    }
    setExpandedEvents(newExpanded);
  };

  const toggleBookmark = (eventId: string) => {
    const newBookmarked = new Set(bookmarkedEvents);
    if (newBookmarked.has(eventId)) {
      newBookmarked.delete(eventId);
    } else {
      newBookmarked.add(eventId);
    }
    setBookmarkedEvents(newBookmarked);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 30) return `${diffInDays}d ago`;
    const diffInMonths = Math.floor(diffInDays / 30);
    return `${diffInMonths}mo ago`;
  };

  // Sample events if none provided
  const sampleEvents: TimelineEvent[] = [
    {
      id: '1',
      title: 'Initial Complaint Filed',
      description: 'Plaintiff filed initial complaint against defendant for breach of contract',
      date: '2024-01-15T09:00:00Z',
      type: 'filing',
      status: 'completed',
      participants: ['Plaintiff Attorney', 'Court Clerk'],
      documents: ['Complaint.pdf', 'Summons.pdf'],
      importance: 'high'
    },
    {
      id: '2',
      title: 'Defendant Response Due',
      description: 'Deadline for defendant to file answer or motion to dismiss',
      date: '2024-02-15T17:00:00Z',
      type: 'deadline',
      status: 'upcoming',
      participants: ['Defense Attorney'],
      documents: [],
      importance: 'critical'
    },
    {
      id: '3',
      title: 'Discovery Conference',
      description: 'Initial discovery conference to establish timeline and scope',
      date: '2024-03-01T10:00:00Z',
      type: 'hearing',
      status: 'upcoming',
      participants: ['Judge', 'Plaintiff Attorney', 'Defense Attorney'],
      documents: ['Discovery_Plan.pdf'],
      importance: 'medium'
    }
  ];

  const displayEvents = filteredEvents.length > 0 ? filteredEvents : sampleEvents;

  // Export timeline as CSV
  const exportTimeline = () => {
    const headers = ['Title', 'Description', 'Date', 'Type', 'Status', 'Importance', 'Participants', 'Documents'];
    const rows = displayEvents.map(event => [
      event.title,
      event.description,
      event.date,
      event.type,
      event.status,
      event.importance,
      event.participants ? event.participants.join('; ') : '',
      event.documents ? event.documents.join('; ') : ''
    ]);
    
    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
      csvContent += row.map(field => `"${field}"`).join(',') + '\n';
    });
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'legal_timeline.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-900/50 to-blue-900/30 backdrop-blur-sm">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-dark border-b border-white/10 p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Calendar className="h-6 w-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{title}</h2>
              <p className="text-gray-400 text-sm">Track important legal events and deadlines</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <span>{displayEvents.length} events</span>
            <div className="w-1 h-1 bg-gray-500 rounded-full"></div>
            <span>{bookmarkedEvents.size} bookmarked</span>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="glass rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              {eventTypes.map(type => (
                <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
              ))}
            </select>
          </div>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="glass rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            {statuses.map(status => (
              <option key={status} value={status}>{status.charAt(0).toUpperCase() + status.slice(1)}</option>
              ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'importance')}
            className="glass rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-blue-500"
          >
            <option value="date">Sort by Date</option>
            <option value="importance">Sort by Importance</option>
          </select>

          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search events..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 glass rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex space-x-2">
            <button
              onClick={exportTimeline}
              className="glass p-2 text-gray-400 hover:text-white rounded-lg transition-colors"
              title="Export timeline"
            >
              <Download className="h-4 w-4" />
            </button>
            <button className="glass p-2 text-gray-400 hover:text-white rounded-lg transition-colors" title="Print timeline">
              <Printer className="h-4 w-4" />
            </button>
            <button className="glass p-2 text-gray-400 hover:text-white rounded-lg transition-colors" title="Share timeline">
              <Share2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 to-purple-500"></div>

          {/* Events */}
          <div className="space-y-6">
            <AnimatePresence>
              {displayEvents.map((event, index) => {
                const Icon = getEventIcon(event.type);
                const isExpanded = expandedEvents.has(event.id);
                const isBookmarked = bookmarkedEvents.has(event.id);

                return (
                  <motion.div
                    key={event.id}
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 50 }}
                    transition={{ delay: index * 0.1 }}
                    className="relative flex items-start space-x-6"
                  >
                    {/* Timeline Node */}
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center ${getStatusColor(event.status)} border-2 cursor-pointer`}
                      onClick={() => toggleEventExpansion(event.id)}
                    >
                      <Icon className="h-6 w-6" />
                      {isBookmarked && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-400 rounded-full flex items-center justify-center">
                          <Star className="h-3 w-3 text-yellow-900 fill-current" />
                        </div>
                      )}
                    </motion.div>

                    {/* Event Card */}
                    <motion.div
                      whileHover={{ scale: 1.02 }}
                      className={`flex-1 glass rounded-xl p-6 border-l-4 ${getImportanceColor(event.importance)} cursor-pointer`}
                      onClick={() => toggleEventExpansion(event.id)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-start justify-between">
                            <h3 className="text-lg font-semibold text-white mb-1">
                              {event.title}
                            </h3>
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleBookmark(event.id);
                              }}
                              className="ml-2 text-gray-400 hover:text-yellow-400 transition-colors"
                            >
                              <Bookmark className={`h-4 w-4 ${isBookmarked ? 'fill-current text-yellow-400' : ''}`} />
                            </button>
                          </div>
                          <p className="text-gray-300 text-sm mb-3">
                            {event.description}
                          </p>
                          <div className="flex flex-wrap items-center gap-3 text-xs text-gray-400">
                            <span className="flex items-center space-x-1">
                              <Calendar className="h-3 w-3" />
                              <span>{formatDate(event.date)}</span>
                            </span>
                            <span className="flex items-center space-x-1">
                              <Clock className="h-3 w-3" />
                              <span>{formatTimeAgo(event.date)}</span>
                            </span>
                            <span className={`px-2 py-1 rounded-full ${getStatusColor(event.status)}`}>
                              {event.status}
                            </span>
                            <span className="capitalize">{event.type}</span>
                            <span className={`px-2 py-1 rounded ${getImportanceBadgeColor(event.importance)}`}>
                              {event.importance}
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-4">
                          {isExpanded ? (
                            <ChevronDown className="h-5 w-5 text-gray-400" />
                          ) : (
                            <ChevronRight className="h-5 w-5 text-gray-400" />
                          )}
                        </div>
                      </div>

                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="border-t border-white/10 pt-4 mt-4"
                          >
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {event.participants && event.participants.length > 0 && (
                                <div>
                                  <h4 className="text-sm font-medium text-white mb-2 flex items-center">
                                    <Users className="h-4 w-4 mr-2" />
                                    Participants
                                  </h4>
                                  <div className="flex flex-wrap gap-2">
                                    {event.participants.map((participant, idx) => (
                                      <span
                                        key={idx}
                                        className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full"
                                      >
                                        {participant}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {event.documents && event.documents.length > 0 && (
                                <div>
                                  <h4 className="text-sm font-medium text-white mb-2 flex items-center">
                                    <FileText className="h-4 w-4 mr-2" />
                                    Documents
                                  </h4>
                                  <div className="space-y-1">
                                    {event.documents.map((doc, idx) => (
                                      <div
                                        key={idx}
                                        className="text-xs text-gray-300 hover:text-blue-400 cursor-pointer flex items-center space-x-2 group"
                                      >
                                        <FileText className="h-3 w-3" />
                                        <span className="group-hover:underline">{doc}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>

                            <div className="mt-4 flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <Info className="h-4 w-4 text-gray-400" />
                                <span className="text-xs text-gray-400">
                                  Click on the timeline node to collapse this event
                                </span>
                              </div>
                              <div className="flex space-x-2">
                                <button className="text-xs bg-gray-600/30 hover:bg-gray-600/50 text-gray-300 px-2 py-1 rounded transition-colors">
                                  Add Reminder
                                </button>
                                <button className="text-xs bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 px-2 py-1 rounded transition-colors">
                                  Add Note
                                </button>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </motion.div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>

          {displayEvents.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <Calendar className="h-16 w-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-400 mb-2">
                No Events Found
              </h3>
              <p className="text-gray-500">
                No timeline events match your current filters.
              </p>
              <button 
                onClick={() => {
                  setFilterType('all');
                  setFilterStatus('all');
                  setSearchTerm('');
                }}
                className="mt-4 text-sm bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 px-4 py-2 rounded-lg transition-colors"
              >
                Clear Filters
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LegalTimeline;