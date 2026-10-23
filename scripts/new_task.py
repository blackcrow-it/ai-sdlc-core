#!/usr/bin/env python3
"""Create an editable task contract; DOES NOT dispatch any Orca worker."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--id',required=True)
    parser.add_argument('--title',required=True)
    parser.add_argument('--role',required=True)
    parser.add_argument('--project',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    task={
      'task_id':args.id,'project_id':args.project,'title':args.title,
      'owner_agent':args.role,'reviewer_agent':'code-reviewer' if args.role!='code-reviewer' else 'qa-engineer',
      'status':'draft','risk_level':'medium','priority':'medium','dependencies':[],
      'scope':{'allowed_paths':['REPLACE_WITH_ALLOWED_PATH/**'],'forbidden_actions':['deploy_production','edit_secrets']},
      'acceptance_criteria':['REPLACE with observable behavior and verification'],
      'required_checks':['REPLACE_WITH_PROJECT_CHECK'],'deliverables':['REPLACE_WITH_REAL_OUTPUT'],
      'max_attempts':3,'human_approval_required':True,'input_artifacts':[],'orca_run_id':None,'evidence_paths':[]}
    if args.output.exists(): parser.error('Refusing to overwrite existing output')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(task,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Created draft task: {args.output} (edit placeholders before dispatch)')

if __name__=='__main__': main()
