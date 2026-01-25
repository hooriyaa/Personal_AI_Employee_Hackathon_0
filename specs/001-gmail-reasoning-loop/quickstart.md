# Quickstart Guide: Gmail Reasoning Loop

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Google Account with Gmail enabled
- Access to Google Cloud Console to create API credentials

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If requirements.txt doesn't exist yet, install the required packages:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib watchdog python-dotenv
```

### 4. Setup Gmail API Credentials

#### A. Create Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" and then "New Project"
3. Enter a project name (e.g., "Gmail Reasoning Loop") and click "Create"

#### B. Enable Gmail API
1. In your project, search for "Gmail API" in the search bar
2. Click on "Gmail API" in the results
3. Click "Enable" to enable the API for your project

#### C. Create OAuth 2.0 Credentials
1. Go to "Credentials" in the left sidebar
2. Click "Create Credentials" and select "OAuth client ID"
3. Select "Desktop application" as the application type
4. Enter a name (e.g., "Gmail Reasoning Loop Client")
5. Click "Create"
6. Download the credentials JSON file
7. Rename the downloaded file to `credentials.json`

#### D. Store Credentials Securely
1. Create a `secrets` directory in the project root:
   ```bash
   mkdir secrets
   ```
2. Move the `credentials.json` file to the `secrets` directory:
   ```bash
   mv Downloads/credentials.json secrets/
   ```
3. Add the secrets directory to `.gitignore` to prevent committing credentials:
   ```bash
   echo "secrets/" >> .gitignore
   ```

### 5. Directory Structure Setup
Ensure the following directories exist in your project root:
```bash
mkdir -p Inbox Needs_Action Plans Pending_Approval Approved Done Logs
```

### 6. Initial Run
```bash
python main.py
```

On the first run:
1. The application will prompt you to visit a URL in your browser
2. Sign in to your Google account
3. Grant the requested permissions
4. Copy the authorization code and paste it back into the terminal
5. The application will create a `token.json` file in the `secrets` directory for future use

## How It Works

### Gmail Monitoring
- The system polls your Gmail account every 60-120 seconds
- Looks for unread emails with labels "URGENT" or "IMPORTANT"
- Converts these emails to Markdown format
- Saves them as files in the `/Needs_Action` directory

### Reasoning Loop
- Monitors the `/Needs_Action` directory for new files
- When a new file appears, creates a plan in `/Plans`
- The plan includes steps to process the email appropriately

### Approval Process
- For sensitive actions (like sending emails), the system creates a file in `/Pending_Approval`
- Move the file to `/Approved` to authorize the action
- The system will then execute the approved action

## Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:
```env
VAULT_PATH=./  # Path to the vault directory (default: current directory)
GMAIL_POLL_INTERVAL=60  # Polling interval in seconds (default: 60)
LOG_LEVEL=INFO  # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Custom Labels
By default, the system looks for emails with "URGENT" or "IMPORTANT" labels. To customize:
1. Edit the configuration in `src/config/settings.py`
2. Modify the `WATCHED_LABELS` list to include your preferred labels

## Troubleshooting

### Common Issues

#### API Quota Exceeded
- Solution: Increase the polling interval in settings
- Check your daily usage in Google Cloud Console

#### Authentication Problems
- Ensure `credentials.json` is in the `secrets` directory
- Delete `token.json` and re-authenticate if permissions have changed

#### File Permissions
- Ensure the application has read/write access to all required directories
- On Unix systems, check file permissions with `ls -la`

### Logging
- Logs are stored in the `Logs` directory
- Check `Logs/app.log` for detailed information about system operations
- Use the `LOG_LEVEL` environment variable to adjust verbosity

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- The `secrets` directory is automatically added to `.gitignore`
- Token files contain OAuth 2.0 access information - protect them accordingly
- Review the permissions granted to your Google Cloud application regularly