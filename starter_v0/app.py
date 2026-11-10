"""Streamlit chat UI using the same model/tool loop as chat.py."""
from __future__ import annotations

import json
import os
from html import escape
from pathlib import Path
from uuid import uuid4

import streamlit as st

from chat import now_iso, run_model_tool_loop, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "artifacts/system_prompt.md"
TOOLS = ROOT / "artifacts/tools.yaml"
VERSION_NOTES = {
    "v0": "Baseline starter. Có chỉ dẫn tự đoán khi thiếu thông tin và gửi ngay.",
    "v1": "Hỏi lại khi thiếu tài khoản hoặc URL, thay vì tự đoán.",
    "v2": "Giữ cải tiến v1 và hỏi xác nhận trước khi gửi Telegram.",
    "v3": "Làm rõ lookup: nguồn web, tin tức và ngữ cảnh qua nhiều lượt.",
    "v4-tools": "Bổ sung deduplicate để lọc nguồn trùng URL. Bản demo hiện tại.",
    "working": "Nạp trực tiếp các file prompt/tools đang sửa trong dự án.",
}
VERSION_LABELS = {"v0": "v0 · Baseline", "v1": "v1 · Hỏi lại khi thiếu dữ liệu",
                  "v2": "v2 · Xác nhận trước khi gửi", "v3": "v3 · Tìm đúng nguồn web",
                  "v4-tools": "v4-tools · Thêm lọc nguồn trùng", "working": "Bản đang sửa"}
PROVIDERS = {
    "openrouter": ("OPENROUTER_API_KEY", "openai/gpt-4o-mini"),
    "openai": ("OPENAI_API_KEY", "gpt-4o-mini"),
    "anthropic": ("ANTHROPIC_API_KEY", ""),
    "gemini": ("GEMINI_API_KEY", ""),
    "ollama": (None, "qwen2.5:7b"),
}
EXAMPLES = [
    "Tìm 5 tin về AI hôm nay trên web, kèm liên kết nguồn.",
    "Tóm tắt 5 tweet mới nhất giúp mình.",
    'Lọc trùng hai nguồn này, giữ nguồn đầu tiên: [{"title":"AI report","url":"https://example.org/ai?utm_source=demo"},{"title":"Bản trùng","url":"https://example.org/ai"}].',
]


def version_options() -> list[str]:
    return [version for version in VERSION_NOTES if version == "working" or
            all((ROOT / "artifacts/snapshots" / version / name).is_file()
                for name in ["system_prompt.md", "tools.yaml"])]


def artifact_paths(version: str) -> tuple[Path, Path]:
    if version not in version_options():
        raise ValueError("Unknown or incomplete version snapshot")
    if version == "working":
        return PROMPT, TOOLS
    directory = ROOT / "artifacts/snapshots" / version
    return directory / "system_prompt.md", directory / "tools.yaml"


def reset_conversation() -> None:
    for key in ["conversation", "suggested_prompt", "save_error"]:
        st.session_state.pop(key, None)


def current_version() -> str:
    """Use a run label only when both artifact hashes match the current files."""
    current = build_artifact_version("current", PROMPT, TOOLS)
    for path in sorted((ROOT / "runs").glob("*.json"), reverse=True):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
            if (run.get("prompt_hash") == current.prompt_hash
                    and run.get("tools_hash") == current.tools_hash):
                return run["version"]
        except (OSError, ValueError, KeyError):
            continue
    return "working"


def new_conversation(provider_name: str, model: str, version: str, rounds: int) -> dict:
    provider = make_provider(provider_name)
    prompt_path, tools_path = artifact_paths(version)
    artifact = build_artifact_version(version, prompt_path, tools_path)
    transcript_id = f"{artifact.version}_ui_{uuid4().hex}"
    # A UUID filename keeps the user-editable version label out of filesystem paths.
    path = ROOT / "transcripts" / f"ui_{uuid4().hex}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "source": "streamlit",
        "provider": provider_name,
        "model": model or getattr(provider, "default_model", None),
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": 8,
        "max_tool_rounds": rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return {
        "provider": provider,
        "model": model or None,
        "prompt": prompt_path.read_text(encoding="utf-8"),
        "tools": to_openai_tools(load_tool_declarations(tools_path)),
        "snapshot_selection": version,
        "history": [],
        "path": path,
        "transcript": transcript,
    }


def render_turn(turn: dict) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant", avatar="🔎"):
        if turn["status"] == "provider_error":
            st.error(turn["assistant_text"])
        else:
            st.markdown(turn.get("assistant_text") or "Chưa có câu trả lời.")
        if turn["status"] == "waiting_for_user":
            st.caption("Đang chờ bạn bổ sung thông tin hoặc xác nhận ở ô chat bên dưới.")
        elif turn["status"] == "max_tool_rounds":
            st.warning("Đã đạt giới hạn gọi tool. Bạn có thể thu hẹp yêu cầu và thử lại.")
        events = turn.get("tool_events", [])
        if events:
            with st.expander(f"Xem {len(events)} lần gọi tool"):
                for event in events:
                    st.markdown(f"**{event['tool']}**")
                    st.json(event)


def main() -> None:
    st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="centered")
    if st.session_state.get("save_error"):
        st.warning("Chưa lưu được transcript trên máy. Bạn vẫn có thể tải JSON từ thanh bên.")
    st.markdown(f"<style>{(ROOT / 'assets/ui.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    conversation = st.session_state.get("conversation")
    if conversation and "snapshot_selection" not in conversation:
        reset_conversation()
        conversation = None
    active = conversation is not None
    options = version_options()
    if st.session_state.get("artifact_choice") not in options:
        detected = current_version()
        st.session_state["artifact_choice"] = detected if detected in options else "working"

    with st.sidebar:
        st.markdown('<div class="brand"><div class="brand-mark">⌕</div><div><div class="brand-name">Research Agent</div><div class="brand-note">YOUR RESEARCH WORKSPACE</div></div></div>', unsafe_allow_html=True)
        if st.button("＋ Cuộc trò chuyện mới", type="primary", use_container_width=True):
            reset_conversation()
            st.rerun()
        st.markdown('<div class="section-label">KHÔNG GIAN LÀM VIỆC</div>', unsafe_allow_html=True)
        version = st.selectbox("Phiên bản agent", options, key="artifact_choice",
                               format_func=lambda value: VERSION_LABELS.get(value, value),
                               on_change=reset_conversation)
        st.markdown(f'<div class="version-note">{escape(VERSION_NOTES[version])}</div>', unsafe_allow_html=True)
        st.caption("Đổi phiên bản sẽ bắt đầu hội thoại mới. Transcript cũ vẫn được giữ.")
        with st.expander("Cấu hình nâng cao"):
            provider_name = st.selectbox("Provider", list(PROVIDERS), disabled=active, key="provider")
            model = st.text_input("Model (để trống dùng mặc định)", disabled=active, key="model",
                                  placeholder=PROVIDERS[provider_name][1] or "Model mặc định của provider")
            rounds = st.slider("Số vòng tool tối đa mỗi lượt", 1, 8, 4, disabled=active, key="rounds")

        with st.expander("Kết nối dịch vụ"):
            key_name, _ = PROVIDERS[provider_name]
            if key_name:
                st.caption("Model: " + ("đã có API key" if os.getenv(key_name) else "chưa có API key"))
            else:
                st.caption("Model local: cần Ollama đang chạy.")
            for label, keys in [
                ("Tìm web", ["TAVILY_API_KEY"]),
                ("Đọc URL", ["FIRECRAWL_API_KEY"]),
                ("X/Twitter", ["RAPIDAPI_KEY"]),
                ("Telegram", ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]),
            ]:
                st.caption(f"{label}: " + ("đã cấu hình" if all(os.getenv(k) for k in keys) else "chưa cấu hình"))
            st.caption("Trạng thái chỉ kiểm tra cấu hình, chưa kiểm tra kết nối.")

        if conversation:
            transcript = conversation["transcript"]
            st.caption(f"Phiên bản: {transcript['version']} · {transcript['model']}")
            with st.expander("Thông tin phiên chạy"):
                st.code(transcript["artifact_version"], language=None)
            if transcript["turns"]:
                st.download_button(
                    "Tải transcript JSON",
                    data=json.dumps(transcript, ensure_ascii=False, indent=2, default=str),
                    file_name=conversation["path"].name,
                    mime="application/json",
                    use_container_width=True,
                )

    st.markdown('<span class="workspace-badge">RESEARCH WORKSPACE · LOCAL</span>', unsafe_allow_html=True)
    if active:
        st.markdown('<div class="hero"><div class="eyebrow">CUỘC TRÒ CHUYỆN CỦA BẠN</div><h1>Cùng đọc <span>sâu hơn.</span></h1></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="hero"><div class="eyebrow">TÒ MÒ LÀ ĐIỂM KHỞI ĐẦU</div><h1>Từ câu hỏi đến<br><span>thông tin có nguồn.</span></h1><p>Tìm tin mới, đọc sâu tài liệu và kết nối thông tin.<br>Một không gian gọn gàng cho những điều bạn muốn hiểu rõ.</p></div>', unsafe_allow_html=True)
        _, selected_tools = artifact_paths(version)
        columns = st.columns(3)
        columns[0].metric("Phiên bản đang chọn", version)
        columns[1].metric("Công cụ sẵn có", len(load_tool_declarations(selected_tools)))
        columns[2].metric("Bằng chứng hội thoại", "JSON")
    if not conversation:
        st.markdown('<div class="section-label">BẮT ĐẦU TỪ MỘT Ý TƯỞNG</div>', unsafe_allow_html=True)
        cards = [("🌐", "Theo dõi tin mới", "Khám phá những tin AI đáng chú ý hôm nay, kèm nguồn để đọc thêm.", "Tìm tin AI", EXAMPLES[0]),
                 ("💬", "Đọc dòng thảo luận", "Tìm hiểu các bài đăng mới nhất. Agent sẽ hỏi nếu bạn chưa chọn tài khoản.", "Thử hỏi lại", EXAMPLES[1])]
        if version in {"v4-tools", "working"}:
            cards.append(("🧩", "Giữ nguồn, bỏ trùng", "Làm gọn danh sách nguồn trước khi tổng hợp bản tin.", "Lọc nguồn trùng", EXAMPLES[2]))
        else:
            cards.append(("📄", "Đọc sâu tài liệu", "Tìm nghiên cứu trên arXiv để mở rộng góc nhìn về một chủ đề.", "Tìm nghiên cứu", "Tìm 3 bài báo trên arXiv về retrieval augmented generation."))
        for column, (icon, title, description, label, example) in zip(st.columns(3), cards):
            with column, st.container(border=True):
                st.markdown(f'<div class="card-icon">{icon}</div><div class="card-title">{title}</div><div class="card-description">{description}</div>', unsafe_allow_html=True)
                if st.button(label + " →", key="example_" + title, use_container_width=True):
                    st.session_state["suggested_prompt"] = example
        st.markdown('<div class="footnote">Câu trả lời tốt bắt đầu bằng nguồn rõ ràng. Luôn kiểm tra thông tin trước khi sử dụng.</div>', unsafe_allow_html=True)

    if conversation:
        for turn in conversation["transcript"]["turns"]:
            render_turn(turn)

    prompt = st.chat_input("Nhập câu hỏi hoặc trả lời yêu cầu làm rõ…")
    prompt = prompt or st.session_state.pop("suggested_prompt", None)
    if not prompt or not prompt.strip():
        return
    prompt = prompt.strip()
    if not conversation:
        try:
            conversation = new_conversation(provider_name, model.strip(), version.strip() or "working", rounds)
        except Exception as exc:
            st.error(f"Không thể khởi tạo agent ({type(exc).__name__}). Kiểm tra cấu hình dự án.")
            return
        st.session_state["conversation"] = conversation

    transcript = conversation["transcript"]
    turn = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": prompt,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    with st.spinner("Agent đang tìm và xử lý thông tin…"):
        try:
            result = run_model_tool_loop(
                provider=conversation["provider"],
                messages=[
                    {"role": "system", "content": conversation["prompt"]},
                    *trim_history(conversation["history"], transcript["history_window"]),
                    {"role": "user", "content": prompt},
                ],
                tools=conversation["tools"],
                model=conversation["model"],
                max_tool_rounds=transcript["max_tool_rounds"],
            )
            turn.update(result)
            conversation["history"].extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": result["assistant_text"]},
            ])
        except Exception as exc:
            turn.update(status="provider_error", error_type=type(exc).__name__,
                        assistant_text=f"Không thể hoàn tất yêu cầu ({type(exc).__name__}). "
                        "Kiểm tra kết nối, API key và tên model rồi gửi lại câu hỏi.")
    turn["ended_at"] = now_iso()
    transcript["turns"].append(turn)
    try:
        write_transcript(conversation["path"], transcript)
        st.session_state.pop("save_error", None)
    except OSError:
        st.session_state["save_error"] = True
    st.rerun()


if __name__ == "__main__":
    main()
