"""Database utilities for storing and retrieving emails."""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from config.settings import settings


class EmailDatabase:
    """SQLite database for caching emails and agent results."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        self.db_path = db_path or settings.db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables."""
        cursor = self.conn.cursor()
        
        # Emails table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                thread_id TEXT,
                subject TEXT,
                sender TEXT,
                recipient TEXT,
                body TEXT,
                received_date TIMESTAMP,
                category TEXT,
                priority INTEGER,
                sentiment TEXT,
                urgency INTEGER,
                summary TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Actions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                description TEXT,
                deadline DATE,
                priority TEXT,
                people TEXT,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails(id)
            )
        """)
        
        # Drafts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                draft_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sent BOOLEAN DEFAULT 0,
                FOREIGN KEY (email_id) REFERENCES emails(id)
            )
        """)
        
        self.conn.commit()
    
    def insert_email(self, email_data: Dict[str, Any]) -> bool:
        """Insert or update an email in the database."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO emails 
                (id, thread_id, subject, sender, recipient, body, received_date, 
                 category, priority, sentiment, urgency, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email_data.get('id'),
                email_data.get('thread_id'),
                email_data.get('subject'),
                email_data.get('sender'),
                email_data.get('recipient'),
                email_data.get('body'),
                email_data.get('received_date'),
                email_data.get('category'),
                email_data.get('priority'),
                email_data.get('sentiment'),
                email_data.get('urgency'),
                email_data.get('summary')
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting email: {e}")
            return False
    
    def get_email(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an email by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_emails_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get emails by category."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM emails WHERE category = ? ORDER BY received_date DESC LIMIT ?",
            (category, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get most recent emails."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM emails ORDER BY received_date DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def insert_action(self, action_data: Dict[str, Any]) -> bool:
        """Insert an action item."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO actions (email_id, description, deadline, priority, people)
                VALUES (?, ?, ?, ?, ?)
            """, (
                action_data.get('email_id'),
                action_data.get('description'),
                action_data.get('deadline'),
                action_data.get('priority'),
                json.dumps(action_data.get('people', []))
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting action: {e}")
            return False
    
    def get_pending_actions(self) -> List[Dict[str, Any]]:
        """Get all pending action items."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT a.*, e.subject, e.sender 
            FROM actions a
            JOIN emails e ON a.email_id = e.id
            WHERE a.completed = 0
            ORDER BY a.deadline ASC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def save_draft(self, email_id: str, draft_content: str) -> bool:
        """Save a draft response."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO drafts (email_id, draft_content)
                VALUES (?, ?)
            """, (email_id, draft_content))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving draft: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        self.conn.close()
