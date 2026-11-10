"""Unit tests cho tool cluster_stories (gộp nguồn trùng chuyện theo tiêu đề).

Offline hoàn toàn: tool chỉ xử lý dữ liệu đã có, không gọi mạng.
Làm theo pattern của các test deduplicate trong test_tools_todo.py.
"""
from __future__ import annotations

import pytest

from tools import TOOL_FUNCTIONS


def test_cluster_stories_merges_same_story_from_web_and_x() -> None:
    items = [
        {"title": "OpenAI ra mắt GPT-5 hôm nay", "url": "https://example.org/gpt5", "source": "example.org", "score": 0.9},
        {"title": "gpt-5 openai ra mắt", "url": "https://x.com/sama/status/1", "source": "@sama"},
    ]
    before = [dict(item) for item in items]
    result = TOOL_FUNCTIONS["cluster_stories"](items=items)
    assert result["item_count"] == 1 and result["merged_count"] == 1
    rep = result["items"][0]
    assert rep["url"] == "https://example.org/gpt5" and rep["story_count"] == 2
    assert rep["also_from"] == [{"source": "@sama", "url": "https://x.com/sama/status/1", "title": "gpt-5 openai ra mắt"}]
    assert items == before  # Không sửa items đầu vào.


def test_cluster_stories_keeps_distinct_stories_separate() -> None:
    items = [{"title": "Elon Musk mua Twitter", "url": "https://example.org/musk"},
             {"title": "Tin AI mới nhất hôm nay", "url": "https://example.org/ai"}]
    result = TOOL_FUNCTIONS["cluster_stories"](items=items)
    assert result["item_count"] == 2 and result["merged_count"] == 0
    assert result["items"][0]["title"] == "Elon Musk mua Twitter"


def test_cluster_stories_folds_diacritics_and_stopwords() -> None:
    items = [{"title": "Tin AI mới nhất hôm nay"}, {"title": "tin ai moi nhat"}]
    result = TOOL_FUNCTIONS["cluster_stories"](items=items)
    assert result["item_count"] == 1 and result["merged_count"] == 1


def test_cluster_stories_prefers_highest_score_representative() -> None:
    items = [
        {"title": "OpenAI ra mắt GPT-5 hôm nay", "source": "@sama"},
        {"title": "gpt-5 openai ra mắt", "source": "example.org", "score": 0.9},
    ]
    result = TOOL_FUNCTIONS["cluster_stories"](items=items)
    assert result["items"][0]["source"] == "example.org"
    # Thứ tự chuyện vẫn theo item đầu tiên xuất hiện, không theo score.


def test_cluster_stories_similarity_threshold_controls_merging() -> None:
    items = [{"title": "OpenAI ra mắt GPT-5"}, {"title": "Google ra mắt Gemini"}]
    default = TOOL_FUNCTIONS["cluster_stories"](items=items)
    assert default["item_count"] == 2  # Jaccard ~0.33 < 0.6: khác chuyện.
    loose = TOOL_FUNCTIONS["cluster_stories"](items=items, similarity=0.3)
    assert loose["item_count"] == 1 and loose["merged_count"] == 1


def test_cluster_stories_max_items_caps_output() -> None:
    words = ["alpha", "beta", "gamma", "delta", "epsilon"]
    items = [{"title": f"Chuyện riêng về chủ đề {word}"} for word in words]
    result = TOOL_FUNCTIONS["cluster_stories"](items=items, max_items=3)
    assert len(result["items"]) == 3 and result["item_count"] == 3 and result["input_count"] == 5
    assert TOOL_FUNCTIONS["cluster_stories"](items=items, max_items=-1)["item_count"] == 3  # Âm → mặc định 10: trả đủ 3 chuyện.


def test_cluster_stories_invalid_items_reported_and_valid_still_clustered() -> None:
    items = [{"url": "https://example.org/no-title"}, {"title": "  "}, "text", 5,
             {"title": "Tin AI mới nhất"}, {"title": "tin ai moi nhat"}]
    result = TOOL_FUNCTIONS["cluster_stories"](items=items)
    assert result["error"] == "invalid_items" and len(result["invalid_items"]) == 4
    assert result["item_count"] == 1 and result["input_count"] == 6


@pytest.mark.parametrize("items", [None, "", "https://example.org", {}, 5])
def test_cluster_stories_bad_input_returns_error(items) -> None:
    assert TOOL_FUNCTIONS["cluster_stories"](items=items)["error"] == "invalid_input"


def test_cluster_stories_empty_items_returns_zero_stories() -> None:
    result = TOOL_FUNCTIONS["cluster_stories"](items=[])
    assert result["items"] == [] and result["item_count"] == 0 and "error" not in result
