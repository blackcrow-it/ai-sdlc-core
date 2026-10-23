#!/usr/bin/env python3
"""Validate the static Orca SDLC configuration using only Python standard library.
This does not connect to Orca or execute agents / CI and is not a complete JSON Schema validator.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_task(task, registry):
    errors = []
    required = ('task_id', 'project_id', 'title', 'owner_agent', 'reviewer_agent', 'status',
                'dependencies', 'scope', 'acceptance_criteria', 'required_checks',
                'deliverables', 'max_attempts', 'human_approval_required')
    for name in required:
        if name not in task:
            errors.append(f'Missing task field: {name}')
    ids = {r['id'] for r in registry['roles']}
    if task.get('owner_agent') not in ids:
        errors.append('Unknown owner_agent')
    if task.get('reviewer_agent') not in ids:
        errors.append('Unknown reviewer_agent')
    if task.get('owner_agent') == task.get('reviewer_agent'):
        errors.append('Owner and reviewer cannot be the same role')
    if task.get('status') not in ('draft','ready','in_progress','blocked',
                                  'submitted_for_review','changes_requested','accepted','cancelled'):
        errors.append('Invalid task status')
    if not isinstance(task.get('dependencies'), list):
        errors.append('dependencies must be a list')
    elif task.get('task_id') in task['dependencies']:
        errors.append('Task cannot depend on itself')
    scope = task.get('scope')
    if not isinstance(scope, dict) or not scope.get('allowed_paths') or not isinstance(scope.get('forbidden_actions'),list):
        errors.append('scope needs nonempty allowed_paths and list forbidden_actions')
    if not isinstance(task.get('acceptance_criteria'), list) or not task.get('acceptance_criteria'):
        errors.append('acceptance_criteria cannot be empty')
    if not isinstance(task.get('required_checks'),list) or not task.get('required_checks'):
        errors.append('required_checks cannot be empty')
    if not isinstance(task.get('deliverables'),list) or not task.get('deliverables'):
        errors.append('deliverables cannot be empty')
    tries = task.get('max_attempts')
    if type(tries) is not int or not 1 <= tries <= 10:
        errors.append('max_attempts must be integer 1..10')
    if type(task.get('human_approval_required')) is not bool:
        errors.append('human_approval_required must be boolean')
    # new_task.py produces intentionally incomplete drafts; reject their placeholders.
    if 'REPLACE' in json.dumps(task,ensure_ascii=False):
        errors.append('Unedited REPLACE placeholder in task contract')
    return errors


def validate_repository(root=ROOT):
    errors = []
    must_exist = ['README.md','AGENTS.md','CLAUDE.md','docs/ORCA-SETUP.md',
                  'docs/HANDOFF.md','docs/ORCHESTRATOR-QUICKSTART.md',
                  'docs/ORCHESTRATOR-SMOKE-PROMPT.md',
                  'scripts/build_worker_spec.py','scripts/check_smoke_output.py',
                  'policies/permissions.md','policies/quality-gates.md',
                  'policies/approval-rules.md','schemas/task.schema.json','schemas/artifact.schema.json']
    for rel in must_exist:
        if not (root / rel).is_file(): errors.append(f'Missing {rel}')
    roles = read_json(root / 'agents/registry.json')
    paths = set()
    for role in roles['roles']:
        rel = role['role_file']
        if rel in paths: errors.append(f'Duplicate role_file: {rel}')
        paths.add(rel)
        if not (root / rel).is_file(): errors.append(f'Missing role: {rel}')
        if not role['primary_skill'].startswith('orca-native:'):
            skill = root / 'skills' / role['primary_skill'] / 'SKILL.md'
            if not skill.is_file(): errors.append(f'Missing primary skill: {skill}')
    if len(roles['roles']) != 14: errors.append(f'Expected 14 roles, found {len(roles["roles"])}')
    for f in sorted((root / 'skills').glob('*/SKILL.md')):
        content = f.read_text(encoding='utf-8')
        match = re.match(r'^---\n(.*?)\n---\n',content,re.S)
        if not match:
            errors.append(f'Missing skill YAML frontmatter: {f.relative_to(root)}')
            continue
        name = re.search(r'(?m)^name:\s*(\S+)\s*$', match.group(1))
        desc = re.search(r'(?m)^description:\s*(.+)$', match.group(1))
        if not name or name.group(1) != f.parent.name:
            errors.append(f'Skill name invalid: {f.relative_to(root)}')
        if not desc or len(desc.group(1)) > 1024:
            errors.append(f'Skill description invalid: {f.relative_to(root)}')
    workflows = read_json(root / 'workflows/manifest.json')
    if len(workflows['phases']) != 9: errors.append('Expected 9 SDLC phases')
    valid_phases = {p['name'] for p in workflows['phases']}
    for phase in workflows['phases']:
        if not (root / phase['playbook']).is_file(): errors.append(f'Missing workflow: {phase["playbook"]}')
        if phase['next'] not in valid_phases: errors.append(f'Invalid next phase: {phase["next"]}')
        for rel in phase['required_template_paths']:
            if not (root / rel).is_file(): errors.append(f'Missing template: {rel}')
    return errors


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--task',type=Path,help='Optional JSON task contract to validate (core fields only)')
    args=parser.parse_args()
    problems=validate_repository()
    if args.task:
        problems += validate_task(read_json(args.task),read_json(ROOT/'agents/registry.json'))
    if problems:
        print('INVALID CONFIG:')
        for p in problems: print(' -',p)
        sys.exit(1)
    print('OK: 14 roles, 9 workflows, local skills and required policies verified.')
    if args.task: print(f'OK: validated core task fields for {args.task}')

if __name__=='__main__': main()
