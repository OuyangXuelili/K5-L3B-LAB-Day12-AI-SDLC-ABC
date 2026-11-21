# Lê Khánh Cường — Phase 4

Phần tôi nhận là QA và bàn giao cuối. Nhánh `cuonglk` bổ sung soak 10 ngày,
benchmark cảnh lặn, tương phản cao và gói chạy từ mã nguồn.
Các commit chính: `7d001ad` (soak/contract), `1293abc` (benchmark/test),
`a4f19da` (cảnh báo), `d55219d` (đóng gói/kiểm chứng).

Điểm cần chú ý nhất khi tích hợp là vòng ngày cũ chỉ tra kế hoạch đến D5 và
bộ đọc kho chưa nhận v1.3. Tôi giữ nguyên schema cá thể để không làm lại phần
độ tươi của Mạnh. Bộ kiểm chứng chạy lại cả test cũ và gói giải nén.

Một lỗi trong phần hỗ trợ lập trình là chuỗi tiếng Việt bị đổi thành dấu hỏi
khi đi qua terminal. Kiểm tra mã và chạy trình duyệt phát hiện được lỗi này.
Đã sửa chuỗi UTF-8 rồi kiểm lại các cảnh báo bằng ảnh.

Bài học là kết quả test chưa đủ cho UI; phải nhìn cả màn hình để thấy chữ bị
cắt hoặc mất dấu. Review chéo với thành viên khác chưa được ghi nhận; tôi cần
xác nhận bước này trước khi nhóm công bố release.
