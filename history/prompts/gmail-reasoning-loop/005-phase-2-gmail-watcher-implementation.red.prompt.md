---
id: "005"
title: "Phase 2 Gmail Watcher Implementation"
stage: "red"
date_iso: "2026-01-25"
surface: "agent"
model: "Qwen Code"
feature: "gmail-reasoning-loop"
branch: "001-gmail-reasoning-loop"
user: "PMLS"
command: "/sp.implement"
labels: ["gmail", "watcher", "perception", "authentication", "email-processing"]
links:
  spec: "../spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "src/gmail/auth.py"
  - "src/gmail/email_processor.py"
  - "src/gmail/gmail_watcher.py"
  - "src/utils/helpers.py"
  - "src/filesystem/watcher.py"
  - "src/models/entities.py"
  - "skills/plan_generation_skill.py"
  - "main.py"
tests_yaml: []
---

## Summary of Implementation: Phase 2 Gmail Watcher (Perception)

I have successfully implemented Phase 2: Gmail Watcher (Perception) from the Silver Tier Task List. Here's what was accomplished:

### 1. Authentication Module (`src/gmail/auth.py`)
- Implemented OAuth 2.0 flow for Gmail API authentication
- Created `GmailAuthenticator` class to handle credential loading, token refresh, and validation
- Added automatic token refresh and proper credential storage
- Included error handling for authentication issues

### 2. Email Processing Module (`src/gmail/email_processor.py`)
- Created functions to decode email bodies from base64 encoding
- Implemented HTML to Markdown conversion
- Developed email parsing to extract headers, body, and attachments
- Added functionality to save emails as Markdown files in the Needs_Action directory
- Included proper error handling and logging

### 3. Gmail Watcher Script (`src/gmail/gmail_watcher.py`)
- Implemented polling logic with 60-second interval (configurable)
- Created query building for "is:unread" with "URGENT" or "IMPORTANT" labels
- Added email processing and conversion to Markdown format
- Included functionality to save email content as `.md` files in `/Needs_Action`
- Implemented automatic token generation on first run
- Added proper error handling for API rate limits and connection issues
- Included logging for all activities

### 4. Utility Functions (`src/utils/helpers.py`)
- Created file operations utilities (move, copy, checksum)
- Added path management functions
- Implemented unique filename generation
- Added file metadata extraction

### 5. File System Monitoring (`src/filesystem/watcher.py`)
- Implemented file system monitoring using the watchdog library
- Created custom event handler for file creation, modification, and deletion
- Added callback functionality for handling file system events

### 6. Data Models (`src/models/entities.py`)
- Defined core data structures: EmailEntity, TaskEntity, PlanEntity, ApprovalEntity
- Created enumerations for statuses and types
- Added validation methods for entities
- Included helper functions to create entities from Gmail messages

### 7. Plan Generation Skill (`skills/plan_generation_skill.py`)
- Created skill to read task files from Needs_Action directory
- Implemented logic to generate structured plans with action steps
- Added functionality to save plans as Markdown files in Plans directory
- Included file movement from Needs_Action to Done after plan creation

### 8. Main Application (`main.py`)
- Orchestrated all components of the system
- Integrated Gmail Watcher, Plan Generation Skill, and File System Watcher
- Implemented threading for concurrent operation
- Added graceful shutdown handling

### Tasks Completed:
- [X] T007: Implemented authentication module `src/gmail/auth.py`
- [X] T008: Implemented file system monitoring module `src/filesystem/watcher.py`
- [X] T009: Created utility functions in `src/utils/helpers.py`
- [X] T010: Created data models in `src/models/entities.py`
- [X] T011: Created email processing module `src/gmail/email_processor.py`
- [X] T012: Implemented `gmail_watcher.py` with authentication and polling logic
- [X] T013: Implemented email filtering logic for UNREAD emails with "URGENT" or "IMPORTANT" labels
- [X] T014: Implemented email to Markdown conversion and save to `/Needs_Action` directory
- [X] T015: Created plan generation skill that reads tasks and creates plan files
- [X] T016: Implemented file movement from `/Needs_Action` to `/Done` after plan creation
- [X] T017: Added error handling for Gmail API rate limits and connection issues
- [X] T018: Added logging for email processing activities

The implementation follows security best practices with proper credential handling and includes comprehensive error handling and logging. The system is now capable of monitoring Gmail for urgent/important emails, converting them to Markdown files, generating action plans, and managing the workflow between different directories.