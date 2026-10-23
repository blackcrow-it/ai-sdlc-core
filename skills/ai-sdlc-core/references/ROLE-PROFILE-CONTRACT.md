# Shared role execution contract

Read this with the assigned `agents/<role>.md`, task contract and primary skill. The profile adds domain-specific
judgment; it does not change core policies, project permissions or the calling workflow. Select only the methods
and artifacts needed by this task. A capability listed in a profile is not a requirement to add it to the product.

## Establish the assignment

- Read `references/OPERATING-CONTRACT.md`, the applicable workflow, all core policies, project `AGENTS.md` and
  `.ai-sdlc/project.json`. In supervised work, use the complete injected spec and the installed Orca guide.
- Identify the task's requirement IDs, input revisions and approval state, owner, independent reviewer,
  dependencies, `allowed_paths`, checks, retry budget and deliverables. Missing approval blocks work that needs
  that approval; authorised discovery may still investigate and propose options without claiming acceptance.
- Read existing code, contracts, glossary and ADRs before proposing changes. Keep facts with sources, hypotheses
  with a verification method, and recommendations with trade-offs. A source's examples and metric targets are
  not project requirements. Missing business targets, research, legal obligations or risk acceptance need an owner.
- Tool availability is factual, not implied by a role or CLI name. Resolve Orca CLIs per `ROLE-ASSIGNMENT.md`;
  use only installed, permitted tools and documented commands. A role never switches the current CLI by itself.

## Work and verify

- One contract per worker; write only owned paths and use the authorised environment. Shared contracts and
  document writers need coordination. Request an amended contract for changed scope, criteria or test seams.
- Human decisions use `sdlc-grilling` when appropriate to the calling workflow. A supervised worker sends them
  through Orchestrator ask/reply; missing answers remain owned blockers. Interview completion is not dispatch,
  publication or release approval. Preserve the workflow's exact approval tokens and named human gates.
- Verify claims with evidence appropriate to the claim: code inspection for a proposed design, assertions or
  recorded outcomes for behaviour, screenshots for appearance, measurements for performance, and restore/drill
  results for recovery. An artifact's existence or a tool's exit code alone does not prove all acceptance criteria.
- Record revision, environment, command, exit code and evidence path for real runs; identify mocks and coverage
  limits. Keep `pass`, `fail`, `blocked`, `not_run` and authorised `waived` distinct. Missing evidence is a gap,
  not a fabricated defect or pass. Zero reproducible defects is valid within a documented test scope.
- Execute the contract's required checks and scope check. Scale optional verification to the risk; do not
  introduce a new framework, quota, recurring job, scanner or infrastructure just to satisfy a profile checklist.

## Close with a usable handoff

Apply `DOCUMENTATION-CONTINUITY.md`: update owned canonical documents and requirement-to-evidence links,
preserve revision/approval history, run `sdlc.py docs-check`, and report missing baselines or out-of-scope updates.
Do not create parallel PRDs, task lists or trackers. Planned work remains planned until actual evidence exists.

Use `references/HANDOFF.md`: acceptance criterion → artifact/test/result, changed paths, commands/exit codes,
documentation outcome, open decisions with owner and what they block, residual risk and next owner. The task's
reviewer and workflow determine routing; a profile's suggested next owner does not override them. A recommendation
is not a human acceptance, merge or release. Report only observed progress, not an invented percentage or score.

For failures, preserve the exact repro and useful evidence, attempt only within the configured budget, then
escalate the concrete blocker with options. Reconcile uncertain Orca receipts before retries. Redact sensitive
data from evidence. Learning means updating an authorised retro or artifact, not claiming persistent memory.
