from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def _canonical_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Each item must have a non-empty HTTP(S) url")
    value = url.strip()
    if any(char.isspace() for char in value):
        raise ValueError("URL must not contain whitespace")
    parts = urlsplit(value)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError("Only absolute HTTP(S) URLs are supported")
    if parts.username is not None or parts.password is not None:
        raise ValueError("URLs with embedded credentials are not supported")
    host = parts.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    port = parts.port  # Also validates malformed or out-of-range ports.
    if port is not None and (parts.scheme.lower(), port) not in {("http", 80), ("https", 443)}:
        host += f":{port}"
    params = [(key, val) for key, val in parse_qsl(parts.query, keep_blank_values=True)
              if not key.lower().startswith("utm_") and key.lower() not in {"fbclid", "gclid"}]
    return urlunsplit((parts.scheme.lower(), host, parts.path or "/", urlencode(params), ""))


def deduplicate_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Remove duplicate source URLs locally; preserve first item and input order."""
    if not isinstance(items, list):
        return {"tool": "deduplicate", "error": "invalid_input", "message": "items must be an array of objects with a url"}
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    removed: list[int] = []
    invalid: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        try:
            if not isinstance(item, dict):
                raise ValueError("Each item must be an object with a url")
            canonical = _canonical_url(item.get("url"))
        except (TypeError, ValueError) as exc:
            invalid.append({"index": index, "message": str(exc)})
            continue
        if canonical in seen:
            removed.append(index)
            continue
        seen.add(canonical)
        unique.append(dict(item))
    result = {
        "tool": "deduplicate", "items": unique, "input_count": len(items),
        "item_count": len(unique), "duplicate_count": len(removed),
        "removed_indices": removed, "invalid_items": invalid,
    }
    if invalid:
        result.update(error="invalid_items", message="Some items have invalid URLs; valid unique items are returned")
    return result
