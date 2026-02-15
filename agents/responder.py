"""Email response drafting agent using LLM."""

from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from config.settings import settings
from utils.prompts import RESPONSE_DRAFT_PROMPT
from utils.db import EmailDatabase


class EmailResponder:
    """Drafts responses to emails using LLM."""
    
    def __init__(self):
        """Initialize the responder with LLM."""
        self.llm = ChatOpenAI(
            model=settings.response_model,
            temperature=0.7,  # Higher temp for more creative responses
            api_key=settings.openai_api_key
        )
        self.db = EmailDatabase()
    
    def draft_response(
        self, 
        email_data: Dict[str, Any],
        user_context: str = "",
        tone: str = "professional"
    ) -> str:
        """
        Draft a response to an email.
        
        Args:
            email_data: Dictionary containing email information
            user_context: Additional context about the user/situation
            tone: Desired tone (professional, casual, friendly, formal)
        
        Returns:
            Drafted response text
        """
        # Enhance prompt with tone
        enhanced_context = user_context
        if not user_context:
            enhanced_context = f"Respond in a {tone} tone."
        
        prompt = RESPONSE_DRAFT_PROMPT.format(
            subject=email_data.get('subject', ''),
            sender=email_data.get('sender', ''),
            body=email_data.get('body', '')[:1500],
            user_context=enhanced_context
        )
        
        try:
            response = self.llm.invoke(prompt)
            draft = response.content.strip()
            
            # Save draft to database
            if email_data.get('id'):
                self.db.save_draft(email_data['id'], draft)
            
            return draft
        except Exception as e:
            print(f"Error drafting response: {e}")
            return "Error generating response draft"
    
    def draft_quick_reply(self, email_data: Dict[str, Any], reply_type: str) -> str:
        """
        Generate quick reply templates.
        
        Args:
            email_data: Dictionary containing email information
            reply_type: Type of quick reply (acknowledge, decline, accept, request_info)
        
        Returns:
            Quick reply text
        """
        templates = {
            "acknowledge": """
Thank you for your email regarding {subject}.

I've received your message and will review it shortly. I'll get back to you with a detailed response soon.

Best regards
""",
            "decline": """
Thank you for reaching out regarding {subject}.

Unfortunately, I won't be able to accommodate this request at this time. I appreciate your understanding.

Best regards
""",
            "accept": """
Thank you for your email regarding {subject}.

I'm happy to confirm that I can help with this. Please let me know the next steps or if you need any additional information.

Best regards
""",
            "request_info": """
Thank you for your email regarding {subject}.

To better assist you, could you please provide some additional information:
- [Specific detail needed]
- [Another detail needed]

Looking forward to your response.

Best regards
"""
        }
        
        template = templates.get(reply_type, templates["acknowledge"])
        return template.format(subject=email_data.get('subject', 'your message'))
    
    def suggest_responses(self, email_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Suggest multiple response options.
        
        Args:
            email_data: Dictionary containing email information
        
        Returns:
            Dictionary with different response options
        """
        category = email_data.get('category', 'UNKNOWN')
        
        suggestions = {}
        
        # Professional response
        suggestions['professional'] = self.draft_response(
            email_data, 
            tone="professional"
        )
        
        # Quick acknowledgment
        if category in ['URGENT', 'WORK']:
            suggestions['quick_ack'] = self.draft_quick_reply(
                email_data, 
                'acknowledge'
            )
        
        # Friendly response for personal emails
        if category == 'PERSONAL':
            suggestions['friendly'] = self.draft_response(
                email_data,
                tone="friendly and casual"
            )
        
        return suggestions
    
    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'db'):
            self.db.close()
