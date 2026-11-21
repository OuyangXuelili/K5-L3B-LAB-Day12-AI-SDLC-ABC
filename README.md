# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Nhóm ABC — Phan Anh, Phase 2 / Ticket-02

Đã tích hợp contract v1.1: quán có 2 bếp, 4 bàn, 6 món; khách giữ nguyên liệu,
nấu/bưng/phục vụ/thu tiền và uy tín. Vòng ngày nối lặn → quán → Shop, kế hoạch
5 ngày, nâng bình oxy/áo phao từ ngày sau, pause, cá bơi/sinh và cá sấu.
Giao diện có menu, giới thiệu, kết quả và HUD. Chỉ cần Python 3, không thêm dependency.

```powershell
python tools/verify_phase2.py
python -m chonoi.live --mode day --days 5
```

Mở địa chỉ terminal in ra, chọn **Chơi**. WASD/mũi tên di chuyển, **E** hái/cập bến/
nấu/bưng/phục vụ, **Space** bắt cá, **P/Esc** pause, **R** chơi lại.
Shop dùng nút mua và **Xong**. E/Space cần nhả rồi bấm lại.
Ở quán, E tại bếp lấy đơn chờ cũ nhất; món chín thì E bưng, mang đến đúng bàn rồi E giao.
Tiền là nghìn đồng; điểm = earned + 100 × floor(reputation). Mua nâng cấp chỉ giảm money.

Demo rút ngắn **có tiền/kho dựng sẵn**, không phải bằng chứng hái thật:

```powershell
python -m chonoi.live --mode day --days 2 --scenario docs/scenarios/phase-2-demo.json
python -m chonoi.headless --mode day --days 1 --seed 7 --ticks 22200 --out out.jsonl
python tools/check_inventory.py docs/contracts/inventory.phase2.sample.json
```

Chế độ độc lập vẫn hỗ trợ gather xuất kho và quan nạp kho theo lệnh bên dưới.
`day` tự chuyển kho trong bộ nhớ, không nhận cờ file kho. macOS/Linux dùng `python3` nếu cần.

Tài liệu hiện tại: [bàn giao Phase 2](docs/verification/phase-2.md),
[JSON kiểm chứng](docs/proof/phase-2/verification.json),
[ADR 0002](docs/adr/0002-phase2-v11.md),
[hồ sơ Phan Anh](docs/members/alpha19102004.md).
Chưa có review chéo, đối chiếu đầy đủ payload quán PRD-0, QA hình ảnh/FPS hoặc push tag.
Không coi test do nhóm viết là kết quả test ẩn hay bằng chứng nộp đúng giờ.
Codex hỗ trợ tích hợp phần phụ thuộc, không ghi thay đóng góp của Quang/Mạnh/Cường.

## Lịch sử bàn giao phần Quang, Phase 1

Phần này giữ mô tả từ baseline P1; trạng thái quán hiện tại theo mục Phase 2 ở trên.

Phân công và GitHub handle ở [TEAM.md](TEAM.md). Đợt này hoàn thiện luật
lặn/thu thập trong `sim/gather`: oxy, ngạt, ngất, hái/mọc lại, bắt cá/hồi chiêu,
sức chứa và thứ tự giỏ. Kho xuất từ lượt hái thật đã có probe nạp vào quán.
Các quyết định đang áp dụng ở [ADR 0001](docs/adr/0001-phase1-gather.md);
kết quả đối chiếu PRD-0 và phần chờ tích hợp ở [docs/clarify.md](docs/clarify.md).

Chỉ cần Python 3, không cài dependency hay API key:

```powershell
python tools/verify_phase1.py
python tools/check_inventory.py docs/contracts/inventory.sample.json
python -m chonoi.live --mode gather
```

`verify_phase1.py` chạy test, kiểm TEAM/kho và tạo
`docs/proof/phase-1/verification.json` từ thực thi. Cùng seed/input phải sinh
JSONL và kho giống từng byte. Bộ test hộp đen giữ nguyên; helper trên Windows
dùng Python đang chạy để tránh alias `python3` của Windows Store.

Phần Quang đã đối chiếu PRD-0 / Test Contract v1.0, mục D–G tại
[tab Phase 1](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-1), sau khi
đăng nhập Claude. Luật khách/bếp/phục vụ do Phan Anh phụ trách, UI do Mạnh và
QA toàn phase do Cường; toàn Phase 1 còn cần tích hợp các phần này. Thỏa thuận nhóm,
review con người và tag chỉ ghi hoàn tất sau khi thực sự diễn ra.
Các commit phần Quang được dẫn trong [hồ sơ cá nhân](docs/members/OuyangXuelili.md).

Từ clone sạch trên macOS/Linux, chạy trong 3 lệnh:

```bash
git clone https://github.com/OuyangXuelili/K5-L3B-LAB-Day12-AI-SDLC-ABC.git && cd K5-L3B-LAB-Day12-AI-SDLC-ABC
python3 tools/verify_phase1.py
python3 -m chonoi.live --mode gather
```

WASD/mũi tên để bơi/đi, E để hái/cập bến/tương tác, Space để bắt cá, R chơi lại.
Điểm theo preset là `earned + 100 × floor(reputation)`; tiền tính bằng nghìn đồng.
Chế độ quán mở bằng `python3 -m chonoi.live --mode quan --inventory kho.json` khi
đã có file kho từ lượt gather kết thúc; luật quán hiện vẫn là phần cần tích hợp.

Hợp đồng kho/UI/event tại [docs/contracts/README.md](docs/contracts/README.md).
Test `test_template_is_rejected` dùng fixture mẫu riêng để không coi `TEAM.md`
đã điền là dữ liệu lỗi; không thay điều kiện kiểm tính hợp lệ của thành viên.

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Bắt đầu nhanh

```bash
git clone <fork-của-nhóm> && cd <fork-của-nhóm>
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v        # smoke test
python3 -m chonoi.live --mode gather                                # chơi thử trên trình duyệt (tùy chọn)
```

Game cần chế độ **headless** theo Test Contract (`python3 -m chonoi.headless --mode gather|quan …`) để được chạy và chấm tự động. **Công nghệ không ràng buộc**: khung Python trong `chonoi/` chỉ là gợi ý, chi tiết ở [`docs/STARTER.md`](docs/STARTER.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.
