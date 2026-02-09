# Quickstart Guide: Selenium LinkedIn Automation

## Setup

1. **Install Dependencies**
   Dependencies are already added to requirements.txt:
   ```
   selenium==4.15.0
   webdriver-manager==4.0.1
   ```

2. **Install the packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure Chrome is Installed**
   The automation requires Chrome browser to be installed on the system.

## Usage

### LinkedIn Post Automation
When a file with type `linkedin_post` is moved to the `/Approved` directory, the system will:
1. Open Chrome using the user's existing profile
2. Navigate to LinkedIn
3. Click "Start a post"
4. Populate the content from the approved file
5. Leave the post in draft state for manual review and publishing

### Error Handling
- If Chrome is already in use, the system will log an appropriate error
- If the user is not logged in to LinkedIn, a warning will be displayed
- If UI elements cannot be found due to interface changes, an error will be logged

## Testing
Run the following to test the LinkedIn automation:
```bash
# Create a test LinkedIn post file in Pending_Approval
echo -e "type: linkedin_post\ncontent: This is a test post from the AI agent." > "/Pending_Approval/LINKEDIN_TEST.md"

# Move to Approved to trigger automation
mv "/Pending_Approval/LINKEDIN_TEST.md" "/Approved/"
```