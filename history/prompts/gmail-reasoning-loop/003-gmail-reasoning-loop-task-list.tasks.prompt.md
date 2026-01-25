---
id: "003"
title: "Gmail Reasoning Loop Task List"
stage: "tasks"
date_iso: "2026-01-25"
surface: "agent"
model: "Qwen Code"
feature: "gmail-reasoning-loop"
branch: "001-gmail-reasoning-loop"
user: "PMLS"
command: "/sp.tasks"
labels: ["tasks", "implementation", "planning"]
links:
  spec: "../spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "specs/001-gmail-reasoning-loop/tasks.md"
tests_yaml: []
---

# Task List: Gmail Reasoning Loop

**Feature**: Gmail Reasoning Loop  
**Branch**: `001-gmail-reasoning-loop`  
**Date**: 2026-01-25  

## Overview

This task list implements the Gmail Reasoning Loop feature that monitors Gmail for URGENT/IMPORTANT emails, converts them to Markdown files in `/Needs_Action`, generates plans in `/Plans`, and implements a pre-approval mechanism for sensitive actions. The system will poll Gmail API every 60-120 seconds with secure credential handling.

## Dependencies

- Python 3.11+
- Google API client libraries
- Watchdog library for file system monitoring
- Properly configured Gmail API credentials

## Parallel Execution Examples

- T001 and T002 can run in parallel (different aspects of setup)
- T007 [P] and T008 [P] can run in parallel (different files)
- T012 [P] [US1] and T013 [P] [US1] can run in parallel (different components of US1)

## Implementation Strategy

1. **MVP Scope**: Implement User Story 1 (Automated Email Processing) with basic Gmail polling and file creation
2. **Incremental Delivery**: Add reasoning loop and approval mechanism in subsequent iterations
3. **Testing Approach**: Each user story is independently testable

---

## Phase 1: Setup

### Goal
Initialize the project with necessary dependencies, secure credential handling, and directory structure.

### Independent Test Criteria
- Dependencies are installed and accessible
- Secrets directory is created and added to .gitignore
- Required directories exist for the system to function

### Tasks

- [ ] T001 Create `/secrets` folder and update `.gitignore` to include the secrets directory
- [ ] T002 Install Google client libraries (`google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`) and watchdog
- [ ] T003 [P] Create required directories: `Inbox`, `Needs_Action`, `Plans`, `Pending_Approval`, `Approved`, `Done`, `Logs`
- [ ] T004 [P] Document the exact steps for the user to go to Google Cloud Console, enable Gmail API, and download `credentials.json` to the `/secrets` folder
- [ ] T005 [P] Create configuration file `src/config/settings.py` with default values for Gmail polling interval and watched labels
- [ ] T006 [P] Create logging configuration to write logs to the `Logs` directory

---

## Phase 2: Foundational Components

### Goal
Implement foundational components that are required for all user stories to function properly.

### Independent Test Criteria
- Authentication module can handle Gmail API credentials
- File system monitoring can detect file changes
- Basic utility functions work as expected

### Tasks

- [ ] T007 [P] Implement authentication module `src/gmail/auth.py` for Gmail API OAuth 2.0 flow
- [ ] T008 [P] Implement file system monitoring module `src/filesystem/watcher.py` using watchdog library
- [ ] T009 [P] Create utility functions in `src/utils/helpers.py` for file operations and path management
- [ ] T010 [P] Create data models for EmailEntity, TaskEntity, PlanEntity, and ApprovalEntity in `src/models/entities.py`
- [ ] T011 [P] Create email processing module `src/gmail/email_processor.py` to convert emails to Markdown format

---

## Phase 3: User Story 1 - Automated Email Processing (Priority: P1)

### Goal
As a busy professional, I want the system to automatically detect urgent and important emails and create action plans for them, so I can focus on high-priority tasks without missing critical communications.

### Independent Test Criteria
The system can connect to Gmail, identify emails with URGENT or IMPORTANT labels, convert them to files in a processing directory, and create corresponding plan files before moving them to a completed directory.

### Acceptance Scenarios
1. Given user has Gmail account with URGENT and IMPORTANT labeled emails, When the email monitoring system runs, Then it creates files for unread emails with these labels
2. Given there are files in the processing directory, When the reasoning system detects them, Then it creates plan files before moving the original files to a completed directory

### Tasks

- [ ] T012 [P] [US1] Implement `gmail_watcher.py` with authentication and polling logic (every 60-120 seconds)
- [ ] T013 [P] [US1] Implement email filtering logic to identify UNREAD emails with "URGENT" or "IMPORTANT" labels
- [ ] T014 [US1] Implement email to Markdown conversion and save to `/Needs_Action` directory
- [ ] T015 [US1] Create plan generation skill `skills/plan_generation_skill.py` that reads tasks and creates plan files in `/Plans`
- [ ] T016 [US1] Implement file movement from `/Needs_Action` to `/Done` after plan creation
- [ ] T017 [US1] Add error handling for Gmail API rate limits and connection issues
- [ ] T018 [US1] Add logging for email processing activities

---

## Phase 4: User Story 2 - Gmail API Integration (Priority: P2)

### Goal
As a user, I want to securely connect my Gmail account to the assistant, so that it can monitor my emails without compromising my privacy.

### Independent Test Criteria
The system can authenticate with Gmail API and access the user's emails with appropriate permissions.

### Acceptance Scenarios
1. Given user has properly configured authentication credentials, When the system attempts to connect to Gmail API, Then it successfully authenticates and accesses the mailbox

### Tasks

- [ ] T019 [P] [US2] Enhance authentication module to handle token refresh and expiration
- [ ] T020 [US2] Implement secure credential storage and retrieval from `/secrets` directory
- [ ] T021 [US2] Add authentication error handling and user notifications
- [ ] T022 [US2] Implement token validation function to check if credentials are still valid
- [ ] T023 [US2] Add retry logic with exponential backoff for API failures
- [ ] T024 [US2] Create a test function to verify Gmail connection without sending emails

---

## Phase 5: User Story 3 - Task Management Workflow (Priority: P3)

### Goal
As a user, I want to track the progress of email processing through different stages (Needs Action → Planned → Done), so I can monitor what the assistant is working on and what has been completed.

### Independent Test Criteria
Files move through the correct directories as the system processes them.

### Acceptance Scenarios
1. Given an email converted to a file in the processing directory, When the reasoning system creates a plan, Then a corresponding plan file appears and the original is moved to a completed directory

### Tasks

- [ ] T025 [P] [US3] Implement status tracking for tasks using the TaskEntity model
- [ ] T026 [US3] Create a dashboard or log file to track task progression through different stages
- [ ] T027 [US3] Enhance the plan generation skill to update task status as it progresses
- [ ] T028 [US3] Implement file movement tracking to ensure proper progression from Needs Action → Planned → Done
- [ ] T029 [US3] Add timestamps and metadata to track how long each task spends in each stage
- [ ] T030 [US3] Create reporting function to show statistics on task completion rates and times

---

## Phase 6: Approval Mechanism

### Goal
Implement the pre-approval mechanism for sensitive actions as specified in the requirements.

### Independent Test Criteria
Sensitive actions (like sending emails) generate files in `/Pending_Approval` first, and execution only occurs when moved to `/Approved`.

### Tasks

- [ ] T031 [P] Create approval request skill `skills/approval_request_skill.py` for sensitive actions
- [ ] T032 [P] Enhance file system watcher to monitor `/Pending_Approval` and `/Approved` directories
- [ ] T033 Implement approval entity model and tracking in the system
- [ ] T034 Add logic to detect when files are moved from `/Pending_Approval` to `/Approved`
- [ ] T035 Implement execution of approved actions after file movement is detected
- [ ] T036 Add logging and notifications for approval workflow

---

## Phase 7: Orchestration Update

### Goal
Update the main application to run both filesystem watcher and gmail watcher simultaneously.

### Independent Test Criteria
Both watchers run concurrently without interfering with each other.

### Tasks

- [ ] T037 Update `main.py` to use threading to run `filesystem_watcher.py` and `gmail_watcher.py` simultaneously
- [ ] T038 Implement proper thread management and cleanup
- [ ] T039 Add graceful shutdown handling for both threads
- [ ] T040 Add monitoring to ensure both threads are running properly
- [ ] T041 Update configuration to allow independent control of both watchers

---

## Phase 8: Polish & Cross-Cutting Concerns

### Goal
Complete the implementation with proper error handling, logging, and documentation.

### Independent Test Criteria
The system is robust, well-documented, and handles edge cases appropriately.

### Tasks

- [ ] T042 [P] Add comprehensive error handling throughout the application
- [ ] T043 [P] Improve logging with appropriate levels and structured format
- [ ] T044 [P] Add input validation for all user-facing components
- [ ] T045 [P] Write comprehensive documentation for installation and usage
- [ ] T046 [P] Add unit tests for critical components
- [ ] T047 [P] Perform integration testing of the complete workflow
- [ ] T048 [P] Optimize performance based on observed usage patterns
- [ ] T049 [P] Add monitoring and alerting for critical failures
- [ ] T050 [P] Prepare release notes and deployment instructions