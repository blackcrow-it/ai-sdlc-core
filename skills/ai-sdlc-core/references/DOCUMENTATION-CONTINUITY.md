# Documentation continuity

Apply to new projects and every feature, bug fix, refactor and release. The spec, task authoring, owner,
reviewer and Orchestrator all use this contract. Completion means the applicable canonical documents describe
the delivered product and each changed requirement is traceable to its source, task and verification evidence.

## 1. Establish the canonical documents

Read the project's existing documents before planning. Maintain a project-owned documentation map from core
`templates/documentation-map.md` at `docs/documentation-map.md`, or reuse its existing equivalent. The map is an
index, not another requirements document or task tracker. Each applicable artifact has one canonical path,
an owner, status and a reference to the reviewed revision. Existing filenames and requirement IDs take precedence
over the example paths below. Link supporting feature specs to the canonical requirements.

Assess every category; record `not applicable` with a concrete reason when the project does not need one:

| Category | Canonical content | Update trigger |
|---|---|---|
| Brief / PRD | Product goals, users, scope, journeys, success criteria | Product intent or scope changes |
| SRS | Functional requirements, rules, failures, NFRs, acceptance criteria | Observable behavior or constraints change |
| UI specification | Screens, interactions, states, accessibility | User interaction changes |
| Architecture / ADRs | Components, boundaries, significant decisions | Architecture or a recorded decision changes |
| API / data contracts | Schemas, versions, errors, migrations, ownership | Public interfaces or persisted data change |
| Glossary | Canonical domain concepts and relationships | Terms are added, split or renamed |
| Test plan / traceability | Requirement → acceptance criterion → task → test → run evidence | Requirements or verification change |
| User / operator guides | Usage, configuration, rollout, rollback, recovery | User or operator actions change |
| Release notes | Delivered behavior, compatibility and migration notes | A change is released |

For a new project, plan creation of applicable documents through the enabled phases, with PRD/SRS before the
implementation that depends on them. For an existing project, identify missing or stale baselines as explicit
documentation tasks. Reconstruct only verified behavior from code, tests and stakeholder decisions; mark
inferences and unresolved questions. Missing required baselines block dependent implementation until resolved
or a named human records a scoped exception per the quality-gate policy. Disabling a phase does not remove its
documentation obligations: assign them to an enabled qualified role or report a blocker.

## 2. Assess each change

The feature spec includes a **Documentation impact** table using the feature-spec template. For a single task,
put the same assessment in its contract. Inspect the categories above, identify the affected canonical sections
and requirement IDs, explain the change, and identify its owner and verification. Record why unaffected
categories need no update. Unknown impact remains an open decision, not `no impact`.

PRD and SRS remain the current product baseline. A feature spec records the change and links to those documents;
it does not replace updating them. Update only affected sections, preserve unrelated content and history, retain
stable IDs, and mark removed/replaced requirements as retired or superseded with links. Never silently reuse IDs.
Update document revision/change history and link the source feature/task. A changed document returns to draft or
pending review; an old sign-off still applies only to its immutable earlier revision. Record a new approval only
when the authorized person actually gives it.

## 3. Plan document ownership and dependencies

Every newly authored task has `documentation`:

```json
{
  "assessment": "The recovery flow changes authentication behavior; update the canonical SRS and its traceability.",
  "updates": [
    {
      "path": "docs/SRS.md",
      "change": "Add recovery-token expiry and rejection criteria, then link the task and tests.",
      "requirement_ids": ["REQ-AUTH-012"]
    }
  ]
}
```

- `assessment` states the impact and the disposition of unaffected categories. `updates` lists only files this
  task owns and will actually change, with exact repository-relative paths inside its write scope, outside
  protected paths. `change` states what will become true. `requirement_ids` names the IDs that must appear in
  that file; use an empty list only for documents without requirement-level content and explain why.
- An empty `updates` list requires a specific no-impact justification, or references to the tasks that own the
  affected documents. The reviewer checks those references. Outsourcing an update does not remove the feature's
  obligation or authorize a worker to edit another task's files.
- Each impact row maps to an owned update or an explicit no-impact decision. Include document updates in the
  task's deliverables and acceptance criteria. Add canonical input paths to `input_artifacts`.
- Update and approve changed requirements/contracts before dependent implementation. Final test results and
  user/operator instructions can be filled after code exists; link that work to a final reconciliation task
  which depends on all feature slices and documentation tasks and blocks feature acceptance/release.
- Keep narrow vertical slices. A small documentation update can belong to the same slice; larger work is a
  separate task owned by an appropriate analysis, architecture, QA or documentation role.
- Shared baseline files have one writer at a time. Sequence overlapping updates or give them one integration
  owner, then reconcile against the integrated revision. Independent worktrees do not resolve semantic conflicts.
- Project write ceilings and protected paths still apply. Request the user's scope decision for a required
  document outside them; never mark that document complete to work around the boundary.

## 4. Verify each task and the integrated feature

Before handoff, run both the scope check and:

```text
python "<CORE>/scripts/sdlc.py" docs-check --task <contract-file-or-issue-body> --base <recorded-base-commit>
```

The command is read-only. It checks that the contract has an assessment and that every declared update is a
nonempty UTF-8 text file, changed since the task base (committed, staged, unstaged or untracked), with its declared
requirement IDs present. It checks exact paths and scope through task validation. A file renamed or retired uses
the surviving canonical text document as the update target, with the disposition and redirects checked by review.
Binary originals may remain supporting inputs; keep the maintained, verifiable requirements in text documents.

This is a structural check over declared updates. It cannot discover omitted documents, prove semantic
consistency, validate the truth of no-impact claims, or establish human approval. The independent reviewer must:

1. Compare the change with the documentation map and impact assessment; flag missing categories and stale or
   contradictory requirements, interfaces, diagrams, instructions and examples.
2. Follow every changed requirement through source → canonical requirement → feature spec → task → acceptance
   criterion → test → actual result/evidence. Keep the canonical coverage matrix in the SRS (or the project's
   existing traceability document), with links elsewhere rather than competing copies.
3. Verify that task/test/evidence references exist and match the reviewed revision. Before execution, label links
   as planned; before acceptance, replace them with actual references and outcomes. Failed, blocked and `not_run`
   results remain visible. A requirement intentionally verified by review/manual inspection names its method,
   owner and actual evidence instead of a fabricated automated test.
4. Check approval history for changed baselines and the final integrated result. A task's docs-check pass does
   not prove a sibling's update landed. The reconciliation owner reads the integrated files and all linked task
   outcomes before the human accepts the feature or release.

Missing required documentation, broken traceability, unreviewed behavior changes or inconsistent baselines are
`changes_requested`/`blocked`, never a successful closure with "update docs later". An exception requires the
named human's decision with scope, reason, owner and expiry; record it as `waived`, not `pass`.

## Compatibility

Core 0.1.1 adds the optional `documentation` task field and `docs-check`; the project config schema stays 0.1.
Older contracts remain readable and valid, with a validation warning when unassessed. Before executing or
accepting one, reassess it, review any scope/dependency changes and update the single tracker record. New drafts
include an unresolved assessment placeholder. No project is automatically rewritten or reapproved on upgrade.
