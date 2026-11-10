"""Run real evals or a three-turn CLI demo without enabling Telegram delivery."""
from __future__ import annotations

import argparse
import builtins
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["base", "group", "chat"])
    parser.add_argument("--version", default="v4-tools")
    parser.add_argument("--model", default="openai/gpt-4o-mini")
    args = parser.parse_args()

    # Both modules load .env on import. Disable delivery AFTER those imports:
    # evaluation can observe send guardrails without publishing anything.
    import run_eval
    import chat

    os.environ.pop("TELEGRAM_BOT_TOKEN", None)
    os.environ.pop("TELEGRAM_CHAT_ID", None)
    common = ["--provider", "openrouter", "--model", args.model, "--version", args.version]
    if args.stage in {"base", "group"}:
        sys.argv = ["run_eval.py", *common, "--suite", args.stage,
                    "--eval-cases", str(ROOT / "data" / f"eval_{args.stage}.json")]
        run_eval.main()
        return

    # These are scripted user inputs; model responses and tool results are real.
    # Running chat.main preserves the required CLI transcript format.
    prompts = iter([
        "Lọc trùng các nguồn giúp tôi.",
        'Chỉ lọc trùng danh sách này, không tìm web: [{"title":"AI report",'
        '"url":"https://example.org/ai?utm_source=demo"},{"title":"AI duplicate",'
        '"url":"https://example.org/ai"},{"title":"Robotics report",'
        '"url":"https://example.org/robotics"}]. Giữ nguồn đầu tiên.',
        "Trình bày các nguồn duy nhất vừa có thành bullets, kèm URL. Không tìm thêm nguồn.",
        "/exit",
    ])
    original_input = builtins.input

    def demo_input(label: str = "") -> str:
        message = next(prompts, "/exit")
        print(label + message)
        return message

    try:
        builtins.input = demo_input
        sys.argv = ["chat.py", *common]
        chat.main()
    finally:
        builtins.input = original_input


if __name__ == "__main__":
    main()
