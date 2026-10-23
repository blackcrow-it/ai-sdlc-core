"""Read-only checks for documentation updates promised by a task contract."""
import re
from pathlib import Path


def check_documentation(task, project_dir, changed_paths):
    """Check a validated contract's declared files and IDs; semantic completeness needs review."""
    documentation = task.get('documentation')
    if documentation is None:
        return ['Missing documentation assessment; update the legacy contract before task acceptance.']
    root, changed, problems = Path(project_dir).resolve(), set(changed_paths), []
    for update in documentation['updates']:
        rel = update['path']
        path = (root / rel).resolve()
        if not path.is_relative_to(root):
            problems.append(f'{rel}: resolves outside the project repository')
            continue
        if path != root / rel:
            problems.append(f'{rel}: documentation path must not traverse a symlink or junction')
            continue
        if not path.is_file():
            problems.append(f'{rel}: missing documentation file')
            continue
        if rel not in changed:
            problems.append(f'{rel}: promised documentation update was not changed since the base')
        try:
            content = path.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            problems.append(f'{rel}: cannot read documentation as UTF-8 text ({exc})')
            continue
        if not content.strip():
            problems.append(f'{rel}: documentation file is empty')
        for req_id in update['requirement_ids']:
            if not re.search(r'(?<![\w-])' + re.escape(req_id) + r'(?![\w-])', content):
                problems.append(f'{rel}: missing requirement ID {req_id}')
    return problems
