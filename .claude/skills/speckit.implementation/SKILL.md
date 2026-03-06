---
name: speckit.implementation
description: "Execute implementation tasks from tasks.md, following the spec-delta as source of truth."
user-invocable: true
---

# speckit.implementation — Implement from Spec

## Purpose

Execute the implementation tasks defined in `tasks.md`, using the `spec-delta.md` as the source of truth for expected behavior. Ensures code matches spec at every step.

## Instructions

1. Ask the user which change to implement (list active proposals from `changes/` if needed).

2. Run `speckit.checklist` logic internally — if not READY, stop and tell the user what's missing.

3. Read `changes/[change-name]/tasks.md` to get the ordered task list.

4. Read `changes/[change-name]/spec-delta.md` to understand expected behavior.

5. For each task in order:
   a. Read the referenced Given/When/Then scenario(s)
   b. Implement the code to satisfy the scenario
   c. Mark the task as complete in `tasks.md`
   d. Commit with `[impl]` prefix after each logical unit of work

6. **Rules during implementation:**
   - NEVER modify `specs/features/` files directly — only `changes/` artifacts
   - Code MUST satisfy the Given/When/Then scenarios exactly
   - If a scenario is ambiguous or impossible to implement, STOP and ask the user (do not guess)
   - Mirror code paths in spec paths (`src/features/X/` → `specs/features/X/spec.md`)
   - Follow existing code patterns and conventions in the project

7. After all tasks are complete:
   - Confirm all scenarios are implemented
   - Remind the user to review and then run archive to complete the cycle

8. **Commit convention:**
   - Each `[impl]` commit message should reference the change name
   - Example: `[impl] Implement research agent tool integration`
