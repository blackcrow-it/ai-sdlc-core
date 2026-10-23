import copy
import unittest

from helpers import CORE, CORE_ROOT, ROOT, example_task, load
from sdlc_core import schema
from sdlc_core.core import compat_error, parse_version
from sdlc_core.project import validate_config
from sdlc_core.validate import paths_overlap, validate_core, validate_task


class CorePackageTests(unittest.TestCase):
    def test_core_and_bundled_skills_are_consistent(self):
        self.assertEqual(validate_core(CORE, check_bundled_siblings=True), [])

    def test_single_canonical_version(self):
        self.assertEqual(CORE.manifest['config_schema_version'], '0.1')
        self.assertEqual(len(CORE.roles), 14)
        self.assertEqual(len(CORE.phases), 9)

    def test_role_skills_are_namespaced(self):
        for role in CORE.roles:
            skill = role['primary_skill']
            self.assertTrue(skill.startswith(('sdlc-', 'orca-native:')), skill)

    def test_workflow_skills_drive_the_engine(self):
        for name in CORE.manifest['workflow_skills']:
            skill_dir = CORE_ROOT.parent / name
            text = (skill_dir / 'SKILL.md').read_text(encoding='utf-8')
            self.assertIn('ai-sdlc-core', text, name)
            self.assertIn('scripts/sdlc.py', text, name)
            self.assertTrue((skill_dir / 'agents' / 'openai.yaml').is_file(), name)
            # Mutating workflows run only when the user invokes them.
            if name != 'sdlc-status':
                self.assertIn('disable-model-invocation: true', text, name)
                self.assertIn('allow_implicit_invocation: false',
                              (skill_dir / 'agents' / 'openai.yaml').read_text(encoding='utf-8'), name)
        for name, keyword in (('sdlc-orchestrate', 'APPROVE-SDLC-PLAN'), ('sdlc-smoke', 'START-ORCA-SMOKE-TEST')):
            self.assertIn(keyword, (CORE_ROOT.parent / name / 'SKILL.md').read_text(encoding='utf-8'))

    def test_no_root_level_copies_of_core_content(self):
        for legacy in ('agents', 'workflows', 'policies', 'templates', 'schemas', 'scripts'):
            self.assertFalse((ROOT / legacy).exists(), f'{legacy}/ must live inside skills/ai-sdlc-core')


class VersionTests(unittest.TestCase):
    def test_compatibility_rules(self):
        # 0.x: only patch releases are compatible; every minor may break.
        self.assertIsNone(compat_error('0.1.0', '0.1.0'))
        self.assertIsNone(compat_error('0.1.0', '0.1.4'))
        self.assertIn('older', compat_error('0.1.3', '0.1.0'))
        self.assertIn('incompatible', compat_error('0.1.0', '0.2.0'))
        self.assertIn('incompatible', compat_error('0.1.0', '1.0.0'))
        # >= 1.0: same major and installed >= pinned.
        self.assertIsNone(compat_error('1.0.0', '1.3.1'))
        self.assertIn('older', compat_error('1.4.0', '1.0.0'))
        self.assertIn('incompatible', compat_error('1.0.0', '2.0.0'))

    def test_invalid_version(self):
        with self.assertRaises(ValueError):
            parse_version('2.0')


class SchemaTests(unittest.TestCase):
    def test_subset_validator(self):
        spec = {'type': 'object', 'required': ['a'], 'additionalProperties': False,
                'properties': {'a': {'type': 'array', 'minItems': 1, 'items': {'type': 'integer', 'minimum': 1}}}}
        self.assertEqual(schema.validate({'a': [1, 2]}, spec), [])
        self.assertTrue(schema.validate({}, spec))
        self.assertTrue(schema.validate({'a': []}, spec))
        self.assertTrue(schema.validate({'a': [0]}, spec))
        self.assertTrue(schema.validate({'a': [True]}, spec))
        self.assertTrue(schema.validate({'a': [1], 'b': 1}, spec))

    def test_example_project_config_is_valid(self):
        errors, _ = validate_config(load(ROOT / 'examples' / 'project.example.json'), CORE)
        self.assertEqual(errors, [])

    def test_this_repository_is_managed_by_the_core(self):
        errors, _ = validate_config(load(ROOT / '.ai-sdlc' / 'project.json'), CORE, ROOT)
        self.assertEqual(errors, [])


class TaskContractTests(unittest.TestCase):
    def setUp(self):
        self.config = load(ROOT / 'examples' / 'project.example.json')

    def test_example_task(self):
        self.assertEqual(validate_task(example_task(), CORE), [])
        self.assertEqual(validate_task(example_task(), CORE, self.config), [])

    def test_reject_self_review(self):
        task = example_task()
        task['reviewer_agent'] = task['owner_agent']
        self.assertTrue(any('same role' in e for e in validate_task(task, CORE)))

    def test_reject_unknown_role_and_placeholders(self):
        task = example_task()
        task['owner_agent'] = 'system-root'
        task['deliverables'] = ['REPLACE_WITH_REAL_OUTPUT']
        errors = validate_task(task, CORE)
        self.assertIn('Unknown owner_agent', errors)
        self.assertIn('Unedited REPLACE placeholder in task contract', errors)

    def test_reject_role_disabled_by_project(self):
        config = copy.deepcopy(self.config)
        config['sdlc']['enabled_roles'].remove('database-engineer')
        task = example_task()
        task['owner_agent'] = 'database-engineer'
        self.assertTrue(any('not enabled' in e for e in validate_task(task, CORE, config)))

    def test_reject_protected_and_escaping_paths(self):
        task = example_task()
        task['scope']['allowed_paths'] = ['.github/workflows/ci.yml', '../other/**', '**']
        errors = validate_task(task, CORE, self.config)
        self.assertTrue(any('.github/workflows/ci.yml overlaps' in e for e in errors))
        self.assertTrue(any('repo-relative: ../other/**' in e for e in errors))
        self.assertTrue(any('entry ** overlaps' in e for e in errors))

    def test_path_overlap_rules(self):
        self.assertTrue(paths_overlap('src/**', 'src/legacy/**'))
        self.assertTrue(paths_overlap('src/secrets/**', '**/secrets/**'))
        self.assertFalse(paths_overlap('src/auth/**', '**/*.pem'))
        self.assertFalse(paths_overlap('.ai-sdlc/tasks/**', '.ai-sdlc/project.json'))


class ProjectConfigRuleTests(unittest.TestCase):
    def setUp(self):
        self.config = load(ROOT / 'examples' / 'project.example.json')

    def errors(self, config):
        return validate_config(config, CORE)[0]

    def test_config_cannot_drop_independent_review_or_testing(self):
        config = copy.deepcopy(self.config)
        config['sdlc']['enabled_roles'].remove('code-reviewer')
        config['sdlc']['enabled_phases'].remove('testing')
        errors = self.errors(config)
        self.assertTrue(any('Independent review' in e for e in errors))
        self.assertTrue(any('testing phase' in e for e in errors))

    def test_config_requires_test_command_and_orchestrator(self):
        config = copy.deepcopy(self.config)
        config['commands']['test'] = []
        self.assertTrue(any('commands.test' in e for e in self.errors(config)))
        config = copy.deepcopy(self.config)
        config['sdlc']['enabled_roles'].remove('orchestrator')
        self.assertTrue(any('must include orchestrator' in e for e in self.errors(config)))

    def test_config_rejects_incompatible_core_and_absolute_paths(self):
        config = copy.deepcopy(self.config)
        config['core_version'] = '0.2.0'
        config['scope']['allowed_paths'] = ['/etc/**']
        errors = self.errors(config)
        self.assertTrue(any('incompatible' in e for e in errors))
        self.assertTrue(any('/etc/**' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
