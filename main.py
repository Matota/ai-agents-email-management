"""Main entry point for the Email Management Agent."""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from agents.email_fetcher import EmailFetcher
from agents.categorizer import EmailCategorizer
from utils.db import EmailDatabase
from config.settings import settings


console = Console()


@click.group()
def cli():
    """Email Management Agent - Intelligent inbox management powered by AI."""
    pass


@cli.command()
@click.option('--limit', default=10, help='Number of emails to fetch')
@click.option('--query', default='', help='Gmail search query')
def fetch(limit: int, query: str):
    """Fetch and categorize recent emails."""
    console.print(Panel.fit(
        "📧 Fetching and analyzing emails...",
        style="bold blue"
    ))
    
    # Initialize components
    fetcher = EmailFetcher()
    categorizer = EmailCategorizer()
    db = EmailDatabase()
    
    # Fetch emails
    emails = fetcher.fetch_recent_emails(max_results=limit, query=query)
    
    if not emails:
        console.print("[yellow]No emails found.[/yellow]")
        return
    
    # Process and store emails
    table = Table(title=f"Processed {len(emails)} Emails")
    table.add_column("Subject", style="cyan", no_wrap=False, max_width=40)
    table.add_column("From", style="magenta", max_width=30)
    table.add_column("Category", style="green")
    table.add_column("Priority", justify="center")
    table.add_column("Urgency", justify="center")
    
    for email in emails:
        # Categorize email
        processed_email = categorizer.process_email(email)
        
        # Store in database
        db.insert_email(processed_email)
        
        # Add to table
        table.add_row(
            processed_email.get('subject', 'No Subject')[:40],
            processed_email.get('sender', 'Unknown')[:30],
            processed_email.get('category', 'UNKNOWN'),
            str(processed_email.get('priority', 0)),
            str(processed_email.get('urgency', 0))
        )
    
    console.print(table)
    db.close()


@cli.command()
@click.option('--category', help='Filter by category')
@click.option('--limit', default=20, help='Number of emails to show')
def list_emails(category: str, limit: int):
    """List emails from the database."""
    db = EmailDatabase()
    
    if category:
        emails = db.get_emails_by_category(category.upper(), limit)
        title = f"Emails in category: {category.upper()}"
    else:
        emails = db.get_recent_emails(limit)
        title = "Recent Emails"
    
    if not emails:
        console.print("[yellow]No emails found.[/yellow]")
        db.close()
        return
    
    table = Table(title=title)
    table.add_column("Subject", style="cyan", no_wrap=False, max_width=40)
    table.add_column("From", style="magenta", max_width=25)
    table.add_column("Category", style="green")
    table.add_column("Priority", justify="center")
    table.add_column("Date", style="blue")
    
    for email in emails:
        table.add_row(
            email.get('subject', 'No Subject')[:40],
            email.get('sender', 'Unknown')[:25],
            email.get('category', 'UNKNOWN'),
            str(email.get('priority', 0)),
            email.get('received_date', '')[:10]
        )
    
    console.print(table)
    db.close()


@cli.command()
def stats():
    """Show email statistics."""
    db = EmailDatabase()
    emails = db.get_recent_emails(limit=1000)
    
    if not emails:
        console.print("[yellow]No emails in database.[/yellow]")
        db.close()
        return
    
    # Calculate statistics
    categories = {}
    total_priority = 0
    
    for email in emails:
        cat = email.get('category', 'UNKNOWN')
        categories[cat] = categories.get(cat, 0) + 1
        total_priority += email.get('priority', 0)
    
    # Display stats
    console.print(Panel.fit(
        f"📊 Email Statistics\n\n"
        f"Total Emails: {len(emails)}\n"
        f"Average Priority: {total_priority / len(emails):.1f}",
        style="bold green"
    ))
    
    # Category breakdown
    table = Table(title="Category Breakdown")
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="right", style="magenta")
    table.add_column("Percentage", justify="right", style="green")
    
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(emails)) * 100
        table.add_row(cat, str(count), f"{percentage:.1f}%")
    
    console.print(table)
    db.close()


@cli.command()
def setup():
    """Setup wizard for first-time configuration."""
    console.print(Panel.fit(
        "🚀 Email Management Agent Setup",
        style="bold blue"
    ))
    
    console.print("\n[bold]Step 1:[/bold] Gmail API Setup")
    console.print("""
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials.json to this directory
    """)
    
    console.print("\n[bold]Step 2:[/bold] Environment Variables")
    console.print("""
1. Copy .env.example to .env
2. Add your OpenAI API key
3. Add your email address
    """)
    
    console.print("\n[bold]Step 3:[/bold] Install Dependencies")
    console.print("""
Run: pip install -r requirements.txt
    """)
    
    console.print("\n[green]✓ Setup guide complete![/green]")
    console.print("\nRun 'python main.py fetch' to start fetching emails.")


if __name__ == '__main__':
    cli()
