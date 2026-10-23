# Task tracker: GitLab Issues

Each task is one GitLab issue titled `TASK-NNN: <title>`. Its description, rendered by `SDLC task body`, embeds the
contract between `BEGIN AI-SDLC TASK CONTRACT` and `END AI-SDLC TASK CONTRACT`. That block is the source of truth and
the issue is the only copy. Use the `glab` CLI inside the clone (`tracker.project` is `group/project` when set; pass
it as `--repo`). Flags differ between `glab` versions: confirm with `glab issue <command> --help` before first use.
`SDLC` below is `python "<CORE>/scripts/sdlc.py"`.

| Operation | How |
|---|---|
| Next ID | `glab issue list --all --search "TASK-" --output json`; highest `TASK-NNN` plus one |
| Create | `SDLC task new ...` writes a draft to `.ai-sdlc/runs/tasks/`; complete and `SDLC validate --task <draft>`; `SDLC task body --task <draft> --output <body>`; `glab issue create --title "TASK-NNN: <title>" --description "$(cat <body>)" --label "sdlc,sdlc:<status>,role:<owner>"` |
| Verify round-trip | `glab issue view <n> --output json`, save the `description` to `.ai-sdlc/runs/tasks/TASK-NNN.md`, then `SDLC validate --task` on it must pass |
| Read | Same as round-trip; `SDLC spec --task .ai-sdlc/runs/tasks/TASK-NNN.md`. Comments: `glab issue view <n> --comments` |
| List | `glab issue list --label sdlc --all` |
| Change the contract | Edit the block's JSON, validate, re-render, `glab issue update <n> --description "$(cat <body>)"` |
| Set status | Update `status` in the contract **and** labels in the same step: `glab issue update <n> --unlabel "sdlc:<old>" --label "sdlc:<new>"` |
| Record evidence | `glab issue note <n> --message "<HANDOFF report>"` |
| Dependencies | `dependencies` lists task IDs; mention `Blocked by #<n>` in the description when helpful |
| Link to Orca | After `worker-start`, `orca reference add <issue-url> --worktree id:<worktree id from the receipt>` |
| Close | `glab issue close <n>` after commenting the gate decision (`accepted` or `cancelled`). If `input_artifacts` names a triaged source issue whose tasks are now all closed, comment the outcome there and close it too |

Never put secrets, credentials or private data in issues.
