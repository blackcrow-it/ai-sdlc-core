"""Locate and read the installed AI SDLC Core package (roles, phases, schemas, version)."""
import json
import re
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[2]
VERSION_RE = re.compile(r'^(\d+)\.(\d+)\.(\d+)$')
FRONTMATTER_RE = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n', re.S)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def parse_version(text):
    match = VERSION_RE.match(str(text))
    if not match:
        raise ValueError(f'Invalid version: {text!r} (expected MAJOR.MINOR.PATCH)')
    return tuple(int(part) for part in match.groups())


def compat_line(version):
    """Semver compatibility line: MAJOR, or (0, MINOR) while MAJOR is 0 (every 0.x minor may break)."""
    major, minor, _ = parse_version(version)
    return (major,) if major else (0, minor)


def compat_error(required, installed):
    """Return an error message when a project pinned to `required` cannot use `installed`."""
    req, inst = parse_version(required), parse_version(installed)
    if compat_line(required) != compat_line(installed):
        return (f'Project requires AI SDLC Core {required} but {installed} is installed; '
                'this is an incompatible version change (see README "Versioning").')
    if inst < req:
        return f'Project requires AI SDLC Core >= {required}; installed {installed} is older. Update the skill.'
    return None


def read_frontmatter(skill_md):
    """Return (name, description, version) from a SKILL.md frontmatter, or None if absent."""
    match = FRONTMATTER_RE.match(Path(skill_md).read_text(encoding='utf-8'))
    if not match:
        return None
    block = match.group(1)
    def field(pattern):
        found = re.search(pattern, block, re.M)
        return found.group(1).strip() if found else None
    return (field(r'^name:\s*(\S+)\s*$'), field(r'^description:\s*(.+)$'),
            field(r'^\s+version:\s*"?([0-9.]+)"?\s*$'))


class Core:
    def __init__(self, root=CORE_ROOT):
        self.root = Path(root)
        self.manifest = read_json(self.root / 'core.json')
        self.version = self.manifest['version']
        self.registry = read_json(self.root / 'agents/registry.json')
        self.phases = read_json(self.root / 'workflows/manifest.json')['phases']

    @property
    def roles(self):
        return self.registry['roles']

    @property
    def role_ids(self):
        return [r['id'] for r in self.roles]

    @property
    def phase_names(self):
        return [p['name'] for p in self.phases]

    def role(self, role_id):
        for role in self.roles:
            if role['id'] == role_id:
                return role
        raise ValueError(f'Unknown role: {role_id}')

    def phases_owned_by(self, role_id):
        return [p for p in self.phases if p['owner'] == role_id]

    def schema(self, name):
        return read_json(self.root / 'schemas' / f'{name}.schema.json')

    def asset(self, rel):
        return (self.root / 'assets' / rel).read_text(encoding='utf-8')

    @property
    def script(self):
        return (self.root / 'scripts' / 'sdlc.py').as_posix()

    def layout(self, key):
        return self.manifest['project_layout'][key]
