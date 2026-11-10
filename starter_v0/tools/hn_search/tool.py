from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


HN_API_URL = "https://hn.algolia.com/api/v1/search"


def hn_search(query: str = "", max_results: int = 5, tags: str = "story") -> dict[str, Any]:
    """Search Hacker News stories/comments via the Algolia API (no key needed)."""
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query must be a non-empty string")
        try:
            max_results = int(max_results)
        except (TypeError, ValueError):
            max_results = 5
        max_results = max(1, min(max_results, 20))
        tags = tags if tags in {"story", "comment"} else "story"

        response = requests.get(
            HN_API_URL,
            params={"query": query, "tags": tags, "hitsPerPage": max_results},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for hit in data.get("hits", [])[:max_results]:
            items.append({
                "title": hit.get("title") or hit.get("story_title") or "",
                "author": hit.get("author", ""),
                "points": hit.get("points", 0),
                "num_comments": hit.get("num_comments", 0),
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                "published": hit.get("created_at", ""),
                "source": "news.ycombinator.com",
            })
        return {
            "tool": "hn_search",
            "query": query,
            "tags": tags,
            "total_results": data.get("nbHits"),
            "items": items,
        }
    except Exception as exc:
        return err("hn_search", exc)
