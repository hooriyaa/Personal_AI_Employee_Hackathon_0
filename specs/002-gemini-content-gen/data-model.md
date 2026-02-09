# Data Model: Gemini API Integration

## Entities

### EmailReplyRequest
Represents the input for email reply generation, containing email_body, sender_name, and intent.

- **email_body** (string): The content of the original email that needs a reply
- **sender_name** (string): The name of the person who sent the original email
- **intent** (string): The intended purpose or tone of the reply (e.g., "BUSINESS", "SUPPORT", "GENERAL")

### LinkedInPostRequest
Represents the input for LinkedIn post generation, containing the topic.

- **topic** (string): The subject or theme for the LinkedIn post
- **hashtags** (optional, list of strings): Suggested hashtags to include in the post

### APIConfiguration
Represents the API key and connection settings for Gemini service.

- **api_key** (string): The Gemini API key loaded from environment variables
- **model** (string): The specific Gemini model to use (e.g., "gemini-pro")
- **timeout** (integer): Request timeout in seconds

### GeneratedContent
Represents the output from the AI service, including the generated text and metadata.

- **content** (string): The AI-generated text (email reply or LinkedIn post)
- **confidence** (float): Confidence score of the generated content (0-1)
- **tokens_used** (integer): Number of tokens consumed in the generation
- **timestamp** (datetime): When the content was generated
- **request_type** (string): Type of request ("email_reply" or "linkedin_post")

## Relationships

- An `EmailReplyRequest` is processed by the Gemini API to produce a `GeneratedContent`
- A `LinkedInPostRequest` is processed by the Gemini API to produce a `GeneratedContent`
- An `APIConfiguration` is used to configure the connection to the Gemini service

## Validation Rules

- `email_body` must not exceed 10,000 characters to comply with API limits
- `sender_name` must be a non-empty string
- `intent` must be one of the predefined values: "GENERAL", "BUSINESS", "SUPPORT", "SCHEDULING", "CAREER", "SOCIAL"
- `topic` must be a non-empty string
- `api_key` must be present and valid
- `content` must not be empty after generation