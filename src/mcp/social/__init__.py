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
"""

from .server import SocialMediaMCPServer, main

__all__ = ["SocialMediaMCPServer", "main"]
