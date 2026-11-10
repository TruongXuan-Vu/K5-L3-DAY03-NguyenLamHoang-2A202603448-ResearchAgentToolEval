"""Refresh report evidence from actual measured runs and CLI transcripts."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def esc(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def load_latest(version: str, suite: str = "base"):
    candidates = []
    for path in (ROOT / "runs").glob(f"{version}_B_{suite}_*.json"):
        run = json.loads(path.read_text(encoding="utf-8"))
        if run["summary"].get("measured_cases") and not run["summary"].get("provider_error_cases"):
            candidates.append((path, run))
    return sorted(candidates, key=lambda value: value[0].name)[-1]


def main() -> None:
    report_path = ROOT / "artifacts/REPORT.md"
    current = report_path.read_text(encoding="utf-8")
    part_a = current.split("# PHẦN B — Chi tiết / Bằng chứng", 1)[0]
    part_a = part_a.replace("- Team:\n", "- Team: Chưa cung cấp\n").replace("- Members:\n", "- Members: Chưa cung cấp\n")
    part_a = part_a.replace("- Provider/model:\n", "- Provider/model: OpenRouter / openai/gpt-4o-mini\n")
    part_a = part_a.replace("Hiện cả 10 tool đều có sẵn trong starter; nhóm chưa đăng ký tool mới.",
                            "Hiện có 11 tool: 10 tool starter và 1 tool mới của nhóm (`deduplicate`).")
    if "| `deduplicate` |" not in part_a:
        part_a = part_a.replace("| `paper_text`", "| `deduplicate` | Lọc nguồn trùng URL, giữ bản đầu tiên; xử lý local, không cần API key. | Có |\n| `paper_text`", 1)
    part_a = part_a.replace("**Link public cho team khác:** chưa bổ sung; cần triển khai hoặc mở Cloudflare Tunnel theo README.",
                            "**Link demo local:** http://127.0.0.1:8501 — chỉ mở trên máy chạy UI. Theo lựa chọn của người dùng, không tạo link public.")
    part_a = part_a.replace("3. **Theo dõi tài khoản:** \"Lấy 5 bài đăng mới nhất của @elonmusk trên X/Twitter.\"",
                            '3. **Tool mới — lọc nguồn trùng:** `Lọc trùng các nguồn này, giữ bản đầu: [{"url":"https://example.org/ai?utm_source=demo"},{"url":"https://example.org/ai"}].`')

    runs = {version: load_latest(version) for version in ["v0", "v1", "v2", "v3", "v4-tools"]}
    group_path, group = load_latest("v4-tools", "group")
    changes = {
        "v0": "Starter chưa sửa; baseline",
        "v1": "Thay chỉ dẫn đoán account/URL bằng hỏi clarify khi thiếu dữ liệu",
        "v2": "Thay gửi ngay bằng hỏi xác nhận trước khi gửi Telegram",
        "v3": "Chỉ sửa lookup.description: web/news, args và ngữ cảnh nhiều lượt",
        "v4-tools": "Thêm deduplicate, TOOL.md và đăng ký; giữ prompt/declarations v3 khác",
    }
    lines = ["# PHẦN B — Chi tiết / Bằng chứng", "", "## B1. Version Evidence", "",
             "Các run dưới đây dùng cùng model `openai/gpt-4o-mini`, cùng base eval 20 case và không có provider error. Mỗi điểm là một lần đo; không coi đây là trung bình thống kê.", "",
             "| Version | Thay đổi / giả thuyết | Case đúng | Routing | Arguments | Multi-turn | Run file |",
             "|---|---|---:|---:|---:|---:|---|"]
    for version, (path, run) in runs.items():
        s = run["summary"]
        lines.append(f"| {version} | {changes[version]} | {s['passed_cases']}/{s['total_cases']} ({s['case_accuracy']:.0%}) | {s['tool_routing_accuracy']:.0%} | {s['argument_accuracy']:.0%} | {s['multiturn_accuracy']:.2%} | `{path.relative_to(ROOT).as_posix()}` |")
    lines += ["", "Giả thuyết đầy đủ, metric trước/sau, prompt/tools hash và đường dẫn run được ghi trong `artifacts/version_log.csv`. Snapshots v1–v4-tools ở `artifacts/snapshots/`. Run v1 có 20 lỗi kết nối được giữ làm bằng chứng sự cố, không đưa vào so sánh chất lượng.", "",
              "V2 giảm từ 18/20 xuống 17/20: không kết luận bản mới luôn tốt hơn. V3 đạt 19/20, sửa R13/M02 nhưng vẫn gọi thừa Twitter ở M06. V4-tools cũng đạt 19/20, routing và multi-turn đạt 100%, nhưng R11 thiếu `response_type=text`. Đây là các kết quả quan sát, chưa chứng minh tính ổn định qua nhiều lần chạy.", "",
              "Cấu hình demo hiện tại là `v4-tools` để có tool mới. V3 vẫn được lưu nguyên trạng; việc thêm tool thay đổi tools hash nên không gán điểm v3 cho artifacts hiện tại.", "",
              "## B2. Failure Analysis", "",
              "| Case | failure_type của case | v0 | v1 | v2 | v3 | v4-tools |",
              "|---|---|---|---|---|---|---|"]
    results = {version: {r["id"]: r for r in run["results"]} for version, (_, run) in runs.items()}
    case_ids = list(dict.fromkeys(r["id"] for _, run in runs.values() for r in run["results"] if not r["result"]["passed"]))
    for case_id in case_ids:
        states = ["PASS" if results[v][case_id]["result"]["passed"] else "FAIL" for v in runs]
        category = next(results[v][case_id]["result"].get("case_failure_type", "") for v in runs if not results[v][case_id]["result"]["passed"])
        lines.append("| " + " | ".join([case_id, category, *states]) + " |")
    lines += ["", "- **R10/R11:** v0 tự đoán `sama`/URL. V1 yêu cầu hỏi lại; v4-tools R11 chọn đúng clarify nhưng không truyền tường minh `response_type`, nên strict eval vẫn FAIL dù tool có default text.",
              "- **R12:** prompt v2 sửa ranh giới gửi; case chuyển PASS. Tool runtime cũng chặn gửi nếu chưa confirmed. Eval này chỉ chứng minh bước hỏi xác nhận, không chứng minh gửi Telegram thật thành công.",
              "- **R13/M02:** lỗi topic/news và nhầm nguồn. Mô tả lookup v3 giúp hai case PASS trong run đã đo.",
              "- **M06:** v3 gọi đúng lookup nhưng gọi thêm social_search cho nguồn user đã bỏ; v4-tools không gọi thừa trong lần đo này. Không gán sự khác biệt đó chắc chắn cho tool mới từ một cặp run.",
              "- **R08/R14:** no_tool PASS chỉ kiểm tra không gọi tool; không tự chấm chất lượng từ chối ngoài phạm vi.", "",
              "**Các lỗi còn lại của cấu hình demo:**", "",
              "| Suite / Case | Tool calls thực tế | Failures |",
              "|---|---|---|"]
    for suite, run in [("base", runs["v4-tools"][1]), ("group", group)]:
        for row in run["results"]:
            if not row["result"]["passed"]:
                calls = json.dumps(row["result"]["actual_tool_calls"], ensure_ascii=False)
                lines.append(f"| {suite} / {row['id']} | `{esc(calls)}` | {esc('; '.join(row['result']['failures']))} |")
    tool_errors = [(row["id"], event["tool"], event["result"].get("error"))
                   for row in runs["v4-tools"][1]["results"] for event in row.get("tool_results", [])
                   if isinstance(event.get("result"), dict) and event["result"].get("error")]
    lines += ["", "**Lỗi tool khác với lỗi model:** base eval chấm routing/arguments, không bảo đảm API tool thành công."]
    if tool_errors:
        lines += ["Run base hiện có lỗi thực thi: " + "; ".join(f"`{case}/{tool}: {error}`" for case, tool, error in tool_errors) + ". Cần kiểm tra cấu hình/dịch vụ trước demo; không sửa điểm eval để che lỗi tool."]
    lines += ["", "## B3. Team Eval Cases", "",
              f"Đã viết **10 case: 5 single-turn và 5 multi-turn** trong `data/eval_group.json`. Run `{group_path.relative_to(ROOT).as_posix()}` đạt **{group['summary']['passed_cases']}/10**, không có provider error. Đây là suite riêng, không so trực tiếp 80% group với 95% base.", "",
              "| Case | Kiểu | Kiểm tra gì | Kỳ vọng | Kết quả |",
              "|---|---|---|---|---|"]
    for row in group["results"]:
        expect = row["expect"]
        wanted = "Không gọi tool" if expect.get("no_tool") else ", ".join(call["name"] for call in expect["tool_calls"])
        lines.append(f"| {row['id']} | {'Multi' if row['is_multiturn'] else 'Single'} | {esc(row['metadata']['what_it_tests'])} | {wanted} | {'PASS' if row['result']['passed'] else 'FAIL'} |")
    lines += ["", "G02/G09 chấm routing tới tool mới; không so nested array items trong scorer hiện tại. Payload và kết quả dedup được kiểm tra bằng unit tests. Không sửa bộ base eval hoặc nới kỳ vọng group sau khi xem kết quả.", "",
              "## B4. Live Chat Evidence", ""]
    chat_paths = sorted((ROOT / "transcripts").glob("v4-tools_openrouter_*.transcript.json"))
    if chat_paths:
        path = chat_paths[-1]
        transcript = json.loads(path.read_text(encoding="utf-8"))
        lines += [f"Transcript CLI: `{path.relative_to(ROOT).as_posix()}`. Chạy `chat.main()` thật qua `scripts/run_submission_checks.py chat --version v4-tools` với 3 lượt input được chuẩn bị sẵn; responses và tool results đều do model/API thực trả về, không phải mock.", "",
                  "| Lượt | User yêu cầu | Tool thực gọi | Trạng thái |",
                  "|---|---|---|---|"]
        for turn in transcript["turns"]:
            names = ", ".join(event["tool"] for event in turn.get("tool_events", [])) or "Không gọi tool"
            request = turn["user"]
            if len(request) > 210:
                request = "Cung cấp 3 nguồn gồm một URL trùng có tracking; chỉ lọc trùng và giữ nguồn đầu."
            lines.append(f"| {turn['turn_index']} | {esc(request)} | {names} | {turn['status']} |")
        lines += ["", "Quan sát: lượt đầu model hỏi xin nguồn bằng text trực tiếp; lượt hai gọi deduplicate, giữ 2/3 nguồn; lượt ba gọi format để trình bày kết quả. Hỏi bằng text chưa phải bằng chứng gọi clarify, nên không diễn giải hai hành vi là giống nhau trong eval. Prompt/tools hash nằm trong transcript."]
    lines += ["", "## B5. Tool mới, test và demo", "",
              "- Tool mới: `tools/deduplicate/tool.py` + `TOOL.md`, đã đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml`.",
              "- So URL sau khi bỏ tracking/fragment và chuẩn hóa host/port; giữ nguồn đầu và thứ tự, không gộp khác path/query nội dung, không truy cập mạng. Input sai trả error dict; item lỗi được báo riêng và vẫn trả các nguồn hợp lệ.",
              "- Tool mới có **9 trường hợp unit test** (gồm parametrization): happy path, sai kiểu, URL lỗi, giữ URL khác nội dung và danh sách rỗng. Đã hoàn thành toàn bộ stub test tool cũ.",
              "- Lệnh kiểm tra: `python -X utf8 -m pytest -q tests/test_tool_contract.py tests/test_tools_examples.py tests/test_tools_todo.py`. Kết quả: **90 passed, 0 failed, 0 skipped**. Bằng chứng: `analysis/tool_tests.txt`. HTTP đều mock, không tốn API; bộ test UI không chạy theo yêu cầu người dùng. Không khẳng định đây là kết quả toàn bộ pytest gồm UI.",
              "- Chưa ghi nhận/sửa bug code tool có sẵn trong lượt làm này; các hồi quy model được ghi ở B2, không gọi chúng là regression test của Python tool.",
              "- UI: `app.py`, chat nhiều lượt, xem tool events, tải và tự lưu transcript. Giữ **local** tại http://127.0.0.1:8501 theo lựa chọn người dùng; không có URL public. Hướng dẫn: `UI-README.md`.",
              "- Telegram không được gửi trong đợt kiểm tra: helper loại token/chat ID khỏi môi trường sau khi nạp cấu hình. Không có bằng chứng gửi thật. Không công bố bonus action đã hoàn thành chỉ từ R12 PASS.",
              "- Có UI + 1 tool mới, chưa đủ điều kiện bonus hơn 3 tool mới.", "",
              "## B6. Reflection", "",
              "1. System prompt phù hợp cho nguyên tắc hỏi lại và xin xác nhận; tool declaration phù hợp cho ranh giới routing và conventions arguments. V3 kiểm chứng thay đổi một description thay vì sửa case để tăng điểm.",
              "2. Cần phân biệt lỗi model với lỗi API tool; PASS routing không bảo đảm dữ liệu đúng/đầy đủ. Trường hợp no_tool cần đọc câu trả lời thủ công; kết quả format/dedup còn cần unit test.",
              "3. Còn hạn chế: prompt vẫn có câu ép một bước/chọn một tool; nhiều mô tả tool starter còn ngắn. Lượt sau nên tách các giả thuyết riêng để bỏ mâu thuẫn đó, mô tả conventions đầy đủ và kiểm tra lại toàn bộ suite. Không coi việc hoàn thành v0–v3 là bằng chứng đã khắc phục mọi lỗi.",
              "4. Lỗi còn lại cần thử: clarify truyền response_type tường minh; lookup giữ topic=news qua lượt đổi nguồn. Chạy nhiều lần hoặc holdout trước khi kết luận ổn định, không tối ưu chỉ cho các câu trong base eval.", "",
              "## B7. Small Local Model Challenge (bonus)", "", "Chưa thực hiện; chưa có run Ollama hoặc bảng so sánh cloud/local. Không tính bonus này.", ""]
    report_path.write_text(part_a + "\n".join(lines), encoding="utf-8")
    print("Updated Part A and generated Part B from measured run/transcript evidence.")


if __name__ == "__main__":
    main()
