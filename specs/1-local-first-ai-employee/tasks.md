---

description: "Task list for Local-First AI Employee (Bronze Tier)"
---

# Tasks: Local-First AI Employee (Bronze Tier)

**Input**: Design documents from `/specs/1-local-first-ai-employee/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan in src/ directory
- [X] T002 [P] Initialize Python project with requirements.txt containing watchdog, pyyaml, and pathlib
- [X] T003 [P] Create the Obsidian Vault directory structure (Inbox, Needs_Action, Done, Logs, Plans, Pending_Approval, Approved, Briefings)
- [X] T004 Create config.py with vault directory paths and polling settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create base file operations utility in src/utils/file_operations.py
- [X] T006 [P] Implement file size polling logic for write completion detection
- [X] T007 [P] Create dashboard initialization functionality
- [X] T008 Set up logging framework for audit trails

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - File Drop Processing (Priority: P1) 🎯 MVP

**Goal**: Enable users to drop files into the Inbox folder so the AI employee can automatically process them

**Independent Test**: A user drops a file into the `/Inbox` folder, and the system automatically moves it to `/Needs_Action` with a metadata trigger file created.

### Implementation for User Story 1

- [X] T009 [P] [US1] Create File entity model in src/models/file_model.py
- [X] T010 [P] [US1] Create Task entity model in src/models/task_model.py
- [X] T011 [P] [US1] Create MetadataTrigger entity model in src/models/metadata_trigger_model.py
- [X] T012 [US1] Implement FilesystemWatcher class in src/filesystem_watcher.py
- [X] T013 [US1] Add file detection logic to monitor /Inbox for new files
- [X] T014 [US1] Implement file size polling to ensure write completion before moving
- [X] T015 [US1] Implement file move functionality from /Inbox to /Needs_Action
- [X] T016 [US1] Create metadata trigger file with YAML frontmatter in /Needs_Action
- [X] T017 [US1] Add duplicate filename handling with timestamp appending
- [X] T018 [US1] Add logging for file operations to /Logs

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Status Tracking (Priority: P2)

**Goal**: Allow users to track the status of their files through a dashboard to monitor what the AI employee is working on

**Independent Test**: The AI employee updates the `Dashboard.md` file to reflect the current status of tasks.

### Implementation for User Story 2

- [X] T019 [P] [US2] Create Dashboard entity model in src/models/dashboard_model.py
- [X] T020 [US2] Implement Vault_Read_Skill in src/skills/vault_read_skill.py
- [X] T021 [US2] Implement Vault_Write_Skill in src/skills/vault_write_skill.py
- [X] T022 [US2] Add dashboard update functionality to reflect task status changes
- [X] T023 [US2] Implement task status tracking in the dashboard
- [X] T024 [US2] Add dashboard refresh/update mechanism

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Task Lifecycle Management (Priority: P3)

**Goal**: Archive processed files so users can distinguish between pending and completed tasks

**Independent Test**: Files that have been processed by the AI employee are moved from `/Needs_Action` to `/Done`.

### Implementation for User Story 3

- [X] T025 [P] [US3] Implement Task_Completion_Skill in src/skills/task_completion_skill.py
- [X] T026 [US3] Add file move functionality from /Needs_Action to /Done
- [X] T027 [US3] Update task status to completed when moving to /Done
- [X] T028 [US3] Add completion logging to track task lifecycle

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T029 [P] Add comprehensive error handling across all components
- [ ] T030 [P] Add unit tests for all core functionality in tests/
- [ ] T031 [P] Add integration tests for end-to-end workflows
- [ ] T032 [P] Documentation updates in docs/
- [ ] T033 Code cleanup and refactoring
- [ ] T034 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence