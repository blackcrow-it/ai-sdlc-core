# Task tracker: Jira (through Orca)

Each task is one Jira issue in project `tracker.project`, summary `TASK-NNN: <title>`. Its description, rendered by
`SDLC task body`, embeds the contract between `BEGIN AI-SDLC TASK CONTRACT` and `END AI-SDLC TASK CONTRACT`; that block
is the source of truth and the issue is the only copy. All calls use the Orca CLI's Jira integration, which needs a
connected site (`orca jira connection --json` shows `"connected": true`). Add `--site <id>` when several sites exist.
`SDLC` below is `python "<CORE>/scripts/sdlc.py"`.

| Operation | How |
|---|---|
| Issue type | Once per project: `orca jira project types --project <KEY> --json`; use the Task type's id |
| Next ID | `orca jira search "project = <KEY> AND summary ~ \"TASK-\"" --limit 500 --json`; highest `TASK-NNN` plus one |
| Create | `SDLC task new ...` writes a draft to `.ai-sdlc/runs/tasks/`; complete and `SDLC validate --task <draft>`; `SDLC task body --task <draft> --output <body>`; `orca jira create --project <KEY> --type <typeId> --title "TASK-NNN: <title>" --body-file <body> --json`; then `orca jira label add <issue> --label sdlc --label sdlc-<status>` |
| Verify round-trip | `orca jira issue <issue> --json`, save the description text to `.ai-sdlc/runs/tasks/TASK-NNN.md`, then `SDLC validate --task` on it must pass. If Jira formatting breaks the block, stop and report it rather than storing the contract elsewhere |
| Read | Same as round-trip; `SDLC spec --task .ai-sdlc/runs/tasks/TASK-NNN.md`. Comments: `orca jira comment list <issue>` |
| List | `orca jira search "project = <KEY> AND labels = sdlc" --json` |
| Change the contract | Edit the block's JSON, validate, re-render, then update the description (check `orca jira --help` for the edit command of your Orca version) |
| Set status | Update `status` in the contract, move the issue with `orca jira status list <issue>` then `orca jira status set <issue> --to "<transition>"`, and replace the `sdlc-<status>` label. Map: `draft`/`ready` to the To Do state, `in_progress` to In Progress, `submitted_for_review`/`changes_requested` to the review state if the workflow has one, `accepted` to Done, `cancelled` to the workflow's won't-do state |
| Record evidence | `orca jira comment add <issue> --body-file <HANDOFF report>` |
| Dependencies | `dependencies` lists task IDs; mention the blocking issue keys in a comment when helpful |
| Link to Orca | After `worker-start`, `orca reference add <ISSUE-KEY> --worktree id:<worktree id from the receipt>` |
| Close | Transition to Done (`accepted`) or the won't-do state (`cancelled`) after commenting the gate decision. If `input_artifacts` names a triaged source issue whose tasks are now all closed, comment the outcome there and transition it too |

Never put secrets, credentials or private data in issues.
