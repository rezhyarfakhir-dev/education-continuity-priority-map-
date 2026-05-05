# Education Continuity Priority Map

A transferable open data method for prioritising areas at risk of education
disruption in conflict affected regions. Demonstrated on North East Nigeria
(Borno, Adamawa, Yobe, the BAY states).

**Live artifact:** https://rezhyarfakhir-dev.github.io/education-continuity-priority-map-/

## What this is

A composite priority score is computed for each of the 65 BAY LGAs from four
indicators:

1. ACLED political violence events, 2020 to 2026
2. IOM DTM Round 50 displaced individuals
3. **OCHA JIAF 2026 Education sector severity (1 to 5)**
4. Inverse of school age population within 5 km of an education facility (HeiGIT 2026)

Each indicator is min max normalised to `[0, 1]`. The composite is a
**pairwise** unweighted mean (`skipna=True`): indicators 1 to 3 cover all
65 LGAs, while indicator 4 (HeiGIT) is missing for 35 of 65 LGAs. Those
35 LGAs are scored on the 3 available indicators rather than imputed to a
worst-case value. Each LGA carries a `score_basis` flag
(`4_indicators` or `3_indicators_no_heigit`) which is surfaced in the
popup. See `docs/missing_data_policy.md`.

The composite is tercile classified into **high, medium, lower** priority
and rendered as a choropleth on a Leaflet map, with full per LGA detail in
the popups.

All 65 LGAs are scored, including the 21 in Adamawa. The OCHA JIAF
Education layer is the official 2026 humanitarian community estimate. It
resolves a state wide data ceiling that affected an earlier iMMAP 2019
school list (zero closures recorded across the whole of Adamawa). The
iMMAP figures still appear in the popup as context but no longer drive
the classification. See `docs/adamawa_decision.md` for the full story.

## Why North East Nigeria

This case is a *demonstration only*. North East Nigeria is used as a
reference because it is data rich (every required source is published), it
exposes a real data quality problem (the Adamawa school status ceiling), and
the same pipeline can be re-run against any country whose admin boundaries
and source layers are accessible. The repository is structured so that
re-targeting it is a question of swapping the contents of `data/raw/` and
re-running `scripts/run_all.py`.

## Repository layout

```
data/raw/        immutable source files, one folder per source, each with a README
data/clean/      pipeline outputs, regenerable from raw via run_all.py
scripts/         eight cleaning scripts plus run_all.py orchestrator
assets/          data.geojson, insights.json, style.css, map.js for the published map
docs/            method, sources, numeric checks, Adamawa decision note
index.html       the published map page
logs/            pipeline run logs (gitignored except .gitkeep)
```

## Reproducing the pipeline

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/run_all.py
```

The orchestrator runs all eight scripts in order and writes a timestamped
log to `logs/`. Output files in `data/clean/` and `assets/` are overwritten
in place.

## Method, sources, validation

- `docs/method.md`: composite score construction, classification rule, choices made.
- `docs/sources.md`: every source with URL, vintage, licence, limitations.
- `docs/numeric_checks.md`: the assertions baked into the pipeline.
- `docs/adamawa_decision.md`: how the Adamawa data ceiling was found and how it was resolved by switching to JIAF.

## AI assistance disclosure

This repository was put together with the help of large language model
coding tools, used as a pair programming aid. Every numeric figure on the
published map and in the documentation has been independently verified by
the author (a human) by running the pipeline locally against the raw source
files and inspecting the cleaned outputs row by row. Each upstream source
(ACLED, IOM DTM, OCHA JIAF, iMMAP, OCHA, UNFPA, HeiGIT) was opened and
read directly; no figure was accepted from the model without being
reproduced from the underlying file. The Adamawa data ceiling was
identified by the author during that verification, not assumed. All
design choices, the demonstration framing, and the contents of the
documentation were reviewed and approved by the author. No AI generated
text appears in the source citations or the licence notices. The author
takes full responsibility for the contents of this repository.

## Licence

Source code and pipeline outputs: MIT (see `LICENSE`).
Raw data files in `data/raw/` retain their upstream licences (per source
READMEs).
