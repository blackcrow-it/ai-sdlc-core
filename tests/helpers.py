import contextlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_ROOT = ROOT / 'skills' / 'ai-sdlc-core'
sys.path.insert(0, str(CORE_ROOT / 'scripts'))

from sdlc_core.cli import main  # noqa: E402
from sdlc_core.core import Core  # noqa: E402

CORE = Core(CORE_ROOT)


def run_cli(*argv):
    """Run the CLI in-process; returns (exit_code, stdout)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(list(argv), core=CORE)
    return code, out.getvalue()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def example_task():
    return load(ROOT / 'examples' / 'task-auth.json')
