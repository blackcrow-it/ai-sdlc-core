#!/usr/bin/env python3
"""Static checks only; does not verify Orca lifecycle or factual quality."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / 'outputs/smoke-test/auth-requirements.md'
HANDOFF = ROOT / 'outputs/smoke-test/ba-handoff.md'
HEADINGS = {
    REQ: ['# Authentication Requirements','## Scope','## User Stories',
          '## Functional Requirements','## Non-functional Requirements',
          '## Acceptance Criteria','## Assumptions','## Open Questions'],
    HANDOFF: ['# BA Handoff','## Artifacts','## Evidence','## Risks','## Next Owner'],
}

def check_files(headings=HEADINGS):
    errors=[]
    for path,required in headings.items():
        if not path.is_file():
            errors.append(f'Missing file: {path}')
            continue
        content=path.read_text(encoding='utf-8')
        if len(content.strip()) < 250:
            errors.append(f'Insufficient content in {path.name}')
        lines={line.strip() for line in content.splitlines()}
        for heading in required:
            if heading not in lines:
                errors.append(f'Missing heading {heading} in {path.name}')
        if 'REPLACE' in content or 'TODO_FILL' in content:
            errors.append(f'Unfilled placeholders in {path.name}')
    return errors

def main():
    problems=check_files()
    if problems:
        for issue in problems: print('FAIL:',issue)
        print('Not finished. This is only a static check; Orca runtime and semantic review remain separate.')
        return 1
    print('OK: required output paths, section headings and minimum text size present.')
    print('NOTE: real Orca Run/Dispatch, permissions, policy compliance and semantics still require verification.')
    return 0

if __name__=='__main__': sys.exit(main())
