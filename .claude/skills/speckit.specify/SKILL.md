---
name: speckit.specify
description: "Write Given/When/Then behavioral specifications for a change proposal's spec-delta.md."
user-invocable: true
---

# speckit.specify — Write Behavioral Specifications

## Purpose

Fill in the `spec-delta.md` for an existing change proposal with detailed Given/When/Then scenarios covering all requirements and error cases.

## Instructions

1. Ask the user which change to specify (list active proposals from `changes/` if needed).

2. Read the `changes/[change-name]/proposal.md` to understand the problem, solution, and scope.

3. Read any existing `specs/features/` files that are in scope to understand current behavior.

4. For each behavior described in the proposal, write Given/When/Then scenarios:
   ```
   Given [precondition]
   When [action]
   Then [expected outcome]
   ```

5. **Requirements:**
   - At least one scenario per requirement
   - Error cases MUST be specified explicitly
   - Include edge cases where relevant
   - Group scenarios under ADDED, MODIFIED, or REMOVED sections

6. Update `changes/[change-name]/spec-delta.md` with the scenarios.

7. Update `changes/[change-name]/tasks.md` to check off the specify step.

8. Remind the user to review the scenarios and run `speckit.analyze` for validation.
