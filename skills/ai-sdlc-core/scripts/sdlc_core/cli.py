"""Command-line interface of the AI SDLC Core Bootstrap CLI."""
import argparse
import json
import sys
from pathlib import Path

from .core import Core, read_json
from .environment import install_skills, install_targets, run_doctor, upgrade_project
from .project import APPROVER_ROLES, COMMAND_KEYS, init_project, load_config, refresh_blocks, validate_config, write_text
from .render import (build_activation_prompt, build_smoke_prompt, build_smoke_spec,
                     build_worker_spec, check_smoke_outputs, smoke_paths)
from .validate import effective_forbidden_actions, validate_core, validate_task


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


def _valid_config_or_exit(core, project_dir):
    config = load_config(project_dir, core)
    errors, warnings = validate_config(config, core, project_dir)
    for warning in warnings:
        print(f'WARN: {warning}')
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
            'extra_policies': args.extra_policy, 'detect': not args.no_detect}
    opts.update({f'{key}_commands': getattr(args, f'{key}_cmd') for key in COMMAND_KEYS})
    approvers = {}
    for item in args.approver or []:
        role, _, name = item.partition('=')
        if role not in APPROVER_ROLES or not name.strip():
            print(f'FAIL: --approver expects ROLE=NAME with ROLE in {", ".join(APPROVER_ROLES)}; got {item!r}')
            return 1
        approvers[role] = name.strip()
    opts['approvers'] = approvers
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
    for task_path in args.task:
        problems += [f'{task_path}: {e}' for e in validate_task(read_json(task_path), core, config)]
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


def cmd_task_new(core, args):
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
        'required_checks': cmds['lint'] + cmds['typecheck'] + cmds['test'],
        'deliverables': ['REPLACE_WITH_REAL_OUTPUT'],
        'max_attempts': config['sdlc']['default_max_attempts'], 'human_approval_required': True,
        'input_artifacts': [], 'orca_run_id': None, 'evidence_paths': []}
    out = Path(args.output) if args.output else d / core.layout('tasks_dir') / f'{args.id}.json'
    out = out if out.is_absolute() else d / out
    if out.exists():
        print(f'FAIL: refusing to overwrite {out}')
        return 1
    write_text(out, json.dumps(task, indent=2, ensure_ascii=False) + '\n')
    print(f'Created draft task: {out.relative_to(d).as_posix() if out.is_relative_to(d) else out} '
          '(replace REPLACE placeholders, then `sdlc.py validate --task <file>`)')
    return 0


def cmd_spec(core, args):
    d = _project_dir(args)
    config = _valid_config_or_exit(core, d)
    task = read_json(args.task)
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
        print('Next: open a Claude Code/Codex session for this repository inside Orca and paste the whole file.'
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
        p.add_argument(f'--{flag}', choices=['claude', 'codex'] if flag == 'agent' else None)
    for flag in ('language', 'framework', 'runtime', 'architecture-doc', 'rule', 'rule-file', 'in-scope',
                 'out-of-scope', 'allowed-path', 'protected-path', 'forbidden-action', 'role', 'phase',
                 'extra-policy'):
        p.add_argument(f'--{flag}', action='append', help='repeatable')
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
    p.add_argument('--task', action='append', default=[], help='task contract JSON (repeatable)')

    p = command('doctor', cmd_doctor, 'read-only readiness checks: Python, Git, config, skills, Orca')
    p.add_argument('--offline', action='store_true', help='skip Orca CLI checks')
    p.add_argument('--json', action='store_true')

    p = command('task', cmd_task_new, 'create a draft task contract prefilled from the project config')
    p.add_argument('action', choices=['new'])
    p.add_argument('--id', required=True)
    p.add_argument('--title', required=True)
    p.add_argument('--role', required=True)
    p.add_argument('--reviewer')
    p.add_argument('--output')

    p = command('spec', cmd_spec, 'render a self-contained Orca worker task spec from a task contract')
    p.add_argument('--task', required=True)
    p.add_argument('--output')
    p.add_argument('--stdout', action='store_true')

    p = command('activate', cmd_activate, 'render the Orchestrator activation prompt for this project')
    p.add_argument('--brief', help='repo-relative project brief / objective file')
    p.add_argument('--agent', choices=['claude', 'codex'])
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
