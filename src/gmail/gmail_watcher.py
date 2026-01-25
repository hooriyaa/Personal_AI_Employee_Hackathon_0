"""
Gmail Watcher - Monitors Gmail for new emails with specific labels.

This script polls Gmail API at regular intervals to check for new emails
with specified labels (URGENT, IMPORTANT) and saves them as Markdown files
in the Needs_Action directory.
"""

import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

from googleapiclient.errors import HttpError
from src.gmail.auth import get_gmail_service
from src.gmail.email_processor import convert_gmail_to_markdown
from src.config.settings import (
    GMAIL_POLL_INTERVAL, MAX_POLL_INTERVAL, MIN_POLL_INTERVAL,
    WATCHED_LABELS, NEEDS_ACTION_DIR, validate_credentials_exist
)


class GmailWatcher:
    """Monitors Gmail for new emails with specific labels."""

    def __init__(self):
        """Initialize the Gmail watcher."""
        self.service = None
        self.running = False
        self.last_poll_time = None

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('Logs/gmail_watcher.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Validate credentials exist
        if not validate_credentials_exist():
            self.logger.warning(
                "Credential files not found. Please follow setup instructions."
            )

    def initialize_service(self):
        """Initialize the Gmail API service."""
        try:
            self.service = get_gmail_service()
            self.logger.info("Gmail API service initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Gmail service: {e}")
            return False

    def build_query(self):
        """Build the Gmail search query to identify UNREAD emails with "URGENT" or "IMPORTANT" labels."""
        # Start with unread emails
        query_parts = ["is:unread"]

        # Add label filters for URGENT or IMPORTANT
        label_filters = []
        for label in WATCHED_LABELS:
            # Handle both Gmail system labels and user labels
            clean_label = label.strip().lower()
            if clean_label in ['urgent', 'important']:
                # For backward compatibility, also search for capitalized versions
                label_filters.append(f"label:{clean_label}")
                label_filters.append(f"label:{clean_label.upper()}")
            else:
                label_filters.append(f"label:{clean_label}")

        if label_filters:
            # Join all label conditions with OR inside parentheses
            labels_query = "(" + " OR ".join(label_filters) + ")"
            query_parts.append(labels_query)

        # Join all parts with AND operator
        query = " ".join(query_parts)
        return query

    def get_new_emails(self):
        """Fetch new emails matching the query."""
        if not self.service:
            if not self.initialize_service():
                return []

        try:
            query = self.build_query()
            self.logger.info(f"Searching for emails with query: {query}")

            # Get messages matching the query
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100  # Limit to 100 results to avoid overwhelming
            ).execute()

            messages = results.get('messages', [])
            self.logger.info(f"Found {len(messages)} matching emails")

            # Get full message details
            detailed_messages = []
            for msg in messages:
                try:
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    detailed_messages.append(full_msg)
                except HttpError as e:
                    self.logger.error(f"Error fetching message {msg['id']}: {e}")

            return detailed_messages

        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            # Handle specific error codes
            if e.resp.status == 401:
                self.logger.error("Authentication error. Please re-authenticate.")
                self.service = None  # Force re-authentication on next attempt
            elif e.resp.status == 403:
                self.logger.error("Quota exceeded. Consider increasing poll interval.")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error fetching emails: {e}")
            return []

    def mark_email_as_read(self, email_id):
        """Mark an email as read after processing."""
        if not self.service:
            return False

        try:
            # Modify message labels to remove 'UNREAD'
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as e:
            self.logger.error(f"Error marking email {email_id} as read: {e}")
            return False

    def process_emails(self):
        """Process new emails and save them as Markdown files in `/Needs_Action` directory."""
        # Get new emails
        emails = self.get_new_emails()
        processed_count = 0

        for email in emails:
            try:
                # Convert email to Markdown and save
                file_path = convert_gmail_to_markdown(
                    email,
                    self.service,
                    NEEDS_ACTION_DIR
                )

                if file_path:
                    email_id = email['id']

                    # Mark email as read after successful processing
                    if self.mark_email_as_read(email_id):
                        self.logger.info(f"Processed and marked as read: {email_id}")
                    else:
                        self.logger.warning(f"Could not mark as read: {email_id}")

                    processed_count += 1
                else:
                    self.logger.error(f"Failed to process email: {email.get('id', 'unknown')}")

            except Exception as e:
                self.logger.error(f"Error processing individual email: {e}")

        return processed_count

    def poll_once(self):
        """Perform a single polling cycle."""
        self.logger.info("Starting polling cycle...")

        # Process emails and get count of processed emails
        processed_count = self.process_emails()

        if processed_count > 0:
            self.logger.info(f"Completed processing {processed_count} emails")
        else:
            self.logger.info("No new emails found")

        # Update last poll time
        self.last_poll_time = datetime.now()

    def run(self):
        """Start the continuous polling process."""
        self.logger.info("Starting Gmail Watcher...")
        self.running = True

        # Validate poll interval
        poll_interval = max(MIN_POLL_INTERVAL, min(GMAIL_POLL_INTERVAL, MAX_POLL_INTERVAL))
        self.logger.info(f"Polling interval set to {poll_interval} seconds")

        while self.running:
            try:
                # Perform a polling cycle
                self.poll_once()

                # Sleep for the specified interval
                self.logger.info(f"Sleeping for {poll_interval} seconds...")
                time.sleep(poll_interval)

            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal. Stopping...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in polling loop: {e}")
                # Wait before retrying to avoid rapid error cycles
                time.sleep(min(poll_interval, 30))

    def stop(self):
        """Stop the polling process."""
        self.logger.info("Stopping Gmail Watcher...")
        self.running = False


def main():
    """Main entry point for the Gmail Watcher."""
    watcher = GmailWatcher()

    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        watcher.stop()


if __name__ == "__main__":
    main()