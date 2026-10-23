# Orca Orchestrator – hướng dẫn chạy thử (Phase 2.1)

## Mục tiêu
Orchestrator tạo Run trong Orca, giao **một** task cho Business Analyst và xác minh tài liệu tạo ra. Đây là smoke test **có giám sát**, không phải triển khai production hoặc tự động hóa toàn bộ SDLC.

## Điều kiện cần
- Giải nén repository rồi mở thư mục bằng Orca (`Add Repo`). Nếu thư mục chưa là Git repo, chạy `git init`, `git add .`, `git commit -m "Initialize Orca SDLC configs"` từ terminal trước khi mở trong Orca. Nếu đã là Git repo, chỉ commit các file cấu hình mới. Đặt tên/địa chỉ Git user khi được Git yêu cầu. Nếu đang mở repository phần mềm khác, hãy chuyển sang repository này cho bài kiểm thử tài liệu.
- Orca đang chạy, Settings → Experimental bật **Orchestration**; Settings → General → **Orca CLI** đã đăng ký.
- Đăng nhập và bật `codex` hoặc `claude` dưới Settings → Agents. Chọn **Manual** khi thử lần đầu.
- Python 3.10+, Git và Orca CLI có thể chạy trong Terminal của Orca.

## 1. Kiểm tra local (không sửa trạng thái Orca)
Mở Terminal trong thư mục repository:

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python scripts/orca_preflight.py
```

Lệnh `orca_preflight.py` chỉ kiểm tra Git, CLI và khả năng kết nối runtime; không tạo Run hoặc Agent. Nếu CLI vắng mặt, xem `docs/ORCA-SETUP.md`.

## 2. Cài và đọc guide có phiên bản tương ứng

```bash
orca status --json
orca skills install --skill orca-cli --skill orchestration
orca skills get orchestration --full
```

Trên Linux, tên chương trình có thể là `orca-ide`. Nếu lệnh không có, dùng chính hướng dẫn của Orca đang cài, không đoán cờ.

## 3. Tạo task spec thử nghiệm (offline)

```bash
python scripts/build_worker_spec.py --role business-analyst --output outputs/smoke-test/ba-task-spec.md
```

File được sinh ra là **tài liệu giao việc**, không phải task đã đăng ký với Orca. Hãy đọc nó trước khi dispatch. Script không gọi model, không đăng nhập và không điều khiển Orca.

## 4. Mở Orchestrator và đưa prompt

1. Mở terminal/Chat UI Codex hoặc Claude Code trong **workspace repository** hiện tại.
2. Dán **toàn bộ nội dung** `docs/ORCHESTRATOR-SMOKE-PROMPT.md`.
3. Orchestrator chỉ được *đọc, kiểm tra và đề xuất* kế hoạch ở lượt đầu. Không cho dispatch trước khi người dùng chấp thuận rõ ràng.
4. Khi kế hoạch và `outputs/smoke-test/ba-task-spec.md` đúng, hãy gửi `START-ORCA-SMOKE-TEST` trong chính phiên Orchestrator để cho phép bắt đầu.

## 5. Luồng điều phối thực tế

Khi đã được phê duyệt, Orchestrator tự chạy theo guide phiên bản đã nạp. Đây là **ví dụ cú pháp**, không phải một script để dán chạy nguyên khối:

```bash
orca orchestration run-create --objective "SMOKE: BA writes demo authentication requirements" --json
orca orchestration task-create --task-title "Draft demo authentication requirements" --spec "<paste the complete self-contained worker spec>" --json
orca orchestration worker-start --task <actualTaskId> --worktree current --agent codex --json
orca orchestration check --wait --types "worker_done,escalation,question" --timeout-ms 900000 --json
```

- Thay `<actualTaskId>` bằng ID được Orca trả về. Không chạy literal dấu `<>`.
- Orchestrator dùng **nội dung đầy đủ** của task spec, không dùng nguyên chuỗi placeholder trong ví dụ.
- Nếu chọn Claude, thay `--agent codex` bằng `--agent claude`.
- Bài thử chỉ sửa `outputs/smoke-test/auth-requirements.md` và `outputs/smoke-test/ba-handoff.md`; dùng `--worktree current` để dễ kiểm tra. Khi triển khai code thực, dùng worktree tách biệt và CI.
- Chỉ coi `worker_done` là tín hiệu ứng viên hoàn thành, không tự động đồng nghĩa đã đạt chất lượng.
- Với inbox delivery có ID, xử lý từng tin, xác minh kết quả, sau đó dùng `check --ack <delivery_id>` theo guide; worker đã settle được **reuse / retain / release** chính xác một lần.
- Nếu mất kết nối, worker không phản hồi hoặc CLI trả trạng thái không chắc chắn, kiểm tra `worker-list` / `worker-show` theo guide. **Không tự dispatch lại** vì có thể tạo bản chạy trùng.

## 6. Kiểm tra kết quả

```bash
python scripts/check_smoke_output.py
```

Smoke test chỉ đạt khi đồng thời có:
1. Orca có Run ID, Task ID, Dispatch ID thực (kiểm tra trực tiếp từ runtime).
2. Worker đã gửi `worker_done` có `--outcome succeeded` hợp lệ; không tồn tại hỏi đáp/escalation chưa xử lý.
3. File `outputs/smoke-test/auth-requirements.md` được tạo, có nội dung đặc tả, tiêu chí nghiệm thu, giả định và câu hỏi còn mở.
4. File `outputs/smoke-test/ba-handoff.md` có báo cáo và evidence cụ thể.
5. Coordinator đối chiếu output với `examples/project-brief.md`, không khẳng định đã viết code hoặc chạy test mà chưa thực hiện.
6. Worker đã settle được reuse, retain hoặc release theo hướng dẫn Orca.

Script chỉ kiểm tra tĩnh của artifact; **không thể** chứng thực Run/Dispatch/terminal hay chất lượng nghiệp vụ. Coordinator phải kiểm tra phần đó.

## 7. Các lỗi thường gặp
- `orca: command not found`: Settings → General → Orca CLI và PATH; Linux thử `orca-ide`.
- `orca status` lỗi: mở app/runtime Orca, kiểm tra repo trong đúng host.
- `worker-start` thất bại: giữ receipt và kiểm tra `failedStage`/`residualResources`; không vội chạy lại.
- `check` timeout: đây là checkpoint, không phải bằng chứng worker chết.
- Output không xuất hiện: kiểm tra đúng worktree/path, đúng active Dispatch và báo cáo worker.
- Repo chưa có Git: khởi tạo/cam kết thay đổi vào Git trước khi dùng `new-child` trong các bước về sau.

Tài liệu: https://www.onorca.dev/docs/cli/orchestration và `orca skills get orchestration --full`.
