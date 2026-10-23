# AI SDLC Core v2.0 – Reusable Agent Skills Package cho Orca ADE

Một bản **chuẩn, có phiên bản** của toàn bộ tổ chức AI Agent (14 vai trò, 9 workflow SDLC, policy, template,
schema) được đóng gói thành **Agent Skills**, kèm **Bootstrap CLI** `sdlc.py`. Với mỗi repository mới chỉ cần:
**cài Skill → khởi tạo cấu hình dự án → kích hoạt Orchestrator**.

Repo này **không** phải plugin Orca tự chạy, không cung cấp AI model và Bootstrap CLI **không bao giờ** tạo Run/Task/worker
trong Orca. Mọi thay đổi trạng thái Orca do Orchestrator thực hiện sau khi con người phê duyệt.

## Mô hình ba lớp

| Lớp | Trách nhiệm | Nằm ở đâu |
|---|---|---|
| **AI SDLC Core** | Một phiên bản chuẩn của agents, workflows, policies, templates, schemas, prompt và Bootstrap CLI | Skill `ai-sdlc-core` + 5 role skill `sdlc-*` (thư mục `skills/` của repo này) |
| **Orca ADE** | Điều phối Agent: Runs, tasks, supervised workers, Git worktree | Orca runtime + native skill `orca-cli`, `orchestration` |
| **Repository dự án** | Chỉ cấu hình đặc thù: ngôn ngữ, kiến trúc, lệnh test/lint/build, quy tắc coding, phạm vi chức năng, đường dẫn được ghi/bị bảo vệ, người phê duyệt | `.ai-sdlc/project.json` (+ task contract trong `.ai-sdlc/tasks/`, khối quản lý trong `AGENTS.md`/`CLAUDE.md`) |

Thứ tự ưu tiên: chỉ thị con người > bằng chứng repo/CI > **policy của core** > `project.json` (chỉ được *siết chặt*,
không bao giờ cấp quyền) > task spec > workflow/role/skill.

## Bắt đầu nhanh

### 1. Cài Skill (một lần mỗi máy)

```bash
# Orca native skills
orca skills install --skill orca-cli --skill orchestration

# AI SDLC Core – cách A: community skills CLI (đã kiểm với skills@1.7.4; nguồn là Git URL hoặc đường dẫn clone)
npx skills add <git-url-hoac-duong-dan-repo-nay> --list        # phải thấy đủ 6 skill
npx skills add <git-url-hoac-duong-dan-repo-nay> --skill ai-sdlc-core --skill sdlc-requirements-analysis \
  --skill sdlc-system-design --skill sdlc-implementation --skill sdlc-code-review --skill sdlc-testing \
  --global --agent claude-code --agent codex --copy -y

# AI SDLC Core – cách B: offline từ bản clone (copy vào ~/.claude/skills và ~/.agents/skills)
python skills/ai-sdlc-core/scripts/sdlc.py install --dry-run
python skills/ai-sdlc-core/scripts/sdlc.py install
```

`install` hỗ trợ `--agent claude|universal` (`.claude/skills` hoặc `.agents/skills` cho Codex và agent khác),
`--scope project` (cài vào repo hiện tại), `--dest <dir>`, `--force` (chỉ thay thế thư mục skill hợp lệ).
Role skill có tiền tố `sdlc-` để không đụng skill khác cùng tên (ví dụ `code-review`) đã cài sẵn.

### 2. Khởi tạo cấu hình dự án (mỗi repository)

```bash
cd /path/to/new-repo
SDLC="python ~/.claude/skills/ai-sdlc-core/scripts/sdlc.py"   # hoặc ~/.agents/skills/...

$SDLC init \
  --architecture-style "modular monolith" --architecture-summary "Express REST API + PostgreSQL" \
  --test-cmd "pnpm run test" --rule "TypeScript strict; no any" \
  --in-scope "Order management API" --out-of-scope "Payments" --allowed-path "src/**" --allowed-path "tests/**"
$SDLC validate
git add .ai-sdlc/project.json AGENTS.md CLAUDE.md .gitignore && git commit -m "Adopt AI SDLC Core"
```

`init` suy luận ngôn ngữ/lệnh **chỉ từ bằng chứng** (`package.json` scripts, lockfile, `go.mod`, `Cargo.toml`,
`pom.xml`, Gradle, `*.csproj`, pytest/ruff/mypy config, `Makefile`…) và in rõ nguồn `DETECTED ...`. Không có bằng chứng thì
để trống và `validate` báo lỗi (ví dụ thiếu `commands.test`) thay vì đoán. Nội dung `AGENTS.md`/`CLAUDE.md` sẵn có được giữ nguyên;
CLI chỉ chèn/cập nhật khối giữa `<!-- ai-sdlc-core:begin -->` và `<!-- ai-sdlc-core:end -->`.

### 3. Kích hoạt Orchestrator

```bash
$SDLC doctor                          # read-only: Python, Git baseline, config, skills, orca status, orca skills
$SDLC activate --brief docs/brief.md  # -> .ai-sdlc/runs/orchestrator-activation.md
$SDLC activate --smoke                # tuỳ chọn: smoke test 1 worker BA (-> .ai-sdlc/runs/smoke-test/)
```

Mở phiên Claude Code/Codex của repository trong Orca và dán prompt. Orchestrator chỉ đọc, kiểm tra và đề xuất DAG; chỉ khi
bạn gửi `APPROVE-SDLC-PLAN` (smoke test: `START-ORCA-SMOKE-TEST`) mới được tạo Run/Task/worker. Chi tiết:
[ORCHESTRATOR-ACTIVATION](skills/ai-sdlc-core/references/ORCHESTRATOR-ACTIVATION.md), [ORCA-SETUP](skills/ai-sdlc-core/references/ORCA-SETUP.md).

## Bootstrap CLI `sdlc.py`

Python 3.10+, chỉ thư viện chuẩn. Mọi lệnh nhận `-C <project-dir>` (mặc định thư mục hiện tại).

| Lệnh | Tác dụng |
|---|---|
| `version`, `where [--json]` | Phiên bản và đường dẫn core đã cài (các đường dẫn `agents/...`, `policies/...` trong tài liệu core tính từ đây) |
| `install` | Copy 6 skill vào thư mục skill của agent (offline) |
| `init` | Tạo `.ai-sdlc/project.json`, khối quản lý `AGENTS.md`/`CLAUDE.md`, ignore `.ai-sdlc/runs/` (`--dry-run`, `--force`, `--no-detect`, `--no-agent-files`) |
| `validate [--task F] [--core-only] [--bundled]` | Kiểm tra toàn vẹn core, config dự án (schema + quy tắc) và task contract |
| `doctor [--offline] [--json]` | Kiểm tra sẵn sàng, chỉ đọc; exit 1 khi có FAIL |
| `task new --id --title --role` | Tạo task contract nháp trong `.ai-sdlc/tasks/`, điền sẵn checks/forbidden actions từ config |
| `spec --task F` | Render worker spec tự chứa (role, policy, cấu hình dự án, phạm vi, checks) vào `.ai-sdlc/runs/specs/` |
| `activate [--brief F] [--smoke] [--agent claude\|codex]` | Render prompt kích hoạt Orchestrator |
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
| `skills/sdlc-*/SKILL.md` | 5 role skill: requirements-analysis, system-design, implementation, code-review, testing |
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

## Giới hạn quan trọng

- Git worktree tách nhánh mã nguồn, **không cô lập quyền hệ điều hành/mạng/secrets**.
- Không tự merge/deploy production, xóa dữ liệu, sửa secrets hoặc migration phá hủy.
- LLM review không thay thế CI, test runner, codeowner, branch protection và human approval.
- Quyền thực tế do sandbox/CI/credentials triển khai, **không** do prompt hay `project.json` quyết định.
- `validate`/`smoke check` là kiểm tra tĩnh; Orca không tự đọc `registry.json`/`manifest.json`.
- Đường dẫn core trong prompt/spec là đường dẫn tuyệt đối trên máy sinh ra chúng; sinh lại nếu chuyển máy.
