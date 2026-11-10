# v2: hỏi xác nhận trước khi gửi

Mốc so sánh: `runs/v1_B_base_openrouter_20261110T111806972710.json`, model `openai/gpt-4o-mini`: 18/20 case, routing 90%, arguments 90%, multi-turn 83.33%, provider errors 0.

## Hai case còn fail trong v1

| Case | Thực tế | Mong đợi |
| --- | --- | --- |
| R12_confirm_before_send | `send(text="Bản tin này")`, tool trả `needs_confirmation` | Gọi `clarify(response_type="yes_no")` để hỏi trước khi gửi |
| M06_switch_tool | `social_search(query="OpenAI", search_type="Latest", limit=5)` | Gọi `lookup(query="OpenAI", topic="news")` vì user đã bỏ Twitter, chuyển sang web |

## Giả thuyết duy nhất và thay đổi

Prompt v1 vẫn yêu cầu gửi ngay khi user đề nghị gửi/post/publish. Chỉ thay đoạn này trong `artifacts/system_prompt.md` bằng quy tắc xác nhận: hỏi qua `clarify` dạng yes/no, chờ user duyệt ở lượt sau, chỉ gọi `send(confirmed=true)` khi biết nội dung và nơi gửi. Không dùng `send` để trả lời trong chat; nội dung hoặc nơi gửi thay đổi thì cần xác nhận lại. Quy tắc này ưu tiên hơn chỉ dẫn làm trong một bước.

Giữ nguyên code, `tools.yaml` và eval cases. M06 để vòng v3 kiểm chứng giả thuyết riêng về đổi nguồn giữa hội thoại.

## Đánh giá cần chạy

```powershell
python run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v2 --suite base --eval-cases data/eval_base.json
```

Mục tiêu: R12 PASS; R10/R11, M01/M04 tiếp tục PASS; theo dõi cả 20 case để phát hiện hồi quy. Nếu chỉ R12 được sửa và mọi case khác giữ nguyên thì dự kiến 19/20, đây không phải kết quả đo. Base eval không đủ chứng minh toàn bộ vòng đời xác nhận (duyệt, từ chối, đổi nội dung); cần kiểm tra bổ sung khi làm live chat/group eval.

## Kết quả thực đo v2

Người dùng đã chạy `runs/v2_B_base_openrouter_20261110T113058268871.json`. Model giống v1; tools hash giữ nguyên; prompt hash khớp bản v2. Đo đủ 20 case, không có provider error.

| Chỉ số | v1 | v2 |
| --- | --- | --- |
| Case đúng | 18/20 (90%) | 17/20 (85%) |
| Routing | 90% | 90% |
| Arguments | 90% | 85% |
| Multi-turn | 5/6 (83.33%) | 4/6 (66.67%) |

| Case thay đổi hoặc còn FAIL | v1 | v2 | Bằng chứng |
| --- | --- | --- | --- |
| R12_confirm_before_send | FAIL | PASS | Đã hỏi xác nhận qua `clarify`, đáp ứng kỳ vọng của case |
| R13_parallel_web_and_tweets | PASS | FAIL | Gọi đủ hai tool nhưng `lookup` thiếu `topic="news"` |
| M02_carryover_timeframe | PASS | FAIL | Chọn `social_search` cho tin robotics hôm nay; cần `lookup(query="robotics", topic="news", timeframe="day")` |
| M06_switch_tool | FAIL | FAIL | Vẫn gọi `social_search` sau khi user chuyển sang web; cần `lookup(query="OpenAI", topic="news")` |

Tổng cộng sửa được một case nhưng có hai hồi quy, nên số FAIL tăng từ 2 lên 3. Các case còn lại giữ trạng thái PASS. Giả thuyết xác nhận được hỗ trợ tại R12, nhưng giả định không ảnh hưởng các case khác không được hỗ trợ bởi run này. Không coi v2 là cải thiện tổng thể so với v1.

Prompt v2 vẫn có chỉ dẫn "Always finish ... single step. Pick one tool" và tool descriptions còn mơ hồ, chưa quy định rõ phân biệt web news với Twitter hay conventions `topic/timeframe`. Đây là các giả thuyết hợp lý cho lỗi còn lại, không phải nguyên nhân đã được chứng minh. Một cặp run không tách được ảnh hưởng thay prompt khỏi độ dao động của provider/model.

Theo README Step 2: "Chạy lại, so metric trước/sau. Nếu không cải thiện, đổi giả thuyết." Đã cập nhật version log bằng số đo thật, giữ nguyên log gốc và lưu artifacts v2 trong `artifacts/snapshots/v2/`. V1 là bản có điểm tổng cao nhất đã đo; không chọn v2 làm bản tốt nhất chỉ vì version lớn hơn. Giữ lại sửa xác nhận như một ứng viên có lợi về hành vi để đánh giá tiếp, không âm thầm bỏ yêu cầu xác nhận.

Giả thuyết cho vòng tiếp theo: mô tả `lookup` thiếu ranh giới web/news so với social search và thiếu convention args. Có thể chỉ sửa description của `lookup` để nói rõ dùng cho tin web, giữ chủ đề/khoảng thời gian qua các lượt, ưu tiên nguồn user vừa chuyển sang, truyền rõ `topic="news"` và `timeframe` khi được yêu cầu. Đây là một thay đổi riêng cần được chạy eval trước khi kết luận.

62 contract/example tests pass ở bước chuẩn bị v2 chỉ xác nhận code/schema và hành vi offline được test; chúng không xác nhận chất lượng chọn tool của model qua API.
