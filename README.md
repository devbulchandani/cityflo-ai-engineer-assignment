# Cityflo Route Review MCP

A local, read-only MCP server for Priya's 3–9 August 2026 route punctuality review. It exposes route aggregates, trip-level evidence, data-quality references, and curated operational context. The server does not expose raw ops-log text.

## Run

Requires Python 3.11+ and `uv`.

```sh
uv sync
uv run python cityflo_mcp.py
```

The server uses MCP stdio transport. Add it to an MCP host with command `uv` and arguments `run --directory /absolute/path/to/cityflo python cityflo_mcp.py`. Set `CITYFLO_DATA_DIR` only if the CSV bundle is stored somewhere other than `./data`.

To drive the tools through the included MCP client and refresh the sanitized evidence files:

```sh
uv run python drive_mcp.py
```

## Tools

- `route_review`: all 40 route verdicts, route-level late-trip counts, robust daily medians, and excess trip-delay burden.
- `trip_evidence`: auditable records by route/date/lateness, returned by trip ID.
- `data_quality`: counts and trip references for excluded records, plus REC-114 and timezone handling.
- `ops_context`: curated, non-verbatim operational event summaries. Ops notes have no route key, so the tool explicitly marks them as unlinked context.

## Data and privacy

The source bundle is in `data/`; its public assignment source is `https://careers.cityflo.com/takehomes/ai-engineer/`. The MCP server reads the two CSV files only. It does not load `ops_log.txt`; its operational summaries are curated in `cityflo_mcp.py`. Tool outputs use route codes, trip IDs, timestamps, computed metrics, and non-sensitive event categories only. No rider phone number or verbatim complaint text is emitted or logged.

See [DECISION.md](DECISION.md) for the committed review and [evidence/](evidence/) for sanitized MCP results.
