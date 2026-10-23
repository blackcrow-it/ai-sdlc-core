"""Static validation of the core package, task contracts and path scopes."""
import json
import re
from fnmatch import fnmatchcase as fnmatch
from pathlib import Path

from . import schema
from .core import read_frontmatter, read_skill_meta

CORE_FILES = [
    'SKILL.md', 'core.json', 'THIRD_PARTY_NOTICES.md', 'agents/registry.json', 'workflows/manifest.json',
    'policies/permissions.md', 'policies/approval-rules.md', 'policies/quality-gates.md',
    'schemas/task.schema.json', 'schemas/project.schema.json',
    'references/OPERATING-CONTRACT.md', 'references/HANDOFF.md', 'references/ORCA-SETUP.md',
    'references/ORCHESTRATOR-ACTIVATION.md', 'references/ROLE-ASSIGNMENT.md',
    'assets/prompts/orchestrator-activation.md', 'assets/prompts/smoke-orchestrator.md',
    'assets/prompts/worker-spec.md', 'assets/prompts/smoke-ba-spec.md',
    'assets/project/AGENTS.block.md', 'assets/project/CLAUDE.block.md',
    'assets/smoke/project-brief.md', 'templates/project-brief.md', 'templates/feature-spec.md',
    'templates/pull-request.md', 'references/TASK-AUTHORING.md',
    'references/DOCUMENTATION-CONTINUITY.md', 'templates/documentation-map.md',
    'references/ROLE-PROFILE-CONTRACT.md', 'references/ROLE-PROFILE-SOURCES.md',
    *[f'references/trackers/{name}.md' for name in ('local', 'github', 'gitlab', 'jira', 'other')],
]


def _check_skill(skill_md, expected_name, expected_version, label):
    meta = read_frontmatter(skill_md)
    if meta is None:
        return [f'Missing skill YAML frontmatter: {label}']
    name, desc, version = meta
    errors = []
    if name != expected_name:
        errors.append(f'Skill name invalid: {label} (expected {expected_name}, found {name})')
    if not desc or len(desc) > 1024:
        errors.append(f'Skill description invalid: {label}')
    if version != expected_version:
        errors.append(f'Skill version mismatch: {label} has {version}, core is {expected_version}')
    return errors


def validate_core(core, check_bundled_siblings=False):
    """Integrity of the installed core. With check_bundled_siblings, also verify every bundled
    skill directory next to the core (true in the source repository and full installs)."""
    root, errors = core.root, []
    for rel in CORE_FILES:
        if not (root / rel).is_file():
            errors.append(f'Missing core file: {rel}')
    manifest = core.manifest
    bundled = manifest['bundled_skills']
    seen = set()
    for role in core.roles:
        rel = role['role_file']
        if rel in seen:
            errors.append(f'Duplicate role_file: {rel}')
        seen.add(rel)
        if not (root / rel).is_file():
            errors.append(f'Missing role: {rel}')
        skill = role['primary_skill']
        if not skill.startswith('orca-native:') and skill not in bundled:
            errors.append(f'Primary skill {skill} of {role["id"]} is not a bundled skill')
    if len(core.roles) != manifest['role_count']:
        errors.append(f'Expected {manifest["role_count"]} roles, found {len(core.roles)}')
    if len(core.phases) != manifest['phase_count']:
        errors.append(f'Expected {manifest["phase_count"]} SDLC phases, found {len(core.phases)}')
    names, role_ids = set(core.phase_names), set(core.role_ids)
    for phase in core.phases:
        if not (root / phase['playbook']).is_file():
            errors.append(f'Missing workflow: {phase["playbook"]}')
        if phase['next'] not in names:
            errors.append(f'Invalid next phase: {phase["next"]}')
        if phase['owner'] not in role_ids:
            errors.append(f'Unknown owner {phase["owner"]} for phase {phase["name"]}')
        for rel in phase['required_template_paths']:
            if not (root / rel).is_file():
                errors.append(f'Missing template: {rel}')
    if (root / 'SKILL.md').is_file():
        errors += _check_skill(root / 'SKILL.md', manifest['name'], core.version, 'ai-sdlc-core/SKILL.md')
    if check_bundled_siblings:
        for name in bundled:
            if name == manifest['name']:
                continue
            skill_md = root.parent / name / 'SKILL.md'
            if not skill_md.is_file():
                errors.append(f'Missing bundled skill: {name}')
            else:
                errors += _check_skill(skill_md, name, core.version, f'{name}/SKILL.md')
        errors += validate_invocation(core)
    return errors


SKILL_CALL_RE = re.compile(r'[Cc]all the Skill tool[^.\n]*')
QUOTED_NAME_RE = re.compile(r'"([a-z0-9][a-z0-9-]*)"')
ROUTER_SKILL = 'sdlc-help'


def validate_invocation(core):
    """Invocation invariants of the bundled skills (source repository and full installs):
    - every skill has agents/openai.yaml, user-invoked in both harnesses or in neither;
    - user-invoked skills are listed as workflow skills;
    - "call the Skill tool" steps only name model-invoked skills (a user-invoked skill is unreachable);
    - the router names every skill, so it never sends the user to a skill that does not exist."""
    manifest, parent, errors = core.manifest, core.root.parent, []
    names = [n for n in manifest['bundled_skills'] if (parent / n / 'SKILL.md').is_file()]
    metas = {n: read_skill_meta(parent / n / 'SKILL.md') for n in names}
    callable_skills = {n for n, meta in metas.items() if meta and not meta['user_invoked']}
    callable_skills |= set(manifest['orca_native_skills'])
    for name, meta in metas.items():
        if meta is None:
            continue
        yaml_path = parent / name / 'agents' / 'openai.yaml'
        if not yaml_path.is_file():
            errors.append(f'Missing {name}/agents/openai.yaml')
        else:
            implicit_off = 'allow_implicit_invocation: false' in yaml_path.read_text(encoding='utf-8')
            if implicit_off != meta['user_invoked']:
                errors.append(f'{name}: disable-model-invocation and agents/openai.yaml policy disagree')
        if meta['user_invoked'] and name not in manifest['workflow_skills']:
            errors.append(f'{name} is user-invoked but not listed in core.json workflow_skills')
        for doc in sorted((parent / name).rglob('*.md')):
            for sentence in SKILL_CALL_RE.findall(doc.read_text(encoding='utf-8')):
                for target in QUOTED_NAME_RE.findall(sentence):
                    if target not in callable_skills:
                        errors.append(f'{doc.relative_to(parent).as_posix()}: calls the Skill tool with "{target}", '
                                      'which is not a model-invoked bundled or Orca native skill')
    for name in manifest['workflow_skills']:
        if name not in manifest['bundled_skills']:
            errors.append(f'Workflow skill {name} is not a bundled skill')
    router = parent / ROUTER_SKILL / 'SKILL.md'
    if router.is_file():
        text = router.read_text(encoding='utf-8')
        for name in names:
            if name not in (manifest['name'], ROUTER_SKILL) and f'/{name}`' not in text:
                errors.append(f'{ROUTER_SKILL} does not route to /{name}')
    return errors


def bad_relative_path(pattern):
    """Project paths must be repo-relative POSIX globs without parent traversal."""
    if pattern.startswith(('/', '~')) or '\\' in pattern or (len(pattern) > 1 and pattern[1] == ':'):
        return True
    return '..' in pattern.split('/')


def _static_prefix(pattern):
    parts = []
    for segment in pattern.split('/'):
        if any(ch in segment for ch in '*?['):
            break
        parts.append(segment)
    return '/'.join(parts)


def _within(child, parent):
    return child == parent or child.startswith(parent + '/')


def paths_overlap(allowed, protected):
    """True when an allowed write scope reaches into a protected path.
    Protected patterns without a static directory (e.g. `**/*.pem`) are file-level rules
    enforced at review time, so they do not invalidate a directory scope."""
    if fnmatch(allowed, protected) or fnmatch(protected, allowed):
        return True
    pa, pp = _static_prefix(allowed), _static_prefix(protected)
    if not pp:
        return False
    if not pa:
        return True
    return _within(pa, pp) or _within(pp, pa)


def effective_protected_paths(core, config):
    extra = config['scope']['protected_paths'] if config else []
    return list(dict.fromkeys(core.manifest['default_protected_paths'] + extra))


def effective_forbidden_actions(core, config):
    extra = config['scope']['forbidden_actions'] if config else []
    return list(dict.fromkeys(core.manifest['default_forbidden_actions'] + extra))


CONTRACT_BEGIN = 'BEGIN AI-SDLC TASK CONTRACT'
CONTRACT_END = 'END AI-SDLC TASK CONTRACT'
CONTRACT_RE = re.compile(re.escape(CONTRACT_BEGIN) + r'\s*(\{.*\})\s*' + re.escape(CONTRACT_END), re.S)


def parse_task(text):
    """A task contract is either a JSON file or a tracker issue body that embeds the contract
    between the BEGIN/END marker lines rendered by `sdlc.py task body`."""
    stripped = text.lstrip('﻿').strip()
    if stripped.startswith('{'):
        return json.loads(stripped)
    match = CONTRACT_RE.search(stripped)
    if not match:
        raise ValueError(f'No task contract found: expected JSON or a "{CONTRACT_BEGIN}" block')
    return json.loads(match.group(1))


def load_task(path):
    return parse_task(Path(path).read_text(encoding='utf-8'))


def implementation_roles(core):
    """Roles that change product code; their tasks must agree test seams up front."""
    return {role['id'] for role in core.roles if role['primary_skill'] == 'sdlc-implementation'}


def validate_task_graph(tasks):
    """Checks over a breakdown of contracts -> (errors, warnings): unique IDs, no dependency cycles,
    and a warning for dependencies outside the set (those must already exist and be accepted)."""
    errors, warnings, by_id = [], [], {}
    for task in tasks:
        task_id = task.get('task_id')
        if task_id in by_id:
            errors.append(f'Duplicate task_id {task_id}')
        by_id[task_id] = task
    for task_id, task in by_id.items():
        for dep in task.get('dependencies') or []:
            if dep not in by_id:
                warnings.append(f'{task_id} depends on {dep}, which is not in this set (it must exist and be accepted first)')
    state = {}

    def visit(task_id, path):
        state[task_id] = 'open'
        for dep in by_id[task_id].get('dependencies') or []:
            if dep not in by_id:
                continue
            if state.get(dep) == 'open':
                errors.append('Dependency cycle: ' + ' -> '.join(path[path.index(dep):] + [dep]))
            elif dep not in state:
                visit(dep, path + [dep])
        state[task_id] = 'done'

    for task_id in by_id:
        if task_id not in state:
            visit(task_id, [task_id])
    return errors, warnings


def path_matches(path, pattern):
    """Glob match for repo-relative POSIX paths; `**/x` also matches at the root and `dir/**` the dir."""
    return (fnmatch(path, pattern) or (pattern.startswith('**/') and fnmatch(path, pattern[3:]))
            or (pattern.endswith('/**') and path == pattern[:-3]))


def scope_violations(changed, allowed, protected):
    """Changed paths that fall inside a protected path or outside every allowed path."""
    problems = []
    for path in changed:
        guards = [guard for guard in protected if path_matches(path, guard)]
        if guards:
            problems.append(f'{path}: protected ({", ".join(guards)})')
        elif not any(path_matches(path, pattern) for pattern in allowed):
            problems.append(f'{path}: outside allowed_paths')
    return problems


def validate_task(task, core, config=None):
    """Validate a task contract against the core schema, the role registry and,
    when a project config is given, the project's enabled roles and protected paths."""
    errors = schema.validate(task, core.schema('task'))
    if not isinstance(task, dict):
        return errors
    roles = set(config['sdlc']['enabled_roles']) if config else set(core.role_ids)
    owner, reviewer = task.get('owner_agent'), task.get('reviewer_agent')
    if owner not in core.role_ids:
        errors.append('Unknown owner_agent')
    elif owner not in roles:
        errors.append(f'owner_agent {owner} is not enabled in the project config')
    if reviewer not in core.role_ids:
        errors.append('Unknown reviewer_agent')
    elif reviewer not in roles:
        errors.append(f'reviewer_agent {reviewer} is not enabled in the project config')
    if owner is not None and owner == reviewer:
        errors.append('Owner and reviewer cannot be the same role')
    if isinstance(task.get('dependencies'), list) and task.get('task_id') in task['dependencies']:
        errors.append('Task cannot depend on itself')
    if owner in implementation_roles(core) and not task.get('test_seams'):
        errors.append(f'test_seams is required when owner_agent is {owner} (see references/TASK-AUTHORING.md)')
    if 'REPLACE' in json.dumps(task, ensure_ascii=False):
        errors.append('Unedited REPLACE placeholder in task contract')
    scope = task.get('scope')
    allowed = scope.get('allowed_paths', []) if isinstance(scope, dict) else []
    protected = effective_protected_paths(core, config)
    for path in allowed if isinstance(allowed, list) else []:
        if not isinstance(path, str):
            continue
        if bad_relative_path(path):
            errors.append(f'allowed_paths entry must be repo-relative: {path}')
            continue
        for guard in protected:
            if paths_overlap(path, guard):
                errors.append(f'allowed_paths entry {path} overlaps protected path {guard}')
    documentation = task.get('documentation')
    if isinstance(documentation, dict):
        assessment = documentation.get('assessment')
        if isinstance(assessment, str) and len(assessment.strip()) < 10:
            errors.append('documentation.assessment must explain the impact or why no update is needed')
        updates, seen = documentation.get('updates'), set()
        for update in updates if isinstance(updates, list) else []:
            if not isinstance(update, dict) or not isinstance(update.get('path'), str):
                continue  # malformed shapes are already reported by the schema
            path = update['path']
            if (not path or bad_relative_path(path) or any(c in path for c in '*?[]:\n\r\t\0')
                    or any(part in ('', '.') for part in path.split('/'))):
                errors.append(f'documentation path must be an exact repo-relative file: {path}')
                continue
            if path in seen:
                errors.append(f'Duplicate documentation path: {path}')
            seen.add(path)
            errors += [f'documentation {problem}' for problem in scope_violations(
                [path], [p for p in allowed if isinstance(p, str)] if isinstance(allowed, list) else [], protected)]
    return errors
