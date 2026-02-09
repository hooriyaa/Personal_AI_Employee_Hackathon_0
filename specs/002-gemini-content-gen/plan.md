# Implementation Plan: Dynamic AI Content Generation (Gemini)

**Branch**: `002-gemini-content-gen` | **Date**: 2026-02-08 | **Spec**: [link](./spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan integrates Google's Gemini API to replace static templates with AI-generated content for email replies and LinkedIn posts. The implementation will update the PlanGenerationSkill to use the Gemini API for generating contextually appropriate responses, while maintaining the existing file-based workflow and human approval process. The solution includes proper error handling with fallback messages and secure API key management.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: watchdog, PyYAML, pathlib, google-generativeai (to be added)
**Storage**: File-based (Markdown files in structured directories)
**Testing**: pytest (to be implemented)
**Target Platform**: Cross-platform (Windows, macOS, Linux)
**Project Type**: Single project with modular architecture
**Performance Goals**: <10 second response time for AI-generated content
**Constraints**: <200ms p95 for local operations, API rate limits for Gemini
**Scale/Scope**: Single user AI employee system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Privacy is Absolute**: The Gemini API integration must not upload sensitive client data unnecessarily. Only essential email content and LinkedIn post topics will be sent to the API.
2. **The Vault is Truth**: All generated plans and logs will continue to be stored as Markdown files in the designated directories.
3. **Human Authority**: The AI-generated content will be placed in the `/Pending_Approval` directory for human review before execution.
4. **The "Ralph Wiggum" Standard**: The implementation will include proper error handling and validation to ensure complete and correct responses.
5. **Secrets Management**: The GEMINI_API_KEY will be loaded from environment variables and never written to Markdown files or logs.
6. **Data Sanitation**: Any PII in email content will be preserved as-is since it's necessary for the context of the reply, but we won't store or log the API key.

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
│   └── entities.py      # TaskEntity, PlanEntity, PlanStep classes
├── services/
│   └── gemini_service.py # New service for Gemini API integration
├── gmail/
│   └── gmail_watcher.py
├── filesystem/
│   └── watcher.py
├── config/
│   └── settings.py
└── utils/
    └── helpers.py

skills/
├── plan_generation_skill.py  # Modified to use Gemini API
└── [other skills]

tests/
├── contract/
├── integration/
└── unit/

requirements.txt          # Updated with google-generativeai
main.py                   # Entry point
```

**Structure Decision**: Single project structure selected as this is a modular AI employee system where the Gemini integration enhances existing functionality without requiring separate services or platforms.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
