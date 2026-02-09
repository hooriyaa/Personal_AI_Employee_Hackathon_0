# Data Model: Selenium LinkedIn Automation

## Entities

### LinkedInPostDraft
Represents the content to be posted on LinkedIn, containing the text and metadata.

- **content** (string): The main content of the LinkedIn post
- **metadata** (dict): Additional information about the post (timestamp, source, etc.)
- **status** (string): Current status of the post (e.g., "approved", "posted", "failed")

### BrowserProfile
Represents the Chrome profile configuration for maintaining user session.

- **profile_path** (string): Path to the Chrome profile directory
- **user_data_dir** (string): Directory containing user data for the Chrome profile
- **session_state** (dict): Information about the current session state

### AutomationResult
Represents the outcome of the automation process, including success/failure status and error messages.

- **success** (boolean): Whether the automation was successful
- **error_message** (string, optional): Error message if automation failed
- **post_url** (string, optional): URL of the posted content if successful
- **timestamp** (datetime): When the automation was attempted
- **action_taken** (string): What action was performed (e.g., "opened_browser", "populated_content", "failed_login")

## Relationships

- A `LinkedInPostDraft` is processed by the LinkedIn automation to produce an `AutomationResult`
- A `BrowserProfile` is used during the automation process to maintain the user's LinkedIn session

## Validation Rules

- `content` in LinkedInPostDraft must not be empty
- `success` in AutomationResult must be a boolean value
- `profile_path` in BrowserProfile must be a valid directory path
- `error_message` in AutomationResult should be present when success is false