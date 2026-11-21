# Lê Khánh Cường — Phase 4

Tôi phụ trách QA và bàn giao cuối: soak 10 ngày, benchmark cảnh lặn,
tương phản cao và đóng gói. Các commit chính: `7d001ad`, `1293abc`,
`a4f19da`, `d55219d`; kết quả trong [báo cáo P4](../verification/phase-4.md).

Khi tích hợp, tôi tập trung sửa vòng ngày chỉ tra kế hoạch đến D5 và bộ đọc
kho chưa nhận v1.3. Tôi giữ schema cá thể để nối tiếp phần độ tươi của Mạnh,
chạy lại test cũ và kiểm gói giải nén.

AI từng tạo chuỗi tiếng Việt thành dấu hỏi khi đi qua terminal. Đọc mã và
kiểm trình duyệt giúp phát hiện; sau khi sửa UTF-8, các cảnh báo được kiểm lại bằng ảnh.

Qua trao đổi nhóm, tôi rút ra cần kiểm luật, giao diện và gói chạy riêng.
Test xanh vẫn có thể bỏ sót chữ mất dấu hoặc nội dung bị cắt trên màn hình.
