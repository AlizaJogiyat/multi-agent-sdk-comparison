---
name: speckit.analyze
description: "Analyze a spec-delta for completeness, consistency, and conflicts with existing specs."
user-invocable: true
---

# speckit.analyze — Analyze Specification Quality

## Purpose

Review a change proposal's `spec-delta.md` for completeness, consistency with existing specs, and potential conflicts or gaps.

## Instructions

1. Ask the user which change to analyze (list active proposals from `changes/` if needed).

2. Read `changes/[change-name]/spec-delta.md` and `changes/[change-name]/proposal.md`.

3. Read all `specs/features/*/spec.md` files that overlap with the change's scope.

4. Read `specs/constitution.md` to check for principle violations.

5. Perform the following checks:

   **Completeness:**
   - Does every requirement in the proposal have at least one scenario?
   - Are all error cases covered?
   - Are edge cases addressed?

   **Consistency:**
   - Do new scenarios contradict existing specs?
   - Are naming conventions consistent?
   - Do data formats align across agent boundaries?

   **Constitution Compliance:**
   - Does the change violate any immutable principles?

   **Gaps:**
   - Are there implicit requirements not yet specified?
   - Are handoff contracts between agents fully defined?

6. Output a structured report:
   ```
   ## Analysis: [Change Name]

   ### Completeness: [PASS/WARN/FAIL]
   - [Details]

   ### Consistency: [PASS/WARN/FAIL]
   - [Details]

   ### Constitution Compliance: [PASS/FAIL]
   - [Details]

   ### Gaps Found
   - [List of missing scenarios or underspecified behavior]

   ### Recommendations
   - [Suggested additions or modifications]
   ```

7. If issues are found, suggest the user run `speckit.clarify` to resolve ambiguities.
