# Giao thức bàn giao Agent → Agent

## Quy tắc
- Tất cả handoff phải có `task_id`, `role`, `status`, `artifact_paths`, `evidence`, `risks`, `next_owner`.
- Chỉ trạng thái `submitted_for_review` khi đã tạo file thực; chỉ `accepted` khi gate/đại diện quyền hợp lệ duyệt.
- Handoff không tự làm thay đổi trạng thái native của Orca; Orchestrator dùng công cụ đã xác minh để cập nhật.
- Nếu reviewer từ chối: tạo issue rõ nguyên nhân, sửa trên task gốc/child task, giữ lịch sử.

## Mẫu báo cáo

```yaml
task_id: TASK-001
role: backend-developer
status: submitted_for_review
artifact_paths:
  - src/auth/service.ts
  - tests/auth.test.ts
evidence:
  - command: npm test -- auth.test.ts
    exit_code: 0
    log_path: reports/TASK-001-tests.log
risks:
  - Session invalidation not covered by this task.
next_owner: code-reviewer
approval_required: false
```

Tuyệt đối không ghi giả `exit_code: 0` hoặc artifact path. Nếu chạy test không được, ghi `not_run` và lý do.
