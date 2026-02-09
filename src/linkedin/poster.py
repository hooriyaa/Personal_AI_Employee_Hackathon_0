"""
LinkedIn Poster Module - Automates LinkedIn posting using Selenium WebDriver.

This module provides functionality to open Chrome browser using the user's
existing profile, navigate to LinkedIn, and populate a post with content
while maintaining human oversight by not clicking the final "Post" button.
"""

import os
import re
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


class LinkedInPoster:
    """Class to handle LinkedIn posting automation using Selenium."""
    
    def __init__(self):
        """Initialize the LinkedInPoster."""
        self.driver = None
        self.logger = logging.getLogger(__name__)

    def clean_text(self, text):
        """
        Remove markdown artifacts from text to make it appear more human-written.

        Args:
            text (str): The text to clean

        Returns:
            str: Cleaned text without markdown formatting
        """
        # Remove bold: **text** -> text
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Remove italics: *text* -> text
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove headers/lines: replace --- and ### with empty strings
        text = text.replace('---', '').replace('###', '')
        
        # Clean up extra whitespace that might result from removals
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Replace multiple blank lines with single blank line
        text = text.strip()  # Remove leading/trailing whitespace

        return text

    def clean_markdown(self, text):
        """
        Remove markdown artifacts from text to make it appear more human-written.

        Args:
            text (str): The text to clean

        Returns:
            str: Cleaned text without markdown formatting
        """
        # Remove bold syntax **word** -> word
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)

        # Remove italic syntax *word* -> word
        text = re.sub(r'\*(.*?)\*', r'\1', text)

        # Remove horizontal rules ---
        text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

        # Remove headers ### Header -> Header
        text = re.sub(r'^\s*#+\s*(.*)', r'\1', text, flags=re.MULTILINE)

        # Clean up extra whitespace that might result from removals
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Replace multiple blank lines with single blank line
        text = text.strip()  # Remove leading/trailing whitespace

        return text
        
    def setup_browser(self):
        """
        Set up the Chrome browser with a temporary profile.

        Returns:
            WebDriver: Configured Chrome WebDriver instance
        """
        print("🚀 Launching Chrome with persistent profile...")
        import os
        options = webdriver.ChromeOptions()

        # Add persistent user data directory to save login sessions
        user_data_dir = os.path.join(os.getcwd(), "chrome_data")
        options.add_argument(f"--user-data-dir={user_data_dir}")

        # Add stability arguments to prevent "DevToolsActivePort" errors:
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")

        options.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.wait = WebDriverWait(self.driver, 120)
        return self.driver
    
    def navigate_to_linkedin(self):
        """
        Navigate to LinkedIn feed.
        
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to LinkedIn: {e}")
            return False
    
    def check_login_status(self):
        """
        Check if the user is logged in to LinkedIn.

        Returns:
            bool: True if user appears to be logged in, False otherwise
        """
        try:
            # Wait for the page to load and check for elements that indicate login status
            # Look for the "Start a post" button which is present when logged in
            # Use a shorter timeout since we're checking periodically in the main method
            start_post_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'share-box-feed-entry__trigger') or contains(@data-test-id, 'share-box-feed-entry-trigger')]"))
            )
            return start_post_button is not None
        except:
            # If we can't find the start post button, the user might not be logged in
            return False
    
    def find_and_click_start_post(self):
        """
        Find and click the "Start a post" button.

        Returns:
            bool: True if button was found and clicked, False otherwise
        """
        try:
            # Increased timeout to 120 seconds to give user enough time to log in manually
            wait = WebDriverWait(self.driver, 120)

            # Aggressive selectors for the "Start a post" button with priority order
            selectors = [
                "//*[text()='Start a post']",
                "//span[contains(text(), 'Start a post')]",
                "//button[contains(@aria-label, 'Start a post')]"
            ]

            start_post_button = None
            for selector in selectors:
                try:
                    # Use JavaScript to find the element immediately, reducing wait time
                    elements = self.driver.execute_script(
                        f"return document.evaluate(`{selector}`, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);"
                    )
                    if elements.snapshotLength > 0:
                        start_post_button = elements.snapshotItem(0)
                        break
                except:
                    # If JavaScript evaluation fails, fall back to Selenium
                    try:
                        start_post_button = wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except:
                        continue

            if start_post_button is None:
                raise Exception("Could not find 'Start a post' button with any of the selectors")

            # Use JavaScript to click the button immediately once found
            self.driver.execute_script("arguments[0].click();", start_post_button)
            return True
        except Exception as e:
            self.logger.error(f"Error finding or clicking 'Start a post' button: {e}")
            return False
    
    def populate_post_content(self, content):
        """
        Populate the post content in the text editor.

        Args:
            content (str): The content to be posted on LinkedIn

        Returns:
            bool: True if content was populated successfully, False otherwise
        """
        try:
            # Clean the content to remove AI formatting before copying to clipboard
            cleaned_content = self.clean_markdown(content)

            # Wait for the text editor to be available with faster detection
            # Use a faster, more direct XPATH to find the editor
            editor_selectors = [
                "//div[contains(@class, 'ql-editor')]",
                "//div[@role='textbox']",
                "div[contenteditable='true'][data-test-id='artdeco-text-input-content-editable']",
                "div[data-test-id='share-content-textarea']",
                "div[aria-label='Share your insight']",
                "div[aria-label='Create a post']"
            ]

            editor = None
            for selector in editor_selectors:
                try:
                    # Use shorter timeout for faster failure
                    if selector.startswith("//"):
                        editor = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        editor = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    break
                except:
                    continue

            if editor is None:
                self.logger.error("Could not find the text editor on the LinkedIn post modal")
                return False

            # Clear the editor and add the content using clipboard to handle emojis
            import pyperclip
            from selenium.webdriver.common.keys import Keys

            editor.clear()

            # Find editor (ql-editor) and click it
            editor.click()

            # Copy cleaned content to clipboard
            pyperclip.copy(cleaned_content)

            # Wait 0.5 seconds for focus and clipboard to be ready (reduced from 3s)
            time.sleep(0.5)

            # Paste content (Ctrl+V)
            editor.send_keys(Keys.CONTROL, 'v')

            return True
        except Exception as e:
            self.logger.error(f"Error populating post content: {e}")
            return False
    
    def post_to_linkedin(self, content):
        """
        Main method to post content to LinkedIn.

        Args:
            content (str): The content to be posted on LinkedIn

        Returns:
            dict: Result of the automation with success status and details
        """
        try:
            # CRITICAL: Clean the content at the very beginning
            content = self.clean_text(content)

            # Set up the browser
            driver = self.setup_browser()

            # Navigate to LinkedIn
            if not self.navigate_to_linkedin():
                return {
                    "success": False,
                    "error": "Failed to navigate to LinkedIn",
                    "automation_result": {
                        "browser_opened": True,
                        "content_populated": False,
                        "error_details": "Navigation to LinkedIn failed"
                    }
                }
            
            # Check if user is logged in with more responsive feedback
            import time
            login_check_interval = 1  # seconds between checks (reduced from 5s for faster response)
            elapsed_time = 0
            max_wait_time = 120  # total time to wait

            while elapsed_time < max_wait_time:
                # Check if user is logged in via URL first (faster detection)
                if "linkedin.com/feed" in self.driver.current_url:
                    self.logger.info("[SUCCESS] Login detected via URL! Starting post...")
                    break

                if self.check_login_status():
                    break
                else:
                    if elapsed_time % 15 == 0:  # Show warning every 15 seconds
                        self.logger.warning("[WARNING] Please log in to LinkedIn in the browser.")
                        print("[WARNING] Please log in to LinkedIn in the browser.")

                    time.sleep(login_check_interval)
                    elapsed_time += login_check_interval
            
            # Find and click the "Start a post" button
            if not self.find_and_click_start_post():
                return {
                    "success": False,
                    "error": "Could not find or click 'Start a post' button",
                    "automation_result": {
                        "browser_opened": True,
                        "content_populated": False,
                        "error_details": "Start post button not found or clickable"
                    }
                }
            
            # Populate the post content
            if not self.populate_post_content(content):
                return {
                    "success": False,
                    "error": "Could not populate post content",
                    "automation_result": {
                        "browser_opened": True,
                        "content_populated": False,
                        "error_details": "Content population failed"
                    }
                }
            
            # Important: Do NOT click the final "Post" button
            # Leave the browser open for user review and manual posting
            return {
                "success": True,
                "message": "LinkedIn post content populated successfully. Please review and click 'Post' manually.",
                "automation_result": {
                    "browser_opened": True,
                    "content_populated": True,
                    "post_ready_for_review": True
                }
            }
        except Exception as e:
            self.logger.error(f"Error during LinkedIn posting automation: {e}")
            return {
                "success": False,
                "error": str(e),
                "automation_result": {
                    "browser_opened": False,
                    "content_populated": False,
                    "error_details": str(e)
                }
            }
    
    def close_browser(self):
        """Close the browser if it's open."""
        if self.driver:
            self.driver.quit()
            self.driver = None