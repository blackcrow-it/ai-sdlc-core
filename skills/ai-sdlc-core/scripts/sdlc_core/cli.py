"""Command-line interface of the AI SDLC Core Bootstrap CLI."""
import argparse
import json
import sys
from difflib import get_close_matches
from pathlib import Path

from .core import Core
from .documentation import check_documentation
from .environment import install_skills, install_targets, run_doctor, upgrade_project
from .project import (APPROVER_ROLES, COMMAND_KEYS, EFFORTS, MODEL_ID, ORCA_AGENTS, TRIAGE_ROLES, changed_paths,
                      init_project, load_config, model_route_errors, refresh_blocks, validate_config, write_text)
from .render import (build_activation_prompt, build_smoke_prompt, build_smoke_spec, build_task_body,
                     build_worker_spec, check_smoke_outputs, smoke_paths)
from .validate import (effective_forbidden_actions, effective_protected_paths, implementation_roles, load_task,
                       scope_violations, validate_core, validate_task, validate_task_graph)


class _Abort(Exception):
    """Raised after the reason has already been printed."""


def _project_dir(args):
    return Path(getattr(args, 'project_dir', None) or '.').resolve()


def _write(project_dir, rel_or_path, content, stdout=False):
    if stdout:
        print(content)
        return
    path = Path(rel_or_path)
    path = path if path.is_absolute() else project_dir / path
    write_text(path, content)
    shown = path.relative_to(project_dir).as_posix() if path.is_relative_to(project_dir) else path.as_posix()
    print(f'WROTE {shown} ({len(content)} characters). Not dispatched to Orca.')


def _valid_config_or_exit(core, project_dir, rendering_to_stdout=False):
    """Load and validate the project config. When the command renders a document to stdout (which agents
    redirect into issue bodies or prompts), warnings go to stderr so they never end up inside it."""
    config = load_config(project_dir, core)
    errors, warnings = validate_config(config, core, project_dir)
    for warning in warnings:
        print(f'WARN: {warning}', file=sys.stderr if rendering_to_stdout else sys.stdout)
    if errors:
        print('INVALID PROJECT CONFIG:')
        for error in errors:
            print(f' - {error}')
        raise _Abort()
    return config


def cmd_version(core, args):
    print(f'{core.manifest["name"]} {core.version}')
    return 0


def cmd_where(core, args):
    info = {'name': core.manifest['name'], 'version': core.version, 'root': core.root.as_posix(),
            'cli': core.script, 'skills_source': core.root.parent.as_posix()}
    print(json.dumps(info, indent=2) if args.json else core.root.as_posix())
    return 0


def cmd_install(core, args):
    dests = [Path(p) for p in args.dest] or install_targets(_project_dir(args), args.scope, args.agent or ['claude', 'universal'])
    actions, errors = install_skills(core, dests, args.skill or None, force=args.force, dry_run=args.dry_run)
    for line in actions:
        print(line)
    for error in errors:
        print(f'FAIL: {error}')
    if not errors and not args.dry_run:
        print('Next: run `sdlc.py init` inside each project repository. Orca native skills are separate:'
              ' `orca skills install --skill orca-cli --skill orchestration`.')
    return 1 if errors else 0


def cmd_init(core, args):
    d = _project_dir(args)
    opts = {'name': args.name, 'id': args.id, 'description': args.description,
            'default_branch': args.default_branch, 'repository_url': args.repository_url,
            'reply_language': args.reply_language, 'languages': args.language,
            'frameworks': args.framework, 'package_manager': args.package_manager,
            'runtimes': args.runtime, 'architecture_style': args.architecture_style,
            'architecture_summary': args.architecture_summary, 'architecture_docs': args.architecture_doc,
            'rules': args.rule, 'rule_files': args.rule_file, 'in_scope': args.in_scope,
            'out_of_scope': args.out_of_scope, 'allowed_paths': args.allowed_path,
            'protected_paths': args.protected_path, 'forbidden_actions': args.forbidden_action,
            'roles': args.role, 'phases': args.phase, 'agent': args.agent,
            'extra_policies': args.extra_policy, 'detect': not args.no_detect,
            'tracker': args.tracker, 'tracker_project': args.tracker_project, 'tracker_notes': args.tracker_notes}
    opts.update({f'{key}_commands': getattr(args, f'{key}_cmd') for key in COMMAND_KEYS})
    approvers = {}
    for item in args.approver or []:
        role, _, name = item.partition('=')
        if role not in APPROVER_ROLES or not name.strip():
            print(f'FAIL: --approver expects ROLE=NAME with ROLE in {", ".join(APPROVER_ROLES)}; got {item!r}')
            return 1
        approvers[role] = name.strip()
    opts['approvers'] = approvers
    labels = {}
    for item in args.triage_label or []:
        role, _, label = item.partition('=')
        if role not in TRIAGE_ROLES or not label.strip():
            print(f'FAIL: --triage-label expects ROLE=LABEL with ROLE in {", ".join(TRIAGE_ROLES)}; got {item!r}')
            return 1
        labels[role] = label.strip()
    opts['triage_labels'] = labels
    role_agents = {}
    for item in args.role_agent or []:
        role, separator, agent = item.partition('=')
        role, agent = role.strip(), agent.strip()
        if not separator or role not in core.role_ids or agent not in ORCA_AGENTS:
            print(f'FAIL: --role-agent expects ROLE=AGENT with an SDLC role and AGENT in '
                  f'{", ".join(ORCA_AGENTS)}; got {item!r}')
            return 1
        if role not in (args.role or core.role_ids):
            print(f'FAIL: --role-agent role is not enabled: {role}')
            return 1
        if role in role_agents and role_agents[role] != agent:
            print(f'FAIL: conflicting --role-agent assignments for {role}')
            return 1
        role_agents[role] = agent
    opts['role_agents'] = role_agents
    role_models = {}
    for item in args.role_model or []:
        role, separator, model = item.partition('=')
        role, model = role.strip(), model.strip()
        head, _, effort = model.rpartition(':')
        route = {'model': head, 'effort': effort} if effort in EFFORTS else {'model': model}
        typo = get_close_matches(effort, EFFORTS, n=1, cutoff=0.75) if effort not in EFFORTS else []
        if (not separator or role not in core.role_ids or not route['model'] or typo
                or not MODEL_ID.fullmatch(route['model'])):
            print(f'FAIL: --role-model expects ROLE=MODEL[:EFFORT] with an SDLC role, a model id of '
                  f'[A-Za-z0-9._:/@+-] and EFFORT in {", ".join(EFFORTS)}; got {item!r}'
                  + (f' (did you mean :{typo[0]}?)' if typo else ''))
            return 1
        if role in role_models and role_models[role] != route:
            print(f'FAIL: conflicting --role-model assignments for {role}')
            return 1
        problems = model_route_errors(role, route, role_agents)
        if problems:
            print(f'FAIL: {problems[0]} (pass --role-agent {role}=AGENT)')
            return 1
        role_models[role] = route
    opts['role_models'] = role_models
    try:
        config, actions, evidence = init_project(core, d, opts, force=args.force, dry_run=args.dry_run,
                                                 write_agent_files=not args.no_agent_files)
    except FileExistsError as exc:
        print(f'FAIL: {exc}')
        return 1
    for line in evidence:
        print(f'DETECTED {line}')
    for line in actions:
        print(line)
    if args.dry_run:
        print(json.dumps(config, indent=2, ensure_ascii=False))
    errors, warnings = validate_config(config, core, d)
    for warning in warnings:
        print(f'WARN: {warning}')
    for error in errors:
        print(f'TODO: {error}')
    print(f'\nAI SDLC Core {core.version} initialised for {config["project"]["id"]}.')
    print('Next steps:')
    print(f'  1. Review/complete {core.layout("config")} (architecture, commands, coding rules, scope, approvers).')
    print('  2. sdlc.py validate')
    print(f'  3. git add {core.layout("config")} AGENTS.md CLAUDE.md .gitignore && git commit')
    print('  4. sdlc.py doctor        (Orca CLI, skills, Git baseline)')
    print('  5. sdlc.py activate      (Orchestrator prompt; optional: sdlc.py activate --smoke)')
    return 0


def cmd_validate(core, args):
    d = _project_dir(args)
    problems = validate_core(core, check_bundled_siblings=args.bundled)
    config, warnings = None, []
    if not args.core_only:
        try:
            config = load_config(d, core)
        except FileNotFoundError as exc:
            problems.append(str(exc))
        else:
            errors, warnings = validate_config(config, core, d)
            problems += errors
    tasks = [load_task(task_path) for task_path in args.task]
    for task_path, task in zip(args.task, tasks):
        problems += [f'{task_path}: {e}' for e in validate_task(task, core, config)]
        if isinstance(task, dict) and 'documentation' not in task:
            warnings.append(f'{task_path}: legacy contract has no documentation assessment; '
                            'add it before execution/acceptance (docs-check will fail).')
    if len(tasks) > 1:
        graph_errors, graph_warnings = validate_task_graph(tasks)
        problems += graph_errors
        warnings = warnings + graph_warnings
    for warning in warnings:
        print(f'WARN: {warning}')
    if problems:
        print('INVALID CONFIG:')
        for problem in problems:
            print(f' - {problem}')
        return 1
    print(f'OK: core {core.version} ({len(core.roles)} roles, {len(core.phases)} workflows, policies, schemas).')
    if config:
        print(f'OK: project {config["project"]["id"]} config valid against core {core.version}.')
    for task_path in args.task:
        print(f'OK: task contract {task_path}')
    if len(tasks) > 1:
        print(f'OK: task graph of {len(tasks)} contracts (unique IDs, no dependency cycles)')
    return 0


def cmd_doctor(core, args):
    results = run_doctor(core, _project_dir(args), offline=args.offline)
    if args.json:
        print(json.dumps([{'status': s, 'check': c, 'detail': d} for s, c, d in results], indent=2))
    else:
        print(f'AI SDLC CORE DOCTOR (read-only) - core {core.version}')
        for status, check, detail in results:
            print(f'[{status:<4}] {check:<10} {detail}')
    failed = any(s == 'FAIL' for s, _, _ in results)
    if not args.json:
        print('Result: ' + ('BLOCKED - fix FAIL items before activating the Orchestrator.' if failed
                            else 'READY (review WARN items).'))
    return 1 if failed else 0


def cmd_task(core, args):
    return cmd_task_body(core, args) if args.action == 'body' else cmd_task_new(core, args)


def cmd_task_new(core, args):
    if not (args.id and args.title and args.role):
        print('FAIL: task new needs --id, --title and --role')
        return 1
    d = _project_dir(args)
    config = _valid_config_or_exit(core, d)
    reviewer = args.reviewer or ('code-reviewer' if args.role != 'code-reviewer' else 'qa-engineer')
    cmds = config['commands']
    task = {
        'task_id': args.id, 'project_id': config['project']['id'], 'title': args.title,
        'owner_agent': args.role, 'reviewer_agent': reviewer, 'status': 'draft',
        'risk_level': 'medium', 'priority': 'medium', 'dependencies': [],
        'scope': {'allowed_paths': ['REPLACE_WITH_NARROW_PATH/**'],
                  'forbidden_actions': effective_forbidden_actions(core, config)},
        'acceptance_criteria': ['REPLACE with observable behavior and verification'],
        **({'test_seams': ['REPLACE with the public interface the tests exercise']}
           if args.role in implementation_roles(core) else {}),
        'documentation': {'assessment': 'REPLACE with affected canonical documents or a justified no-impact decision',
                          'updates': []},
        'required_checks': cmds['lint'] + cmds['typecheck'] + cmds['test'],
        'deliverables': ['REPLACE_WITH_REAL_OUTPUT'],
        'max_attempts': config['sdlc']['default_max_attempts'], 'human_approval_required': True,
        'input_artifacts': [], 'orca_run_id': None, 'evidence_paths': []}
    # Local tracker: contracts live in tasks_dir. Remote trackers: the issue is the record, so the
    # draft goes to the ignored runs dir until it is published per references/trackers/<provider>.md.
    draft_dir = (core.layout('tasks_dir') if config['tracker']['provider'] == 'local'
                 else f'{core.layout("runs_dir")}/tasks')
    out = Path(args.output) if args.output else d / draft_dir / f'{args.id}.json'
    out = out if out.is_absolute() else d / out
    if out.exists():
        print(f'FAIL: refusing to overwrite {out}')
        return 1
    write_text(out, json.dumps(task, indent=2, ensure_ascii=False) + '\n')
    print(f'Created draft task: {out.relative_to(d).as_posix() if out.is_relative_to(d) else out} '
          '(replace REPLACE placeholders, then `sdlc.py validate --task <file>`)')
    return 0


def cmd_task_body(core, args):
    """Print the tracker issue body for a validated contract (title: `<task_id>: <title>`)."""
    if not args.task:
        print('FAIL: task body needs --task <file>')
        return 1
    d = _project_dir(args)
    config = _valid_config_or_exit(core, d, rendering_to_stdout=not args.output)
    task = load_task(args.task)
    errors = validate_task(task, core, config)
    if errors:
        print('INVALID TASK CONTRACT:')
        for error in errors:
            print(f' - {error}')
        return 1
    _write(d, args.output, build_task_body(task), stdout=not args.output)
    return 0


def cmd_scope(core, args):
    """Deterministic scope check: every changed path must match an allowed path and no protected path."""
    d = _project_dir(args)
    config = _valid_config_or_exit(core, d)
    allowed = list(args.allowed)
    if args.task:
        task = load_task(args.task)
        errors = validate_task(task, core, config)
        if errors:
            print('INVALID TASK CONTRACT:')
            for error in errors:
                print(f' - {error}')
            return 1
        allowed += task['scope']['allowed_paths']
    if not allowed:
        print('FAIL: scope needs --task <contract> or at least one --allowed PATTERN')
        return 1
    try:
        base, paths = changed_paths(d, args.base, config['project']['default_branch'])
    except ValueError as exc:
        print(f'FAIL: {exc}')
        return 1
    problems = scope_violations(paths, allowed, effective_protected_paths(core, config))
    print(f'SCOPE base {base[:12]}: {len(paths)} changed path(s); allowed: {", ".join(allowed)}')
    for problem in problems:
        print(f'VIOLATION {problem}')
    if problems:
        print(f'Result: FAIL - {len(problems)} path(s) outside the task scope.')
        return 1
    print('Result: OK - every changed path is inside allowed_paths and outside protected paths.')
    return 0


def cmd_docs_check(core, args):
    """Verify the documentation promises in one task against its actual worktree."""
    d = _project_dir(args)
    config = _valid_config_or_exit(core, d)
    task = load_task(args.task)
    problems = validate_task(task, core, config)
    if not problems:
        try:
            base, paths = changed_paths(d, args.base, config['project']['default_branch'], final_state=True)
        except ValueError as exc:
            problems.append(str(exc))
        else:
            print(f'DOCUMENTATION base {base}: {task["task_id"]}')
            problems += check_documentation(task, d, paths)
    for problem in problems:
        print(f'FAIL: {problem}')
    if problems:
        return 1
    print('OK: declared documentation files were updated and declared requirement IDs are present.')
    print('NOTE: semantic review must verify completeness, no-impact reasoning, traceability and approvals.')
    return 0


def cmd_spec(core, args):
    d = _project_dir(args)
    config = _valid_config_or_exit(core, d, rendering_to_stdout=args.stdout)
    task = load_task(args.task)
    errors = validate_task(task, core, config)
    if errors:
        print('INVALID TASK CONTRACT:')
        for error in errors:
            print(f' - {error}')
        return 1
    rel = args.output or f'{core.layout("runs_dir")}/specs/{task["task_id"]}.md'
    _write(d, rel, build_worker_spec(core, config, task), args.stdout)
    return 0


def cmd_activate(core, args):
    d = _project_dir(args)
    config = _valid_config_or_exit(core, d)
    if args.brief and not (d / args.brief).is_file():
        print(f'FAIL: brief not found: {args.brief}')
        return 1
    failed = [r for r in run_doctor(core, d, offline=args.offline) if r[0] == 'FAIL']
    for _, check, detail in failed:
        print(f'BLOCKER [{check}] {detail}')
    if args.smoke:
        paths = smoke_paths(core)
        _write(d, paths['spec'], build_smoke_spec(core, config))
        prompt, rel = build_smoke_prompt(core, config, args.agent), paths['prompt']
    else:
        prompt = build_activation_prompt(core, config, args.brief, args.agent)
        rel = f'{core.layout("runs_dir")}/orchestrator-activation.md'
    _write(d, rel, prompt, args.stdout)
    if not args.stdout:
        print('Next: open an agent session with core skills and orchestration tools for this repository inside Orca and paste the whole file.'
              ' The Orchestrator must stop for explicit human approval before any Orca mutation.')
    if failed:
        print('NOTE: blockers above must be resolved first; the prompt instructs the Orchestrator to stop and report them.')
    return 0


def cmd_smoke(core, args):
    d = _project_dir(args)
    if args.action == 'spec':
        config = _valid_config_or_exit(core, d)
        _write(d, args.output or smoke_paths(core)['spec'], build_smoke_spec(core, config), args.stdout)
        return 0
    problems = check_smoke_outputs(core, d)
    if problems:
        for issue in problems:
            print('FAIL:', issue)
        print('Not finished. This is only a static check; Orca runtime and semantic review remain separate.')
        return 1
    print('OK: required output paths, section headings and minimum text size present.')
    print('NOTE: real Orca Run/Dispatch, permissions, policy compliance and semantics still require verification.')
    return 0


def cmd_upgrade(core, args):
    d = _project_dir(args)
    try:
        config, messages = upgrade_project(core, d, dry_run=args.dry_run)
    except (FileNotFoundError, ValueError) as exc:
        print(f'FAIL: {exc}')
        return 1
    messages += refresh_blocks(core, config, d, dry_run=args.dry_run)
    for line in messages:
        print(line)
    errors, _ = validate_config(config, core, d)
    for error in errors:
        print(f'TODO: {error}')
    return 1 if errors else 0


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('-C', '--project-dir', default=argparse.SUPPRESS,
                        help='project repository root (default: current directory)')
    parser = argparse.ArgumentParser(prog='sdlc.py', parents=[common],
                                     description='AI SDLC Core Bootstrap CLI: install skills, initialise a '
                                                 'project config and activate the Orca Orchestrator.')
    sub = parser.add_subparsers(dest='command', required=True)

    def command(name, func, help_text):
        p = sub.add_parser(name, parents=[common], help=help_text, description=help_text)
        p.set_defaults(func=func)
        return p

    command('version', cmd_version, 'print the installed core version')
    p = command('where', cmd_where, 'print the core root (paths in core docs are relative to it)')
    p.add_argument('--json', action='store_true')

    p = command('install', cmd_install, 'copy the bundled skills into agent skill directories (offline)')
    p.add_argument('--scope', choices=['global', 'project'], default='global')
    p.add_argument('--agent', action='append', choices=sorted(['claude', 'universal']),
                   help='claude -> .claude/skills, universal -> .agents/skills (Codex and others); default both')
    p.add_argument('--dest', action='append', default=[], help='explicit skills directory (repeatable)')
    p.add_argument('--skill', action='append', help='install only this bundled skill (repeatable)')
    p.add_argument('--force', action='store_true', help='replace existing skill directories')
    p.add_argument('--dry-run', action='store_true')

    p = command('init', cmd_init, 'create .ai-sdlc/project.json and managed AGENTS.md/CLAUDE.md blocks')
    for flag in ('name', 'id', 'description', 'default-branch', 'repository-url', 'reply-language',
                 'package-manager', 'architecture-style', 'architecture-summary', 'agent'):
        p.add_argument(f'--{flag}', choices=ORCA_AGENTS if flag == 'agent' else None)
    p.add_argument('--role-agent', action='append', metavar='ROLE=AGENT',
                   help='CLI override for an enabled SDLC role; others inherit --agent (repeatable)')
    p.add_argument('--role-model', action='append', metavar='ROLE=MODEL[:EFFORT]',
                   help='provider model (and effort) for a role with --role-agent; passed to Orca worker-start (repeatable)')
    for flag in ('language', 'framework', 'runtime', 'architecture-doc', 'rule', 'rule-file', 'in-scope',
                 'out-of-scope', 'allowed-path', 'protected-path', 'forbidden-action', 'role', 'phase',
                 'extra-policy'):
        p.add_argument(f'--{flag}', action='append', help='repeatable')
    p.add_argument('--tracker', choices=['local', 'github', 'gitlab', 'jira', 'other'],
                   help='where task contracts live (default: local)')
    p.add_argument('--tracker-project', help='owner/repo, group/project or Jira project key')
    p.add_argument('--tracker-notes', help='workflow description (required for --tracker other)')
    p.add_argument('--triage-label', action='append', metavar='ROLE=LABEL',
                   help=f'triage label override, ROLE in {", ".join(TRIAGE_ROLES)} (repeatable)')
    p.add_argument('--approver', action='append', metavar='ROLE=NAME',
                   help=f'human approver, ROLE in {", ".join(APPROVER_ROLES)} (repeatable)')
    for key in COMMAND_KEYS:
        p.add_argument(f'--{key}-cmd', action='append', help=f'{key} command (repeatable; overrides detection)')
    p.add_argument('--no-detect', action='store_true', help='do not infer stack/commands from repository files')
    p.add_argument('--no-agent-files', action='store_true', help='do not touch AGENTS.md / CLAUDE.md')
    p.add_argument('--force', action='store_true', help='overwrite an existing project config')
    p.add_argument('--dry-run', action='store_true')

    p = command('validate', cmd_validate, 'validate core integrity, the project config and task contracts')
    p.add_argument('--core-only', action='store_true', help='skip the project config')
    p.add_argument('--bundled', action='store_true', help='also verify sibling bundled skills (source repo)')
    p.add_argument('--task', action='append', default=[],
                   help='task contract file or issue body (repeatable; several also get the dependency-graph check)')

    p = command('doctor', cmd_doctor, 'read-only readiness checks: Python, Git, config, skills, Orca')
    p.add_argument('--offline', action='store_true', help='skip Orca CLI checks')
    p.add_argument('--json', action='store_true')

    p = command('task', cmd_task, 'new: draft a task contract from the project config; '
                'body: render the tracker issue body that embeds a contract')
    p.add_argument('action', choices=['new', 'body'])
    p.add_argument('--id')
    p.add_argument('--title')
    p.add_argument('--role')
    p.add_argument('--task', help='contract file (body)')
    p.add_argument('--reviewer')
    p.add_argument('--output')

    p = command('scope', cmd_scope, 'check that changed paths stay inside the task allowed_paths and outside '
                'protected paths (committed, staged, unstaged and untracked changes)')
    p.add_argument('--task', help='task contract file or issue body')
    p.add_argument('--allowed', action='append', default=[], metavar='PATTERN', help='allowed path glob (repeatable)')
    p.add_argument('--base', help='base commit (default: merge-base with the project default branch)')

    p = command('docs-check', cmd_docs_check, 'check promised documentation updates and requirement IDs '
                '(structural only; semantic review is required)')
    p.add_argument('--task', required=True, help='task contract file or issue body')
    p.add_argument('--base', help='base commit (default: merge-base with the project default branch)')

    p = command('spec', cmd_spec, 'render a self-contained Orca worker task spec from a task contract')
    p.add_argument('--task', required=True)
    p.add_argument('--output')
    p.add_argument('--stdout', action='store_true')

    p = command('activate', cmd_activate, 'render the Orchestrator activation prompt for this project')
    p.add_argument('--brief', help='repo-relative project brief / objective file')
    p.add_argument('--agent', choices=ORCA_AGENTS, help='override the default worker CLI; role assignments still win')
    p.add_argument('--smoke', action='store_true', help='one-worker BA smoke test instead of a full SDLC run')
    p.add_argument('--offline', action='store_true', help='skip Orca reachability checks')
    p.add_argument('--stdout', action='store_true')

    p = command('smoke', cmd_smoke, 'BA smoke test: render its worker spec or statically check its outputs')
    p.add_argument('action', choices=['spec', 'check'])
    p.add_argument('--output')
    p.add_argument('--stdout', action='store_true')

    p = command('upgrade', cmd_upgrade, 'pin the project to the installed (compatible) core version')
    p.add_argument('--dry-run', action='store_true')
    return parser


def main(argv=None, core=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(errors='backslashreplace')
    args = build_parser().parse_args(argv)
    core = core or Core()
    try:
        return args.func(core, args)
    except _Abort:
        return 1
    except FileNotFoundError as exc:
        print(f'FAIL: {exc}')
        return 1
    except json.JSONDecodeError as exc:
        print(f'FAIL: invalid JSON: {exc}')
        return 1
