---
name: deduplicate
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [items]
outputs: [items, input_count, item_count, duplicate_count, removed_indices, invalid_items]
side_effect: false
---
# deduplicate

Tool mới của nhóm: loại các nguồn trùng URL trước khi tổng hợp bản tin đa nguồn.

Nhận danh sách object có `url`, giữ bản đầu tiên và thứ tự ban đầu, không sửa metadata hoặc dữ liệu đầu vào. So sánh URL sau khi chuẩn hóa scheme/hostname, port mặc định và bỏ fragment, tham số `utm_*`, `fbclid`, `gclid`. Giữ nguyên path, các tham số nội dung, thứ tự query parameters và phân biệt HTTP với HTTPS; không gộp hai bài chỉ vì giống tiêu đề.

Chỉ xử lý HTTP(S) URL tuyệt đối, không truy cập mạng, không cần API key và không gửi dữ liệu đi. URL sai/thiếu hoặc chứa credentials được báo trong `invalid_items`; các nguồn hợp lệ vẫn được trả về cùng `error="invalid_items"`. Sai kiểu `items` trả `error="invalid_input"` thay vì raise. Danh sách rỗng trả 0 nguồn.

Dùng khi user yêu cầu lọc trùng các nguồn đã có. Không dùng thay tìm web, đọc bài hoặc format; không tự đoán danh sách nguồn còn thiếu. Trường hợp lỗi được kiểm tra offline trong `tests/test_tools_todo.py`.
