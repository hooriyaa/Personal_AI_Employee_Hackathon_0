---
id: 4
title: Generate Tasks for Local First AI Employee
stage: tasks
date: 2026-01-25
surface: agent
model: Qwen
feature: local-first-ai-employee
branch: 1-local-first-ai-employee
user: PMLS
command: /sp.tasks
labels: ["tasks", "ai-employee", "local-first", "implementation"]
links:
  spec: ../spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-local-first-ai-employee/tasks.md
tests:
 - none
---

## Prompt

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (API endpoints), research.md (decisions), quickstart.md (test scenarios)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
   - If data-model.md exists: Extract entities and map to user stories
   - If contracts/ exists: Map endpoints to user stories
   - If research.md exists: Extract decisions for setup tasks
   - Generate tasks organized by user story (see Task Generation Rules below)
   - Generate dependency graph showing user story completion order
   - Create parallel execution examples per user story
   - Validate task completeness (each user story has all needed tasks, independently testable)

4. **Generate tasks.md**: Use `.specify/templates/tasks-template.md` as structure, fill with:
   - Correct feature name from plan.md
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories)
   - Phase 3+: One phase per user story (in priority order from spec.md)
   - Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks
   - Final Phase: Polish & cross-cutting concerns
   - All tasks must follow the strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - Dependencies section showing story completion order
   - Parallel execution examples per story
   - Implementation strategy section (MVP first, incremental delivery)

5. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per user story
   - Parallel opportunities identified
   - Independent test criteria for each story
   - Suggested MVP scope (typically just User Story 1)
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)

Context for task generation: Based on the approved Implementation Plan for Bronze Tier, please generate the detailed Task List. Ensure the tasks are granular and sequential. We want to execute them in this order: 1. **Task-001 [Environment]:** Create the specific directory structure and install the `watchdog` library. 2. **Task-002 [Perception]:** Develop the `filesystem_watcher.py` script with the robust file-size polling logic. 3. **Task-003 [Skills]:** Generate the Agent Skills (`Vault_Read`, `Vault_Write`, `Task_Completion`) as Markdown files. Ready to approve tasks immediately after generation.

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Response snapshot

I'll generate the task list based on the design artifacts we've created. First, let me run the prerequisites check to get the feature directory and available documents.

```
powershell -ExecutionPolicy Bypass -File ".specify/scripts/powershell/check-prerequisites.ps1" -Json
```

Now I'll read the required documents to generate the tasks:

```
.type specs/1-local-first-ai-employee/plan.md
```

Now I'll read the spec file to understand the user stories and requirements:

```
.type specs/1-local-first-ai-employee/spec.md
```

Now I'll read the data model to understand the entities:

```
.type specs/1-local-first-ai-employee/data-model.md
```

Now I'll read the contracts to understand the API specifications:

```
.type specs/1-local-first-ai-employee/contracts/skills-contract.md
```

Now I'll read the quickstart guide to understand the implementation details:

```
.type specs/1-local-first-ai-employee/quickstart.md
```

Now I'll create the tasks.md file based on all the design artifacts:

```
.write specs/1-local-first-ai-employee/tasks.md
```

## Outcome

- ✅ Impact: Created comprehensive task list for Local-First AI Employee implementation
- 🧪 Tests: none
- 📁 Files: specs/1-local-first-ai-employee/tasks.md
- 🔁 Next prompts: /sp.implement to start implementation
- 🧠 Reflection: Successfully created a detailed task list organized by user stories with proper dependencies and parallelization opportunities

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A