import re
import unittest
from unittest import mock

from helpers import CORE, CORE_ROOT, ROOT, load
from sdlc_core import environment

SETUP = CORE_ROOT.parent / 'sdlc-setup'


def read(path):
    return path.read_text(encoding='utf-8')


class ThirdPartyConnectionTests(unittest.TestCase):
    """Third-party connections are owned by /sdlc-setup; workers only report a blocker."""

    def test_setup_owns_the_connection_procedures(self):
        skill = read(SETUP / 'SKILL.md')
        self.assertIn('CONNECTIONS.md', skill)
        self.assertRegex(skill, r'## \d+\. Connect third-party services')
        self.assertIn('`connect`', skill)
        procedures = read(SETUP / 'CONNECTIONS.md')
        for service in ('## Google Stitch', '## Rive', '## Issue tracker'):
            self.assertIn(service, procedures)
        for status in ('verified', 'unverified', 'declined'):
            self.assertIn(status, procedures)

    def test_workers_never_connect_and_name_setup_instead(self):
        for rel in ('agents/ui-ux-designer.md', 'agents/frontend-developer.md', 'references/DESIGN-TOOLS.md'):
            with self.subTest(file=rel):
                self.assertIn('/sdlc-setup connect', read(CORE.root / rel))
        connect_steps = re.compile(r'`rive login`|Create key|mcp add|plugin marketplace add|npx plugins add|auth login')
        for path in CORE_ROOT.parent.rglob('*'):
            if path.suffix in ('.md', '.py', '.yaml', '.json') and SETUP not in path.parents:
                with self.subTest(file=path.relative_to(CORE_ROOT.parent).as_posix()):
                    self.assertIsNone(connect_steps.search(read(path)))

    def test_doctor_sends_missing_tracker_logins_to_setup(self):
        config = load(ROOT / 'examples/project.example.json')
        config['tracker'].update(provider='github', project='acme/shop')
        with mock.patch.object(environment.shutil, 'which', return_value='gh'), \
                mock.patch.object(environment, '_run', return_value=(1, '')):
            status, _, detail = environment.tracker_checks(config, '.')[0]
        self.assertEqual(status, 'FAIL')
        self.assertIn('/sdlc-setup connect', detail)
        with mock.patch.object(environment.shutil, 'which', return_value=None):
            self.assertIn('/sdlc-setup connect', environment.tracker_checks(config, '.')[0][2])

    def test_connect_mode_does_not_reinitialise(self):
        skill = read(SETUP / 'SKILL.md')
        first_step = re.search(r'## 1\..*?## 2\.', skill, re.S).group(0)
        for phrase in ('`connect`', '/sdlc-status', 'run `SDLC validate`', 'without re-initialising',
                       'full /sdlc-setup first', 'ask again'):
            self.assertIn(phrase, first_step)


if __name__ == '__main__':
    unittest.main()
