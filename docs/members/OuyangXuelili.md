# Trần Văn Quang — 2A202604032 — OuyangXuelili

Bản ghi kỹ thuật của phần đã thực hiện; review chéo cần cập nhật khi diễn ra.

- Đã làm: [nhóm và hợp đồng tích hợp](https://github.com/OuyangXuelili/K5-L3B-LAB-Day12-AI-SDLC-ABC/commit/6be0188ee360ecce49314096d6fed4d5919d4f79); [luật gather và test](https://github.com/OuyangXuelili/K5-L3B-LAB-Day12-AI-SDLC-ABC/commit/17c77608c8c8cdb42e9bf5ee25a751868953acba); [công cụ kiểm chứng và bằng chứng](https://github.com/OuyangXuelili/K5-L3B-LAB-Day12-AI-SDLC-ABC/commits/main/tools/verify_phase1.py).
- Review: chưa có bằng chứng review chéo của thành viên; không tính test tự động là review con người.
- AI sai: phiên chưa đăng nhập khiến kết luận PRD chưa có. Đọc lại bản chính thức phát hiện payload event khác đề; đã sửa và thêm test. Lượt test đầu còn gọi nhầm alias `python3` Windows Store; helper chuyển sang Python đang chạy.
- Kiểm chứng: 64/64 test đạt; hái thật → cập bến → xuất kho → quán đọc đúng. Replay cùng seed/input giống từng byte. Bằng chứng tại `docs/proof/phase-1/verification.json`.
- Điểm rút ra từ kiểm thử: test biên thời gian phải kiểm cả tick chạm 0, tick ngạt và tick cuối; test xanh chưa đủ nếu chưa đối chiếu schema event với PRD. Tuning và schema kho giữ nguyên.
- Bàn giao: gather/kho sẵn sàng tích hợp. Quán/UI, hoạt động nhóm và hạn tag cần xác nhận sau khi thực hiện.
