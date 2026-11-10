# v3 — Làm rõ cách dùng lookup

## Mốc so sánh và lỗi cần kiểm chứng

Hai lần chạy v2 đều đạt 17/20 (85%). Lấy lần gần nhất `runs/v2_B_base_openrouter_20261110T113445708717.json` làm mốc, model `openai/gpt-4o-mini`: routing 90%, arguments 85%, multi-turn 66.67%, không có provider error.

- R13: gọi đủ web và Twitter nhưng `lookup` thiếu `topic="news"`.
- M02: yêu cầu tin robotics hôm nay nhưng chọn `social_search`, cần tìm web với chủ đề mới và giữ thời gian hôm nay.
- M06: user đã bỏ Twitter, chuyển sang web nhưng agent vẫn chọn `social_search`.

## Một giả thuyết, một thay đổi

Giả thuyết: mô tả `lookup` quá mơ hồ nên model chưa phân biệt nguồn web với Twitter và chưa truyền rõ arguments cho tin tức.

Chỉ sửa `lookup.description` trong `artifacts/tools.yaml`, từ “Tra cứu thông tin trên internet.” thành hướng dẫn:

- Dùng cho web và tin tức không chỉ định mạng xã hội; không dùng thay timeline, tìm tweet hoặc đọc URL đã biết.
- Tin tức phải truyền rõ `topic="news"`; thời gian hôm nay/tuần/tháng/năm tương ứng `day/week/month/year`.
- Giữ từ khóa chủ đề trong `query`, không tự thêm từ chỉ nguồn/thời gian.
- Giữ các ràng buộc còn hiệu lực qua các lượt, thay chủ đề khi user sửa; chuyển sang `lookup` nếu user đổi từ Twitter sang web.
- Khi cần cả hai nguồn, gọi cả `lookup` và `social_search`.

Giữ nguyên prompt v2, schema arguments, các tool khác, code Python và bộ eval. Như vậy quy tắc hỏi lại của v1 và xác nhận trước khi gửi của v2 vẫn được giữ. Không khẳng định đã sửa được lỗi trước khi có run thực tế.

Snapshots: `artifacts/snapshots/v2/` là bản trước khi sửa; `artifacts/snapshots/v3/` là bản v3. Hash, giả thuyết và điểm thực đo đã ghi vào `artifacts/version_log.csv`.

## Lệnh chạy tại starter_v0

```powershell
python run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v3 --suite base --eval-cases data/eval_base.json
```

Kiểm tra đủ 20 case, nhất là R13/M02/M06 có chuyển sang PASS không và R10/R11/R12 có tiếp tục PASS không. So điểm tổng với v2 (85%) và v1 (90%); không chọn v3 chỉ vì version mới hơn. Khi run xong, cập nhật điểm thực đo và đường dẫn run vào version log.

Trong bước chuẩn bị v3 không chạy pytest theo yêu cầu của người dùng. Chỉ kiểm tra YAML đọc được, đúng một description thay đổi, và prompt vẫn khớp snapshot v2. Sau đó người dùng đã chạy API và có kết quả thực tế dưới đây.

## Kết quả thực đo

Run `runs/v3_B_base_openrouter_20261110T144339922260.json`: 19/20 (95%), routing 95%, arguments 95%, multi-turn 83.33%, không có provider error. R13 và M02 đã PASS. M06 vẫn FAIL: agent gọi đúng `lookup(query="OpenAI", topic="news")` nhưng gọi thêm `social_search(query="OpenAI")` dù nguồn Twitter đã bị hủy. Đây là lỗi gọi thừa, không còn là thiếu lookup.

V3 tốt hơn v2 ở run đã đo, nhưng chưa có bằng chứng ổn định qua nhiều lần chạy. Việc thêm tool sau đó được ghi riêng là `v4-tools`, không sửa snapshot hoặc hash của v3.

## Demo trên UI

Trong UI đã cập nhật, chọn `v3` từ dropdown “Phiên bản agent” để nạp đúng snapshot v3. Đổi version tự bắt đầu cuộc trò chuyện mới, giữ nguyên các transcript cũ. Chọn “Bản đang sửa” nếu muốn dùng các file hiện tại thay vì snapshot.

Ví dụ: “Tin AI hôm nay có gì?” → “Còn robotics thì sao? Vẫn chỉ lấy tin hôm nay trên web.” Hoặc yêu cầu tìm Twitter rồi chuyển sang web để quan sát agent có đổi từ `social_search` sang `lookup` hay không. Demo này không thay thế base eval.
