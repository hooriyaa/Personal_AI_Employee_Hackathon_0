---
id: 3
title: Plan Local First AI Employee
stage: plan
date: 2026-01-25
surface: agent
model: Qwen
feature: local-first-ai-employee
branch: 1-local-first-ai-employee
user: PMLS
command: /sp.plan
labels: ["planning", "ai-employee", "local-first", "implementation"]
links:
  spec: ../spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-local-first-ai-employee/plan.md
 - specs/1-local-first-ai-employee/research.md
 - specs/1-local-first-ai-employee/data-model.md
 - specs/1-local-first-ai-employee/quickstart.md
 - specs/1-local-first-ai-employee/contracts/skills-contract.md
tests:
 - none
---

## Prompt

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `.specify/scripts/powershell/setup-plan.ps1 -Json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `.specify/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update**:
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType qwen`
   - These scripts detect which AI agent is in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications

---

/sp.plan Based on the clarified Bronze Tier specification, generate a detailed Implementation Plan.

Please break the work down into these 3 phases:

1.  **Phase 1: Environment Setup**
    - Task: Create the Obsidian Vault directory structure (`/Inbox`, `/Needs_Action`, `/Done`, etc.).
    - Task: Verify Python environment and install `watchdog` library.

2.  **Phase 2: Perception Layer (The Watcher)**
    - Task: Implement `filesystem_watcher.py` with the robust logic we defined (file size polling for write completion, timestamp naming for duplicates).
    - Task: Test the watcher manually by dropping dummy files.

3.  **Phase 3: Reasoning Layer (The Brain)**
    - Task: Create `Vault_Read_Skill` (to read the .md trigger).
    - Task: Create `Vault_Write_Skill` (to update Dashboard.md).
    - Task: Create `Task_Completion_Skill` (to move files to `/Done`).

Ensure the plan includes a "Validation Step" for each phase to ensure we meet the Hackathon Bronze criteria.

## Response snapshot

I'll execute the implementation planning workflow for the Local-First AI Employee feature. Let me start by running the setup script to get the necessary paths.

```
powershell -ExecutionPolicy Bypass -File ".specify/scripts/powershell/setup-plan.ps1" -Json
```

Now I'll read the feature specification and the constitution to understand the context:

```
.type specs/1-local-first-ai-employee/spec.md
```

Now let me read the constitution to understand the governing principles:

```
.type .specify/memory/constitution.md
```

Now let me read the implementation plan template that was copied:

```
.type specs/1-local-first-ai-employee/plan.md
```

Now I'll create the research.md file as part of Phase 0:

```
.write specs/1-local-first-ai-employee/research.md
```

Now I'll create the data-model.md file as part of Phase 1:

```
.write specs/1-local-first-ai-employee/data-model.md
```

Now I'll create the quickstart.md file as part of Phase 1:

```
.write specs/1-local-first-ai-employee/quickstart.md
```

Now I'll create a basic contract file:

```
.write specs/1-local-first-ai-employee/contracts/skills-contract.md
```

Now I'll update the implementation plan with all the details from the research and design phases:

```
.edit specs/1-local-first-ai-employee/plan.md
```

## Outcome

- ✅ Impact: Created comprehensive implementation plan with research, data model, quickstart guide, and contracts
- 🧪 Tests: none
- 📁 Files: specs/1-local-first-ai-employee/plan.md, specs/1-local-first-ai-employee/research.md, specs/1-local-first-ai-employee/data-model.md, specs/1-local-first-ai-employee/quickstart.md, specs/1-local-first-ai-employee/contracts/skills-contract.md
- 🔁 Next prompts: /sp.tasks to break the plan into tasks
- 🧠 Reflection: Successfully created a detailed implementation plan that addresses all three phases requested by the user

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A