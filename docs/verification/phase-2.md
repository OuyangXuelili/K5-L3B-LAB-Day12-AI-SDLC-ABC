# Bàn giao Phase 2 — Phan Nguyễn Phan Anh, 2A202604004

GitHub: **alpha19102004**. Ngày thực hiện: **21/11/2026**.
Nguồn: Ticket-02 (PDF 10 trang do người dùng cung cấp), Test Contract v1.1.
Phân công dự kiến và chênh lệch P1 → P2: [kế hoạch](../plan/phase-2.md).
Các thay đổi contract/khung: [ADR 0002](../adr/0002-phase2-v11.md).

## Cách kiểm chứng lại

Từ thư mục gốc, chỉ cần Python 3 (Windows/macOS/Linux):

```powershell
python tools/verify_phase2.py
python tools/check_inventory.py docs/contracts/inventory.phase2.sample.json
python -m chonoi.live --mode day --days 5
```

Mở URL terminal in ra. Chọn **Chơi**; WASD/mũi tên di chuyển, E hái/cập bến/nấu/bưng/phục vụ,
Space bắt cá, P/Esc pause, R bắt đầu lại. Shop dùng nút mua và **Xong**.

Demo rút ngắn, **có kho và tiền dựng sẵn bằng scenario**, không phải bằng chứng hái thật:

```powershell
python -m chonoi.live --mode day --days 2 --scenario docs/scenarios/phase-2-demo.json
```

Ở demo: bấm E tại bến để sang tối, chờ khách đến, E tại bếp để nấu;
đợi chín, nhả/bấm E để bưng, đi đúng bàn khách rồi E để giao. Kết ca vào Shop,
mua bình oxy bằng tiền có sẵn; sang ngày 2 thấy mức tối đa 45s.

## Ma trận yêu cầu và bằng chứng

| Ticket-02 | Thực hiện / phép kiểm | Kết quả |
|---|---|---|
| 1.1, 4.1: số chuẩn, 6 nguyên liệu, N5/N6, 8 đàn | manifest v1.1, kiểm kho cũ/mới, P1 smoke thích nghi preset | Đạt test hiện có |
| 1.3: 2 bếp, 4 bàn, 6 món từ dữ liệu | `test_quan_rules.py`, đủ công thức/giá/thời gian trong manifest | Đạt |
| Giữ nguyên liệu, khách theo lịch, đơn cũ nhất, chọn tương tác | Test chống nhận quá kho; lịch 120+900k; hòa bếp/bàn/id | Đạt |
| Nấu → chín → bưng → giao → ăn → thu tiền/boa | Test vòng phục vụ và biên 50% kiên nhẫn | Đạt |
| Khách bỏ đi, giải phóng giữ chỗ/món; đóng ca không phạt khách chờ | Test timeout, ăn dở trả ngay, quan_end đúng một lần | Đạt |
| 2: vòng gather → quan → shop, kế hoạch 5 ngày | `test_phase2.py`, probe CLI hai ngày, mặc định một ngày 22.200 tick | Đạt |
| Kho sáng → tối, ngất vẫn sang quán với kho rỗng | P1 kho/hái thật probe; test faint và chuyển pha v1.1 | Đạt |
| Shop, đủ đúng giá, max/funds/unknown, áp dụng từ ngày sau | Probe CLI tiền 200 → 0, earned 200 giữ nguyên; ngày 2 oxy 2.700 tick | Đạt |
| 4.2: cạnh nút qua pha, buy không kế thừa, pause mọi timer | Test input, pause gather/quan/shop, resume chạy ngay | Đạt |
| 1.1: cá bơi, phản xạ, sinh theo seed, fixture đứng yên | Test biên/góc, spawn tick 360, age mới = 0, random_fish:false | Đạt |
| 1.2: cá sấu, LIFO, bất tử, recoil, ngất, M2 ngày 3 | Test hit/recoil 60 bước, bất tử, ngạt xuyên bất tử, tie M2 trước M10 | Đạt |
| 4.3: fixture sai mã 2; không ghi đầu ra khi sai trước chạy | Test CLI dữ liệu sai, order assigned thiếu món, giữ vượt kho, day metadata | Đạt |
| 4.4: event pha cũ / snapshot pha mới tick 0 / days_completed | Test chuyển pha, replay giống bytes, Shop cuối phải đóng | Đạt |
| 2: menu/intro/result/summary/shop/HUD | Đã triển khai, unit kiểm live flow, HTTP `/` và `/state` mã 200; JS syntax check | Chưa QA trực quan |
| Hiệu năng headless ≤20s / 22.200 tick | Đạt giới hạn 20s; thời gian từng lượt trong JSON thực thi | Đạt trên máy hiện tại; chưa đo máy chấm |
| ≥30 FPS ở 1280×720 | Có bộ đếm tại `canvas.dataset.fps`; công cụ browser không khả dụng | Chưa đo |
| Payload/fixture quán đầy đủ theo PRD-0 v1.0 | Ticket-02 không nhắc lại toàn bộ; ADR ghi định dạng đang dùng | Cần PO đối chiếu |

## Kết quả thực thi và lượt tích hợp

- Trước thay đổi: **64 test P1 đạt**, xem [baseline](../proof/phase-2/baseline-phase-1.json).
- Lượt tích hợp sau lát quán/day: probe kho đạt nhưng 11 assertion P1 thất bại,
  xem [bằng chứng lần đầu](../proof/phase-2/mid-integration.json).
  Hai nguyên nhân: fixture cá P1 cần `random_fish:false` để giữ đứng yên;
  `invuln_ticks` nay hợp lệ nên ca dữ liệu lỗi dùng số âm.
  Các assertion còn lại là hệ quả file output đã tồn tại sau fixture đầu không còn sai.
- Sau sửa fixture theo ticket: **76 test đạt**, xem [lần chạy lại](../proof/phase-2/mid-integration-after-fix.json).
  Đây là lượt chạy tích hợp thực tế trong phiên hỗ trợ; không khẳng định đúng phút thứ 20 của lab.
- Bản cuối: **97 test đạt**, kiểm TEAM/kho đạt, probe hái thật → cập bến → quán đạt,
  replay hai ngày giống từng byte, benchmark đạt. Nguồn số đo: [verification.json](../proof/phase-2/verification.json).
- Lệnh mở live chạy được trên Windows; sửa thông báo terminal dùng ASCII để tránh
  `UnicodeEncodeError` trên console cp1252. HTTP trả Menu và không có lỗi sim.
- Kiểm cú pháp JavaScript bằng `node --check` đạt; Node chỉ dùng khi kiểm tra,
  không phải dependency để chơi game hoặc chạy `verify_phase2.py`.
- [HTTP và cú pháp JS](../proof/phase-2/live-check.json): máy chủ thật trả Menu,
  không có lỗi. Không có screenshot hoặc số đo FPS vì browser host không khả dụng.
- [Chạy đủ 5 ngày](../proof/phase-2/five-days.json): seed 7, 111.000 tick,
  đóng đủ 5 Shop; hash JSONL và dòng end được lưu. Chạy lại bằng
  `python -m chonoi.headless --mode day --days 5 --seed 7 --ticks 111000 --out out.jsonl`.
- [Dấu vết nguồn ticket](../proof/phase-2/ticket-source.json) lưu tên PDF, 10 trang
  và SHA-256 để phân biệt nguồn yêu cầu với các lựa chọn triển khai trong ADR.

## Phạm vi bàn giao và việc cần nhóm thực hiện

Đã chuẩn bị bản chạy, code, test, bằng chứng và tài liệu phần Phan Anh.
Lịch sử dùng danh tính Git cấu hình của alpha19102004; không tạo commit dưới tên thành viên khác.
Tag `phase-2` là mốc cục bộ sau kiểm chứng, không phải bằng chứng đã nộp đúng giờ.

Chưa có review chéo, xác nhận thỏa thuận nhóm, push tag lên GitHub, kiểm hình ảnh/FPS
hoặc kết quả test ẩn. Người đọc lại cần đối chiếu payload quán PRD-0 trước khi push.
AGENTS.md yêu cầu người đọc lại thay đổi trước khi đẩy; bản này không tự nhận hoạt động đó đã diễn ra.
Nhóm 4 người không bắt buộc mở rộng nên giữ toàn bộ mục mở rộng tắt.
