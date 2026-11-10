# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Chưa cung cấp
- Members: Chưa cung cấp
- Provider/model: OpenRouter / openai/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tìm tin trên web và X/Twitter, đọc nội dung từ URL, tìm tài liệu khoa học và trình bày thông tin thành bản tin có liên kết nguồn. Agent hỏi lại khi thiếu tài khoản hoặc URL; bản v2 bổ sung quy tắc hỏi xác nhận trước khi gửi nội dung lên Telegram.

**Dành cho:** người cần theo dõi tin AI/công nghệ, tổng hợp thông tin theo chủ đề và tra cứu nguồn để đọc sâu hơn.

**Link dùng thử (deploy):**

UI Streamlit đã được bổ sung tại `app.py`, hỗ trợ chat nhiều lượt, xem các lần gọi tool và tải transcript JSON. Chạy `python -m streamlit run app.py` trong thư mục `starter_v0`, sau khi cài `requirements.txt`, rồi mở **http://localhost:8501** trên máy chạy UI.

**Link demo local:** http://127.0.0.1:8501 — chỉ mở trên máy chạy UI. Theo lựa chọn của người dùng, không tạo link public. Hướng dẫn chạy và dùng thử: `UI-README.md`.

**Lưu ý khi dùng thử:** chức năng X/Twitter và gửi Telegram cần cấu hình dịch vụ tương ứng; log hiện tại còn báo thiếu key X/Twitter. Khả năng chọn tool và lấy dữ liệu thành công được kiểm tra riêng, nên điểm eval không đồng nghĩa mọi dịch vụ đã hoạt động đầy đủ.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi bổ sung thông tin hoặc xin xác nhận trước khi gửi. | Không |
| `timeline` | Lấy các bài đăng gần đây của một tài khoản X/Twitter. | Không |
| `social_search` | Tìm bài đăng X/Twitter theo từ khóa, ưu tiên mới nhất hoặc nổi bật. | Không |
| `lookup` | Tìm thông tin và tin tức trên web theo chủ đề, khoảng thời gian. | Không |
| `fetch` | Đọc nội dung một URL được cung cấp. | Không |
| `format` | Trình bày các mục thông tin đã có thành bản tin Markdown. | Không |
| `send` | Gửi nội dung lên Telegram khi được xác nhận. | Không |
| `policy` | Tra cứu các tài liệu chính sách nội bộ có sẵn. | Không |
| `papers` | Tìm bài báo khoa học trên arXiv. | Không |
| `deduplicate` | Lọc nguồn trùng URL, giữ bản đầu tiên; xử lý local, không cần API key. | Có |
| `paper_text` | Tải PDF arXiv và trích xuất nội dung văn bản. | Không |

Hiện có 11 tool: 10 tool starter và 1 tool mới của nhóm (`deduplicate`).

## A3. Câu hỏi mẫu để thử

1. **Tìm tin web:** "Tìm 5 tin về AI hôm nay trên web, kèm liên kết nguồn."
2. **Đọc bài viết:** "Đọc và tóm tắt bài viết tại https://www.anthropic.com/news/claude."
3. **Tool mới — lọc nguồn trùng:** `Lọc trùng các nguồn này, giữ bản đầu: [{"url":"https://example.org/ai?utm_source=demo"},{"url":"https://example.org/ai"}].`
4. **Thử hỏi lại:** "Tóm tắt 5 tweet mới nhất giúp mình." Khi agent hỏi tài khoản, trả lời: "Của @elonmusk nhé."
5. **Thử xác nhận gửi:** "Đăng bản tin này lên Telegram giúp mình: Ba chủ đề cần theo dõi hôm nay là AI, robotics và an toàn mô hình." Quan sát agent hỏi xác nhận; có thể trả lời "Không gửi" để kết thúc bước thử.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Các run dưới đây dùng cùng model `openai/gpt-4o-mini`, cùng base eval 20 case và không có provider error. Mỗi điểm là một lần đo; không coi đây là trung bình thống kê.

| Version | Thay đổi / giả thuyết | Case đúng | Routing | Arguments | Multi-turn | Run file |
|---|---|---:|---:|---:|---:|---|
| v0 | Starter chưa sửa; baseline | 14/20 (70%) | 75% | 70% | 100.00% | `runs/v0_B_base_openrouter_20261110T105954975593.json` |
| v1 | Thay chỉ dẫn đoán account/URL bằng hỏi clarify khi thiếu dữ liệu | 18/20 (90%) | 90% | 90% | 83.33% | `runs/v1_B_base_openrouter_20261110T111806972710.json` |
| v2 | Thay gửi ngay bằng hỏi xác nhận trước khi gửi Telegram | 17/20 (85%) | 90% | 85% | 66.67% | `runs/v2_B_base_openrouter_20261110T113445708717.json` |
| v3 | Chỉ sửa lookup.description: web/news, args và ngữ cảnh nhiều lượt | 19/20 (95%) | 95% | 95% | 83.33% | `runs/v3_B_base_openrouter_20261110T144339922260.json` |
| v4-tools | Thêm deduplicate, TOOL.md và đăng ký; giữ prompt/declarations v3 khác | 19/20 (95%) | 100% | 95% | 100.00% | `runs/v4-tools_B_base_openrouter_20261110T155521666806.json` |

Giả thuyết đầy đủ, metric trước/sau, prompt/tools hash và đường dẫn run được ghi trong `artifacts/version_log.csv`. Snapshots v1–v4-tools ở `artifacts/snapshots/`. Run v1 có 20 lỗi kết nối được giữ làm bằng chứng sự cố, không đưa vào so sánh chất lượng.

V2 giảm từ 18/20 xuống 17/20: không kết luận bản mới luôn tốt hơn. V3 đạt 19/20, sửa R13/M02 nhưng vẫn gọi thừa Twitter ở M06. V4-tools cũng đạt 19/20, routing và multi-turn đạt 100%, nhưng R11 thiếu `response_type=text`. Đây là các kết quả quan sát, chưa chứng minh tính ổn định qua nhiều lần chạy.

Cấu hình demo hiện tại là `v4-tools` để có tool mới. V3 vẫn được lưu nguyên trạng; việc thêm tool thay đổi tools hash nên không gán điểm v3 cho artifacts hiện tại.

## B2. Failure Analysis

| Case | failure_type của case | v0 | v1 | v2 | v3 | v4-tools |
|---|---|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | FAIL | PASS | PASS | PASS | PASS |
| R10_missing_handle | missing_info | FAIL | PASS | PASS | PASS | PASS |
| R11_missing_url | missing_info | FAIL | PASS | PASS | PASS | FAIL |
| R12_confirm_before_send | wrong_boundary | FAIL | FAIL | PASS | PASS | PASS |
| R13_parallel_web_and_tweets | wrong_tool | FAIL | PASS | FAIL | PASS | PASS |
| R14_out_of_scope_coding | out_of_scope | FAIL | PASS | PASS | PASS | PASS |
| M06_switch_tool | wrong_tool | PASS | FAIL | FAIL | FAIL | PASS |
| M02_carryover_timeframe | wrong_arg_value | PASS | PASS | FAIL | PASS | PASS |

- **R10/R11:** v0 tự đoán `sama`/URL. V1 yêu cầu hỏi lại; v4-tools R11 chọn đúng clarify nhưng không truyền tường minh `response_type`, nên strict eval vẫn FAIL dù tool có default text.
- **R12:** prompt v2 sửa ranh giới gửi; case chuyển PASS. Tool runtime cũng chặn gửi nếu chưa confirmed. Eval này chỉ chứng minh bước hỏi xác nhận, không chứng minh gửi Telegram thật thành công.
- **R13/M02:** lỗi topic/news và nhầm nguồn. Mô tả lookup v3 giúp hai case PASS trong run đã đo.
- **M06:** v3 gọi đúng lookup nhưng gọi thêm social_search cho nguồn user đã bỏ; v4-tools không gọi thừa trong lần đo này. Không gán sự khác biệt đó chắc chắn cho tool mới từ một cặp run.
- **R08/R14:** no_tool PASS chỉ kiểm tra không gọi tool; không tự chấm chất lượng từ chối ngoài phạm vi.

**Các lỗi còn lại của cấu hình demo:**

| Suite / Case | Tool calls thực tế | Failures |
|---|---|---|
| base / R11_missing_url | `[{"name": "clarify", "args": {"question": "Bạn có thể cung cấp URL hoặc nội dung của bài viết không?"}}]` | response_type: expected 'text', got None |
| group / G01_deduplicate_missing_items | `[{"name": "clarify", "args": {"question": "Bạn có thể cung cấp danh sách các nguồn mà bạn muốn lọc trùng không?"}}]` | response_type: expected 'text', got None |
| group / G06_replace_twitter_with_web | `[{"name": "lookup", "args": {"query": "AI", "topic": "general", "timeframe": "week"}}]` | topic: expected 'news', got 'general' |

**Lỗi tool khác với lỗi model:** base eval chấm routing/arguments, không bảo đảm API tool thành công.
Run base hiện có lỗi thực thi: `R01_user_tweets_routing/timeline: RuntimeError`; `R02_search_tweets_routing/social_search: RuntimeError`; `R05_limit_arg/timeline: RuntimeError`; `R07_search_type_arg/social_search: RuntimeError`; `R13_parallel_web_and_tweets/social_search: RuntimeError`; `M01_clarify_then_fill/timeline: RuntimeError`; `M03_correction_handle/timeline: RuntimeError`; `M05_correction_limit/timeline: RuntimeError`. Cần kiểm tra cấu hình/dịch vụ trước demo; không sửa điểm eval để che lỗi tool.

## B3. Team Eval Cases

Đã viết **10 case: 5 single-turn và 5 multi-turn** trong `data/eval_group.json`. Run `runs/v4-tools_B_group_openrouter_20261110T155319890960.json` đạt **8/10**, không có provider error. Đây là suite riêng, không so trực tiếp 80% group với 95% base.

| Case | Kiểu | Kiểm tra gì | Kỳ vọng | Kết quả |
|---|---|---|---|---|
| G01_deduplicate_missing_items | Single | Tool mới cần danh sách nguồn; chưa có thì hỏi lại, không bịa items. | clarify | FAIL |
| G02_deduplicate_supplied_sources | Single | Route đến tool mới khi user đã cung cấp nguồn. Eval chấm routing; nội dung items và kết quả lọc được kiểm tra bằng unit test. | deduplicate | PASS |
| G03_web_news_week | Single | Explicit topic=news, timeframe=week và giới hạn kết quả. | lookup | PASS |
| G04_format_existing_items | Single | Dữ liệu đã đủ thì format, tránh gọi tool research thừa. | format | PASS |
| G05_confirm_before_delivery | Single | Yêu cầu gửi ban đầu chưa phải xác nhận; hỏi yes/no trước. | clarify | PASS |
| G06_replace_twitter_with_web | Multi | Hồi quy M06: đổi nguồn phải bỏ tool cũ, không gọi song song. | lookup | FAIL |
| G07_correct_account_and_limit | Multi | Ưu tiên correction mới nhất và bỏ @ khỏi screenname. | timeline | PASS |
| G08_cancel_delivery | Multi | User từ chối gửi thì dừng hành động; no_tool không tự kiểm tra nội dung câu trả lời. | Không gọi tool | PASS |
| G09_deduplicate_after_clarification | Multi | Sau clarify phải dùng items vừa được cung cấp để route đến tool mới. Payload được kiểm tra bằng unit test. | deduplicate | PASS |
| G10_correct_news_timeframe | Multi | Đổi timeframe/limit nhưng giữ chủ đề và nguồn web. | lookup | PASS |

G02/G09 chấm routing tới tool mới; không so nested array items trong scorer hiện tại. Payload và kết quả dedup được kiểm tra bằng unit tests. Không sửa bộ base eval hoặc nới kỳ vọng group sau khi xem kết quả.

## B4. Live Chat Evidence

Transcript CLI: `transcripts/v4-tools_openrouter_20261110T155506079575.transcript.json`. Chạy `chat.main()` thật qua `scripts/run_submission_checks.py chat --version v4-tools` với 3 lượt input được chuẩn bị sẵn; responses và tool results đều do model/API thực trả về, không phải mock.

| Lượt | User yêu cầu | Tool thực gọi | Trạng thái |
|---|---|---|---|
| 1 | Lọc trùng các nguồn giúp tôi. | Không gọi tool | answered |
| 2 | Cung cấp 3 nguồn gồm một URL trùng có tracking; chỉ lọc trùng và giữ nguồn đầu. | deduplicate | answered |
| 3 | Trình bày các nguồn duy nhất vừa có thành bullets, kèm URL. Không tìm thêm nguồn. | format | answered |

Quan sát: lượt đầu model hỏi xin nguồn bằng text trực tiếp; lượt hai gọi deduplicate, giữ 2/3 nguồn; lượt ba gọi format để trình bày kết quả. Hỏi bằng text chưa phải bằng chứng gọi clarify, nên không diễn giải hai hành vi là giống nhau trong eval. Prompt/tools hash nằm trong transcript.

## B5. Tool mới, test và demo

- Tool mới: `tools/deduplicate/tool.py` + `TOOL.md`, đã đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml`.
- So URL sau khi bỏ tracking/fragment và chuẩn hóa host/port; giữ nguồn đầu và thứ tự, không gộp khác path/query nội dung, không truy cập mạng. Input sai trả error dict; item lỗi được báo riêng và vẫn trả các nguồn hợp lệ.
- Tool mới có **9 trường hợp unit test** (gồm parametrization): happy path, sai kiểu, URL lỗi, giữ URL khác nội dung và danh sách rỗng. Đã hoàn thành toàn bộ stub test tool cũ.
- Lệnh kiểm tra: `python -X utf8 -m pytest -q tests/test_tool_contract.py tests/test_tools_examples.py tests/test_tools_todo.py`. Kết quả: **90 passed, 0 failed, 0 skipped**. Bằng chứng: `analysis/tool_tests.txt`. HTTP đều mock, không tốn API; bộ test UI không chạy theo yêu cầu người dùng. Không khẳng định đây là kết quả toàn bộ pytest gồm UI.
- Chưa ghi nhận/sửa bug code tool có sẵn trong lượt làm này; các hồi quy model được ghi ở B2, không gọi chúng là regression test của Python tool.
- UI: `app.py`, chat nhiều lượt, xem tool events, tải và tự lưu transcript. Giữ **local** tại http://127.0.0.1:8501 theo lựa chọn người dùng; không có URL public. Hướng dẫn: `UI-README.md`.
- Telegram không được gửi trong đợt kiểm tra: helper loại token/chat ID khỏi môi trường sau khi nạp cấu hình. Không có bằng chứng gửi thật. Không công bố bonus action đã hoàn thành chỉ từ R12 PASS.
- Có UI + 1 tool mới, chưa đủ điều kiện bonus hơn 3 tool mới.

## B6. Reflection

1. System prompt phù hợp cho nguyên tắc hỏi lại và xin xác nhận; tool declaration phù hợp cho ranh giới routing và conventions arguments. V3 kiểm chứng thay đổi một description thay vì sửa case để tăng điểm.
2. Cần phân biệt lỗi model với lỗi API tool; PASS routing không bảo đảm dữ liệu đúng/đầy đủ. Trường hợp no_tool cần đọc câu trả lời thủ công; kết quả format/dedup còn cần unit test.
3. Còn hạn chế: prompt vẫn có câu ép một bước/chọn một tool; nhiều mô tả tool starter còn ngắn. Lượt sau nên tách các giả thuyết riêng để bỏ mâu thuẫn đó, mô tả conventions đầy đủ và kiểm tra lại toàn bộ suite. Không coi việc hoàn thành v0–v3 là bằng chứng đã khắc phục mọi lỗi.
4. Lỗi còn lại cần thử: clarify truyền response_type tường minh; lookup giữ topic=news qua lượt đổi nguồn. Chạy nhiều lần hoặc holdout trước khi kết luận ổn định, không tối ưu chỉ cho các câu trong base eval.

## B7. Small Local Model Challenge (bonus)

Chưa thực hiện; chưa có run Ollama hoặc bảng so sánh cloud/local. Không tính bonus này.
