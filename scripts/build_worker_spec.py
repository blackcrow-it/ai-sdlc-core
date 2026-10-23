#!/usr/bin/env python3
"""Build an auditable, self-contained Orca worker spec (no Orca calls)."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'outputs/smoke-test/ba-task-spec.md'


def generate_spec(root=ROOT, role='business-analyst'):
    registry = json.loads((root / 'agents/registry.json').read_text(encoding='utf-8'))
    matched = [r for r in registry['roles'] if r['id'] == role]
    if len(matched) != 1:
        raise ValueError(f'Invalid or ambiguous role: {role}')
    if role != 'business-analyst':
        raise ValueError('Phase 2.1 smoke test only authorizes business-analyst')
    role_path = root / matched[0]['role_file']
    def section(title, relative):
        data = (root / relative).read_text(encoding='utf-8').strip()
        return f'\n## {title} ({relative})\n\n{data}\n'

    header = """# Orca supervised Task Spec — BA Smoke Test

TARGET
- Work inside the **current repository/worktree** only.
- Read `examples/project-brief.md`; analyze a demo authentication feature.

CHANGE
- Create `outputs/smoke-test/auth-requirements.md` with distinct sections:
  `# Authentication Requirements`, `## Scope`, `## User Stories`,
  `## Functional Requirements`, `## Non-functional Requirements`,
  `## Acceptance Criteria`, `## Assumptions`, `## Open Questions`.
- Create `outputs/smoke-test/ba-handoff.md` with distinct sections:
  `# BA Handoff`, `## Artifacts`, `## Evidence`, `## Risks`, `## Next Owner`.
- Distinguish verified requirements from assumptions. Do not guess login method,
  session lifetime or compliance requirements. Place unknown decisions under Open Questions.

OWNERSHIP & BOUNDARIES
- Primary owner: business-analyst. Later independent reviewer: orchestrator/human.
- May write **only** the two files above; may create their parent directories.
- No source-code edits, branch merge, production access, secrets, infrastructure,
  CI configuration edits, network publishing, or destructive operations.
- The task spec is not an elevation of tool permissions; actual runtime controls apply.

OBSERVABLE ACCEPTANCE
- Both deliverables exist at the specified paths and are non-empty.
- The requirements document covers visitor/member/admin roles with traceable
  acceptance criteria and explicit open questions.
- The handoff names produced files, document-based evidence, risks and next owner.
- Report what you actually did. Do not invent executed tests or approvals.
- Coordinator will run `python scripts/check_smoke_output.py` and review semantics.
- Follow the current injected Orca supervised worker preamble. Send
  `worker_done` exactly once with explicit `--outcome succeeded` or `failed`,
  real task/dispatch IDs and meaningful three-sentence summary.
"""
    # Keep the CLI argument short enough for Windows terminals. The spec itself
    # contains all mandatory task semantics; shared references are read locally.
    reference_paths = [
        matched[0]['role_file'], 'workflows/requirements.md',
        'policies/permissions.md', 'policies/approval-rules.md',
        'policies/quality-gates.md', 'docs/HANDOFF.md',
        'skills/requirements-analysis/SKILL.md',
    ]
    references = ('\nREFERENCE FILES TO READ BEFORE ACTION\n'
                  + ''.join(f'- `{path}`\n' for path in reference_paths))
    brief = section('Source project brief', 'examples/project-brief.md')
    return header.strip() + '\n' + brief + references



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--role', default='business-analyst')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    content=generate_spec(role=args.role)
    dest = args.output if args.output.is_absolute() else ROOT / args.output
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(content,encoding='utf-8')
    print(f'WROTE {dest} ({len(content)} characters). Not dispatched to Orca.')

if __name__ == '__main__': main()
