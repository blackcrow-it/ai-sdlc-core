# Task tracker: GitHub Issues

Each task is one GitHub issue titled `TASK-NNN: <title>`. Its body, rendered by `SDLC task body`, embeds the contract
between `BEGIN AI-SDLC TASK CONTRACT` and `END AI-SDLC TASK CONTRACT`. That block is the source of truth and the
issue is the only copy: nothing is kept in `.ai-sdlc/tasks/`. Use the `gh` CLI inside the clone (it infers the repo;
`tracker.project` is `owner/repo` when set). `SDLC` below is `python "<CORE>/scripts/sdlc.py"`.

| Operation | How |
|---|---|
| Next ID | `gh issue list --state all --search "TASK- in:title" --json title --limit 500`; highest `TASK-NNN` plus one |
| Create | `SDLC task new ...` writes a draft to `.ai-sdlc/runs/tasks/`; complete and `SDLC validate --task <draft>`; `SDLC task body --task <draft> --output .ai-sdlc/runs/tasks/TASK-NNN.body.md`; `gh issue create --title "TASK-NNN: <title>" --body-file <body> --label sdlc --label "sdlc:<status>" --label "role:<owner>"` |
| Verify round-trip | `gh issue view <n> --json body --jq .body > .ai-sdlc/runs/tasks/TASK-NNN.md` then `SDLC validate --task .ai-sdlc/runs/tasks/TASK-NNN.md` must pass |
| Read | Same `gh issue view` command; `SDLC spec --task .ai-sdlc/runs/tasks/TASK-NNN.md` renders the worker spec. Comments: `gh issue view <n> --comments` |
| List | `gh issue list --label sdlc --state all --json number,title,labels,state` |
| Change the contract | Edit the fetched block's JSON, `SDLC validate --task`, re-render with `SDLC task body`, `gh issue edit <n> --body-file <body>` |
| Set status | Update `status` in the contract as above **and** swap the label in the same step: `gh issue edit <n> --remove-label "sdlc:<old>" --add-label "sdlc:<new>"` |
| Record evidence | `gh issue comment <n> --body-file <file>` with Run/Task/Dispatch IDs, commands, exit codes, changed paths (HANDOFF format) |
| Dependencies | `dependencies` lists task IDs; also add `Blocked by: #<n>` at the top of the body text above the summary when helpful |
| Link to Orca | After `worker-start`, `orca reference add <issue-url> --worktree id:<worktree id from the receipt>` |
| Close | `accepted`: `gh issue close <n> --reason completed --comment "<gate decision>"`; `cancelled`: `--reason "not planned"` |

Never put secrets, credentials or private data in issues: they are visible to everyone with repository access.
