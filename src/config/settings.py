"""
Configuration settings for the Gmail Reasoning Loop application.

This module defines all configurable parameters for the application,
including API settings, file paths, and operational parameters.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Secrets directory - critical for storing sensitive files
SECRETS_DIR = BASE_DIR / "secrets"

# Ensure the secrets directory exists
SECRETS_DIR.mkdir(exist_ok=True)

# Credential file paths - these must be secured and never committed
CREDENTIALS_FILE = SECRETS_DIR / "credentials.json"
TOKEN_FILE = SECRETS_DIR / "token.json"

# Directory configuration
VAULT_PATH = os.getenv("VAULT_PATH", str(BASE_DIR))
INBOX_DIR = Path(os.getenv("INBOX_DIR", VAULT_PATH)) / "Inbox"
NEEDS_ACTION_DIR = Path(os.getenv("NEEDS_ACTION_DIR", VAULT_PATH)) / "Needs_Action"
PLANS_DIR = Path(os.getenv("PLANS_DIR", VAULT_PATH)) / "Plans"
PENDING_APPROVAL_DIR = Path(os.getenv("PENDING_APPROVAL_DIR", VAULT_PATH)) / "Pending_Approval"
APPROVED_DIR = Path(os.getenv("APPROVED_DIR", VAULT_PATH)) / "Approved"
DONE_DIR = Path(os.getenv("DONE_DIR", VAULT_PATH)) / "Done"
LOGS_DIR = Path(os.getenv("LOGS_DIR", VAULT_PATH)) / "Logs"

# Create required directories if they don't exist
REQUIRED_DIRS = [
    INBOX_DIR,
    NEEDS_ACTION_DIR,
    PLANS_DIR,
    PENDING_APPROVAL_DIR,
    APPROVED_DIR,
    DONE_DIR,
    LOGS_DIR
]

for directory in REQUIRED_DIRS:
    directory.mkdir(parents=True, exist_ok=True)

# Gmail API configuration
GMAIL_POLL_INTERVAL = int(os.getenv("GMAIL_POLL_INTERVAL", "60"))  # seconds
MAX_POLL_INTERVAL = 120  # seconds (maximum allowed by requirements)
MIN_POLL_INTERVAL = 30   # seconds (minimum to avoid rate limits)

# Labels to watch for in Gmail
WATCHED_LABELS = os.getenv("WATCHED_LABELS", "URGENT,IMPORTANT").split(",")

# Email processing settings
MARK_EMAIL_AS_READ_AFTER_PROCESSING = os.getenv("MARK_EMAIL_AS_READ", "true").lower() == "true"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# Security settings
ALLOW_INSECURE_STORAGE = os.getenv("ALLOW_INSECURE_STORAGE", "false").lower() == "true"  # Should always be false in production

def validate_credentials_exist():
    """
    Validates that the required credential files exist in the secrets directory.
    
    Returns:
        bool: True if credentials exist, False otherwise
    """
    return CREDENTIALS_FILE.exists() and TOKEN_FILE.exists()

def get_credentials_info():
    """
    Gets information about credential status for debugging purposes.
    
    Returns:
        dict: Dictionary containing credential status information
    """
    return {
        "credentials_file_exists": CREDENTIALS_FILE.exists(),
        "token_file_exists": TOKEN_FILE.exists(),
        "secrets_dir_exists": SECRETS_DIR.exists(),
        "credentials_path": str(CREDENTIALS_FILE),
        "token_path": str(TOKEN_FILE),
        "secrets_path": str(SECRETS_DIR)
    }

# Validate that credential files exist at startup if not in development
if not ALLOW_INSECURE_STORAGE:
    if not validate_credentials_exist():
        print(f"WARNING: Credential files not found!")
        print(f"  Expected credentials file: {CREDENTIALS_FILE}")
        print(f"  Expected token file: {TOKEN_FILE}")
        print(f"  Please follow the setup instructions to create these files.")