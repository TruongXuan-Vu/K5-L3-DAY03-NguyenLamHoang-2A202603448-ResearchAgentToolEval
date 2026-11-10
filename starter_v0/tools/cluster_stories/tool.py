from __future__ import annotations

from typing import Any

from tools._shared import terms


def _title_terms(item: Any) -> set[str] | None:
    """Tokenize the item title; None when the item is unusable for clustering."""
    if not isinstance(item, dict):
        return None
    title = item.get("title")
    if not isinstance(title, str) or not title.strip():
        return None
    return terms(title)


def _score(item: dict[str, Any]) -> float:
    score = item.get("score")
    return score if isinstance(score, (int, float)) else float("-inf")


def cluster_stories(items: list[dict[str, Any]] | None = None, max_items: int = 10, similarity: float = 0.6) -> dict[str, Any]:
    """Group items that cover the same story by title similarity; keep one representative per story."""
    if not isinstance(items, list):
        return {"tool": "cluster_stories", "error": "invalid_input", "message": "items must be an array of objects with a title"}
    try:
        threshold = float(similarity)
    except (TypeError, ValueError):
        threshold = 0.6
    threshold = min(max(threshold, 0.0), 1.0)
    clusters: list[dict[str, Any]] = []  # {"terms": set, "items": [item, ...]}
    invalid: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        title_terms = _title_terms(item)
        if title_terms is None:
            invalid.append({"index": index, "message": "Each item must be an object with a non-empty title"})
            continue
        for cluster in clusters:
            union = title_terms | cluster["terms"]
            if union and len(title_terms & cluster["terms"]) / len(union) >= threshold:
                cluster["items"].append(item)
                cluster["terms"] = cluster["terms"] | title_terms
                break
        else:
            clusters.append({"terms": title_terms, "items": [item]})
    representatives: list[dict[str, Any]] = []
    merged_count = 0
    for cluster in clusters:
        members = cluster["items"]
        merged_count += len(members) - 1
        best = max(members, key=_score)  # Ties keep the first item: max() is stable.
        representative = dict(best)
        representative["story_count"] = len(members)
        if len(members) > 1:
            representative["also_from"] = [
                {"source": member.get("source") or "", "url": member.get("url") or "", "title": member.get("title") or ""}
                for member in members if member is not best
            ]
        representatives.append(representative)
    try:
        max_items_int = int(max_items)
    except (TypeError, ValueError):
        max_items_int = 10
    if max_items_int <= 0:
        max_items_int = 10
    output = representatives[:max_items_int]
    result = {
        "tool": "cluster_stories", "items": output,
        "input_count": len(items), "item_count": len(output),
        "merged_count": merged_count, "invalid_items": invalid,
    }
    if invalid:
        result.update(error="invalid_items", message="Some items have invalid titles; valid items are still clustered")
    return result
