"""
Social Media MCP Server - Production-ready Model Context Protocol server for social media platforms.

This server provides real-time posting capabilities to:
- Facebook (via Graph API v19.0)
- X/Twitter (via Twitter API v2)

Gold Tier Compliance:
- Real social media API integration
- Proper error handling for 400/401/500 errors
- Human-in-the-Loop approval enforcement (via skill layer)
- Full audit logging

Environment Variables Required:
- FB_PAGE_ACCESS_TOKEN: Facebook Page Access Token
- FB_PAGE_ID: Facebook Page ID
- TWITTER_BEARER_TOKEN: Twitter API Bearer Token
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("social_media_mcp_server")


class FacebookAPIError(Exception):
    """Raised when Facebook API request fails."""
    pass


class TwitterAPIError(Exception):
    """Raised when Twitter API request fails."""
    pass


class AuthenticationError(Exception):
    """Raised when API authentication fails."""
    pass


class SocialMediaAPIClient:
    """
    Production social media API client for Facebook and Twitter/X.

    Uses official APIs:
    - Facebook Graph API v19.0: https://graph.facebook.com/v19.0/
    - Twitter API v2: https://api.twitter.com/2/
    """

    def __init__(self, fb_page_access_token: Optional[str] = None,
                 fb_page_id: Optional[str] = None,
                 twitter_bearer_token: Optional[str] = None):
        """
        Initialize social media API client.

        Args:
            fb_page_access_token: Facebook Page Access Token
            fb_page_id: Facebook Page ID
            twitter_bearer_token: Twitter API Bearer Token
        """
        self.fb_page_access_token = fb_page_access_token
        self.fb_page_id = fb_page_id
        self.twitter_bearer_token = twitter_bearer_token

        # API endpoints
        self.facebook_base_url = "https://graph.facebook.com/v19.0"
        self.twitter_base_url = "https://api.twitter.com/2"

    def _validate_facebook_config(self) -> None:
        """Validate Facebook configuration is present."""
        if not self.fb_page_access_token:
            raise AuthenticationError("Facebook Page Access Token not configured")
        if not self.fb_page_id:
            raise AuthenticationError("Facebook Page ID not configured")

    def _validate_twitter_config(self) -> None:
        """Validate Twitter configuration is present."""
        if not self.twitter_bearer_token:
            raise AuthenticationError("Twitter Bearer Token not configured")

    def post_to_facebook(self, message: str) -> Dict[str, Any]:
        """
        Post a message to Facebook Page.

        Args:
            message: The message content to post

        Returns:
            Dictionary with post_id and success status

        Raises:
            AuthenticationError: If credentials not configured
            FacebookAPIError: If API request fails (400/401/500)
        """
        self._validate_facebook_config()

        endpoint = f"{self.facebook_base_url}/{self.fb_page_id}/feed"
        payload = {
            'message': message,
            'access_token': self.fb_page_access_token
        }

        logger.info(f"Posting to Facebook Page {self.fb_page_id}")

        try:
            response = requests.post(endpoint, data=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            post_id = result.get('id', 'unknown')

            logger.info(f"Facebook post successful: {post_id}")

            return {
                "success": True,
                "post_id": post_id,
                "platform": "facebook",
                "posted_at": datetime.now().isoformat(),
                "message_preview": message[:100] + "..." if len(message) > 100 else message
            }

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            error_message = self._parse_facebook_error(e.response)

            if status_code == 400:
                raise FacebookAPIError(f"Bad Request (400): {error_message}")
            elif status_code == 401:
                raise AuthenticationError(f"Unauthorized (401): {error_message}")
            elif status_code >= 500:
                raise FacebookAPIError(f"Server Error ({status_code}): {error_message}")
            else:
                raise FacebookAPIError(f"HTTP Error ({status_code}): {error_message}")

        except requests.exceptions.Timeout:
            raise FacebookAPIError("Request timeout - Facebook API did not respond in time")
        except requests.exceptions.RequestException as e:
            raise FacebookAPIError(f"Network error: {str(e)}")

    def _parse_facebook_error(self, response: requests.Response) -> str:
        """Parse Facebook API error response."""
        try:
            error_data = response.json()
            error_info = error_data.get('error', {})
            message = error_info.get('message', 'Unknown error')
            error_type = error_info.get('type', 'Unknown')
            return f"[{error_type}] {message}"
        except Exception:
            return response.text[:200] if response.text else "No error details"

    def post_to_twitter(self, text: str) -> Dict[str, Any]:
        """
        Post a tweet to X/Twitter.

        Args:
            text: The tweet text content (max 280 characters)

        Returns:
            Dictionary with tweet data and success status

        Raises:
            AuthenticationError: If credentials not configured
            TwitterAPIError: If API request fails (400/401/500)
        """
        self._validate_twitter_config()

        endpoint = f"{self.twitter_base_url}/tweets"
        headers = {
            'Authorization': f'Bearer {self.twitter_bearer_token}',
            'Content-Type': 'application/json'
        }
        payload = {'text': text}

        logger.info(f"Posting to Twitter/X")

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            tweet_id = result.get('data', {}).get('id', 'unknown')

            logger.info(f"Twitter post successful: {tweet_id}")

            return {
                "success": True,
                "tweet_id": tweet_id,
                "platform": "twitter",
                "posted_at": datetime.now().isoformat(),
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            }

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            error_message = self._parse_twitter_error(e.response)

            if status_code == 400:
                raise TwitterAPIError(f"Bad Request (400): {error_message}")
            elif status_code == 401:
                raise AuthenticationError(f"Unauthorized (401): {error_message}")
            elif status_code == 403:
                raise TwitterAPIError(f"Forbidden (403): {error_message}")
            elif status_code >= 500:
                raise TwitterAPIError(f"Server Error ({status_code}): {error_message}")
            else:
                raise TwitterAPIError(f"HTTP Error ({status_code}): {error_message}")

        except requests.exceptions.Timeout:
            raise TwitterAPIError("Request timeout - Twitter API did not respond in time")
        except requests.exceptions.RequestException as e:
            raise TwitterAPIError(f"Network error: {str(e)}")

    def _parse_twitter_error(self, response: requests.Response) -> str:
        """Parse Twitter API error response."""
        try:
            error_data = response.json()
            errors = error_data.get('errors', [])
            if errors:
                error_details = []
                for err in errors:
                    msg = err.get('message', 'Unknown error')
                    error_details.append(msg)
                return "; ".join(error_details)
            return error_data.get('title', 'Unknown error')
        except Exception:
            return response.text[:200] if response.text else "No error details"


class SocialMediaMCPServer:
    """
    MCP Server for Social Media posting operations.

    Implements Gold Tier tools:
    - post_to_facebook: Post message to Facebook Page
    - post_to_twitter: Post tweet to X/Twitter

    Note: This MCP server is called by the skill layer which enforces
    Human-in-the-Loop approval workflow. The skill creates Pending_Approval
    files first, and only calls these tools after human approval.
    """

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("social-media")
        self.client: Optional[SocialMediaAPIClient] = None
        self._setup_tools()
        self._initialize_client()

    def _get_env_credentials(self) -> Dict[str, Optional[str]]:
        """
        Get social media credentials from environment variables.

        Returns:
            Dictionary with fb_page_access_token, fb_page_id, twitter_bearer_token
        """
        return {
            'fb_page_access_token': os.environ.get('FB_PAGE_ACCESS_TOKEN'),
            'fb_page_id': os.environ.get('FB_PAGE_ID'),
            'twitter_bearer_token': os.environ.get('TWITTER_BEARER_TOKEN')
        }

    def _initialize_client(self):
        """Initialize social media API client connection."""
        try:
            creds = self._get_env_credentials()
            self.client = SocialMediaAPIClient(
                fb_page_access_token=creds['fb_page_access_token'],
                fb_page_id=creds['fb_page_id'],
                twitter_bearer_token=creds['twitter_bearer_token']
            )

            # Log configuration status (without exposing values)
            fb_configured = bool(creds['fb_page_access_token'] and creds['fb_page_id'])
            twitter_configured = bool(creds['twitter_bearer_token'])

            logger.info(f"Social Media MCP Server initialized - Facebook: {fb_configured}, Twitter: {twitter_configured}")

        except Exception as e:
            logger.error(f"Failed to initialize social media client: {e}")
            self.client = None

    def _setup_tools(self):
        """Register MCP tools with the server."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available Social Media tools."""
            return [
                Tool(
                    name="post_to_facebook",
                    description=(
                        "Post a message to a Facebook Page. "
                        "Uses Facebook Graph API v19.0. "
                        "Requires FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID environment variables. "
                        "NOTE: This tool should only be called after Human-in-the-Loop approval. "
                        "The skill layer creates Pending_Approval files first."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message content to post to Facebook (max 63,206 characters)"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="post_to_twitter",
                    description=(
                        "Post a tweet to X/Twitter. "
                        "Uses Twitter API v2. "
                        "Requires TWITTER_BEARER_TOKEN environment variable. "
                        "NOTE: This tool should only be called after Human-in-the-Loop approval. "
                        "The skill layer creates Pending_Approval files first. "
                        "Tweet text must be 280 characters or less."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The tweet text content (max 280 characters)"
                            }
                        },
                        "required": ["text"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls from MCP clients."""
            try:
                if not self.client:
                    return [TextContent(
                        type="text",
                        text="Error: Social Media client not initialized. Check environment variables."
                    )]

                if name == "post_to_facebook":
                    result = await self._post_to_facebook(
                        message=arguments.get("message", "")
                    )
                elif name == "post_to_twitter":
                    result = await self._post_to_twitter(
                        text=arguments.get("text", "")
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [TextContent(type="text", text=str(result))]

            except AuthenticationError as e:
                logger.error(f"Authentication error in {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"AuthenticationError: {str(e)}"
                )]
            except (FacebookAPIError, TwitterAPIError) as e:
                logger.error(f"API error in {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"APIError: {str(e)}"
                )]
            except Exception as e:
                logger.error(f"Error in {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def _post_to_facebook(self, message: str) -> Dict[str, Any]:
        """
        Post a message to Facebook Page.

        Args:
            message: The message content to post

        Returns:
            Dictionary with post result

        Raises:
            FacebookAPIError: If posting fails
            AuthenticationError: If credentials invalid
        """
        if not self.client:
            raise FacebookAPIError("Social Media client not initialized")

        if not message or not message.strip():
            raise FacebookAPIError("Message cannot be empty")

        return self.client.post_to_facebook(message)

    async def _post_to_twitter(self, text: str) -> Dict[str, Any]:
        """
        Post a tweet to X/Twitter.

        Args:
            text: The tweet text content

        Returns:
            Dictionary with post result

        Raises:
            TwitterAPIError: If posting fails
            AuthenticationError: If credentials invalid
        """
        if not self.client:
            raise TwitterAPIError("Social Media client not initialized")

        if not text or not text.strip():
            raise TwitterAPIError("Tweet text cannot be empty")

        if len(text) > 280:
            raise TwitterAPIError(f"Tweet exceeds 280 character limit (got {len(text)} characters)")

        return self.client.post_to_twitter(text)

    async def run(self):
        """Run the MCP server using stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# Main entry point
async def main():
    """Main entry point for the Social Media MCP Server."""
    server = SocialMediaMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
