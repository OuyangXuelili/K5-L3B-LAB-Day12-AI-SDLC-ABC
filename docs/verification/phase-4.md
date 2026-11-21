# Bàn giao Phase 4 — Cường

Nhánh làm việc: `cuonglk`, bắt đầu từ main `0fc8217`. Bản này dùng contract 1.3,
giữ luật và kho cá thể của Phase 3. Kết quả chạy được lưu trong
[verification.json](../proof/phase-4/verification.json); SHA-256 nguồn trong file
cho phép đối chiếu đúng mã đã kiểm tra bằng `tools.verify_phase4.source_digest`.

| Tiêu chí | Cách kiểm | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P4-01: manifest và benchmark | Chạy seed 42, 30 giây, Chromium 1280×720 | [bench.json](../proof/phase-4/bench.json) | Đạt cấu trúc; avg 60,0025 FPS, 1% low 59,5238 FPS, load 1813,87 ms |
| AC-P4-02: soak | Chạy seed 7, 10 ngày hai lần; bỏ duration_s khi so | [soak.json](../proof/phase-4/soak.json), [replay](../proof/phase-4/soak-replay.json) | Đạt: days_completed=10, crashes=0; gameplay giống nhau |
| AC-P4-03: cảnh báo và tương phản | Dựng ca oxy thấp/quái gần và khách còn ít kiên nhẫn; bật rồi tải lại | [ui.json](../proof/phase-4/ui.json), [sáng](../proof/phase-4/gather-contrast.png), [tối](../proof/phase-4/quan-contrast.png) | Ba cảnh báo có chữ; cài đặt còn sau tải lại |
| AC-P4-04: hồi quy | Chạy toàn bộ unittest cả trong repo và ZIP đã giải nén | [verification.json](../proof/phase-4/verification.json) | Đạt: 115 test; các lệnh kiểm chứng trả mã 0 |
| AC-P4-05: đóng gói | Tạo ZIP, giải nén thư mục mới, chạy test, day và soak | [công cụ đóng gói](../../tools/package_release.py), verification.json | Gói mã nguồn cần Python 3.10+, không kèm runtime |
| AC-P4-06: báo cáo | Rà README, CHANGELOG, credits, license, retro và hồ sơ | [retro](../retro.md), [cá nhân](../members/lekhanhcuongvk1.md) | Đã hoàn thiện hồ sơ; nội dung thảo luận và thống nhất nhóm theo xác nhận của thành viên |
| AC-P4-07: phát hành | phase-4 và v1.0.0 cùng commit main, kèm ZIP | [release notes](../release-v1.0.0.md) | Chờ tích hợp main và công bố trên GitHub |
| AC-P4-08: demo | Chơi gather → quan → đóng Shop, chạy test và mở ma trận | [kịch bản](../release-v1.0.0.md) | Đã chuẩn bị kịch bản; chưa ghi nhận buổi demo |

Các mã AC trên là mã truy vết nội bộ theo DoD của Ticket-04. Không nhận là mã
test ẩn của lớp. Số đo hiện tại ở Windows/Chromium headless; chưa có phép đo
trên máy chấm hoặc clone sạch macOS/Linux. Gói ZIP đã được kiểm ở thư mục tạm.

Soak cho bot đứng yên chạy hết đồng hồ từng pha. Nó kiểm vòng đời, không chứng minh
khả năng chơi hay bán hàng; test riêng kiểm hàng, ID, tiền và nâng cấp xuyên 10 ngày.
115 test gồm 111 test kế thừa và 4 ca mới. Ca demo đi qua cập bến, nấu, bưng,
phục vụ, thu tiền, mua oxy và đóng Shop trên cùng Session. Không đổi kỳ vọng P1–P3 cho xanh.

Chạy lại: `python tools/verify_phase4.py`. Cần cài phụ thuộc benchmark theo README.
Thời điểm nộp và bước review đối chiếu theo lịch sử GitHub khi nhóm công bố bản cuối.
