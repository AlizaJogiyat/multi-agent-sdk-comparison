---
name: speckit.checklist
description: "Generate a pre-implementation checklist verifying all SDD gates are met before coding begins."
user-invocable: true
---

# speckit.checklist — Pre-Implementation Gate Check

## Purpose

Verify that all SDD requirements are satisfied before implementation begins. Acts as a go/no-go gate.

## Instructions

1. Ask the user which change to check (list active proposals from `changes/` if needed).

2. Read all artifacts in `changes/[change-name]/`.

3. Run through the following checklist:

   ```
   ## Pre-Implementation Checklist: [Change Name]

   ### Required Artifacts
   - [ ] proposal.md exists and is complete
   - [ ] spec-delta.md exists with Given/When/Then scenarios
   - [ ] tasks.md exists with implementation checklist
   - [ ] All artifacts committed with [spec] prefix

   ### Specification Quality
   - [ ] Every requirement has at least one scenario
   - [ ] Error cases are explicitly specified
   - [ ] No contradictions with existing specs
   - [ ] No violations of constitution.md principles
   - [ ] Spec file stays under 500 lines

   ### Handoff Contracts (if applicable)
   - [ ] Input/output schemas defined for each agent boundary
   - [ ] Error propagation behavior specified
   - [ ] Data format explicitly documented

   ### Ready to Implement?
   [READY / NOT READY — list blocking items]
   ```

4. Mark each item as passing or failing with brief explanation.

5. If NOT READY, list exactly what needs to be done and suggest the appropriate speckit command to fix it.
