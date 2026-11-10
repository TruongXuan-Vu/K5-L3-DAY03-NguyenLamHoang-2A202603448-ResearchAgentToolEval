---
name: deduplicate
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items, mode]
outputs: [items, input_count, item_count, duplicates_removed, mode]
side_effect: false
---
# deduplicate

Remove duplicate URLs from items already supplied by the user or research tools.
No network, API key, disk write, summarization, or publishing occurs.

- `normalized_url` (default): lowercase scheme/host, remove default port,
  fragments, `utm_*`, `fbclid`, `gclid`. Keep meaningful query parameters,
  their order, path case, and trailing slash. HTTP and HTTPS remain distinct.
- `exact_url`: compare the original URL after trimming surrounding whitespace.
- Keep the first item and its original metadata/URL; preserve input order.
- Keep every item with no URL: titles alone do not prove duplication.
- Invalid modes, item shapes or non-HTTP(S)/credential-bearing URLs return
  an error dictionary; the tool never returns a partially cleaned result.
- Requires an `items` array. If the user provides neither items nor research
  results, ask for the data rather than inventing URLs.

Use when deduplication is explicitly requested or duplicate research results
need cleaning before a digest. Do not use as a search, fetch, or formatting tool.
