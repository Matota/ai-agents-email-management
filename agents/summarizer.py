"""Email summarization agent using LLM."""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from config.settings import settings
from utils.prompts import SUMMARIZATION_PROMPT
from utils.db import EmailDatabase


class EmailSummarizer:
    """Summarizes email threads and individual emails."""
    
    def __init__(self):
        """Initialize the summarizer with LLM."""
        self.llm = ChatOpenAI(
            model=settings.summary_model,
            temperature=0.5,
            api_key=settings.openai_api_key
        )
        self.db = EmailDatabase()
    
    def summarize_email(self, email_data: Dict[str, Any]) -> str:
        """
        Generate a concise summary of an email.
        
        Args:
            email_data: Dictionary containing email information
        
        Returns:
            Summary string
        """
        # Format email thread (single email for now)
        email_thread = f"""
Subject: {email_data.get('subject', '')}
From: {email_data.get('sender', '')}
Date: {email_data.get('received_date', '')}

{email_data.get('body', '')[:2000]}
"""
        
        prompt = SUMMARIZATION_PROMPT.format(email_thread=email_thread)
        
        try:
            response = self.llm.invoke(prompt)
            summary = response.content.strip()
            
            # Update database with summary
            if email_data.get('id'):
                self.db.conn.execute(
                    "UPDATE emails SET summary = ? WHERE id = ?",
                    (summary, email_data['id'])
                )
                self.db.conn.commit()
            
            return summary
        except Exception as e:
            print(f"Error summarizing email: {e}")
            return "Error generating summary"
    
    def summarize_thread(self, thread_id: str) -> str:
        """
        Summarize an entire email thread.
        
        Args:
            thread_id: Gmail thread ID
        
        Returns:
            Thread summary
        """
        # Get all emails in thread
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT * FROM emails WHERE thread_id = ? ORDER BY received_date ASC",
            (thread_id,)
        )
        emails = [dict(row) for row in cursor.fetchall()]
        
        if not emails:
            return "No emails found in thread"
        
        # Format thread
        email_thread = ""
        for i, email in enumerate(emails, 1):
            email_thread += f"""
--- Email {i} ---
Subject: {email.get('subject', '')}
From: {email.get('sender', '')}
Date: {email.get('received_date', '')}

{email.get('body', '')[:1000]}

"""
        
        prompt = SUMMARIZATION_PROMPT.format(email_thread=email_thread)
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error summarizing thread: {e}")
            return "Error generating thread summary"
    
    def get_key_points(self, email_data: Dict[str, Any]) -> List[str]:
        """
        Extract key points from an email.
        
        Args:
            email_data: Dictionary containing email information
        
        Returns:
            List of key points
        """
        summary = self.summarize_email(email_data)
        
        # Simple extraction - split by bullet points or newlines
        # In production, you'd use another LLM call for structured extraction
        key_points = []
        for line in summary.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                key_points.append(line.lstrip('-•* '))
            elif line and len(line) > 20:  # Substantial line
                key_points.append(line)
        
        return key_points[:5]  # Top 5 points
    
    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'db'):
            self.db.close()
