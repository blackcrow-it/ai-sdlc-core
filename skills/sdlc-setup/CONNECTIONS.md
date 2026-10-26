# Third-party connections

Every connection to a service outside the repository is made here, by /sdlc-setup, on each execution host that
will run the affected roles (Orca remote hosts need their own pass). Workers, the Orchestrator and other skills
never log in, register MCP servers, install third-party skills or create keys; they report a blocker that names
`/sdlc-setup connect`.

## Rules for every service

1. **Decide what is needed.** Derive it from the agreed config: the tracker, the CLIs resolved for the roles that use
   the service (`orca.role_agents`, then `orca.agent`) and the detected stack. Skip services the project does not use.
2. **Discover read-only first.** Use only commands whose `--help` confirms them on this host (for example
   `claude mcp list`, `codex mcp list`, `agy mcp list`, `gh auth status`, `rive doctor`). A binary on PATH is not
   a connection.
3. **Ask before each machine change.** Show the exact command, what it writes (user or project scope) and what it
   downloads or sends; run it only on the user's go-ahead. Prefer user scope. A project-scope install writes into
   the repository and is committed separately with the user's approval, never as part of a task.
4. **Secrets and interactive logins stay with the user.** Browser or device logins run in the user's own terminal
   (in Claude Code they can type `! <command>`). API keys are created by the user and stored in their environment or
   secret store; never ask for, echo, log or write a key into the repository, config, tracker, spec or handoff.
   Prefer client config that references an environment variable over a pasted value.
5. **Verify read-only.** After connecting, repeat discovery and make one read-only call through the same CLI. Do
   not create, edit or publish anything to prove the connection.
6. **Record the outcome** per service, CLI and host as `verified`, `unverified` (with the blocker and next step) or
   `declined` in the setup summary. This is machine state: it is not written to `.ai-sdlc/project.json`.

## Google Stitch

Needed when the project has a user interface (detected frontend/mobile frameworks or the user confirms one), for the
CLIs resolved for `ui-ux-designer` and `frontend-developer`. Usage after connection: core `references/DESIGN-TOOLS.md`.

1. Discover: list the CLI's MCP servers and look for a Stitch server.
2. Key: the user creates a Stitch API key (profile picture → Stitch settings → API key → Create key) and stores it
   outside the repository, for example as a user environment variable.
3. Server: register the Stitch MCP server for each CLI following the current official page
   <https://stitch.withgoogle.com/docs/mcp/setup>; Antigravity installs it from Agent Manager → MCP Servers →
   Stitch → Install, which the user does in the app. The endpoint `https://stitch.googleapis.com/mcp` with header
   `X-Goog-Api-Key` comes only from third-party guides; confirm it against the official page before using it.
4. Skills: install `google-labs-code/stitch-skills` with the exact command for that CLI from the repository's current
   README <https://github.com/google-labs-code/stitch-skills> (Apache-2.0, "not an officially supported Google
   product"). It downloads and runs code from the network: rule 3 applies.
5. Verify: ask the CLI, through the Stitch MCP, to list the user's Stitch projects without changing anything.

## Rive

Needed for mobile projects that use Rive (`rive.yaml` detected or the user plans motion). Local work (`rive create`,
`--verify`, `--once`, `inspect`) needs only the CLI; `push`, `pull`, `library` and `--publish` need an account session.

1. Discover: `rive --version` and `rive doctor` (its `auth` line). Offer `rive update` when doctor reports one.
2. Login: when account actions are planned, the user runs `rive login` in their own terminal.
3. Verify: `rive whoami`.

## Issue tracker

Needed for a remote tracker (`github`, `gitlab`, `jira`). `local` and `other` need nothing here.

1. Discover: `gh auth status`, `glab auth status`, or the Jira access reported by the installed `orca-cli` guide;
   `SDLC doctor` repeats this in its `tracker` line.
2. Login: the user runs `gh auth login` / `glab auth login` (or connects Jira in Orca) themselves.
3. Verify: a read-only call against the configured project (for example `gh repo view <owner/repo>`).
