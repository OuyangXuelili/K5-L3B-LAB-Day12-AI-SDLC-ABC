# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Phase 2 / Ticket-02 v1.1: `python tools/verify_phase2.py` (test P1+P2, replay ngày/Shop, kho và benchmark; sinh `docs/proof/phase-2/verification.json`).
- Chơi vòng 5 ngày: `python -m chonoi.live --mode day --days 5`; headless: `python -m chonoi.headless --mode day --days 1 --seed 7 --ticks 22200 --out out.jsonl`.
- Kiểm tra phần Phase 1 trên Windows/Linux: `python tools/verify_phase1.py` (sinh bằng chứng tại `docs/proof/phase-1/verification.json`).
- Kiểm file kho: `python tools/check_inventory.py docs/contracts/inventory.sample.json` (mã 0 hợp lệ, 2 sai dữ liệu).
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Headless: `python3 -m chonoi.headless --mode gather|quan --seed 1 --ticks 600 --out out.jsonl`
- Chơi thử trên trình duyệt: `python3 -m chonoi.live --mode gather|quan` (mở địa chỉ in ra; WASD, E, Space, R)

## Cấu trúc & quy ước
- (Starter Python là TÙY CHỌN; nhóm có thể dùng ngôn ngữ khác nếu giữ Test Contract.) Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi của nhóm: `chonoi/sim/gather.py`, `chonoi/sim/quan.py` (tìm `TODO(nhóm)`).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase và hợp đồng kho trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- `verify_phase2`: chạy trước bàn giao phần Phan Anh; kiểm chứng đồng thời luật cũ và mới. `check_inventory` nay nhận đủ 6 id của Ticket-02; thử `python tools/check_inventory.py docs/contracts/inventory.phase2.sample.json`.
- V1.1 theo Ticket-02 người dùng cung cấp: đọc ADR 0002 trước tích hợp. Khung phải đổi để hỗ trợ day/pause/buy; event kết thúc giữ pha cũ, snapshot pha mới có phase_tick=0. Không dùng kết quả test tự viết để khẳng định đã qua test ẩn hoặc review con người.
- `verify_phase1`: chạy trước khi bàn giao phần Quang; test toàn repo, kiểm TEAM/kho, replay cùng seed và probe hái → cập bến → quán. Command của nhóm nằm ở `tools/verify_phase1.py`.
- `check_inventory`: chạy khi nhận/đổi file kho để phát hiện sai schema/id/số lượng; dùng `tools/check_inventory.py`.
- Nguồn Phase 1: PRD-0 / Test Contract v1.0 tại tab Phase 1 trên lab board (link trong README, cần đăng nhập Claude để đọc dữ liệu). Phần gather đã đối chiếu D–G; ADR 0001 ghi thay đổi khi đối chiếu. Không coi test gather đạt là toàn Phase 1 hoàn tất.
