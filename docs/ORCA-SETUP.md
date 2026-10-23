# Thiết lập trong Orca ADE

## Yêu cầu
- Orca ADE, Git và Codex hoặc Claude Code đã cài, đã đăng nhập.
- Repository Git đã có nhánh mặc định và được Orca Add Repo.
- Python 3.10+ để chạy validator nội bộ (không cần Python để Orca điều phối).

## Thực hiện
1. Trong Orca → Settings → General → Orca CLI, đăng ký CLI (nếu chưa có).
2. Terminal trong repo: `orca status --json` (trên một số bản Linux là `orca-ide`).
3. Cài **Orca native skills** vào coding agent (khác với skill nghiệp vụ trong repo):
   ```bash
   orca skills install --skill orca-cli --skill orchestration
   orca skills get orca-cli
   orca skills get orchestration --full
   ```
   Nếu lệnh cài không tương thích phiên bản: tra giao diện Orca Skills hoặc tài liệu docs/cli/skills.
4. Settings → Agents → Agent Permissions: chọn **Manual** hoặc sandbox giới hạn.
5. Settings → Repository → Hooks: cấu hình install dependencies theo dự án, KHÔNG tự đọc/copy `.env` chứa secret vào worktree.
6. Kiểm tra branch protection/CI ở Git provider; không dùng prompt thay thế controls.
7. Cài repo-specific Agent Skills (nếu cần) bằng trình quản lý Skills của Orca hoặc `npx skills add <git-url-cua-repo> --skill <name>` sau khi đẩy repo lên Git. Kiểm tra lại skill được CLI phát hiện; file `skills/` không đảm bảo tự kích hoạt trong mọi provider.
8. Mở phiên Agent, đọc `docs/BOOTSTRAP-PROMPT.md`, tạo một supervised Run và thử nghiệm với `examples/project-brief.md`.

## Kiểm chứng độc lập với Orca
- `python scripts/validate_repo.py` phải ra OK.
- `python -m unittest discover -s tests -v` phải chạy qua.
- Task đầu tiên chỉ lập tài liệu; task sửa code chỉ hoạt động trong worktree được cấp.

## Tài liệu tham khảo
- https://www.onorca.dev/docs/agents/hooks-memory
- https://www.onorca.dev/docs/cli/skills
- https://www.onorca.dev/docs/cli/overview
- https://www.onorca.dev/docs/cli/reference
- https://agentskills.io/specification

## Ghi chú thực tế
Orca phiên bản khác nhau có thể thay đổi tên subcommand và flag. Trước **mỗi thay đổi** orchestration, đọc hướng dẫn đúng phiên bản bằng `orca skills get orchestration --full` và xem `--help`. Không đưa lệnh từ tài liệu mẫu vào production một cách mù quáng.
