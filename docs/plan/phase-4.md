# Phase 4 — QA và bàn giao cuối

Đầu mối: Lê Khánh Cường. Nhánh triển khai `cuonglk` lấy từ main `0fc8217`.
Phạm vi là Ticket-04, contract v1.3; giữ luật và schema cá thể v1.2.

| Việc | Kết quả triển khai | Commit |
|---|---|---|
| Rà khả năng chạy nhiều ngày, phiên bản kho | Lặp kế hoạch D1–D5, hỗ trợ kho v1.3, soak dùng Session thật | 7d001ad |
| Đo render và thêm hồi quy | Chromium 1280×720, FPS/1% low/load, kiểm ID và nâng cấp xuyên ngày | 1293abc |
| Cảnh báo và tương phản cao | Ba cảnh báo bằng chữ, cài đặt lưu được, kiểm bằng ảnh | a4f19da |
| Gói bàn giao | ZIP/SHA-256, kiểm bản giải nén, ADR quyết định kỹ thuật | d55219d |
| Hồ sơ và demo | Ma trận, báo cáo, phản tư, fixture demo và workflow release | 2d596ae |

Thứ tự thực hiện: kiểm baseline → sửa khả năng chạy v1.3 → đo render → kiểm UI
→ chạy hồi quy/bản giải nén → chốt bằng chứng. Đây là trình tự công việc đã làm,
không phải nhật ký chứng minh hoàn thành trong 30 phút của lớp.

Rủi ro còn lại: máy chấm khác máy phát triển; giấy phép starter chưa rõ; cần
review nhóm và chạy main trước khi tag. Không nhận thực hiện review thay thành viên.
