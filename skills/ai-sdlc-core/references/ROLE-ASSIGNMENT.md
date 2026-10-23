# Hướng dẫn gán role vào worker Orca

1. Task nên có `owner_agent` khớp `agents/registry.json`.
2. Orchestrator đọc `agents/<role>.md`, policy, artifact được duyệt và task contract.
3. Task contract nằm ở `.ai-sdlc/tasks/` của repository dự án; render spec tự chứa bằng `sdlc.py spec --task <file>` (gồm role, policy, cấu hình dự án, `allowed_paths`, kiểm tra, review và output).
4. Worker không được cấp quyền dựa trên lời nhắc; cấu hình quyền trong Orca/CLI/sandbox/CI.
5. Điều phối phải xác thực các sự kiện worker đúng theo CLI hiện tại (`orca skills get orchestration --full`).
6. Khi worker trả kết quả, thu thập commit/diff, artifacts và test logs; reviewer không được là tác giả cùng task.
7. Chỉ điều phối tiếp task phụ thuộc khi quality gate đạt; nếu không, tạo remediation task.

## Lưu ý
Một role ≠ một tiến trình cố định. Cùng một provider CLI có thể được điều phối ở nhiều role khác nhau qua những task spec khác nhau. Đừng giả định Orca đọc `registry.json` tự động.
