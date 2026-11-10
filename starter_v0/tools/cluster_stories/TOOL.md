---
name: cluster_stories
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [items, max_items, similarity]
outputs: [items, input_count, item_count, merged_count, invalid_items]
side_effect: false
---
# cluster_stories

Tool của nhóm là gộp các nguồn khác nhau đang nói về cùng một chuyện
trước khi tổng hợp bảng tin đa nguồn web + X.

Nhận danh sách object có `title` (mà `lookup` và `social_search` đều trả về),
so độ tương đồng tiêu đề bằng tập token sau khi fold dấu và bỏ stopword
(tiếng Việt lẫn tiếng Anh), gộp khi Jaccard ≥ `similarity` (mặc định 0.6).
Mỗi chuyện giữ đúng một đại diện: item có `score` cao nhất, kèm `story_count`
và `also_from` (các nguồn phụ cùng chuyện); thứ tự câu chuyện theo item đầu
tiên xuất hiện. Không truy cập mạng, không cần API key, không sửa items đầu
vào và không bịa nguồn mới.

Khác `deduplicate` (chỉ bỏ trùng URL): tool này gộp trùng nội dung qua tiêu
đề nên dùng sau khi đã bỏ trùng URL. Không dùng thay tìm web, đọc bài hoặc
format. Item thiếu/sai `title` được báo trong `invalid_items`, các item hợp lệ
vẫn được gộp; sai kiểu `items` trả `error="invalid_input"` thay vì raise.
Danh sách rỗng trả 0 chuyện. Hành vi được kiểm tra offline trong
`tests/test_cluster_stories.py`.
