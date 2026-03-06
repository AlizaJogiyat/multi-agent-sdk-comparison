---
name: disrupt-sdd
description: "Enforce Spec-Driven Development (Disrupt STD-001). Ensures every behavior-changing feature has a specification before implementation begins."
user-invocable: false
---

# Spec-Driven Development (STD-001)

## Purpose

Every code change that modifies observable behavior MUST have a written specification committed before implementation. Specs live in the repository, are reviewed like code, and are the single source of truth for what the system does.

## Always

1. Maintain the required directory structure (see Required Structure below).
2. Create a change proposal (`proposal.md`, `spec-delta.md`, `tasks.md`) BEFORE writing implementation code.
3. Commit proposal artifacts with the `[spec]` prefix before any `[impl]` commits in the same PR.
4. Write specs using Given/When/Then scenarios for every requirement.
5. Include at least one scenario per requirement; specify error cases explicitly.
6. Keep spec files under 500 lines. Split large features into focused specs.
7. Mirror code paths in spec paths (`src/features/auth/` → `specs/features/auth/spec.md`).
8. On PR merge, move the change directory from `changes/` to `archive/` and merge the spec-delta into canonical `specs/features/` files.

## Ask First

1. Skipping a proposal for a change that arguably modifies observable behavior — confirm with the team lead.
2. Splitting or merging spec files — confirm the new structure with the team.
3. Modifying `specs/constitution.md` — requires explicit team approval.

## Never

1. Never merge implementation code without the corresponding spec artifacts in the same PR.
2. Never modify canonical `specs/features/` files directly during implementation; use `spec-delta.md` in `changes/`.
3. Never delete or overwrite `specs/constitution.md` without team approval.
4. Never skip error-case scenarios in specifications.

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

```
project/
├── specs/
│   ├── constitution.md
│   └── features/
│       └── [feature]/
│           └── spec.md
├── changes/
│   └── [change-name]/
│       ├── proposal.md
│       ├── spec-delta.md
│       └── tasks.md
└── archive/
```

## Commit Convention

| Prefix | Usage |
| :--- | :--- |
| `[spec]` | Proposal and spec artifacts |
| `[impl]` | Implementation code |
| `[archive]` | Moving completed changes to archive |
| `[fix]` | Bug fix restoring specified behavior |
| `[refactor]` | Refactor with no behavior change |

## Templates

### proposal.md

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
```

### spec-delta.md

```markdown
# Spec Delta: [Change Name]

## ADDED
- [New behavior with Given/When/Then]

## MODIFIED
- [Changed behavior with before/after scenarios]

## REMOVED
- [Deleted behavior and rationale]
```

### tasks.md

```markdown
# Tasks: [Change Name]

- [ ] Create proposal and spec-delta
- [ ] Review with team
- [ ] Implement changes
- [ ] Update tests
- [ ] Archive change on merge
```
