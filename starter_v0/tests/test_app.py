"""Offline interaction tests for the Streamlit UI (no real model calls)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from providers.base import ModelResponse, ToolCall

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def ui(monkeypatch, tmp_path):
    # Import app helpers without reading real service credentials in the test.
    env = tmp_path / "empty.env"
    env.write_text("", encoding="utf-8")
    monkeypatch.setenv("DAY04_ENV_FILE", str(env))
    import chat

    saved = []
    original = chat.write_transcript

    def save(path, transcript):
        target = tmp_path / path.name
        original(target, transcript)
        saved.append(target)

    monkeypatch.setattr(chat, "write_transcript", save)
    return AppTest.from_file(str(ROOT / "app.py"), default_timeout=15), saved


def test_start_page_does_not_call_provider(ui, monkeypatch):
    import providers

    def forbidden(*args, **kwargs):
        raise AssertionError("Opening the UI must not call the model")

    monkeypatch.setattr(providers, "make_provider", forbidden)
    app, saved = ui
    app.run()
    assert not app.exception
    assert len(app.chat_input) == 1
    assert len(app.chat_message) == 0
    assert not saved


def test_clarification_then_answer_retains_history_and_writes_transcript(ui, monkeypatch):
    import providers

    class FakeProvider:
        default_model = "offline-model"

        def __init__(self):
            self.messages = []

        def complete(self, messages, tools, **kwargs):
            self.messages.append(messages)
            if len(self.messages) == 1:
                return ModelResponse(tool_calls=[ToolCall("clarify", {
                    "question": "Bạn muốn theo dõi tài khoản nào?", "response_type": "text",
                })])
            assert any(m["content"] == "Tóm tắt tweet giúp mình" for m in messages)
            assert any("tài khoản nào" in m["content"] for m in messages)
            assert messages[-1]["content"] == "Của @elonmusk"
            return ModelResponse(text="Đã nhận tài khoản @elonmusk.")

    provider = FakeProvider()
    monkeypatch.setattr(providers, "make_provider", lambda name: provider)
    app, saved = ui
    app.run().chat_input[0].set_value("Tóm tắt tweet giúp mình").run()
    assert not app.exception
    assert app.session_state["conversation"]["transcript"]["turns"][0]["status"] == "waiting_for_user"
    app.chat_input[0].set_value("Của @elonmusk").run()
    assert not app.exception
    assert len(app.chat_message) == 4
    transcript = json.loads(saved[-1].read_text(encoding="utf-8"))
    assert len(transcript["turns"]) == 2
    assert transcript["turns"][0]["tool_events"][0]["tool"] == "clarify"
    assert transcript["turns"][1]["assistant_text"] == "Đã nhận tài khoản @elonmusk."
    assert transcript["prompt_hash"] and transcript["tools_hash"]
    assert transcript["model"] == "offline-model"
    app.run()
    assert len(provider.messages) == 2, "A normal rerun must not repeat a model call"


def test_provider_error_is_saved_and_new_conversation_clears_history(ui, monkeypatch):
    import providers

    class BrokenProvider:
        default_model = "offline-model"

        def complete(self, *args, **kwargs):
            raise ConnectionError("private credential must not appear")

    monkeypatch.setattr(providers, "make_provider", lambda name: BrokenProvider())
    app, saved = ui
    app.run().chat_input[0].set_value("Tìm tin AI").run()
    assert not app.exception
    assert app.error
    assert "private credential" not in app.error[0].value
    transcript = json.loads(saved[-1].read_text(encoding="utf-8"))
    assert transcript["turns"][0]["status"] == "provider_error"
    assert not app.session_state["conversation"]["history"]
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert len(app.chat_message) == 0
    assert saved[-1].exists()


def test_separate_browser_sessions_keep_history_and_transcripts_separate(ui, monkeypatch):
    import providers

    class EchoProvider:
        default_model = "offline-model"

        def complete(self, messages, tools, **kwargs):
            return ModelResponse(text=messages[-1]["content"])

    monkeypatch.setattr(providers, "make_provider", lambda name: EchoProvider())
    first, saved = ui
    second = AppTest.from_file(str(ROOT / "app.py"), default_timeout=15)
    first.run().chat_input[0].set_value("Nghiên cứu AI").run()
    second.run().chat_input[0].set_value("Nghiên cứu robotics").run()
    assert not first.exception and not second.exception
    assert first.session_state["conversation"]["path"] != second.session_state["conversation"]["path"]
    first_turns = first.session_state["conversation"]["transcript"]["turns"]
    second_turns = second.session_state["conversation"]["transcript"]["turns"]
    assert len(first_turns) == len(second_turns) == 1
    assert first_turns[0]["user"] == "Nghiên cứu AI"
    assert second_turns[0]["user"] == "Nghiên cứu robotics"
    assert len(set(saved)) == 2
