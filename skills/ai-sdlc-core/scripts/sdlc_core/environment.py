"""Read-only environment checks (`doctor`) and offline skill installation (`install`)."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from .core import compat_line, parse_version, read_frontmatter, read_json
from .project import config_path, load_config, validate_config, write_text
from .validate import validate_core

AGENT_SKILL_DIRS = {'claude': '.claude/skills', 'universal': '.agents/skills'}


def _run(cmd, cwd, timeout=15):
    try:
        cp = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8',
                            errors='replace', timeout=timeout, check=False)
        return cp.returncode, (cp.stdout or cp.stderr or '').strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)


def skill_search_dirs(project_dir):
    home, d = Path.home(), Path(project_dir)
    dirs = [d / '.claude/skills', d / '.agents/skills', home / '.claude/skills',
            home / '.agents/skills', home / '.codex/skills']
    dirs += [Path(p) for p in os.environ.get('AI_SDLC_SKILLS_DIRS', '').split(os.pathsep) if p]
    return list(dict.fromkeys(dirs))


def installed_version(skill_dir, core_name):
    if skill_dir.name == core_name and (skill_dir / 'core.json').is_file():
        return read_json(skill_dir / 'core.json').get('version')
    meta = read_frontmatter(skill_dir / 'SKILL.md')
    return meta[2] if meta else None


def find_installed(core, project_dir):
    """{skill_name: [(dir, version)]} across known agent skill directories."""
    found = {name: [] for name in core.manifest['bundled_skills']}
    for base in skill_search_dirs(project_dir):
        for name in found:
            skill_dir = base / name
            if (skill_dir / 'SKILL.md').is_file():
                found[name].append((skill_dir, installed_version(skill_dir, core.manifest['name'])))
    return found


def run_doctor(core, project_dir, offline=False):
    """Return a list of (status, check, detail) with status OK | WARN | FAIL. Never mutates state."""
    d, out = Path(project_dir).resolve(), []
    add = lambda status, check, detail='': out.append((status, check, detail))  # noqa: E731
    ok_py = sys.version_info >= (3, 10)
    add('OK' if ok_py else 'FAIL', 'python', sys.version.split()[0] + ('' if ok_py else ' (need 3.10+)'))
    core_errors = validate_core(core)
    add('FAIL' if core_errors else 'OK', 'core', f'{core.manifest["name"]} {core.version} at {core.root.as_posix()}')
    for err in core_errors:
        add('FAIL', 'core', err)

    if not shutil.which('git'):
        add('FAIL', 'git', 'git not installed')
    else:
        code, top = _run(['git', 'rev-parse', '--show-toplevel'], d)
        if code != 0:
            add('FAIL', 'git', f'{d} is not a Git repository (Orca worktrees need one)')
        else:
            add('OK', 'git', top)
            if _run(['git', 'rev-parse', '--verify', 'HEAD'], d)[0] != 0:
                add('WARN', 'git', 'No commit yet: Orca worktrees are created from commits')
            elif _run(['git', 'ls-files', '--error-unmatch', core.layout('config')], d)[0] != 0:
                add('WARN', 'git', f'{core.layout("config")} is not committed: worktrees created from HEAD will not see it')
            code, dirty = _run(['git', 'status', '--porcelain'], d)
            if code == 0 and dirty:
                add('WARN', 'git', 'Working tree has uncommitted changes')

    if not config_path(d, core).is_file():
        add('FAIL', 'config', f'{core.layout("config")} missing: run `sdlc.py init`')
    else:
        try:
            config = load_config(d, core)
        except ValueError as exc:
            add('FAIL', 'config', f'Invalid JSON: {exc}')
        else:
            errors, warnings = validate_config(config, core, d)
            add('FAIL' if errors else 'OK', 'config',
                f'{config["project"]["id"]} pinned to core {config.get("core_version")}')
            out.extend(('FAIL', 'config', e) for e in errors)
            out.extend(('WARN', 'config', w) for w in warnings)

    for name, hits in find_installed(core, d).items():
        if not hits:
            if name == core.manifest['name']:
                add('WARN', 'skill', f'{name}: running from {core.root.as_posix()} (not in a known agent skills dir)')
            else:
                add('WARN', 'skill', f'{name}: not installed for any detected agent (run `sdlc.py install`)')
            continue
        for skill_dir, version in hits:
            mismatch = version != core.version
            add('WARN' if mismatch else 'OK', 'skill',
                f'{name} {version} at {skill_dir.as_posix()}' + (f' (core is {core.version})' if mismatch else ''))

    if offline:
        add('WARN', 'orca', 'skipped (--offline); activation still requires a reachable Orca runtime')
        return out
    orca = shutil.which('orca') or shutil.which('orca-ide')
    if not orca:
        add('FAIL', 'orca', 'Orca CLI not found: Orca -> Settings -> General -> Orca CLI (Linux: orca-ide)')
        return out
    code, status = _run([orca, 'status', '--json'], d)
    add('OK' if code == 0 else 'FAIL', 'orca', f'{Path(orca).name} status: '
        + ('reachable' if code == 0 else f'unavailable ({status[:200]})'))
    code, listing = _run([orca, 'skills', 'installed'], d, timeout=30)
    for skill in core.manifest['orca_native_skills']:
        present = code == 0 and any(line.split(' ')[0] == skill for line in listing.splitlines())
        add('OK' if present else 'WARN', 'orca-skill',
            skill + ('' if present else f' not detected: `orca skills install --skill {skill}`'))
    return out


def install_targets(project_dir, scope, agents):
    base = Path.home() if scope == 'global' else Path(project_dir)
    return [base / AGENT_SKILL_DIRS[a] for a in agents]


def install_skills(core, dest_dirs, names=None, force=False, dry_run=False):
    """Copy bundled skills (siblings of the core directory) into agent skill dirs.
    Returns (actions, errors). Refuses to overwrite unless force, and only replaces skill dirs."""
    names = names or core.manifest['bundled_skills']
    source_root, actions, errors = core.root.parent, [], []
    unknown = [n for n in names if n not in core.manifest['bundled_skills']]
    if unknown:
        return [], [f'Not a bundled skill: {", ".join(unknown)}']
    for name in names:
        if not (source_root / name / 'SKILL.md').is_file():
            errors.append(f'{name} not found next to the core ({source_root.as_posix()}); '
                          'install from a full clone or with `npx skills add`')
    if errors:
        return [], errors
    ignore = shutil.ignore_patterns('__pycache__', '*.pyc')
    for dest in dest_dirs:
        for name in names:
            src, target = source_root / name, Path(dest) / name
            if target.exists() and target.resolve() == src.resolve():
                actions.append(f'skip {target.as_posix()} (is the source)')
                continue
            if target.exists():
                if not force:
                    actions.append(f'skip {target.as_posix()} (exists; use --force to replace)')
                    continue
                if not (target / 'SKILL.md').is_file():
                    errors.append(f'Refusing to replace {target.as_posix()}: not a skill directory')
                    continue
            actions.append(f'{"would install" if dry_run else "installed"} {name} {core.version} -> {target.as_posix()}')
            if not dry_run:
                if target.exists():
                    shutil.rmtree(target)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src, target, ignore=ignore)
    return actions, errors


def upgrade_project(core, project_dir, dry_run=False):
    """Move the project pin to the installed core when compatible. Returns (config, messages)."""
    config = load_config(project_dir, core)
    pinned = config['core_version']
    want, have = parse_version(pinned), parse_version(core.version)
    if compat_line(pinned) != compat_line(core.version):
        raise ValueError(f'Incompatible upgrade {pinned} -> {core.version}; follow README "Versioning"')
    if have < want:
        return config, [f'Installed core {core.version} is older than the pinned {pinned}; update the skill instead']
    if have == want:
        return config, [f'Already on core {core.version}']
    config['core_version'] = core.version
    if not dry_run:
        write_text(config_path(project_dir, core), json.dumps(config, indent=2, ensure_ascii=False) + '\n')
    return config, [f'{"would pin" if dry_run else "pinned"} core {pinned} -> {core.version}']
