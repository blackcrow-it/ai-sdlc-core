# Orca ADE – AI Software Development Organization (v1.1 – Orchestrator Bootstrap)

Bộ cấu hình **14 vai trò AI Agent**, **9 workflow SDLC**, **5 Agent Skills**, biểu mẫu,
chính sách và script kiểm tra cấu hình. Repo này là **bộ quy tắc + nội dung hướng dẫn**;
**không phải** plugin Orca tự chạy, không tự khởi tạo worker và không cung cấp AI model.

## Bắt đầu nhanh

1. Giải nén/clone repo này; mở thư mục bằng Orca ADE (`Add Repo`).
2. Chạy `python scripts/validate_repo.py` (Python 3.10+; không cần dependency ngoài).
3. Đăng ký Orca CLI trong Settings → General → Orca CLI; xác minh `orca status --json`.
4. Cài **skill của chính Orca** vào coding agent:
   ```bash
   orca skills install --skill orca-cli --skill orchestration
   orca skills get orchestration --full
   ```
   Trên Linux, tên CLI có thể là `orca-ide`. Nếu không tìm được CLI, xem [ORCA-SETUP](docs/ORCA-SETUP.md).
5. Cấu hình agent ở chế độ **Manual** trước (Settings → Agents → Agent Permissions); bật quyền tối thiểu.
6. Mở phiên Codex hoặc Claude Code trong Orca; gửi prompt trong [BOOTSTRAP](docs/BOOTSTRAP-PROMPT.md).
7. Dùng `examples/project-brief.md` làm đề bài thử và tạo PR trên **staging**, không triển khai production.

## Bản đồ repository

| Đường dẫn | Ý nghĩa |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | Hướng dẫn gốc được coding agents nhận diện |
| `agents/*.md` | Nội dung vai trò để Orchestrator nạp vào task spec |
| `agents/registry.json` | Danh mục vai trò, năng lực, định tuyến task (đề xuất) |
| `skills/*/SKILL.md` | Kỹ năng chuẩn Agent Skills, cài/nạp riêng cho agent |
| `workflows/*.md` | Playbook theo giai đoạn SDLC, do Orchestrator đọc |
| `workflows/manifest.json` | Thứ tự, điều kiện và đầu ra workflow (quy ước nội bộ) |
| `templates/*.md` | Mẫu tài liệu bàn giao giữa Agent |
| `policies/*.md` | Chính sách bảo mật, quyền hạn, quality gate, approval |
| `schemas/*.json` | JSON Schema của task/artifact |
| `scripts/`, `tests/` | Kiểm tra và tạo task mẫu bằng Python stdlib |

## Cách nạp và chạy

- **Orca** quản lý worktrees, phiên coding-agent, Runs, tasks và supervised workers.
- **Codex/Claude** đọc `AGENTS.md` / `CLAUDE.md` theo quy ước của chính agent.
- `agents/*.md`, `workflows/*.md`, `policies/*.md` là **hướng dẫn nội bộ**: Orchestrator
  phải **đọc file và đưa chỉ dẫn vào task spec**, không tự nhiên biến thành plugin.
- `skills/` chứa **Agent Skills chuẩn**; nạp/cài riêng để CLI agent phát hiện skill.
- `registry.json` / `manifest.json` **không phải cấu hình native Orca**; không có lời
  hứa Orca tự parse hoặc tạo task từ các file này.
- Trước khi dùng `orca orchestration` để **thay đổi** trạng thái, luôn đọc
  `orca skills get orchestration --full`, xác nhận câu lệnh/flags với phiên bản cài đặt.

## Kiểm chứng

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python scripts/new_task.py --id TASK-001 --title 'Add login' \
  --role backend-developer --project PROJECT-001 --output /tmp/task-001.json

# Hãy thay hết REPLACE trong /tmp/task-001.json rồi mới chạy kiểm tra:
python scripts/validate_repo.py --task /tmp/task-001.json
```

## Giới hạn quan trọng

- Git worktree tách nhánh mã nguồn, **không cô lập quyền hệ điều hành/mạng/secrets**.
- Không tự merge/deploy production, xóa dữ liệu, sửa secrets hoặc migration phá hủy.
- LLM review không thay thế CI, test runner, codeowner, branch protection và human approval.
- Quyền thực tế do sandbox/CI/credentials triển khai, **không chỉ** do prompt quyết định.
- Không tự tin báo hoàn thành khi thiếu bằng chứng hoặc công cụ thực thi bị lỗi.

## Phase 2.1 – Kích hoạt Orchestrator

Chạy thử **một** BA worker với giám sát Orca (có bước xác nhận trước dispatch):

```bash
python scripts/validate_repo.py
python scripts/orca_preflight.py
python scripts/build_worker_spec.py --role business-analyst
```

Đọc [Orchestrator Quickstart](docs/ORCHESTRATOR-QUICKSTART.md) và dán [Smoke Prompt](docs/ORCHESTRATOR-SMOKE-PROMPT.md) vào phiên Orchestrator trong Orca. Sau worker chạy xong kiểm tra `python scripts/check_smoke_output.py`. **Mẫu này chưa tự gọi Orca từ môi trường khác và chưa chạy Agent trên máy bạn.**

Tài liệu tiếp theo: [thiết lập Orca](docs/ORCA-SETUP.md), [prompt khởi chạy](docs/BOOTSTRAP-PROMPT.md), [giao thức bàn giao](docs/HANDOFF.md).
