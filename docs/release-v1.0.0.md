# Quán Ăn Chợ Nổi v1.0.0

Út Sen lặn bắt cá, hái rau rồi mang nguyên liệu về mở quán. Bản này có vòng
5 ngày, nâng cấp oxy/máu, cá sấu và độ tươi cho từng nguyên liệu. Phase 4 bổ sung
tương phản cao, cảnh báo bằng chữ, benchmark trình duyệt và soak nhiều ngày.

## Chạy bản đóng gói

Giải nén `chonoi-v1.0.0.zip`, vào thư mục `chonoi-v1.0.0`, cài Python 3.10 trở lên.

```bash
python3 -m chonoi.live --mode day --days 5
```

Mở địa chỉ in ở terminal. WASD/mũi tên để di chuyển, E tương tác, Space bắt cá,
P/Esc tạm dừng, R chơi lại. Nút Tương phản cao ở đầu màn hình. Shop mua qua nút
và đóng bằng Xong. Windows dùng `python` nếu không có `python3`.

Kiểm thử: `python3 tools/verify_phase4.py` sau khi cài phụ thuộc benchmark trong README.
Đính kèm ZIP và file `.sha256` từ `dist/`. Gameplay không cần thư viện ngoài.

## Giới hạn đã biết

- Benchmark tự mở Chromium headless; kết quả phụ thuộc máy, tải nền và driver.
- Không có âm thanh hay leaderboard. Nhóm bốn người ưu tiên phần lõi.
- Bản phát hành là source, không chứa Python/Chromium. Soak dùng bot đứng yên.
- Giấy phép upstream chưa có trong starter; xem LICENSE trước khi phân phối ngoài lớp.
- Cần review nhóm và kiểm máy macOS/Linux. Chưa khẳng định thời hạn lab đã đạt.

## Checklist công bố của Integrator

1. Review nhánh cuonglk, tích hợp vào main và chạy lại `python tools/verify_phase4.py`.
2. Tạo lại ZIP từ đúng commit main; kiểm checksum và bằng chứng.
3. Gắn `phase-4` và `v1.0.0` vào cùng commit đó, đẩy tag.
4. Tạo GitHub Release v1.0.0, dùng nội dung phần đầu tài liệu, đính ZIP và SHA-256.

Workflow `release.yml` có thể làm bước 4 khi đẩy tag v1.0.0. Workflow kiểm tag
phase-4 cùng commit và commit thuộc main, chạy test trên Ubuntu rồi tạo gói.
Nếu đã có Release cùng tên, cần rà bản hiện có thay vì ghi đè tự động.

## Demo dưới 5 phút

- Mở game với `--mode day --days 1 --scenario docs/scenarios/phase-4-demo.json`.
  Nói rõ đây là fixture rút ngắn, có hàng/tiền dựng sẵn.
- Chơi sáng, cập bến, mở quán, nấu/bưng/phục vụ và đóng Shop.
- Bật tương phản cao; mở ảnh kiểm chứng ba cảnh báo nếu demo chưa gặp đủ.
- Chạy test; mở verification và một bằng chứng tương ứng.
- Mở TEAM và lịch sử commit để chỉ phần đóng góp, không nhận việc của thành viên khác.
