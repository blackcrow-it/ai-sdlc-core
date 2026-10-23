# Thiết lập Orca ADE cho AI SDLC Core

## Yêu cầu
- Orca ADE, Git và Codex hoặc Claude Code đã cài, đã đăng nhập.
- Repository dự án là Git repo có nhánh mặc định và **ít nhất một commit**, đã được Orca `Add Repo`.
- Python 3.10+ để chạy Bootstrap CLI `sdlc.py` (không cần Python để Orca điều phối).

## Thực hiện (một lần cho mỗi máy)
1. Orca → Settings → General → Orca CLI: đăng ký CLI. Kiểm tra `orca status --json` (Linux có thể là `orca-ide`).
2. Cài **Orca native skills** (khác với skill của AI SDLC Core):
   ```bash
   orca skills install --skill orca-cli --skill orchestration
   orca skills get orchestration --full
   ```
   Lệnh này chạy `npx skills add ...` đã pin theo bản Orca; xem `orca skills install --help` và dùng `--dry-run` để kiểm tra trước.
3. Cài **AI SDLC Core** (6 skill: `ai-sdlc-core` + 5 role skill `sdlc-*`):
   - Qua community skills CLI (đã kiểm với `skills@1.7.4`; nguồn là Git URL hoặc đường dẫn clone): chạy `npx skills add <nguon> --list` để thấy đủ 6 skill, rồi `npx skills add <nguon> --skill ai-sdlc-core --skill sdlc-requirements-analysis --skill sdlc-system-design --skill sdlc-implementation --skill sdlc-code-review --skill sdlc-testing --global --agent claude-code --agent codex --copy -y`. Không có `--copy` thì CLI tạo symlink; phiên bản khác có thể đổi flag, xem `npx skills add --help`.
   - Hoặc offline từ bản clone: `python skills/ai-sdlc-core/scripts/sdlc.py install` (mặc định copy vào `~/.claude/skills` và `~/.agents/skills`; `--scope project` để cài vào repo hiện tại; `--dry-run` để xem trước).
4. Settings → Agents → Agent Permissions: chọn **Manual** hoặc sandbox giới hạn.

## Thực hiện (cho mỗi repository dự án)
1. `python <skills-dir>/ai-sdlc-core/scripts/sdlc.py init` → tạo `.ai-sdlc/project.json`, khối quản lý trong `AGENTS.md`/`CLAUDE.md`.
2. Hoàn thiện config, `sdlc.py validate`, commit config.
3. Settings → Repository → Hooks: cấu hình install dependencies theo `commands.install` của dự án; KHÔNG tự đọc/copy `.env` chứa secret vào worktree.
4. Kiểm tra branch protection/CI ở Git provider; prompt không thay thế controls.
5. `sdlc.py doctor` → `sdlc.py activate` (hoặc `activate --smoke` để thử một worker BA).

## Kiểm chứng độc lập với Orca
- `sdlc.py validate` phải ra OK cho core và config dự án.
- `sdlc.py doctor --offline` không có FAIL.
- Task đầu tiên chỉ lập tài liệu; task sửa code chỉ hoạt động trong worktree được cấp.

## Tài liệu tham khảo
- https://www.onorca.dev/docs/agents/hooks-memory
- https://www.onorca.dev/docs/cli/skills
- https://www.onorca.dev/docs/cli/overview
- https://www.onorca.dev/docs/cli/reference
- https://agentskills.io/specification

## Ghi chú thực tế
Orca phiên bản khác nhau có thể thay đổi tên subcommand và flag. Trước **mỗi thay đổi** orchestration, đọc hướng dẫn đúng phiên bản bằng `orca skills get orchestration --full` và xem `--help`. Không đưa lệnh từ tài liệu mẫu vào production một cách mù quáng.
