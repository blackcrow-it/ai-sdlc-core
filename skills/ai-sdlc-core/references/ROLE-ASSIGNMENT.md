# Hướng dẫn gán role vào worker Orca

1. Task nên có `owner_agent` khớp `agents/registry.json`.
2. Orchestrator đọc `agents/<role>.md`, policy, artifact được duyệt và task contract.
3. Task contract nằm ở đúng một tracker đã chọn khi setup (`tracker` trong `.ai-sdlc/project.json`; mặc định `.ai-sdlc/tasks/`), viết theo `references/TASK-AUTHORING.md`; render spec tự chứa bằng `sdlc.py spec --task <file-hoặc-issue-body>` (gồm role, policy, cấu hình dự án, `allowed_paths`, test seams, lệnh scope check, kiểm tra, review và output).
4. Worker không được cấp quyền dựa trên lời nhắc; cấu hình quyền trong Orca/CLI/sandbox/CI.
5. Điều phối phải xác thực các sự kiện worker đúng theo CLI hiện tại (`orca skills get orchestration --full`).
6. Khi worker trả kết quả, thu thập commit/diff, artifacts, test logs và kết quả `sdlc.py scope`; reviewer (một worker khác, dùng skill `sdlc-code-review` với ba trục Spec, Standards, Risk) không được là tác giả cùng task.
7. Chỉ điều phối tiếp task phụ thuộc khi quality gate đạt; nếu không, tạo remediation task.

## Lưu ý
Một role ≠ một tiến trình cố định. Cùng một provider CLI có thể được điều phối ở nhiều role khác nhau qua những task spec khác nhau. Đừng giả định Orca đọc `registry.json` tự động.

## Chọn CLI theo công việc

`orca.agent` là CLI mặc định (`claude`, `codex`, `antigravity`, `opencode`, `cursor` hoặc `opencode2`, theo agent ID mà Orca nhận). `orca.role_agents` là map tùy chọn từ
role ID đang bật sang CLI; role không có entry kế thừa mặc định. Ví dụ:

```json
{
  "agent": "claude",
  "role_agents": {
    "business-analyst": "claude",
    "frontend-developer": "antigravity",
    "backend-developer": "codex",
    "code-reviewer": "claude"
  },
  "worktree_strategy": "per-task",
  "max_parallel_workers": 2
}
```

Đây là phần `orca` của config, không phải config đầy đủ hay xếp hạng năng lực CLI. `/sdlc-setup` hỏi lựa chọn
và ghi bằng `init --agent <id> --role-agent <role>=<id>` (lặp flag theo role). Config cũ không có map giữ nguyên
hành vi. Không dùng role đã tắt, không dùng tên skill hoặc task ID làm key. Owner/reviewer trong task contract
vẫn là role, không thay thành tên CLI; không thêm bản sao map vào tracker.

Orchestrator áp dụng `role_agents[owner_agent]` rồi `agent`; reviewer dùng `role_agents[reviewer_agent]` rồi
`agent` riêng. `activate --agent <id>` chỉ thay mặc định trong prompt của lần chạy đó, không ghi config và không
ghi đè role đã chọn riêng. Smoke dùng role `business-analyst`. Spec hiển thị owner/reviewer CLI theo config;
nếu dùng mặc định tạm thời khi activate, đối chiếu lại các role kế thừa trước dispatch, không sửa role override.
CLI render chỉ tạo văn bản; Orca không tự đọc map. Orchestrator truyền CLI đã phân giải vào
`worker-start --agent <id>` theo guide đúng phiên bản và ghi CLI thực tế cùng Task/Dispatch ID trong evidence.

Với OpenCode, dùng `--agent opencode` hoặc `--role-agent backend-developer=opencode` khi init; validation
chấp nhận CLI này từ core 0.1.5. Đây là hỗ trợ cấu hình và render, không chứng minh Orca trên execution host
đã tích hợp đúng phiên bản OpenCode. Kiểm tra agent ID Orca thực sự hỗ trợ, xác thực, skill discovery, công cụ
và lifecycle trước dispatch; nếu host dùng ID khác hoặc chưa hỗ trợ, báo blocker thay vì tự đổi ID/CLI.
Model/effort do cấu hình provider quyết định, trừ khi `orca.role_models` ghim cho role (mục bên dưới). Chỉ truyền flag được guide/CLI trên host
xác nhận hỗ trợ cho OpenCode; generic launch help không đủ để chứng minh khả năng chọn model của provider.

Trước khi trình plan và ngay trước dispatch, kiểm tra trên **execution host**: CLI đã tích hợp và được bật trong
Orca, xác thực sẵn sàng, đọc được core/role skills, có tools và hỗ trợ lifecycle orchestration cần cho task.
Dùng guide `orca-cli`/`orchestration` đang cài và các lệnh discovery read-only được `--help` xác nhận; không bịa
lệnh liệt kê agent, tên model hay đường dẫn skill cho provider. Nếu không xác minh được, ghi unverified/blocker;
không khởi chạy thử để thay cho kiểm tra read-only trước approval. Chỉ có binary trên PATH chưa đủ.

Trình role → CLI và các khả năng còn thiếu trong plan xin duyệt. Khi thiếu CLI/tool, dừng task bị ảnh hưởng và
đề nghị người dùng chọn lại; không tự thay CLI, tự cài tool hay bật integration. Sau lỗi khởi chạy không rõ kết
quả, đối soát receipt/lifecycle theo guide trước mọi retry, không mở worker khác để né lỗi.

## Chọn model/effort theo role

`orca.role_models` là map tùy chọn từ role sang `{model, effort?}`; Orchestrator truyền thành
`worker-start --model <id> --effort <level>` cho cả owner và reviewer. Role chỉ được ghim model khi có entry
`orca.role_agents` riêng, vì model ID phụ thuộc provider và `activate --agent` không được làm model lệch CLI.
Role không ghim giữ model trong cấu hình của CLI. Ví dụ:

```json
{
  "role_agents": {"backend-developer": "codex", "code-reviewer": "claude", "frontend-developer": "antigravity"},
  "role_models": {
    "backend-developer": {"model": "gpt-6.1-sol", "effort": "high"},
    "code-reviewer": {"model": "claude-opus-5-5", "effort": "high"},
    "frontend-developer": {"model": "gemini-3.8-flash-high"}
  }
}
```

Init: `--role-model ROLE=MODEL[:EFFORT]` (lặp theo role; hậu tố `:EFFORT` chỉ được tách khi là
`minimal|low|medium|high|xhigh|max`). Theo help của Orca 1.4.230, `--model` hỗ trợ claude, codex, cursor,
antigravity (và muse); `--effort` cần `--model`; OpenCode chỉ nhận `--model` khi worktree đã tồn tại, CLI trên host
đã xác minh và model khả dụng (validation cảnh báo); opencode2 và CLI khác dùng model của config riêng, nên
validation từ chối model pin cho chúng. Validation không biết model ID có tồn tại hay không: trước dispatch,
xác minh bằng discovery read-only trên execution host (ví dụ `agy models`, `opencode models`, config provider).
Không tự đổi model/effort khi model không khả dụng; báo blocker và xin người dùng chọn lại.

Map không cấp quyền, không tự thay model/effort ngoài `orca.role_models` và không chuyển CLI của phiên đang chạy. Entry `orchestrator` là
lựa chọn khi con người mở phiên điều phối; phiên hiện tại chỉ báo khác biệt, không tự khởi chạy hay handoff.
`/sdlc-implement` trực tiếp vẫn làm trong phiên hiện tại; map chỉ là dữ liệu dispatch cho Orca, không là lý do
để tự tạo worker. Reviewer phải độc lập với tác giả dù dùng cùng CLI hay khác CLI.
