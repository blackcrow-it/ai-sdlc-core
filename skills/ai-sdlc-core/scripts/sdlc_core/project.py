"""Project-side configuration: stack detection, `.ai-sdlc/project.json` creation and validation,
and the managed AGENTS.md / CLAUDE.md blocks. A project repository stores only this data."""
import json
import re
import subprocess
from pathlib import Path

from . import schema
from .core import compat_error
from .validate import bad_relative_path

COMMAND_KEYS = ('install', 'build', 'lint', 'typecheck', 'test', 'e2e', 'security')
BLOCK_BEGIN = '<!-- ai-sdlc-core:begin -->'
BLOCK_END = '<!-- ai-sdlc-core:end -->'
APPROVER_ROLES = ('product_owner', 'tech_lead', 'security_owner', 'release_owner')
DEVELOPER_ROLES = {'frontend-developer', 'backend-developer', 'database-engineer', 'devops-engineer'}
SOURCE_DIRS = ('src', 'lib', 'app', 'apps', 'packages', 'pkg', 'cmd', 'internal', 'server',
               'client', 'web', 'api', 'tests', 'test', 'spec', 'docs')
ARCHITECTURE_DOCS = ('ARCHITECTURE.md', 'docs/architecture.md', 'docs/ARCHITECTURE.md')
RULE_FILES = ('CONTRIBUTING.md', 'docs/CONTRIBUTING.md', 'STYLEGUIDE.md', 'docs/coding-standards.md',
              '.editorconfig')
JS_FRAMEWORKS = ('react', 'next', 'vue', 'nuxt', 'svelte', '@angular/core', 'express', 'fastify',
                 '@nestjs/core', 'electron')
PY_FRAMEWORKS = ('django', 'flask', 'fastapi')


def write_text(path, content):
    """Write UTF-8 text keeping the file's existing line endings (LF for new files)."""
    path = Path(path)
    newline = '\r\n' if path.is_file() and b'\r\n' in path.read_bytes() else '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline=newline)


def config_path(project_dir, core):
    return Path(project_dir) / core.layout('config')


def load_config(project_dir, core):
    path = config_path(project_dir, core)
    if not path.is_file():
        raise FileNotFoundError(f'{core.layout("config")} not found in {project_dir}; run `sdlc.py init` first')
    return json.loads(path.read_text(encoding='utf-8'))


def _read(path):
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def detect_stack(project_dir):
    """Infer languages and commands only from evidence in the repository.
    Returns a dict with languages, frameworks, package_manager, commands and evidence notes."""
    d = Path(project_dir)
    found = {'languages': [], 'frameworks': [], 'package_manager': None,
             'commands': {key: [] for key in COMMAND_KEYS}, 'evidence': []}

    def lang(name):
        if name not in found['languages']:
            found['languages'].append(name)

    def pm(name):
        found['package_manager'] = found['package_manager'] or name

    def add(kind, command, why):
        if command not in found['commands'][kind]:
            found['commands'][kind].append(command)
            found['evidence'].append(f'{kind}: `{command}` <- {why}')

    pkg = d / 'package.json'
    if pkg.is_file():
        try:
            data = json.loads(_read(pkg))
        except ValueError:
            data = {}
        deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
        lang('typescript' if 'typescript' in deps or (d / 'tsconfig.json').is_file() else 'javascript')
        manager = next((name for lock, name in (('pnpm-lock.yaml', 'pnpm'), ('yarn.lock', 'yarn'),
                                                ('bun.lockb', 'bun'), ('bun.lock', 'bun'))
                        if (d / lock).is_file()), 'npm')
        pm(manager)
        add('install', 'npm ci' if manager == 'npm' and (d / 'package-lock.json').is_file()
            else f'{manager} install', 'package.json')
        scripts = data.get('scripts', {})
        for kind, names in (('test', ('test',)), ('lint', ('lint',)), ('build', ('build',)),
                            ('typecheck', ('typecheck', 'type-check', 'tsc')), ('e2e', ('e2e', 'test:e2e'))):
            for name in names:
                if name in scripts and 'no test specified' not in str(scripts[name]):
                    add(kind, f'{manager} run {name}', f'package.json scripts.{name}')
                    break
        found['frameworks'] += [f for f in JS_FRAMEWORKS if f in deps]

    py_markers = [d / n for n in ('pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt',
                                  'requirements-dev.txt', 'pytest.ini', 'tox.ini')]
    if any(p.is_file() for p in py_markers):
        lang('python')
        text = '\n'.join(_read(p) for p in py_markers if p.is_file()).lower()
        runner = 'uv run ' if (d / 'uv.lock').is_file() else 'poetry run ' if (d / 'poetry.lock').is_file() else ''
        pm('uv' if runner == 'uv run ' else 'poetry' if runner else 'pip')
        if 'pytest' in text or (d / 'conftest.py').is_file():
            add('test', f'{runner}pytest' if runner else 'python -m pytest', 'pytest configuration/dependency')
        if 'ruff' in text:
            add('lint', f'{runner}ruff check .', 'ruff configuration/dependency')
        if 'mypy' in text:
            add('typecheck', f'{runner}mypy .', 'mypy configuration/dependency')
        found['frameworks'] += [f for f in PY_FRAMEWORKS if re.search(rf'\b{f}\b', text)]

    if (d / 'go.mod').is_file():
        lang('go'); pm('go')
        add('build', 'go build ./...', 'go.mod')
        add('lint', 'go vet ./...', 'go.mod')
        add('test', 'go test ./...', 'go.mod')
    if (d / 'Cargo.toml').is_file():
        lang('rust'); pm('cargo')
        add('build', 'cargo build', 'Cargo.toml')
        add('test', 'cargo test', 'Cargo.toml')
    if (d / 'pom.xml').is_file():
        lang('java'); pm('maven')
        add('build', 'mvn -B -DskipTests package', 'pom.xml')
        add('test', 'mvn -B test', 'pom.xml')
    gradle = next((p for p in (d / 'build.gradle.kts', d / 'build.gradle') if p.is_file()), None)
    if gradle:
        lang('kotlin' if gradle.suffix == '.kts' else 'java'); pm('gradle')
        tool = './gradlew' if (d / 'gradlew').is_file() else 'gradle'
        add('build', f'{tool} assemble', gradle.name)
        add('test', f'{tool} test', gradle.name)
    if any(d.glob('*.sln')) or any(d.glob('*.csproj')) or any(d.glob('*/*.csproj')):
        lang('csharp'); pm('dotnet')
        add('build', 'dotnet build', '*.sln/*.csproj')
        add('test', 'dotnet test', '*.sln/*.csproj')
    if (d / 'composer.json').is_file():
        lang('php'); pm('composer')
        if '"test"' in _read(d / 'composer.json'):
            add('test', 'composer test', 'composer.json scripts.test')
    if (d / 'Gemfile').is_file():
        lang('ruby'); pm('bundler')
        if 'rspec' in _read(d / 'Gemfile'):
            add('test', 'bundle exec rspec', 'Gemfile rspec')
    if (d / 'pubspec.yaml').is_file():
        flutter = 'flutter:' in _read(d / 'pubspec.yaml')
        lang('dart'); pm('flutter' if flutter else 'dart')
        add('test', 'flutter test' if flutter else 'dart test', 'pubspec.yaml')
    makefile = _read(d / 'Makefile') if (d / 'Makefile').is_file() else ''
    for target in ('test', 'lint', 'build'):
        if re.search(rf'(?m)^{target}\s*:', makefile):
            add(target, f'make {target}', f'Makefile target {target}')
    return found


def _git(project_dir, *args):
    try:
        cp = subprocess.run(['git', *args], cwd=project_dir, capture_output=True, text=True, encoding='utf-8',
                            errors='replace', timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return cp.stdout.strip() if cp.returncode == 0 else None


def suggest_tracker(project_dir):
    """Suggest (provider, project, evidence) from the origin remote; the user confirms the choice."""
    url = _git(project_dir, 'remote', 'get-url', 'origin') or ''
    match = re.search(r'(github\.com|gitlab[^/:]*)[/:]([^\s]+?)(?:\.git)?$', url)
    if not match:
        return 'local', None, 'no GitHub/GitLab origin remote'
    provider = 'github' if match.group(1) == 'github.com' else 'gitlab'
    return provider, match.group(2), f'origin remote on {match.group(1)}'


def detect_default_branch(project_dir):
    remote_head = _git(project_dir, 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD')
    if remote_head:
        return remote_head.split('/', 1)[-1]
    return _git(project_dir, 'symbolic-ref', '--short', 'HEAD') or 'main'


def _slug_id(name):
    slug = re.sub(r'[^A-Z0-9]+', '-', name.upper()).strip('-')
    return f'PROJECT-{slug}' if slug else 'PROJECT-APP'


def build_config(core, project_dir, opts=None):
    """Assemble a project config from explicit options (preferred) and repository evidence."""
    opts = opts or {}
    d = Path(project_dir).resolve()
    detected = detect_stack(d) if opts.get('detect', True) else {
        'languages': [], 'frameworks': [], 'package_manager': None,
        'commands': {key: [] for key in COMMAND_KEYS}, 'evidence': []}
    commands = {key: list(opts.get(f'{key}_commands') or detected['commands'][key]) for key in COMMAND_KEYS}
    name = opts.get('name') or d.name
    config = {
        'schema_version': core.manifest['config_schema_version'],
        'core_version': core.version,
        'project': {
            'id': opts.get('id') or _slug_id(name),
            'name': name,
            'description': opts.get('description') or '',
            'default_branch': opts.get('default_branch') or detect_default_branch(d),
            'repository_url': opts.get('repository_url'),
            'reply_language': opts.get('reply_language') or 'Vietnamese',
        },
        'stack': {
            'languages': list(opts.get('languages') or detected['languages']),
            'frameworks': list(opts.get('frameworks') or dict.fromkeys(detected['frameworks'])),
            'package_manager': opts.get('package_manager') or detected['package_manager'],
            'runtimes': list(opts.get('runtimes') or []),
        },
        'architecture': {
            'style': opts.get('architecture_style') or '',
            'summary': opts.get('architecture_summary') or '',
            'docs': list(opts.get('architecture_docs') or [p for p in ARCHITECTURE_DOCS if (d / p).is_file()]),
            'components': [],
        },
        'commands': commands,
        'coding_rules': {
            'rules': list(opts.get('rules') or []),
            'files': list(opts.get('rule_files') or [p for p in RULE_FILES if (d / p).is_file()]),
        },
        'scope': {
            'in_scope': list(opts.get('in_scope') or []),
            'out_of_scope': list(opts.get('out_of_scope') or []),
            'allowed_paths': list(opts.get('allowed_paths') or [f'{p}/**' for p in SOURCE_DIRS if (d / p).is_dir()]),
            'protected_paths': list(opts.get('protected_paths') or []),
            'forbidden_actions': list(opts.get('forbidden_actions') or []),
        },
        'sdlc': {
            'enabled_phases': list(opts.get('phases') or core.phase_names),
            'enabled_roles': list(opts.get('roles') or core.role_ids),
            'approvers': {**dict.fromkeys(APPROVER_ROLES), **(opts.get('approvers') or {})},
            'default_max_attempts': 2,
            'release_environments': ['staging'],
        },
        'tracker': {
            'provider': opts.get('tracker') or 'local',
            'project': opts.get('tracker_project'),
            'notes': opts.get('tracker_notes') or '',
        },
        'orca': {
            'agent': opts.get('agent') or 'claude',
            'worktree_strategy': 'per-task',
            'max_parallel_workers': 2,
        },
        'extra_policies': list(opts.get('extra_policies') or []),
    }
    evidence = list(detected['evidence'])
    if not opts.get('tracker'):
        provider, project, why = suggest_tracker(d)
        if provider != 'local':
            evidence.append(f'tracker suggestion: `--tracker {provider} --tracker-project {project}` <- {why} '
                            '(config keeps `local` until the user chooses)')
    return config, evidence


def validate_config(config, core, project_dir=None):
    """Return (errors, warnings). Errors block activation; warnings need human review."""
    errors = schema.validate(config, core.schema('project'))
    if errors:
        return errors, []
    warnings = []
    problem = compat_error(config['core_version'], core.version)
    if problem:
        errors.append(problem)
    if config['schema_version'] != core.manifest['config_schema_version']:
        errors.append(f'schema_version {config["schema_version"]} is not supported by core {core.version}')
    if 'REPLACE' in json.dumps(config, ensure_ascii=False):
        errors.append('Unedited REPLACE placeholder in project config')
    sdlc = config['sdlc']
    roles, phases = set(sdlc['enabled_roles']), set(sdlc['enabled_phases'])
    for role in sorted(roles - set(core.role_ids)):
        errors.append(f'Unknown role in sdlc.enabled_roles: {role}')
    for phase in sorted(phases - set(core.phase_names)):
        errors.append(f'Unknown phase in sdlc.enabled_phases: {phase}')
    if 'orchestrator' not in roles:
        errors.append('sdlc.enabled_roles must include orchestrator')
    for phase in core.phases:
        if phase['name'] in phases and phase['owner'] not in roles:
            errors.append(f'Phase {phase["name"]} is enabled but its owner {phase["owner"]} is not')
    if roles & DEVELOPER_ROLES and 'code-reviewer' not in roles:
        errors.append('Independent review is mandatory: enable code-reviewer when developer roles are enabled')
    if 'development' in phases and 'testing' not in phases:
        errors.append('The testing phase cannot be disabled while development is enabled')
    scope, arch, rules = config['scope'], config['architecture'], config['coding_rules']
    referenced = arch['docs'] + rules['files'] + config['extra_policies']
    for path in scope['allowed_paths'] + scope['protected_paths'] + referenced:
        if bad_relative_path(path):
            errors.append(f'Path must be repo-relative POSIX (no "..", no absolute): {path}')
    if project_dir is not None:
        for path in referenced:
            if not bad_relative_path(path) and not (Path(project_dir) / path).is_file():
                warnings.append(f'Referenced file does not exist yet: {path}')
    if not arch['style'] or not arch['summary']:
        warnings.append('architecture.style/summary empty: Software Architect must document it before design gates')
    if not scope['in_scope']:
        warnings.append('scope.in_scope empty: the Orchestrator will ask the human for functional scope')
    if not config['commands']['lint'] and not config['commands']['typecheck']:
        warnings.append('No lint/typecheck command configured: implementation gate relies on tests only')
    if not any(sdlc['approvers'].values()):
        warnings.append('No human approvers named: gates that need approval will stay blocked')
    tracker = config['tracker']
    if tracker['provider'] == 'jira' and not tracker['project']:
        errors.append('tracker.project must be the Jira project key when tracker.provider is jira')
    if tracker['provider'] == 'other' and len(tracker['notes'].strip()) < 20:
        errors.append('tracker.notes must describe the workflow (create, read, status, comment) when provider is other')
    if config['orca']['worktree_strategy'] == 'current':
        warnings.append('orca.worktree_strategy=current is only appropriate for doc-only smoke tests')
    return errors, warnings


def render_block(core, config, name):
    text = core.asset(f'project/{name}.block.md')
    values = {'core_version': core.version, 'reply_language': config['project']['reply_language'],
              'config': core.layout('config')}
    for key, value in values.items():
        text = text.replace('{{' + key + '}}', value)
    return f'{BLOCK_BEGIN}\n{text.strip()}\n{BLOCK_END}\n'


def upsert_block(text, block):
    """Insert or replace the managed block; content outside the markers is preserved."""
    pattern = re.compile(re.escape(BLOCK_BEGIN) + r'.*?' + re.escape(BLOCK_END) + r'\n?', re.S)
    if pattern.search(text):
        return pattern.sub(lambda _: block, text, count=1)
    return (text.rstrip() + '\n\n' + block) if text.strip() else block


def init_project(core, project_dir, opts, force=False, dry_run=False, write_agent_files=True):
    """Create the project config and managed agent-instruction blocks. Returns (actions, evidence)."""
    d = Path(project_dir).resolve()
    target = config_path(d, core)
    if target.exists() and not force:
        raise FileExistsError(f'{core.layout("config")} already exists; use --force to overwrite '
                              'or `sdlc.py upgrade` to move to a newer core')
    config, evidence = build_config(core, d, opts)
    writes = {target: json.dumps(config, indent=2, ensure_ascii=False) + '\n'}
    if write_agent_files:
        for filename, block in (('AGENTS.md', 'AGENTS'), ('CLAUDE.md', 'CLAUDE')):
            path = d / filename
            current = path.read_text(encoding='utf-8') if path.is_file() else ''
            updated = upsert_block(current, render_block(core, config, block))
            if updated != current:
                writes[path] = updated
    gitignore = d / '.gitignore'
    runs_rule = core.layout('runs_dir').rstrip('/') + '/'
    current = gitignore.read_text(encoding='utf-8') if gitignore.is_file() else ''
    if runs_rule not in current.splitlines():
        writes[gitignore] = (current.rstrip() + '\n' if current.strip() else '') + \
            f'# AI SDLC Core generated prompts/specs\n{runs_rule}\n'
    actions = []
    for path, content in writes.items():
        actions.append(f'{"would write" if dry_run else "wrote"} {path.relative_to(d).as_posix()}')
        if not dry_run:
            write_text(path, content)
    return config, actions, evidence


def refresh_blocks(core, config, project_dir, dry_run=False):
    d, actions = Path(project_dir), []
    for filename, block in (('AGENTS.md', 'AGENTS'), ('CLAUDE.md', 'CLAUDE')):
        path = d / filename
        if not path.is_file() or BLOCK_BEGIN not in path.read_text(encoding='utf-8'):
            continue
        current = path.read_text(encoding='utf-8')
        updated = upsert_block(current, render_block(core, config, block))
        if updated != current:
            actions.append(f'{"would refresh" if dry_run else "refreshed"} managed block in {filename}')
            if not dry_run:
                write_text(path, updated)
    return actions
