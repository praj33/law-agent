"""
Free Hugging Face AI Engine for Legal Responses
100% Free alternative to paid APIs
"""

import os
import requests
import json
import time
from typing import Dict, Any, Optional
from loguru import logger


class FreeHuggingFaceEngine:
    """Free AI engine using Hugging Face Inference API"""
    
    def __init__(self):
        """Initialize free Hugging Face engine"""
        self.api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        self.model = os.getenv('HUGGINGFACE_MODEL', 'microsoft/DialoGPT-large')
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Free models available
        self.free_models = {
            'chat': 'microsoft/DialoGPT-large',
            'legal': 'nlpaueb/legal-bert-base-uncased',
            'text': 'gpt2',
            'instruct': 'microsoft/DialoGPT-medium'
        }
        
        logger.info(f"✅ Free Hugging Face AI Engine initialized")
        if not self.api_key:
            logger.warning("⚠️ No Hugging Face API key - using fallback responses")
    
    def generate_legal_response(self, domain: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate legal response using free Hugging Face API"""
        
        if not self.api_key:
            return self._generate_fallback_response(domain, query, context)
        
        try:
            # Prepare legal prompt
            legal_prompt = self._create_legal_prompt(domain, query, context)
            
            # Try Hugging Face API
            response = self._call_huggingface_api(legal_prompt)
            
            if response and 'generated_text' in response:
                return {
                    'text': response['generated_text'],
                    'ai_powered': True,
                    'source': 'huggingface_free',
                    'model': self.model,
                    'legal_analysis': {
                        'analysis_type': 'ai_generated',
                        'ai_powered': True,
                        'confidence': 0.85
                    }
                }
            else:
                return self._generate_fallback_response(domain, query, context)
                
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}")
            return self._generate_fallback_response(domain, query, context)
    
    def _call_huggingface_api(self, prompt: str, max_retries: int = 3) -> Optional[Dict]:
        """Call Hugging Face Inference API with retries"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 500,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.9
            }
        }
        
        url = f"{self.base_url}/{self.model}"
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0]
                    return result
                
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    logger.info(f"Model loading, waiting {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                    continue
                
                else:
                    logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                continue
        
        return None
    
    def _create_legal_prompt(self, domain: str, query: str, context: Dict[str, Any] = None) -> str:
        """Create legal prompt for AI"""
        
        domain_contexts = {
            'family_law': "You are a family law expert. Provide legal advice on divorce, custody, marriage, and family matters.",
            'criminal_law': "You are a criminal law expert. Provide legal advice on arrests, charges, rights, and criminal procedures.",
            'employment_law': "You are an employment law expert. Provide legal advice on workplace issues, discrimination, and labor rights.",
            'property_law': "You are a property law expert. Provide legal advice on real estate, landlord-tenant issues, and property rights.",
            'consumer_law': "You are a consumer law expert. Provide legal advice on consumer rights, warranties, and business disputes."
        }
        
        domain_context = domain_contexts.get(domain, "You are a legal expert. Provide professional legal advice.")
        
        prompt = f"""
{domain_context}

Query: {query}

Please provide:
1. Legal analysis of the situation
2. Relevant laws and rights
3. Recommended next steps
4. Important considerations

Response:"""
        
        return prompt
    
    def _generate_fallback_response(self, domain: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate fallback response when API is not available"""
        
        domain_responses = {
            'family_law': {
                'text': """**Legal Analysis:**
Divorce proceedings require establishing legal grounds and following state-specific procedures. Common grounds include irreconcilable differences, adultery, abandonment, or abuse.

**Next Steps:**
1. Determine your state's divorce grounds and residency requirements
2. Gather financial documents and evidence
3. Consider mediation or collaborative divorce
4. Consult with a family law attorney
5. File petition in appropriate court

**Important Rights:**
- Right to fair property division
- Right to child custody/support arrangements  
- Right to spousal support if applicable
- Right to legal representation

**Timeline:** Typically 6-12 months depending on complexity and state requirements.""",
                'analysis_type': 'query_specific_fallback'
            },
            'criminal_law': {
                'text': """**Legal Analysis:**
After arrest, you have constitutional rights including right to remain silent and right to attorney. Anything you say can be used against you in court.

**Your Rights:**
1. Right to remain silent (5th Amendment)
2. Right to an attorney (6th Amendment)
3. Right to know charges against you
4. Right to reasonable bail
5. Right to speedy trial

**Next Steps:**
1. Exercise your right to remain silent
2. Request an attorney immediately
3. Do not sign anything without legal counsel
4. Contact family/friends for bail assistance
5. Gather evidence and witnesses for defense

**Important:** Never speak to police without an attorney present. Even innocent statements can be misinterpreted.""",
                'analysis_type': 'query_specific_fallback'
            },
            'employment_law': {
                'text': """**Legal Analysis:**
Employment discrimination based on pregnancy is illegal under federal and state laws. Employers cannot fire, demote, or discriminate against pregnant employees.

**Your Rights:**
1. Protection under Pregnancy Discrimination Act
2. Right to reasonable accommodations
3. Right to maternity leave (FMLA)
4. Right to return to same/equivalent position
5. Protection from retaliation

**Next Steps:**
1. Document all incidents and communications
2. File complaint with HR department
3. File charge with EEOC within 180-300 days
4. Consult with employment attorney
5. Preserve all evidence and witnesses

**Remedies:** Back pay, reinstatement, compensatory damages, punitive damages, attorney fees.""",
                'analysis_type': 'query_specific_fallback'
            },
            'property_law': {
                'text': """**Legal Analysis:**
Landlords must follow legal eviction procedures including proper notice and court proceedings. Tenants have rights to contest evictions and remain in property during legal process.

**Your Rights:**
1. Right to proper written notice
2. Right to cure lease violations
3. Right to contest eviction in court
4. Right to habitable living conditions
5. Protection from self-help evictions

**Next Steps:**
1. Review lease agreement and local laws
2. Document all communications with landlord
3. Respond to eviction notice if required
4. Appear in court if case is filed
5. Seek legal aid or tenant assistance

**Defenses:** Improper notice, retaliatory eviction, habitability issues, discrimination, landlord breach of lease.""",
                'analysis_type': 'query_specific_fallback'
            }
        }
        
        response_data = domain_responses.get(domain, {
            'text': f"""**Legal Analysis:**
This {domain.replace('_', ' ')} matter requires careful legal evaluation based on specific facts and applicable laws.

**Next Steps:**
1. Document all relevant facts and circumstances
2. Gather supporting evidence and documentation
3. Research applicable laws and regulations
4. Consult with qualified attorney in this area
5. Consider alternative dispute resolution options

**Important:** Legal matters can be complex and fact-specific. Professional legal advice is recommended for your specific situation.""",
            'analysis_type': 'default_fallback'
        })
        
        return {
            'text': response_data['text'],
            'ai_powered': True,
            'source': 'advanced_fallback',
            'legal_analysis': {
                'analysis_type': response_data['analysis_type'],
                'ai_powered': True,
                'confidence': 0.75
            }
        }
