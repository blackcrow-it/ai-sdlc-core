# Task tracker: other (described by the project)

The project described its own tracker in `.ai-sdlc/project.json` → `tracker.notes` (for example Linear, Azure Boards
or a spreadsheet). Map every operation below onto that description. If the notes do not say how to do one of them,
ask the user once and suggest they add the answer to `tracker.notes`. `SDLC` below is `python "<CORE>/scripts/sdlc.py"`.

Rules that hold for every tracker:

- Each task is exactly one record, titled `TASK-NNN: <title>`. Its body is the output of `SDLC task body`, which embeds
  the contract between `BEGIN AI-SDLC TASK CONTRACT` and `END AI-SDLC TASK CONTRACT`. That block is the source of truth.
- Drafts in `.ai-sdlc/runs/tasks/` (ignored by Git) are scratch copies. Once published, the tracker record is the only
  authoritative copy.
- After every create or edit, read the record back and run `SDLC validate --task` on the saved text.
- Operations to map: next ID, create, read, list, change contract, set status (`draft`, `ready`, `in_progress`,
  `blocked`, `submitted_for_review`, `changes_requested`, `accepted`, `cancelled`), record evidence, dependencies,
  link to the Orca worktree (`orca reference add <url> --worktree ...`), close.
- Never put secrets, credentials or private data in the tracker.
