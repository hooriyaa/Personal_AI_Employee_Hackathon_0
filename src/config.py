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