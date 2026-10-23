"""Static validation of the core package, task contracts and path scopes."""
import json
from fnmatch import fnmatchcase as fnmatch

from . import schema
from .core import read_frontmatter

CORE_FILES = [
    'SKILL.md', 'core.json', 'agents/registry.json', 'workflows/manifest.json',
    'policies/permissions.md', 'policies/approval-rules.md', 'policies/quality-gates.md',
    'schemas/task.schema.json', 'schemas/project.schema.json',
    'references/OPERATING-CONTRACT.md', 'references/HANDOFF.md', 'references/ORCA-SETUP.md',
    'references/ORCHESTRATOR-ACTIVATION.md', 'references/ROLE-ASSIGNMENT.md',
    'assets/prompts/orchestrator-activation.md', 'assets/prompts/smoke-orchestrator.md',
    'assets/prompts/worker-spec.md', 'assets/prompts/smoke-ba-spec.md',
    'assets/project/AGENTS.block.md', 'assets/project/CLAUDE.block.md',
    'assets/smoke/project-brief.md', 'templates/project-brief.md',
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
    return errors
