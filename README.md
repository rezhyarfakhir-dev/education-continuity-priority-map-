# Education Continuity Priority Map

A transferable open-data method for prioritising areas at risk of education
disruption in conflict-affected regions. Demonstrated on North East Nigeria
(Borno, Adamawa, Yobe — the BAY states).

**Live artifact:** https://rezhyarfakhir-dev.github.io/education-continuity-priority-map-/

## What this is

A composite priority score is computed for each of 65 BAY LGAs from four
indicators:

1. ACLED political-violence events, 2020-2026
2. IOM DTM Round 50 displaced individuals
3. Percentage of schools listed as closed (iMMAP 2019)
4. Inverse of school-age population within 5 km of an education facility (HeiGIT 2026)

Each indicator is min-max-normalised to `[0, 1]`. The mean of the four is
tercile-classified into **high / medium / lower** priority and rendered as a
choropleth on a Leaflet map with full per-LGA detail in the popups.

The 21 LGAs of Adamawa are flagged **validation needed** rather than
classified, because the iMMAP 2019 source records 0 closed schools state-wide
(see `docs/adamawa_decision.md`).

## Why North East Nigeria

This case is a *demonstration only*. North East Nigeria is used as a
reference because it is data-rich (every required source is published), it
exposes a real data-quality problem (the Adamawa school-status ceiling), and
the same pipeline can be re-run against any country whose admin boundaries
and source layers are accessible. The repository is structured so that
re-targeting is a question of swapping the contents of `data/raw/` and
re-running `scripts/run_all.py`.

## Repository layout

```
data/raw/        immutable source files, one folder per source, each with a README
data/clean/      pipeline outputs, regenerable from raw via run_all.py
scripts/         seven cleaning scripts + run_all.py orchestrator
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

The orchestrator runs all seven scripts in order and writes a timestamped log
to `logs/`. Output files in `data/clean/` and `assets/` are overwritten in
place.

## Method, sources, validation

- `docs/method.md` — composite score construction, classification rule, choices made.
- `docs/sources.md` — every source with URL, vintage, licence, limitations.
- `docs/numeric_checks.md` — the assertions baked into the pipeline.
- `docs/adamawa_decision.md` — why Adamawa is "validation needed" and not classified.

## AI assistance disclosure

This repository was assembled with the assistance of large-language-model
coding tools used as a pair-programming aid. Every numeric figure on the
published map and in the documentation has been independently verified by
the author (a human) by running the pipeline locally against the raw source
files and inspecting the cleaned outputs row by row. Each upstream source —
ACLED, IOM DTM, iMMAP, OCHA, UNFPA, HeiGIT — was opened and read directly;
no figure was accepted from the model without being reproduced from the
underlying file. The Adamawa data-ceiling issue was identified by the
author during that verification, not assumed. All design choices, the
demonstration framing, and the contents of the documentation were
reviewed and approved by the author. No AI-generated text appears in the
source citations or the licence notices. The author takes full
responsibility for the contents of this repository.

## Licence

Source code and pipeline outputs: MIT (see `LICENSE`).
Raw data files in `data/raw/` retain their upstream licences (per-source
READMEs).
