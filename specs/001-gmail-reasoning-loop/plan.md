# Implementation Plan: Gmail Reasoning Loop

**Branch**: `001-gmail-reasoning-loop` | **Date**: 2026-01-25 | **Spec**: [link to spec]
**Input**: Feature specification from `/specs/001-gmail-reasoning-loop/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a Gmail Reasoning Loop that monitors Gmail for URGENT/IMPORTANT emails, converts them to Markdown files in `/Needs_Action`, generates plans in `/Plans`, and implements a pre-approval mechanism for sensitive actions. The system will poll Gmail API every 60-120 seconds with secure credential handling.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: google-api-python-client, google-auth-httplib2, google-auth-oauthlib, watchdog
**Storage**: File-based (Markdown files in designated directories)
**Testing**: pytest
**Target Platform**: Cross-platform (Windows, Mac, Linux)
**Project Type**: Desktop application with file system integration
**Performance Goals**: Process emails within 5 minutes of arrival, handle 1000+ emails per day
**Constraints**: Must respect Gmail API rate limits (poll every 60-120 seconds), secure credential handling
**Scale/Scope**: Single-user system, up to 100 emails per day

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

All requirements align with the project constitution. The system will be local-first with secure credential handling and human-in-the-loop safety mechanisms.

## Project Structure

### Documentation (this feature)

```text
specs/001-gmail-reasoning-loop/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── gmail/
│   ├── __init__.py
│   ├── gmail_watcher.py      # Gmail API polling and email processing
│   ├── auth.py               # Authentication with Gmail API
│   └── email_processor.py    # Convert emails to Markdown
├── reasoning/
│   ├── __init__.py
│   ├── planner.py            # Plan generation logic
│   └── approval_handler.py   # Handle pre-approval mechanism
├── filesystem/
│   ├── __init__.py
│   └── watcher.py            # File system monitoring
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration management
└── utils/
    ├── __init__.py
    └── helpers.py            # Utility functions

skills/
├── plan_generation_skill.py     # Skill to generate plans
└── approval_request_skill.py    # Skill to request approvals

secrets/                        # Secure storage for credentials (in .gitignore)
├── credentials.json
└── token.json

tests/
├── unit/
│   ├── gmail/
│   ├── reasoning/
│   └── filesystem/
├── integration/
│   └── end_to_end_tests.py
└── fixtures/
    └── sample_emails.json
```

**Structure Decision**: Single project structure with modular organization by functionality (gmail, reasoning, filesystem). Credentials are stored securely in a dedicated secrets directory that's git-ignored.

## Phase 0: Outline & Research

### Research Tasks

1. **Gmail API Authentication Research**
   - Decision: Use OAuth 2.0 with service account or user credentials
   - Rationale: OAuth 2.0 is the standard and secure way to access Gmail API
   - Alternatives considered: Basic authentication (deprecated), API keys (insufficient for Gmail)

2. **Rate Limiting Research**
   - Decision: Implement 60-120 second polling intervals
   - Rationale: Gmail API has daily quotas and per-user rate limits
   - Alternatives considered: Push notifications (more complex), shorter polling (risk of rate limits)

3. **File System Monitoring Research**
   - Decision: Use watchdog library for cross-platform file system monitoring
   - Rationale: Well-maintained, cross-platform, event-driven
   - Alternatives considered: Built-in os.stat polling (less efficient), platform-specific solutions

4. **Approval Mechanism Research**
   - Decision: File-based approval system with `/Pending_Approval` and `/Approved` directories
   - Rationale: Simple, transparent, allows human oversight without complex UI
   - Alternatives considered: Database tracking (overkill), email confirmations (circular issue)

## Phase 1: Design & Contracts

### Data Model

**EmailEntity**
- id: str (Gmail message ID)
- subject: str
- sender: str
- recipients: List[str]
- body: str
- labels: List[str]
- timestamp: datetime
- is_read: bool
- urgency_level: Enum('URGENT', 'IMPORTANT', 'NORMAL')

**TaskEntity**
- id: str (generated UUID)
- source_email_id: str (reference to EmailEntity.id)
- content: str (Markdown content)
- created_at: datetime
- status: Enum('NEW', 'PLANNED', 'APPROVED', 'COMPLETED')
- assigned_to: str (optional)

**PlanEntity**
- id: str (generated UUID)
- task_id: str (reference to TaskEntity.id)
- steps: List[str] (action steps as checklist)
- created_at: datetime
- status: Enum('DRAFT', 'APPROVED', 'EXECUTING', 'COMPLETED')

### API Contracts

**Gmail Service Interface**
```
GET /gmail/messages?label=URGENT&unread=true
Response: List[EmailEntity]

POST /gmail/mark-read/{message_id}
Response: Boolean

GET /gmail/token-status
Response: {valid: Boolean, expires_in: Int}
```

**File System Service Interface**
```
POST /files/move
Request: {source: String, destination: String}
Response: {success: Boolean, message: String}

GET /files/watch
Response: Stream of file system events
```

**Approval Service Interface**
```
POST /approvals/request
Request: {action: String, details: Object}
Response: {approval_id: String, status: String}

POST /approvals/{approval_id}/approve
Response: {success: Boolean}

GET /approvals/pending
Response: List[ApprovalEntity]
```

### Quickstart Guide

1. **Setup Credentials**
   - Navigate to Google Cloud Console
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop Application type)
   - Download credentials.json and place in `/secrets/` directory

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initial Run**
   ```bash
   python main.py
   ```
   - First run will initiate OAuth flow to generate token.json
   - System will begin monitoring Gmail and file system

4. **Directory Structure**
   - Ensure `/Inbox`, `/Needs_Action`, `/Plans`, `/Pending_Approval`, `/Approved`, `/Done` directories exist

## Phase 2: Implementation Plan

### Phase 1: Environment & Secrets
- Task: Create a `/secrets` folder and add it to `.gitignore`.
- Task: Install Google Client Library (`google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`).
- Task: Document the steps to get `credentials.json` from Google Cloud Console.

### Phase 2: Gmail Watcher (Perception)
- Task: Implement `gmail_watcher.py`.
- Logic: Authenticate -> Poll every 60s -> Find "UNREAD" & "URGENT" -> Save as Markdown in `/Needs_Action`.

### Phase 3: Reasoning & Approval Skills
- Task: Create `Plan_Generation_Skill` (reads task -> writes `Plan.md` in `/Plans`).
- Task: Create `Approval_Request_Skill` (writes sensitive actions to `/Pending_Approval`).

### Phase 4: Orchestration Update
- Task: Update `main.py` to run BOTH `filesystem_watcher.py` and `gmail_watcher.py` simultaneously (using threading or async).

## Validation Steps

1. **Gmail Connection Test**
   - Verify authentication works without sending emails
   - Test reading sample emails from test account
   - Confirm rate limiting is respected

2. **File System Integration Test**
   - Verify file movement between directories
   - Test plan generation from email files
   - Confirm approval workflow functions correctly

3. **End-to-End Test**
   - Simulate receiving an urgent email
   - Verify it gets converted to Markdown
   - Confirm plan generation and approval process
   - Test execution of approved actions

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple dependencies | Gmail API integration requires official client libraries | Building custom HTTP clients would be insecure and error-prone |
| File-based architecture | Aligns with local-first principle and existing vault structure | Database would add complexity without clear benefits for single-user system |