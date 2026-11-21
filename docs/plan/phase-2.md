# Phase 2 — Phan Nguyễn Phan Anh (alpha19102004)

Nguồn yêu cầu: Ticket-02 do người dùng cung cấp, 10 trang, Test Contract v1.1.
Phạm vi được người dùng giao: hoàn thiện phần Phan Anh và tích hợp Phase 2.
Đây là kế hoạch/bản ghi kỹ thuật; không xác nhận các thành viên đã thực hiện việc dưới đây.

| Lát tích hợp | Đầu mối dự kiến | Thay đổi so với Phase 1 |
|---|---|---|
| Quán | Phan Anh | Hoàn thiện vòng khách/giữ nguyên liệu/nấu/bưng/phục vụ/trả tiền, 2 bếp, 4 bàn, 6 món |
| Ngày/Shop | Phan Anh | Điều phối gather → quan → shop, kế hoạch 5 ngày, tiền/uy tín/nâng cấp xuyên ngày, pause |
| Lặn/kho | Quang hỗ trợ | 6 nguyên liệu, cá bơi/sinh, cá sấu, kho v1.1 |
| Giao diện | Mạnh hỗ trợ | Menu, intro, kết quả, Shop, pause, HUD kế hoạch/cảnh báo |
| QA | Cường hỗ trợ | Hồi quy P1, biên tick, replay seed, benchmark, kiểm kho sáng–tối |

Trong phiên hỗ trợ này Codex triển khai và kiểm tra các phần phụ thuộc để có bản tích hợp;
không gán các sửa đổi đó thành đóng góp đã diễn ra của Quang/Mạnh/Cường.

Mốc lab đề xuất: 0–10 phút đọc/so ticket; 10–20 phút lát quán và contract;
khoảng phút 20 chạy probe tích hợp; 20–45 phút tích hợp ngày/Shop/UI;
45–55 phút hồi quy, bằng chứng, review và tag. Không dùng lịch này làm bằng chứng thời gian thực.

Không làm các mục mở rộng tùy chọn (nhóm 4 người). Không triển khai Ticket-03/04.
