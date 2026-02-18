"""
LinkedIn Skill - Silver Tier Agent Skill for LinkedIn posting automation.

This skill wraps the LinkedIn poster functionality into a formal Agent Skill
that follows the hackathon architecture. It uses Selenium to automate
LinkedIn posting while maintaining Human-in-the-Loop (HITL) oversight.

Tier: Silver (Core automation skill)
"""

import os
import re
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


class LinkedInSkill:
    """
    Agent Skill for LinkedIn posting automation.
    
    This skill provides the execute() method that follows the standard
    Agent Skill interface, plus helper methods for LinkedIn operations.
    
    Human-in-the-Loop: The skill opens the browser and populates content,
    but does NOT click the final "Post" button - requiring human review.
    """

    def __init__(self, chrome_data_dir: Optional[str] = None):
        """
        Initialize the LinkedIn Skill.
        
        Args:
            chrome_data_dir: Path to Chrome user data directory for persistent sessions
        """
        self.driver = None
        self.wait = None
        self.chrome_data_dir = chrome_data_dir
        self.logger = logging.getLogger(__name__)
        
        # Default to project's chrome_data directory
        if not self.chrome_data_dir:
            self.chrome_data_dir = os.path.join(os.getcwd(), "chrome_data")

    def clean_markdown(self, text: str) -> str:
        """
        Remove markdown artifacts from text to make it appear human-written.
        
        Args:
            text: The text to clean
            
        Returns:
            Cleaned text without markdown formatting
        """
        # Remove bold: **text** -> text
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Remove italics: *text* -> text
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove headers/lines
        text = text.replace('---', '').replace('###', '')
        
        # Remove horizontal rules
        text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
        
        # Remove headers ### Header -> Header
        text = re.sub(r'^\s*#+\s*(.*)', r'\1', text, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text

    def setup_browser(self) -> webdriver.Chrome:
        """
        Set up the Chrome browser with a temporary profile.
        
        Returns:
            Configured Chrome WebDriver instance
        """
        self.logger.info("🚀 Launching Chrome with persistent profile...")
        options = webdriver.ChromeOptions()
        
        # Add persistent user data directory to save login sessions
        options.add_argument(f"--user-data-dir={self.chrome_data_dir}")
        
        # Add stability arguments
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

    def navigate_to_linkedin(self) -> bool:
        """
        Navigate to LinkedIn feed.
        
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to LinkedIn: {e}")
            return False

    def check_login_status(self) -> bool:
        """
        Check if the user is logged in to LinkedIn.
        
        Returns:
            True if user appears to be logged in, False otherwise
        """
        try:
            start_post_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//button[contains(@class, 'share-box-feed-entry__trigger') or contains(@data-test-id, 'share-box-feed-entry-trigger')]"
                ))
            )
            return start_post_button is not None
        except Exception:
            return False

    def find_and_click_start_post(self) -> bool:
        """
        Find and click the "Start a post" button.
        
        Returns:
            True if button was found and clicked, False otherwise
        """
        try:
            wait = WebDriverWait(self.driver, 120)
            
            # Aggressive selectors for the "Start a post" button
            selectors = [
                "//*[text()='Start a post']",
                "//span[contains(text(), 'Start a post')]",
                "//button[contains(@aria-label, 'Start a post')]"
            ]
            
            start_post_button = None
            for selector in selectors:
                try:
                    elements = self.driver.execute_script(
                        f"return document.evaluate(`{selector}`, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);"
                    )
                    if elements.snapshotLength > 0:
                        start_post_button = elements.snapshotItem(0)
                        break
                except Exception:
                    try:
                        start_post_button = wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except Exception:
                        continue
            
            if start_post_button is None:
                raise Exception("Could not find 'Start a post' button")
            
            # Use JavaScript to click
            self.driver.execute_script("arguments[0].click();", start_post_button)
            return True
            
        except Exception as e:
            self.logger.error(f"Error finding or clicking 'Start a post' button: {e}")
            return False

    def populate_post_content(self, content: str) -> bool:
        """
        Populate the post content in the LinkedIn text editor.
        
        Args:
            content: The content to be posted on LinkedIn
            
        Returns:
            True if content was populated successfully, False otherwise
        """
        try:
            # Clean the content first
            cleaned_content = self.clean_markdown(content)
            
            # Selectors for the text editor
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
                    if selector.startswith("//"):
                        editor = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        editor = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    break
                except Exception:
                    continue
            
            if editor is None:
                self.logger.error("Could not find the text editor")
                return False
            
            # Clear and paste content using clipboard
            import pyperclip
            from selenium.webdriver.common.keys import Keys
            
            editor.click()
            editor.clear()
            
            # Copy to clipboard and paste
            pyperclip.copy(cleaned_content)
            time.sleep(0.5)
            editor.send_keys(Keys.CONTROL, 'v')
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error populating post content: {e}")
            return False

    def execute(self, content: str, wait_for_login_timeout: int = 120) -> Dict[str, Any]:
        """
        Execute the LinkedIn posting skill.
        
        This is the main entry point that follows the Agent Skill interface.
        
        Args:
            content: The LinkedIn post content
            wait_for_login_timeout: Seconds to wait for user login (default: 120)
            
        Returns:
            Dictionary with execution result:
            {
                "success": bool,
                "message": str,
                "skill_name": "LinkedInSkill",
                "tier": "Silver",
                "hitl_required": bool,
                "automation_result": dict
            }
        """
        try:
            # Clean content at the beginning
            content = self.clean_markdown(content)
            
            # Set up browser
            driver = self.setup_browser()
            
            # Navigate to LinkedIn
            if not self.navigate_to_linkedin():
                return {
                    "success": False,
                    "message": "Failed to navigate to LinkedIn",
                    "skill_name": "LinkedInSkill",
                    "tier": "Silver",
                    "hitl_required": True,
                    "automation_result": {
                        "browser_opened": True,
                        "content_populated": False,
                        "error_details": "Navigation failed"
                    }
                }
            
            # Wait for user login with responsive feedback
            login_check_interval = 1
            elapsed_time = 0
            
            while elapsed_time < wait_for_login_timeout:
                if "linkedin.com/feed" in self.driver.current_url:
                    self.logger.info("[SUCCESS] Login detected via URL!")
                    break
                
                if self.check_login_status():
                    break
                else:
                    if elapsed_time % 15 == 0:
                        self.logger.warning("[WARNING] Please log in to LinkedIn in the browser.")
                        print("[WARNING] Please log in to LinkedIn in the browser.")
                    
                    time.sleep(login_check_interval)
                    elapsed_time += login_check_interval
            
            # Find and click "Start a post"
            if not self.find_and_click_start_post():
                return {
                    "success": False,
                    "message": "Could not find or click 'Start a post' button",
                    "skill_name": "LinkedInSkill",
                    "tier": "Silver",
                    "hitl_required": True,
                    "automation_result": {
                        "browser_opened": True,
                        "content_populated": False,
                        "error_details": "Start post button not found"
                    }
                }
            
            # Populate content
            if not self.populate_post_content(content):
                return {
                    "success": False,
                    "message": "Could not populate post content",
                    "skill_name": "LinkedInSkill",
                    "tier": "Silver",
                    "hitl_required": True,
                    "automation_result": {
                        "browser_opened": True,
                        "content_populated": False,
                        "error_details": "Content population failed"
                    }
                }
            
            # HITL: Do NOT click final "Post" button
            return {
                "success": True,
                "message": "LinkedIn post content populated. Please review and click 'Post' manually.",
                "skill_name": "LinkedInSkill",
                "tier": "Silver",
                "hitl_required": True,
                "automation_result": {
                    "browser_opened": True,
                    "content_populated": True,
                    "post_ready_for_review": True,
                    "human_action_required": "Click the 'Post' button to publish"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error during LinkedIn posting: {e}")
            return {
                "success": False,
                "message": str(e),
                "skill_name": "LinkedInSkill",
                "tier": "Silver",
                "hitl_required": True,
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
            self.logger.info("Browser closed.")


# Convenience function for direct skill invocation
def post_linkedin_update(content: str) -> Dict[str, Any]:
    """
    Post an update to LinkedIn.
    
    Args:
        content: The post content
        
    Returns:
        Execution result dictionary
    """
    skill = LinkedInSkill()
    try:
        result = skill.execute(content)
        return result
    finally:
        skill.close_browser()


# Skill metadata for registry
SKILL_METADATA = {
    "name": "LinkedInSkill",
    "version": "1.0.0",
    "tier": "Silver",
    "description": "Automates LinkedIn posting using Selenium with HITL oversight",
    "hitl_required": True,
    "functions": ["execute", "post_linkedin_update"],
    "inputs": {
        "content": "str - The LinkedIn post content"
    },
    "outputs": {
        "success": "bool - Whether the operation succeeded",
        "message": "str - Result message",
        "automation_result": "dict - Detailed automation status"
    }
}


if __name__ == "__main__":
    # Test the skill
    print("Testing LinkedIn Skill...")
    print("-" * 50)
    
    test_content = """
🚀 Excited to share our latest AI automation breakthrough!

Our new Agent Skills architecture enables:
✅ Local-first AI operations
✅ Human-in-the-Loop oversight
✅ Seamless integration with business tools

#AI #Automation #Innovation #Hackathon2026
"""
    
    result = post_linkedin_update(test_content)
    print(f"Result: {result}")
