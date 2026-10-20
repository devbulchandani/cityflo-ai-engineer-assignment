"""Run Cityflo review tools through a real MCP stdio client."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"


async def call_tool(name: str, arguments: dict) -> str:
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "cityflo_mcp.py")],
        env=None,
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
            if result.isError:
                raise RuntimeError(f"MCP tool {name} returned an error")
            return "\n".join(item.text for item in result.content if hasattr(item, "text"))


async def main() -> None:
    calls = [
        ("data_quality", {}),
        ("ops_context", {"day": "2026-08-05"}),
        ("route_review", {"limit": 40}),
        ("trip_evidence", {"route": "R-35", "start_date": "2026-08-05", "end_date": "2026-08-05", "min_lateness_min": 30, "limit": 25}),
        ("trip_evidence", {"route": "R-27", "start_date": "2026-08-06", "end_date": "2026-08-08", "min_lateness_min": 10, "limit": 25}),
        ("trip_evidence", {"route": "R-14", "start_date": "2026-08-03", "end_date": "2026-08-04", "min_lateness_min": 10, "limit": 25}),
        ("trip_evidence", {"route": "R-33", "start_date": "2026-08-04", "end_date": "2026-08-09", "min_lateness_min": 10, "limit": 25}),
        ("trip_evidence", {"route": "R-26", "start_date": "2026-08-05", "end_date": "2026-08-06", "min_lateness_min": 10, "limit": 25}),
        ("trip_evidence", {"route": "R-37", "start_date": "2026-08-03", "end_date": "2026-08-07", "min_lateness_min": 10, "limit": 25}),
        ("trip_evidence", {"route": "R-23", "start_date": "2026-08-03", "end_date": "2026-08-03", "limit": 25}),
        ("trip_evidence", {"route": "R-17", "start_date": "2026-08-07", "end_date": "2026-08-07", "min_lateness_min": 10, "limit": 25}),
    ]
    EVIDENCE.mkdir(exist_ok=True)
    transcript = []
    for index, (name, arguments) in enumerate(calls, start=1):
        raw = await call_tool(name, arguments)
        result = json.loads(raw)
        record = {"tool": name, "arguments": arguments, "result": result}
        transcript.append(record)
        filename = {
            "route_review": "route_review.json",
            "data_quality": "data_quality.json",
            "ops_context": "ops_context.json",
        }.get(name, f"trip_evidence_{index}.json")
        (EVIDENCE / filename).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"## {name} {json.dumps(arguments, sort_keys=True)}")
        print(json.dumps(result, indent=2))
    (EVIDENCE / "mcp_tool_calls.json").write_text(json.dumps(transcript, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
