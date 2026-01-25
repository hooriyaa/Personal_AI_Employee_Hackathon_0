"""
Authentication module for Gmail API OAuth 2.0 flow.

This module handles the authentication process with Gmail API using OAuth 2.0.
It manages credential loading, token refresh, and authentication validation.
"""

import os
import pickle
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from src.config.settings import CREDENTIALS_FILE, TOKEN_FILE


class GmailAuthenticator:
    """Handles Gmail API authentication using OAuth 2.0."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.modify',  # Read/write access to emails
        'https://www.googleapis.com/auth/gmail.settings.basic'  # Access to settings
    ]

    def __init__(self):
        """Initialize the authenticator."""
        self.service = None
        self.credentials = None

    def authenticate(self):
        """
        Authenticate with Gmail API using stored credentials or OAuth flow.
        
        Returns:
            googleapiclient.discovery.Resource: Gmail API service object
        """
        # Load existing token if available
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'rb') as token:
                self.credentials = pickle.load(token)

        # Refresh credentials if they are expired or invalid
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
            self._save_credentials()

        # If there are no valid credentials, initiate the OAuth flow
        if not self.credentials or not self.credentials.valid:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Credentials file not found at {CREDENTIALS_FILE}. "
                    f"Please follow the setup instructions to create this file."
                )
            
            # Run the OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, self.SCOPES
            )
            self.credentials = flow.run_local_server(port=0)
            
            # Save the credentials for next run
            self._save_credentials()

        # Build and return the Gmail API service
        self.service = build('gmail', 'v1', credentials=self.credentials)
        return self.service

    def _save_credentials(self):
        """Save the current credentials to the token file."""
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(self.credentials, token)

    def validate_credentials(self):
        """
        Validate if the current credentials are still valid.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        if not self.credentials:
            return False
        
        # Check if credentials exist and are not expired
        if not TOKEN_FILE.exists():
            return False
            
        # Check if token is expired
        if self.credentials.expired and not self.credentials.refresh_token:
            return False
            
        return True

    def get_user_info(self):
        """
        Get basic user info from Gmail API.
        
        Returns:
            dict: User profile information
        """
        if not self.service:
            self.authenticate()
        
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile
        except Exception as e:
            print(f"Error retrieving user info: {e}")
            return None

    def check_api_access(self):
        """
        Check if the API access is working properly.
        
        Returns:
            bool: True if API access is working, False otherwise
        """
        try:
            if not self.service:
                self.authenticate()
                
            # Try to fetch a minimal amount of data to verify access
            result = self.service.users().labels().list(userId='me').execute()
            return 'labels' in result
        except Exception as e:
            print(f"API access check failed: {e}")
            return False


def get_gmail_service():
    """
    Convenience function to get authenticated Gmail service.
    
    Returns:
        googleapiclient.discovery.Resource: Gmail API service object
    """
    authenticator = GmailAuthenticator()
    return authenticator.authenticate()


if __name__ == "__main__":
    # Test the authentication
    try:
        service = get_gmail_service()
        print("Authentication successful!")
        
        # Get user info to verify access
        authenticator = GmailAuthenticator()
        user_info = authenticator.get_user_info()
        if user_info:
            print(f"Logged in as: {user_info.get('emailAddress', 'Unknown')}")
        
        # Check API access
        if authenticator.check_api_access():
            print("API access verified!")
        else:
            print("API access check failed!")
    except Exception as e:
        print(f"Authentication failed: {e}")