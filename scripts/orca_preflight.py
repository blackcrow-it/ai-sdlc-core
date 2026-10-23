#!/usr/bin/env python3
"""Read-only local preflight: does not create Orca Runs or workers."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def probe(exe, args):
    try:
        cp = subprocess.run([exe] + args, cwd=ROOT, capture_output=True, text=True, timeout=15, check=False)
        return cp.returncode, (cp.stdout or cp.stderr).strip()[:400]
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, str(e)

def main():
    print('ORCA PHASE 2.1 PREFLIGHT (read-only)')
    print(f'Python: {sys.version.split()[0]}')
    git=shutil.which('git')
    if git:
        status,out=probe(git,['rev-parse','--show-toplevel'])
        print(f'Git repo: {"OK" if status==0 else "NOT INITIALIZED"} {out}')
    else:
        print('Git: NOT INSTALLED')
    orca=shutil.which('orca') or shutil.which('orca-ide')
    if not orca:
        print('Orca CLI: NOT FOUND. Register under Settings -> General -> Orca CLI.')
        return 1
    code,output=probe(orca,['status','--json'])
    print(f'Orca runtime: {"REACHABLE" if code == 0 else "UNAVAILABLE"} {output}')
    if code != 0:
        return 1
    print('Next: `orca skills get orchestration --full`; check enabled agent manually.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
