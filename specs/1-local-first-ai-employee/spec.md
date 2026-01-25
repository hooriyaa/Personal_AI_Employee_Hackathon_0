# Feature Specification: Local-First AI Employee (Bronze Tier)

**Feature Branch**: `1-local-first-ai-employee`
**Created**: 2026-01-25
**Status**: Draft
**Input**: User description: "Build the Minimum Viable Deliverable (MVD) for the Personal AI Employee. Focus: Establish the Local-First Architecture, Folder Structure, and basic File System monitoring."

## Clarifications
### Session 2026-01-25
- Q: How will the watcher ensure a large file is fully written/copied to `/Inbox` before attempting to move it? → A: Polling with file size comparison - Check if file size remains the same over a short interval to ensure it's fully written before moving
- Q: What is the specific behavior if a file with the same name already exists in `/Needs_Action`? → A: Append timestamp - If a file with the same name exists in `/Needs_Action`, append a timestamp to the new file name to avoid overwriting
- Q: What is the exact format for the metadata trigger .md file? → A: Standard YAML frontmatter - Use a YAML frontmatter format with standardized fields (filename, size, timestamp, original_path) at the beginning of the .md file
- Q: Should all paths be relative to the Vault root for portability? → A: Relative to Vault root - All paths should be relative to the Vault root to ensure portability across different machines (Mac/Windows)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - File Drop Processing (Priority: P1)

As a user, I want to drop files into an Inbox folder so that the AI employee can automatically process them without requiring my constant attention.

**Why this priority**: This is the core functionality that enables the AI employee to operate autonomously and respond to user requests.

**Independent Test**: A user drops a file into the `/Inbox` folder, and the system automatically moves it to `/Needs_Action` with a metadata trigger file created.

**Acceptance Scenarios**:

1. **Given** a file is dropped into `/Inbox`, **When** the filesystem watcher detects the new file, **Then** the file is moved to `/Needs_Action` and a metadata trigger file is created
2. **Given** a file exists in `/Inbox`, **When** the file write operation completes, **Then** the system waits for write completion before moving the file

---

### User Story 2 - Status Tracking (Priority: P2)

As a user, I want to track the status of my files through a dashboard so that I can monitor what the AI employee is working on.

**Why this priority**: This provides visibility into the AI employee's activities and helps users understand the system's progress.

**Independent Test**: The AI employee updates the `Dashboard.md` file to reflect the current status of tasks.

**Acceptance Scenarios**:

1. **Given** a file is processed by the AI employee, **When** the processing is complete, **Then** the dashboard is updated to reflect the task completion

---

### User Story 3 - Task Lifecycle Management (Priority: P3)

As a user, I want processed files to be archived so that I can distinguish between pending and completed tasks.

**Why this priority**: This provides a clean separation between active tasks and completed work, helping maintain an organized workspace.

**Independent Test**: Files that have been processed by the AI employee are moved from `/Needs_Action` to `/Done`.

**Acceptance Scenarios**:

1. **Given** a file has been processed in `/Needs_Action`, **When** the AI employee marks it as complete, **Then** the file is moved to `/Done`

---

### Edge Cases

- What happens when a file is dropped into `/Inbox` while the system is down?
- How does the system handle extremely large files that might take a long time to process?
- What happens if the `/Needs_Action` folder becomes full or reaches storage limits?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST monitor the `/Inbox` folder for new file drops
- **FR-002**: System MUST wait for file write operations to complete before processing using polling with file size comparison to ensure the file is fully written
- **FR-003**: System MUST move files from `/Inbox` to `/Needs_Action` when detected
- **FR-004**: System MUST create a metadata trigger file (.md) in `/Needs_Action` for each moved file
- **FR-005**: Metadata trigger files MUST contain file name, size, and timestamp in YAML frontmatter format
- **FR-006**: System MUST update `Dashboard.md` to reflect task status changes
- **FR-007**: System MUST move processed files from `/Needs_Action` to `/Done`
- **FR-008**: System MUST store logs in the `/Logs` folder for audit purposes
- **FR-009**: System MUST operate locally without requiring internet connectivity
- **FR-010**: System MUST read and interpret Markdown files from the Obsidian Vault
- **FR-011**: When moving files to `/Needs_Action`, if a file with the same name exists, append a timestamp to the new file name to avoid overwriting
- **FR-012**: All file paths MUST be relative to the Vault root to ensure portability across different machines and operating systems

### Key Entities

- **File**: Represents a document dropped into the system, characterized by name, size, timestamp, and content
- **Task**: Represents a file that requires processing, with status (pending, in-progress, completed)
- **Metadata Trigger**: A Markdown file containing information about a file that needs processing
- **Dashboard**: A central status tracker showing the current state of tasks and system health

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can drop a file into `/Inbox` and see it appear in `/Needs_Action` within 5 seconds
- **SC-002**: 100% of files dropped into `/Inbox` are successfully moved to `/Needs_Action` with metadata triggers created
- **SC-003**: Dashboard updates accurately reflect the status of all tasks in the system
- **SC-004**: System operates reliably for 24 hours without manual intervention