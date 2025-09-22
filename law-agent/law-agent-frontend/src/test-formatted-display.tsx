// Test for the FormattedResponseDisplay component
import React from 'react';
import { createRoot } from 'react-dom/client';
import FormattedResponseDisplay from './components/FormattedResponseDisplay';
import { Message } from './types';

// Sample formatted response from the backend
const sampleResponse: Message = {
  id: 'test-1',
  type: 'ai',
  content: `
🎯 **ULTIMATE LEGAL ANALYSIS - ANY QUERY TYPE**
================================================================================

**📋 QUERY:** "What are my rights in a contract dispute?"

**🏛️ LEGAL CLASSIFICATION:**
• Primary Domain:: Contract Law
• Specific Subdomain: General

**📚 BHARATIYA NYAYA SANHITA (BNS) 2023 SECTIONS:**
1. **Section 319: Cheating by personation**
   BNS Section 319: Cheating by personation

2. **Section 320: Dishonest or fraudulent removal or concealment of property to prevent distribution among creditors**
   BNS Section 320: Dishonest or fraudulent removal or concealment of property to prevent distribution among creditors

**📖 INDIAN PENAL CODE (IPC) SECTIONS:**
1. **Section 415: Cheating**

2. **Section 420: Cheating and dishonestly inducing delivery of property**

**⚖️ CCODE OF CRIMINAL PROCEDURE (CrPC) SECTIONS:**
1. **Section 154: Information in cognizable cases**
   Information regarding cognizable cases must be recorded in the prescribed manner.

2. **Section 156: Police officer's power to investigate cognizable case**
   A police officer has the power to investigate a cognizable case.

**⚡ IMMEDIATE ACTIONS:**

**📋 LEGAL PROCEDURES:**

================================================================================
⚖️ LEGAL DISCLAIMER:
This analysis covers ANY type of legal query using BNS 2023, IPC, and CrPC.
Consult with a qualified attorney for specific legal advice.
================================================================================
`,
  timestamp: new Date()
};

// Create a simple test page
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(
    <div className="p-6 bg-gray-900 min-h-screen">
      <h1 className="text-2xl font-bold text-white mb-6">Formatted Response Display Test</h1>
      <div className="bg-gray-800 p-6 rounded-xl">
        <FormattedResponseDisplay message={sampleResponse} />
      </div>
    </div>
  );
}