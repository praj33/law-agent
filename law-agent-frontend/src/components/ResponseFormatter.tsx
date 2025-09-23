import React from 'react';

interface FormattedResponseProps {
  content: string;
}

const ResponseFormatter: React.FC<FormattedResponseProps> = ({ content }) => {
  // Function to format the response content
  const formatResponse = (text: string): JSX.Element[] => {
    if (!text) return [<p key="empty" className="text-gray-300">No content available</p>];
    
    // Special handling for welcome message
    if (text.startsWith('🏛️ Welcome to Law Agent')) {
      // Split the welcome message into sections
      const lines = text.split('\n');
      const title = lines[0];
      const subtitle = lines[1];
      const listItems = lines.slice(3, 9); // Get the 6 list items
      const features = lines.slice(10, 13); // Get the 3 features
      const closing = lines[14]; // Get the closing line
      
      return [
        // Title with special styling
        <h1 key="welcome-title" className="text-2xl font-bold text-blue-400 mt-2 mb-2 text-center">
          {title.replace('🏛️ ', '')}
        </h1>,
        
        // Subtitle
        <p key="welcome-subtitle" className="text-gray-300 mb-4 text-center italic">
          {subtitle}
        </p>,
        
        // List of services
        <ul key="welcome-list" className="list-disc list-inside ml-4 space-y-2 mb-4 text-gray-200">
          {listItems
            .filter(item => item.trim() !== '') // Filter out empty items
            .map((item, index) => (
              <li key={`item-${index}`} className="pl-2 flex items-start">
                <span className="text-blue-400 mr-2">•</span>
                <span>{item.replace('• ', '')}</span>
              </li>
            ))}
        </ul>,
        
        // Features/benefits
        <div key="welcome-features" className="flex justify-center space-x-4 mb-4 text-sm">
          {features.map((feature, index) => (
            <span key={`feature-${index}`} className="flex items-center text-gray-400">
              <span className="mr-1">{feature.split(' ')[0]}</span>
              <span>{feature.split(' ').slice(1).join(' ')}</span>
            </span>
          ))}
        </div>,
        
        // Closing paragraph
        <p key="welcome-closing" className="text-gray-200 mt-2 mb-2 leading-relaxed font-semibold text-center">
          {closing}
        </p>
      ];
    }
    
    // Split the text into sections based on common patterns
    const sections = text.split(/\n{2,}/).filter(section => section.trim()); // Split by double newlines and filter empty sections
    
    // Keep track of processed sections to avoid duplicates
    const processedSections = new Set<string>();
    
    return sections.map((section, index) => {
      // Remove leading/trailing whitespace
      const trimmedSection = section.trim();
      
      if (!trimmedSection) return null;
      
      // Create a unique key for this section to check for duplicates
      const sectionKey = trimmedSection.substring(0, 50) + index;
      if (processedSections.has(sectionKey)) {
        return null; // Skip duplicate sections
      }
      processedSections.add(sectionKey);
      
      // Check if this is a main header (all caps or ends with colon)
      if (/^[A-Z\s]{15,}$/.test(trimmedSection) || trimmedSection.endsWith(':')) {
        return (
          <h2 key={index} className="text-2xl font-bold text-blue-400 mt-8 mb-4 pb-2 border-b-2 border-blue-500/50">
            {trimmedSection.replace(/:$/, '')}
          </h2>
        );
      }
      
      // Check if this is a sub-header (short line ending with colon, followed by content)
      if ((trimmedSection.endsWith(':') && trimmedSection.length < 80) || 
          (trimmedSection.length < 60 && sections[index + 1] && 
           (sections[index + 1].trim().startsWith('- ') || 
            sections[index + 1].trim().startsWith('* ') || 
            sections[index + 1].trim().startsWith('• ') ||
            /^\d+\.\s/.test(sections[index + 1].trim())))) {
        return (
          <h3 key={index} className="text-xl font-bold text-blue-300 mt-6 mb-3 pb-1 border-b border-blue-500/30">
            {trimmedSection.replace(/:$/, '')}
          </h3>
        );
      }
      
      // Check if this is a list item
      if (trimmedSection.startsWith('- ') || trimmedSection.startsWith('* ') || trimmedSection.startsWith('• ')) {
        const listItems = trimmedSection.split(/\n/).filter(item => item.trim());
        return (
          <ul key={index} className="list-disc list-inside ml-6 space-y-2 mt-2 mb-4">
            {listItems.map((item, itemIndex) => {
              const cleanItem = item.replace(/^[-*•]\s*/, '').trim();
              // Check if this list item contains nested content
              if (cleanItem.includes(':') && cleanItem.length > 30) {
                const colonIndex = cleanItem.indexOf(':');
                const title = cleanItem.substring(0, colonIndex);
                const description = cleanItem.substring(colonIndex + 1).trim();
                return (
                  <li key={`${index}-${itemIndex}`} className="text-gray-200">
                    <span className="font-semibold text-blue-200">{title}:</span>
                    <span className="ml-2">{description}</span>
                  </li>
                );
              }
              return (
                <li key={`${index}-${itemIndex}`} className="text-gray-200 pl-2">
                  {cleanItem}
                </li>
              );
            })}
          </ul>
        );
      }
      
      // Check if this is a numbered list
      if (/^\d+\.\s/.test(trimmedSection)) {
        const listItems = trimmedSection.split(/\n/).filter(item => item.trim());
        return (
          <ol key={index} className="list-decimal list-inside ml-6 space-y-2 mt-2 mb-4">
            {listItems.map((item, itemIndex) => {
              const cleanItem = item.replace(/^\d+\.\s*/, '').trim();
              return (
                <li key={`${index}-${itemIndex}`} className="text-gray-200 pl-2">
                  {cleanItem}
                </li>
              );
            })}
          </ol>
        );
      }
      
      // Check for bold text patterns
      if (trimmedSection.includes('**') || trimmedSection.includes('__')) {
        const parts = trimmedSection.split(/(\*\*.*?\*\*|__.*?__)/g);
        return (
          <p key={index} className="text-gray-200 mb-4 leading-relaxed">
            {parts.map((part, partIndex) => {
              if ((part.startsWith('**') && part.endsWith('**')) || 
                  (part.startsWith('__') && part.endsWith('__'))) {
                return (
                  <span key={partIndex} className="font-bold text-yellow-300">
                    {part.slice(2, -2)}
                  </span>
                );
              }
              return part;
            })}
          </p>
        );
      }
      
      // Regular paragraph with legal term highlighting
      const highlightedContent = highlightLegalTerms(trimmedSection);
      
      return (
        <p key={index} className="text-gray-200 mb-4 leading-relaxed">
          {highlightedContent}
        </p>
      );
    }).filter(Boolean) as JSX.Element[]; // Remove null values
  };

  // Function to highlight key legal terms
  const highlightLegalTerms = (content: string): React.ReactNode => {
    // Common legal terms to highlight
    const legalTerms = [
      'contract', 'liability', 'jurisdiction', 'statute', 'plaintiff', 'defendant',
      'tort', 'negligence', 'damages', 'injunction', 'precedent', 'appeal',
      'constitutional', 'civil rights', 'criminal', 'prosecution', 'defense',
      'evidence', 'testimony', 'verdict', 'settlement', 'litigation',
      'plaintiff', 'defendant', 'petitioner', 'respondent', 'appellant', 'appellee',
      'brief', 'motion', 'discovery', 'deposition', 'affidavit', 'pleading',
      'complaint', 'summons', 'subpoena', 'warrant', 'indictment', 'arraignment',
      'bail', 'sentencing', 'probation', 'parole', 'appeal', 'retrial',
      'tort', 'negligence', 'intentional', 'strict liability', 'product liability',
      'breach of contract', 'specific performance', 'rescission', 'reformation',
      'property', 'real estate', 'personal property', 'intellectual property',
      'copyright', 'patent', 'trademark', 'trade secret', 'domain name',
      'family law', 'divorce', 'custody', 'alimony', 'child support', 'adoption',
      'employment', 'discrimination', 'harassment', 'wrongful termination', 'FMLA',
      'bankruptcy', 'Chapter 7', 'Chapter 11', 'Chapter 13', 'discharge', 'automatic stay',
      'tax', 'IRS', 'audit', 'refund', 'penalty', 'lien', 'levy'
    ];
    
    // Sort terms by length (longest first) to avoid partial matches
    const sortedTerms = [...legalTerms].sort((a, b) => b.length - a.length);
    
    const elements: React.ReactNode[] = [];
    let lastIndex = 0;
    
    // Create a regex that matches any of the legal terms (case insensitive)
    const termsRegex = new RegExp(
      `\\b(${sortedTerms.map(term => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b`, 
      'gi'
    );
    
    let match;
    while ((match = termsRegex.exec(content)) !== null) {
      // Add text before the match
      if (match.index > lastIndex) {
        elements.push(content.substring(lastIndex, match.index));
      }
      
      // Add the highlighted term
      elements.push(
        <span key={match.index} className="font-semibold text-yellow-300">
          {match[0]}
        </span>
      );
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < content.length) {
      elements.push(content.substring(lastIndex));
    }
    
    return elements.length > 0 ? elements : content;
  };

  // Format the content
  const formattedContent = formatResponse(content);

  return (
    <div className="formatted-response p-2">
      {formattedContent}
    </div>
  );
};

export default ResponseFormatter;