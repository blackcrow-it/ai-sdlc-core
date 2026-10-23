# AI SDLC Core v2.1 – Reusable Agent Skills Package cho Orca ADE

Một bản **chuẩn, có phiên bản** của toàn bộ tổ chức AI Agent (14 vai trò, 9 workflow SDLC, policy, template,
schema) được đóng gói thành **Agent Skills**. Bạn làm việc hoàn toàn bằng **slash command** (theo phong cách bộ skill
workflow của mattpocock): agent tự chạy engine `sdlc.py`, bạn không cần gõ lệnh Python nào.
Với mỗi repository mới: **cài Skill → `/sdlc-setup` → `/sdlc-orchestrate`**.

Repo này **không** phải plugin Orca tự chạy và không cung cấp AI model. Engine **không bao giờ** tạo Run/Task/worker;
mọi thay đổi trạng thái Orca do Orchestrator thực hiện sau khi con người phê duyệt.

## Mô hình ba lớp

| Lớp | Trách nhiệm | Nằm ở đâu |
|---|---|---|
| **AI SDLC Core** | Một phiên bản chuẩn của agents, workflows, policies, templates, schemas, prompt, engine `sdlc.py` | Skill `ai-sdlc-core`, 5 workflow skill, 5 role skill `sdlc-*` (thư mục `skills/`) |
| **Orca ADE** | Điều phối Agent: Runs, tasks, supervised workers, Git worktree | Orca runtime + native skill `orca-cli`, `orchestration` |
| **Repository dự án** | Chỉ cấu hình đặc thù: ngôn ngữ, kiến trúc, lệnh test/lint/build, quy tắc coding, phạm vi chức năng, đường dẫn được ghi/bị bảo vệ, người phê duyệt | `.ai-sdlc/project.json` (+ task contract trong `.ai-sdlc/tasks/`, khối quản lý trong `AGENTS.md`/`CLAUDE.md`) |

Thứ tự ưu tiên: chỉ thị con người > bằng chứng repo/CI > **policy của core** > `project.json` (chỉ được *siết chặt*,
không bao giờ cấp quyền) > task spec > workflow/role/skill.

## Bắt đầu nhanh

### 1. Cài Skill (một lần mỗi máy)

```bash
orca skills install --skill orca-cli --skill orchestration          # Orca native skills
npx skills add <git-url-hoac-duong-dan-repo-nay> --skill '*' --global --agent claude-code --agent codex --copy -y
```

Lệnh thứ hai cài toàn bộ 11 skill của gói, cú pháp đã kiểm với `skills@1.7.4`; chạy với `--list` để xem trước.
Nếu không dùng npx, từ bản clone chạy `python skills/ai-sdlc-core/scripts/sdlc.py install` (copy offline vào
`~/.claude/skills` và `~/.agents/skills`). Cần Python 3.10+ trên máy vì agent dùng nó làm engine.

### 2. Dùng trong repository dự án

Mở phiên Claude Code hoặc Codex của repository trong Orca, rồi gõ:

| Slash command | Tác dụng |
|---|---|
| `/sdlc-setup` | Agent dò stack từ repo, phỏng vấn bạn theo từng vòng (câu hỏi đánh số, kèm đề xuất) về kiến trúc, lệnh test, quy tắc coding, phạm vi, người phê duyệt; ghi và validate `.ai-sdlc/project.json`, commit sau khi bạn đồng ý |
| `/sdlc-status` | Báo cáo chỉ đọc: core, skill, config, Git baseline, Orca, task, Run đang chạy, và lệnh nên dùng tiếp theo |
| `/sdlc-smoke` | Chứng minh điều phối Orca chạy được: giám sát một worker BA, dừng chờ `START-ORCA-SMOKE-TEST` |
| `/sdlc-task <mục tiêu>` | Tạo một task contract đã validate và worker spec tự chứa, không dispatch |
| `/sdlc-orchestrate <mục tiêu hoặc file brief>` | Phiên hiện tại trở thành Orchestrator: lập DAG, dừng chờ `APPROVE-SDLC-PLAN`, rồi dispatch, theo dõi, kiểm chứng worker |

Ví dụ: `/sdlc-orchestrate Thêm đăng nhập bằng email cho API đơn hàng`.

Các workflow có tác dụng thay đổi (`setup`, `task`, `smoke`, `orchestrate`) có `disable-model-invocation: true`, tức
chỉ chạy khi bạn gọi. `/sdlc-status` thì agent được tự gọi khi bạn hỏi kiểu "AI SDLC đã sẵn sàng chưa?".

Khi setup, `init` chỉ suy luận ngôn ngữ và lệnh **từ bằng chứng** trong repo (`package.json` scripts, lockfile, `go.mod`,
`Cargo.toml`, `pom.xml`, Gradle, `*.csproj`, cấu hình pytest/ruff/mypy, `Makefile`…). Thiếu lệnh test thì agent hỏi bạn,
không đoán. Nội dung `AGENTS.md`/`CLAUDE.md` sẵn có được giữ nguyên; chỉ khối giữa
`<!-- ai-sdlc-core:begin -->` và `<!-- ai-sdlc-core:end -->` được chèn hoặc cập nhật. Chi tiết:
[ORCHESTRATOR-ACTIVATION](skills/ai-sdlc-core/references/ORCHESTRATOR-ACTIVATION.md), [ORCA-SETUP](skills/ai-sdlc-core/references/ORCA-SETUP.md).

## Engine `sdlc.py` (nâng cao: CI, script, gỡ lỗi)

Các workflow skill gọi engine này; bạn chỉ cần dùng trực tiếp khi chạy CI hoặc gỡ lỗi. Python 3.10+, chỉ thư viện chuẩn.
Mọi lệnh nhận `-C <project-dir>` (mặc định thư mục hiện tại).

| Lệnh | Tác dụng |
|---|---|
| `version`, `where [--json]` | Phiên bản và đường dẫn core đã cài (các đường dẫn `agents/...`, `policies/...` trong tài liệu core tính từ đây) |
| `install` | Copy 11 skill vào thư mục skill của agent (offline) |
| `init` | Tạo `.ai-sdlc/project.json`, khối quản lý `AGENTS.md`/`CLAUDE.md`, ignore `.ai-sdlc/runs/` (`--approver ROLE=NAME`, `--dry-run`, `--force`, `--no-detect`, `--no-agent-files`) |
| `validate [--task F] [--core-only] [--bundled]` | Kiểm tra toàn vẹn core, config dự án (schema + quy tắc) và task contract |
| `doctor [--offline] [--json]` | Kiểm tra sẵn sàng, chỉ đọc; exit 1 khi có FAIL |
| `task new --id --title --role` | Tạo task contract nháp trong `.ai-sdlc/tasks/`, điền sẵn checks/forbidden actions từ config |
| `spec --task F` | Render worker spec tự chứa (role, policy, cấu hình dự án, phạm vi, checks) vào `.ai-sdlc/runs/specs/` |
| `activate [--brief F] [--smoke] [--stdout] [--agent claude\|codex]` | Render prompt kích hoạt Orchestrator |
| `smoke spec\|check` | Spec smoke test BA / kiểm tra tĩnh output |
| `upgrade [--dry-run]` | Chuyển `core_version` của dự án lên core đã cài nếu tương thích, làm mới khối quản lý |

## Cấu hình dự án `.ai-sdlc/project.json`

Schema: [`project.schema.json`](skills/ai-sdlc-core/schemas/project.schema.json); ví dụ đầy đủ:
[`examples/project.example.json`](examples/project.example.json).

| Khối | Nội dung |
|---|---|
| `core_version`, `schema_version` | Pin phiên bản core (cùng major, core đã cài ≥ pin) |
| `project` | `id`, tên, mô tả, nhánh mặc định, ngôn ngữ trả lời |
| `stack` | Ngôn ngữ lập trình, framework, package manager, runtime |
| `architecture` | Kiểu kiến trúc, tóm tắt, tài liệu, component → paths |
| `commands` | `install`, `build`, `lint`, `typecheck`, `test` (bắt buộc), `e2e`, `security` |
| `coding_rules` | Quy tắc coding và file quy tắc (`CONTRIBUTING.md`…) |
| `scope` | `in_scope`/`out_of_scope` chức năng, `allowed_paths` (trần ghi), `protected_paths`, `forbidden_actions` bổ sung |
| `sdlc` | Phase/role được bật, người phê duyệt, retry mặc định, môi trường release |
| `orca` | Agent (`claude`/`codex`), chiến lược worktree, số worker song song |
| `extra_policies` | Policy riêng của dự án (chỉ bổ sung ràng buộc) |

Quy tắc bất biến được `validate` cưỡng chế: phải bật `orchestrator`; có developer role thì phải có `code-reviewer`;
có `development` thì phải có `testing`; owner của phase được bật phải được bật; đường dẫn phải tương đối, không `..`;
không còn placeholder `REPLACE`. Protected paths và forbidden actions mặc định của core (`.ai-sdlc/project.json`,
`.github/workflows/**`, `.env*`, khóa/secrets; deploy production, sửa secrets, merge nhánh bảo vệ, force push…)
**luôn** áp dụng; task có `allowed_paths` chạm vào protected path bị từ chối.

## Bản đồ repository

| Đường dẫn | Ý nghĩa |
|---|---|
| `skills/ai-sdlc-core/SKILL.md`, `core.json` | Skill chính và manifest phiên bản (nguồn sự thật duy nhất của version) |
| `skills/ai-sdlc-core/agents/`, `workflows/` | 14 vai trò + `registry.json`; 9 playbook + `manifest.json` |
| `skills/ai-sdlc-core/policies/`, `templates/`, `schemas/` | Policy, mẫu tài liệu, JSON Schema (task, artifact, project) |
| `skills/ai-sdlc-core/references/` | Operating contract, handoff, gán role, thiết lập Orca, kích hoạt Orchestrator |
| `skills/ai-sdlc-core/assets/` | Template prompt/spec, khối `AGENTS.md`/`CLAUDE.md`, brief smoke test |
| `skills/ai-sdlc-core/scripts/` | Bootstrap CLI `sdlc.py` + gói `sdlc_core` |
| `skills/sdlc-{setup,status,task,smoke,orchestrate}/` | 5 workflow skill (slash command) + `agents/openai.yaml` cho Codex |
| `skills/sdlc-{requirements-analysis,system-design,implementation,code-review,testing}/` | 5 role skill cho worker |
| `.ai-sdlc/project.json` | Repo này cũng được quản lý bằng chính core (dogfooding) |
| `examples/` | Config mẫu, task contract mẫu, hồ sơ DAG demo-auth từ v1.1 |
| `tests/` | Unit/integration test cho core và CLI |

## Kiểm chứng

```bash
python skills/ai-sdlc-core/scripts/sdlc.py validate --bundled --task examples/task-auth.json
python -m unittest discover -s tests -v
python skills/ai-sdlc-core/scripts/sdlc.py doctor --offline
```

## Migration từ v1.1

v1.1 đặt toàn bộ cấu hình ở gốc repo; v2.0 chuyển chúng vào skill và thay script rời bằng `sdlc.py`.

| v1.1 | v2.0 |
|---|---|
| `agents/`, `workflows/`, `policies/`, `templates/`, `schemas/` ở gốc | `skills/ai-sdlc-core/<cùng tên>/` |
| `AGENTS.md` (contract SDLC) | `skills/ai-sdlc-core/references/OPERATING-CONTRACT.md`; dự án chỉ có khối quản lý |
| `docs/HANDOFF.md`, `ROLE-ASSIGNMENT.md`, `ORCA-SETUP.md`, `ORCHESTRATOR-QUICKSTART.md` | `skills/ai-sdlc-core/references/` (`ORCHESTRATOR-ACTIVATION.md`) |
| `docs/BOOTSTRAP-PROMPT.md`, `ORCHESTRATOR-SMOKE-PROMPT.md` | Template trong `assets/prompts/`, render bằng `sdlc.py activate [--smoke]` |
| Skill `requirements-analysis`, `system-design`, `implementation`, `code-review`, `testing` | `sdlc-requirements-analysis`, … (`registry.json` đã cập nhật) |
| `scripts/validate_repo.py [--task]` | `sdlc.py validate [--task]` |
| `scripts/new_task.py` | `sdlc.py task new` |
| `scripts/orca_preflight.py` | `sdlc.py doctor` |
| `scripts/build_worker_spec.py --role business-analyst` | `sdlc.py smoke spec` (smoke) / `sdlc.py spec --task` (mọi role) |
| `scripts/check_smoke_output.py` | `sdlc.py smoke check` |
| `outputs/smoke-test/` | `.ai-sdlc/runs/smoke-test/` |
| `docs/proposals/auth-sdlc.md`, `reports/preflight/auth-sdlc.json` | `examples/demo-auth/` (hồ sơ tham khảo) |

Dự án đang dùng bản sao v1.1: cài skill v2.0, chạy `sdlc.py init`, chuyển quy tắc riêng của dự án vào
`.ai-sdlc/project.json` (hoặc `extra_policies`), rồi xoá các bản sao `agents/`, `workflows/`, `policies/`… khỏi repo dự án.

### v2.0 → v2.1

v2.1 thêm 5 workflow skill (`/sdlc-setup`, `/sdlc-status`, `/sdlc-task`, `/sdlc-smoke`, `/sdlc-orchestrate`) và flag
`init --approver`; config 2.0 vẫn tương thích. Cài lại skill, rồi chạy `/sdlc-status` trong từng dự án: agent sẽ đề xuất
`upgrade` để chuyển pin lên 2.1.0 và làm mới khối quản lý trong `AGENTS.md`/`CLAUDE.md`.

## Giới hạn quan trọng

- Git worktree tách nhánh mã nguồn, **không cô lập quyền hệ điều hành/mạng/secrets**.
- Không tự merge/deploy production, xóa dữ liệu, sửa secrets hoặc migration phá hủy.
- LLM review không thay thế CI, test runner, codeowner, branch protection và human approval.
- Quyền thực tế do sandbox/CI/credentials triển khai, **không** do prompt hay `project.json` quyết định.
- `validate`/`smoke check` là kiểm tra tĩnh; Orca không tự đọc `registry.json`/`manifest.json`.
- Đường dẫn core trong prompt/spec là đường dẫn tuyệt đối trên máy sinh ra chúng; sinh lại nếu chuyển máy.
