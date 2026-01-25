# Quickstart Guide: Local-First AI Employee (Bronze Tier)

## Setup Instructions

### 1. Clone or Create the Vault Structure
First, create the required Obsidian Vault structure:

```bash
mkdir -p vault/{Inbox,Needs_Action,Done,Logs,Plans,Pending_Approval,Approved,Briefings}
touch vault/Dashboard.md
```

### 2. Install Dependencies
Make sure you have Python 3.11+ installed, then install the required packages:

```bash
pip install watchdog pyyaml
```

### 3. Configure the Filesystem Watcher
Create a configuration file `config.py` with the following content:

```python
import os
from pathlib import Path

# Vault directory (relative to where the script runs)
VAULT_DIR = Path("./vault").resolve()

# Folder paths (relative to VAULT_DIR)
INBOX_DIR = VAULT_DIR / "Inbox"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
DONE_DIR = VAULT_DIR / "Done"
LOGS_DIR = VAULT_DIR / "Logs"
DASHBOARD_PATH = VAULT_DIR / "Dashboard.md"

# Polling interval for checking if file is fully written (in seconds)
POLLING_INTERVAL = 1.0

# Time to wait between polls to confirm file size stability (in seconds)
CONFIRMATION_DELAY = 2.0
```

### 4. Run the Filesystem Watcher
Start the filesystem watcher service:

```bash
cd src
python filesystem_watcher.py
```

## How It Works

### File Detection and Processing
1. Place any file in the `vault/Inbox/` folder
2. The filesystem watcher detects the new file
3. It waits for the file to be fully written using polling
4. It moves the file to `vault/Needs_Action/`
5. It creates a metadata trigger file (.md) in `vault/Needs_Action/` with YAML frontmatter
6. The agent can then process the trigger file and update the dashboard

### Example Metadata Trigger File
When a file named `example.pdf` is moved, a corresponding `example_trigger.md` will be created:

```markdown
---
filename: "example.pdf"
size: 102400
timestamp: "2026-01-25T10:00:00"
original_path: "./vault/Inbox/example.pdf"
---

# File Processing Request

A new file has been detected and moved to Needs_Action for processing.
```

## Validation Steps

### 1. Test File Detection
1. Create a test file in the Inbox: `touch vault/Inbox/test.txt`
2. Verify it moves to Needs_Action within 5 seconds
3. Verify a corresponding .md trigger file is created

### 2. Test Duplicate Handling
1. Create two files with the same name in the Inbox
2. Verify both are moved to Needs_Action with timestamp-appended names

### 3. Test Dashboard Update
1. Manually update the dashboard with the Vault_Write_Skill
2. Verify the changes are reflected in `vault/Dashboard.md`

## Troubleshooting

### File Not Moving from Inbox
- Check that the filesystem watcher is running
- Verify the file is completely written before the watcher attempts to move it
- Check the logs in `vault/Logs/` for any errors

### Duplicate Files Not Handled Correctly
- Ensure the timestamp appending logic is working
- Check that the file system has write permissions to the Needs_Action directory

### Dashboard Not Updating
- Verify the Vault_Write_Skill has proper write permissions
- Check that the dashboard path is correctly configured