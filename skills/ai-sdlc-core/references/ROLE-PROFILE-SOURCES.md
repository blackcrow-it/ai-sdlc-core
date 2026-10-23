# Role profile source notes

Maintenance reference; workers use their local role profile and `ROLE-PROFILE-CONTRACT.md`, without fetching
upstream prompts. Reviewed 2026-10-23 against
[`msitarzewski/agency-agents` commit `4e3ac3ca6604c75113f52c695dbddcc7af928b46`](https://github.com/msitarzewski/agency-agents/tree/4e3ac3ca6604c75113f52c695dbddcc7af928b46).
The source is MIT licensed, copyright 2025 AgentLand Contributors; full notice in `../THIRD_PARTY_NOTICES.md`.

## Adaptation map

Paths in the source column are relative to that pinned upstream tree. Role IDs, task contracts, primary skills,
single tracker, approval gates and Orca lifecycle remain those of AI SDLC Core.

| Existing role | Source profiles inspected | Adapted judgment and observable result |
|---|---|---|
| `orchestrator` | `specialized/agents-orchestrator.md` | Dependency-aware quality loops, complete handoffs, bounded remediation and integrated evidence before advancing |
| `product-manager` | `product/product-manager.md`, `product/product-feedback-synthesizer.md` | Problem before solution, source/confidence-aware prioritisation, measurable outcomes and explicit scope trade-offs |
| `business-analyst` | `product/product-feedback-synthesizer.md`, `design/design-ux-researcher.md` | Triangulate stakeholder signals, separate observation from inference, model exceptions and verify traceable rules |
| `ui-ux-designer` | `design/design-ux-researcher.md`, `design/design-ui-designer.md`, `design/design-ux-architect.md` | Evidence-based journeys, component/state/token handoff, inclusive interaction design and explicit prototype limits |
| `software-architect` | `engineering/engineering-software-architect.md`, `engineering/engineering-backend-architect.md` | Domain-led alternatives, costs and reversibility, dependency boundaries, failure semantics and evolution strategy |
| `project-manager` | `project-management/project-manager-senior.md`, `project-management/project-management-project-shepherd.md`, `product/product-sprint-prioritizer.md` | Spec-faithful slices, critical dependencies, resource conflicts, estimates with uncertainty and change impact |
| `frontend-developer` | `engineering/engineering-frontend-developer.md`, `design/design-ui-designer.md` | Full interaction states, accessible components, resilient API state, responsive/visual and measured performance checks |
| `backend-developer` | `engineering/engineering-backend-architect.md` | Contract/error semantics, authorisation, concurrency, bounded external failures, redacted observability and compatibility |
| `database-engineer` | `engineering/engineering-database-optimizer.md`, `engineering/engineering-database-reliability-engineer.md` | Query-plan evidence, engine-specific lock budgets, mixed-version migration safety, reconciliation and tested recovery |
| `qa-engineer` | `testing/testing-api-tester.md`, `testing/testing-test-results-analyzer.md`, `testing/testing-evidence-collector.md`, `testing/testing-reality-checker.md`, `testing/testing-performance-benchmarker.md`, `testing/testing-accessibility-auditor.md` | Risk-based coverage, reproducible defects, evidence suited to each claim, comparable measurements, manual/automated limits and release uncertainty |
| `code-reviewer` | `engineering/engineering-code-reviewer.md` | Specific findings with causal impact and fixes, complete feedback, independent verification, actionable severity |
| `security-engineer` | `security/security-appsec-engineer.md`, `security/security-architect.md` | Threat-to-control-to-test mapping, business-logic and tenant boundaries, exploitability-aware triage and retest |
| `devops-engineer` | `engineering/engineering-devops-automator.md`, `engineering/engineering-sre.md` | Reproducible artifacts, scoped rollout/recovery, user-impact signals, bounded operations and release evidence |
| `technical-writer` | `engineering/engineering-technical-writer.md` | Audience/task-driven documentation, tested examples, version and prerequisite accuracy, migration/troubleshooting guidance |

## Deliberate changes from upstream

The profiles are selective rewrites, not copies of the upstream organisation. The BA role combines relevant
research and feedback practices; it is not presented as a one-to-one upstream role. We retain 14 local roles
and their IDs, without importing marketing, sales or other unrelated teams.

We do not import persona biographies, persistent-memory claims, tool paths or commands from the upstream
project, automatic pipeline permission, fixed retry counts, prescribed stack choices, mandatory theme toggles,
universal latency/coverage/delivery targets, or assumptions that every first pass must fail. Metrics and gates
come from reviewed project requirements. Screenshots support visual claims; assertions or observed outcomes
support behaviour. Missing required evidence stays `blocked`/`not_run`; it does not justify invented findings.

Database rollback may require forward recovery and an executed restore rather than a nominal DOWN script.
Security findings distinguish observed exploits, code-supported exposure and unverified hypotheses. Neither
role receives permission to access production or conduct intrusive tests from these capabilities.

Role-specific completion criteria complement shared discipline skills. The shared requirements skill routes
PM, BA, UX, planning and writing tasks to their actual artifacts, so role specialisation does not accidentally
force every task into a new PRD/SRS. No schema, role registry or external workflow API is changed by this upgrade.
