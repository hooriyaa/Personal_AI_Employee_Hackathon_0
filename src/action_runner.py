"""
Action Runner - Executes approved actions from the `/Approved` directory.

This script monitors the `/Approved` directory for new files and executes
the specified actions based on the file content. Currently supports
email sending actions.
"""

import time
import logging
import yaml
import json
from pathlib import Path
from datetime import datetime
import re

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

from src.gmail.auth import get_gmail_service
from src.config.settings import APPROVED_DIR, DONE_DIR
from src.utils.helpers import move_file


class ActionRunner:
    """Executes approved actions from the Approved directory."""

    def __init__(self):
        """Initialize the action runner."""
        self.service = None
        self.running = False

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('Logs/action_runner.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def initialize_service(self):
        """Initialize the Gmail API service."""
        try:
            self.service = get_gmail_service()
            self.logger.info("Gmail API service initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Gmail service: {e}")
            return False

    def create_message(self, sender, to, subject, body):
        """
        Create a message for an email.

        Args:
            sender (str): Email address of the sender
            to (str): Recipient email address(es)
            subject (str): Email subject
            body (str): Email body

        Returns:
            dict: Message object
        """
        message = MIMEText(body)
        # Handle various email formats including "Name" <email@domain.com>
        message['to'] = self._format_email_address(to)
        message['from'] = sender
        message['subject'] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def _format_email_address(self, email_str):
        """
        Format email address properly for use in message headers.

        Args:
            email_str (str): Raw email string which might be in various formats

        Returns:
            str: Properly formatted email address
        """
        import re
        # Remove extra whitespace
        email_str = email_str.strip()

        # If it's in the format "Name" <email@domain.com> or Name <email@domain.com>
        # Extract just the email address part
        if '<' in email_str and '>' in email_str:
            # Use regex to extract email from angle brackets
            match = re.search(r'<([^>]+)>', email_str)
            if match:
                return match.group(1).strip()
            else:
                # If regex fails, return as is but cleaned
                return email_str
        elif '@' in email_str and ' ' not in email_str:
            # Simple email format: email@domain.com
            return email_str
        else:
            # If it's not a recognizable format, return as is but cleaned
            return email_str

    def send_email(self, to, subject, body):
        """
        Send an email using the Gmail API.

        Args:
            to (str): Recipient email address(es)
            subject (str): Email subject
            body (str): Email body

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.service:
            if not self.initialize_service():
                return False

        try:
            # Get the user's email address
            profile = self.service.users().getProfile(userId='me').execute()
            sender = profile.get('emailAddress', '')

            # Create the message
            message = self.create_message(sender, to, subject, body)

            # Send the message
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            self.logger.info(f"Message sent successfully. Message Id: {sent_message['id']}")
            return True

        except HttpError as error:
            self.logger.error(f"An error occurred while sending email: {error}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error while sending email: {e}")
            return False

    def parse_action_file(self, file_path):
        """
        Parse an action file to extract action details.

        Args:
            file_path (Path): Path to the action file

        Returns:
            dict: Parsed action details or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse as YAML first
            try:
                action_data = yaml.safe_load(content)
                if action_data:
                    return action_data
            except yaml.YAMLError:
                self.logger.debug("File is not in YAML format, trying to extract data differently")

            # If YAML parsing fails, try to extract information using structured approach
            action_data = {}

            # Split content into lines for processing
            lines = content.strip().split('\n')

            # Track where header ends and body begins
            header_end_idx = -1
            for i, line in enumerate(lines):
                # Look for empty line that separates headers from body
                if line.strip() == '':
                    header_end_idx = i
                    break

            # Process headers if they exist
            if header_end_idx != -1:
                header_lines = lines[:header_end_idx]

                # Parse header fields
                for line in header_lines:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()

                        if key == 'type':
                            action_data['type'] = value.lower()
                        elif key == 'to':
                            action_data['to'] = value
                        elif key == 'subject':
                            action_data['subject'] = value
                        elif key == 'body':
                            # If body is specified in headers, use that value
                            action_data['body'] = value

                # Extract body content from the rest of the file
                body_lines = lines[header_end_idx + 1:]  # Skip the empty line
                body_content = '\n'.join(body_lines).strip()

                # Only set body if it wasn't already set from the 'body:' header
                if 'body' not in action_data:
                    action_data['body'] = body_content
            else:
                # No clear separation between headers and body, try line-by-line parsing approach
                # This handles cases like:
                # type: email_send
                # to: email@example.com
                # subject: Subject
                # body: This is the first line
                # This is the second line
                i = 0
                while i < len(lines):
                    line = lines[i].strip()

                    if line and ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()

                        if key == 'type':
                            action_data['type'] = value.lower()
                        elif key == 'to':
                            action_data['to'] = value
                        elif key == 'subject':
                            action_data['subject'] = value
                        elif key == 'body':
                            # The body might continue on subsequent lines that don't start with a field name
                            body_parts = [value]
                            i += 1
                            while i < len(lines):
                                next_line = lines[i].strip()
                                # If the next line is not empty and doesn't look like a field (doesn't have colon early in the line)
                                # we consider it part of the body
                                if next_line:
                                    # Check if this looks like a new field (has colon near the beginning)
                                    words = next_line.split()
                                    has_colon_as_field_separator = any(word.endswith(':') for word in words[:2])  # Check first couple of words

                                    if not has_colon_as_field_separator:
                                        body_parts.append(next_line)
                                        i += 1
                                    else:
                                        # This looks like a new field, so break and process normally
                                        break
                                else:
                                    # Empty line, continue to next
                                    i += 1
                            action_data['body'] = '\n'.join(body_parts).strip()
                            continue  # Don't increment i again since we already did in the loop
                    i += 1

            return action_data

        except Exception as e:
            self.logger.error(f"Error parsing action file {file_path}: {e}")
            return None

    def execute_action(self, action_data, original_file_path):
        """
        Execute an action based on its type.

        Args:
            action_data (dict): Action details
            original_file_path (Path): Path to the original action file

        Returns:
            bool: True if action executed successfully, False otherwise
        """
        action_type = action_data.get('type', '').lower()

        if action_type == 'email_send':
            return self.execute_email_send_action(action_data, original_file_path)
        else:
            self.logger.warning(f"Unknown action type: {action_type}")
            return False

    def execute_email_send_action(self, action_data, original_file_path):
        """
        Execute an email send action.

        Args:
            action_data (dict): Email action details
            original_file_path (Path): Path to the original action file

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        to = action_data.get('to')
        subject = action_data.get('subject')
        body = action_data.get('body', '')

        if not to or not subject:
            self.logger.error(f"Missing required fields for email action in {original_file_path}")
            return False

        self.logger.info(f"Sending email to: {to}, subject: {subject}")

        success = self.send_email(to, subject, body)

        if success:
            self.logger.info(f"Email sent successfully: {original_file_path}")
        else:
            self.logger.error(f"Failed to send email: {original_file_path}")

        return success

    def process_approved_file(self, file_path):
        """
        Process a file in the Approved directory.

        Args:
            file_path (Path): Path to the approved file
        """
        self.logger.info(f"Processing approved file: {file_path}")

        # Parse the action file
        action_data = self.parse_action_file(file_path)

        if not action_data:
            self.logger.error(f"Could not parse action file: {file_path}")
            return

        # Execute the action
        success = self.execute_action(action_data, file_path)

        # Move the file to Done regardless of success/failure
        done_dir = DONE_DIR
        done_dir.mkdir(parents=True, exist_ok=True)

        # Create destination path in Done directory
        dest_path = done_dir / file_path.name

        # Move the file
        if move_file(file_path, dest_path):
            self.logger.info(f"Moved processed file from Approved to Done: {file_path.name}")
        else:
            self.logger.error(f"Failed to move processed file: {file_path.name}")

    def run_once(self):
        """Process all files in the Approved directory."""
        approved_files = list(APPROVED_DIR.glob("*.md")) + list(APPROVED_DIR.glob("*.txt"))

        for file_path in approved_files:
            try:
                self.process_approved_file(file_path)
            except Exception as e:
                self.logger.error(f"Error processing approved file {file_path}: {e}")

    def run(self):
        """Start the action runner loop."""
        self.logger.info("Starting Action Runner...")
        self.running = True

        while self.running:
            try:
                # Process all approved files
                self.run_once()

                # Sleep for a bit before checking again
                time.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal. Stopping...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in action runner loop: {e}")
                # Wait before retrying to avoid rapid error cycles
                time.sleep(30)

    def stop(self):
        """Stop the action runner."""
        self.logger.info("Stopping Action Runner...")
        self.running = False


def main():
    """Main entry point for the Action Runner."""
    runner = ActionRunner()

    try:
        runner.run()
    except KeyboardInterrupt:
        print("\nShutting down Action Runner...")
        runner.stop()


if __name__ == "__main__":
    main()