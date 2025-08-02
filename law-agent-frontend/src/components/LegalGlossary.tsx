import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen,
  Search,
  Filter,
  ChevronDown,
  ChevronRight,
  Scale,
  Gavel,
  FileText,
  Building,
  Heart,
  Home,
  Briefcase,
  AlertTriangle
} from 'lucide-react';
import { GlossaryTerm } from '../types';

interface LegalGlossaryProps {
  terms: GlossaryTerm[];
  title: string;
}

const LegalGlossary: React.FC<LegalGlossaryProps> = ({ terms, title }) => {
  const [filteredTerms, setFilteredTerms] = useState<GlossaryTerm[]>(terms);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedTerms, setExpandedTerms] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<'alphabetical' | 'category' | 'importance'>('alphabetical');

  // Sample terms if none provided
  const sampleTerms: GlossaryTerm[] = [
    {
      term: 'Affidavit',
      definition: 'A written statement of facts confirmed by the oath of the party making it, before a notary or officer having authority to administer oaths.',
      category: 'Civil Procedure',
      examples: ['Affidavit of service', 'Affidavit of identity'],
      relatedTerms: ['Oath', 'Notary', 'Sworn statement'],
      importance: 'basic'
    },
    {
      term: 'Breach of Contract',
      definition: 'Failure to perform any term of a contract, written or oral, without a legitimate legal excuse.',
      category: 'Contract Law',
      examples: ['Non-payment of agreed amount', 'Failure to deliver goods on time'],
      relatedTerms: ['Contract', 'Performance', 'Damages'],
      importance: 'basic'
    },
    {
      term: 'Custody',
      definition: 'The care, control, and maintenance of a child awarded by a court to one of the parents in a divorce or separation proceeding.',
      category: 'Family Law',
      examples: ['Joint custody', 'Sole custody', 'Physical custody'],
      relatedTerms: ['Visitation', 'Child support', 'Parental rights'],
      importance: 'intermediate'
    },
    {
      term: 'Due Process',
      definition: 'The constitutional requirement that laws and legal proceedings be fair and that individuals be given notice and an opportunity to be heard.',
      category: 'Constitutional Law',
      examples: ['Right to counsel', 'Right to fair trial', 'Notice of charges'],
      relatedTerms: ['Constitutional rights', 'Fair trial', 'Legal procedure'],
      importance: 'advanced'
    },
    {
      term: 'Easement',
      definition: 'A right to use another person\'s land for a specific limited purpose.',
      category: 'Property Law',
      examples: ['Right of way', 'Utility easement', 'Access easement'],
      relatedTerms: ['Property rights', 'Land use', 'Servitude'],
      importance: 'intermediate'
    },
    {
      term: 'Felony',
      definition: 'A serious crime punishable by imprisonment for more than one year or by death.',
      category: 'Criminal Law',
      examples: ['Murder', 'Armed robbery', 'Drug trafficking'],
      relatedTerms: ['Misdemeanor', 'Criminal offense', 'Sentencing'],
      importance: 'basic'
    }
  ];

  const displayTerms = terms.length > 0 ? terms : sampleTerms;

  const categories = useMemo(() => {
    const cats = Array.from(new Set(displayTerms.map(term => term.category)));
    return cats.sort();
  }, [displayTerms]);

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'criminal law': return AlertTriangle;
      case 'civil procedure': return Scale;
      case 'contract law': return FileText;
      case 'family law': return Heart;
      case 'property law': return Home;
      case 'employment law': return Briefcase;
      case 'corporate law': return Building;
      case 'constitutional law': return Gavel;
      default: return BookOpen;
    }
  };

  const getImportanceColor = (importance?: string) => {
    switch (importance) {
      case 'basic': return 'text-green-400 bg-green-400/20';
      case 'intermediate': return 'text-yellow-400 bg-yellow-400/20';
      case 'advanced': return 'text-red-400 bg-red-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
  };

  useEffect(() => {
    let filtered = displayTerms;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(term =>
        term.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
        term.definition.toLowerCase().includes(searchTerm.toLowerCase()) ||
        term.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(term => term.category === selectedCategory);
    }

    // Sort terms
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'alphabetical':
          return a.term.localeCompare(b.term);
        case 'category':
          return a.category.localeCompare(b.category) || a.term.localeCompare(b.term);
        case 'importance':
          const importanceOrder = { 'basic': 0, 'intermediate': 1, 'advanced': 2 };
          const aImportance = importanceOrder[a.importance as keyof typeof importanceOrder] ?? 3;
          const bImportance = importanceOrder[b.importance as keyof typeof importanceOrder] ?? 3;
          return aImportance - bImportance || a.term.localeCompare(b.term);
        default:
          return 0;
      }
    });

    setFilteredTerms(filtered);
  }, [displayTerms, searchTerm, selectedCategory, sortBy]);

  const toggleTermExpansion = (term: string) => {
    const newExpanded = new Set(expandedTerms);
    if (newExpanded.has(term)) {
      newExpanded.delete(term);
    } else {
      newExpanded.add(term);
    }
    setExpandedTerms(newExpanded);
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
            <BookOpen className="h-8 w-8 text-primary-400" />
            <h2 className="text-2xl font-bold text-white">{title}</h2>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <span>{filteredTerms.length} terms</span>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search legal terms..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 glass rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="glass rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="glass rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-primary-500"
          >
            <option value="alphabetical">A-Z</option>
            <option value="category">Category</option>
            <option value="importance">Importance</option>
          </select>
        </div>
      </motion.div>

      {/* Terms List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-4">
          <AnimatePresence>
            {filteredTerms.map((term, index) => {
              const isExpanded = expandedTerms.has(term.term);
              const CategoryIcon = getCategoryIcon(term.category);

              return (
                <motion.div
                  key={term.term}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.05 }}
                  className="glass rounded-xl border border-white/10 overflow-hidden"
                >
                  <button
                    onClick={() => toggleTermExpansion(term.term)}
                    className="w-full flex items-center justify-between p-6 text-left hover:bg-white/5 transition-colors"
                  >
                    <div className="flex items-center space-x-4 flex-1">
                      <CategoryIcon className="h-6 w-6 text-primary-400 flex-shrink-0" />
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-white mb-1">
                          {term.term}
                        </h3>
                        <div className="flex items-center space-x-3">
                          <span className="text-xs px-2 py-1 bg-primary-500/20 text-primary-400 rounded">
                            {term.category}
                          </span>
                          {term.importance && (
                            <span className={`text-xs px-2 py-1 rounded ${getImportanceColor(term.importance)}`}>
                              {term.importance}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {isExpanded ? (
                        <ChevronDown className="h-5 w-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-gray-400" />
                      )}
                    </div>
                  </button>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="border-t border-white/10 p-6"
                      >
                        <div className="space-y-4">
                          {/* Definition */}
                          <div>
                            <h4 className="text-sm font-medium text-white mb-2">Definition</h4>
                            <p className="text-gray-300 leading-relaxed">
                              {term.definition}
                            </p>
                          </div>

                          {/* Examples */}
                          {term.examples && term.examples.length > 0 && (
                            <div>
                              <h4 className="text-sm font-medium text-white mb-2">Examples</h4>
                              <ul className="space-y-1">
                                {term.examples.map((example, idx) => (
                                  <li key={idx} className="text-gray-300 text-sm flex items-start space-x-2">
                                    <span className="text-primary-400 mt-1">•</span>
                                    <span>{example}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Related Terms */}
                          {term.relatedTerms && term.relatedTerms.length > 0 && (
                            <div>
                              <h4 className="text-sm font-medium text-white mb-2">Related Terms</h4>
                              <div className="flex flex-wrap gap-2">
                                {term.relatedTerms.map((relatedTerm, idx) => (
                                  <span
                                    key={idx}
                                    className="text-xs bg-gray-600/30 text-gray-300 px-2 py-1 rounded cursor-pointer hover:bg-primary-500/20 hover:text-primary-400 transition-colors"
                                    onClick={() => setSearchTerm(relatedTerm)}
                                  >
                                    {relatedTerm}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>

        {filteredTerms.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <BookOpen className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">
              No Terms Found
            </h3>
            <p className="text-gray-500">
              No legal terms match your current search and filters.
            </p>
          </motion.div>
        )}
      </div>

      {/* Category Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-dark border-t border-white/10 p-4"
      >
        <div className="flex flex-wrap gap-2">
          {categories.map(category => {
            const count = displayTerms.filter(term => term.category === category).length;
            const CategoryIcon = getCategoryIcon(category);
            
            return (
              <button
                key={category}
                onClick={() => setSelectedCategory(selectedCategory === category ? 'all' : category)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs transition-colors ${
                  selectedCategory === category
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                    : 'bg-gray-600/20 text-gray-400 hover:bg-gray-600/30 hover:text-white'
                }`}
              >
                <CategoryIcon className="h-3 w-3" />
                <span>{category}</span>
                <span className="bg-white/20 px-1 rounded">{count}</span>
              </button>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
};

export default LegalGlossary;
