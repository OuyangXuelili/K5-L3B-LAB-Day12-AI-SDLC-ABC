# Nhật ký dùng AI (theo phase và theo người)

## Phiên hỗ trợ Phan Anh — 21/11/2026

- Phase 2, alpha19102004: Codex triển khai theo Ticket-02 người dùng cung cấp;
  đọc PDF ảnh qua trích ảnh JPEG để đối chiếu đủ 10 trang. Không gọi LLM API từ game.
- Công việc: so P1/P2, ADR, hoàn thiện quán, dữ liệu v1.1, day/Shop/pause,
  cá bơi/sinh/cá sấu, live/HUD, 33 test mới, command verify_phase2 và hồ sơ bàn giao.
- Kiểm chứng thật: baseline 64 test, tích hợp 76 test, bản cuối 97 test;
  [bằng chứng](proof/phase-2/verification.json). Token/chi phí phiên không có số đo, không ước lượng bịa.
- Sai sót phát hiện/sửa: lỗi cú pháp ban đầu ở dish_picked; fixture P1 cần random_fish:false;
  invuln_ticks nay được phép; console cp1252 không in được tiếng Việt khi chạy live.
- Giới hạn: công cụ web không đọc được lab board; tự động duyệt chặn đọc cửa sổ Edge
  đang là Zalo vì nội dung riêng tư không liên quan. Browser host không khả dụng khi mở
  preview localhost. Không ghi đã xem PRD-0, review con người, đo FPS hoặc nộp đúng giờ.
- Danh tính commit lấy từ Git đã cấu hình (alpha19102004), không sửa tác giả của người khác.

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|
| 1 | Trần Văn Quang — OuyangXuelili | Codex; tên model không hiển thị trong phiên | Triển khai gather, test, công cụ kiểm kho/replay và bản bàn giao. Chưa có xác nhận con người đã review. | Không có thống kê token/chi phí phiên; không gọi API LLM từ ứng dụng | Test đầu dùng alias `python3` Windows Store, trả mã 9009; sửa helper dùng Python đang chạy trên Windows. |
| 1 | Trần Văn Quang — OuyangXuelili | Codex; tên model không hiển thị trong phiên | Đọc PRD-0 trên tab Chrome sau người dùng đăng nhập, rà từng file và đối chiếu Test Contract D–G; sửa event và bổ sung test. | Không có thống kê token/chi phí phiên; không gọi API LLM từ ứng dụng | Ban đầu kết luận quá sớm từ trang chưa đăng nhập. PRD có đầy đủ luật; bản đầu dùng sai tên trường event. Đã sửa theo nguồn chính thức, không giữ giả định thay cho yêu cầu đã rõ. |
| 1 | Trần Văn Quang — OuyangXuelili | Codex; tên model không hiển thị trong phiên | Rà diff, chạy lại kiểm chứng, tổ chức ba commit theo phạm vi và cập nhật link bàn giao theo yêu cầu người dùng. | Không có thống kê token/chi phí phiên; không gọi API LLM từ ứng dụng | Dùng email GitHub noreply; quét file bàn giao chưa phát hiện key hoặc đường dẫn người dùng. Chưa ghi nhận review chéo của thành viên. |
