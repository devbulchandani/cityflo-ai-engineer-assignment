# Friday Route Review — Decision Record

**Decision for Priya:** Flag **R-35, R-27, and R-14** as the three highest weekly delay burdens, in that order. Keep **R-33, R-26, and R-37** on a recurring-delay watch list; do not yet treat them as the three worst routes. Monitor the other 34 routes. “Monitor” does not mean every trip was on time: it means the route did not meet this review’s route-level flag/watch rule.

This review covers 3–9 August 2026. The source contains 5,292 trip rows. After the documented data screens below, 5,250 trips contribute to the route metrics. The five-minute threshold is an explicit review tolerance chosen to avoid escalating small GPS/schedule jitter; it is not a Cityflo policy found in the bundle.

## How the call is made

1. Compute trip lateness as `actual arrival in India time − scheduled departure in India time − applicable scheduled runtime`.
2. Convert the device timestamp using its stated `tz_offset` before comparing it to local scheduled time. Apply REC-114 to the referenced 4xx series using `schedule_v2.csv` on and after its effective date. This applied 188 runtime overrides.
3. Exclude unparseable timestamps/offsets. Also exclude rows where the converted arrival precedes scheduled departure: without an actual departure timestamp, those rows cannot support a comparable scheduled-runtime calculation. They are retained in the quality references, not silently repaired.
4. For the weekly ranking, compute **excess trip-delay minutes** as `sum(max(lateness − 5, 0))` over valid trips, then sort descending. This sums the delay above tolerance; it does not let a route’s large trip count disappear inside a mean. A trip can add at most its actual lateness minus five, so one row cannot set the result by itself.
5. A **material late day** has at least 10 valid trips and a within-day median lateness of at least 5 minutes. The top three by weekly excess burden are **FLAG**. Non-top-three routes with material late days on at least two dates are **WATCH**. All other routes are **MONITOR**.

The ops notes report a Wednesday morning western-corridor diversion of about 35 minutes and a citywide festival slowdown around 18:20. The ops log has no route key. Those facts are timing context only; they do not prove the cause of any route’s lateness.

### REC-114 effective-date sensitivity

The baseline applies R-14's 53-minute revised runtime only from the stated 5 August 2026 effective date. Under that interpretation R-14 has 249 excess trip-minutes and ranks third; R-33 has 182 and ranks fourth. As a sensitivity check, applying the revised runtime to all R-14 trips from 3–9 August lowers R-14 to 166 excess trip-minutes (down 83) and moves it to fourth, while R-33 becomes third and enters the FLAG group. Keep the strict effective-date interpretation: the schedule explicitly dates the change to 5 August, and no source says it is retroactive. If ops confirms the revision should cover the full week, revise the baseline and flags accordingly.

## One verdict per route

“Trips >5m” counts trips with lateness strictly greater than five minutes. “Excess trip-min” sums only the minutes beyond five per trip. “Late days” applies the minimum sample and daily median rule above. Negative weekly medians mean the midpoint of included trips arrived before the scheduled runtime; they do not offset positive excess burden.

| Burden rank | Route | Verdict | Valid trips | Weekly median late (min) | P90 late (min) | Trips >5m | Excess trip-min >5m | Material late days |
|---:|:---|:---|---:|---:|---:|---:|---:|---:|
| 1 | R-35 | FLAG | 132 | 2.0 | 50.7 | 32 | 914.0 | 1 |
| 2 | R-27 | FLAG | 143 | 4.0 | 14.0 | 62 | 384.0 | 3 |
| 3 | R-14 | FLAG | 118 | 4.0 | 12.0 | 51 | 249.0 | 2 |
| 4 | R-33 | WATCH | 104 | 5.0 | 10.0 | 49 | 182.0 | 6 |
| 5 | R-26 | WATCH | 103 | 4.0 | 9.6 | 44 | 131.0 | 4 |
| 6 | R-17 | MONITOR | 147 | 3.0 | 8.2 | 41 | 130.0 | 1 |
| 7 | R-37 | WATCH | 105 | 4.0 | 9.0 | 42 | 125.0 | 2 |
| 8 | R-09 | MONITOR | 146 | 2.0 | 8.0 | 33 | 100.0 | 0 |
| 9 | R-07 | MONITOR | 147 | 3.0 | 8.0 | 32 | 91.0 | 0 |
| 10 | R-31 | MONITOR | 112 | 4.0 | 8.0 | 37 | 91.0 | 1 |
| 11 | R-18 | MONITOR | 154 | 2.0 | 7.0 | 32 | 86.0 | 0 |
| 12 | R-11 | MONITOR | 137 | 2.0 | 8.0 | 23 | 84.0 | 0 |
| 13 | R-40 | MONITOR | 152 | 3.0 | 7.0 | 33 | 83.0 | 0 |
| 14 | R-15 | MONITOR | 119 | 3.0 | 8.0 | 25 | 77.0 | 1 |
| 15 | R-20 | MONITOR | 145 | 2.0 | 7.0 | 24 | 77.0 | 0 |
| 16 | R-38 | MONITOR | 146 | 1.0 | 7.0 | 24 | 75.0 | 0 |
| 17 | R-34 | MONITOR | 124 | 3.0 | 8.0 | 28 | 74.0 | 1 |
| 18 | R-08 | MONITOR | 126 | 3.0 | 7.0 | 26 | 73.0 | 0 |
| 19 | R-39 | MONITOR | 154 | 2.0 | 6.5 | 25 | 73.0 | 0 |
| 20 | R-19 | MONITOR | 125 | 3.0 | 7.0 | 23 | 63.0 | 1 |
| 21 | R-05 | MONITOR | 105 | 2.0 | 7.0 | 20 | 62.0 | 1 |
| 22 | R-25 | MONITOR | 139 | 1.0 | 7.0 | 20 | 59.0 | 0 |
| 23 | R-21 | MONITOR | 124 | 2.0 | 7.0 | 26 | 55.0 | 0 |
| 24 | R-03 | MONITOR | 103 | 2.0 | 7.0 | 21 | 54.0 | 0 |
| 25 | R-10 | MONITOR | 126 | 1.0 | 7.0 | 18 | 51.0 | 0 |
| 26 | R-32 | MONITOR | 133 | 1.0 | 7.0 | 21 | 49.0 | 0 |
| 27 | R-01 | MONITOR | 153 | 1.0 | 5.0 | 13 | 47.0 | 0 |
| 28 | R-12 | MONITOR | 112 | 2.0 | 6.7 | 15 | 47.0 | 0 |
| 29 | R-24 | MONITOR | 146 | 1.0 | 6.0 | 16 | 45.0 | 0 |
| 30 | R-22 | MONITOR | 112 | 2.0 | 6.0 | 18 | 43.0 | 0 |
| 31 | R-28 | MONITOR | 151 | 1.0 | 5.8 | 15 | 36.0 | 0 |
| 32 | R-30 | MONITOR | 147 | -1.0 | 5.0 | 11 | 33.0 | 0 |
| 33 | R-02 | MONITOR | 105 | 2.0 | 6.4 | 15 | 31.0 | 0 |
| 34 | R-36 | MONITOR | 132 | 1.0 | 5.7 | 13 | 30.0 | 0 |
| 35 | R-04 | MONITOR | 144 | 0.0 | 5.5 | 14 | 27.0 | 0 |
| 36 | R-29 | MONITOR | 151 | -1.0 | 4.0 | 6 | 20.0 | 0 |
| 37 | R-16 | MONITOR | 146 | 0.0 | 4.3 | 7 | 18.0 | 0 |
| 38 | R-13 | MONITOR | 133 | -1.0 | 5.0 | 8 | 16.0 | 0 |
| 39 | R-23 | MONITOR | 132 | 0.0 | 5.0 | 8 | 15.0 | 0 |
| 40 | R-06 | MONITOR | 117 | -2.0 | 4.0 | 6 | 14.0 | 0 |


## Defended calls

Dollar impact, passenger counts, fares, and incentive values are not in this bundle. The quantified cost below is **trip-minutes above tolerance**, not rider-minutes or currency. If a route is falsely flagged, the depot head risks losing the on-time incentive. If it is wrongly cleared, riders bear delay and the refund queue bears the resulting claims. I will not invent a rupee estimate.

### 1. Flag R-35 — largest weekly burden, but concentrated on one date

- **Rule and result:** R-35 ranks first with 914 excess trip-minutes, 32 trips above five minutes, and 19/19 valid trips on 5 August late by 36–61 minutes (daily median 52). The whole-week median is only 2 minutes, which hides the event; the P90 is 50.7 minutes. Evidence includes [R-35 trip drilldown](evidence/trip_evidence_4.json) and [the full MCP ranking](evidence/route_review.json).
- **Case the rule breaks on:** `T1-04521` is 61 minutes late and contributes 56 excess minutes on its own. More broadly, the rule makes R-35 #1 even though its weekly median is only 2 minutes and the severe signal is concentrated on one date; that would be the wrong verdict if “worst” meant chronic route failure. I keep it as an *acute weekly burden* because Priya asked what actually happened this week, and the other 18 same-day trips are also at least 36 minutes late; the route-day median stays 52, so the call is not driven by that one row.
- **Cost and who pays:** The 19 trips on 5 August account for 880 excess trip-minutes; the weekly total is 914. Flagging risks the depot head’s incentive. Clearing would leave a documented cluster of 19 badly delayed trips for riders and the refund queue to absorb. The data cannot turn trips into passenger counts.
- **What changes my mind:** Independent dispatch/arrival records showing a shared clock or route-assignment fault across the 19 trips would remove this flag. A second similarly bad day would instead establish recurrence rather than a one-day event.

### 2. Flag R-27 — repeated, material lateness after REC-114

- **Rule and result:** R-27 ranks second at 384 excess trip-minutes, with 62 trips >5 minutes. It has three material days: daily medians of 7, 11, and 8 minutes on 6–8 August; weekly median 4 and P90 14. The revised runtime is applied from its 5 August effective date. See [R-27 trip drilldown](evidence/trip_evidence_5.json).
- **Case the rule breaks on:** `T1-03500` is 25 minutes late on 8 August. If it were an isolated bad device row, it would be a poor reason to penalize the depot; the decision rests on 11–13 trips over five minutes on each of three dates, not on this maximum.
- **Cost and who pays:** 62 trips exceeded tolerance and accumulated 384 excess trip-minutes. A false flag costs the depot head incentive; clearing a repeated three-day signal leaves riders and support handling delay complaints. No fare or rider count is supplied.
- **What changes my mind:** Dispatch records showing the schedule-v2 runtime or the reported trip assignments are wrong, or independent GPS contradicting the 6–8 August pattern, would overturn the flag.

### 3. Flag R-14 — third by weekly burden; issue is early-week

- **Rule and result:** R-14 ranks third with 249 excess trip-minutes and 51 trips >5 minutes. Its material days are 3 and 4 August (daily medians 7 and 8.5 minutes); weekly median 4, P90 12. REC-114’s revised 53-minute runtime is used from 5 August onward, so this verdict does not carry the old baseline forward. See [R-14 trip drilldown](evidence/trip_evidence_6.json).
- **Case the rule breaks on:** `T1-01678` is 17 minutes late on 3 August. One trip should not decide route rank; here it is representative of a day with 12/17 trips over five minutes and a 7-minute median, followed by a second material day.
- **Cost and who pays:** 51 trips exceeded the tolerance and total excess burden is 249 trip-minutes. Flagging may cost the depot’s incentive; clearing the early-week service issue shifts the risk to riders and the refund queue. The post-5-Aug revised schedule reduces measured delay, so the recommendation is a weekly ranking rather than a claim that the route remained late all week.
- **What changes my mind:** A corrected REC-114 effective date/runtime that materially lowers the 3–4 August burden, or dispatch data showing those days were not late, would move R-14 out of the top three.

### Borderline calls — WATCH, not FLAG

**R-33:** WATCH for recurrence, not a top-three penalty. It has six material days, weekly median 5 minutes, P90 10, and 49 trips >5; burden is 182 excess trip-minutes (rank 4). `T1-04286` was 15 minutes late on 6 August, but this is not the sole basis: the daily median was 7 and five other dates also met the five-minute threshold. The precise five-minute boundary is the weak point: a systematic timestamp bias of a few minutes could create this watch signal. The conservative cost of a red flag would be an incentive penalty on a route whose median is exactly at threshold; clearing entirely would leave six repeat dates unexamined. Independent arrival scans showing a route-level clock bias, or a next-week distribution below five minutes, would remove the watch. See [R-33 trip evidence](evidence/trip_evidence_7.json).

**R-26:** WATCH because four dates meet the rule; 44 trips >5, weekly median 4, P90 9.6, and 131 excess trip-minutes (rank 5). `T1-03314` is 13 minutes late on 5 August, while the 5–6 August daily medians are both 6. This is a modest signal, not enough for a top-three incentive decision. A schedule correction or verified device bias that takes the four daily medians below five would remove the watch; a continued pattern next week would strengthen it. See [R-26 trip evidence](evidence/trip_evidence_8.json).

**R-37:** WATCH on two dates, with 42 trips >5, weekly median 4, P90 9, and 125 excess trip-minutes (rank 7). `T1-04787` is 13 minutes late on 6 August; treating this worst trip alone as route-level proof would overstate the case, so the decision depends on the second qualifying day too. One qualifying day is exactly at the five-minute median threshold. A route-level clock offset or a clean next-week sample would clear the watch; another two-day pattern would keep it. See [R-37 trip evidence](evidence/trip_evidence_9.json).

**R-17 is the closest WATCH/MONITOR cutoff.** Its 130 excess trip-minutes narrowly exceed R-37’s 125, but all of its signal is concentrated in one material day (7 August, median 6 minutes); R-37 meets the same rule on two dates. The recurrence rule therefore leaves R-17 at MONITOR and puts R-37 on WATCH, even though their totals are nearly tied. `T1-02139` is 14 minutes late; the remaining R-17 drilldown is [here](evidence/trip_evidence_11.json). The cost of monitoring R-17 is that its 41 trips >5 minutes and 130 excess trip-minutes receive no watch escalation; promoting it without recurrence risks an incentive penalty from one-day noise. Another date with at least 10 valid trips and median lateness ≥5 would change my mind and move R-17 to WATCH.

## Data limits and auditable exceptions

The server excludes **24 invalid timestamp/offset rows** (including impossible minute values such as `08:60`) and **18 rows whose converted arrival precedes scheduled departure**. These 42 rows are referenced by trip ID, route, date, and reason in [data-quality evidence](evidence/data_quality.json); no malformed time string is echoed. The choice to exclude the 18 chronologically ambiguous rows could bias a route’s late-day median upward because some appear early. Re-running with those rows treated as early would be the sensitivity check; if any watch/flag changes, Priya should review the source records before a depot decision.

One `+00:00` device arrival is normalized to India time: `T1-02864` on R-23 becomes 07:02 local and −2 minutes late, not a five-and-a-half-hour early outlier. See [R-23 trip evidence](evidence/trip_evidence_10.json). REC-114 overrides were applied to 188 valid 4xx records from the effective date.

The ops notes have no route join. Wednesday’s weather/crowd events coincide with R-35’s severe day, but this review does not assign causation. The MCP server emits curated event categories only; it does not read or return raw ops-log lines, rider numbers, or complaint text.

## Reproducibility and steering

Run `uv sync && uv run python drive_mcp.py` to connect through MCP stdio, call the tools, and refresh `evidence/`. The exact threshold and verdict rules are implemented in `cityflo_mcp.py`. The steering ledger contains the user’s explicit scope decision verbatim; the data-scoring rules are the agent’s analysis choices, not user instructions.
