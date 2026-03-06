STD-001: Spec-Driven Development
Summary
All code that changes observable behavior MUST be preceded by a written specification. Specs live in the repository, are reviewed like code, and are the source of truth for what the system does.
Requirements
1. Repository Structure
Every project MUST have the following structure:

project/
├── specs/
│   ├── constitution.md        # Immutable project principles
│   └── features/
│       └── [feature]/
│           └── spec.md        # Current behavior specification
├── changes/
│   └── [change-name]/
│       ├── proposal.md        # What and why
│       ├── spec-delta.md      # ADDED / MODIFIED / REMOVED
│       └── tasks.md           # Implementation checklist
└── archive/                   # Completed changes
2. When a Proposal is Required
A change proposal MUST be created when the change:

Adds new features or functionality
Modifies observable behavior
Introduces breaking API changes
Changes architecture or security patterns
Alters database schemas

A change proposal MAY be skipped when the change:

Fixes a bug to restore behavior already described in the spec
Is a refactor with no behavior change
Updates config, dependencies, or documentation only
3. Proposal-Before-Code
Change proposals (proposal.md, spec-delta.md, tasks.md) MUST be committed before implementation changes in the same PR. The proposal commit SHOULD use the [spec] prefix, followed by [impl] for the implementation. The canonical specs/ files are updated during archival (see requirement 6).

Commit Prefix
Description
[spec]
Add SSO support specification
[impl]
Implement SSO support
[archive]
Archive add-sso-support

4. Spec Format
Feature specs MUST use Given/When/Then scenarios for all requirements:

Given [precondition]
When [action]
Then [expected outcome]

Each requirement MUST have at least one scenario. Error cases MUST be specified explicitly.
5. PR Gates
Every PR that requires a proposal MUST include:

changes/[name]/proposal.md describing what and why
changes/[name]/spec-delta.md with explicit ADDED/MODIFIED/REMOVED sections
changes/[name]/tasks.md with implementation checklist
Proposal artifacts committed before code changes
6. Archive on Merge
When a PR merges, the change directory MUST be moved from changes/ to archive/ and the spec-delta MUST be merged into the canonical specs/features/ files.
7. Naming Convention
Code and spec locations MUST mirror each other:

Code Location
Spec Location
src/features/auth/
specs/features/auth/spec.md
src/features/billing/
specs/features/billing/spec.md

8. Spec Size
A single spec file SHOULD NOT exceed 500 lines. If it does, the feature SHOULD be split into smaller, focused specifications.
Why
Documentation drift is a systems problem, not a discipline problem. When specs live outside the development workflow, they go stale within weeks. This standard ensures specs are co-located with code, reviewed in PRs, and kept current by making updates the path of least resistance.
Learn More
Full SDD Reference Guide -- complete methodology with templates, workflows, anti-patterns, and AI/agent integration
SDD Context Engineering Course -- hands-on training
Deploy to Your Project
Copy the skill directory into your project so coding agents (Claude Code, Cursor, etc.) enforce this standard automatically.

cp -r standards/std-001-spec-driven-development/skill/ <project>/.claude/skills/disrupt-sdd/
Preview SKILL.md
---
name: disrupt-sdd
description: "Enforce Spec-Driven Development (Disrupt STD-001). Ensures every behavior-changing feature has a specification before implementation begins."
user-invocable: false
---

# Spec-Driven Development (STD-001)

## Purpose

Every code change that modifies observable behavior MUST have a written specification committed before implementation. Specs live in the repository, are reviewed like code, and are the single source of truth for what the system does.

## Always

1.  Maintain the required directory structure (see Required Structure below).
2.  Create a change proposal (`proposal.md`, `spec-delta.md`, `tasks.md`) BEFORE writing implementation code.
3.  Commit proposal artifacts with the `[spec]` prefix before any `[impl]` commits in the same PR.
4.  Write specs using Given/When/Then scenarios for every requirement.
5.  Include at least one scenario per requirement; specify error cases explicitly.
6.  Keep spec files under 500 lines. Split large features into focused specs.
7.  Mirror code paths in spec paths (`src/features/auth/` -> `specs/features/auth/spec.md`).
8.  On PR merge, move the change directory from `changes/` to `archive/` and merge the spec-delta into canonical `specs/features/` files.

## Ask First

1.  Skipping a proposal for a change that arguably modifies observable behavior -- confirm with the team lead.
2.  Splitting or merging spec files -- confirm the new structure with the team.
3.  Modifying `specs/constitution.md` -- requires explicit team approval.

## Never

1.  Never merge implementation code without the corresponding spec artifacts in the same PR.
2.  Never modify canonical `specs/features/` files directly during implementation; use `spec-delta.md` in `changes/`.
3.  Never delete or overwrite `specs/constitution.md` without team approval.
4.  Never skip error-case scenarios in specifications.

## Decision: Do I Need a Proposal?

| Change Type | Proposal Required? |
| :--- | :--- |
| Adding new features or functionality? | YES |
| Modifying observable behavior? | YES |
| Introducing breaking API changes? | YES |
| Changing architecture or security patterns? | YES |
| Altering database schemas? | YES |
| Fixing a bug to restore already-specified behavior? | NO |
| Refactoring with no behavior change? | NO |
| Updating config, deps, or docs only? | NO |

## Required Structure

project/
specs/
constitution.md              # Immutable project principles
features/
[feature]/
spec.md                  # Current behavior specification
changes/
[change-name]/
proposal.md                # What and why
spec-delta.md              # ADDED / MODIFIED / REMOVED sections
tasks.md                   # Implementation checklist
archive/                       # Completed changes (moved on merge)


## Commit Convention

| Prefix | Usage |
| :--- | :--- |
| `[spec]` | Proposal and spec artifacts |
| `[impl]` | Implementation code |
| `[archive]` | Moving completed changes to archive |
| `[fix]` | Bug fix restoring specified behavior |
| `[refactor]` | Refactor with no behavior change |

**Examples:**

[spec] Add SSO support specification
[impl] Implement SSO support
[archive] Archive add-sso-support
[fix] Restore correct session timeout behavior


## Templates

### proposal.md (minimal)

```markdown
# Proposal: [Change Name]

## Problem
[What is broken or missing]

## Solution
[What we will do]

## Scope
[Which features/specs are affected]

## Risks
[What could go wrong]
spec-delta.md (minimal)
# Spec Delta: [Change Name]

## ADDED
- [New behavior with Given/When/Then]

## MODIFIED
- [Changed behavior with before/after scenarios]

## REMOVED
- [Deleted behavior and rationale]
tasks.md (minimal)
# Tasks: [Change Name]

- [ ] Create proposal and spec-delta
- [ ] Review with team
- [ ] Implement changes
- [ ] Update tests
- [ ] Archive change on merge

Full templates with detailed guidance: see references/templates.md


