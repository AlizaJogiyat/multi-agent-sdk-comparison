---
name: speckit.plan
description: "Create a new change proposal for a feature. Generates proposal.md, spec-delta.md, and tasks.md in changes/[change-name]/."
user-invocable: true
---

# speckit.plan — Create a Change Proposal

## Purpose

Scaffold a new change proposal under `changes/[change-name]/` with the three required SDD artifacts: `proposal.md`, `spec-delta.md`, and `tasks.md`.

## Instructions

1. Ask the user for:
   - **Change name** (kebab-case, e.g., `add-research-agent`)
   - **Problem** — what is broken or missing
   - **Solution** — what we will do
   - **Scope** — which features/specs are affected
   - **Risks** — what could go wrong

2. Create the directory `changes/[change-name]/`.

3. Generate `proposal.md`:
   ```markdown
   # Proposal: [Change Name]

   ## Problem
   [From user input]

   ## Solution
   [From user input]

   ## Scope
   [From user input]

   ## Risks
   [From user input]
   ```

4. Generate a skeleton `spec-delta.md`:
   ```markdown
   # Spec Delta: [Change Name]

   ## ADDED
   - [To be filled during speckit.specify]

   ## MODIFIED
   - [To be filled during speckit.specify]

   ## REMOVED
   - [To be filled during speckit.specify]
   ```

5. Generate a skeleton `tasks.md`:
   ```markdown
   # Tasks: [Change Name]

   - [ ] Create proposal and spec-delta
   - [ ] Specify behavior (speckit.specify)
   - [ ] Review with team
   - [ ] Implement changes
   - [ ] Update tests
   - [ ] Archive change on merge
   ```

6. Confirm creation and remind the user to run `speckit.specify` next to fill in Given/When/Then scenarios.
