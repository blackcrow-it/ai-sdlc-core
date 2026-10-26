import copy
import json
import tempfile
import unittest
from pathlib import Path

from helpers import CORE, ROOT, example_task, load, run_cli
from sdlc_core.project import validate_config
from sdlc_core.render import build_activation_prompt, build_smoke_prompt, build_worker_spec


class AgentRoutingTests(unittest.TestCase):
    def setUp(self):
        self.config = load(ROOT / 'examples/project.example.json')
        self.config['orca']['agent'] = 'claude'

    def cli(self, directory, *args):
        return run_cli('-C', str(directory), *args)

    def test_setup_persists_multiple_role_agents_and_antigravity_default(self):
        with tempfile.TemporaryDirectory() as directory:
            code, out = self.cli(directory, 'init', '--no-detect', '--test-cmd', 'python -m unittest',
                                 '--allowed-path', 'src/**', '--language', 'python',
                                 '--agent', 'antigravity', '--role-agent', 'business-analyst=claude',
                                 '--role-agent', 'backend-developer=codex',
                                 '--role-agent', 'code-reviewer=claude')
            self.assertEqual(code, 0, out)
            config = load(Path(directory) / '.ai-sdlc/project.json')
            self.assertEqual(config['orca']['agent'], 'antigravity')
            self.assertEqual(config['orca']['role_agents'], {
                'business-analyst': 'claude', 'backend-developer': 'codex', 'code-reviewer': 'claude'})
            code, out = self.cli(directory, 'validate')
            self.assertEqual(code, 0, out)

    def test_dry_run_displays_choices_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            code, out = self.cli(directory, 'init', '--no-detect', '--test-cmd', 'python -m unittest',
                                 '--role-agent', 'frontend-developer=antigravity', '--dry-run')
            self.assertEqual(code, 0, out)
            self.assertIn('"frontend-developer": "antigravity"', out)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_invalid_or_conflicting_assignments_fail_before_writing(self):
        cases = [
            ['backend=codex'], ['backend-developer=unknown'], ['backend-developer='],
            ['backend-developer'], ['backend-developer=codex', 'backend-developer=claude'],
        ]
        for assignments in cases:
            with self.subTest(assignments=assignments), tempfile.TemporaryDirectory() as directory:
                flags = [flag for value in assignments for flag in ('--role-agent', value)]
                code, out = self.cli(directory, 'init', '--no-detect', *flags)
                self.assertEqual(code, 1, out)
                self.assertEqual(list(Path(directory).iterdir()), [])
        with tempfile.TemporaryDirectory() as directory:
            code, out = self.cli(directory, 'init', '--role', 'orchestrator',
                                 '--role-agent', 'backend-developer=codex')
            self.assertEqual(code, 1, out)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_validation_rejects_invalid_map_and_disabled_roles(self):
        for mapping in ({'invented-role': 'codex'}, {'backend-developer': 'unknown'},
                        {'backend-developer': {'agent': 'codex'}}, [], {'backend-developer': ''}):
            with self.subTest(mapping=mapping):
                config = copy.deepcopy(self.config)
                config['orca']['role_agents'] = mapping
                self.assertTrue(validate_config(config, CORE)[0])
        self.config['orca']['role_agents'] = {'technical-writer': 'codex'}
        self.config['sdlc']['enabled_roles'].remove('technical-writer')
        self.assertTrue(validate_config(self.config, CORE)[0])

    def test_legacy_config_uses_default_for_both_workers(self):
        self.config['orca'].pop('role_agents', None)
        self.assertEqual(validate_config(self.config, CORE)[0], [])
        spec = build_worker_spec(CORE, self.config, example_task())
        self.assertIn('Owner CLI: `claude`; reviewer CLI: `claude`', spec)
        self.assertIn('--agent claude', build_smoke_prompt(CORE, self.config))

    def test_worker_and_review_routes_are_resolved_independently(self):
        self.config['orca']['role_agents'] = {
            'backend-developer': 'codex', 'code-reviewer': 'antigravity'}
        task = example_task()
        task.update(owner_agent='backend-developer', reviewer_agent='code-reviewer')
        spec = build_worker_spec(CORE, self.config, task)
        self.assertIn('Owner CLI: `codex`; reviewer CLI: `antigravity`', spec)
        self.assertEqual(task['owner_agent'], 'backend-developer')

    def test_activation_preserves_routes_and_overrides_default_only(self):
        self.config['orca']['role_agents'] = {'business-analyst': 'codex'}
        original = copy.deepcopy(self.config)
        prompt = build_activation_prompt(CORE, self.config, agent='antigravity')
        self.assertIn('default worker CLI (`antigravity`)', prompt)
        self.assertIn('`business-analyst` → `codex`', prompt)
        smoke = build_smoke_prompt(CORE, self.config, agent='antigravity')
        self.assertIn('--agent codex', smoke)
        self.config['orca']['role_agents'] = {}
        self.assertIn('--agent antigravity', build_smoke_prompt(CORE, self.config, agent='antigravity'))
        self.config['orca']['role_agents'] = original['orca']['role_agents']
        self.assertEqual(self.config, original)

    def test_activate_cli_accepts_antigravity_and_uses_ba_override(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.ai-sdlc/project.json'
            path.parent.mkdir()
            self.config['orca']['role_agents'] = {'business-analyst': 'codex'}
            path.write_text(json.dumps(self.config), encoding='utf-8')
            code, prompt = self.cli(directory, 'activate', '--smoke', '--offline', '--stdout',
                                    '--agent', 'antigravity')
            self.assertEqual(code, 0, prompt)
            self.assertIn('--agent codex', prompt)

    def test_init_and_validate_accept_opencode_default_and_role_override(self):
        for default, mapping in [('opencode', 'backend-developer=codex'),
                                 ('codex', 'backend-developer=opencode')]:
            with self.subTest(default=default), tempfile.TemporaryDirectory() as directory:
                code, out = self.cli(directory, 'init', '--no-detect',
                                     '--test-cmd', 'python -m unittest', '--allowed-path', 'src/**',
                                     '--language', 'python',
                                     '--agent', default, '--role-agent', mapping)
                self.assertEqual(code, 0, out)
                config = load(Path(directory) / '.ai-sdlc/project.json')
                self.assertEqual(config['orca']['agent'], default)
                self.assertEqual(config['orca']['role_agents']['backend-developer'], mapping.split('=')[1])
                code, out = self.cli(directory, 'validate')
                self.assertEqual(code, 0, out)

    def test_opencode_worker_and_reviewer_routes_render_independently(self):
        for owner, reviewer in [('opencode', 'antigravity'), ('codex', 'opencode')]:
            with self.subTest(owner=owner, reviewer=reviewer):
                self.config['orca']['role_agents'] = {
                    'backend-developer': owner, 'code-reviewer': reviewer}
                self.assertEqual(validate_config(self.config, CORE)[0], [])
                spec = build_worker_spec(CORE, self.config, example_task())
                self.assertIn(f'Owner CLI: `{owner}`; reviewer CLI: `{reviewer}`', spec)

    def test_activate_opencode_override_preserves_config_and_explicit_role_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.ai-sdlc/project.json'
            path.parent.mkdir()
            self.config['orca']['role_agents'] = {'business-analyst': 'claude'}
            path.write_text(json.dumps(self.config), encoding='utf-8')
            original = path.read_bytes()
            code, prompt = self.cli(directory, 'activate', '--smoke', '--offline', '--stdout',
                                    '--agent', 'opencode')
            self.assertEqual(code, 0, prompt)
            self.assertIn('--agent claude', prompt)
            self.assertEqual(path.read_bytes(), original)
            self.config['orca'].pop('role_agents')
            path.write_text(json.dumps(self.config), encoding='utf-8')
            code, prompt = self.cli(directory, 'activate', '--smoke', '--offline', '--stdout',
                                    '--agent', 'opencode')
            self.assertEqual(code, 0, prompt)
            self.assertIn('--agent opencode', prompt)


class ModelRoutingTests(unittest.TestCase):
    def setUp(self):
        self.config = load(ROOT / 'examples/project.example.json')
        self.config['orca'].update(agent='claude', role_agents={
            'backend-developer': 'codex', 'code-reviewer': 'claude'})

    def cli(self, directory, *args):
        return run_cli('-C', str(directory), *args)

    def test_init_persists_role_models_and_validate_accepts_them(self):
        with tempfile.TemporaryDirectory() as directory:
            code, out = self.cli(directory, 'init', '--no-detect', '--test-cmd', 'python -m unittest',
                                 '--allowed-path', 'src/**', '--language', 'python',
                                 '--role-agent', 'backend-developer=codex',
                                 '--role-agent', 'code-reviewer=claude',
                                 '--role-model', 'backend-developer=gpt-6.1-sol:high',
                                 '--role-model', 'code-reviewer=claude-opus-5-5')
            self.assertEqual(code, 0, out)
            config = load(Path(directory) / '.ai-sdlc/project.json')
            self.assertEqual(config['orca']['role_models'], {
                'backend-developer': {'model': 'gpt-6.1-sol', 'effort': 'high'},
                'code-reviewer': {'model': 'claude-opus-5-5'}})
            code, out = self.cli(directory, 'validate')
            self.assertEqual(code, 0, out)

    def test_init_rejects_bad_role_models_before_writing(self):
        cases = [
            ['--role-model', 'backend-developer=gpt-6.1-sol'],
            ['--role-agent', 'backend-developer=codex', '--role-model', 'backend-developer='],
            ['--role-agent', 'backend-developer=codex', '--role-model', 'backend=gpt-6.1-sol'],
            ['--role-agent', 'backend-developer=codex', '--role-model', 'backend-developer=a',
             '--role-model', 'backend-developer=b'],
            ['--role-agent', 'backend-developer=opencode', '--role-model', 'backend-developer=minimax/MiniMax-M3:high'],
            ['--role-agent', 'backend-developer=opencode2', '--role-model', 'backend-developer=minimax/MiniMax-M3'],
            ['--role-agent', 'backend-developer=codex', '--role-model', 'backend-developer=gpt-6.1-sol:hihg'],
            ['--role-agent', 'backend-developer=codex', '--role-model', 'backend-developer=:high'],
            ['--role-agent', 'backend-developer=codex', '--role-model', 'backend-developer=gpt;rm'],
            ['--role-agent', 'backend-developer=codex', '--role-model', 'backend-developer=$(x)'],
        ]
        for flags in cases:
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as directory:
                code, out = self.cli(directory, 'init', '--no-detect', *flags)
                self.assertEqual(code, 1, out)
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_model_ids_with_colons_keep_unknown_suffixes(self):
        with tempfile.TemporaryDirectory() as directory:
            code, out = self.cli(directory, 'init', '--no-detect', '--dry-run',
                                 '--role-agent', 'backend-developer=codex',
                                 '--role-model', 'backend-developer=vendor:model-v1:0')
            self.assertEqual(code, 0, out)
            self.assertIn('"model": "vendor:model-v1:0"', out)

    def test_validation_rejects_invalid_model_routes(self):
        cases = [
            {'backend-developer': {'model': ''}},
            {'backend-developer': {'model': 'x', 'effort': 'extreme'}},
            {'backend-developer': {'effort': 'high'}},
            {'backend-developer': 'gpt-6.1-sol'},
            {'backend-developer': {'model': 'x', 'agent': 'codex'}},
            {'frontend-developer': {'model': 'x'}},
            {'invented-role': {'model': 'x'}},
            {'backend-developer': {'model': 'gpt`x`'}},
        ]
        for mapping in cases:
            with self.subTest(mapping=mapping):
                config = copy.deepcopy(self.config)
                config['orca']['role_models'] = mapping
                self.assertTrue(validate_config(config, CORE)[0])
        self.config['orca']['role_agents']['technical-writer'] = 'opencode'
        self.config['orca']['role_models'] = {'technical-writer': {'model': 'kimi/k3', 'effort': 'low'}}
        self.assertTrue(validate_config(self.config, CORE)[0])
        self.config['orca']['role_models'] = {'technical-writer': {'model': 'kimi/k3'}}
        errors, warnings = validate_config(self.config, CORE)
        self.assertEqual(errors, [])
        self.assertTrue(any('OpenCode' in w for w in warnings), warnings)

    def test_worker_spec_renders_model_and_effort_per_role(self):
        self.config['orca']['role_models'] = {
            'backend-developer': {'model': 'gpt-6.1-sol', 'effort': 'high'},
            'code-reviewer': {'model': 'claude-opus-5-5'}}
        self.assertEqual(validate_config(self.config, CORE)[0], [])
        task = example_task()
        task.update(owner_agent='backend-developer', reviewer_agent='code-reviewer')
        spec = build_worker_spec(CORE, self.config, task)
        self.assertIn('Owner CLI: `codex` (model `gpt-6.1-sol`, effort `high`); '
                      'reviewer CLI: `claude` (model `claude-opus-5-5`)', spec)
        self.assertIn('`backend-developer` → `gpt-6.1-sol` (`high`)', spec)

    def test_smoke_prompt_carries_launch_flags_and_activation_explains_them(self):
        self.config['orca']['role_agents']['business-analyst'] = 'antigravity'
        self.config['orca']['role_models'] = {
            'business-analyst': {'model': 'gemini-3.8-flash-high', 'effort': 'medium'}}
        smoke = build_smoke_prompt(CORE, self.config)
        self.assertIn('--agent antigravity --model gemini-3.8-flash-high --effort medium', smoke)
        prompt = build_activation_prompt(CORE, self.config, agent='codex')
        self.assertIn('orca.role_models', prompt)
        self.assertIn('`business-analyst` → `gemini-3.8-flash-high` (`medium`)', prompt)

    def test_no_model_pinned_renders_nothing_extra(self):
        self.config['orca'].pop('role_models', None)
        spec = build_worker_spec(CORE, self.config, example_task())
        self.assertNotIn('(model `', spec)
        smoke = build_smoke_prompt(CORE, self.config)
        self.assertIn('--worktree current --agent claude` as allowed', smoke)
        self.assertIn('keep their CLI model config): (none)', smoke)


class AgentIdTests(unittest.TestCase):
    def test_cursor_and_opencode2_are_accepted_everywhere(self):
        for agent in ('cursor', 'opencode2'):
            with self.subTest(agent=agent), tempfile.TemporaryDirectory() as directory:
                code, out = run_cli('-C', directory, 'init', '--no-detect', '--test-cmd', 'python -m unittest',
                                    '--allowed-path', 'src/**', '--language', 'python',
                                    '--agent', agent, '--role-agent', f'business-analyst={agent}')
                self.assertEqual(code, 0, out)
                code, out = run_cli('-C', directory, 'validate')
                self.assertEqual(code, 0, out)
                code, prompt = run_cli('-C', directory, 'activate', '--smoke', '--offline', '--stdout',
                                       '--agent', agent)
                self.assertEqual(code, 0, prompt)
                self.assertIn(f'--agent {agent}', prompt)


if __name__ == '__main__':
    unittest.main()
