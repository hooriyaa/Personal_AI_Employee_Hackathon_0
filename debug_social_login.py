"""
Debug Script - Manual Social Media Login Session Setup

This script opens a visible browser window with persistent chrome_data session
to allow manual login to Facebook, Instagram, and Twitter/X.

After logging in, the sessions will be saved in the chrome_data directory
for future automated posting operations.

Usage:
    python debug_social_login.py
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright


def setup_browser(chrome_data_dir: str):
    """
    Set up Chrome browser with persistent user data directory.
    
    Args:
        chrome_data_dir: Path to Chrome user data directory
        
    Returns:
        Playwright browser context
    """
    print(f"\n[INFO] Launching browser with persistent profile: {chrome_data_dir}")
    
    playwright = sync_playwright().start()
    
    # Launch browser with persistent user data
    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=chrome_data_dir,
        headless=False,  # Visible window for manual login
        slow_mo=500,     # Slow down for visibility
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--start-maximized",
            "--disable-blink-features=AutomationControlled"
        ],
        viewport={"width": 1920, "height": 1080}
    )
    
    print("[OK] Browser launched successfully with persistent context")
    return playwright, browser


def navigate_and_wait(browser, page, platform_name: str, url: str, timeout_seconds: int = 120):
    """
    Navigate to a platform and wait for manual login.
    
    Args:
        browser: Browser context
        page: Browser page
        platform_name: Name of the platform
        url: URL to navigate to
        timeout_seconds: Maximum time to wait
    """
    print(f"\n{'='*70}")
    print(f"Platform: {platform_name}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    # Navigate to platform
    print(f"[INFO] Navigating to {platform_name}...")
    page.goto(url, wait_until="networkidle", timeout=60000)
    time.sleep(3)
    
    # Wait for user to login
    print(f"\n[INFO] Please log in to {platform_name} in the browser window.")
    print(f"[INFO] You have {timeout_seconds} seconds to complete the login.")
    print(f"[INFO] The script will wait and then proceed to the next platform...")
    
    start_time = time.time()
    check_interval = 5  # seconds
    
    while time.time() - start_time < timeout_seconds:
        elapsed = int(time.time() - start_time)
        if elapsed % 30 == 0:  # Show reminder every 30 seconds
            remaining = timeout_seconds - elapsed
            print(f"[REMINDER] {remaining} seconds remaining for {platform_name}...")
        time.sleep(check_interval)
    
    print(f"[OK] Time's up for {platform_name}. Proceeding to next platform...")


def main():
    """Main function to open browser for manual login to all platforms."""
    print("="*70)
    print("Social Media Login Session Setup")
    print("="*70)
    print("\nThis script will:")
    print("1. Open a visible browser window with persistent session")
    print("2. Navigate to Facebook, Instagram, and Twitter/X")
    print("3. Wait for you to manually log in to each platform")
    print("4. Save the sessions in chrome_data directory")
    print("\n" + "="*70)
    
    # Get chrome_data directory
    chrome_data_dir = os.path.join(os.getcwd(), "chrome_data")
    print(f"\n[INFO] Chrome data directory: {chrome_data_dir}")
    
    # Create directory if it doesn't exist
    os.makedirs(chrome_data_dir, exist_ok=True)
    print(f"[OK] Chrome data directory ready")
    
    # Setup browser
    playwright, browser = setup_browser(chrome_data_dir)
    
    try:
        # Create a new page
        page = browser.new_page()
        
        # Platform 1: Facebook
        navigate_and_wait(
            browser, page,
            platform_name="Facebook",
            url="https://www.facebook.com",
            timeout_seconds=90
        )
        
        # Small delay between platforms
        time.sleep(2)
        
        # Platform 2: Instagram
        navigate_and_wait(
            browser, page,
            platform_name="Instagram",
            url="https://www.instagram.com",
            timeout_seconds=90
        )
        
        # Small delay between platforms
        time.sleep(2)
        
        # Platform 3: Twitter/X
        navigate_and_wait(
            browser, page,
            platform_name="X (Twitter)",
            url="https://twitter.com",
            timeout_seconds=90
        )
        
        # Final wait
        print(f"\n{'='*70}")
        print("All platforms processed!")
        print(f"{'='*70}")
        print("\n[INFO] Browser will remain open for 30 more seconds.")
        print("[INFO] Use this time to verify all sessions are logged in.")
        time.sleep(30)
        
    except Exception as e:
        print(f"\n[ERROR] Error during login setup: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close browser
        print(f"\n{'='*70}")
        print("Closing browser...")
        print(f"{'='*70}")
        
        try:
            browser.close()
            print("[OK] Browser closed successfully")
        except Exception as e:
            print(f"[WARNING] Error closing browser: {e}")
        
        # Stop playwright
        try:
            playwright.stop()
            print("[OK] Playwright stopped")
        except Exception as e:
            print(f"[WARNING] Error stopping playwright: {e}")
    
    print(f"\n{'='*70}")
    print("Session Setup Complete!")
    print(f"{'='*70}")
    print(f"\n[OK] Sessions saved to: {chrome_data_dir}")
    print("\nNext steps:")
    print("1. Run the social media posting skill to test the sessions")
    print("2. Use post_to_instagram(), post_to_social_platforms(), or generate_social_summary()")
    print("3. Check Briefings/Social_Summary.md for activity summary")
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
