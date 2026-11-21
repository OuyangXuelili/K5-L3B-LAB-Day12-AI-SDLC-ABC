# Kế hoạch Phase 1 (≤ 1 trang)

- Mục tiêu phần Quang: hoàn thiện luật `gather` đã mô tả trong starter, xuất kho ổn định và bàn giao giao diện tích hợp cho quán/UI.
- Nguồn: [PRD-0 / Test Contract v1.0](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-1), đã đọc sau đăng nhập Claude; `game.contract.json` và starter. Luật gather/kho đối chiếu mục D–G; quyết định và sửa lệch ở ADR 0001.

| Việc | Người phụ trách | Phụ thuộc / bàn giao |
|---|---|---|
| Danh sách nhóm, đề xuất thỏa thuận và hợp đồng kho | Quang | Handle lấy từ collaborator hiện có; nhóm xác nhận thỏa thuận |
| Oxy, ngạt, ngất, hái, bắt cá, giỏ | Quang | Theo PRD-0 F/G; payload event theo E |
| Quán: khách, bếp, phục vụ, tiền, uy tín | Phan Anh | Đọc kho `{ "items": ... }`; chưa triển khai trong đợt phần Quang |
| Giao diện/HUD | Mạnh | Chỉ đọc snapshot, gửi input; starter vẫn là cửa sổ thử |
| Kiểm thử hồi quy và tích hợp toàn Phase 1 | Cường; Quang chuẩn bị test gather/kho | Nhận code quán/UI và đối chiếu PRD-0 cho các phần đó |

- Kiểm chứng phần Quang: `python tools/verify_phase1.py`; `python tools/check_inventory.py docs/contracts/inventory.sample.json`.
- Tiêu chí bàn giao nội bộ: test gather và smoke đạt; cùng input/seed sinh JSONL giống từng byte; kho hái thật nạp được vào quán; lỗi đầu vào vẫn mã 2.
- Rủi ro còn lại: luật quán còn TODO, chưa có review con người hay tag Phase 1. Chưa mở issue nên không có link issue để ghi.
