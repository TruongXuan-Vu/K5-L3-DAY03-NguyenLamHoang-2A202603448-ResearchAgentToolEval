---
name: recency
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [items, within, max_items]
outputs: [items, input_count, item_count, within, out_of_range_count, undated_count, newest_first]
side_effect: false
---
# recency

Tool lọc và xếp các nguồn theo thời gian đăng trước khi tổng hợp bảng tin, phục vụ các yêu cầu dạng "tin hôm nay", "tin trong tuần này".

Nhận danh sách object có trường `date` (mà `social_search` trả về cho tweet,
hoặc ngày từ trang đã `fetch`), parse đa định dạng (ISO 8601 có/không múi giờ,
RFC 822 của RSS, `dd/mm/yyyy`, unix timestamp giây/mili-giây). `within` nhận
`today` (24 giờ qua), `week` (7 ngày), `month` (31 ngày) hoặc `any` (chỉ xếp,
mặc định); item ngoài khung bị loại và đếm vào `out_of_range_count`. Item
thiếu/sai ngày hoặc có ngày ở tương lai không bịa lại mà dồn xuống cuối danh
sách và đếm vào `undated_count`; entry không phải object bị loại và vẫn đếm
vào `undated_count`. Kết quả xếp mới nhất trước (`newest_first`),
cùng mốc thời gian giữ thứ tự đầu vào; `max_items` cắt số dòng bảng tin.

Không truy cập mạng, không cần API key, không sửa items đầu vào và không tự
đoán ngày còn thiếu. Khác `deduplicate` (trùng URL) và `cluster_stories` (trùng
chuyện): tool này chỉ quan tâm thời gian, dùng sau hai tool đó trước khi
`format`. Sai kiểu `items` trả `error="invalid_input"`, `within` lạ trả
`error="invalid_within"` thay vì raise. Danh sách rỗng trả 0 dòng. Hành vi
được kiểm tra offline trong `tests/test_recency.py`.
