---
name: speckit.clarify
description: "Identify and resolve ambiguities, open questions, and underspecified behavior in a spec-delta."
user-invocable: true
---

# speckit.clarify — Resolve Spec Ambiguities

## Purpose

Surface ambiguities, open questions, and underspecified behavior in a change proposal, then work with the user to resolve them and update the spec-delta.

## Instructions

1. Ask the user which change to clarify (list active proposals from `changes/` if needed).

2. Read `changes/[change-name]/proposal.md` and `changes/[change-name]/spec-delta.md`.

3. Identify ambiguities by looking for:
   - Vague language ("should", "might", "usually", "appropriate")
   - Missing boundary conditions (what happens at limits?)
   - Undefined terms or references
   - Scenarios that assume unstated preconditions
   - Handoff contracts with unspecified error handling
   - Data formats not fully defined

4. Present each ambiguity as a numbered question to the user:
   ```
   ## Open Questions: [Change Name]

   1. [Question about ambiguity] — Options: A) ... B) ... C) ...
   2. [Question about missing boundary] — What should happen when...?
   3. [Question about undefined term] — How is X defined?
   ```

5. For each resolution the user provides, update the `spec-delta.md` with a new or modified Given/When/Then scenario.

6. After all questions are resolved, confirm the spec-delta is updated and suggest running `speckit.analyze` again.
