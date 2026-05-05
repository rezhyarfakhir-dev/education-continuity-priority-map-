# Missing data policy: HeiGIT accessibility

## Summary

HeiGIT's wide-form export
(`data/raw/07_heigit_accessibility/NGA_education_access_wide.csv`)
publishes one row per `(LGA, distance band)` **only when that band
captures school age population**. An LGA that does not appear at the 5 km
band may either (a) genuinely have no school age population within 5 km
of an education facility, or (b) have no nearby facility records ingested
by HeiGIT for that LGA at all. **The two cases are not distinguishable
from the published wide file alone.**

For the 65 BAY LGAs:

- **30** have a 5 km row.
- **35** do not (Borno 11, Adamawa 12, Yobe 12).
- Of the 35, **13 have no HeiGIT row at any distance band up to 50 km**
  (the remaining 22 first appear at the 10, 25 or 50 km bands).

## Decision

The pipeline does **not** impute a value for the missing 35. Specifically:

- `scripts/04_clean_access.py` leaves
  `school_age_population_share`, `weak_access_pct`, and the normalised
  `access_score_norm` as `NaN` for missing rows.
- `scripts/06_compute_scores.py` computes the composite as a **pairwise
  mean** (`pandas.DataFrame.mean(axis=1, skipna=True)`) over indicators
  ACLED, DTM, JIAF Education severity and (where present) HeiGIT access.
  The 35 LGAs are scored on the 3 available indicators.
- A `score_basis` column (`4_indicators` or `3_indicators_no_heigit`) and
  an `indicators_used` count are written for every LGA.
- `scripts/07_export_leaflet_data.py` carries `score_basis` and
  `indicators_used` into the geojson properties; the popup surfaces a
  short note when the LGA is scored on 3 indicators.

## Why not impute?

The earlier version of `04_clean_access.py` substituted "missing 5 km row"
with "0% within 5 km" (i.e. 100% beyond 5 km, the worst possible value).
That was technically defensible (the export does omit zero-population
bands) but it had two problems:

1. **It conflated two different states of the world.** A frontier LGA
   that genuinely has no facilities within 5 km, and an LGA with sparse
   ingestion in HeiGIT's facility layer, both got the same maximum
   penalty. There is no way to distinguish them in the published file.
2. **It mechanically inflated 35 of 65 composites by exactly 0.25**
   (the value of 1.0 / 4 indicators) versus a pairwise mean. That single
   pseudo-data point was enough to push several LGAs across tercile
   thresholds without any real underlying signal.

The pairwise mean policy keeps the composite well-defined for every LGA
and refuses to silently invent worst-case data. The reader can always see
which LGAs were scored on 3 indicators (via popup, geojson, and CSV) and
factor that into operational decisions.

## What this changes in practice

Compared to the prior imputation policy, 16 of 65 LGAs reclassify, all
between adjacent tercile classes. The headline counts remain unchanged:

- 22 high priority (Borno 15, Adamawa 4, Yobe 3) - **unchanged total per
  state**, but composition changes:
  - Borno: Nganzai drops to medium; Kukawa rises to high.
  - Adamawa: Madagali and Lamurde drop to medium; Girei and Hong rise to
    high. Michika and Mubi South unchanged.
  - Yobe: 3 high LGAs (Geidam, Gujba, Gulani) unchanged.
- Of the 22 high LGAs, **17 are scored on 4 indicators and 5 on 3
  indicators** (Borno: Damboa, Dikwa, Kala/Balge; Yobe: Geidam, Gulani).
  All 5 sit within established BAY conflict / displacement hotspots.

## How to refresh this policy under re-targeting

1. Run the pipeline against a new country.
2. Look at the printed output of `04_clean_access.py`:
   `BAY LGAs missing (treated as NULL, dropped from access mean): N`.
3. If `N` is small relative to the LGA count (say <10%), the pairwise
   mean is statistically reasonable. If `N` exceeds ~50% of LGAs, drop
   indicator 4 entirely from that country's composite and document it in
   the country-specific notes.
4. The `score_basis` column lets the contracting authority audit the
   trade-off per LGA without re-running the pipeline.

## Code references

- `scripts/04_clean_access.py` - lines documenting the no-imputation rule.
- `scripts/06_compute_scores.py` - pairwise mean and `score_basis` column.
- `scripts/07_export_leaflet_data.py` - export of `score_basis` and
  `indicators_used` into the geojson.
- `assets/map.js` - popup rendering of "no HeiGIT coverage" and the
  3-of-4 indicators note.
