"""Action extraction agent using LLM."""

import json
from typing import Dict, Any, List
from datetime import datetime
from langchain_openai import ChatOpenAI
from config.settings import settings
from utils.prompts import ACTION_EXTRACTION_PROMPT
from utils.db import EmailDatabase


class ActionExtractor:
    """Extracts actionable items from emails."""
    
    def __init__(self):
        """Initialize the action extractor with LLM."""
        self.llm = ChatOpenAI(
            model=settings.categorization_model,
            temperature=0.3,
            api_key=settings.openai_api_key
        )
        self.db = EmailDatabase()
    
    def extract_actions(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract action items from an email.
        
        Args:
            email_data: Dictionary containing email information
        
        Returns:
            List of action items
        """
        prompt = ACTION_EXTRACTION_PROMPT.format(
            subject=email_data.get('subject', ''),
            body=email_data.get('body', '')[:2000]
        )
        
        try:
            response = self.llm.invoke(prompt)
            result = json.loads(response.content)
            actions = result.get('actions', [])
            
            # Store actions in database
            email_id = email_data.get('id')
            if email_id and actions:
                for action in actions:
                    action_data = {
                        'email_id': email_id,
                        'description': action.get('description', ''),
                        'deadline': action.get('deadline'),
                        'priority': action.get('priority', 'medium'),
                        'people': action.get('people', [])
                    }
                    self.db.insert_action(action_data)
            
            return actions
        except Exception as e:
            print(f"Error extracting actions: {e}")
            return []
    
    def get_upcoming_deadlines(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get actions with upcoming deadlines.
        
        Args:
            days: Number of days to look ahead
        
        Returns:
            List of actions with deadlines
        """
        from datetime import timedelta
        
        cursor = self.db.conn.cursor()
        today = datetime.now().date()
        future_date = today + timedelta(days=days)
        
        cursor.execute("""
            SELECT a.*, e.subject, e.sender 
            FROM actions a
            JOIN emails e ON a.email_id = e.id
            WHERE a.completed = 0 
            AND a.deadline IS NOT NULL
            AND a.deadline BETWEEN ? AND ?
            ORDER BY a.deadline ASC
        """, (today.isoformat(), future_date.isoformat()))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_high_priority_actions(self) -> List[Dict[str, Any]]:
        """
        Get all high priority actions.
        
        Returns:
            List of high priority actions
        """
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT a.*, e.subject, e.sender 
            FROM actions a
            JOIN emails e ON a.email_id = e.id
            WHERE a.completed = 0 
            AND a.priority = 'high'
            ORDER BY a.deadline ASC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_action_complete(self, action_id: int) -> bool:
        """
        Mark an action as completed.
        
        Args:
            action_id: ID of the action to complete
        
        Returns:
            True if successful
        """
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "UPDATE actions SET completed = 1 WHERE id = ?",
                (action_id,)
            )
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Error marking action complete: {e}")
            return False
    
    def get_action_summary(self) -> Dict[str, int]:
        """
        Get summary statistics of actions.
        
        Returns:
            Dictionary with action counts
        """
        cursor = self.db.conn.cursor()
        
        # Total pending
        cursor.execute("SELECT COUNT(*) FROM actions WHERE completed = 0")
        total_pending = cursor.fetchone()[0]
        
        # High priority
        cursor.execute(
            "SELECT COUNT(*) FROM actions WHERE completed = 0 AND priority = 'high'"
        )
        high_priority = cursor.fetchone()[0]
        
        # Overdue
        today = datetime.now().date().isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM actions WHERE completed = 0 AND deadline < ?",
            (today,)
        )
        overdue = cursor.fetchone()[0]
        
        return {
            'total_pending': total_pending,
            'high_priority': high_priority,
            'overdue': overdue
        }
    
    def __del__(self):
        """Close database connection."""
        if hasattr(self, 'db'):
            self.db.close()
