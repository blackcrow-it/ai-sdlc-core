# Policy: Approvals & Decision Gates

## Decision owners
- Product Owner: scope, priorities, core UX/product compromises, UAT acceptance.
- Tech Lead / Architect reviewer: major architecture and data model changes.
- Security owner: exceptions affecting secrets, access control or critical risk.
- Release owner (human): production deployment and destructive operational work.

## Mandatory approval points
1. Initial scope of project/MVP if requirements remain ambiguous or expensive.
2. Significant ADR changes, compliance assumptions and new external data processors.
3. Risk exceptions, critical security findings, or changes to auth/authorization policy.
4. Migration with data loss/irreversibility risk and any production deployment.

## Approval record
Keep task/run ID, change/diff, decision, approver identity, timestamp, scope, expiry if any, and evidence reference. If the Orca decision UI lacks a field, store a durable project record without misrepresenting a tool feature.

## Separation of duties
- Task author cannot approve own code review.
- A release agent cannot simulate a human approval by sending itself a message.
- If no authorized approver is reachable: **blocked**, not approved.
