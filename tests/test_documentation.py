"""Documentation promises are enforced through the public CLI and rendered tracker contracts."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import CORE, example_task, run_cli
from sdlc_core.render import build_task_body, build_worker_spec
from sdlc_core.validate import parse_task, validate_task


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.git('init', '-q', '-b', 'main')
        code, out = self.cli('init', '--no-detect', '--name', 'Docs demo', '--language', 'python',
                             '--test-cmd', 'python -m unittest', '--allowed-path', 'docs/**')
        self.assertEqual(code, 0, out)
        self.doc = self.dir / 'docs' / 'SRS.md'
        self.doc.parent.mkdir()
        self.doc.write_text('# SRS\nREQ-001: Existing login behavior.\n', encoding='utf-8')
        self.task = example_task()
        self.task['scope']['allowed_paths'] = ['src/auth/**', 'tests/auth/**', 'docs/**']
        self.task['documentation'] = {
            'assessment': 'Login behavior changes; update the canonical SRS and its requirement trace.',
            'updates': [{'path': 'docs/SRS.md', 'change': 'Document rejection of expired sessions.',
                         'requirement_ids': ['REQ-001']}],
        }
        self.contract = self.dir / 'task.json'
        self.save_task()
        self.git('add', '-A')
        self.git('commit', '-q', '-m', 'Baseline')

    def git(self, *args):
        return subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                               *args], cwd=self.dir, check=True, capture_output=True, text=True).stdout.strip()

    def cli(self, *args):
        return run_cli('-C', str(self.dir), *args)

    def save_task(self):
        self.contract.write_text(json.dumps(self.task), encoding='utf-8')

    def check(self, base='HEAD'):
        return self.cli('docs-check', '--task', str(self.contract), '--base', base)

    def test_unchanged_and_missing_documents_fail(self):
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn('not changed', out)
        self.doc.unlink()
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn('missing', out.lower())

    def test_changed_document_and_new_document_pass(self):
        self.doc.write_text('# SRS\nREQ-001: Expired sessions are rejected.\n', encoding='utf-8')
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn('semantic review', out.lower())
        self.task['documentation']['updates'][0]['path'] = 'docs/auth.md'
        self.save_task()
        (self.dir / 'docs' / 'auth.md').write_text('REQ-001: Expired sessions are rejected.', encoding='utf-8')
        self.assertEqual(self.check()[0], 0)

    def test_committed_and_staged_updates_are_checked(self):
        base = self.git('rev-parse', 'HEAD')
        self.doc.write_text('REQ-001: Updated behavior.\n', encoding='utf-8')
        self.git('add', 'docs/SRS.md')
        self.assertEqual(self.check(base)[0], 0)
        self.git('commit', '-q', '-m', 'Update requirements')
        self.assertEqual(self.check(base)[0], 0)

    def test_committed_update_reverted_in_worktree_does_not_pass(self):
        base = self.git('rev-parse', 'HEAD')
        original = self.doc.read_text(encoding='utf-8')
        self.doc.write_text('REQ-001: Updated behavior.\n', encoding='utf-8')
        self.git('add', 'docs/SRS.md')
        self.git('commit', '-q', '-m', 'Update requirements')
        self.doc.write_text(original, encoding='utf-8')
        code, out = self.check(base)
        self.assertEqual(code, 1, out)
        self.assertIn('not changed', out)

    def test_empty_and_binary_documents_do_not_pass(self):
        for content in (b' \n\t', b'\xff\xfe\x00\x00'):
            with self.subTest(content=content):
                self.doc.write_bytes(content)
                self.assertEqual(self.check()[0], 1)
    def test_requirement_ids_are_not_substring_matches(self):
        self.doc.write_text('REQ-0010: This is a different requirement.\n', encoding='utf-8')
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn('REQ-001', out)

    def test_unicode_and_space_document_paths_pass(self):
        rel = 'docs/Yêu cầu đăng nhập.md'
        self.task['documentation']['updates'][0]['path'] = rel
        self.save_task()
        (self.dir / rel).write_text('REQ-001: Expired sessions are rejected.', encoding='utf-8')
        self.assertEqual(self.check()[0], 0)
        self.git('add', rel)
        self.assertEqual(self.check()[0], 0)

    def test_legacy_contract_validates_but_cannot_pass_documentation_gate(self):
        del self.task['documentation']
        self.save_task()
        self.assertEqual(validate_task(self.task, CORE), [])
        code, out = self.cli('validate', '--task', str(self.contract))
        self.assertEqual(code, 0, out)
        self.assertIn('legacy contract has no documentation assessment', out)
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn('documentation assessment', out.lower())

    def test_no_impact_requires_an_explicit_assessment(self):
        self.task['documentation'] = {'assessment': 'Internal refactor; requirements and public contracts are unchanged.',
                                      'updates': []}
        self.save_task()
        self.assertEqual(self.check()[0], 0)
        self.task['documentation']['assessment'] = ' '
        self.save_task()
        self.assertEqual(self.check()[0], 1)

    def test_document_paths_must_be_exact_inside_scope_and_unprotected(self):
        for path in ('../SRS.md', '/SRS.md', 'C:/SRS.md', 'docs/*.md', 'docs/./SRS.md',
                     'docs//SRS.md', 'other/SRS.md', '.env', '.', 'docs/SRS.md:stream'):
            with self.subTest(path=path):
                task = copy.deepcopy(self.task)
                task['documentation']['updates'][0]['path'] = path
                self.assertTrue(validate_task(task, CORE), path)

    def test_duplicate_and_malformed_updates_are_rejected(self):
        self.task['documentation']['updates'] *= 2
        self.assertTrue(any('Duplicate documentation path' in e for e in validate_task(self.task, CORE)))
        for value in (None, [], {'assessment': 3, 'updates': [None]},
                      {'assessment': 'A sufficiently long assessment', 'updates': 'docs/SRS.md'}):
            with self.subTest(value=value):
                self.task['documentation'] = value
                self.assertTrue(validate_task(self.task, CORE))

    def test_rendered_contract_preserves_documentation_commitments(self):
        config = json.loads((self.dir / '.ai-sdlc/project.json').read_text(encoding='utf-8'))
        body = build_task_body(self.task)
        self.assertEqual(parse_task(body), self.task)
        spec = build_worker_spec(CORE, config, self.task)
        for rendered in (body, spec):
            for value in ('docs/SRS.md', 'REQ-001', 'Document rejection of expired sessions.'):
                self.assertIn(value, rendered)
        self.assertIn('DOCUMENTATION-CONTINUITY.md', spec)
        self.assertIn('docs-check --task', spec)

    def test_draft_requires_documentation_decision(self):
        code, out = self.cli('task', 'new', '--id', 'TASK-NEW', '--title', 'Add a feature', '--role', 'backend-developer')
        self.assertEqual(code, 0, out)
        task = json.loads((self.dir / '.ai-sdlc/tasks/TASK-NEW.json').read_text(encoding='utf-8'))
        self.assertIn('REPLACE', task['documentation']['assessment'])

    def test_invalid_base_is_reported(self):
        code, out = self.check('no-such-commit')
        self.assertEqual(code, 1, out)
        self.assertIn('cannot resolve the base commit', out)


if __name__ == '__main__':
    unittest.main()
