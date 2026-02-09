# API Contract: LinkedIn Automation Service

## Overview
This document defines the interface for the LinkedIn automation functionality that uses Selenium WebDriver to interact with LinkedIn's web interface.

## Service: LinkedInPoster

### Function: post_to_linkedin
**Description**: Automates the process of posting content to LinkedIn using Selenium WebDriver.

#### Parameters
```json
{
  "content": "string, required - The content to be posted on LinkedIn",
  "profile_path": "string, optional - Path to Chrome profile to use (defaults to user's default profile)"
}
```

#### Return Value (Success)
```json
{
  "success": true,
  "message": "string - Confirmation message",
  "automation_result": {
    "browser_opened": true,
    "content_populated": true,
    "post_ready_for_review": true
  }
}
```

#### Return Value (Error)
```json
{
  "success": false,
  "error": "string - Error message describing what went wrong",
  "automation_result": {
    "browser_opened": false,
    "content_populated": false,
    "error_details": "string - Specific error details"
  }
}
```

## Error Handling
The LinkedInPoster service must implement proper error handling:
- Profile conflicts should return a clear error message
- Network connectivity issues should be handled gracefully
- Interface changes on LinkedIn should be detected and reported
- Login session expiration should be detected and reported

## Security
- No LinkedIn credentials should be stored or transmitted
- Only rely on the user's existing browser session
- Maintain human oversight by not automatically clicking "Post"
- Log errors without exposing sensitive information