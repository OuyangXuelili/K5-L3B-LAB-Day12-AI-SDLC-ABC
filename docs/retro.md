# Retro nhóm

## Phase 2 (nhanh)
- Ghi nhận từ phiên hỗ trợ Phan Anh ngày 21/11/2026; chưa khẳng định là ý kiến đồng thuận cả nhóm.
- Điều tốt: giữ một sim cho live/headless; probe CLI kiểm chuyển kho và nâng cấp xuyên ngày;
  97 test và benchmark có command tái chạy, không nhập kết quả bằng tay.
- Điều tệ: fixture P1 ngầm giả định cá đứng yên và invuln_ticks chưa tồn tại;
  v1.1 làm lộ các giả định này. Lệnh live thực còn lộ lỗi console Windows cp1252.
  Đối chiếu PRD-0 cho quán và QA trực quan chưa thực hiện được.
- 1 hành động cho Phase 3: trước khi nhận Ticket-03, review chéo schema quán và các
  biên tick/đổi pha, đo FPS thực ở 1280×720, ghi link review thật; không tự nhận đã hoàn tất.

## Phase 4 (cuối)
- Rà hành động P2: đã có phép đo FPS thật ở 1280×720 và kiểm UI bằng ảnh. Chưa có
  bằng chứng review chéo giữa người với người; việc này vẫn phải làm trước release.
- Điều tốt: cùng một Session giúp soak dùng lại luật thật, không phải viết bản mô phỏng riêng.
- Điều vướng: test luật không phát hiện chữ mất dấu hay hướng dẫn bị cắt ở cuối màn hình.
  Phải kiểm bằng trình duyệt và tăng chỗ cho cảnh báo.
- Số liệu đóng góp: xem `git shortlog -sne HEAD` và lịch sử nhánh; không tính các
  commit của starter thành đóng góp nhóm. Token/chi phí không có số đo.
- Lỗi AI: chuỗi UTF-8 qua terminal bị thành dấu hỏi; đọc diff và ảnh UI giúp phát hiện.
- Việc tiếp theo: Integrator nhận review nhánh cuonglk, chạy lại kiểm chứng trên main;
  QA rà cùng gói ở macOS/Linux rồi mới công bố tag và release.
- Đây là ghi nhận kỹ thuật cho phần bàn giao P4, cần nhóm bổ sung nhận xét sau buổi demo.
