---
name: hn_search
track: bonus
kind: live_api
provider: Hacker News Algolia API
requires_env: []
inputs: [query, max_results, tags]
outputs: [items, total_results]
side_effect: false
---
# hn_search

Searches Hacker News (stories or comments) via the free Algolia API.
Use for community/tech discussion around a topic. No API key required.
