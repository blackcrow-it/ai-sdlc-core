# Project Brief — Demo authentication feature

## Objective
Thêm đăng nhập vào một **ứng dụng demo** hiện có (chưa có source code trong bộ config này).

## Users
- Visitor: xem trang công khai.
- Member: đăng nhập, xem trang thành viên.
- Admin: quản lý quyền (chỉ thiết kế ở MVP, chưa triển khai).

## Success criteria
- User stories, SRS và API contract được tạo và review.
- Có task backend + frontend với boundary rõ, có regression tests.
- Chỉ phát hành lên staging sau CI và human approval.

## Known constraints
- Không sử dụng production credentials hoặc dữ liệu thật.
- Chưa lựa chọn framework: Architect phải kiểm tra repo ứng dụng đích trước khi đề xuất.
- Đây là **đề bài kiểm tra SDLC**, không phải dự án có đủ source code để tự build.

## Open decisions
- Cơ chế đăng nhập (password/OAuth/passkey)?
- Session lifetime và chính sách khóa tài khoản?
- Phiên bản API cần backward compatibility?
