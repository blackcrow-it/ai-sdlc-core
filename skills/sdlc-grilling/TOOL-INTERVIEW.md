# Interactive interview adapters

Use with `SKILL.md` after inspecting the current session's tool catalog and instructions. These are conditional
adapters, not API declarations. Use only real callable tools and their current schema; platform/mode/tool rules
override these examples. Keep all interview decisions under the calling workflow's existing permissions.

## Select a channel

| Session capability | Interview behavior |
|---|---|
| A permitted synchronous question tool, such as `AskUserQuestion` or `request_user_input` | Submit a small independent batch using its real question/options fields; read the returned answers before dependent follow-ups |
| A permitted asynchronous question tool, such as `request_user_input_async` | Submit once, keep question IDs pending, continue independent exploration and consume replies delivered later; the immediate return acknowledges submission only |
| A question tool restricted to a mode or purpose that does not apply here | Use another permitted channel; the skill cannot enable a mode, bypass a restriction or make a mandatory decision optional |
| No suitable tool, a specific input the tool cannot represent, or a failed/disabled tool | Briefly explain the limitation and ask a short question in chat, with recommendation/options where useful; return to the tool for questions it can represent |
| A supervised worker without a direct human conversation | Use Orchestrator ask/reply per the installed guide; report a blocker if unavailable |

Prefer the permitted synchronous tool when it fits the question; otherwise use the permitted asynchronous tool.
If both fit equally, choose one and keep the interview coherent. Do not send the same pending question through
multiple tools or also print it as a second actionable Markdown questionnaire. Chat can introduce context and
summarise answers without duplicating the controls. A fallback is per question/capability, not a reason to convert
the rest of a tool-capable interview back to Markdown.

## Adapt inputs without inventing a schema

- On tools with `id`, keep a stable machine identifier such as `recovery_scope`; short headers should fit their
  length limit. On tools with only a title, put the complete prompt in that title and retain IDs in session state.
- If options accept label/description objects, keep labels short and put consequences in the descriptions. If
  options are strings, include a concise consequence in each string or the prompt. Respect native option counts.
- For tools whose UI already supplies free text or "Other", let that affordance carry custom answers. Do not add
  a duplicate "Other" or treat a preselected recommendation as an answer. Omit options for free-text questions
  only when the schema permits it. If free text is unsupported, use chat for that value.
- A tool may permit only optional clarifications, or only Plan mode questions. Use it only for questions that
  meet those restrictions. Required business decisions or final confirmations go through a channel permitted
  for them; do not switch modes or call an unavailable tool to force an interactive UI.
- For an approval restricted to explicit chat text, show the concrete artifact/summary and request the required
  text in chat. Do not embed a dispatch/release approval in a preference selector.

## Delivery and recovery

After an async submission, keep `pending` until a real user reply is delivered. Do not poll or sleep merely to
make silence count as an answer. Respect the host's waiting/cancellation rules. An unrelated user message steers
the ongoing work but does not answer every pending question; a direct correction or custom answer does.

On partial results, retain actual answers and identify which questions remain pending, were skipped or are
deferred. Follow the host's unanswered-question rule; ask a narrower follow-up only when needed to resolve a
required decision or ambiguous reply. Do not resend optional questions after a host says to continue without them.

On a tool error, inspect whether submission occurred. If a question may still be live, avoid a duplicate and
reconcile its state first. If submission failed or the tool is disabled, use the fallback for that question rather
than retrying a known-invalid call. Record open blockers when no permitted response channel exists.
