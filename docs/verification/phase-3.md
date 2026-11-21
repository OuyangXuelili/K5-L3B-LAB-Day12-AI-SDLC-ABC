# Ma trận kiểm chứng Phase 3 — Nguyễn Hữu Mạnh

Ticket-03 “Mùa Nước Nổi”, Test Contract v1.2. Nhóm đã thống nhất dùng kho cá thể. ABC có bốn thành viên nên phạm vi bàn giao là cơ chế độ tươi bắt buộc. [Nguồn Ticket-03](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-3) · [ADR 0003](../adr/0003-phase3-ticket-03.md)

| Mã | Tiêu chí và cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P3-01 | CLI đọc kho đúng phiên bản, giữ ID/độ tươi, từ chối kho đếm mã 2 trước khi chạm đầu ra | [Test kho](../../tests/test_inventory_v12.py), [test CLI sát ngưỡng](../../tests/test_phase3.py), `gather_inventory` trong [báo cáo](../proof/phase-3/verification.json) | Đạt |
| AC-P3-02 | Hao độ tươi đầu tick, giữ hàng ươn trong giỏ/kho, pause dừng hao. `spoiled` đúng một lần và theo ID số | [Test Phase 3](../../tests/test_phase3.py), [kết quả](../proof/phase-3/verification.json) | Đạt |
| AC-P3-03 | Giữ cá thể tươi nhất, hòa theo ID. Hai đơn hỏng cùng tick thử giữ lại theo thứ tự, đơn thiếu chuyển `unfulfillable` | [Test Phase 3](../../tests/test_phase3.py), [kết quả](../proof/phase-3/verification.json) | Đạt |
| AC-P3-04 | Chốt giá theo các ID thật tại bếp, bao gồm biên `floor`. Tính boa từ giá đã chốt, giao được đúng tick hết kiên nhẫn/đóng ca | [Test Phase 3](../../tests/test_phase3.py), [kết quả](../proof/phase-3/verification.json) | Đạt |
| AC-P3-05 | Kho qua `day` không hao thêm tại chuyển pha, Shop giữ nguyên độ tươi, ngày mới cấp ID tiếp nối, replay cùng seed giống từng byte | [Test Phase 3](../../tests/test_phase3.py), `day_replay` trong [báo cáo](../proof/phase-3/verification.json) | Đạt |
| AC-P3-06 | Trình duyệt hiển thị % độ tươi và nhãn ươn ở giỏ và kho. Qua pause, chuyển ca, mua oxy và hoàn tất hai ngày | [Ảnh HUD](../proof/phase-3/phase-3-gather-hud.png), [kết quả Chrome](../proof/phase-3/phase-3-hud.json) | Đạt kiểm tự động ở 1280×720 |
| AC-P3-07 | Hồi quy P1–P2, kiểm danh sách nhóm và mẫu kho v1.2, benchmark headless 22.200 tick | [Báo cáo cuối](../proof/phase-3/verification.json), [mốc trước khi sửa](../proof/phase-3/phase-2-baseline.json) | 111/111 test. Benchmark 0,736 s trên máy này. |

## Chạy lại

```powershell
python tools/verify_phase2.py --out docs/proof/phase-3/verification.json
python tools/check_inventory.py docs/contracts/inventory.phase3.sample.json
python -m chonoi.live --mode day --days 2 --seed 7 --scenario docs/scenarios/phase-3-demo.json
```

Trong demo, chọn **Chơi** và **Xuống nước**. Giỏ có sẵn ba cá thể, một cá thể bắt đầu ở đúng 30 và ươn ở tick đầu. Nhấn **P** để kiểm pause. Nhấn **E** tại bến rồi chọn **Mở ca tối** để xem ID, độ tươi và kho khả dụng. Demo dùng dữ liệu fixture. Probe file trong báo cáo hái nguyên liệu bằng input thật.

## Phạm vi bằng chứng

- Bản chuẩn trước thay đổi có 97 test đạt và [kiểm HUD Phase 2 trên Chrome](../proof/phase-3/phase-2-hud-baseline.json). [Mốc starter](../proof/phase-3/starter-baseline.md) ghi riêng 32 test ban đầu.
- Các assertion v1.1 cần đổi do giỏ, kho, `lost`, món trên tay và giá đổi schema hoặc luật. Các kiểm tra thứ tự sự kiện, giới hạn sức chứa, LIFO, thu tiền, pause, Shop và chuyển pha vẫn chạy. Chi tiết chuyển fixture nằm trong [CHANGELOG.md](../../CHANGELOG.md).
- Ảnh và FPS đo bằng Chrome headless trên máy hiện tại với fixture demo. Người dùng xác nhận đã review và đồng ý đẩy bản bàn giao. Kết quả test ẩn chưa được xác nhận.
