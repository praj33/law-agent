// Component to display formatted legal responses
import React from 'react';
import { Message } from '../types';

interface FormattedResponseDisplayProps {
  message: Message;
}

const FormattedResponseDisplay: React.FC<FormattedResponseDisplayProps> = ({ message }) => {
  // Function to parse and format the response content
  const formatLegalResponse = (content: string) => {
    if (!content) return null;
    
    try {
      // Split the content into sections based on markdown-style headers
      const sections = content.split('\n================================================================================\n');
      
      // Parse the main content
      const mainContent = sections[0] || content;
      
      // Split into lines and remove empty lines
      const lines = mainContent.split('\n').filter(line => line.trim() !== '');
      
      // Find sections by their markers
      const queryLineIndex = lines.findIndex(line => line.includes('**📋 QUERY:**'));
      const domainLineIndex = lines.findIndex(line => line.includes('**🏛️ LEGAL CLASSIFICATION:**'));
      const bnsLineIndex = lines.findIndex(line => line.includes('**📚 BHARATIYA NYAYA SANHITA (BNS) 2023 SECTIONS:**'));
      const ipcLineIndex = lines.findIndex(line => line.includes('**📖 INDIAN PENAL CODE (IPC) SECTIONS:**'));
      const crpcLineIndex = lines.findIndex(line => line.includes('**⚖️ CCODE OF CRIMINAL PROCEDURE (CrPC) SECTIONS:**'));
      const actionsLineIndex = lines.findIndex(line => line.includes('**⚡ IMMEDIATE ACTIONS:**'));
      const proceduresLineIndex = lines.findIndex(line => line.includes('**📋 LEGAL PROCEDURES:**'));
      const disclaimerLineIndex = lines.findIndex(line => line.includes('**⚖️ LEGAL DISCLAIMER:**'));
      
      // Extract query
      let query = '';
      if (queryLineIndex !== -1) {
        const queryLine = lines[queryLineIndex];
        const queryMatch = queryLine.match(/"([^"]+)"/);
        query = queryMatch ? queryMatch[1] : queryLine.replace(/\*\*/g, '').replace('📋 QUERY:', '').trim();
      }
      
      // Extract domain info
      let domainInfo = [];
      if (domainLineIndex !== -1) {
        let i = domainLineIndex + 1;
        while (i < lines.length && !lines[i].startsWith('**') && i !== bnsLineIndex && i !== ipcLineIndex && i !== crpcLineIndex) {
          if (lines[i].trim() !== '') {
            domainInfo.push(lines[i].replace('• ', '').replace(/\*\*/g, '').trim());
          }
          i++;
        }
      }
      
      // Extract BNS sections
      let bnsSections = [];
      if (bnsLineIndex !== -1) {
        let i = bnsLineIndex + 1;
        let currentSection = null;
        while (i < lines.length && !lines[i].startsWith('**') && i !== ipcLineIndex && i !== crpcLineIndex && i !== actionsLineIndex && i !== proceduresLineIndex && i !== disclaimerLineIndex) {
          const line = lines[i].trim();
          if (line !== '') {
            if (line.match(/^\d+\.\s*\*\*/)) {
              if (currentSection) {
                bnsSections.push(currentSection);
              }
              const titleMatch = line.match(/^\d+\.\s*\*\*(.*?)\*\*/);
              const contentMatch = line.match(/^\d+\.\s*\*\*.*?\*\*\s*(.*)$/);
              currentSection = {
                title: titleMatch ? titleMatch[1].replace(/\*\*/g, '') : line.replace(/^\d+\.\s*\*\*(.*?)\*\*.*/, '$1').replace(/\*\*/g, ''),
                content: contentMatch ? contentMatch[1].replace(/\*\*/g, '') : line.replace(/^\d+\.\s*\*\*.*?\*\*\s*/, '').replace(/\*\*/g, '')
              };
            } else if (currentSection) {
              currentSection.content += ' ' + line.replace(/\*\*/g, '');
            }
          }
          i++;
        }
        if (currentSection) {
          bnsSections.push(currentSection);
        }
      }
      
      // Extract IPC sections
      let ipcSections = [];
      if (ipcLineIndex !== -1) {
        let i = ipcLineIndex + 1;
        let currentSection = null;
        while (i < lines.length && !lines[i].startsWith('**') && i !== crpcLineIndex && i !== actionsLineIndex && i !== proceduresLineIndex && i !== disclaimerLineIndex) {
          const line = lines[i].trim();
          if (line !== '') {
            if (line.match(/^\d+\.\s*\*\*/)) {
              if (currentSection) {
                ipcSections.push(currentSection);
              }
              const titleMatch = line.match(/^\d+\.\s*\*\*(.*?)\*\*/);
              const contentMatch = line.match(/^\d+\.\s*\*\*.*?\*\*\s*(.*)$/);
              currentSection = {
                title: titleMatch ? titleMatch[1].replace(/\*\*/g, '') : line.replace(/^\d+\.\s*\*\*(.*?)\*\*.*/, '$1').replace(/\*\*/g, ''),
                content: contentMatch ? contentMatch[1].replace(/\*\*/g, '') : line.replace(/^\d+\.\s*\*\*.*?\*\*\s*/, '').replace(/\*\*/g, '')
              };
            } else if (currentSection) {
              currentSection.content += ' ' + line.replace(/\*\*/g, '');
            }
          }
          i++;
        }
        if (currentSection) {
          ipcSections.push(currentSection);
        }
      }
      
      // Extract CrPC sections
      let crpcSections = [];
      if (crpcLineIndex !== -1) {
        let i = crpcLineIndex + 1;
        let currentSection = null;
        while (i < lines.length && !lines[i].startsWith('**') && i !== actionsLineIndex && i !== proceduresLineIndex && i !== disclaimerLineIndex) {
          const line = lines[i].trim();
          if (line !== '') {
            if (line.match(/^\d+\.\s*\*\*/)) {
              if (currentSection) {
                crpcSections.push(currentSection);
              }
              const titleMatch = line.match(/^\d+\.\s*\*\*(.*?)\*\*/);
              const contentMatch = line.match(/^\d+\.\s*\*\*.*?\*\*\s*(.*)$/);
              currentSection = {
                title: titleMatch ? titleMatch[1].replace(/\*\*/g, '') : line.replace(/^\d+\.\s*\*\*(.*?)\*\*.*/, '$1').replace(/\*\*/g, ''),
                content: contentMatch ? contentMatch[1].replace(/\*\*/g, '') : line.replace(/^\d+\.\s*\*\*.*?\*\*\s*/, '').replace(/\*\*/g, '')
              };
            } else if (currentSection) {
              currentSection.content += ' ' + line.replace(/\*\*/g, '');
            }
          }
          i++;
        }
        if (currentSection) {
          crpcSections.push(currentSection);
        }
      }
      
      // Extract Immediate Actions
      let immediateActions = [];
      if (actionsLineIndex !== -1) {
        let i = actionsLineIndex + 1;
        while (i < lines.length && !lines[i].startsWith('**') && i !== proceduresLineIndex && i !== disclaimerLineIndex) {
          if (lines[i].trim() !== '') {
            immediateActions.push(lines[i].replace(/\*\*/g, '').trim());
          }
          i++;
        }
      }
      
      // Extract Legal Procedures
      let legalProcedures = [];
      if (proceduresLineIndex !== -1) {
        let i = proceduresLineIndex + 1;
        while (i < lines.length && !lines[i].startsWith('**') && i !== disclaimerLineIndex) {
          if (lines[i].trim() !== '') {
            legalProcedures.push(lines[i].replace(/\*\*/g, '').trim());
          }
          i++;
        }
      }
      
      return {
        query,
        domainInfo,
        bnsSections,
        ipcSections,
        crpcSections,
        immediateActions,
        legalProcedures
      };
    } catch (error) {
      console.error('Error parsing legal response:', error);
      return null;
    }
  };
  
  // Parse the content
  const parsedContent = formatLegalResponse(message.content);
  
  // If parsing fails or content is simple text, display as plain text
  if (!parsedContent || (!parsedContent.query && !parsedContent.domainInfo.length && 
      !parsedContent.bnsSections.length && !parsedContent.ipcSections.length && 
      !parsedContent.crpcSections.length && !parsedContent.immediateActions.length && 
      !parsedContent.legalProcedures.length)) {
    // Remove asterisks from plain text content as well
    const cleanContent = message.content.replace(/\*\*/g, '');
    return (
      <div className="text-sm leading-relaxed whitespace-pre-wrap">
        {cleanContent}
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header with decorative elements */}
      <div className="text-center py-3 border-b border-gray-600/50">
        <h2 className="text-xl font-bold text-blue-300 flex items-center justify-center gap-2">
          <span className="text-2xl">⚖️</span> 
          Legal Analysis Report
          <span className="text-2xl">⚖️</span>
        </h2>
        <p className="text-gray-400 text-sm mt-1">Comprehensive legal guidance powered by AI</p>
      </div>
      
      {/* Query Section */}
      {parsedContent.query && (
        <div className="bg-gradient-to-r from-blue-900/40 to-blue-800/30 p-5 rounded-2xl border border-blue-700/50 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-2xl">❓</div>
            <h3 className="font-bold text-blue-300 text-lg">Your Legal Query</h3>
          </div>
          <div className="bg-blue-900/30 p-4 rounded-xl">
            <p className="text-white text-base">{parsedContent.query}</p>
          </div>
        </div>
      )}
      
      {/* Domain Classification */}
      {parsedContent.domainInfo.length > 0 && (
        <div className="bg-gradient-to-r from-purple-900/40 to-purple-800/30 p-5 rounded-2xl border border-purple-700/50 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-2xl">🏛️</div>
            <h3 className="font-bold text-purple-300 text-lg">Legal Classification</h3>
          </div>
          <div className="space-y-2">
            {parsedContent.domainInfo.map((info, index) => (
              <div key={index} className="flex items-start bg-purple-900/30 p-3 rounded-lg">
                <div className="text-purple-400 mr-2 mt-0.5">◆</div>
                <span className="text-purple-100">{info}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* BNS Sections */}
      {parsedContent.bnsSections.length > 0 && (
        <div className="bg-gradient-to-r from-indigo-900/40 to-indigo-800/30 p-5 rounded-2xl border border-indigo-700/50 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-2xl">📚</div>
            <h3 className="font-bold text-indigo-300 text-lg">Bharatiya Nyaya Sanhita (BNS) 2023</h3>
          </div>
          <div className="space-y-4">
            {parsedContent.bnsSections.map((section, index) => (
              <div key={index} className="bg-indigo-900/30 p-4 rounded-xl border border-indigo-700/30">
                <h4 className="font-bold text-indigo-200 flex items-center gap-2">
                  <span className="bg-indigo-700 px-2 py-1 rounded text-sm">§{index + 1}</span>
                  {section.title}
                </h4>
                <p className="mt-2 text-indigo-100">{section.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* IPC Sections */}
      {parsedContent.ipcSections.length > 0 && (
        <div className="bg-gradient-to-r from-green-900/40 to-green-800/30 p-5 rounded-2xl border border-green-700/50 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-2xl">📖</div>
            <h3 className="font-bold text-green-300 text-lg">Indian Penal Code (IPC)</h3>
          </div>
          <div className="space-y-4">
            {parsedContent.ipcSections.map((section, index) => (
              <div key={index} className="bg-green-900/30 p-4 rounded-xl border border-green-700/30">
                <h4 className="font-bold text-green-200 flex items-center gap-2">
                  <span className="bg-green-700 px-2 py-1 rounded text-sm">§{index + 1}</span>
                  {section.title}
                </h4>
                <p className="mt-2 text-green-100">{section.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* CrPC Sections */}
      {parsedContent.crpcSections.length > 0 && (
        <div className="bg-gradient-to-r from-yellow-900/40 to-yellow-800/30 p-5 rounded-2xl border border-yellow-700/50 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-2xl">⚖️</div>
            <h3 className="font-bold text-yellow-300 text-lg">Code of Criminal Procedure (CrPC)</h3>
          </div>
          <div className="space-y-4">
            {parsedContent.crpcSections.map((section, index) => (
              <div key={index} className="bg-yellow-900/30 p-4 rounded-xl border border-yellow-700/30">
                <h4 className="font-bold text-yellow-200 flex items-center gap-2">
                  <span className="bg-yellow-700 px-2 py-1 rounded text-sm">§{index + 1}</span>
                  {section.title}
                </h4>
                <p className="mt-2 text-yellow-100">{section.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Immediate Actions */}
      {parsedContent.immediateActions.length > 0 && (
        <div className="bg-gradient-to-r from-red-900/40 to-red-800/30 p-5 rounded-2xl border border-red-700/50 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-2xl">⚡</div>
            <h3 className="font-bold text-red-300 text-lg">Immediate Actions</h3>
          </div>
          <div className="space-y-2">
            {parsedContent.immediateActions.map((action, index) => (
              <div key={index} className="flex items-start bg-red-900/30 p-3 rounded-lg">
                <div className="text-red-400 mr-2 mt-0.5">▶</div>
                <span className="text-red-100">{action}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Legal Procedures */}
      {parsedContent.legalProcedures.length > 0 && (
        <div className="bg-gradient-to-r from-cyan-900/40 to-cyan-800/30 p-5 rounded-2xl border border-cyan-700/50 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <div className="text-2xl">📋</div>
            <h3 className="font-bold text-cyan-300 text-lg">Legal Procedures</h3>
          </div>
          <div className="space-y-2">
            {parsedContent.legalProcedures.map((procedure, index) => (
              <div key={index} className="flex items-start bg-cyan-900/30 p-3 rounded-lg">
                <div className="text-cyan-400 mr-2 mt-0.5">→</div>
                <span className="text-cyan-100">{procedure}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Disclaimer */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-5 rounded-2xl border border-gray-700 shadow-lg">
        <div className="flex items-center gap-3 mb-3">
          <div className="text-2xl">⚠️</div>
          <h3 className="font-bold text-gray-300 text-lg">Legal Disclaimer</h3>
        </div>
        <div className="bg-gray-800/50 p-4 rounded-xl">
          <p className="text-gray-300 text-sm">
            This analysis is provided for informational purposes only and does not constitute legal advice. 
            Consult with a qualified attorney for specific legal advice tailored to your situation. 
            Laws may vary by jurisdiction and are subject to change.
          </p>
        </div>
      </div>
      
      {/* Footer */}
      <div className="text-center py-3 border-t border-gray-600/50">
        <p className="text-gray-500 text-sm flex items-center justify-center gap-2">
          <span>🛡️</span> 
          Protected by Legal AI Technology 
          <span>🛡️</span>
        </p>
      </div>
    </div>
  );
};

export default FormattedResponseDisplay;