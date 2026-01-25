"""
Email processing module to convert Gmail messages to Markdown format.

This module handles the conversion of Gmail messages to Markdown files,
including extracting headers, body content, and formatting appropriately.
"""

import base64
import html
import re
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from pathlib import Path
import logging
from datetime import datetime


def decode_email_body(encoded_body):
    """
    Decode the email body from base64 encoding.
    
    Args:
        encoded_body (str): Base64 encoded email body
        
    Returns:
        str: Decoded email body
    """
    if not encoded_body:
        return ""
    
    # Remove any padding issues
    missing_padding = len(encoded_body) % 4
    if missing_padding:
        encoded_body += '=' * (4 - missing_padding)
    
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_body)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        logging.error(f"Error decoding email body: {e}")
        return ""


def html_to_markdown(html_content):
    """
    Convert HTML content to Markdown format.
    
    Args:
        html_content (str): HTML content to convert
        
    Returns:
        str: Converted Markdown content
    """
    if not html_content:
        return ""
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Convert common HTML elements to Markdown equivalents
    # Headers
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(header.name[1])
        header.string = f"\n{'#' * level} {header.get_text()}\n"
    
    # Bold
    for bold in soup.find_all(['b', 'strong']):
        bold.string = f"**{bold.get_text()}**"
    
    # Italic
    for italic in soup.find_all(['i', 'em']):
        italic.string = f"*{italic.get_text()}*"
    
    # Links
    for link in soup.find_all('a'):
        link.string = f"[{link.get_text()}]({link.get('href', '')})"
    
    # Lists
    for li in soup.find_all('li'):
        li.string = f"- {li.get_text()}\n"
    
    # Line breaks
    for br in soup.find_all('br'):
        br.replace_with("\n")
    
    # Paragraphs
    for p in soup.find_all('p'):
        p.insert_after("\n\n")
        p.unwrap()
    
    # Get text and clean up
    text = soup.get_text()
    
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove extra newlines
    text = text.strip()
    
    return text


def extract_email_parts(message):
    """
    Extract different parts of an email message (text, HTML, attachments).
    
    Args:
        message (dict): Gmail API message object
        
    Returns:
        tuple: (text_body, html_body, attachments)
    """
    text_body = ""
    html_body = ""
    attachments = []
    
    payload = message.get('payload', {})
    parts = payload.get('parts', [])
    
    # If there are no parts, try the body directly
    if not parts:
        body = payload.get('body', {}).get('data', '')
        if body:
            text_body = decode_email_body(body)
        return text_body, html_body, attachments
    
    # Process each part
    for part in parts:
        mime_type = part.get('mimeType', '')
        body_data = part.get('body', {}).get('data', '')
        
        if mime_type == 'text/plain':
            text_body = decode_email_body(body_data)
        elif mime_type == 'text/html':
            html_body = decode_email_body(body_data)
        elif mime_type.startswith('multipart/'):
            # Handle nested multipart messages
            nested_parts = part.get('parts', [])
            for nested_part in nested_parts:
                nested_mime_type = nested_part.get('mimeType', '')
                nested_body_data = nested_part.get('body', {}).get('data', '')
                
                if nested_mime_type == 'text/plain':
                    text_body = decode_email_body(nested_body_data)
                elif nested_mime_type == 'text/html':
                    html_body = decode_email_body(nested_body_data)
        else:
            # This is likely an attachment
            filename = part.get('filename', '')
            if filename:
                attachments.append({
                    'filename': filename,
                    'attachment_id': part.get('body', {}).get('attachmentId', ''),
                    'mime_type': mime_type
                })
    
    return text_body, html_body, attachments


def create_markdown_from_email(email_data):
    """
    Create a Markdown representation of an email.
    
    Args:
        email_data (dict): Email data with all required fields
        
    Returns:
        str: Markdown formatted email content
    """
    subject = email_data.get('subject', 'No Subject')
    sender = email_data.get('sender', 'Unknown Sender')
    recipients = email_data.get('recipients', [])
    cc = email_data.get('cc', [])
    bcc = email_data.get('bcc', [])
    date = email_data.get('date', '')
    labels = email_data.get('labels', [])
    body = email_data.get('body', '')
    
    markdown_content = f"""# {subject}

**From:** {sender}
**To:** {', '.join(recipients)}
**CC:** {', '.join(cc) if cc else 'None'}
**BCC:** {', '.join(bcc) if bcc else 'None'}
**Date:** {date}
**Labels:** {', '.join(labels)}

---

{body}
"""
    return markdown_content


def process_gmail_message(message, service):
    """
    Process a Gmail message and convert it to Markdown format.
    
    Args:
        message (dict): Gmail API message object
        service: Gmail API service object
        
    Returns:
        dict: Processed email data ready for Markdown conversion
    """
    # Get message headers
    headers = {}
    for header in message.get('payload', {}).get('headers', []):
        name = header.get('name', '').lower()
        value = header.get('value', '')
        headers[name] = value
    
    # Extract email components
    subject = headers.get('subject', 'No Subject')
    sender = headers.get('from', 'Unknown Sender')
    to = headers.get('to', '')
    cc = headers.get('cc', '')
    date = headers.get('date', '')
    
    # Get message body
    text_body, html_body, attachments = extract_email_parts(message)
    
    # Prefer HTML body if available and text body is empty
    if html_body and not text_body:
        body = html_to_markdown(html_body)
    else:
        body = text_body
    
    # Get message labels
    message_labels = message.get('labelIds', [])
    
    # Format recipients
    recipients = [r.strip() for r in to.split(',')] if to else []
    cc_recipients = [r.strip() for r in cc.split(',')] if cc else []
    
    # Create email data dictionary
    email_data = {
        'id': message['id'],
        'thread_id': message['threadId'],
        'subject': subject,
        'sender': sender,
        'recipients': recipients,
        'cc': cc_recipients,
        'date': date,
        'labels': message_labels,
        'body': body,
        'size': message.get('sizeEstimate', 0),
        'snippet': message.get('snippet', ''),
        'internal_date': message.get('internalDate', ''),
        'raw_body': text_body if text_body else html_body
    }
    
    return email_data


def save_email_as_markdown(email_data, output_dir):
    """
    Save email data as a Markdown file.
    
    Args:
        email_data (dict): Processed email data
        output_dir (str or Path): Directory to save the Markdown file
        
    Returns:
        Path: Path to the saved Markdown file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create a safe filename from the subject
    subject = email_data['subject']
    safe_subject = re.sub(r'[^\w\s-]', '_', subject[:50]).strip()
    safe_subject = re.sub(r'[-\s]+', '-', safe_subject)

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{safe_subject}.md"

    file_path = output_path / filename
    
    # Create markdown content
    markdown_content = create_markdown_from_email(email_data)
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    logging.info(f"Saved email as Markdown: {file_path}")
    return file_path


def convert_gmail_to_markdown(message, service, output_dir):
    """
    Complete workflow to convert a Gmail message to a Markdown file.
    
    Args:
        message (dict): Gmail API message object
        service: Gmail API service object
        output_dir (str or Path): Directory to save the Markdown file
        
    Returns:
        Path: Path to the saved Markdown file, or None if failed
    """
    try:
        # Process the email message
        email_data = process_gmail_message(message, service)
        
        # Save as markdown
        file_path = save_email_as_markdown(email_data, output_dir)
        
        return file_path
    except Exception as e:
        logging.error(f"Error converting email to markdown: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # This would be used within the context of a Gmail API service
    print("Email processor module loaded successfully.")
    print("Use convert_gmail_to_markdown() function to convert emails to Markdown.")