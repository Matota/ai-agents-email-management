# Email Management Agent

An intelligent AI agent that manages your inbox using LangChain and OpenAI GPT-4.

## Features

- 📧 **Email Reading**: Connect to Gmail via API
- 🏷️ **Smart Categorization**: Classify emails (urgent, promotional, personal, work)
- 📝 **Intelligent Summarization**: Generate concise summaries of email threads
- ✍️ **Draft Responses**: Auto-generate contextual replies with multiple tone options
- 🚨 **Priority Detection**: Flag important emails using sentiment analysis
- 📋 **Action Extraction**: Identify tasks, meetings, and deadlines
- 🧠 **Conversation Memory**: Track context across email threads
- 🎨 **Streamlit UI**: Beautiful web interface for visual interaction

## Architecture

```
Email Inbox → Fetch Agent → Categorizer → Summarizer → Action Detector
                                ↓
                          Draft Response Agent
```

## Tech Stack

- **Python 3.10+**
- **LangChain** - Agent framework
- **LangGraph** - Workflow orchestration
- **OpenAI API** - GPT-4 for understanding
- **Gmail API** - Email access
- **SQLite** - Local email cache
- **Streamlit** - Web UI
- **Rich** - Beautiful CLI output

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` and place in project root

### 3. Set Environment Variables

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 4. Run the Agent

**CLI Mode:**
```bash
python main.py --help
```

**Web UI:**
```bash
streamlit run app.py
```

## Project Structure

```
project-1-email-agent/
├── main.py                 # CLI entry point
├── app.py                  # Streamlit UI
├── agents/
│   ├── __init__.py
│   ├── email_fetcher.py    # Gmail API integration
│   ├── categorizer.py      # Email classification
│   ├── summarizer.py       # Thread summarization ✨ NEW
│   ├── responder.py        # Response generation ✨ NEW
│   └── action_extractor.py # Task/deadline detection ✨ NEW
├── utils/
│   ├── __init__.py
│   ├── db.py              # SQLite operations
│   └── prompts.py         # LLM prompts
├── config/
│   └── settings.py        # Configuration
├── tests/
│   └── test_agents.py     # Unit tests
├── credentials.json       # Gmail OAuth (gitignored)
├── .env                   # API keys (gitignored)
├── .env.example          # Example env file
├── requirements.txt      # Python dependencies
├── ARCHITECTURE.md       # Architecture documentation
└── README.md            # This file
```

## Usage

### CLI Mode

```bash
# Fetch and categorize recent emails
python main.py fetch --limit 10

# List emails by category
python main.py list-emails --category URGENT

# Summarize a specific email
python main.py summarize <email_id>

# Draft a response
python main.py draft <email_id> --tone professional

# Extract actions from an email
python main.py extract-actions <email_id>

# View all pending actions
python main.py actions

# Mark action as complete
python main.py complete-action <action_id>

# View statistics
python main.py stats

# Setup wizard
python main.py setup
```

### Streamlit UI

```bash
streamlit run app.py
```

Features:
- 📥 **Inbox View**: Browse and filter emails
- 📊 **Analytics Dashboard**: Visualize email patterns
- 📋 **Action Tracker**: Manage tasks and deadlines
- ⚙️ **Settings**: Configure and manage database

## Learning Outcomes

- ✅ LLM API integration with real-world data
- ✅ Multi-step agent workflows
- ✅ Tool/function calling (email APIs)
- ✅ Text classification and NLP
- ✅ Prompt engineering for different tasks
- ✅ State management across operations
- ✅ Working with external APIs (OAuth, rate limits)

## Next Steps

- [ ] Add email search with natural language queries
- [ ] Implement auto-reply for common scenarios
- [ ] Create email templates based on past responses
- [ ] Add support for Microsoft Outlook
- [ ] Implement email scheduling
- [ ] Add attachment handling

## License

MIT
