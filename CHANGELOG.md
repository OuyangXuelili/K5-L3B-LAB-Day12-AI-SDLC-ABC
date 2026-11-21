# Changelog
## Unreleased

## phase-4 — 21/11/2026 (nhánh cuonglk)

- Contract 1.3, bench_cmd và soak_cmd; bộ đọc kho giữ schema v1.2.
- Soak nhiều ngày lặp D1–D5 trong cùng Session; giữ RNG, ID, tiền và nâng cấp.
- Đo FPS/1% low/load từ Chromium 1280×720, không quy đổi tốc độ mô phỏng thành FPS.
- Cảnh báo bằng chữ độc lập, tương phản cao lưu theo trình duyệt; kiểm ba cảnh báo.
- Gói ZIP/SHA-256, test bản giải nén, báo cáo và kịch bản release/demo.
- Thêm 4 test hồi quy, gồm trọn luồng demo có phục vụ/thu tiền; không đổi yêu cầu test P1–P3. Tag/Release chờ tích hợp main.

## phase-3 — 21/11/2026

- **Breaking change:** Test Contract v1.2 thay kho đếm bằng `{"items":[{"id":"I1","kind":"ca_loc","fresh":100}]}`. Kho rỗng dùng `{"items":[]}`. CLI v1.2 từ chối kho đếm bằng mã 2.
- Khi đổi fixture, thay `gather.hold` dạng danh sách loại và `quan.stock` dạng bảng đếm bằng mảng cá thể. Cấp ID duy nhất cho từng phần, giữ thứ tự vào giỏ. Dùng `fresh:100` nếu fixture không kiểm độ tươi. `customers[].reserved` khai mảng ID hoặc bỏ trường để quán tự cấp. Món đã ở bếp/trên tay cần `base_price` đã chốt.
- Độ tươi hao theo tick và giữ chính xác ở ngưỡng 30. Quán thử giữ lại phần hỏng, chốt giá và tính boa theo giá đã chốt. HUD hiển thị % và nhãn hàng ươn.
- Chuyển các fixture và assertion cũ vì kho, `lost` và món đổi cấu trúc, giá thay đổi theo độ tươi. Giữ các kiểm tra hành vi P1–P2 còn hiệu lực và thêm các ca v1.2. Kết quả 111/111 test. [Ma trận kiểm chứng](docs/verification/phase-3.md)

## phase-2 — 21/11/2026 (mốc cục bộ)

- Tích hợp Ticket-02 / contract v1.1: 6 nguyên liệu, 6 món, 2 bếp, 4 bàn.
- Hoàn thiện quán: khách, giữ nguyên liệu, nấu, bưng, phục vụ, tiền/boa/uy tín, đóng ca.
- Vòng 1–5 ngày, kế hoạch thu gom, Shop oxygen/hp, pause, cá bơi/sinh và cá sấu.
- Menu/intro/result/summary/HUD dùng cùng Session với headless; sửa console Windows.
- Thêm 33 test (tổng 97), verify_phase2, bằng chứng replay/benchmark và hồ sơ Phan Anh.
- Còn review con người, đối chiếu payload PRD-0, QA hình ảnh/FPS, push/tag trên remote.
