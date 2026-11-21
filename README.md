# Quán Ăn Chợ Nổi — nhóm ABC

Game 2D: sáng lặn bắt cá/hái rau, tối nấu và phục vụ trên nhà bè, cuối ngày mua
nâng cấp. Bản hiện tại dùng Test Contract **1.3**, có 5 kế hoạch ngày, 6 món,
2 bếp/4 bàn, cá sấu và độ tươi từng nguyên liệu. Nhóm 4 người tập trung phần lõi.

## Chạy từ clone sạch

Cần Python **3.10+** và trình duyệt hiện đại; chơi game không cần pip hay API key.
Trên macOS/Linux, dùng ba lệnh:

```bash
git clone https://github.com/OuyangXuelili/K5-L3B-LAB-Day12-AI-SDLC-ABC.git
cd K5-L3B-LAB-Day12-AI-SDLC-ABC
python3 -m chonoi.live --mode day --days 5
```

Mở địa chỉ in trong terminal. Nếu nhánh bàn giao chưa tích hợp, thêm
`--branch cuonglk` vào lệnh clone. Windows dùng `python` thay `python3` nếu cần.
Gói ZIP: giải nén, vào thư mục `chonoi-v1.0.0` rồi chạy lệnh live như trên.

WASD/mũi tên di chuyển; **E** hái, cập bến, nấu, bưng và phục vụ; **Space** bắt
cá; **P/Esc** tạm dừng; **R** chơi lại. Nhả E/Space trước lần bấm tiếp theo.
Tại bếp, E nhận đơn chờ cũ nhất; khi chín, E bưng rồi đến đúng bàn và E giao.
Shop dùng nút mua và Xong. Nâng cấp áp dụng từ ngày sau. Nút **Tương phản cao**
ở đầu màn hình, lưu cài đặt trong trình duyệt. Cảnh báo có chữ, không chỉ dùng màu.

Tiền tính bằng nghìn đồng. Điểm = `earned + 100 × floor(reputation)`.
Mua nâng cấp giảm `money`, không giảm `earned`. Nguyên liệu ươn dưới 30 điểm tươi
không dùng nấu được. Kho dư bỏ sau Shop.

## Test và kiểm chứng

Một lệnh chạy test, không cài dependency:

```bash
python3 -m unittest discover -s tests -v
```

Benchmark/UI cần Playwright và Chromium, cài riêng một lần:

```bash
python3 -m pip install -r requirements-bench.txt
python3 -m playwright install chromium
python3 tools/verify_phase4.py
```

Trên Linux tối giản, Chromium có thể cần thư viện hệ thống:
`python3 -m playwright install --with-deps chromium`.
`verify_phase4.py` lưu test, replay soak, số đo render, ảnh UI và kiểm gói giải nén
vào `docs/proof/phase-4/`. Kết quả máy phát triển không thay số đo máy chấm.

```bash
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json
python3 -m chonoi.soak --seed 7 --days 10 --out soak.json
python3 -m chonoi.headless --mode day --days 1 --seed 7 --ticks 22200 --out day.jsonl
```

Benchmark dùng cảnh gather thật ở 1280×720; 1% low dựa trên 1% frame chậm nhất.
Mốc báo cáo: trung bình 60 FPS, 1% low 30 FPS, tải trong 10 giây.
Soak chạy bot đứng yên qua toàn bộ đồng hồ sáng/tối/Shop, lặp kế hoạch D1–D5;
ngưỡng đạt là hoàn tất 10 ngày, không crash. Không ghi leaderboard.

Hai mode độc lập bàn giao kho qua file:

```bash
python3 -m chonoi.headless --mode gather --seed 42 --ticks 10800 --inventory-out kho.json --out gather.jsonl
python3 -m chonoi.headless --mode quan --seed 42 --ticks 10800 --inventory kho.json --out quan.jsonl
```

Kho v1.3 là `{"items":[{"id":"I1","kind":"ca_loc","fresh":100}]}`.
Kho đếm v1.0/v1.1 bị từ chối ở bản hiện hành. Xem [hợp đồng](docs/contracts/README.md)
và [CHANGELOG](CHANGELOG.md) khi chuyển fixture cũ.

## Đóng gói và demo

`python3 tools/package_release.py` tạo ZIP và SHA-256 trong `dist/`.
[Release notes và checklist](docs/release-v1.0.0.md) ghi bước tích hợp main,
tag `phase-4`/`v1.0.0` và đính kèm gói. Nhánh cuonglk chưa phải release đã công bố.

Demo ngắn: `python3 -m chonoi.live --mode day --days 1 --scenario docs/scenarios/phase-4-demo.json`.
Đây là **fixture có hàng và tiền dựng sẵn**, không phải bằng chứng thu thập thật.
Cập bến bằng E, mở quán, E nấu tại B1, đợi chín rồi E bưng, đi đến T1 và E giao.
Sau ca, đóng Shop. Demo trực tiếp hoặc video `.mp4` dưới 5 phút phải cho thấy
một ngày tới Shop, test, đóng góp từng người và bằng chứng theo ma trận.

## Bàn giao và quy tắc lab

- Một fork chung public, nhóm 4–6 người, collaborator quyền Write. Thành viên và
  thỏa thuận ở [TEAM](TEAM.md), `team_size` phải khớp. Mỗi người ít nhất 3 commit
  có nội dung; làm cặp ghi `Co-authored-by:`. Không sao chép repo nhóm khác.
- Tag trên main: `phase-1` trước 1:00, `phase-2` trước 1:55, `phase-3` trước 2:30,
  `phase-4` và Release v1.0.0 trước 3:00 tính từ lúc bắt đầu lab. Ghi trung thực phần chưa đạt.
- [Phase 1](docs/verification/phase-1.md), [Phase 2](docs/verification/phase-2.md),
  [Phase 3](docs/verification/phase-3.md), [Phase 4](docs/verification/phase-4.md).
- Nhật ký AI, làm rõ, retro và phản tư cá nhân trong `docs/`. Không dựng review,
  số đo hoặc bằng chứng nộp đúng giờ. CI, PR và ruleset là lựa chọn của nhóm.
- Tuning lấy từ dữ liệu, RNG qua Streams, ID qua IdAllocator. Live/headless dùng
  chung Session. Không đưa đồng hồ thực vào gameplay.

| Hạng mục | Điểm |
|---|---:|
| Test ẩn và hồi quy | 25 |
| Làm việc nhóm | 25 |
| Kiểm chứng và bằng chứng | 15 |
| Harness AI | 10 |
| Đánh giá và retro | 10 |
| Chất lượng sản phẩm | 10 |
| Demo | 5 |

## Sáng tạo của nhóm

Chưa khai mở rộng tùy chọn. Hoàn thiện lõi trước; phần tự thêm phải tắt ở headless
hoặc giữ kết quả contract. Asset phải có quyền sử dụng và ghi trong [CREDITS](CREDITS.md).
Không commit secret. Starter chưa có giấy phép rõ; xem [LICENSE](LICENSE).
Nguồn đề: [Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg).
