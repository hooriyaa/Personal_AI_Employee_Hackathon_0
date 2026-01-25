# Implementation Plan: Local-First AI Employee (Bronze Tier)

**Branch**: `1-local-first-ai-employee` | **Date**: 2026-01-25 | **Spec**: [Local-First AI Employee Spec](./spec.md)
**Input**: Feature specification from `/specs/1-local-first-ai-employee/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build the Minimum Viable Deliverable (MVD) for the Personal AI Employee. Focus on establishing the Local-First Architecture, Folder Structure, and basic File System monitoring. The system will consist of an Obsidian Vault with specific folder structure, a Python-based filesystem watcher that monitors the Inbox folder, and basic agent skills to process files and update the dashboard. Based on the research, we'll use Python 3.11 with the watchdog library for file monitoring and PyYAML for metadata parsing.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: watchdog (for filesystem monitoring), PyYAML (for YAML parsing), pathlib (for path operations)
**Storage**: File-based (Obsidian Vault structure)
**Testing**: pytest for unit and integration tests
**Target Platform**: Cross-platform (Windows, Mac, Linux) - local only
**Project Type**: Single project with local file system integration
**Performance Goals**: Process files within 5 seconds of detection; handle files up to 100MB
**Constraints**: Local-only operation (no internet connectivity required); portable across different machines using relative paths
**Scale/Scope**: Single user, single vault, up to 1000 files per month

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Privacy is Absolute: System operates locally with no data uploaded to external servers
- ✅ The Vault is Truth: All plans, logs, and statuses stored as Markdown files in the vault
- ✅ Human Authority: System follows predefined rules without requiring real-time human approval for basic file operations
- ✅ The "Ralph Wiggum" Standard: System will include validation steps to ensure completion
- ✅ Folder Architecture: System implements the required folder structure (/Inbox, /Needs_Action, /Done, /Logs)
- ✅ Security & Privacy: No sensitive data handled beyond user's own files in their vault

## Project Structure

### Documentation (this feature)

```text
specs/1-local-first-ai-employee/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command output)
├── data-model.md        # Phase 1 output (/sp.plan command output)
├── quickstart.md        # Phase 1 output (/sp.plan command output)
├── contracts/           # Phase 1 output (/sp.plan command output)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── filesystem_watcher.py    # Main file system monitoring script
├── skills/                  # Agent skill implementations
│   ├── __init__.py
│   ├── vault_read_skill.py
│   ├── vault_write_skill.py
│   └── task_completion_skill.py
├── utils/                   # Utility functions
│   ├── __init__.py
│   └── file_operations.py
└── config.py                # Configuration settings

tests/
├── unit/
│   ├── test_filesystem_watcher.py
│   └── test_skills/
│       ├── test_vault_read_skill.py
│       ├── test_vault_write_skill.py
│       └── test_task_completion_skill.py
├── integration/
│   └── test_end_to_end.py
└── fixtures/
    └── mock_vault/
        ├── Inbox/
        ├── Needs_Action/
        ├── Done/
        └── Logs/
```

**Structure Decision**: Single project structure chosen to keep all components in one place while maintaining clear separation of concerns between the filesystem watcher, agent skills, and utility functions. The implementation will follow the three-phase approach outlined in the user requirements: Environment Setup, Perception Layer, and Reasoning Layer.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Implementation Phases

### Phase 1: Environment Setup
- Task: Create the Obsidian Vault directory structure (`/Inbox`, `/Needs_Action`, `/Done`, etc.).
- Task: Verify Python environment and install `watchdog` library.
- Validation Step: Confirm all required directories exist and Python dependencies are installed.

### Phase 2: Perception Layer (The Watcher)
- Task: Implement `filesystem_watcher.py` with the robust logic we defined (file size polling for write completion, timestamp naming for duplicates).
- Task: Test the watcher manually by dropping dummy files.
- Validation Step: Verify that files are detected, fully written check passes, and files are moved to the correct location with appropriate metadata files created.

### Phase 3: Reasoning Layer (The Brain)
- Task: Create `Vault_Read_Skill` (to read the .md trigger).
- Task: Create `Vault_Write_Skill` (to update Dashboard.md).
- Task: Create `Task_Completion_Skill` (to move files to `/Done`).
- Validation Step: Verify that the skills can read from the vault, write updates to the dashboard, and move processed files to the Done folder.
