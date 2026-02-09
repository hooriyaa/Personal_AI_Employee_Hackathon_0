# Implementation Plan: Real LinkedIn Posting via Selenium

**Branch**: `003-linkedin-selenium-post` | **Date**: 2026-02-09 | **Spec**: [link](./spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan implements real LinkedIn posting functionality using Selenium WebDriver to replace the current simulated logging in the action runner. The implementation will add selenium and webdriver-manager to the project dependencies, create a LinkedIn poster module that automates the posting process while maintaining human oversight, and update the action runner to use this new functionality. The solution includes proper error handling and respects the Human-in-the-Loop safety mechanism by not automatically clicking the final "Post" button.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Privacy is Absolute**: The LinkedIn automation must not upload sensitive client data unnecessarily. The content being posted will be limited to what was approved in the `/Pending_Approval` directory.
2. **The Vault is Truth**: All generated plans and logs will continue to be stored as Markdown files in the designated directories.
3. **Human Authority**: The automation will maintain human oversight by stopping before the final "Post" action, requiring manual confirmation (Human-in-the-Loop safety).
4. **The "Ralph Wiggum" Standard**: The implementation will include proper error handling and validation to ensure complete and correct responses.
5. **Secrets Management**: No LinkedIn credentials will be stored in code, only relying on the user's existing browser session.
6. **Data Sanitation**: The automation will only use content that was previously approved through the `/Pending_Approval` → `/Approved` workflow.
7. **Human-in-the-Loop (HITL) Workflow**: The implementation respects the safety mechanism by NOT automatically clicking the final "Post" button, requiring human approval before publishing.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
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
├── models/
├── services/
├── cli/
├── config/
├── utils/
├── gmail/
├── filesystem/
├── linkedin/            # New directory for LinkedIn automation
│   └── poster.py        # Module for LinkedIn posting via Selenium
└── action_runner.py     # Updated to use Selenium for LinkedIn posts

skills/
├── plan_generation_skill.py
└── [other skills]

tests/
├── contract/
├── integration/
└── unit/

requirements.txt          # Updated with selenium and webdriver-manager
main.py                   # Entry point
```

**Structure Decision**: Single project structure selected as this is a modular AI employee system where the LinkedIn automation enhances existing functionality without requiring separate services or platforms. The new src/linkedin/ directory will contain the Selenium automation logic.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
