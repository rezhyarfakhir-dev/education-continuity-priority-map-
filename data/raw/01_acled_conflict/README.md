# ACLED — Political Violence Events (Nigeria)

**File:** `nigeria_political_violence_events_apr2026.xlsx`
**Source:** ACLED (Armed Conflict Location & Event Data Project), via HDX
**URL:** https://data.humdata.org/dataset/political-violence-events-and-fatalities
**Vintage:** event records 1997 — April 2026 (this snapshot accessed May 2026)
**Licence:** CC BY-NC-SA 4.0 (attribution, non-commercial, share-alike)
**Coverage:** all of Nigeria; we filter to Borno, Adamawa, Yobe and to years 2020 onwards.

## Schema (sheet `Data`)
`Country, Admin1, Admin2, ISO3, Admin2 Pcode, Admin1 Pcode, Month, Year, Events, Fatalities`

Each row is a monthly aggregation of political-violence events for one Admin2 (LGA).

## Limitations
- Reporting density varies by location; remote LGAs may be under-reported.
- "Events" includes battles, violence against civilians, explosions, riots, and protests — we treat the count as an exposure proxy.
- We aggregate 2020-2026 for the score; the long-tail history is not used.

## Used by
`scripts/01_clean_conflict.py` → `data/clean/conflict_by_lga.csv`
