# ADR 0004 — Kiểm chứng và đóng gói Phase 4

Phase 4 nâng manifest lên v1.3, giữ gameplay và kho cá thể của v1.2.
Các thay đổi khung được giới hạn ở đọc phiên bản, kế hoạch ngày lặp và xử lý
ngắt kết nối trình duyệt bình thường. Không đổi schema kho hay công thức món.

Benchmark mở đúng giao diện gather bằng Chromium, viewport 1280×720 và đo
requestAnimationFrame khi renderer đang hoạt động. 1% low là nghịch đảo thời
gian frame trung bình của 1% frame chậm nhất, làm tròn số frame lên.
load_ms đo từ bắt đầu điều hướng tới khi giao diện nhận snapshot và có FPS.
Đây là số đo Chromium headless trên máy phát triển, không thay cho máy chấm.

Soak dùng cùng Session, RNG và bộ cấp ID, cho mỗi pha chạy hết thời gian tự nhiên.
Bot đứng yên không thu hàng, không mua nâng cấp. Test hồi quy riêng dựng hàng
và tiền để kiểm ID, số dư và cấp xuyên 10 ngày. CLI day thông thường vẫn chỉ
nhận 1–5 ngày; chỉ soak mở rộng số ngày và lặp kế hoạch D1–D5.

Gói ZIP dùng danh sách thư mục/tệp cho phép, loại cache, Git, secret và file tải
về của người dùng. Bản đóng gói là mã nguồn chạy bằng Python, không phải binary
có sẵn runtime. Phụ thuộc benchmark được cài riêng; chơi game không cần pip.

Tag phase-4 và Release v1.0.0 chỉ công bố từ cùng commit trên main sau tích hợp.
Không gắn tag từ nhánh cuonglk rồi ghi thành đã bàn giao main.
