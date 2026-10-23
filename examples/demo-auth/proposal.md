# Đề xuất DAG SDLC — demo authentication

- Trạng thái: `draft / awaiting_human_approval`.
- Vai trò hiện tại: `orchestrator`; người quyết định tiếp theo: Human Product Owner.
- Run ID / Task ID / Dispatch ID native: chưa tạo. Các nhãn `D01`–`D16` và `G0`–`G8` dưới đây chỉ là nhãn đề xuất.
- Nguồn: `examples/project-brief.md`, `AGENTS.md`, `agents/orchestrator.md`, toàn bộ `policies/*`, `docs/HANDOFF.md`, registry, manifest, các workflow SDLC và templates tương ứng.
- Bằng chứng kiểm tra môi trường: `reports/preflight/auth-sdlc.json` (lệnh, output và exit code thực; có toàn văn guide Orca đã cài).

## Phát hiện đã xác minh

Orca `1.4.230` đang chạy, runtime `ready`, kết nối `connected`; executable được chọn cho phiên là `orca`. Đã chạy `orca status --json` trước khi nạp `orca skills get orchestration --full`. `orca orchestration run-current --json` trả `run: null`. Chưa thay đổi trạng thái orchestration, tạo worker hoặc worktree.

Repo hiện là bộ cấu hình SDLC, chưa có source ứng dụng demo. HEAD là `344ac1748e55301ae0d7863c55a59382b97f8093`, tree của HEAD rỗng; cấu hình, policies và workflows đều đang untracked. Worktree tạo từ HEAD lúc này sẽ thiếu các tài liệu đó. Không tự commit toàn bộ nội dung hiện có.

Python `3.12.6`; `python scripts/validate_repo.py --task examples/task-auth.json` exit `0`; `python -m unittest discover -s tests -v` exit `0`, 3 tests đạt. Validator chỉ kiểm tra cấu hình/core task fields, không phải JSON Schema validator đầy đủ, kiểm tra chu trình tổng thể, hay bằng chứng tính năng auth. `.github/workflows/config-check.yml` có định nghĩa CI nhưng chưa xác minh lần chạy CI remote nào. Build/lint/typecheck/auth integration/E2E/staging smoke: `not_run`, thiếu ứng dụng và môi trường.

## Phạm vi xin duyệt

**A — khuyến nghị cho Run đầu:** discovery, PRD, SRS, user stories/acceptance criteria, UI specification dạng tài liệu và trạng thái màn hình; ghi rõ các quyết định còn mở. Dừng ở hồ sơ được human review hoặc blocker chưa giải quyết. Chưa chọn framework, tạo ứng dụng mới hay thực hiện deployment. Nếu chưa chốt nghiệp vụ, task tiếp theo bị chặn ở gate tương ứng.

**B — mở rộng có điều kiện:** thêm khảo sát repo ứng dụng đích, kiến trúc/API contract, kế hoạch task backend/frontend, triển khai, review, kiểm thử và chuẩn bị staging. Cần cung cấp đường dẫn repo được phép đọc, revision cơ sở và phạm vi sửa cụ thể. Việc duyệt B không thay thế các approval sau ở thiết kế, security và staging.

MVP đề xuất: Visitor xem public page; Member đăng nhập/đăng xuất, xem member page và nhận xử lý đúng khi phiên hết hạn hoặc truy cập trái quyền. Admin chỉ ở mức mô hình quyền/thiết kế như brief. Chưa đưa đăng ký, khôi phục mật khẩu, MFA hay quản trị Admin vào triển khai; cần Product Owner chấp thuận ranh giới này.

Giả định cần human quyết định: ưu tiên khảo sát password + server-side session cho demo, dữ liệu tài khoản tổng hợp; OAuth/passkey là phương án cần so sánh nếu có yêu cầu. Đây chỉ là giả định lập kế hoạch, chưa phải ADR hay chính sách auth được chấp thuận. Chưa đặt session lifetime, account lockout/rate limit hoặc cam kết backward compatibility: Product Owner/Security owner cần chốt trước khi SRS qua gate. Architect phải khảo sát source trước khi đề xuất framework, storage, cookie/CSRF và API version. Không có processor ngoài nào được chấp thuận qua bản đề xuất này.

## DAG và deliverables đề xuất

Đường dẫn trong bảng là **đầu ra dự kiến, chưa tồn tại**. `docs/projects/demo-auth/` viết tắt là `DOC/`; `reports/demo-auth/` là `REP/`. Đường dẫn source trong repo đích chỉ được điền sau khảo sát và trước dispatch. Mỗi worker chỉ được sửa đầu ra được giao cùng report của chính nó; inputs/policies/templates là read-only.

| Nhãn | Owner | Phụ thuộc và gate trước khi bắt đầu | Phạm vi / đầu ra dự kiến | Điều kiện nghiệm thu quan sát được |
|---|---|---|---|---|
| D01 | product-manager | G0 | `DOC/PRD.md`, `DOC/decisions.md` | PRD theo template; mục tiêu, actor, MVP/non-goals, success criteria và câu hỏi có owner; human duyệt scope ở G1 |
| D02 | business-analyst | D01, G1 | `DOC/SRS.md`, `DOC/traceability.md` | Requirement IDs, Given/When/Then, lỗi đăng nhập, logout, hết phiên, unauthorized; các policy mở được quyết định hoặc ghi blocker; G2 |
| D03 | ui-ux-designer | D02, G2 | `DOC/UI-SPEC.md` | Public/login/member flows, loading/error/expired/forbidden, responsive và accessibility checklist; artifact tài liệu thật, không bịa prototype; G3 |
| D04 | software-architect | D03, G3, quyền đọc + source/revision ứng dụng đích | `DOC/repo-assessment.md`, `DOC/architecture.md`, `DOC/api-contract.yaml` | Có đường dẫn/revision khảo sát, API schemas/errors/auth boundary, tương thích, data ownership, migration/rollback và tradeoffs; chưa tự duyệt ADR |
| D05 | security-engineer | D04 | `REP/design-security.md` | Đánh giá trust/data flow của D04, auth/authz/session, logging, scan scope; ghi verified findings riêng với giả thuyết; đầu vào G4 |
| D06 | project-manager | D04, D05, G4 | `DOC/tasks/*.md`, `DOC/tasks/*.json`, `DOC/native-id-map.json` | Contract theo template/schema; owner/reviewer khác nhau, path cụ thể, dependencies không chu trình, AC/checks/budget; G5 |
| D07 | backend-developer | D06, G5 | Chỉ backend/auth paths và regression tests trong repo đích đã ghi tại contract; `REP/backend.md` | Behavior đúng SRS/API, enforcement authz, test happy/failure/expired/logout, focused checks; diff và revision thật |
| D08 | frontend-developer | D06, G5 | Chỉ UI/auth paths và UI tests trong repo đích đã ghi tại contract; `REP/frontend.md` | UI đúng D03, lỗi/loading/expired/forbidden và accessibility; tests theo contract; mock nếu dùng phải công bố |
| D09 | backend-developer, Dispatch tích hợp riêng | D07, D08 | Candidate branch/worktree riêng, `REP/integration.md` | Ghép đúng revisions D07/D08 vào candidate có commit SHA; build/lint/typecheck/unit/integration và CI cần thiết cho chính SHA đó; không merge protected branch |
| D10 | code-reviewer, worker độc lập với D07–D09 | D09 | `REP/code-review.md` | Đọc diff thực + AC + CI; findings severity/file/line, approve/request changes; read-only source, không tự sửa rồi tự review |
| D11 | qa-engineer, độc lập với implementation | D09 | Test-only paths được giao, `REP/test-report.md` | Report theo template, trace từng AC, regression/E2E/negative auth, commands/exit/logs/env; dùng đúng candidate SHA |
| D12 | security-engineer | D09 | `REP/implementation-security.md` | Scoped secrets/dependency/authz checks thực; finding có repro/evidence; không scan ngoài quyền được cấp |
| D13 | devops-engineer | D10, D11, D12, G6 | `DOC/release-notes.md`, `DOC/staging-runbook.md` | Immutable artifact digest gắn candidate SHA/CI, rollback/monitoring, target và smoke plan cụ thể; chỉ chuẩn bị release |
| D14 | devops-engineer | D13, G7 | Chỉ staging được human chỉ định; `REP/staging-deploy.md` | Human approval còn hiệu lực, đúng artifact digest/target, deploy receipts; không truy cập/sửa secrets; thiếu quyền thì chặn |
| D15 | qa-engineer | D14 | `REP/staging-smoke.md` | Smoke public/login/member/logout/expiry/authz trên artifact đã deploy, UAT nếu cần, kết quả/logs thực; G8 |
| D16 | technical-writer | D15, G8, monitoring/feedback thực | `DOC/operations-handoff.md`, `DOC/follow-up-backlog.md` | Setup/known limitations, monitoring owner, release evidence; incident report chỉ khi có sự cố thực |

Dependency list trên là DAG; D07/D08 được làm song song sau contract được duyệt. D10/D11/D12 là wave độc lập cùng kiểm tra một candidate SHA, mỗi worker có output paths riêng. Mỗi giai đoạn serial trước đó phản ánh prerequisite thật trong manifest; không cắt bỏ gate chỉ để rút ngắn critical path. Nếu candidate thay đổi sau review/test thì kết quả liên quan mất hiệu lực và phải kiểm tra lại.

Trong phạm vi A, chỉ D01–D03 có thể được cho phép theo các gate; D04–D16 là kế hoạch có điều kiện. Trong phạm vi B, cũng không dispatch D04 trước khi repo/revision/quyền đọc được xác nhận; D07–D16 chưa có source paths/commands nên hiện chưa phải contract thực thi.

## Human gates và evidence

| Gate | Điều kiện | Người có quyền quyết định |
|---|---|---|
| G0 | Duyệt bản đề xuất: phạm vi A/B, giả định, budget; thống nhất baseline tài liệu cho workers | Human Product Owner; chủ repo cho phép baseline nếu cần |
| G1 | PRD đúng scope, users, success criteria; quyết định product còn mở có disposition | Human Product Owner |
| G2 | SRS có traceability và measurable AC; auth mechanism, lifetime, failure/rate-limit, compatibility không còn mơ hồ | Human Product Owner; Security owner cho chính sách auth/authorization |
| G3 | UI flows/states/accessibility được review | Human Product Owner/design approver |
| G4 | Architecture/API/data/ADR và D05 được review độc lập; material assumptions/processor được duyệt rõ | Tech Lead/Architect reviewer khác tác giả; Security owner khi áp dụng |
| G5 | Task contracts/schema, dependencies, paths, tests, independent reviewer và budgets được kiểm tra | Orchestrator kiểm chứng; human duyệt priority/budget thay đổi |
| G6 | Exact candidate SHA có required CI green, independent review và QA/security evidence; blocker/critical findings được giải quyết | Required codeowner và người có quyền tương ứng; không tự waiver |
| G7 | Human cho phép **deploy staging** theo target/digest/rollback cụ thể sau CI; controls/permissions thật sẵn có | Human release owner |
| G8 | Staging smoke đạt, UAT được chấp nhận nếu áp dụng, monitoring/rollback owner xác định | Human Product Owner/release owner |

G0 hoặc G7 không cho phép production. Production, sửa secrets và tự duyệt risk exception nằm ngoài nhiệm vụ này. Waiver chỉ hợp lệ nếu đúng human owner ghi rationale, scope, timestamp, expiry; Orchestrator không đóng vai người phê duyệt.

Approval record phải lưu version/hash tài liệu, quyết định, danh tính do human cung cấp, timestamp, scope/expiry và tham chiếu bằng chứng tại `DOC/approvals/`. Không giả danh human bằng message nội bộ. Native gate dùng cho DAG decision của coordinator; chỉ resolve dựa trên quyết định hợp lệ đã ghi. Nếu UI không đủ trường, giữ record trong repo. Native Task thành công không tự đồng nghĩa business/quality gate đã qua; coordinator chỉ dispatch dependent sau khi kiểm tra artifact và gate.

## Task contracts, ngân sách và isolation

Trước dispatch, từng task/review task có contract theo `templates/task.md`; task JSON theo `schemas/task.schema.json`; test reports theo `templates/test-report.md`; handoff theo `docs/HANDOFF.md`. Contract ghi actual native Run/Task IDs sau receipt và ánh xạ nhãn đề xuất sang ID trong `DOC/native-id-map.json`. Không ghi các nhãn Dxx thành ID do Orca cấp.

Ngân sách đề xuất: D01–D06, D10, D12, D13, D16 tối đa 20.000 tokens và 45 phút/task; D07–D09, D11 tối đa 40.000 tokens và 90 phút/task; D14/D15 tối đa 15.000 tokens và 30 phút/task. Tối đa 2 attempts/task (lần đầu + 1 retry sau thất bại đã xác minh), tối đa 2 code editors đồng thời, tối đa 3 workers trong review wave. Phạm vi A có trần 60.000 tokens/135 phút worker cộng dồn. Mở rộng B cần duyệt tổng ngân sách mới trước dispatch. Retry không được vượt trần tổng; thiếu budget thì escalation.

Đây là giới hạn contract/điểm escalation, không phải khẳng định Orca có token-limit CLI flag. Phải kiểm tra khả năng runtime theo dõi/enforce usage trước chạy; nếu không có telemetry/enforcement phù hợp, yêu cầu human quyết định trước thay vì bịa usage. Timeout/liveness không chứng minh worker thất bại.

Mọi code worker dùng worktree riêng từ baseline đã xác minh; integration dùng worktree thứ ba; reviewer có checkout đúng candidate SHA và quyền source read-only nếu runtime hỗ trợ. Git worktree không phải security sandbox. Quyền OS/network/credentials phải được kiểm tra riêng; prompt/role markdown không cấp quyền.

G0 cần chọn cách phân phối tài liệu hiện đang untracked: đề xuất review rồi commit permitlist cấu hình không nhạy cảm làm baseline, không `git add .`; hoặc giữ nguyên working tree và cấp snapshot inputs được kiểm chứng. Chưa commit, push, đăng ký repo khác hoặc thay đổi hooks/permissions. Setup hooks cần được đọc trước khi chạy để tránh tác dụng ngoài scope.

Với doc-only tasks, dùng paths riêng và phối hợp serial tại shared document; reviewer độc lập được human hoặc task review riêng thực hiện, có native ID nếu dùng worker. Code reviewer D10 bắt buộc là worker khác implementation owner; worker làm remediation không thể tự approve bản sửa của mình.

## Quy trình native sau khi có approval

1. Ghi quyết định G0, xác minh baseline, runtime và guide đúng phiên bản; nếu CLI/guide thiếu thì không mutation. Tra `--help` trước thay đổi theo hướng dẫn repo.
2. Tạo một tracked Run bằng `orca orchestration run-create`; lưu receipt thật. Tạo native Tasks bằng `task-create --spec ... --deps ...` theo topo order cho phần scope đã duyệt, dùng native dependency IDs trong `--deps`.
3. Native Run không tự schedule/parse manifest hoặc registry. Task spec phải tự chứa target/change/constraints/ownership/observable AC và role/skill/template refs. Chỉ `worker-start --task ...` khi dependencies và gate được kiểm chứng; code workers dùng placement worktree riêng đúng guide.
4. Xác nhận start receipt và active Dispatch trước khi tính worker đã chạy; không coi enqueue là acknowledgment. Nếu start lỗi/uncertain thì đọc failedStage/residualResources/request receipt và recovery guide; không dispatch lặp khi chưa rõ.
5. Theo dõi `check --wait` bằng các lần chờ tối đa 60 giây để giữ cập nhật; xử lý toàn bộ FIFO delivery, trả lời worker questions, kiểm tra completion đúng active Dispatch và artifacts/CI trước ack. Sau ba lượt chờ rỗng, inspect worker-list của đúng Run theo guide; absence không phải exit.
6. Native `worker_done` hợp lệ settle Task/Dispatch; chất lượng vẫn được kiểm chứng riêng. Với settlement được chấp nhận, reuse ngay cho task hợp lệ tiếp theo hoặc `worker-release`; chỉ retain nếu user yêu cầu. Không dùng terminal close thay recovery, không retry task chưa chứng minh failed/stopped.
7. Findings tạo remediation có owner/contract rõ và giữ lịch sử; gate fail/blocked không mở task phía sau. Handoff cuối liệt kê actual Run/Task/Dispatch IDs, revision/diff, artifacts, commands/status/logs, review, risk và next owner.

## Handoff hiện tại

```yaml
task_id: null  # Pre-approval proposal; no native Task created.
run_id: null
dispatch_ids: []
role: orchestrator
status: awaiting_human_approval
artifact_paths:
  - docs/proposals/auth-sdlc.md
  - reports/preflight/auth-sdlc.json
evidence:
  - command: orca status --json
    exit_code: 0
    log_path: reports/preflight/auth-sdlc.json
  - command: orca skills get orchestration --full
    exit_code: 0
    log_path: reports/preflight/auth-sdlc.json
  - command: orca orchestration run-current --json
    exit_code: 0
    result: run_null
    log_path: reports/preflight/auth-sdlc.json
  - command: python scripts/validate_repo.py --task examples/task-auth.json
    exit_code: 0
    log_path: reports/preflight/auth-sdlc.json
  - command: python -m unittest discover -s tests -v
    exit_code: 0
    result: 3_tests_passed
    log_path: reports/preflight/auth-sdlc.json
risks:
  - Missing approved scope, auth policy decisions, named approvers and execution budget.
  - Current HEAD has no files; untracked SDLC inputs need a verified worker baseline.
  - Target application repository/revision and staging environment are unavailable.
  - No remote CI, application tests or staging results verified.
next_owner: Human Product Owner
approval_required: true
```

Đề nghị human trả lời: chọn A/B; chấp thuận hoặc sửa MVP/giả định auth và gates; chấp thuận budget; chọn baseline commit permitlist hay snapshot. Nếu B, cung cấp repo/revision được phép đọc. Nêu người có quyền duyệt product/security/architecture/release khi đến gate; chưa có người duyệt thì gate giữ blocked.

Yêu cầu approval đến từ chỉ thị trực tiếp của user và `policies/approval-rules.md` (initial scope, significant ADR/auth-policy, risk exceptions), cùng brief yêu cầu human approval trước staging; không phải yêu cầu tự suy diễn từ skill.
