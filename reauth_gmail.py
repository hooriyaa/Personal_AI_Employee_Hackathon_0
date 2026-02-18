"""
Re-authenticate with Gmail API - deletes old token and creates new one.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment to allow insecure storage temporarily
os.environ['ALLOW_INSECURE_STORAGE'] = 'true'

from src.config.settings import TOKEN_FILE, CREDENTIALS_FILE
from src.gmail.auth import get_gmail_service, GmailAuthenticator

def main():
    print("=" * 60)
    print("Gmail API Re-authentication")
    print("=" * 60)
    
    # Check credentials file
    if not CREDENTIALS_FILE.exists():
        print(f"\n[ERROR] credentials.json not found at: {CREDENTIALS_FILE}")
        print("Please download credentials.json from Google Cloud Console")
        return
    
    print(f"\n[OK] Found credentials.json")
    
    # Check if old token exists and delete it
    if TOKEN_FILE.exists():
        print(f"[INFO] Removing old token: {TOKEN_FILE}")
        TOKEN_FILE.unlink()
        print("[OK] Old token deleted")
    else:
        print("[INFO] No existing token found (will create new one)")
    
    print("\n[INFO] Starting Gmail OAuth flow...")
    print("A browser window will open. Please:")
    print("  1. Select your Google account")
    print("  2. Grant Gmail API permissions")
    print("  3. Complete the authorization")
    print("\nStarting in 2 seconds...")
    
    import time
    time.sleep(2)
    
    try:
        service = get_gmail_service()
        print("\n[OK] Authentication successful!")
        
        # Verify by getting user info
        authenticator = GmailAuthenticator()
        user_info = authenticator.get_user_info()
        if user_info:
            email = user_info.get('emailAddress', 'Unknown')
            print(f"Logged in as: {email}")
        
        # Check API access
        if authenticator.check_api_access():
            print("[OK] API access verified!")
            print("\n" + "=" * 60)
            print("Gmail API is ready to use!")
            print("=" * 60)
        else:
            print("[WARN] API access check failed - please try again")
            
    except Exception as e:
        print(f"\n[ERROR] Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure credentials.json exists in secrets/")
        print("  2. Check that Gmail API is enabled in Google Cloud Console")
        print("  3. Make sure your browser allows pop-ups for localhost")

if __name__ == "__main__":
    main()
