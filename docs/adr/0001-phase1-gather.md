# ADR 0001 — Luật thu thập đang áp dụng trong phần Quang

- Ngày: 21/11/2026.
- Trạng thái: đã đối chiếu PRD-0 và cập nhật code/test.
- Phạm vi: `GatherSim`, kho và dữ liệu event bàn giao cho quán/UI.
- Căn cứ: [PRD-0 / Test Contract v1.0, mục D–G](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-1), đọc sau khi đăng nhập Claude.

## Quyết định

1. Mỗi lượt hái/bắt nhận trọn yield. Nếu thiếu chỗ, phát `hold_full`, giữ nguồn
   nguyên liệu và không tiêu hồi chiêu. Khi đàn gần nhất không vừa giỏ, không thử
   đàn khác. Đây là quy định F/Gather bước 3–4.
2. Tick có oxy cuối bước bằng 0 được tính vào bộ đếm ngạt nếu còn dưới nước.
   Lên mặt nước đặt bộ đếm về 0; khoảng ngạt đọc từ tuning. Khớp F/Gather bước 2.
3. Thay payload bản làm trước khi đọc PRD bằng đúng mục E: `amount` cho hái,
   `yield` cho cá, trường action/nguồn/required/free cho giỏ đầy; ngất ghi cause,
   hp và danh sách `lost` theo LIFO. Chi tiết ở `docs/contracts/README.md`.
4. Bỏ `invuln_ticks` của phase sau khỏi fixture/snapshot gather Phase 1; từ chối
   trường lạ trong nút/cá, số không hữu hạn và tick rate khác 60. ID dùng hậu tố
   chữ số ASCII. Các sửa khung đều nhằm đáp ứng Test Contract A/D.

## Bằng chứng

- Code đang thực hiện các quyết định trong `chonoi/sim/gather.py`.
- `tests/test_gather_rules.py` kiểm thiếu chỗ, chuyển oxy về 0, ngạt, hồi chiêu,
  thứ tự event và kho xuất từ thao tác hái thực.
- `docs/proof/phase-1/verification.json` được sinh bởi
  `python tools/verify_phase1.py`; xem số test và kết quả probe/replay trong file sinh tự động.

## Phạm vi bàn giao

Luật gather/kho đã có nguồn đối chiếu. ADR không thay cho review con người,
không xác nhận hoạt động nhóm hoặc thời hạn tag. Luật quán/UI và DoD của cả
Phase 1 cần được các thành viên phụ trách tích hợp, kiểm chứng riêng.
