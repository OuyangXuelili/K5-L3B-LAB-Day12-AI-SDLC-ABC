# Hợp đồng tích hợp (nên chốt sớm; hình thức do nhóm chọn)

## Cập nhật Phase 2 theo Ticket-02 / v1.1

Phần này thay các mô tả P1 bên dưới nếu có khác biệt. [ADR 0002](../adr/0002-phase2-v11.md)
ghi tác động contract và lý do sửa khung; đây là thông tin bàn giao, chưa khẳng định đã họp nhóm.

- Kho giữ cấu trúc `{items:{kind:count}}`; nhận thêm `ca_keo`, `keo_neo`.
  Mẫu mới: `inventory.phase2.sample.json`; mẫu P1 vẫn hợp lệ.
- CLI thêm `day --days 1..5` (mặc định 1), tự chuyển kho trong bộ nhớ.
  Hai cờ file kho chỉ dùng với gather/quan độc lập như P1.
- Input boolean v1.1: `interact`, `catch`, `pause`, `shop_done`, `attack`, `photo`;
  các nút mở rộng chưa bật được bỏ qua. Tất cả chỉ phát ở cạnh lên, giữ qua pha
  không sinh cạnh mới. `buy` là chuỗi chỉ có hiệu lực tại frame chứa nó.
- Session xét pause trước; lúc pause chỉ tăng tick ngoài, không tăng sim_tick/phase_tick,
  không xử lý buy/hành động. Resume chạy mô phỏng ngay trong bước đó.
- Day snapshot có `day`, `day_plan`, `upgrades`, `active_upgrades`; `phase` là
  gather/quan/shop. Event kết thúc thuộc pha/ngày cũ; snapshot đổi pha bắt buộc
  có pha mới và phase_tick=0 dù không trúng snapshot-every. `end.days_completed`
  chỉ tăng khi Shop đóng, kể cả ngày cuối.
- Live dùng `/input` thêm các điều khiển trình bày `continue`, `menu`;
  đây không phải trường input của headless. Menu/intro/kết quả không chạy gameplay.

### Quán: định dạng hiện triển khai, chờ PO đối chiếu PRD-0

Ticket-02 nhắc lại luật nhưng không liệt kê lại toàn bộ fixture/event quán v1.0.
Các tên/payload sau là giao diện trong bản triển khai này, chưa khẳng định đã đối chiếu hết nguồn v1.0.

- Customer: `id`, `table_id`, `order_id` (mặc định id khách), `dish_id`, `state`
  waiting/eating, `order_status` reserved/assigned/unfulfillable, `order_tick`,
  `patience_ticks_left`; eating cần `eat_ticks_left`, `price`, `tip`.
- `reserved` suy ra từ recipe khi đơn reserved; tổng giữ không được vượt `stock`.
  `available_stock` = stock trừ tổng giữ. Bắt đầu nấu mới trừ stock và bỏ phần giữ.
- Món trên tay/bếp: `{order_id,dish_id}`. Đơn waiting/assigned phải có đúng một món
  ở một bếp hoặc trên tay; eating không còn món mang đi. Bếp có
  state idle/cooking/ready, cook_ticks_left và ready_ticks.
- Khách hết kiên nhẫn: giải phóng phần giữ hoặc hủy món đã nấu, trừ uy tín khi còn giờ.
  Hết ca: khách eating trả ngay, waiting rời không phạt; dọn bếp/tay/giữ chỗ.

| Event quán hiện dùng | Payload |
|---|---|
| customer_arrived | customer_id, table_id, order_id, dish_id, order_tick |
| no_dish | table_id |
| cook_started / dish_ready / dish_picked | stove_id, order_id, dish_id |
| served | customer_id, table_id, order_id, dish_id, price, tip |
| paid | customer_id, table_id, order_id, dish_id, price, tip, amount, money, reputation |
| customer_left | customer_id, table_id, order_id, reason (patience/closing), reputation |
| quan_end | reason:time, money, earned, shift_earned, reputation |

Event mới theo Ticket-02: `monster_hit {monster_id,hp,lost,pos}`,
`fish_spawned {id,kind,pos}`, `faint` thêm cause:monster;
`day_start {}`, `day_plan {dishes,ingredients}`, `phase_start {}`,
`paused/resumed {}`, `bought {upgrade,level,price,money}`,
`buy_failed {action,reason}`, `shop_end {reason:done|time}`.
Event ở mode day có thêm `day` ở vỏ; lost giữ LIFO. Số liệu trong manifest.

Các phần dưới đây là lịch sử bàn giao P1, không phải trạng thái hiện tại của quán.

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
