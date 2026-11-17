<!-- contextpilot:research-routing -->
## Research routing (ContextPilot)

For external research (web pages, docs, GitHub issues/PRs, PDFs), prefer the ContextPilot MCP tools over native `WebFetch`/`WebSearch`:

- Discover with `contextpilot_search`, then read URLs with `contextpilot_research` (several URLs or a GitHub issue/PR in one call) or `contextpilot_fetch` (a single URL). Pass the error text or question as `focus`/`query`.
- Recover an omitted detail with `contextpilot_expand({ evidence_id })` — do not re-fetch the same URL or loop fetch→expand.
- They return ranked, token-budgeted, cached evidence with exact errors preserved. If a gateway call returns `ok:false`, fall back to the native tool.
<!-- /contextpilot:research-routing -->
