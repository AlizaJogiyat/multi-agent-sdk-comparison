---
name: speckit.tasks
description: "Generate or update the implementation task breakdown from a finalized spec-delta."
user-invocable: true
---

# speckit.tasks — Generate Implementation Tasks

## Purpose

Break down a finalized spec-delta into concrete, ordered implementation tasks with dependencies and acceptance criteria derived from the Given/When/Then scenarios.

## Instructions

1. Ask the user which change to generate tasks for (list active proposals from `changes/` if needed).

2. Read `changes/[change-name]/spec-delta.md` and `changes/[change-name]/proposal.md`.

3. For each scenario in the spec-delta, derive implementation tasks:
   - Map each ADDED scenario to a "build" task
   - Map each MODIFIED scenario to an "update" task
   - Map each REMOVED scenario to a "remove" task

4. Order tasks by dependency (what must exist before other things can be built).

5. Update `changes/[change-name]/tasks.md` with the detailed breakdown:
   ```markdown
   # Tasks: [Change Name]

   ## Phase 1: Foundation
   - [ ] Task description
     - Acceptance: [Given/When/Then scenario reference]
     - Files: [Expected files to create/modify]

   ## Phase 2: Core Logic
   - [ ] Task description
     - Acceptance: [Given/When/Then scenario reference]
     - Files: [Expected files to create/modify]

   ## Phase 3: Integration & Testing
   - [ ] Task description
     - Acceptance: [Given/When/Then scenario reference]

   ## Phase 4: Cleanup
   - [ ] Update tests
   - [ ] Archive change on merge
   ```

6. Each task MUST reference at least one Given/When/Then scenario as its acceptance criteria.

7. Remind the user to run `speckit.checklist` before starting implementation.
