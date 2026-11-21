# Ma trận truy vết phần Quang — Phase 1

Nguồn: [PRD-0 / Test Contract v1.0 trên Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-1),
đã đọc sau đăng nhập Claude. Bảng truy vết dùng mục của đề, không tự gán mã AC do giảng viên cấp.

| Yêu cầu PRD-0 | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| F/Gather 2: oxy, ngạt, nổi lên đúng tick ngạt | `GatherRules`: oxy, biên mặt nước, khoảng ngạt | [verification.json](../proof/phase-1/verification.json), mục `checks` | Đạt |
| Máu về 0 thì ngất, xóa giỏ, kết thúc một lần | Unit test và headless xuất kho rỗng | Cùng file bằng chứng; `test_faint_writes_empty_inventory_once` | Đạt |
| F/Gather 1,3: hái/mọc lại, chọn gần nhất, id khi hòa | `GatherRules`: nearest node, regrowth, full hold, input cạnh lên | Cùng file bằng chứng | Đạt |
| F/Gather 4: bắt trọn yield, hồi chiêu, không thử đàn khác khi đầy | `GatherRules`: catch, cooldown, capacity và thứ tự giỏ | Cùng file bằng chứng | Đạt |
| Bến được xét trước hái; giỏ giữ đúng khi cập bến/hết giờ | Test unit và smoke starter | Cùng file bằng chứng | Đạt |
| Kho từ lượt hái thật được quán đọc đúng | Probe CLI hái → cập bến → nạp quán | Mục `integration`: `bong_sung=1` ở cả kho và quán | Đạt |
| Cùng seed/input sinh JSONL và kho giống từng byte | Chạy probe hai lần, so bytes/SHA-256 | Mục `integration.replay_bytes_identical` và hai hash | Đạt |
| A/D: 60 Hz, số hữu hạn, fixture sai/trường lạ trả mã 2 trước khi ghi | Headless invalid-fixture và contract tests | Mục `checks`: test chạy thật, exit 0 | Đạt |
| E/F: đúng payload event, tick ngạt và mất giỏ LIFO | Payload assertions và headless event/tick test | Cùng file bằng chứng | Đạt |
| TEAM có 4 handle, khớp `team_size`; file kho mẫu hợp lệ | Hai command kiểm nhóm/kho | Mục `checks`: cả hai exit 0 | Đạt |
| PRD-0 F/Quán và DoD của toàn phase | Cần hoàn thiện quán/UI và kiểm chứng sau tích hợp | [clarify](../clarify.md) | Chưa hoàn tất |
| Khách/bếp/phục vụ và UI hoàn chỉnh | Chờ phần Phan Anh/Mạnh và QA của Cường | [phân công](../../TEAM.md) | Chưa xác nhận |
| Lịch sử đóng góp phần Quang | Ba commit tách theo nhóm/hợp đồng, luật/test, công cụ/bằng chứng | [Hồ sơ Quang](../members/OuyangXuelili.md) | Có lịch sử Git |
| Review thật, tag đúng giờ và thỏa thuận nhóm | Cần hoạt động thực tế và lịch lab | Chưa có | Chưa xác nhận |

## Đánh giá ngắn
- `python tools/verify_phase1.py` sinh JSON bằng chứng sau khi chạy test và probe,
  không chép kết quả hoặc chỉnh số đo bằng tay. Không gọi API LLM khi chạy game/test.
- Bộ test hộp đen `tests/test_smoke_p1.py` giữ nguyên. Helper chỉ sửa cách gọi
  Python/UTF-8 trên Windows vì alias `python3` ban đầu trả mã 9009. Test từ chối
  TEAM mẫu dùng fixture riêng, vẫn giữ việc từ chối handle/tên sai, trùng và sai số người.
- Tuning, schema kho, runner và luật quán giữ nguyên; `game.contract.json` chỉ đổi tên nhóm.
- Sửa khung có lý do: scenario từ chối trường/giá trị sai; ID chỉ dùng hậu tố ASCII;
  contract kiểm 60 Hz/số hữu hạn. Không đổi test hộp đen để hợp thức hóa luật sai.
- Phần gather/kho đã đối chiếu PRD-0 D–G. Tích hợp quán/UI, review thật và gắn tag
  theo lịch thực tế trước khi đánh dấu toàn Phase 1 hoàn tất.
