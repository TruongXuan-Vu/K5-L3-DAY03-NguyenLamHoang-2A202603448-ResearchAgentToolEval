"""Streamlit chat UI using the same model/tool loop as chat.py."""
from __future__ import annotations

import json
import os
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
    "Tìm 3 bài báo trên arXiv về retrieval augmented generation.",
]


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
    artifact = build_artifact_version(version, PROMPT, TOOLS)
    transcript_id = f"{artifact.version}_ui_{uuid4().hex}"
    # A UUID filename keeps the user-editable version label out of filesystem paths.
    path = ROOT / "transcripts" / f"ui_{uuid4().hex}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "source": "streamlit",
        "provider": provider_name,
        "model": model or getattr(provider, "default_model", None),
        "system_prompt": str(PROMPT),
        "tools": str(TOOLS),
        "history_window": 8,
        "max_tool_rounds": rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return {
        "provider": provider,
        "model": model or None,
        "prompt": PROMPT.read_text(encoding="utf-8"),
        "tools": to_openai_tools(load_tool_declarations(TOOLS)),
        "history": [],
        "path": path,
        "transcript": transcript,
    }


def render_turn(turn: dict) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
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
    st.markdown("<style>.block-container{max-width:960px;padding-top:2rem}"
                "[data-testid=stSidebar]{border-right:1px solid #dce3ed}"
                "</style>", unsafe_allow_html=True)
    conversation = st.session_state.get("conversation")
    active = conversation is not None

    with st.sidebar:
        st.title("🔎 Research Agent")
        st.caption("Tìm nguồn · Đọc sâu · Tổng hợp")
        provider_name = st.selectbox("Provider", list(PROVIDERS), disabled=active, key="provider")
        model = st.text_input("Model (để trống dùng mặc định)", disabled=active, key="model",
                              placeholder=PROVIDERS[provider_name][1] or "Model mặc định của provider")
        version = st.text_input("Nhãn phiên bản", value=current_version(), disabled=active, key="version")
        rounds = st.slider("Số vòng tool tối đa mỗi lượt", 1, 8, 4, disabled=active, key="rounds")
        if st.button("＋ Cuộc trò chuyện mới", use_container_width=True):
            st.session_state.pop("conversation", None)
            st.rerun()

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

    st.title("Bạn muốn tìm hiểu điều gì?")
    st.write("Tìm tin, đọc tài liệu và tổng hợp thông tin cùng nguồn tham khảo.")
    if not conversation:
        st.caption("Bắt đầu bằng một câu hỏi mẫu hoặc nhập yêu cầu của bạn.")
        for example in EXAMPLES:
            if st.button(example, use_container_width=True):
                st.session_state["suggested_prompt"] = example

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
