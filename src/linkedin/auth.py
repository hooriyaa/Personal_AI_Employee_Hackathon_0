"""
LinkedIn Authentication Module - Manages LinkedIn login session using cookies.

This script launches a browser (headed) and waits for the user to log in manually
to LinkedIn, then saves the session/cookies to a secure location.
"""

import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the secrets directory
SECRETS_DIR = Path("src/secrets")
SESSION_FILE = SECRETS_DIR / "linkedin_session.json"


def save_session_to_file(context, session_file_path):
    """
    Save the browser context's cookies and storage state to a file.
    
    Args:
        context: Playwright browser context
        session_file_path: Path to save the session data
    """
    session_data = {
        'cookies': context.cookies(),
        'storage_state': context.storage_state()
    }
    
    # Ensure the secrets directory exists
    session_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write session data to file
    with open(session_file_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    
    logger.info(f"Session saved to {session_file_path}")


def load_session_from_file(session_file_path):
    """
    Load session data from a file.
    
    Args:
        session_file_path: Path to the session data file
        
    Returns:
        Session data dictionary or None if file doesn't exist
    """
    if not session_file_path.exists():
        return None
    
    with open(session_file_path, 'r') as f:
        return json.load(f)


def authenticate_linkedin_manually():
    """
    Launches a headed browser and waits for the user to log in to LinkedIn manually.
    Saves the session once logged in.
    """
    logger.info("Launching browser for LinkedIn authentication...")
    logger.info("Please log in to LinkedIn manually in the browser that opens.")
    logger.info("After logging in, close the browser to save the session.")
    
    with sync_playwright() as p:
        # Launch a headed browser (visible)
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to LinkedIn
        page.goto("https://www.linkedin.com")
        
        # Wait for the user to manually log in
        # We'll detect login by checking if the page URL changes to the feed or profile
        logger.info("Waiting for manual login... Please log in to LinkedIn.")
        
        # Wait for navigation to home/feed (indicating successful login)
        try:
            page.wait_for_url("**/feed/**", timeout=300000)  # 5 minutes timeout
            logger.info("Detected successful login to LinkedIn feed.")
        except:
            # If feed URL doesn't match, check for profile URL
            try:
                page.wait_for_url("**/in/**", timeout=30000)
                logger.info("Detected successful login to LinkedIn profile.")
            except:
                logger.info("Still waiting for login... Please continue with manual login.")
                # Wait for user to close the browser or navigate to feed/profile
                try:
                    page.wait_for_timeout(300000)  # Additional wait time
                except:
                    pass
        
        # Save session when user closes the browser or after successful login detection
        save_session_to_file(context, SESSION_FILE)
        
        # Close the browser
        browser.close()
        
        logger.info("LinkedIn session saved successfully!")


def test_authentication():
    """
    Test function to verify if we can load the session and access LinkedIn with it.
    """
    session_data = load_session_from_file(SESSION_FILE)
    
    if not session_data:
        logger.error(f"No session file found at {SESSION_FILE}")
        return False
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=session_data['storage_state'])
        
        # Add cookies to the context
        context.add_cookies(session_data['cookies'])
        
        page = context.new_page()
        page.goto("https://www.linkedin.com/feed/")
        
        # Wait a bit to see if we're logged in
        page.wait_for_timeout(5000)
        
        # Check if we're on the feed page (logged in)
        current_url = page.url
        if "feed" in current_url or "in/" in current_url:
            logger.info("Successfully accessed LinkedIn with saved session!")
            browser.close()
            return True
        else:
            logger.error("Failed to access LinkedIn with saved session.")
            browser.close()
            return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_authentication()
    else:
        authenticate_linkedin_manually()