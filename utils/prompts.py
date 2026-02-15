"""Prompt templates for different agent tasks."""

# Email Categorization Prompt
CATEGORIZATION_PROMPT = """You are an email categorization expert. Analyze the following email and categorize it.

Email Subject: {subject}
Email From: {sender}
Email Body: {body}

Categorize this email into ONE of the following categories:
- URGENT: Requires immediate attention or response
- WORK: Work-related, professional communication
- PERSONAL: Personal communication from friends/family
- PROMOTIONAL: Marketing, newsletters, promotions
- SOCIAL: Social media notifications, updates
- FINANCE: Banking, bills, financial statements
- SPAM: Unwanted or suspicious emails

Also rate the priority on a scale of 1-10 (10 being highest priority).

Respond in JSON format:
{{
    "category": "CATEGORY_NAME",
    "priority": 7,
    "reasoning": "Brief explanation of why this category was chosen"
}}
"""

# Email Summarization Prompt
SUMMARIZATION_PROMPT = """You are an expert at summarizing email conversations. 

Email Thread:
{email_thread}

Provide a concise summary that includes:
1. Main topic/purpose of the email
2. Key points or requests
3. Any action items or deadlines
4. Important people mentioned

Keep the summary under 150 words and focus on actionable information.

Summary:
"""

# Response Drafting Prompt
RESPONSE_DRAFT_PROMPT = """You are a professional email assistant. Draft a response to the following email.

Original Email:
Subject: {subject}
From: {sender}
Body: {body}

Context about the recipient:
{user_context}

Draft a professional, concise response that:
1. Acknowledges the main points
2. Addresses any questions or requests
3. Maintains a friendly but professional tone
4. Is clear and actionable

Draft Response:
"""

# Action Extraction Prompt
ACTION_EXTRACTION_PROMPT = """You are an expert at extracting actionable items from emails.

Email Content:
Subject: {subject}
Body: {body}

Extract all actionable items including:
- Tasks that need to be completed
- Meetings or events mentioned
- Deadlines or due dates
- Questions that need answers
- Decisions that need to be made

For each action item, identify:
1. The action description
2. Any deadline or due date
3. Priority level (high/medium/low)
4. Any people involved

Respond in JSON format:
{{
    "actions": [
        {{
            "description": "Action description",
            "deadline": "YYYY-MM-DD or null",
            "priority": "high/medium/low",
            "people": ["person1", "person2"]
        }}
    ]
}}
"""

# Sentiment Analysis Prompt
SENTIMENT_PROMPT = """Analyze the sentiment and urgency of this email.

Email:
Subject: {subject}
Body: {body}

Determine:
1. Overall sentiment (positive/neutral/negative)
2. Urgency level (1-10, where 10 is most urgent)
3. Emotional tone (professional/casual/frustrated/excited/etc.)

Respond in JSON format:
{{
    "sentiment": "positive/neutral/negative",
    "urgency": 7,
    "tone": "professional",
    "reasoning": "Brief explanation"
}}
"""
