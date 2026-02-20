"""
Social Media Module - Cross-platform social media automation.

This module provides automation for:
- Facebook posting and engagement tracking
- Instagram posting and engagement tracking
- Twitter/X posting and engagement tracking

Uses Playwright with persistent browser context for session management.
"""

from .poster import SocialMediaPoster
from .summary import SocialSummaryGenerator

__all__ = ['SocialMediaPoster', 'SocialSummaryGenerator']
