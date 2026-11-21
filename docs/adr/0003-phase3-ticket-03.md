# ADR 0003 — Kho cá thể và độ tươi theo Ticket-03

**Chấp thuận ngày 21/11/2026.** Nguyễn Hữu Mạnh (`nghmanh04`) phụ trách Phase 3. Người dùng xác nhận nhóm đã thống nhất chuyển hợp đồng kho sang v1.2. Nguồn là [Ticket-03 “Mùa Nước Nổi”](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-3). Bản đối chiếu Phase 2 là `df64d64`. [Dấu vết ảnh nguồn](../proof/phase-3/ticket-source.json)

## Tác động và thứ tự tích hợp

| Phần | Tệp | Hồi quy và thay đổi |
|---|---|---|
| Kho và đầu vào | `inventory.py`, `scenario.py`, `contract.py`, `headless.py`, `live.py` | Đọc theo phiên bản. Dữ liệu sản xuất v1.2 từ chối kho đếm bằng mã 2. Công cụ kiểm vẫn chọn được v1.0/v1.1 khi rà dữ liệu cũ. |
| Lặn và bàn giao | `sim/freshness.py`, `sim/gather.py`, `sim/aquatic.py`, `sim/day.py`, `runner.py`, `jsonl.py` | Giỏ giữ thứ tự nhặt để rơi LIFO. Dùng chung bộ cấp ID qua các pha và ngày. Kiểm tra ngưỡng ươn, ghi kho nguyên tử, kho rỗng khi ngất và không ghi khi bị giới hạn tick. |
| Quán | `sim/quan.py` | Kho giữ từng cá thể và phần giữ theo ID. Hao tươi trước khi nấu, thử giữ lại đúng một lần. Chốt giá theo độ tươi lúc tiêu hàng. Giao món hợp lệ ở bước kiên nhẫn chạm 0 và ở bước cuối ca. |
| HUD và QA | `web/index.html`, `tests/`, `tools/verify_phase1.py`, `tools/verify_phase2.py` | Giỏ và kho hiển thị phần trăm cùng nhãn ươn. Chuyển fixture cũ sang schema mới và chạy lại các assertion về luật còn hiệu lực. |

Tích hợp adapter và test đọc/ghi trước, nối lặn, quán và `day`, rồi bật manifest v1.2 với HUD tương ứng. Live và headless cùng đọc trạng thái từ `Session`. Nhóm có bốn người, nên bản bàn giao triển khai phần độ tươi bắt buộc.

## Quyết định về độ chính xác và dữ liệu

- Tích lũy độ tươi bằng số hữu tỉ theo tick. Cách này cho phép giữ các giá trị fixture sát 30 và chốt giá bằng phép `floor` tại biên nguyên. Kho file và JSONL giữ đủ chữ số để đọc lại cùng nhánh tại ngưỡng 30. Các số thực khác trong JSONL tiếp tục làm tròn như v1.1.
- Kho quán lập chỉ mục theo ID và tính số lượng khả dụng từ cá thể chưa ươn, chưa được giữ. Khi đồng thời có nhiều đơn bị ảnh hưởng, xử lý từng đơn theo `order_tick` rồi ID bàn. Ở mỗi đơn, nhả tất cả cá thể của đơn trước khi thử giữ lại.
- Contract v1.2 giữ cấu trúc payload món và xác định `base_price` là giá đã chốt theo độ tươi. Quán lưu giá này cùng món tại bếp và trên tay, rồi dùng để tính tiền khi giao. Fixture kiểm `base_price` là số nguyên từ 0 đến giá niêm yết, phù hợp với phép `floor` trên độ tươi từ 0 đến 100. Khách đang ăn giữ `price` và `tip` đã xác định lúc giao. [Dấu vết ảnh bổ sung](../proof/phase-3/ticket-source.json)
- Hướng dẫn đổi fixture và giữ dữ liệu cũ theo phiên bản được ghi trong [CHANGELOG.md](../../CHANGELOG.md) và [hợp đồng tích hợp](../contracts/README.md). Kết quả kiểm chứng nằm trong [ma trận Phase 3](../verification/phase-3.md).
