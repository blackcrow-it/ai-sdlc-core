import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_worker_spec import generate_spec
from check_smoke_output import check_files

class OrchestratorBootstrapTests(unittest.TestCase):
    def test_spec_contains_explicit_boundary_and_criteria(self):
        spec=generate_spec()
        for key in ('business-analyst','auth-requirements.md','ba-handoff.md',
                    'OBSERVABLE ACCEPTANCE','--outcome succeeded','Open Questions',
                    'policies/permissions.md'):
            self.assertIn(key,spec)

    def test_unknown_role_is_rejected(self):
        with self.assertRaises(ValueError): generate_spec(role='system-root')

    def test_not_used_for_other_roles(self):
        with self.assertRaises(ValueError): generate_spec(role='backend-developer')

    def test_static_output_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            f=Path(folder)/'requirements.md'
            self.assertTrue(check_files({f:['# Authentication Requirements']}))
            f.write_text('# Authentication Requirements\n' + 'Valid contents ' * 25)
            self.assertEqual(check_files({f:['# Authentication Requirements']}),[])

if __name__=='__main__': unittest.main()
