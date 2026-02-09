# API Contract: Gemini Service Integration

## Overview
This document defines the API contracts for integrating Google's Gemini API into the email reply and LinkedIn post generation functionality.

## Service: GeminiService

### Endpoint: Generate Email Reply
**Method**: POST  
**Path**: `/api/gemini/email-reply`  
**Description**: Generates a professional email reply based on the original email content, sender information, and intended response intent.

#### Request
```json
{
  "email_body": "string, required - The content of the original email",
  "sender_name": "string, required - The name of the sender",
  "intent": "string, required - The intended purpose of the reply (e.g., BUSINESS, SUPPORT, GENERAL)"
}
```

#### Response (Success)
```json
{
  "success": true,
  "content": "string - The AI-generated email reply",
  "confidence": "float - Confidence score between 0 and 1",
  "tokens_used": "integer - Number of tokens consumed"
}
```

#### Response (Error)
```json
{
  "success": false,
  "error": "string - Error message",
  "fallback_message": "string - Safe fallback message to use instead"
}
```

### Endpoint: Generate LinkedIn Post
**Method**: POST  
**Path**: `/api/gemini/linkedin-post`  
**Description**: Generates an engaging LinkedIn post based on a given topic.

#### Request
```json
{
  "topic": "string, required - The subject or theme for the LinkedIn post",
  "style": "string, optional - Desired style of the post (e.g., professional, casual, promotional)"
}
```

#### Response (Success)
```json
{
  "success": true,
  "content": "string - The AI-generated LinkedIn post content",
  "hashtags": "array of strings - Relevant hashtags for the post",
  "confidence": "float - Confidence score between 0 and 1"
}
```

#### Response (Error)
```json
{
  "success": false,
  "error": "string - Error message",
  "fallback_message": "string - Safe fallback message to use instead"
}
```

### Endpoint: Health Check
**Method**: GET  
**Path**: `/api/gemini/health`  
**Description**: Checks the health and connectivity of the Gemini API service.

#### Response
```json
{
  "status": "string - Service status (healthy, degraded, unavailable)",
  "api_reachable": "boolean - Whether the Gemini API is reachable",
  "last_response_time": "integer - Last response time in milliseconds"
}
```

## Error Handling
All API calls must implement proper error handling with fallback mechanisms:
- Network errors should return a safe fallback message
- API quota exceeded errors should return a predefined message
- Invalid input should return appropriate error messages
- All errors should be logged without exposing sensitive information

## Security
- API keys must be loaded from environment variables
- No API keys should be transmitted in request bodies or logs
- All requests should implement appropriate timeout handling