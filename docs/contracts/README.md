# Hợp đồng tích hợp (nên chốt sớm; hình thức do nhóm chọn)

Điền trong 15 phút kickoff (hoặc thay bằng một mục trong README / một bảng trên giấy, miễn cả nhóm cùng thống nhất):
1. **Schema file kho** — khớp mục G của PRD-0 (kho ghi khi `gather_end`) + một file kho mẫu hợp lệ: `inventory.sample.json`.
2. **Giao diện giữa `sim/*` và `client/ui`** — trạng thái nào UI được đọc, lệnh nào UI gửi vào.
3. **Danh sách sự kiện** — tên, `data`, ai phát, ai nghe (gather: `gather`, `node_regrown`, `hold_full`, `fish_caught`, `gather_end`...; quan: theo mục E của PRD-0).

Khi đổi hợp đồng sau này: báo cả nhóm và ghi lại lý do (ADR hoặc ghi chú, tùy chọn).

## Bản bàn giao phần Quang — Phase 1

Trạng thái: phần gather/kho đã đối chiếu PRD-0 / Test Contract v1.0 mục D–G trên lab board; các thành viên nhận tích hợp cần đọc và xác nhận.
Giữ nguyên schema, tuning, tên chế độ và nút bấm có sẵn. Chỉ cập nhật tên nhóm
trong `game.contract.json`; kết quả làm rõ nguồn ghi tại `docs/clarify.md`.

### Kho sáng → tối

```json
{"items":{"bong_sung":2,"ca_loc":1}}
```

- Một khóa gốc `items`; id hợp lệ: `ca_loc`, `ca_linh`, `bong_dien_dien`, `bong_sung`.
- Số lượng là số nguyên không âm; không nhận boolean, id lạ hay khóa gốc thừa.
- Khi ghi, bỏ mục bằng 0 và sắp id; dùng hàm ghi nguyên tử của starter.
- `gather_end` vì `docked`/`time`: xuất toàn bộ giỏ. `fainted`: giỏ rỗng.
- Hết `--ticks` trước `gather_end` thì không ghi đè kho; `quan --inventory` đọc
  file này. Không truyền đồng thời `--inventory` và `quan.stock` trong scenario.
- Kiểm tra: `python tools/check_inventory.py docs/contracts/inventory.sample.json`.

### Mô phỏng → UI

- UI gửi `move: [x,d]`, `interact`, `catch`; hành động chỉ phát ở cạnh lên của nút.
- `d` tăng khi lặn xuống. UI đọc `player.oxygen_ticks`, `oxygen_max_ticks`, `hp`,
  `hp_max`, `at_surface`, `catch_cd_ticks`, `hold`, `hold_count`, `hold_capacity`,
  `nodes`, `fish` trong snapshot. Giỏ giữ thứ tự nhặt, phần tử cuối là mới nhất.
- UI không tính lại luật. Cửa sổ thử và headless dùng cùng `GatherSim`.
- Entity gần nhất trong bán kính được chọn trước; khoảng cách bằng nhau dùng
  thứ tự id số của starter (`N2` trước `N10`).

### Event gather hiện dùng

Tên và payload event dưới đây theo mục E của PRD-0. Code và test dùng cùng giao diện;
[ADR 0001](../adr/0001-phase1-gather.md) ghi việc sửa payload từ bản làm trước khi đọc PRD.

| Event | `data` | Bên phát / bên dùng |
|---|---|---|
| `dive`, `surface` | `pos` sau di chuyển | gather → UI/test |
| `oxygen_empty` | `oxygen_ticks: 0` | gather → UI/test |
| `choke` | `hp` | gather → UI/test |
| `faint` | `cause: "choke"`, `lost` theo LIFO, `hp: 0` | gather → UI/test |
| `gather` | `node_id`, `kind`, `amount` | gather → UI/test |
| `node_regrown` | `node_id` | gather → UI/test |
| `fish_caught` | `fish_id`, `kind`, `yield` | gather → UI/test |
| `hold_full` | `action` (`gather`/`catch`), `node_id` hoặc `fish_id`, `required`, `free` | gather → UI/test |
| `gather_end` | `reason`, `inventory: {items: ...}` | gather → runner/kho/test |

Thứ tự một bước: giảm bộ đếm/mọc lại → di chuyển → chuyển vùng/oxy/ngạt/ngất →
interact (bến trước hái) → bắt cá → hết giờ. Ngất hoặc cập bến kết thúc bước ngay.

### Phần chờ tích hợp

Phan Anh triển khai khách/bếp/phục vụ ở `sim/quan.py`; Mạnh hoàn thiện UI; Cường
kiểm thử toàn phase. Việc quán đọc đúng kho đã được kiểm chứng, còn vòng chơi
quán hoàn chỉnh và DoD của toàn Phase 1 còn cần kiểm chứng sau khi tích hợp.
