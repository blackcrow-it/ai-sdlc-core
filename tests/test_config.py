import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_repo import validate_repository,validate_task


class ConfigTests(unittest.TestCase):
    def test_static_config(self):
        self.assertEqual(validate_repository(),[])

    def test_example_task(self):
        task=json.loads((ROOT/'examples/task-auth.json').read_text(encoding='utf-8'))
        registry=json.loads((ROOT/'agents/registry.json').read_text(encoding='utf-8'))
        self.assertEqual(validate_task(task,registry),[])

    def test_reject_self_review(self):
        task=json.loads((ROOT/'examples/task-auth.json').read_text(encoding='utf-8'))
        registry=json.loads((ROOT/'agents/registry.json').read_text(encoding='utf-8'))
        task['reviewer_agent']=task['owner_agent']
        self.assertTrue(any('same role' in e for e in validate_task(task,registry)))

if __name__=='__main__':unittest.main()
