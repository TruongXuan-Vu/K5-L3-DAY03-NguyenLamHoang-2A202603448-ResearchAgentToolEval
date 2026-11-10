from copy import deepcopy

import pytest

from tools import TOOL_FUNCTIONS

deduplicate = TOOL_FUNCTIONS["deduplicate"]


def test_normalized_urls_keep_first_item_and_leave_input_unchanged():
    items = [{"title": "First", "url": "https://EXAMPLE.com:443/a?utm_source=x&id=7#part", "summary": "keep"},
             {"title": "Copy", "url": "https://example.com/a?id=7"},
             {"title": "Other", "url": "https://example.com/b"}]
    original = deepcopy(items)
    result = deduplicate(items)
    assert result["items"] == [original[0], original[2]]
    assert result["duplicates_removed"] == 1
    assert (result["input_count"], result["item_count"]) == (3, 2)
    assert items == original


def test_exact_mode_keeps_tracking_variants_and_removes_exact_duplicate():
    urls = ["https://example.com/a?utm_source=x", "https://example.com/a", "https://example.com/a"]
    result = deduplicate([{"url": u} for u in urls], "exact_url")
    assert [i["url"] for i in result["items"]] == urls[:2]


def test_meaningful_query_path_and_scheme_differences_are_preserved():
    urls = ["https://example.com/a?id=1", "https://example.com/a?id=2",
            "https://example.com/A?id=1", "http://example.com/a?id=1",
            "https://example.com/a/?id=1"]
    assert deduplicate([{"url": u} for u in urls])["item_count"] == 5


def test_items_without_urls_are_kept_even_when_titles_match():
    items = [{"title": "Same"}, {"title": "Same", "url": ""}, {"url": None}]
    assert deduplicate(items)["items"] == items


def test_empty_input_returns_empty_result():
    assert deduplicate([])["items"] == []
    assert deduplicate()["duplicates_removed"] == 0


@pytest.mark.parametrize("items,mode", [
    ("bad", "normalized_url"), (["bad"], "normalized_url"),
    ([{"url": 123}], "normalized_url"), ([{"url": "not-a-url"}], "normalized_url"),
    ([{"url": "file:///tmp/a"}], "normalized_url"),
    ([{"url": "https://user:password@example.com/a"}], "normalized_url"),
    ([{"url": "https://example.com:invalid/a"}], "exact_url"),
    ([], "invalid"), ([], []),
])
def test_bad_model_arguments_return_error_dict_without_partial_items(items, mode):
    result = deduplicate(items, mode)
    assert result["error"] in {"ValueError", "TypeError"}
    assert "items" not in result


def test_normalized_mode_is_idempotent():
    items = [{"url": "https://example.com/a?gclid=abc#x"}, {"url": "https://example.com/a"}]
    first = deduplicate(items)
    second = deduplicate(first["items"])
    assert second["items"] == first["items"]
    assert second["duplicates_removed"] == 0
