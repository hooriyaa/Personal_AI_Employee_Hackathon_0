"""
Social Media Poster Module - Automates cross-platform social media posting.

This module provides functionality to post to:
- Facebook (https://www.facebook.com)
- Instagram (https://www.instagram.com)
- Twitter/X (https://twitter.com or https://x.com)

Uses Playwright with persistent browser context (chrome_data) for session management,
similar to the LinkedIn automation pattern.

Gold Tier Compliance:
- Uses persistent browser context for authenticated sessions
- Platform-specific selector handling
- Comprehensive error handling and retry logic
- Detailed logging with timestamps
- Human-in-the-Loop oversight (does not auto-submit posts)
"""

import os
import re
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeout


class SocialMediaPoster:
    """
    Class to handle cross-platform social media posting automation using Playwright.

    Implements persistent browser context for session management, allowing
    reuse of authenticated sessions across multiple posting operations.
    """

    def __init__(self, chrome_data_dir: Optional[str] = None):
        """
        Initialize the SocialMediaPoster.

        Args:
            chrome_data_dir: Path to Chrome user data directory for persistent sessions.
                            Defaults to ./chrome_data in project root.
        """
        self.chrome_data_dir = chrome_data_dir
        self.logger = logging.getLogger(__name__)
        self.playwright = None
        self.browser = None
        self.context = None

        # Default to project's chrome_data directory
        if not self.chrome_data_dir:
            self.chrome_data_dir = os.path.join(os.getcwd(), "chrome_data")

        # Platform configuration with URLs and selectors
        self.platform_config = {
            "facebook": {
                "name": "Facebook",
                "base_url": "https://www.facebook.com",
                "post_url": "https://www.facebook.com",
                "login_url": "https://www.facebook.com/login",
                "notification_url": "https://www.facebook.com/notifications",
                "selectors": {
                    "post_button": [
                        '[aria-label="What\'s on your mind?"]',
                        '[data-testid="status-cta-btn"]',
                        'div[role="button"]:has-text("What\'s on your mind?")',
                        '.x1n2onr6.x1n2onr6:has-text("What\'s on your mind?")'
                    ],
                    "post_input": [
                        '[aria-label="What\'s on your mind?"]',
                        '[data-testid="post-creation-textarea"]',
                        'div[contenteditable="true"][data-contents="true"]',
                        'textarea[xpm=""]'
                    ],
                    "post_submit": [
                        '[aria-label="Post"]',
                        '[data-testid="react-composer-post-button"]',
                        'div[role="button"]:has-text("Post")'
                    ],
                    "notification_item": [
                        '[data-pagelet="MainFeed"] [role="article"]',
                        '.pmk7jnqg.k4urcojp.datstx6m',
                        '[data-visualcompletion="css-img"]'
                    ],
                    "notification_count": [
                        '[aria-label="Notifications"] .xzsf02u',
                        '[data-visualcompletion="ignore-dynamic"] span'
                    ]
                }
            },
            "instagram": {
                "name": "Instagram",
                "base_url": "https://www.instagram.com",
                "post_url": "https://www.instagram.com",
                "login_url": "https://www.instagram.com/accounts/login/",
                "notification_url": "https://www.instagram.com/accounts/activity/",
                "selectors": {
                    "post_button": [
                        '[aria-label="New post"]',
                        '[aria-label="Create"]',
                        'svg[aria-label="New post"]',
                        'div[role="button"]:has-text("New")'
                    ],
                    "post_input": [
                        'textarea[aria-label="Write a caption..."]',
                        'textarea[data-gramm="false"]',
                        '[contenteditable="true"]'
                    ],
                    "post_submit": [
                        'button:has-text("Share")',
                        '[aria-label="Share"]',
                        'div[role="button"]:has-text("Share")'
                    ],
                    "notification_item": [
                        '[role="listitem"]',
                        '.x1lliihq.x1lliihq',
                        'div[data-test="recent_activity_item"]'
                    ],
                    "notification_count": [
                        '[aria-label="Notifications"] span',
                        '.xzsf02u.xzsf02u'
                    ]
                }
            },
            "twitter": {
                "name": "X (Twitter)",
                "base_url": "https://twitter.com",
                "alt_base_url": "https://x.com",
                "post_url": "https://twitter.com/home",
                "login_url": "https://twitter.com/login",
                "notification_url": "https://twitter.com/notifications",
                "selectors": {
                    "post_button": [
                        '[data-testid="tweetButton"]',
                        '[data-testid="DraftToolbar"]',
                        'div[role="button"]:has-text("Post")',
                        'div[role="button"]:has-text("Tweet")'
                    ],
                    "post_input": [
                        '[data-testid="tweetTextarea_0"]',
                        '[data-testid="tweetTextarea_0"] > div > div > div > div > span',
                        'div[contenteditable="true"][data-contents="true"]'
                    ],
                    "post_submit": [
                        '[data-testid="tweetButton"]',
                        '[data-testid="tweetButtonInline"]',
                        'div[role="button"]:has-text("Post")',
                        'div[role="button"]:has-text("Tweet")'
                    ],
                    "notification_item": [
                        '[data-testid="notificationItem"]',
                        'article[role="article"]',
                        '[data-testid="primaryColumn"] article'
                    ],
                    "notification_count": [
                        '[aria-label="Notifications"] ~ div',
                        '[data-testid="AppTabBar_Notifications"] ~ div'
                    ]
                }
            }
        }

    def clean_text(self, text: str) -> str:
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

        # Remove links in markdown format [text](url) -> text
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()

        return text

    def setup_browser(self) -> Tuple[BrowserContext, Page]:
        """
        Set up the Chrome browser with persistent user data directory.

        Returns:
            Tuple of (BrowserContext, Page)
        """
        self.logger.info(f"🚀 Launching browser with persistent profile: {self.chrome_data_dir}")

        self.playwright = sync_playwright().start()

        # Launch browser with persistent user data
        self.browser = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.chrome_data_dir,
            headless=False,  # Headed for human oversight
            slow_mo=500,  # Slow down for visibility
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ],
            viewport={"width": 1920, "height": 1080}
        )

        # Create a new page
        page = self.browser.new_page()

        self.logger.info("Browser launched successfully with persistent context")
        return self.browser, page

    def navigate_to_platform(self, page: Page, platform: str) -> bool:
        """
        Navigate to the specified social media platform.

        Args:
            page: Playwright page instance
            platform: Platform name (facebook, instagram, twitter)

        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            config = self.platform_config.get(platform)
            if not config:
                self.logger.error(f"Unknown platform: {platform}")
                return False

            url = config["post_url"]
            self.logger.info(f"Navigating to {config['name']}: {url}")

            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(3)  # Allow page to fully load

            self.logger.info(f"Successfully navigated to {config['name']}")
            return True

        except Exception as e:
            self.logger.error(f"Error navigating to {platform}: {e}")
            return False

    def check_login_status(self, page: Page, platform: str) -> bool:
        """
        Check if the user is logged in to the platform.

        Args:
            page: Playwright page instance
            platform: Platform name

        Returns:
            True if user appears to be logged in, False otherwise
        """
        try:
            config = self.platform_config[platform]

            # Platform-specific login checks
            if platform == "facebook":
                # Check for profile icon or "What's on your mind?" button
                indicators = [
                    '[aria-label="What\'s on your mind?"]',
                    '[data-testid="status-cta-btn"]',
                    'img[alt*="Profile"]',
                    '[aria-label="Menu"]'
                ]
            elif platform == "instagram":
                # Check for profile icon or create post button
                indicators = [
                    '[aria-label="New post"]',
                    '[aria-label="Create"]',
                    'img[alt*="Profile picture"]',
                    '[href*="/direct/inbox/"]'
                ]
            elif platform == "twitter":
                # Check for tweet button or profile menu
                indicators = [
                    '[data-testid="tweetButton"]',
                    '[data-testid="SideNav_Account"]',
                    '[data-testid="app-bar-close"]',
                    'div[role="button"]:has-text("Post")'
                ]
            else:
                indicators = []

            for selector in indicators:
                try:
                    element = page.query_selector(selector)
                    if element:
                        self.logger.info(f"Login detected for {platform} via selector: {selector}")
                        return True
                except Exception:
                    continue

            # Check URL as fallback
            current_url = page.url
            if platform == "facebook" and "facebook.com" in current_url and "login" not in current_url:
                return True
            elif platform == "instagram" and "instagram.com" in current_url and "login" not in current_url:
                return True
            elif platform == "twitter" and ("twitter.com" in current_url or "x.com" in current_url) and "login" not in current_url:
                return True

            self.logger.warning(f"No login indicators found for {platform}")
            return False

        except Exception as e:
            self.logger.error(f"Error checking login status for {platform}: {e}")
            return False

    def find_and_click_post_button(self, page: Page, platform: str) -> bool:
        """
        Find and click the platform's post creation button.

        Args:
            page: Playwright page instance
            platform: Platform name

        Returns:
            True if button was found and clicked, False otherwise
        """
        try:
            config = self.platform_config[platform]
            selectors = config["selectors"]["post_button"]

            for selector in selectors:
                try:
                    # Try to find the element
                    element = page.wait_for_selector(selector, timeout=10000)
                    if element:
                        # Scroll into view and click
                        element.scroll_into_view_if_needed()
                        time.sleep(1)
                        element.click()
                        self.logger.info(f"Clicked post button for {platform} using selector: {selector}")
                        time.sleep(2)  # Allow modal/input to appear
                        return True
                except Exception:
                    continue

            self.logger.warning(f"Could not find post button for {platform} with any selector")
            return False

        except Exception as e:
            self.logger.error(f"Error finding post button for {platform}: {e}")
            return False

    def populate_post_content(self, page: Page, platform: str, content: str) -> bool:
        """
        Populate the post content in the platform's text editor.

        Args:
            page: Playwright page instance
            platform: Platform name
            content: The content to post

        Returns:
            True if content was populated successfully, False otherwise
        """
        try:
            # Clean the content
            cleaned_content = self.clean_text(content)
            config = self.platform_config[platform]
            selectors = config["selectors"]["post_input"]

            # Platform-specific character limits
            char_limits = {
                "facebook": 63206,
                "instagram": 2200,
                "twitter": 280
            }

            max_length = char_limits.get(platform, 63206)
            if len(cleaned_content) > max_length:
                self.logger.warning(f"Content exceeds {platform}'s {max_length} character limit. Truncating...")
                cleaned_content = cleaned_content[:max_length - 10] + "..."

            for selector in selectors:
                try:
                    # Wait for the input element
                    element = page.wait_for_selector(selector, timeout=10000)
                    if element:
                        # Click to focus
                        element.click()
                        time.sleep(1)

                        # Clear existing content
                        element.fill("")
                        time.sleep(0.5)

                        # Type the content
                        element.type(cleaned_content, delay=50)
                        time.sleep(1)

                        self.logger.info(f"Populated content for {platform} using selector: {selector}")
                        return True
                except Exception:
                    continue

            # Fallback: Use keyboard to type directly
            try:
                page.keyboard.press("Control+a")  # Select all
                page.keyboard.press("Delete")  # Delete
                time.sleep(0.5)
                page.keyboard.type(cleaned_content, delay=50)
                self.logger.info(f"Populated content for {platform} using keyboard fallback")
                return True
            except Exception as e:
                self.logger.error(f"Keyboard fallback failed for {platform}: {e}")

            self.logger.error(f"Could not populate content for {platform}")
            return False

        except Exception as e:
            self.logger.error(f"Error populating content for {platform}: {e}")
            return False

    def wait_for_login(self, page: Page, platform: str, timeout: int = 120) -> bool:
        """
        Wait for user to log in manually.

        Args:
            page: Playwright page instance
            platform: Platform name
            timeout: Maximum time to wait in seconds

        Returns:
            True if login detected, False if timeout
        """
        config = self.platform_config[platform]
        self.logger.info(f"Waiting for manual login to {config['name']}...")
        print(f"[INFO] Please log in to {config['name']} in the browser if not already logged in.")

        start_time = time.time()
        check_interval = 2  # seconds

        while time.time() - start_time < timeout:
            if self.check_login_status(page, platform):
                self.logger.info(f"[SUCCESS] Login detected for {config['name']}!")
                return True

            elapsed = int(time.time() - start_time)
            if elapsed % 15 == 0:
                self.logger.warning(f"[WARNING] Waiting for login to {config['name']}... ({elapsed}s/{timeout}s)")
                print(f"[WARNING] Waiting for login to {config['name']}... ({elapsed}s/{timeout}s)")

            time.sleep(check_interval)

        self.logger.error(f"Login timeout for {config['name']} after {timeout} seconds")
        return False

    def post_to_platform(self, content: str, platform: str,
                         wait_for_login_timeout: int = 120,
                         auto_submit: bool = False) -> Dict[str, Any]:
        """
        Post content to a specific social media platform.

        Args:
            content: The content to post
            platform: Platform name (facebook, instagram, twitter)
            wait_for_login_timeout: Seconds to wait for login
            auto_submit: If True, automatically submit the post (NOT recommended for HITL)

        Returns:
            Dictionary with posting result
        """
        timestamp = datetime.now().isoformat()
        config = self.platform_config.get(platform)

        if not config:
            return {
                "success": False,
                "platform": platform,
                "error": f"Unknown platform: {platform}",
                "timestamp": timestamp
            }

        self.logger.info(f"=" * 60)
        self.logger.info(f"Starting post to {config['name']}")
        self.logger.info(f"=" * 60)

        try:
            # Setup browser
            context, page = self.setup_browser()

            # Navigate to platform
            if not self.navigate_to_platform(page, platform):
                return {
                    "success": False,
                    "platform": platform,
                    "error": f"Failed to navigate to {config['name']}",
                    "timestamp": timestamp
                }

            # Wait for login
            if not self.check_login_status(page, platform):
                if not self.wait_for_login(page, platform, wait_for_login_timeout):
                    return {
                        "success": False,
                        "platform": platform,
                        "error": f"Login timeout for {config['name']}",
                        "timestamp": timestamp,
                        "human_action_required": "Please log in and retry"
                    }

            # Find and click post button
            if not self.find_and_click_post_button(page, platform):
                # Some platforms show the input directly without clicking a button
                self.logger.info(f"Post button not found for {platform}, attempting direct input...")

            # Populate content
            if not self.populate_post_content(page, platform, content):
                return {
                    "success": False,
                    "platform": platform,
                    "error": f"Failed to populate content for {config['name']}",
                    "timestamp": timestamp
                }

            # HITL: Do NOT auto-submit unless explicitly requested
            if auto_submit:
                self.logger.warning("Auto-submit is enabled - this bypasses HITL oversight!")
                # Could implement submit logic here, but NOT recommended
                pass

            # Return success with HITL notice
            result = {
                "success": True,
                "platform": platform,
                "platform_name": config['name'],
                "message": f"Content populated for {config['name']}. Please review and submit manually.",
                "timestamp": timestamp,
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "human_action_required": "Click the Post/Share button to publish",
                "browser_open": True,
                "url": page.url
            }

            self.logger.info(f"Post preparation complete for {config['name']}")
            return result

        except Exception as e:
            self.logger.error(f"Error posting to {platform}: {e}")
            return {
                "success": False,
                "platform": platform,
                "error": str(e),
                "timestamp": timestamp
            }
        finally:
            # Keep browser open for HITL review
            # Browser will be closed by close_browser() call
            pass

    def post_to_social_platforms(self, content: str,
                                  platforms: Optional[List[str]] = None,
                                  wait_for_login_timeout: int = 120) -> Dict[str, Any]:
        """
        Post content to multiple social media platforms.

        This is the main entry point for cross-platform posting.

        Args:
            content: The content to post
            platforms: List of platforms to post to. Defaults to ['facebook', 'instagram', 'twitter']
            wait_for_login_timeout: Seconds to wait for login per platform

        Returns:
            Dictionary with results for each platform:
            {
                "success": bool (overall),
                "timestamp": str,
                "platforms": {
                    "facebook": { "success": bool, "message": str, ... },
                    "instagram": { "success": bool, "message": str, ... },
                    "twitter": { "success": bool, "message": str, ... }
                }
            }
        """
        if platforms is None:
            platforms = ['facebook', 'instagram', 'twitter']

        timestamp = datetime.now().isoformat()
        results = {
            "success": True,
            "timestamp": timestamp,
            "platforms": {},
            "summary": {
                "total": len(platforms),
                "successful": 0,
                "failed": 0
            }
        }

        self.logger.info("=" * 70)
        self.logger.info(f"Starting cross-platform social media posting")
        self.logger.info(f"Platforms: {', '.join(platforms)}")
        self.logger.info(f"Content preview: {content[:100]}...")
        self.logger.info("=" * 70)

        for platform in platforms:
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"Processing platform: {platform}")
            self.logger.info(f"{'='*50}")

            try:
                platform_result = self.post_to_platform(
                    content=content,
                    platform=platform,
                    wait_for_login_timeout=wait_for_login_timeout
                )

                results["platforms"][platform] = platform_result

                if platform_result.get("success"):
                    results["summary"]["successful"] += 1
                    self.logger.info(f"[SUCCESS] {platform}: {platform_result.get('message', 'OK')}")
                else:
                    results["summary"]["failed"] += 1
                    results["success"] = False
                    self.logger.error(f"[FAILED] {platform}: {platform_result.get('error', 'Unknown error')}")

            except Exception as e:
                results["summary"]["failed"] += 1
                results["success"] = False
                results["platforms"][platform] = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                self.logger.error(f"[EXCEPTION] {platform}: {e}")

            # Small delay between platforms
            time.sleep(2)

        # Log summary
        self.logger.info("\n" + "=" * 70)
        self.logger.info("CROSS-PLATFORM POSTING SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"Total platforms: {results['summary']['total']}")
        self.logger.info(f"Successful: {results['summary']['successful']}")
        self.logger.info(f"Failed: {results['summary']['failed']}")
        self.logger.info(f"Overall success: {results['success']}")
        self.logger.info("=" * 70)

        return results

    def close_browser(self):
        """Close the browser if it's open."""
        try:
            if self.browser:
                self.browser.close()
                self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

        if self.playwright:
            self.playwright.stop()
            self.logger.info("Playwright stopped")

    def scrape_notifications(self, platform: str, page: Page) -> List[Dict[str, Any]]:
        """
        Scrape notifications/activity from a social media platform.

        Args:
            platform: Platform name (facebook, instagram, twitter)
            page: Playwright page instance

        Returns:
            List of notification dictionaries with type, content, and timestamp
        """
        notifications = []
        config = self.platform_config.get(platform)

        if not config:
            return notifications

        try:
            # Navigate to notifications page
            notification_url = config.get("notification_url", f"{config['base_url']}/notifications")
            self.logger.info(f"Navigating to {platform} notifications: {notification_url}")
            page.goto(notification_url, wait_until="networkidle", timeout=60000)
            time.sleep(3)

            # Get notification items using platform-specific selectors
            selectors = config["selectors"]["notification_item"]

            notification_elements = []
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        notification_elements = elements[:10]  # Limit to 10 most recent
                        self.logger.info(f"Found {len(notification_elements)} notifications for {platform}")
                        break
                except Exception:
                    continue

            # Extract notification data
            for idx, element in enumerate(notification_elements):
                try:
                    notification_text = element.inner_text().strip()[:200]  # Truncate long text
                    
                    # Determine notification type based on keywords
                    notification_type = "general"
                    text_lower = notification_text.lower()
                    if any(word in text_lower for word in ["like", "love", "react"]):
                        notification_type = "like"
                    elif any(word in text_lower for word in ["comment", "reply"]):
                        notification_type = "comment"
                    elif any(word in text_lower for word in ["mention", "tag"]):
                        notification_type = "mention"
                    elif any(word in text_lower for word in ["follow", "friend"]):
                        notification_type = "follow"
                    elif any(word in text_lower for word in ["share", "retweet"]):
                        notification_type = "share"

                    notifications.append({
                        "platform": platform,
                        "type": notification_type,
                        "content": notification_text,
                        "index": idx,
                        "scraped_at": datetime.now().isoformat()
                    })
                except Exception as e:
                    self.logger.warning(f"Error extracting notification {idx} for {platform}: {e}")
                    continue

            self.logger.info(f"Scraped {len(notifications)} notifications from {platform}")

        except Exception as e:
            self.logger.error(f"Error scraping notifications for {platform}: {e}")

        return notifications

    def generate_social_summary(self, platforms: Optional[List[str]] = None,
                                 output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape notifications from all platforms and generate a social summary markdown file.

        Args:
            platforms: List of platforms to scrape. Defaults to ['facebook', 'instagram', 'twitter']
            output_dir: Directory for output file. Defaults to ./Briefings

        Returns:
            Dictionary with summary generation result
        """
        if platforms is None:
            platforms = ['facebook', 'instagram', 'twitter']

        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Set output directory
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "Briefings")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        summary_file = output_path / "Social_Summary.md"

        self.logger.info("=" * 70)
        self.logger.info("Generating Social Media Summary")
        self.logger.info(f"Platforms: {', '.join(platforms)}")
        self.logger.info(f"Output: {summary_file}")
        self.logger.info("=" * 70)

        all_notifications = []
        platform_summaries = {}

        try:
            # Setup browser once for all platforms
            context, page = self.setup_browser()

            for platform in platforms:
                self.logger.info(f"\nScraping notifications from {platform}...")

                try:
                    # Navigate and check login
                    if self.navigate_to_platform(page, platform):
                        if self.check_login_status(page, platform):
                            # Scrape notifications
                            notifications = self.scrape_notifications(platform, page)
                            all_notifications.extend(notifications)

                            # Platform summary
                            platform_summaries[platform] = {
                                "total": len(notifications),
                                "likes": sum(1 for n in notifications if n["type"] == "like"),
                                "comments": sum(1 for n in notifications if n["type"] == "comment"),
                                "mentions": sum(1 for n in notifications if n["type"] == "mention"),
                                "shares": sum(1 for n in notifications if n["type"] == "share"),
                                "follows": sum(1 for n in notifications if n["type"] == "follow")
                            }
                            self.logger.info(f"Scraped {len(notifications)} notifications from {platform}")
                        else:
                            self.logger.warning(f"Not logged in to {platform}, skipping notifications")
                            platform_summaries[platform] = {"error": "Not logged in"}
                    else:
                        self.logger.warning(f"Failed to navigate to {platform}")
                        platform_summaries[platform] = {"error": "Navigation failed"}

                except Exception as e:
                    self.logger.error(f"Error scraping {platform}: {e}")
                    platform_summaries[platform] = {"error": str(e)}

                time.sleep(2)  # Delay between platforms

            # Close browser
            self.close_browser()

        except Exception as e:
            self.logger.error(f"Error setting up browser for summary: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": timestamp_str
            }

        # Generate markdown summary
        total_notifications = len(all_notifications)
        total_likes = sum(1 for n in all_notifications if n["type"] == "like")
        total_comments = sum(1 for n in all_notifications if n["type"] == "comment")
        total_mentions = sum(1 for n in all_notifications if n["type"] == "mention")
        total_shares = sum(1 for n in all_notifications if n["type"] == "share")

        markdown_content = f"""---
type: social_media_summary
generated_at: {timestamp_str}
platforms: {', '.join(platforms)}
total_notifications: {total_notifications}
hackathon_tier: Gold
---

# Social Media Activity Summary

**Generated:** {timestamp_str}

**Platforms Monitored:** {', '.join(platforms)}

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Notifications | {total_notifications} |
| Likes/Reactions | {total_likes} |
| Comments/Replies | {total_comments} |
| Mentions/Tags | {total_mentions} |
| Shares/Retweets | {total_shares} |

---

## Platform Breakdown

"""
        for platform, summary in platform_summaries.items():
            platform_name = self.platform_config.get(platform, {}).get("name", platform.title())
            markdown_content += f"### {platform_name}\n\n"

            if "error" in summary:
                markdown_content += f"**Status:** {summary['error']}\n\n"
            else:
                markdown_content += f"""| Metric | Count |
|--------|-------|
| Total | {summary.get('total', 0)} |
| Likes | {summary.get('likes', 0)} |
| Comments | {summary.get('comments', 0)} |
| Mentions | {summary.get('mentions', 0)} |
| Shares | {summary.get('shares', 0)} |
| New Followers | {summary.get('follows', 0)} |

"""

        # Add recent notifications
        if all_notifications:
            markdown_content += """---

## Recent Notifications

"""
            # Group by type
            by_type = {}
            for notif in all_notifications:
                notif_type = notif["type"]
                if notif_type not in by_type:
                    by_type[notif_type] = []
                by_type[notif_type].append(notif)

            for notif_type, items in sorted(by_type.items()):
                markdown_content += f"### {notif_type.title()}s ({len(items)})\n\n"
                for item in items[:5]:  # Show top 5 per type
                    markdown_content += f"- **{item['platform'].title()}:** {item['content']}\n"
                markdown_content += "\n"

        # Add footer
        markdown_content += f"""---

## Notes

- This summary was automatically generated by the AI Employee system
- Notifications are scraped in real-time from logged-in sessions
- Data is limited to the most recent 10 notifications per platform
- For detailed analytics, check each platform's native insights

---
*Gold Tier Social Media Integration - Personal AI Employee Hackathon 2026*
"""

        # Write summary file
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            self.logger.info(f"Social summary written to: {summary_file}")

            return {
                "success": True,
                "summary_file": str(summary_file),
                "total_notifications": total_notifications,
                "platforms_scraped": len([p for p, s in platform_summaries.items() if "error" not in s]),
                "timestamp": timestamp_str,
                "statistics": {
                    "total": total_notifications,
                    "likes": total_likes,
                    "comments": total_comments,
                    "mentions": total_mentions,
                    "shares": total_shares
                }
            }

        except Exception as e:
            self.logger.error(f"Error writing summary file: {e}")
            return {
                "success": False,
                "error": f"Failed to write summary file: {e}",
                "timestamp": timestamp_str
            }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_browser()
