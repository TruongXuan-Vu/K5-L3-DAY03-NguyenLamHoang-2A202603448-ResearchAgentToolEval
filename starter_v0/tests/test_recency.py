"""Unit tests cho tool recency (lọc + xếp nguồn theo thời gian đăng).

Offline hoàn toàn: ngày trong test tính tương đối so với datetime.now() để
không phụ thuộc thời điểm chạy. Pattern làm theo test_cluster_stories.py.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from tools import TOOL_FUNCTIONS


def _iso(delta: timedelta) -> str:
    return (datetime.now(UTC) + delta).strftime("%Y-%m-%dT%H:%M:%S+0000")


def test_recency_sorts_newest_first_and_keeps_tie_order() -> None:
    items = [{"title": "cũ", "date": _iso(timedelta(days=-3)), "url": "https://example.org/old"},
             {"title": "mới nhất", "date": _iso(timedelta(hours=-1)), "url": "https://example.org/new"},
             {"title": "mới vừa", "date": _iso(timedelta(hours=-2)), "url": "https://example.org/mid"}]
    before = [dict(item) for item in items]
    result = TOOL_FUNCTIONS["recency"](items=items)
    assert [row["title"] for row in result["items"]] == ["mới nhất", "mới vừa", "cũ"]
    assert result["newest_first"] is True and result["out_of_range_count"] == 0 and result["undated_count"] == 0
    assert items == before  # Không sửa items đầu vào.


def test_recency_within_week_drops_old_items() -> None:
    items = [{"title": "tin hôm qua", "date": _iso(timedelta(days=-1))},
             {"title": "tin tháng trước", "date": _iso(timedelta(days=-40))}]
    result = TOOL_FUNCTIONS["recency"](items=items, within="week")
    assert [row["title"] for row in result["items"]] == ["tin hôm qua"]
    assert result["out_of_range_count"] == 1 and result["within"] == "week"


def test_recency_today_keeps_only_last_24_hours() -> None:
    items = [{"title": "vừa nãy", "date": _iso(timedelta(hours=-2))},
             {"title": "hôm trước", "date": _iso(timedelta(days=-2))}]
    result = TOOL_FUNCTIONS["recency"](items=items, within="today")
    assert [row["title"] for row in result["items"]] == ["vừa nãy"]
    assert result["out_of_range_count"] == 1


def test_recency_undated_and_future_items_go_last_without_fabricating() -> None:
    items = [{"title": "thiếu ngày"},
             {"title": "ngày tương lai", "date": _iso(timedelta(days=3))},
             {"title": "có ngày", "date": _iso(timedelta(hours=-1))}]
    result = TOOL_FUNCTIONS["recency"](items=items)
    assert result["undated_count"] == 2
    assert [row["title"] for row in result["items"]] == ["có ngày", "thiếu ngày", "ngày tương lai"]


def test_recency_parses_mixed_date_formats() -> None:
    items = [
        {"title": "iso-z", "date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")},
        {"title": "rfc822", "date": datetime.now(UTC).strftime("%a, %d %b %Y %H:%M:%S +0000")},
        {"title": "dd/mm/yyyy", "date": datetime.now(UTC).strftime("%d/%m/%Y")},
        {"title": "unix-ms", "date": str(int(datetime.now(UTC).timestamp() * 1000))},
    ]
    result = TOOL_FUNCTIONS["recency"](items=items)
    assert result["undated_count"] == 0 and result["item_count"] == 4


def test_recency_max_items_caps_output() -> None:
    items = [{"title": f"tin {i}", "date": _iso(timedelta(hours=-1 - i))} for i in range(5)]
    result = TOOL_FUNCTIONS["recency"](items=items, max_items=3)
    assert len(result["items"]) == 3 and result["item_count"] == 3 and result["input_count"] == 5
    assert result["items"][0]["title"] == "tin 0"  # Vẫn xếp mới nhất trước sau khi cắt.
    assert TOOL_FUNCTIONS["recency"](items=items, max_items=-1)["item_count"] == 5  # Âm → mặc định.


def test_recency_bad_input_and_bad_within_return_errors() -> None:
    assert TOOL_FUNCTIONS["recency"](items="not-a-list")["error"] == "invalid_input"
    assert TOOL_FUNCTIONS["recency"](items=[], within="year")["error"] == "invalid_within"


def test_recency_empty_items_returns_zero_rows() -> None:
    result = TOOL_FUNCTIONS["recency"](items=[])
    assert result["items"] == [] and result["item_count"] == 0 and "error" not in result


def test_recency_within_any_only_sorts_without_dropping() -> None:
    items = [{"title": "mới", "date": _iso(timedelta(hours=-1))},
             {"title": "rất cũ", "date": _iso(timedelta(days=-365))}]
    result = TOOL_FUNCTIONS["recency"](items=items, within="any")
    assert result["item_count"] == 2 and result["out_of_range_count"] == 0
    assert result["items"][0]["title"] == "mới"
