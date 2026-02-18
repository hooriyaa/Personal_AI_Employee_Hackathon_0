"""
Action Runner - Executes approved actions from the `/Approved` directory.

This script monitors the `/Approved` directory for new files and executes
the specified actions based on the file content. Currently supports
email sending actions, LinkedIn posting, and Tool Actions (Odoo & Social Media).
"""

import time
import logging
import yaml
import json
import ast
import inspect
import asyncio
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
from src.skills.accounting_odoo_skill import AccountingOdooSkill
from src.skills.social_media_skill import SocialMediaSkill

# Import the LinkedIn poster module
try:
    from src.linkedin.poster import LinkedInPoster
    LINKEDIN_AVAILABLE = True
except ImportError:
    LINKEDIN_AVAILABLE = False
    print("LinkedIn poster module not found. Install selenium and webdriver-manager to enable LinkedIn posting.")


class ActionRunner:
    """Executes approved actions from the Approved directory."""

    def __init__(self):
        """Initialize the action runner."""
        self.service = None
        self.running = False

        # Configure logging
        import sys
        import io
        
        # Create a custom stream handler that handles Unicode properly
        class SafeStreamHandler(logging.StreamHandler):
            def emit(self, record):
                try:
                    msg = self.format(record)
                    # Encode/decode to handle Unicode characters safely
                    safe_msg = msg.encode('utf-8', errors='replace').decode('utf-8')
                    stream = self.stream
                    # Write the safe message to the stream
                    stream.write(safe_msg + self.terminator)
                    self.flush()
                except Exception:
                    # Fallback to basic error handling
                    self.handleError(record)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('Logs/action_runner.log'),
                SafeStreamHandler()
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
                                    # We'll check if the line starts with a typical field name followed by a colon
                                    starts_with_field = any(next_line.lower().startswith(field + ':')
                                                           for field in ['type', 'to', 'subject', 'body', 'from', 'cc', 'bcc'])

                                    if not starts_with_field:
                                        body_parts.append(next_line)
                                        i += 1
                                    else:
                                        # This looks like a new field, so break and process normally
                                        break
                                else:
                                    # Empty line - could be part of body content, so include it
                                    body_parts.append(next_line)
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
        elif action_type == 'linkedin_post':
            return self.execute_linkedin_post_action(action_data, original_file_path)
        elif action_type == 'approval_request':
            return self.execute_approval_request_action(action_data, original_file_path)
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

        # Safely log the email details to handle Unicode characters like emojis
        safe_to = to.encode('ascii', 'replace').decode('ascii') if isinstance(to, str) else str(to)
        safe_subject = subject.encode('ascii', 'replace').decode('ascii') if isinstance(subject, str) else str(subject)
        self.logger.info(f"Sending email to: {safe_to}, subject: {safe_subject}")

        success = self.send_email(to, subject, body)

        if success:
            self.logger.info(f"Email sent successfully: {original_file_path}")
        else:
            self.logger.error(f"Failed to send email: {original_file_path}")

        return success

    def execute_linkedin_post_action(self, action_data, original_file_path):
        """
        Execute a LinkedIn post action.

        Args:
            action_data (dict): LinkedIn post action details
            original_file_path (Path): Path to the original action file

        Returns:
            bool: True if post was successful, False otherwise
        """
        # Try to get content from 'content' field first, then fall back to 'body' field
        content = action_data.get('content', '')
        if not content:
            content = action_data.get('body', '')

        if not content:
            self.logger.error(f"Missing required 'content' or 'body' field for LinkedIn post action in {original_file_path}")
            return False

        # Safely log the LinkedIn post content to handle Unicode characters like emojis
        safe_content_preview = content[:50].encode('ascii', 'replace').decode('ascii') if isinstance(content, str) else str(content[:50])
        self.logger.info(f"Posting to LinkedIn: {safe_content_preview}...")  # Log first 50 chars

        # Check if LinkedIn functionality is available
        if not LINKEDIN_AVAILABLE:
            self.logger.error("LinkedIn poster module not available. Cannot post to LinkedIn.")
            return False

        # Create LinkedInPoster instance and execute the post
        try:
            poster = LinkedInPoster()
            result = poster.post_to_linkedin(content)
            
            if result.get("success"):
                self.logger.info(f"LinkedIn post content populated successfully: {original_file_path}")
                print(result.get("message", "LinkedIn post content populated successfully. Please review and click 'Post' manually."))
                return True
            else:
                error_msg = result.get("error", "Unknown error occurred")
                self.logger.error(f"Failed to post to LinkedIn: {error_msg}")
                return False
        except Exception as e:
            self.logger.error(f"Error executing LinkedIn post: {e}")
            return False

    def execute_approval_request_action(self, action_data, original_file_path):
        """
        Execute a tool action (Odoo or Social Media) from an approval request file.

        Args:
            action_data (dict): Action details
            original_file_path (Path): Path to the original action file

        Returns:
            bool: True if action executed successfully, False otherwise
        """
        try:
            # Read the full file content to extract tool action details
            with open(original_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract tool name (e.g., "AccountingOdooSkill")
            tool = action_data.get('tool')
            if not tool:
                # Try to extract from content if not in action_data
                tool_match = re.search(r'tool:\s*(\w+)', content)
                if tool_match:
                    tool = tool_match.group(1)
            
            if not tool:
                self.logger.error(f"Missing 'tool' field in {original_file_path}")
                return False

            # Extract action name (e.g., "create_invoice")
            action = action_data.get('action')
            if not action:
                # Try to extract from content if not in action_data
                action_match = re.search(r'action:\s*(\w+)', content)
                if action_match:
                    action = action_match.group(1)
            
            if not action:
                self.logger.error(f"Missing 'action' field in {original_file_path}")
                return False

            # Extract Tool Arguments dictionary using ast.literal_eval
            # Look for text between "Tool Arguments:" and next "---" or end of file
            arguments = {}
            args_match = re.search(r'Tool Arguments:\s*\n(.*?)(?:\n---|\Z)', content, re.DOTALL)
            if args_match:
                args_str = args_match.group(1).strip()
                try:
                    arguments = ast.literal_eval(args_str)
                except (ValueError, SyntaxError) as e:
                    self.logger.error(f"Failed to parse Tool Arguments in {original_file_path}: {e}")
                    return False
            else:
                self.logger.warning(f"No Tool Arguments found in {original_file_path}")

            # Safely log the action details
            safe_tool = tool.encode('ascii', 'replace').decode('ascii')
            safe_action = action.encode('ascii', 'replace').decode('ascii')
            self.logger.info(f"Executing tool action: {safe_tool}.{safe_action}")

            # Execute the appropriate tool based on tool name
            result = None
            
            if tool == 'AccountingOdooSkill':
                result = self._execute_odoo_action(action, arguments, original_file_path)
            elif tool == 'SocialMediaSkill':
                result = self._execute_social_media_action(action, arguments, original_file_path)
            else:
                self.logger.error(f"Unknown tool: {tool}")
                return False

            # Log the result
            if result:
                self.logger.info(f"Tool action executed successfully: {safe_tool}.{safe_action}")
                self.logger.info(f"Result: {result}")
                return True
            else:
                self.logger.error(f"Tool action failed: {safe_tool}.{safe_action}")
                return False

        except Exception as e:
            self.logger.error(f"Error executing approval request action: {e}")
            return False

    def _execute_odoo_action(self, action, arguments, original_file_path):
        """
        Execute an Odoo tool action.

        Args:
            action (str): Action name (e.g., "create_invoice")
            arguments (dict): Tool arguments
            original_file_path (Path): Path to the original action file

        Returns:
            dict: Action result or None if failed
        """
        try:
            # Instantiate the skill
            skill = AccountingOdooSkill()

            # Get the method
            method = getattr(skill, action, None)

            if method is None:
                self.logger.error(f"Action '{action}' not found in AccountingOdooSkill")
                return None

            # Create a robust argument mapping dictionary
            # Maps common agent-generated keys to skill-expected keys
            arg_mapping = {
                'customer': 'client_name',
                'partner_name': 'client_name',
                'client': 'client_name',
                'company': 'client_name',
                'cost': 'amount',
                'price': 'amount',
                'total': 'amount',
                'value': 'amount',
                'desc': 'description',
                'details': 'description',
                'note': 'description',
                'memo': 'description'
            }

            # Apply mapping: create a copy and rename keys
            mapped_arguments = dict(arguments)
            for old_key, new_key in arg_mapping.items():
                if old_key in mapped_arguments and new_key not in mapped_arguments:
                    mapped_arguments[new_key] = mapped_arguments.pop(old_key)

            # Log the mapping for debugging
            if mapped_arguments != arguments:
                self.logger.info(f"Argument mapping applied: {arguments} -> {mapped_arguments}")

            # Call the method with arguments - Smart async detection
            result = None
            try:
                if inspect.iscoroutinefunction(method):
                    # Async method - use asyncio.run()
                    result = asyncio.run(method(**mapped_arguments))
                else:
                    # Synchronous method - call directly
                    result = method(**mapped_arguments)
            except Exception as exec_error:
                self.logger.error(
                    f"Execution Failed for {action}: {exec_error}",
                    exc_info=True
                )
                return None

            return result

        except Exception as e:
            self.logger.error(f"Error executing Odoo action '{action}': {e}", exc_info=True)
            return None

    def _execute_social_media_action(self, action, arguments, original_file_path):
        """
        Execute a Social Media tool action.

        Args:
            action (str): Action name (e.g., "post_to_facebook")
            arguments (dict): Tool arguments
            original_file_path (Path): Path to the original action file

        Returns:
            dict: Action result or None if failed
        """
        try:
            # Instantiate the skill
            skill = SocialMediaSkill()

            # Get the method
            method = getattr(skill, action, None)

            if method is None:
                self.logger.error(f"Action '{action}' not found in SocialMediaSkill")
                return None

            # Call the method with arguments - Smart async detection with safety net
            result = None
            try:
                if inspect.iscoroutinefunction(method):
                    # Async method - use asyncio.run()
                    result = asyncio.run(method(**arguments))
                else:
                    # Synchronous method - call directly
                    result = method(**arguments)
            except Exception as exec_error:
                self.logger.error(
                    f"Execution Failed for {action}: {exec_error}",
                    exc_info=True
                )
                return None

            return result

        except Exception as e:
            self.logger.error(f"Error executing Social Media action '{action}': {e}", exc_info=True)
            return None

    def process_approved_file(self, file_path):
        """
        Process a file in the Approved directory.

        Args:
            file_path (Path): Path to the approved file
        """
        # Safely log the file path to handle Unicode characters
        safe_file_path = str(file_path).encode('ascii', 'replace').decode('ascii')
        self.logger.info(f"Processing approved file: {safe_file_path}")

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