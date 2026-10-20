"""MCP tools for reviewing Cityflo route punctuality without exposing PII."""

from __future__ import annotations

import csv
import json
import os
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median, quantiles
from typing import Any

from mcp.server.fastmcp import FastMCP


ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("CITYFLO_DATA_DIR", ROOT / "data"))
LOCAL_TZ = timezone(timedelta(hours=5, minutes=30))
MCP = FastMCP("Cityflo Route Review")

# Curated, non-sensitive summaries of ops_log.txt. Do not pass arbitrary free text
# from the ops log through MCP; the log has no route key, so events are context only.
OPS_EVENTS = [
    {"date": "2026-08-03", "category": "depot_departure_disruption", "summary": "Two buses reportedly left the depot late; no route IDs recorded."},
    {"date": "2026-08-04", "category": "staffing_disruption_covered", "summary": "An evening driver no-show was covered; no route IDs recorded."},
    {"date": "2026-08-05", "category": "weather_diversion", "summary": "Western corridor waterlogging; an approximately 35-minute diversion was reported during the morning."},
    {"date": "2026-08-05", "category": "citywide_demand_surge", "summary": "Festival crowd surge around 18:20; a citywide slowdown was reported."},
    {"date": "2026-08-06", "category": "vehicle_swap", "summary": "A vehicle was swapped midday after an AC issue; no route IDs recorded."},
    {"date": "2026-08-07", "category": "normal_operations", "summary": "Operations were reported as normal."},
]


def _load() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load, normalize, and screen trips. Raw text fields never leave this module."""
    schedules: dict[str, dict[str, Any]] = {}
    with (DATA_DIR / "schedule_v2.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            schedules[row["route"]] = {
                "runtime": int(row["revised_runtime_min"]),
                "effective": date.fromisoformat(row["effective_date"]),
            }

    trips: list[dict[str, Any]] = []
    excluded: Counter[str] = Counter()
    overrides = 0
    timezone_conversions = 0
    raw_count = 0
    excluded_records: list[dict[str, str]] = []
    with (DATA_DIR / "trips.csv").open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            raw_count += 1
            # Keep output schemas explicit. No free-text ops or complaint fields are copied.
            try:
                departure = datetime.strptime(raw["scheduled_departure"], "%Y-%m-%d %H:%M").replace(tzinfo=LOCAL_TZ)
                offset_text = raw["tz_offset"]
                sign = 1 if offset_text.startswith("+") else -1
                oh, om = (int(part) for part in offset_text[1:].split(":"))
                stamped_tz = timezone(sign * timedelta(hours=oh, minutes=om))
                arrival = datetime.strptime(raw["actual_arrival"], "%Y-%m-%d %H:%M").replace(tzinfo=stamped_tz)
                arrival = arrival.astimezone(LOCAL_TZ)
            except (ValueError, TypeError, KeyError):
                reason = "invalid_timestamp_or_offset"
                excluded[reason] += 1
                excluded_records.append({
                    "trip_id": raw.get("trip_id", ""),
                    "route": raw.get("route", ""),
                    "day": raw.get("scheduled_departure", "")[:10],
                    "reason": reason,
                })
                continue

            if arrival < departure:
                reason = "arrival_before_scheduled_departure"
                excluded[reason] += 1
                excluded_records.append({
                    "trip_id": raw["trip_id"],
                    "route": raw["route"],
                    "day": departure.date().isoformat(),
                    "reason": reason,
                })
                continue

            route = raw["route"]
            series = raw["vehicle_series"]
            runtime = int(raw["scheduled_runtime_min"])
            schedule = schedules.get(route)
            # vehicle_series stores the final two digits; REC-114 applies to the 4xx fleet.
            if series in {"14", "27"} and schedule and departure.date() >= schedule["effective"]:
                runtime = schedule["runtime"]
                overrides += 1

            late = (arrival - departure).total_seconds() / 60 - runtime
            trips.append({
                "trip_id": raw["trip_id"],
                "route": route,
                "vehicle_series": series,
                "day": departure.date().isoformat(),
                "scheduled_departure": departure.strftime("%Y-%m-%d %H:%M"),
                "actual_arrival_local": arrival.strftime("%Y-%m-%d %H:%M"),
                "scheduled_runtime_min": runtime,
                "lateness_min": round(late, 1),
                "tz_offset": offset_text,
            })
            if offset_text != "+05:30":
                timezone_conversions += 1

    return trips, {
        "raw_rows": raw_count,
        "included_rows": len(trips),
        "excluded_rows": dict(sorted(excluded.items())),
        "excluded_trip_references": sorted(excluded_records, key=lambda item: (item["route"], item["day"], item["trip_id"])),
        "schedule_overrides_applied": overrides,
        "nonlocal_timezone_rows_normalized": timezone_conversions,
        "routes": len({trip["route"] for trip in trips}),
        "days": sorted({trip["day"] for trip in trips}),
    }


def _route_stats(trips: list[dict[str, Any]]) -> list[dict[str, Any]]:
    routes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trip in trips:
        routes[trip["route"]].append(trip)

    result: list[dict[str, Any]] = []
    for route, records in routes.items():
        lateness = [trip["lateness_min"] for trip in records]
        route_days: dict[str, list[float]] = defaultdict(list)
        for trip in records:
            route_days[trip["day"]].append(trip["lateness_min"])
        material_days = []
        for day, values in sorted(route_days.items()):
            day_median = median(values)
            if len(values) >= 10 and day_median >= 5:
                material_days.append({
                    "date": day,
                    "valid_trips": len(values),
                    "median_lateness_min": round(day_median, 1),
                    "trips_over_5_min": sum(value > 5 for value in values),
                })

        # Sum route-wide delay burden beyond a five-minute tolerance. This is additive,
        # not a mean: a single extreme trip cannot outweigh a broad set of late trips.
        excess = round(sum(max(0.0, value - 5.0) for value in lateness), 1)
        p90 = quantiles(lateness, n=10)[8] if len(lateness) >= 2 else lateness[0]
        result.append({
            "route": route,
            "valid_trips": len(records),
            "median_lateness_min": round(median(lateness), 1),
            "p90_lateness_min": round(p90, 1),
            "trips_over_5_min": sum(value > 5 for value in lateness),
            "excess_delay_min_over_5": excess,
            "material_late_days": material_days,
            "material_late_day_count": len(material_days),
        })

    ranked = sorted(result, key=lambda item: (-item["excess_delay_min_over_5"], item["route"]))
    for index, item in enumerate(ranked, start=1):
        item["burden_rank"] = index
        if index <= 3:
            item["verdict"] = "FLAG — top-three weekly delay burden"
        elif item["material_late_day_count"] >= 2:
            item["verdict"] = "WATCH — recurring material late days"
        else:
            item["verdict"] = "MONITOR — no sustained route-level signal"
    return ranked


@MCP.tool()
def route_review(limit: int = 40) -> str:
    """Return all route verdict metrics, ranked by total delay beyond five minutes.

    A material route-day has at least 10 valid trips and a daily median lateness of
    at least 5 minutes. Results contain aggregate evidence and route/trip IDs only.
    """
    trips, quality = _load()
    routes = _route_stats(trips)
    if not 1 <= limit <= 40:
        raise ValueError("limit must be between 1 and 40")
    return json.dumps({"quality": quality, "routes": routes[:limit]}, indent=2)


@MCP.tool()
def trip_evidence(route: str, start_date: str | None = None, end_date: str | None = None,
                  min_lateness_min: float | None = None, limit: int = 25) -> str:
    """Retrieve auditable trip rows for one route, with optional date/lateness filters.

    Each record is keyed by trip_id and contains corrected local timestamps and
    computed lateness. No rider text, phone numbers, or unrelated raw fields are returned.
    """
    try:
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None
    except ValueError as exc:
        raise ValueError("Dates must use YYYY-MM-DD") from exc
    if limit < 1 or limit > 200:
        raise ValueError("limit must be between 1 and 200")

    trips, _ = _load()
    selected = [trip for trip in trips if trip["route"].upper() == route.upper()]
    if start:
        selected = [trip for trip in selected if date.fromisoformat(trip["day"]) >= start]
    if end:
        selected = [trip for trip in selected if date.fromisoformat(trip["day"]) <= end]
    if min_lateness_min is not None:
        selected = [trip for trip in selected if trip["lateness_min"] >= min_lateness_min]
    selected.sort(key=lambda trip: (trip["day"], trip["scheduled_departure"], trip["trip_id"]))
    return json.dumps({"route": route.upper(), "matched": len(selected), "trips": selected[:limit]}, indent=2)


@MCP.tool()
def data_quality() -> str:
    """Summarize timestamp and reconciliation handling; never returns raw ops text."""
    _, quality = _load()
    return json.dumps(quality, indent=2)


@MCP.tool()
def ops_context(day: str | None = None) -> str:
    """Return curated operational context, never raw log lines or rider complaint text.

    Ops notes have no route key, so these events can explain timing but cannot
    establish that a specific route caused or experienced the event.
    """
    if day:
        try:
            date.fromisoformat(day)
        except ValueError as exc:
            raise ValueError("day must use YYYY-MM-DD") from exc
        events = [event for event in OPS_EVENTS if event["date"] == day]
    else:
        events = OPS_EVENTS
    return json.dumps({"route_linked": False, "events": events}, indent=2)


def main() -> None:
    MCP.run(transport="stdio")


if __name__ == "__main__":
    main()
