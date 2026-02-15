"""Email categorization agent using LLM."""

import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from config.settings import settings
from utils.prompts import CATEGORIZATION_PROMPT, SENTIMENT_PROMPT


class EmailCategorizer:
    """Categorizes emails using LLM-based classification."""
    
    def __init__(self):
        """Initialize the categorizer with LLM."""
        self.llm = ChatOpenAI(
            model=settings.categorization_model,
            temperature=0.3,
            api_key=settings.openai_api_key
        )
    
    def categorize(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize an email and determine its priority.
        
        Args:
            email_data: Dictionary containing email information
        
        Returns:
            Dictionary with category, priority, and reasoning
        """
        prompt = CATEGORIZATION_PROMPT.format(
            subject=email_data.get('subject', ''),
            sender=email_data.get('sender', ''),
            body=email_data.get('body', '')[:1000]  # Limit body length
        )
        
        try:
            response = self.llm.invoke(prompt)
            result = json.loads(response.content)
            
            return {
                'category': result.get('category', 'UNKNOWN'),
                'priority': result.get('priority', 5),
                'reasoning': result.get('reasoning', '')
            }
        except Exception as e:
            print(f"Error categorizing email: {e}")
            return {
                'category': 'UNKNOWN',
                'priority': 5,
                'reasoning': 'Error during categorization'
            }
    
    def analyze_sentiment(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment and urgency of an email.
        
        Args:
            email_data: Dictionary containing email information
        
        Returns:
            Dictionary with sentiment analysis results
        """
        prompt = SENTIMENT_PROMPT.format(
            subject=email_data.get('subject', ''),
            body=email_data.get('body', '')[:1000]
        )
        
        try:
            response = self.llm.invoke(prompt)
            result = json.loads(response.content)
            
            return {
                'sentiment': result.get('sentiment', 'neutral'),
                'urgency': result.get('urgency', 5),
                'tone': result.get('tone', 'professional'),
                'reasoning': result.get('reasoning', '')
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'urgency': 5,
                'tone': 'professional',
                'reasoning': 'Error during analysis'
            }
    
    def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an email with both categorization and sentiment analysis.
        
        Args:
            email_data: Dictionary containing email information
        
        Returns:
            Enhanced email data with categorization and sentiment
        """
        # Get category and priority
        category_result = self.categorize(email_data)
        
        # Get sentiment analysis
        sentiment_result = self.analyze_sentiment(email_data)
        
        # Merge results
        email_data.update({
            'category': category_result['category'],
            'priority': category_result['priority'],
            'sentiment': sentiment_result['sentiment'],
            'urgency': sentiment_result['urgency'],
            'tone': sentiment_result['tone']
        })
        
        return email_data
