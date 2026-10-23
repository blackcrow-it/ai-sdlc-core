# Kích hoạt Orchestrator trong Orca (AI SDLC Core v2)

## Mục tiêu
Từ một repository đã `sdlc.py init`, sinh prompt kích hoạt Orchestrator có đầy đủ cấu hình dự án + đường dẫn core,
dán vào phiên Claude Code/Codex trong Orca, để Orchestrator lập DAG, **chờ phê duyệt**, rồi điều phối supervised workers.
Bootstrap CLI chỉ sinh tài liệu; **mọi** thay đổi trạng thái Orca do Orchestrator thực hiện sau khi được duyệt.

## Điều kiện cần
- Orca đang chạy; Settings → Experimental bật **Orchestration**; Settings → General → **Orca CLI** đã đăng ký.
- Đã bật `codex` hoặc `claude` dưới Settings → Agents; chọn **Manual** khi chạy lần đầu.
- Skill `ai-sdlc-core` + `sdlc-*` và Orca native `orca-cli`/`orchestration` đã cài (xem `references/ORCA-SETUP.md`).
- `.ai-sdlc/project.json` hợp lệ và **đã commit** (worktree được tạo từ commit).

## 1. Kiểm tra local (không sửa trạng thái Orca)
```bash
python <core>/scripts/sdlc.py validate
python <core>/scripts/sdlc.py doctor
```
`doctor` chỉ đọc: Python, Git baseline, config, skill đã cài, `orca status --json`, `orca skills installed`.

## 2. Sinh prompt
```bash
python <core>/scripts/sdlc.py activate --brief docs/brief.md      # SDLC đầy đủ
python <core>/scripts/sdlc.py activate --smoke                    # smoke test một worker BA
```
- Kết quả: `.ai-sdlc/runs/orchestrator-activation.md` hoặc `.ai-sdlc/runs/smoke-test/orchestrator-prompt.md`
  (+ `ba-task-spec.md`). Thư mục `.ai-sdlc/runs/` bị gitignore.
- Nếu `doctor` có FAIL, `activate` vẫn sinh prompt nhưng in `BLOCKER`; prompt yêu cầu Orchestrator dừng và báo cáo.

## 3. Mở Orchestrator
1. Mở phiên Claude Code/Codex trong **workspace của repository dự án** trong Orca.
2. Dán toàn bộ phần dưới dòng `---` của file prompt.
3. Lượt đầu Orchestrator chỉ *đọc, kiểm tra và đề xuất*. Chỉ khi bạn gửi `APPROVE-SDLC-PLAN`
   (hoặc `START-ORCA-SMOKE-TEST` với smoke test) mới được tạo Run/Task/worker.

## 4. Luồng điều phối thực tế
Sau phê duyệt, Orchestrator chạy theo guide đúng phiên bản đã nạp. Đây là **ví dụ cú pháp** đã quan sát với Orca 1.4.x,
không phải script để dán nguyên khối:

```bash
orca orchestration run-create --objective "<objective>" --json
orca orchestration task-create --task-title "<title>" --spec "<complete rendered spec>" --json
orca orchestration worker-start --task <actualTaskId> --worktree <placement> --agent claude --json
orca orchestration check --wait --types "worker_done,escalation,question" --timeout-ms 900000 --json
```
- Spec của từng task do `sdlc.py spec --task .ai-sdlc/tasks/<TASK>.json` sinh ra; dùng **nội dung đầy đủ**, không dùng đường dẫn.
- Code workers dùng worktree riêng (guide Orca 1.4.230: `--worktree new-child --name <name> --setup run`);
  smoke test tài liệu dùng `--worktree current`. Task phụ thuộc tạo bằng `task-create --spec ... --deps <json_array>`.
- `worker_done` chỉ là tín hiệu ứng viên hoàn thành; Orchestrator phải tự kiểm tra artifact, diff và kết quả lệnh thật.
- Delivery có ID: xử lý từng tin, xác minh, rồi ack theo guide; worker đã settle được reuse / retain / release đúng một lần.
- Mất kết nối hoặc trạng thái không chắc chắn: kiểm tra `worker-list` / `worker-show` theo guide. **Không tự dispatch lại.**

## 5. Kiểm tra kết quả smoke test
```bash
python <core>/scripts/sdlc.py smoke check
```
Smoke test chỉ đạt khi đồng thời: có Run/Task/Dispatch ID thực; worker gửi `worker_done --outcome succeeded` hợp lệ,
không còn câu hỏi/escalation; hai file output có nội dung đặc tả, tiêu chí nghiệm thu, giả định, câu hỏi mở và handoff
có evidence; coordinator đối chiếu với brief; worker đã được settle. Script chỉ kiểm tra tĩnh.

## 6. Lỗi thường gặp
- `orca: command not found`: Settings → General → Orca CLI và PATH; Linux thử `orca-ide`.
- `orca status` lỗi: mở app/runtime Orca, kiểm tra repo trong đúng host.
- `doctor` báo config chưa commit: commit `.ai-sdlc/project.json` trước khi tạo worktree.
- `worker-start` thất bại: giữ receipt, kiểm tra `failedStage`/`residualResources`; không vội chạy lại.
- `check` timeout: là checkpoint, không phải bằng chứng worker chết.
- Output không xuất hiện: kiểm tra đúng worktree/path, đúng active Dispatch và báo cáo worker.

Tài liệu: https://www.onorca.dev/docs/cli/orchestration và `orca skills get orchestration --full`.
