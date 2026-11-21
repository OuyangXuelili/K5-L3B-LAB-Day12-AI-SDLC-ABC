# Mốc kiểm chứng starter cho Phase 3

- Ngày chạy: 2026-11-21
- Mã nguồn được kiểm: `f0a1906` trên `main`
- Môi trường: Windows, Python 3.12.14
- Phạm vi: bộ test công khai của starter và kiểm tra JSONL với cấu hình v1.0 hiện tại. Tiêu chí chấp nhận Phase 3 đang chờ đề chính thức.

## Bộ test công khai

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v
```

Trên Windows, lần chạy đặt `PYTHONPATH=tests;.` và đưa tên `python3.exe` tạm của cùng runtime vào `PATH` để smoke test gọi lệnh đã khai trong `game.contract.json`.

```text
Ran 32 tests in 9.391s

OK
```

## So sánh JSONL

```bash
python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out gather-a.jsonl
python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out gather-b.jsonl
python3 -m chonoi.headless --mode quan --seed 1 --ticks 600 --out quan-a.jsonl
python3 -m chonoi.headless --mode quan --seed 1 --ticks 600 --out quan-b.jsonl
```

Hai file của mỗi mode trùng từng byte. Mỗi file kết thúc tại `ticks=600` với `reason=tick_limit`.

| Mode | SHA-256 của cả hai lần chạy |
|---|---|
| `gather` | `72c30e63f0ca4f4d15de11305be5fae1a967aa6bcd9e00f3deef7d301e1c7ae3` |
| `quan` | `27c95215d88839fdc75af48fbfe1366a276f8d19cec66e4c5cf061c50ee5bdab` |
