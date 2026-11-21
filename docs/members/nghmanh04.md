# Nguyễn Hữu Mạnh — nghmanh04

- Phần phụ trách là Ticket-03, phân tích thay đổi kho và luật, triển khai tích hợp v1.2, cập nhật HUD và kiểm chứng. Xem [ADR 0003](../adr/0003-phase3-ticket-03.md) và [ma trận bàn giao](../verification/phase-3.md).
- Tích hợp theo thứ tự adapter kho, mô phỏng và giao diện, rồi cập nhật tài liệu/bằng chứng. Việc chuyển contract được nhóm xác nhận trước khi bật v1.2 trong manifest.
- Phép kiểm trình duyệt ban đầu dùng đường dẫn API tương đối sai và kỳ vọng lặp ID ngày một ở ngày hai. Sau khi sửa phép kiểm, cùng fixture qua hai ngày với ID mới và giữ được độ tươi qua pha.
- Bài học từ thay đổi là giữ tính toán độ tươi độc lập với cách hiển thị, nhất là tại ngưỡng 30 và các biên làm tròn giá. [Kết quả thực thi](../proof/phase-3/verification.json)
