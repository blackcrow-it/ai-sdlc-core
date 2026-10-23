#!/usr/bin/env bash
# Human-in-the-loop reproduction loop (AI SDLC Core, sdlc-debugging).
# Copy this file outside the repository (or into a clearly marked debug location inside the task's
# allowed_paths), edit the steps, and run it. The agent runs the script; the human follows the prompts.
#
# Usage:
#   bash hitl-loop.sh
#
# Helpers:
#   step "<instruction>"        show an instruction, wait for Enter
#   capture VAR "<question>"    show a question, read the answer into VAR
#
# Captured values are printed as KEY=VALUE at the end for the agent to parse. `capture` echoes what is
# typed, so capture observations only. Signing in, passwords and tokens stay a `step` for the human;
# never capture a secret.

set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [Enter when done] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
}

# --- edit below ---------------------------------------------------------

step "Open the app at http://localhost:3000 and sign in."

capture ERRORED "Click the 'Export' button. Did it throw an error? (y/n)"

capture ERROR_MSG "Paste the error message without any tokens or personal data (or 'none'):"

# --- edit above ---------------------------------------------------------

printf '\n--- Captured ---\n'
printf 'ERRORED=%s\n' "$ERRORED"
printf 'ERROR_MSG=%s\n' "$ERROR_MSG"
