# Phân tích v0 và giả thuyết v1

## Bằng chứng baseline

Cả ba run v0 trong `runs/` đều dùng `openai/gpt-4o-mini`, cùng prompt/tools hash, đạt 14/20 case (70%), routing 75%, arguments 70%, multi-turn 100%, không có provider error.

Chọn run gần nhất làm mốc so sánh: `runs/v0_B_base_openrouter_20261110T105954975593.json`.

| Case FAIL | Hành vi thực tế v0 | Hành vi cần có | Nguyên nhân / hướng sửa |
| --- | --- | --- | --- |
| R08_out_of_scope | Gọi `send` để trả lời bài toán tích phân | Không gọi tool; định hướng về phạm vi research | Prompt chưa giới hạn phạm vi, mô tả `send` mơ hồ. Dành cho vòng tiếp theo. |
| R10_missing_handle | Tự chọn `timeline(screenname="sama")` dù user chưa nói tài khoản | `clarify(response_type="text")` hỏi tài khoản | Prompt yêu cầu đoán và chỉ đích danh một tài khoản để đoán. Sửa trong v1. |
| R11_missing_url | Bịa `fetch(url="https://example.com/article")` | `clarify(response_type="text")` xin URL hoặc nội dung | Prompt yêu cầu tự đoán URL khi user nói "bài này". Sửa trong v1. |
| R12_confirm_before_send | Gọi `send` ngay; tool trả `needs_confirmation` | `clarify(response_type="yes_no")` trước khi gửi | Prompt yêu cầu gửi ngay; cần sửa ranh giới xác nhận ở vòng tiếp theo. Log này không chứng minh đã gửi thành công. |
| R13_parallel_web_and_tweets | Gọi đủ `lookup` và `social_search`, nhưng thiếu `topic="news"`; hai run đầu còn thêm `news` vào query | Giữ từ khóa chủ đề, truyền rõ `topic="news"`, `timeframe="day"` | Mô tả arguments thiếu convention. Dành cho vòng tiếp theo. Case có nhãn `wrong_tool` nhưng mismatch thực tế là `wrong_arg_value`. |
| R14_out_of_scope_coding | Gọi `send` để trả lời bài Python | Không gọi tool; định hướng về phạm vi research | Cùng nhóm nguyên nhân với R08. Dành cho vòng tiếp theo. |

## Thay đổi v1

Giả thuyết duy nhất: chỉ dẫn tự đoán dữ liệu bắt buộc khiến agent gọi research tool thay vì hỏi lại. Thay đoạn chỉ dẫn đó bằng quy tắc kiểm tra dữ liệu trong hội thoại, gọi `clarify` nếu thiếu, không bịa account/URL, và dùng câu trả lời hoặc chỉnh sửa mới nhất khi user đã bổ sung.

Chỉ thay một đoạn trong `artifacts/system_prompt.md`. Giữ nguyên `tools.yaml`, code agent và bộ eval. Hai case mục tiêu: R10 và R11. Theo dõi M01 và M04 để bảo đảm agent tiếp tục làm việc khi đã nhận dữ liệu bổ sung. Nếu chỉ hai case mục tiêu được sửa và các case khác giữ nguyên, dự kiến đạt 16/20; đây là dự đoán, chưa phải kết quả đo.

Chạy so sánh trên cùng model:

```powershell
python run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v1 --suite base --eval-cases data/eval_base.json
```

## Phân biệt lỗi model và lỗi tool

- Các log v0 báo `Missing RAPIDAPI_KEY env var` khi chạy tool mạng xã hội. Cấu hình hiện tại cũng chưa có key này. Cần bổ sung key riêng trong `.env`, không commit key.
- Một số lần gọi Firecrawl bị `ConnectTimeout`.
- Base eval chấm routing và arguments; case PASS không chứng minh tool lấy dữ liệu thành công. Không sửa prompt để che lỗi cấu hình hoặc timeout.

## Kiểm tra

`python -m pytest -q tests/test_tool_contract.py tests/test_tools_examples.py`: 62 passed.

## Kết quả thử chạy live v1

Run: `runs/v1_B_base_openrouter_20261110T111415882369.json`.

- Prompt hash bắt đầu bằng `f3fac79d3486` (xem hash đầy đủ trong run JSON và version log).
- Tools hash giữ nguyên so với v0.
- Cả 20 case gặp `APIConnectionError: Connection error.`; `measured_cases=0`, `provider_error_cases=20`.
- Chưa có dữ liệu để kết luận v1 cải thiện hay hồi quy. Giá trị `case_accuracy=0.0` do chương trình xuất trong run này không phải phép đo chất lượng model hợp lệ.
- Lần kiểm tra kết nối OpenRouter ngoài sandbox bị hệ thống duyệt tự động từ chối vì chưa có sự cho phép rõ ràng gửi tool declarations đến endpoint OpenRouter. Không thực hiện cách khác để vượt qua từ chối này.
- `artifacts/version_log.csv` đã ghi baseline và lần thử v1, với metric sau là unavailable thay vì ghi điểm dự đoán.

Cần được người dùng cho phép rõ ràng gửi prompt, tool declarations và câu hỏi eval đến OpenRouter để thử lại ngoài sandbox, hoặc người dùng tự chạy lệnh ở trên trong terminal có mạng. Sau khi có run hợp lệ mới cập nhật metric trước/sau và kết luận về R10/R11, M01/M04 cùng các case còn lại.

## Cập nhật: run v1 hợp lệ do người dùng chạy

Run `runs/v1_B_base_openrouter_20261110T111806972710.json` đã đo đủ 20 case, không có provider error, đạt 18/20 (90%). Routing và arguments đều 90%; multi-turn 83.33% (5/6), giảm từ 100% ở v0.

R10/R11 đã PASS, M01/M04 vẫn PASS: giả thuyết hỏi lại khi thiếu dữ liệu được hỗ trợ bởi lần chạy này. R08/R13/R14 cũng chuyển sang PASS dù không có thay đổi riêng cho những lỗi đó; không kết luận chúng đã được khắc phục ổn định chỉ từ một lần chạy. R08/R14 không gọi tool nhưng vẫn trả lời bài toán/code: PASS ở đây chỉ chứng minh tiêu chí không gọi tool, không chứng minh agent đã từ chối ngoài phạm vi.

Còn FAIL R12 (gọi `send` trước khi xác nhận) và M06 (gọi `social_search` dù user đã đổi sang web news). M06 là hồi quy so với v0, cần theo dõi và sửa trong vòng riêng.

Đã cập nhật version log bằng điểm thực đo. Bản prompt và tools của v1 được lưu tại `artifacts/snapshots/v1/`, kiểm tra hash khớp run hợp lệ trước khi sửa v2.
