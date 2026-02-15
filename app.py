"""Streamlit UI for Email Management Agent."""

import streamlit as st
import pandas as pd
from datetime import datetime
from agents.email_fetcher import EmailFetcher
from agents.categorizer import EmailCategorizer
from agents.summarizer import EmailSummarizer
from agents.responder import EmailResponder
from agents.action_extractor import ActionExtractor
from utils.db import EmailDatabase


# Page config
st.set_page_config(
    page_title="Email Management Agent",
    page_icon="📧",
    layout="wide"
)

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = EmailDatabase()

# Sidebar
st.sidebar.title("📧 Email Agent")
page = st.sidebar.radio(
    "Navigation",
    ["📥 Inbox", "📊 Analytics", "📋 Actions", "⚙️ Settings"]
)

# Main content
if page == "📥 Inbox":
    st.title("📥 Email Inbox")
    
    # Fetch emails section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Fetch New Emails")
    with col2:
        if st.button("🔄 Fetch Emails", type="primary"):
            with st.spinner("Fetching emails..."):
                try:
                    fetcher = EmailFetcher()
                    categorizer = EmailCategorizer()
                    
                    emails = fetcher.fetch_recent_emails(max_results=10)
                    
                    for email in emails:
                        processed = categorizer.process_email(email)
                        st.session_state.db.insert_email(processed)
                    
                    st.success(f"✓ Fetched {len(emails)} emails!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Filter options
    st.subheader("Filter Emails")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.selectbox(
            "Category",
            ["All", "URGENT", "WORK", "PERSONAL", "PROMOTIONAL", "FINANCE"]
        )
    
    with col2:
        min_priority = st.slider("Min Priority", 1, 10, 1)
    
    with col3:
        limit = st.number_input("Limit", 10, 100, 20)
    
    # Get emails
    if category_filter == "All":
        emails = st.session_state.db.get_recent_emails(limit=limit)
    else:
        emails = st.session_state.db.get_emails_by_category(category_filter, limit=limit)
    
    # Filter by priority
    emails = [e for e in emails if e.get('priority', 0) >= min_priority]
    
    if not emails:
        st.info("No emails found. Click 'Fetch Emails' to get started!")
    else:
        # Display emails
        for email in emails:
            with st.expander(
                f"📧 {email.get('subject', 'No Subject')} - "
                f"{email.get('category', 'UNKNOWN')} (Priority: {email.get('priority', 0)})"
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**From:** {email.get('sender', 'Unknown')}")
                    st.markdown(f"**Date:** {email.get('received_date', '')[:10]}")
                    st.markdown(f"**Category:** {email.get('category', 'UNKNOWN')}")
                    st.markdown(f"**Priority:** {email.get('priority', 0)}/10")
                    st.markdown(f"**Sentiment:** {email.get('sentiment', 'neutral')}")
                
                with col2:
                    if st.button("📝 Summarize", key=f"sum_{email.get('id')}"):
                        with st.spinner("Summarizing..."):
                            summarizer = EmailSummarizer()
                            summary = summarizer.summarize_email(email)
                            st.info(summary)
                    
                    if st.button("✍️ Draft Reply", key=f"draft_{email.get('id')}"):
                        with st.spinner("Drafting response..."):
                            responder = EmailResponder()
                            draft = responder.draft_response(email)
                            st.success("Draft Response:")
                            st.text_area("", draft, height=200, key=f"draft_text_{email.get('id')}")
                    
                    if st.button("📋 Extract Actions", key=f"action_{email.get('id')}"):
                        with st.spinner("Extracting actions..."):
                            extractor = ActionExtractor()
                            actions = extractor.extract_actions(email)
                            if actions:
                                st.success(f"Found {len(actions)} action(s)!")
                                for action in actions:
                                    st.markdown(f"- {action.get('description')} (Priority: {action.get('priority')})")
                            else:
                                st.warning("No actions found")
                
                # Email body
                st.markdown("---")
                st.markdown("**Email Body:**")
                st.text(email.get('body', '')[:500] + "..." if len(email.get('body', '')) > 500 else email.get('body', ''))

elif page == "📊 Analytics":
    st.title("📊 Email Analytics")
    
    emails = st.session_state.db.get_recent_emails(limit=1000)
    
    if not emails:
        st.info("No emails to analyze. Fetch some emails first!")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Emails", len(emails))
        
        with col2:
            avg_priority = sum(e.get('priority', 0) for e in emails) / len(emails)
            st.metric("Avg Priority", f"{avg_priority:.1f}")
        
        with col3:
            urgent_count = sum(1 for e in emails if e.get('category') == 'URGENT')
            st.metric("Urgent Emails", urgent_count)
        
        with col4:
            high_priority = sum(1 for e in emails if e.get('priority', 0) >= 7)
            st.metric("High Priority", high_priority)
        
        # Category distribution
        st.subheader("Category Distribution")
        categories = {}
        for email in emails:
            cat = email.get('category', 'UNKNOWN')
            categories[cat] = categories.get(cat, 0) + 1
        
        df_categories = pd.DataFrame(
            list(categories.items()),
            columns=['Category', 'Count']
        )
        st.bar_chart(df_categories.set_index('Category'))
        
        # Priority distribution
        st.subheader("Priority Distribution")
        priorities = [e.get('priority', 0) for e in emails]
        df_priorities = pd.DataFrame({'Priority': priorities})
        st.bar_chart(df_priorities['Priority'].value_counts().sort_index())
        
        # Sentiment analysis
        st.subheader("Sentiment Analysis")
        sentiments = {}
        for email in emails:
            sent = email.get('sentiment', 'neutral')
            sentiments[sent] = sentiments.get(sent, 0) + 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Positive", sentiments.get('positive', 0))
        with col2:
            st.metric("Neutral", sentiments.get('neutral', 0))
        with col3:
            st.metric("Negative", sentiments.get('negative', 0))

elif page == "📋 Actions":
    st.title("📋 Action Items")
    
    extractor = ActionExtractor()
    
    # Summary
    summary = extractor.get_action_summary()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Pending", summary['total_pending'])
    with col2:
        st.metric("High Priority", summary['high_priority'])
    with col3:
        st.metric("Overdue", summary['overdue'])
    
    # Pending actions
    st.subheader("Pending Actions")
    pending = extractor.db.get_pending_actions()
    
    if not pending:
        st.info("No pending actions!")
    else:
        for action in pending:
            col1, col2 = st.columns([4, 1])
            
            with col1:
                priority_emoji = "🔴" if action.get('priority') == 'high' else "🟡" if action.get('priority') == 'medium' else "🟢"
                st.markdown(f"{priority_emoji} **{action.get('description')}**")
                st.caption(f"From: {action.get('subject', 'Unknown')} | Deadline: {action.get('deadline', 'None')}")
            
            with col2:
                if st.button("✓ Complete", key=f"complete_{action.get('id')}"):
                    extractor.mark_action_complete(action.get('id'))
                    st.success("Marked complete!")
                    st.rerun()
    
    # Upcoming deadlines
    st.subheader("Upcoming Deadlines (Next 7 Days)")
    upcoming = extractor.get_upcoming_deadlines(days=7)
    
    if upcoming:
        for action in upcoming:
            st.warning(f"⏰ {action.get('description')} - Due: {action.get('deadline')}")
    else:
        st.info("No upcoming deadlines")

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.subheader("Configuration")
    
    st.info("""
    **Setup Instructions:**
    
    1. **Gmail API**: Configure OAuth credentials in `credentials.json`
    2. **OpenAI API**: Add your API key to `.env` file
    3. **Email Address**: Set your email in `.env`
    
    See README.md for detailed setup instructions.
    """)
    
    st.subheader("Database Info")
    emails = st.session_state.db.get_recent_emails(limit=10000)
    st.metric("Total Emails in Database", len(emails))
    
    if st.button("🗑️ Clear Database", type="secondary"):
        if st.checkbox("I understand this will delete all data"):
            # Clear tables
            st.session_state.db.conn.execute("DELETE FROM emails")
            st.session_state.db.conn.execute("DELETE FROM actions")
            st.session_state.db.conn.execute("DELETE FROM drafts")
            st.session_state.db.conn.commit()
            st.success("Database cleared!")
            st.rerun()
