from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def _url_key(url: str, mode: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError("Each non-empty url must be an absolute HTTP(S) URL")
    if parts.username is not None or parts.password is not None:
        raise ValueError("URLs must not contain credentials")
    port = parts.port  # Validate ports even in exact_url mode.
    if mode == "exact_url":
        return url.strip()
    host = parts.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    if port is not None and (parts.scheme.lower(), port) not in {("http", 80), ("https", 443)}:
        host += f":{port}"
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
    return urlunsplit((parts.scheme.lower(), host, parts.path or "/", urlencode(query), ""))


def deduplicate_items(items: list[dict[str, Any]] | None = None, mode: str = "normalized_url") -> dict[str, Any]:
    """Keep the first item for each URL; do not infer duplicates from titles."""
    try:
        if mode not in {"exact_url", "normalized_url"}:
            raise ValueError("mode must be exact_url or normalized_url")
        if items is None:
            items = []
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise ValueError("items must be a list of objects")
        kept: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in items:
            url = item.get("url")
            if url is None or url == "":
                kept.append(dict(item))
                continue
            if not isinstance(url, str):
                raise ValueError("url must be a string or null")
            key = _url_key(url, mode)
            if key not in seen:
                seen.add(key)
                kept.append(dict(item))
        return {"tool": "deduplicate", "mode": mode, "items": kept,
                "input_count": len(items), "item_count": len(kept),
                "duplicates_removed": len(items) - len(kept)}
    except (TypeError, ValueError) as exc:
        return {"tool": "deduplicate", "error": type(exc).__name__, "message": str(exc)}
