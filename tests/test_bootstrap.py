import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import CORE, CORE_ROOT, example_task, load, run_cli
from sdlc_core.environment import tracker_checks
from sdlc_core.project import BLOCK_BEGIN, detect_stack, suggest_tracker
from sdlc_core.validate import parse_task
from sdlc_core.render import SMOKE_HEADINGS, check_headings, smoke_paths

INIT_FLAGS = ['--no-detect', '--name', 'Shop API', '--language', 'typescript', '--test-cmd', 'npm run test',
              '--allowed-path', 'src/**', '--architecture-style', 'modular monolith',
              '--architecture-summary', 'Express REST API', '--in-scope', 'Order management']


class ProjectTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def cli(self, *argv):
        return run_cli('-C', str(self.dir), *argv)

    def init(self, *extra):
        code, out = self.cli('init', *INIT_FLAGS, *extra)
        self.assertEqual(code, 0, out)
        return load(self.dir / '.ai-sdlc' / 'project.json')


class DetectionTests(ProjectTestCase):
    def test_node_project_commands_come_from_package_scripts(self):
        (self.dir / 'package.json').write_text(json.dumps({
            'scripts': {'test': 'jest', 'lint': 'eslint .'},
            'devDependencies': {'typescript': '5'}, 'dependencies': {'express': '4'}}))
        (self.dir / 'pnpm-lock.yaml').write_text('')
        found = detect_stack(self.dir)
        self.assertEqual(found['languages'], ['typescript'])
        self.assertEqual(found['package_manager'], 'pnpm')
        self.assertEqual(found['commands']['test'], ['pnpm run test'])
        self.assertEqual(found['commands']['lint'], ['pnpm run lint'])
        self.assertEqual(found['frameworks'], ['express'])

    def test_no_evidence_no_guessed_commands(self):
        (self.dir / 'package.json').write_text(json.dumps(
            {'scripts': {'test': 'echo "Error: no test specified" && exit 1'}}))
        (self.dir / 'requirements.txt').write_text('requests\n')
        found = detect_stack(self.dir)
        self.assertEqual(found['commands']['test'], [])
        self.assertIn('python', found['languages'])

    def test_go_and_python_pytest(self):
        (self.dir / 'go.mod').write_text('module x\n')
        (self.dir / 'pyproject.toml').write_text('[tool.pytest.ini_options]\n')
        found = detect_stack(self.dir)
        self.assertIn('go test ./...', found['commands']['test'])
        self.assertIn('python -m pytest', found['commands']['test'])


class InitTests(ProjectTestCase):
    def test_init_writes_only_project_config_and_managed_blocks(self):
        (self.dir / 'AGENTS.md').write_text('# Team rules\nKeep this line.\n')
        config = self.init()
        self.assertEqual(config['core_version'], CORE.version)
        self.assertEqual(config['commands']['test'], ['npm run test'])
        agents = (self.dir / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('Keep this line.', agents)
        self.assertEqual(agents.count(BLOCK_BEGIN), 1)
        self.assertIn('.ai-sdlc/runs/', (self.dir / '.gitignore').read_text())
        written = {p.relative_to(self.dir).as_posix() for p in self.dir.rglob('*') if p.is_file()}
        self.assertEqual(written, {'.ai-sdlc/project.json', 'AGENTS.md', 'CLAUDE.md', '.gitignore'})
        code, out = self.cli('validate')
        self.assertEqual(code, 0, out)

    def test_init_refuses_overwrite_and_force_keeps_single_block(self):
        self.init()
        code, out = self.cli('init', *INIT_FLAGS)
        self.assertEqual(code, 1)
        self.assertIn('already exists', out)
        self.init('--force')
        self.assertEqual((self.dir / 'CLAUDE.md').read_text(encoding='utf-8').count(BLOCK_BEGIN), 1)

    def test_preserves_crlf_line_endings(self):
        (self.dir / 'AGENTS.md').write_bytes(b'# Rules\r\nLine\r\n')
        self.init()
        self.assertNotIn(b'\n', (self.dir / 'AGENTS.md').read_bytes().replace(b'\r\n', b''))

    def test_missing_test_command_blocks_validation(self):
        code, out = self.cli('init', '--no-detect', '--allowed-path', 'src/**')
        self.assertEqual(code, 0)
        self.assertIn('TODO', out)
        code, out = self.cli('validate')
        self.assertEqual(code, 1)
        self.assertIn('commands.test', out)

    def test_approver_flag(self):
        config = self.init('--approver', 'product_owner=Jane Doe', '--approver', 'release_owner=Ops Lead')
        self.assertEqual(config['sdlc']['approvers'],
                         {'product_owner': 'Jane Doe', 'tech_lead': None, 'security_owner': None, 'release_owner': 'Ops Lead'})
        code, out = self.cli('init', *INIT_FLAGS, '--force', '--approver', 'cto=Someone')
        self.assertEqual(code, 1)
        self.assertIn('--approver expects ROLE=NAME', out)

    def test_dry_run_writes_nothing(self):
        code, out = self.cli('init', *INIT_FLAGS, '--dry-run')
        self.assertEqual(code, 0)
        self.assertEqual(list(self.dir.iterdir()), [])


class RenderTests(ProjectTestCase):
    def test_task_new_then_spec(self):
        self.init()
        code, out = self.cli('task', 'new', '--id', 'TASK-001', '--title', 'Add orders', '--role', 'backend-developer')
        self.assertEqual(code, 0, out)
        task_file = self.dir / '.ai-sdlc' / 'tasks' / 'TASK-001.json'
        task = load(task_file)
        self.assertEqual(task['required_checks'], ['npm run test'])
        code, out = self.cli('spec', '--task', str(task_file))
        self.assertEqual(code, 1)
        self.assertIn('REPLACE', out)
        task.update(acceptance_criteria=['POST /orders returns 201'], deliverables=['src/orders/'])
        task['scope']['allowed_paths'] = ['src/orders/**']
        task_file.write_text(json.dumps(task))
        code, out = self.cli('spec', '--task', str(task_file))
        self.assertEqual(code, 0, out)
        spec = (self.dir / '.ai-sdlc' / 'runs' / 'specs' / 'TASK-001.md').read_text(encoding='utf-8')
        for key in ('TASK-001', 'backend-developer', 'sdlc-implementation', '`npm run test`', 'src/orders/**',
                    'OBSERVABLE ACCEPTANCE', '--outcome succeeded', 'policies/permissions.md',
                    'modular monolith', '.ai-sdlc/project.json'):
            self.assertIn(key, spec)
        self.assertIn((CORE_ROOT / 'agents/backend-developer.md').as_posix(), spec)

    def test_activate_renders_prompt_with_approval_stop(self):
        self.init()
        (self.dir / 'brief.md').write_text('# Brief\n')
        code, out = self.cli('activate', '--offline', '--brief', 'brief.md')
        self.assertEqual(code, 0, out)
        prompt = (self.dir / '.ai-sdlc' / 'runs' / 'orchestrator-activation.md').read_text(encoding='utf-8')
        for key in (f'AI SDLC Core {CORE.version}', 'APPROVE-SDLC-PLAN', 'orca skills get orchestration --full',
                    'brief.md', 'Shop API', 'npm run test', 'doctor'):
            self.assertIn(key, prompt)
        self.assertNotIn('{{', prompt)

    def test_activate_requires_valid_config(self):
        code, out = self.cli('activate', '--offline')
        self.assertEqual(code, 1)
        self.assertIn('sdlc.py init', out)

    def test_smoke_spec_and_check(self):
        self.init()
        code, out = self.cli('activate', '--smoke', '--offline')
        self.assertEqual(code, 0, out)
        paths = smoke_paths(CORE)
        spec = (self.dir / paths['spec']).read_text(encoding='utf-8')
        for key in ('business-analyst', 'auth-requirements.md', 'ba-handoff.md', 'OBSERVABLE ACCEPTANCE',
                    '--outcome succeeded', 'Open Questions', 'policies/permissions.md', 'Demo authentication'):
            self.assertIn(key, spec)
        self.assertIn('START-ORCA-SMOKE-TEST', (self.dir / paths['prompt']).read_text(encoding='utf-8'))
        self.assertEqual(self.cli('smoke', 'check')[0], 1)
        for key, rel in (('requirements', paths['requirements']), ('handoff', paths['handoff'])):
            body = '\n'.join(SMOKE_HEADINGS[key]) + '\n' + 'Valid contents ' * 25
            (self.dir / rel).write_text(body)
        code, out = self.cli('smoke', 'check')
        self.assertEqual(code, 0, out)

    def test_static_heading_check(self):
        f = self.dir / 'requirements.md'
        self.assertTrue(check_headings({f: ['# Authentication Requirements']}))
        f.write_text('# Authentication Requirements\n' + 'Valid contents ' * 25)
        self.assertEqual(check_headings({f: ['# Authentication Requirements']}), [])


class InstallUpgradeTests(ProjectTestCase):
    def test_install_copies_all_bundled_skills_and_refuses_overwrite(self):
        dest = self.dir / 'skills'
        code, out = self.cli('install', '--dest', str(dest))
        self.assertEqual(code, 0, out)
        for name in CORE.manifest['bundled_skills']:
            self.assertTrue((dest / name / 'SKILL.md').is_file(), name)
        self.assertFalse(list(dest.rglob('__pycache__')))
        code, out = self.cli('install', '--dest', str(dest))
        self.assertIn('exists; use --force', out)
        installed = subprocess.run([sys.executable, str(dest / 'ai-sdlc-core/scripts/sdlc.py'), 'validate',
                                    '--core-only', '--bundled'], capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)

    def test_upgrade_pins_compatible_versions_only(self):
        config = self.init()
        self.assertIn('Already on core', self.cli('upgrade')[1])
        path = self.dir / '.ai-sdlc' / 'project.json'
        config['core_version'] = '1.0.0'
        path.write_text(json.dumps(config))
        code, out = self.cli('upgrade')
        self.assertEqual(code, 1)
        self.assertIn('Incompatible upgrade', out)


class TrackerTests(ProjectTestCase):
    def ready_task(self):
        task = example_task()
        task.update(project_id='PROJECT-SHOP-API', acceptance_criteria=['POST /orders returns 201'])
        task['scope']['allowed_paths'] = ['src/orders/**']
        return task

    def test_issue_body_round_trips_the_contract(self):
        self.init()
        task_file = self.dir / 'task.json'
        task_file.write_text(json.dumps(self.ready_task()))
        code, body = self.cli('task', 'body', '--task', str(task_file))
        self.assertEqual(code, 0, body)
        self.assertIn('BEGIN AI-SDLC TASK CONTRACT', body)
        self.assertIn('- [ ] POST /orders returns 201', body)
        # Simulate the tracker: prose around the body, as an issue view would return it.
        fetched = self.dir / 'issue.md'
        fetched.write_text('TASK-001: Implement login endpoint\n\n' + body + '\n---\ncomment', encoding='utf-8')
        self.assertEqual(parse_task(fetched.read_text(encoding='utf-8')), self.ready_task())
        self.assertEqual(self.cli('validate', '--task', str(fetched))[0], 0)
        code, out = self.cli('spec', '--task', str(fetched))
        self.assertEqual(code, 0, out)
        with self.assertRaises(ValueError):
            parse_task('no contract here')

    def test_drafts_live_outside_the_repo_record_for_remote_trackers(self):
        self.init('--tracker', 'github', '--tracker-project', 'acme/shop')
        self.cli('task', 'new', '--id', 'TASK-001', '--title', 'X', '--role', 'backend-developer')
        self.assertTrue((self.dir / '.ai-sdlc' / 'runs' / 'tasks' / 'TASK-001.json').is_file())
        self.assertFalse((self.dir / '.ai-sdlc' / 'tasks').exists())

    def test_local_tracker_keeps_contracts_in_tasks_dir(self):
        config = self.init()
        self.assertEqual(config['tracker'], {'provider': 'local', 'project': None, 'notes': ''})
        self.cli('task', 'new', '--id', 'TASK-001', '--title', 'X', '--role', 'backend-developer')
        self.assertTrue((self.dir / '.ai-sdlc' / 'tasks' / 'TASK-001.json').is_file())

    def test_tracker_specific_rules(self):
        self.init('--tracker', 'jira')
        code, out = self.cli('validate')
        self.assertEqual(code, 1)
        self.assertIn('Jira project key', out)
        self.init('--force', '--tracker', 'other', '--tracker-notes', 'short')
        self.assertIn('must describe the workflow', self.cli('validate')[1])

    def test_tracker_suggestion_from_remote(self):
        for url, expected in (('https://github.com/acme/api.git', ('github', 'acme/api')),
                              ('git@gitlab.example.com:group/proj.git', ('gitlab', 'group/proj')),
                              ('https://bitbucket.org/acme/api.git', ('local', None))):
            with self.subTest(url=url):
                repo = self.dir / expected[0] / str(abs(hash(url)))
                repo.mkdir(parents=True)
                subprocess.run(['git', 'init', '-q'], cwd=repo, check=True)
                subprocess.run(['git', 'remote', 'add', 'origin', url], cwd=repo, check=True)
                self.assertEqual(suggest_tracker(repo)[:2], expected)

    def test_doctor_and_prompt_name_the_tracker(self):
        config = self.init()
        self.assertEqual(tracker_checks(config, self.dir)[0][0], 'OK')
        config['tracker'].update(provider='github', project='acme/shop')
        self.assertEqual(tracker_checks(config, self.dir, offline=True)[0][0], 'WARN')
        self.cli('activate', '--offline')
        prompt = (self.dir / '.ai-sdlc' / 'runs' / 'orchestrator-activation.md').read_text(encoding='utf-8')
        self.assertIn('references/trackers/local.md', prompt)


class CliProcessTests(unittest.TestCase):
    def test_entry_point_runs_as_script(self):
        script = CORE_ROOT / 'scripts' / 'sdlc.py'
        cp = subprocess.run([sys.executable, str(script), 'version'], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertEqual(cp.stdout.strip(), f'ai-sdlc-core {CORE.version}')

    def test_validate_example_task_from_repo(self):
        repo = CORE_ROOT.parents[1]
        code, out = run_cli('-C', str(repo), 'validate', '--bundled', '--task', str(repo / 'examples' / 'task-auth.json'))
        self.assertEqual(code, 0, out)
        self.assertEqual(example_task()['owner_agent'], 'backend-developer')


if __name__ == '__main__':
    unittest.main()
