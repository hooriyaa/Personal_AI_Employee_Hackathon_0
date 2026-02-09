# Quickstart Guide: Gemini API Integration

## Setup

1. **Install Dependencies**
   ```bash
   pip install google-generativeai
   ```

2. **Configure API Key**
   Add your Gemini API key to environment variables:
   ```bash
   # In your .env file or system environment
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Update Requirements**
   Add to `requirements.txt`:
   ```
   google-generativeai==0.4.0
   ```

## Usage

### Email Reply Generation
The system will automatically use Gemini to generate email replies when it detects a new email in the `/Needs_Action` directory. The generated reply will be placed in `/Pending_Approval` for review.

### LinkedIn Post Generation
To generate a LinkedIn post, create a file in `/Needs_Action` with "linkedin post" in the title or content. The system will generate a post based on the topic provided and place it in `/Pending_Approval`.

## Error Handling
- If the Gemini API is unavailable, the system will generate a safe fallback message
- All API errors are logged without exposing sensitive information
- The system continues to function even during API outages

## Testing
Run the following to test the integration:
```bash
python -m pytest tests/unit/test_gemini_integration.py
```