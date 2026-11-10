# UI Research Agent — Streamlit

Chạy các lệnh sau tại `starter_v0` trong PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Mở http://localhost:8501. API key đọc từ `.env` như khi chạy `chat.py`; giao diện không hiển thị giá trị key.

## Dùng thử

1. Chọn provider; để trống model để dùng mặc định của provider hoặc nhập model muốn dùng. Nhãn version được gợi ý từ run có prompt/tools hash khớp với các file hiện tại; nếu chưa có run khớp thì dùng `working`.
2. Nhập yêu cầu hoặc chọn câu hỏi mẫu. Agent dùng cùng vòng lặp gọi tool nhiều bước với `chat.py`.
3. Khi agent hỏi bổ sung thông tin hoặc xác nhận, trả lời trong ô chat để tiếp tục hội thoại.
4. Mở “Xem … lần gọi tool” dưới câu trả lời để xem arguments và kết quả thực thi, bao gồm lỗi dịch vụ.
5. Dùng “Tải transcript JSON” ở thanh bên để lấy bằng chứng. Mỗi lượt cũng tự lưu vào `transcripts/ui_<uuid>.transcript.json`; các phiên trình duyệt dùng transcript riêng.
6. Chọn “Cuộc trò chuyện mới” để thay provider/model/version. Hội thoại trước vẫn có file transcript đã lưu; hội thoại mới không mang lịch sử cũ sang.

Nhãn version chỉ là nhãn; prompt/tools hash trong transcript mới xác định chính xác bộ artifacts. Giao diện giữ bản prompt/tools đã nạp trong suốt cuộc trò chuyện. Sau khi sửa artifacts, bắt đầu cuộc trò chuyện mới để dùng bản sửa.

## Kiểm tra không tốn API

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_app.py tests/test_tool_contract.py tests/test_tools_examples.py
```

UI tests dùng provider giả và thư mục transcript tạm để kiểm tra hội thoại nhiều lượt, lỗi provider và reset phiên, không gửi request API thật. Chúng không đo chất lượng chọn tool của model.

## Chia sẻ khi demo

Sau khi UI chạy local, có thể dùng cách Cloudflare Tunnel trong README chính:

```powershell
cloudflared tunnel --url http://localhost:8501
```

Chép URL HTTPS được trả về vào `artifacts/REPORT.md` Phần A. Giữ cả Streamlit và tunnel đang chạy trong buổi demo. Hiện repo chưa có URL public; không commit `.env` hoặc API keys.
