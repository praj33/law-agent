import React, { useState, useEffect } from 'react';
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
  Search
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

  useEffect(() => {
    let filtered = events;

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
      filtered = filtered.filter(event =>
        event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Sort by date
    filtered.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    setFilteredEvents(filtered);
  }, [events, filterType, filterStatus, searchTerm]);

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

  const toggleEventExpansion = (eventId: string) => {
    const newExpanded = new Set(expandedEvents);
    if (newExpanded.has(eventId)) {
      newExpanded.delete(eventId);
    } else {
      newExpanded.add(eventId);
    }
    setExpandedEvents(newExpanded);
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
            <Calendar className="h-8 w-8 text-primary-400" />
            <h2 className="text-2xl font-bold text-white">{title}</h2>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <span>{displayEvents.length} events</span>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="glass rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Types</option>
              <option value="filing">Filing</option>
              <option value="hearing">Hearing</option>
              <option value="decision">Decision</option>
              <option value="deadline">Deadline</option>
              <option value="motion">Motion</option>
              <option value="discovery">Discovery</option>
            </select>
          </div>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="glass rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="pending">Pending</option>
            <option value="upcoming">Upcoming</option>
            <option value="overdue">Overdue</option>
          </select>

          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search events..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 glass rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Timeline */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary-500 to-purple-500"></div>

          {/* Events */}
          <div className="space-y-6">
            <AnimatePresence>
              {displayEvents.map((event, index) => {
                const Icon = getEventIcon(event.type);
                const isExpanded = expandedEvents.has(event.id);

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
                      className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center ${getStatusColor(event.status)} border-2`}
                    >
                      <Icon className="h-6 w-6" />
                    </motion.div>

                    {/* Event Card */}
                    <motion.div
                      whileHover={{ scale: 1.02 }}
                      className={`flex-1 glass rounded-xl p-6 border-l-4 ${getImportanceColor(event.importance)} cursor-pointer`}
                      onClick={() => toggleEventExpansion(event.id)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-white mb-1">
                            {event.title}
                          </h3>
                          <p className="text-gray-300 text-sm mb-2">
                            {event.description}
                          </p>
                          <div className="flex items-center space-x-4 text-xs text-gray-400">
                            <span className="flex items-center space-x-1">
                              <Calendar className="h-3 w-3" />
                              <span>{formatDate(event.date)}</span>
                            </span>
                            <span className={`px-2 py-1 rounded-full ${getStatusColor(event.status)}`}>
                              {event.status}
                            </span>
                            <span className="capitalize">{event.type}</span>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <span className={`text-xs px-2 py-1 rounded ${
                            event.importance === 'critical' ? 'bg-red-500/20 text-red-400' :
                            event.importance === 'high' ? 'bg-orange-500/20 text-orange-400' :
                            event.importance === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-blue-500/20 text-blue-400'
                          }`}>
                            {event.importance}
                          </span>
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
                            {event.participants && event.participants.length > 0 && (
                              <div className="mb-4">
                                <h4 className="text-sm font-medium text-white mb-2 flex items-center">
                                  <Users className="h-4 w-4 mr-2" />
                                  Participants
                                </h4>
                                <div className="flex flex-wrap gap-2">
                                  {event.participants.map((participant, idx) => (
                                    <span
                                      key={idx}
                                      className="text-xs bg-primary-500/20 text-primary-400 px-2 py-1 rounded"
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
                                      className="text-xs text-gray-300 hover:text-primary-400 cursor-pointer flex items-center space-x-2"
                                    >
                                      <FileText className="h-3 w-3" />
                                      <span>{doc}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
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
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LegalTimeline;
