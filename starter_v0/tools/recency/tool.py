from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any


_DATE_FORMATS = (
    "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601 có múi giờ (kể cả dạng Twitter/X).
    "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d",  # ISO 8601 / ISO đơn giản không múi giờ.
    "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y",  # RFC 822 (feed RSS).
    "%d/%m/%Y", "%m/%d/%Y",  # Ngày rút gọn.
)

_RANGES = {  # name -> số ngày lookback; None = chỉ xếp, không lọc.
    "today": 1,
    "week": 7,
    "month": 31,
    "any": None,
}


def _parse_date(value: Any) -> datetime | None:
    """Parse trường date của item về datetime theo UTC; None nếu thiếu/sai."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+0000")
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(text, fmt)
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    if text.isdigit():  # Unix timestamp (giây hoặc mili-giây).
        seconds = int(text) / (1000 if len(text) > 11 else 1)
        return datetime.fromtimestamp(seconds, tz=UTC)
    return None


def _cutoff(within: str) -> timedelta | None:
    days = _RANGES[within]
    return timedelta(days=days) if days else None


def sort_recency(items: list[dict[str, Any]] | None = None, within: str = "any", max_items: int = 10) -> dict[str, Any]:
    """Lọc items theo khung thời gian và xếp mới nhất lên trước; item thiếu ngày dồn xuống cuối."""
    if not isinstance(items, list):
        return {"tool": "sort_recency", "error": "invalid_input", "message": "items must be an array of objects with a date"}
    try:
        max_items_int = int(max_items)
    except (TypeError, ValueError):
        max_items_int = 10
    if max_items_int <= 0:
        max_items_int = 10
    now = datetime.now(UTC)
    if within not in _RANGES:
        return {"tool": "sort_recency", "error": "invalid_within", "message": f"within must be one of {sorted(_RANGES)}"}
    cutoff = _cutoff(within)
    future_guard = timedelta(minutes=5)  # Cho phép sai số đồng hồ nhỏ, chặn mốc quá tương lai.
    in_range: list[tuple[datetime, int, dict[str, Any]]] = []
    undated: list[dict[str, Any]] = []
    out_of_range = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            undated.append(item)
            continue
        parsed = _parse_date(item.get("date"))
        if parsed is None:
            undated.append(item)
        elif parsed > now + future_guard:
            undated.append(item)  # Ngày ở tương lai: coi như dữ liệu lỗi, không bịa lại.
        elif cutoff is not None and parsed < now - cutoff:
            out_of_range += 1
        else:
            in_range.append((parsed, index, item))
    in_range.sort(key=lambda entry: (entry[0], -entry[1]), reverse=True)  # Mới nhất trước; cùng mốc thì giữ thứ tự đầu vào.
    ordered = [dict(item) for _, _, item in in_range] + [dict(item) for item in undated if isinstance(item, dict)]
    output = ordered[:max_items_int]
    result = {
        "tool": "sort_recency", "items": output,
        "input_count": len(items), "item_count": len(output),
        "within": within, "out_of_range_count": out_of_range,
        "undated_count": len(undated), "newest_first": True,
    }
    return result
