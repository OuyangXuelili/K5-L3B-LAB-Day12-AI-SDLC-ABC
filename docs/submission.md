# Hồ sơ bàn giao — Quán Ăn Chợ Nổi, nhóm ABC

Bản chuẩn bị nộp dùng Test Contract 1.3. Phần triển khai cuối nằm trên `cuonglk`.
Tài liệu này gom các đầu ra để nhóm rà một lượt trước khi phát hành.

## Sản phẩm và kết quả

Game có hai buổi sáng/tối và vòng ngày với Shop; kế hoạch 5 ngày, nâng cấp oxy/máu,
6 món, 2 bếp/4 bàn, cá sấu và độ tươi theo từng cá thể. Giao diện có menu, pause,
HUD, cảnh báo bằng chữ và tương phản cao. Nhóm bốn người chưa khai mở rộng tùy chọn.

| Kiểm chứng cuối | Kết quả | Nguồn |
|---|---|---|
| Test hiện hành | 115/115 đạt, cả repo và gói giải nén | [verification](proof/phase-4/verification.json) |
| Soak seed 7 | 10 ngày hoàn tất, 0 crash | [soak](proof/phase-4/soak.json) |
| Replay soak | Gameplay giống nhau, bỏ thời gian đo thực | [replay](proof/phase-4/soak-replay.json) |
| Benchmark seed 42, 30 giây | Trung bình 60,0025 FPS; 1% low 59,5238 FPS; tải 1813,87 ms | [benchmark](proof/phase-4/bench.json) |
| Cảnh báo và tương phản cao | Ba cảnh báo hiện bằng chữ, cài đặt còn sau tải lại | [UI](proof/phase-4/ui.json) |
| Bản giải nén | Test, một ngày headless và soak chạy thành công | [verification](proof/phase-4/verification.json) |

Số đo trên Windows/Chromium headless của máy phát triển. Chưa đo trên máy chấm.
Soak dùng bot đứng yên chạy hết đồng hồ; test demo riêng kiểm phục vụ, thu tiền,
mua oxy và đóng Shop. Không coi kết quả này là đã vượt test ẩn.

## Tài liệu để đối chiếu

- Thành viên, module và thỏa thuận: [TEAM](../TEAM.md).
- Ma trận: [P1](verification/phase-1.md), [P2](verification/phase-2.md),
  [P3](verification/phase-3.md), [P4](verification/phase-4.md).
- Quyết định thay đổi: [ADR P2](adr/0002-phase2-v11.md),
  [ADR P3](adr/0003-phase3-ticket-03.md), [ADR P4](adr/0004-phase4-release.md).
- [Nhật ký AI](ai-usage-log.md), [làm rõ](clarify.md), [retro](retro.md),
  [standup](standup.md), [hồ sơ Cường](members/lekhanhcuongvk1.md).
- [README](../README.md), [CHANGELOG](../CHANGELOG.md), [CREDITS](../CREDITS.md),
  [LICENSE](../LICENSE), [release notes và demo](release-v1.0.0.md).

## Đóng góp có thể kiểm qua Git

Trong khoảng `f0a1906..2d596ae`, lịch sử có Quang 3 commit, Phan Anh 3 commit,
Mạnh 4 commit và Cường 5 commit. Đây là số đếm theo tác giả Git, không dùng để
khẳng định mỗi commit đã được GitHub liên kết đúng tài khoản hoặc thay cho đánh giá
chất lượng. Nhóm cần kiểm email tài khoản trước khi nộp.

Phần Cường được chia thành năm commit theo chức năng; link nội bộ và phạm vi nằm
trong [kế hoạch P4](plan/phase-4.md). Các báo cáo trước giữ nguyên kết quả lịch sử,
không đổi thành số test của bản cuối.

## Checklist trước khi gửi giảng viên

- [x] Có mã, bộ test, bằng chứng P4, README và gói ZIP/checksum tại `dist/`.
- [x] Có nhật ký AI, retro và hồ sơ cá nhân đủ bốn tệp trong repo.
- [ ] Mỗi thành viên đọc lại phản tư và xác nhận đúng phần việc của mình.
- [x] Nhóm đã thảo luận phân công và thống nhất thỏa thuận trong TEAM.
- [ ] Người trong nhóm review mã và bằng chứng của nhánh cuonglk trước khi đẩy.
- [ ] Push nhánh, tích hợp main, chạy lại kiểm chứng và đóng gói từ commit main.
- [ ] Kiểm repo public, collaborator, GitHub nhận đúng tác giả và tag các phase.
- [ ] Tag phase-4 và v1.0.0 cùng commit main; Release đính ZIP/checksum.
- [ ] Chạy thử gói trên macOS/Linux hoặc ghi rõ chưa kiểm.
- [ ] Demo trực tiếp hoặc video .mp4 dưới 5 phút theo checklist Ticket-04.

Checklist này theo dõi thao tác phát hành ngoài phần code và báo cáo. Khi đẩy
nhánh xong, Integrator tiếp tục tích hợp main, gắn tag và kiểm Release có gói tải
về. Thời điểm bàn giao đối chiếu theo lịch sử GitHub.
