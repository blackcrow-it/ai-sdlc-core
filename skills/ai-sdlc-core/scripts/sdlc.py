#!/usr/bin/env python3
"""AI SDLC Core Bootstrap CLI (Python 3.10+, standard library only).

Typical flow in a new repository:
    python <skills-dir>/ai-sdlc-core/scripts/sdlc.py init
    python <skills-dir>/ai-sdlc-core/scripts/sdlc.py doctor
    python <skills-dir>/ai-sdlc-core/scripts/sdlc.py activate

Run with --help for every command. Nothing here creates Orca Runs or workers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sdlc_core.cli import main  # noqa: E402

if __name__ == '__main__':
    sys.exit(main())
