# Retro nhóm

## Phase 2 (nhanh)
- Nhóm thống nhất giữ một nguồn luật cho cả bản chơi trực tiếp và headless,
  ưu tiên tích hợp kho trước khi mở rộng giao diện.
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
  Tại mốc bàn giao `2d596ae`, khoảng `f0a1906..2d596ae` có Quang 3, Phan Anh 3,
  Mạnh 4 và Cường 5 commit. Bản cuối có 115 test; soak 10/10 ngày không crash.
- Lỗi AI: chuỗi UTF-8 qua terminal bị thành dấu hỏi; đọc diff và ảnh UI giúp phát hiện.
- Việc tiếp theo: Integrator nhận review nhánh cuonglk, chạy lại kiểm chứng trên main;
  QA rà cùng gói ở macOS/Linux rồi mới công bố tag và release.
- Qua thảo luận, nhóm thống nhất lần sau chốt schema và fixture sớm hơn,
  dành riêng thời gian kiểm giao diện và gói phát hành thay vì dồn vào cuối buổi.
