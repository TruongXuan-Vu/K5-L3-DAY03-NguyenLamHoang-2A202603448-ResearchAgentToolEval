# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:
- Members:
- Provider/model:

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tìm tin trên web và X/Twitter, đọc nội dung từ URL, tìm tài liệu khoa học và trình bày thông tin thành bản tin có liên kết nguồn. Agent hỏi lại khi thiếu tài khoản hoặc URL; bản v2 bổ sung quy tắc hỏi xác nhận trước khi gửi nội dung lên Telegram.

**Dành cho:** người cần theo dõi tin AI/công nghệ, tổng hợp thông tin theo chủ đề và tra cứu nguồn để đọc sâu hơn.

**Link dùng thử (deploy):**

UI Streamlit đã được bổ sung tại `app.py`, hỗ trợ chat nhiều lượt, xem các lần gọi tool và tải transcript JSON. Chạy `python -m streamlit run app.py` trong thư mục `starter_v0`, sau khi cài `requirements.txt`, rồi mở **http://localhost:8501** trên máy chạy UI.

**Link public cho team khác:** chưa bổ sung; cần triển khai hoặc mở Cloudflare Tunnel theo README. Hướng dẫn chạy và dùng thử: `UI-README.md`.

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
| `paper_text` | Tải PDF arXiv và trích xuất nội dung văn bản. | Không |

Hiện cả 10 tool đều có sẵn trong starter; nhóm chưa đăng ký tool mới.

## A3. Câu hỏi mẫu để thử

1. **Tìm tin web:** "Tìm 5 tin về AI hôm nay trên web, kèm liên kết nguồn."
2. **Đọc bài viết:** "Đọc và tóm tắt bài viết tại https://www.anthropic.com/news/claude."
3. **Theo dõi tài khoản:** "Lấy 5 bài đăng mới nhất của @elonmusk trên X/Twitter."
4. **Thử hỏi lại:** "Tóm tắt 5 tweet mới nhất giúp mình." Khi agent hỏi tài khoản, trả lời: "Của @elonmusk nhé."
5. **Thử xác nhận gửi:** "Đăng bản tin này lên Telegram giúp mình: Ba chủ đề cần theo dõi hôm nay là AI, robotics và an toàn mô hình." Quan sát agent hỏi xác nhận; có thể trả lời "Không gửi" để kết thúc bước thử.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
