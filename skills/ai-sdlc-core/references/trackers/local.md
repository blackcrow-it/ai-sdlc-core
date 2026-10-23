# Task tracker: local files

Task contracts live as JSON files in `.ai-sdlc/tasks/` and are committed with the repository. This is the only copy.
`SDLC` below is `python "<CORE>/scripts/sdlc.py"`.

| Operation | How |
|---|---|
| Next ID | Highest `TASK-NNN` in `.ai-sdlc/tasks/` plus one, zero-padded to three digits |
| Create | `SDLC task new --id TASK-NNN --title "..." --role <owner>` writes `.ai-sdlc/tasks/TASK-NNN.json`; replace every `REPLACE` value, then `SDLC validate --task <file>` |
| Read | Read the file; `SDLC spec --task .ai-sdlc/tasks/TASK-NNN.json` renders the worker spec |
| List | `.ai-sdlc/tasks/*.json`, reporting `task_id`, `owner_agent`, `status`, `dependencies` |
| Set status | Edit `status` in the file (`draft`, `ready`, `in_progress`, `blocked`, `submitted_for_review`, `changes_requested`, `accepted`, `cancelled`), then `SDLC validate --task <file>` |
| Record evidence | Set `orca_run_id`; append report/log paths to `evidence_paths`; the handoff itself follows `references/HANDOFF.md` |
| Dependencies | The `dependencies` array of task IDs; a task is startable when every dependency is `accepted` |
| Link to Orca | Not needed: the spec given to Orca is self-contained and the contract file is committed in the repository |
| Close | `accepted` or `cancelled`; never delete contract files |

Commit contract changes together with the gate decision they record, so the history shows who approved what.
