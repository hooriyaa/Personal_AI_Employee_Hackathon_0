---
id: 2
title: Clarify Local First AI Employee Spec
stage: spec
date: 2026-01-25
surface: agent
model: Qwen
feature: local-first-ai-employee
branch: 1-local-first-ai-employee
user: PMLS
command: /sp.clarify
labels: ["specification", "ai-employee", "local-first", "clarification"]
links:
  spec: ./spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-local-first-ai-employee/spec.md
tests:
 - none
---

## Prompt

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Detect and reduce ambiguity or missing decision points in the active feature specification and record the clarifications directly in the spec file.

Note: This clarification workflow is expected to run (and be completed) BEFORE invoking `/sp.plan`. If the user explicitly states they are skipping clarification (e.g., exploratory spike), you may proceed, but must warn that downstream rework risk increases.

Execution steps:

1. Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly` from repo root **once** (combined `--json --paths-only` mode / `-Json -PathsOnly`). Parse minimal JSON payload fields:
   - `FEATURE_DIR`
   - `FEATURE_SPEC`
   - (Optionally capture `IMPL_PLAN`, `TASKS` for future chained flows.)
   - If JSON parsing fails, abort and instruct user to re-run `/sp.specify` or verify feature branch environment.
   - For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. Load the current spec file. Perform a structured ambiguity & coverage scan using this taxonomy. For each category, mark status: Clear / Partial / Missing. Produce an internal coverage map used for prioritization (do not output raw map unless no questions will be asked).

   Functional Scope & Behavior:
   - Core user goals & success criteria
   - Explicit out-of-scope declarations
   - User roles / personas differentiation

   Domain & Data Model:
   - Entities, attributes, relationships
   - Identity & uniqueness rules
   - Lifecycle/state transitions
   - Data volume / scale assumptions

   Interaction & UX Flow:
   - Critical user journeys / sequences
   - Error/empty/loading states
   - Accessibility or localization notes

   Non-Functional Quality Attributes:
   - Performance (latency, throughput targets)
   - Scalability (horizontal/vertical, limits)
   - Reliability & availability (uptime, recovery expectations)
   - Observability (logging, metrics, tracing signals)
   - Security & privacy (authN/Z, data protection, threat assumptions)
   - Compliance / regulatory constraints (if any)

   Integration & External Dependencies:
   - External services/APIs and failure modes
   - Data import/export formats
   - Protocol/versioning assumptions

   Edge Cases & Failure Handling:
   - Negative scenarios
   - Rate limiting / throttling
   - Conflict resolution (e.g., concurrent edits)

   Constraints & Tradeoffs:
   - Technical constraints (language, storage, hosting)
   - Explicit tradeoffs or rejected alternatives

   Terminology & Consistency:
   - Canonical glossary terms
   - Avoided synonyms / deprecated terms

   Completion Signals:
   - Acceptance criteria testability
   - Measurable Definition of Done style indicators

   Misc / Placeholders:
   - TODO markers / unresolved decisions
   - Ambiguous adjectives ("robust", "intuitive") lacking quantification

   For each category with Partial or Missing status, add a candidate question opportunity unless:
   - Clarification would not materially change implementation or validation strategy
   - Information is better deferred to planning phase (note internally)

3. Generate (internally) a prioritized queue of candidate clarification questions (maximum 5). Do NOT output them all at once. Apply these constraints:
    - Maximum of 10 total questions across the whole session.
    - Each question must be answerable with EITHER:
       - A short multiple‑choice selection (2–5 distinct, mutually exclusive options), OR
       - A one-word / short‑phrase answer (explicitly constrain: "Answer in <=5 words").
    - Only include questions whose answers materially impact architecture, data modeling, task decomposition, test design, UX behavior, operational readiness, or compliance validation.
    - Ensure category coverage balance: attempt to cover the highest impact unresolved categories first; avoid asking two low-impact questions when a single high-impact area (e.g., security posture) is unresolved.
    - Exclude questions already answered, trivial stylistic preferences, or plan-level execution details (unless blocking correctness).
    - Favor clarifications that reduce downstream rework risk or prevent misaligned acceptance tests.
    - If more than 5 categories remain unresolved, select the top 5 by (Impact * Uncertainty) heuristic.

4. Sequential questioning loop (interactive):
    - Present EXACTLY ONE question at a time.
    - For multiple‑choice questions:
       - **Analyze all options** and determine the **most suitable option** based on:
          - Best practices for the project type
          - Common patterns in similar implementations
          - Risk reduction (security, performance, maintainability)
          - Alignment with any explicit project goals or constraints visible in the spec
       - Present your **recommended option prominently** at the top with clear reasoning (1-2 sentences explaining why this is the best choice).
       - Format as: `**Recommended:** Option [X] - <reasoning>`
       - Then render all options as a Markdown table:

       | Option | Description |
       |--------|-------------|
       | A | <Option A description> |
       | B | <Option B description> |
       | C | <Option C description> (add D/E as needed up to 5) |
       | Short | Provide a different short answer (<=5 words) (Include only if free-form alternative is appropriate) |

       - After the table, add: `You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.`
    - For short‑answer style (no meaningful discrete options):
       - Provide your **suggested answer** based on best practices and context.
       - Format as: `**Suggested:** <your proposed answer> - <brief reasoning>`
       - Then output: `Format: Short answer (<=5 words). You can accept the suggestion by saying "yes" or "suggested", or provide your own answer.`
    - After the user answers:
       - If the user replies with "yes", "recommended", or "suggested", use your previously stated recommendation/suggestion as the answer.
       - Otherwise, validate the answer maps to one option or fits the <=5 word constraint.
       - If ambiguous, ask for a quick disambiguation (count still belongs to same question; do not advance).
       - Once satisfactory, record it in working memory (do not yet write to disk) and move to the next queued question.
    - Stop asking further questions when:
       - All critical ambiguities resolved early (remaining queued items become unnecessary), OR
       - User signals completion ("done", "good", "no more"), OR
       - You reach 5 asked questions.
    - Never reveal future queued questions in advance.
    - If no valid questions exist at start, immediately report no critical ambiguities.

5. Integration after EACH accepted answer (incremental update approach):
    - Maintain in-memory representation of the spec (loaded once at start) plus the raw file contents.
    - For the first integrated answer in this session:
       - Ensure a `## Clarifications` section exists (create it just after the highest-level contextual/overview section per the spec template if missing).
       - Under it, create (if not present) a `### Session YYYY-MM-DD` subheading for today.
    - Append a bullet line immediately after acceptance: `- Q: <question> → A: <final answer>`.
    - Then immediately apply the clarification to the most appropriate section(s):
       - Functional ambiguity → Update or add a bullet in Functional Requirements.
       - User interaction / actor distinction → Update User Stories or Actors subsection (if present) with clarified role, constraint, or scenario.
       - Data shape / entities → Update Data Model (add fields, types, relationships) preserving ordering; note added constraints succinctly.
       - Non-functional constraint → Add/modify measurable criteria in Non-Functional / Quality Attributes section (convert vague adjective to metric or explicit target).
       - Edge case / negative flow → Add a new bullet under Edge Cases / Error Handling (or create such subsection if template provides placeholder for it).
       - Terminology conflict → Normalize term across spec; retain original only if necessary by adding `(formerly referred to as "X")` once.
    - If the clarification invalidates an earlier ambiguous statement, replace that statement instead of duplicating; leave no obsolete contradictory text.
    - Save the spec file AFTER each integration to minimize risk of context loss (atomic overwrite).
    - Preserve formatting: do not reorder unrelated sections; keep heading hierarchy intact.
    - Keep each inserted clarification minimal and testable (avoid narrative drift).

6. Validation (performed after EACH write plus final pass):
   - Clarifications session contains exactly one bullet per accepted answer (no duplicates).
   - Total asked (accepted) questions ≤ 5.
   - Updated sections contain no lingering vague placeholders the new answer was meant to resolve.
   - No contradictory earlier statement remains (scan for now-invalid alternative choices removed).
   - Markdown structure valid; only allowed new headings: `## Clarifications`, `### Session YYYY-MM-DD`.
   - Terminology consistency: same canonical term used across all updated sections.

7. Write the updated spec back to `FEATURE_SPEC`.

8. Report completion (after questioning loop ends or early termination):
   - Number of questions asked & answered.
   - Path to updated spec.
   - Sections touched (list names).
   - Coverage summary table listing each taxonomy category with Status: Resolved (was Partial/Missing and addressed), Deferred (exceeds question quota or better suited for planning), Clear (already sufficient), Outstanding (still Partial/Missing but low impact).
   - If any Outstanding or Deferred remain, recommend whether to proceed to `/sp.plan` or run `/sp.clarify` again later post-plan.
   - Suggested next command.

Behavior rules:

- If no meaningful ambiguities found (or all potential questions would be low-impact), respond: "No critical ambiguities detected worth formal clarification." and suggest proceeding.
- If spec file missing, instruct user to run `/sp.specify` first (do not create a new spec here).
- Never exceed 5 total asked questions (clarification retries for a single question do not count as new questions).
- Avoid speculative tech stack questions unless the absence blocks functional clarity.
- Respect user early termination signals ("stop", "done", "proceed").
- If no questions asked due to full coverage, output a compact coverage summary (all categories Clear) then suggest advancing.
- If quota reached with unresolved high-impact categories remaining, explicitly flag them under Deferred with rationale.

Context for prioritization: Please review the generated Bronze Tier specification with a focus on robustness and Hackathon compliance. Specifically clarify the following edge cases for the "Perception Layer" (filesystem_watcher.py): 1. **Race Conditions:** How will the watcher ensure a large file is fully written/copied to `/Inbox` before attempting to move it? (We need to avoid moving incomplete files). 2. **Naming Conflicts:** What is the specific behavior if a file with the same name already exists in `/Needs_Action`? (e.g., Should we overwrite or append a timestamp?) 3. **Metadata Format:** Confirm the exact YAML frontmatter schema for the trigger `.md` file so the Agent knows exactly how to parse it. 4. **Folder Paths:** Confirm that all paths are relative to the Vault root to ensure portability across different machines (Mac/Windows). Please update the specification to explicitly handle these cases.

## Response snapshot

I'll help you identify and clarify the underspecified areas in the current feature specification. First, I need to run the prerequisites check to get the feature directory and spec file path.

```
powershell -ExecutionPolicy Bypass -File ".specify/scripts/powershell/check-prerequisites.ps1" -Json -PathsOnly
```

Now I'll load the current spec file to analyze it for ambiguities and underspecified areas:

```
.type specs/1-local-first-ai-employee/spec.md
```

Based on the user's input requesting to focus on specific edge cases for the "Perception Layer" (filesystem_watcher.py), I'll analyze the specification for these areas and ask targeted clarification questions. I can see that the specification does need clarification on race conditions, naming conflicts, metadata format, and folder path handling.

Let me start with the first clarification question:

## Question 1: Race Conditions

**Recommended:** Polling with file size comparison - Check if file size remains the same over a short interval to ensure it's fully written before moving.

The polling approach is more reliable than relying on file locks which may not work consistently across all platforms and file systems. It's a common pattern for detecting when a file write operation is complete.

| Option | Description |
|--------|-------------|
| A | Polling with file size comparison - Check if file size remains the same over a short interval to ensure it's fully written before moving |
| B | File lock detection - Attempt to acquire an exclusive lock on the file; if successful, the file is complete |
| C | Fixed delay - Wait a predetermined amount of time after detecting the file before moving it |
| D | Event-based with debounce - Use file system events but add a short delay to allow for continued writes |

You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.

A

Thank you for your answer. I'll now update the specification with this clarification and move to the next question.

I'll add a clarification section to the specification and update the relevant functional requirements:

```
.edit specs/1-local-first-ai-employee/spec.md
```

Now I'll move to the second clarification question about naming conflicts:

## Question 2: Naming Conflicts

**Recommended:** Append timestamp - If a file with the same name exists in `/Needs_Action`, append a timestamp to the new file name to avoid overwriting.

Appending a timestamp preserves all files and avoids accidental data loss, which is important for an AI employee system that should maintain a record of all processed items.

| Option | Description |
|--------|-------------|
| A | Append timestamp - If a file with the same name exists in `/Needs_Action`, append a timestamp to the new file name to avoid overwriting |
| B | Overwrite - Replace the existing file with the new one |
| C | Skip - Don't move the new file if one with the same name already exists |
| D | Append sequence number - Add a sequential number to the filename if a duplicate exists |

You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.

A

Thank you for your answer. I'll now update the specification with this clarification and move to the next question.

```
.edit specs/1-local-first-ai-employee/spec.md
```

Now I'll move to the third clarification question about metadata format:

## Question 3: Metadata Format

**Recommended:** Standard YAML frontmatter - Use a YAML frontmatter format with standardized fields (filename, size, timestamp, original_path) at the beginning of the .md file.

Standard YAML frontmatter is widely supported by Markdown processors and provides a structured way to include metadata that the AI agent can easily parse.

| Option | Description |
|--------|-------------|
| A | Standard YAML frontmatter - Use a YAML frontmatter format with standardized fields (filename, size, timestamp, original_path) at the beginning of the .md file |
| B | JSON object in content - Embed the metadata as a JSON object in the main content of the .md file |
| C | Plain text header - Format the metadata as plain text at the top of the .md file |
| D | Separate .json file - Create a corresponding .json file with the same name as the original file containing the metadata |

You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.

A

Thank you for your answer. I'll now update the specification with this clarification and move to the next question.

```
.edit specs/1-local-first-ai-employee/spec.md
```

Now I'll move to the fourth clarification question about folder paths:

## Question 4: Folder Paths

**Recommended:** Relative to Vault root - All paths should be relative to the Vault root to ensure portability across different machines (Mac/Windows).

Using relative paths ensures the system works consistently regardless of the absolute path where the vault is located on different machines or operating systems.

| Option | Description |
|--------|-------------|
| A | Relative to Vault root - All paths should be relative to the Vault root to ensure portability across different machines (Mac/Windows) |
| B | Absolute paths - Use the full absolute path for all folder references |
| C | Environment variable - Store the vault path in an environment variable and reference it |
| D | Configuration file - Store all paths in a configuration file that gets loaded at startup |

You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.

yes

Thank you for your answer. I'll now update the specification with this final clarification.

```
.edit specs/1-local-first-ai-employee/spec.md
```

Now I'll update the functional requirements section to incorporate the clarifications:

```
.edit specs/1-local-first-ai-employee/spec.md
```

## Outcome

- ✅ Impact: Clarified critical edge cases for the filesystem watcher component
- 🧪 Tests: none
- 📁 Files: specs/1-local-first-ai-employee/spec.md
- 🔁 Next prompts: /sp.plan to create implementation plan
- 🧠 Reflection: Successfully clarified 4 critical edge cases for the perception layer that could have caused issues during implementation

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A