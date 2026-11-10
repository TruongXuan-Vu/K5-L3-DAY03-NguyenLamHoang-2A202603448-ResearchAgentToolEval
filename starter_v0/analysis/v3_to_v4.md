# v4-tools — Thêm tool lọc nguồn trùng

Giả thuyết: một tool local rõ nhiệm vụ giúp xử lý yêu cầu loại nguồn trùng mà không cần tìm web hay nhờ model tự so sánh URL bằng suy đoán.

Thay đổi: thêm `tools/deduplicate/tool.py`, `TOOL.md`, đăng ký trong `tools/__init__.py`, thêm một declaration trong `artifacts/tools.yaml`. Giữ prompt và các declaration v3 hiện có. Snapshots trước/sau được giữ riêng.

## Bằng chứng

- Base: `runs/v4-tools_B_base_openrouter_20261110T155521666806.json`, 19/20 (95%), routing 100%, arguments 95%, multi-turn 100%. R11 FAIL vì model bỏ `response_type=text`, dù chọn đúng clarify. M06 PASS trong run này.
- Group: `runs/v4-tools_B_group_openrouter_20261110T155319890960.json`, 8/10, routing 100%, arguments 80%, multi-turn 80%. G01 thiếu `response_type=text`; G06 dùng `topic=general` thay vì `news`. Giữ nguyên kỳ vọng, không sửa case để tăng điểm.
- Tool mới route đúng ở G02/G09. Scorer hiện không so nested items array ở hai case này; unit tests kiểm tra dữ liệu vào và kết quả lọc.
- Unit: `analysis/tool_tests.txt`, 90 pass, 0 fail, 0 skip cho contract/examples/tool tests; không chạy UI tests. Tool mới có 9 trường hợp test, gồm parametrization.
- CLI thật qua OpenRouter: `transcripts/v4-tools_openrouter_20261110T155506079575.transcript.json`, 3 lượt được chuẩn bị sẵn. Lượt 1 hỏi lại bằng text; lượt 2 gọi deduplicate, còn 2/3 nguồn; lượt 3 gọi format. Không nhầm hỏi bằng text với gọi clarify trong đánh giá routing.

Không diễn giải điểm 95% base và 80% group như điểm trước/sau: đây là hai bộ case khác nhau. Không có provider error trong hai run. Lỗi API của các tool nghiên cứu được ghi riêng trong report; routing PASS không đồng nghĩa tool lấy dữ liệu thành công.

UI giữ local theo lựa chọn người dùng, không tạo tunnel/public URL. Helper `scripts/run_submission_checks.py` không cho gửi Telegram trong các lần eval/demo. Tool mới không cần API key.
