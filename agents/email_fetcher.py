"""Gmail API integration for fetching emails."""

import os
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import settings


class EmailFetcher:
    """Handles fetching emails from Gmail API."""
    
    def __init__(self):
        """Initialize Gmail API client."""
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        
        # Token file stores the user's access and refresh tokens
        if os.path.exists(settings.gmail_token_path):
            creds = Credentials.from_authorized_user_file(
                settings.gmail_token_path, 
                settings.gmail_scopes
            )
        
        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.gmail_credentials_path, 
                    settings.gmail_scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(settings.gmail_token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def fetch_recent_emails(self, max_results: int = 10, query: str = "") -> List[Dict[str, Any]]:
        """
        Fetch recent emails from inbox.
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Gmail search query (e.g., "is:unread", "from:example@gmail.com")
        
        Returns:
            List of email dictionaries
        """
        try:
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print('No messages found.')
                return []
            
            emails = []
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific email.
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            Dictionary with email details
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            # Extract key headers
            subject = self._get_header(headers, 'Subject')
            sender = self._get_header(headers, 'From')
            recipient = self._get_header(headers, 'To')
            date_str = self._get_header(headers, 'Date')
            
            # Get email body
            body = self._get_email_body(message['payload'])
            
            # Parse date
            received_date = self._parse_date(date_str)
            
            return {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'subject': subject,
                'sender': sender,
                'recipient': recipient,
                'body': body,
                'received_date': received_date,
                'labels': message.get('labelIds', [])
            }
            
        except HttpError as error:
            print(f'Error fetching email {message_id}: {error}')
            return None
    
    def _get_header(self, headers: List[Dict], name: str) -> str:
        """Extract a specific header value."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload."""
        body = ''
        
        if 'parts' in payload:
            # Multi-part email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
        else:
            # Simple email
            if 'data' in payload['body']:
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8')
        
        return body
    
    def _parse_date(self, date_str: str) -> str:
        """Parse email date string to ISO format."""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except Exception:
            return datetime.now().isoformat()
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
        
        Returns:
            True if sent successfully
        """
        try:
            from email.mime.text import MIMEText
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f'Email sent to {to}')
            return True
            
        except HttpError as error:
            print(f'Error sending email: {error}')
            return False
