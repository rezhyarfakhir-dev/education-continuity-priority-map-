# Adamawa: from "validation needed" to fully scored (JIAF 2026)

## What we found in the iMMAP 2019 source

The iMMAP / Education Sector school list (19 June 2019) contains 7,229
schools across the BAY states. Crosstab of state by status (after
normalising the Yobe value `Close` to `closed`):

| State | open | closed | total |
|-------|------|--------|-------|
| Borno | 881 | 828 | 1,709 |
| Adamawa | 4,011 | **0** | 4,011 |
| Yobe | 1,307 | 74 | 1,381 |

Borno reports 48 % of its schools as closed. Yobe reports 5 %. **Adamawa
reports zero closed schools across its entire 4,011-record inventory.**

There is no plausible operational reading in which exactly zero of 4,011
schools across 21 LGAs are closed. The most likely explanation is that
the partner who contributed the Adamawa records to the 2019 sectoral
exercise reported only operational schools, or did not perform the
closure-status field. Either way, the source carries no information about
school disruption in Adamawa.

## First-pass response (preserved here for the audit trail)

Originally the 21 Adamawa LGAs were classified as **validation needed**
(grey on the choropleth) and excluded from the tercile thresholds, with
the popup explanation:

> iMMAP 2019 lists all Adamawa schools as 'Open' (no closed records);
> school-disruption indicator unavailable, field validation required.

This was the honest move under the constraint that iMMAP was the only
school-disruption source we had ingested at that point. It surfaced the
data ceiling rather than silently averaging a misleading 0 % into the
score.

## Improved response: swap the indicator (current state)

We then identified a stronger, more current source: the **OCHA Joint
Intersectoral Analysis Framework (JIAF) Nigeria 2026** workbook, which
publishes an Education sector severity score (1-5) and Education sector
PiN per LGA for every BAY LGA, with **no nulls** in Adamawa. JIAF is
the agreed humanitarian-community estimate for the 2026 HNO and is
produced by OCHA in coordination with the Education Cluster.

We swapped indicator 3 in the composite from iMMAP `pct_closed` to JIAF
`education_severity`. As a result:

- All 65 BAY LGAs are now scored, including the 21 in Adamawa.
- The grey "validation needed" class is no longer used.
- iMMAP `total_schools`, `closed_schools` and `pct_closed` are still
  carried through to the popup as **context** so the historical school
  inventory snapshot remains visible, but they no longer influence
  classification.

The pcode format (`Admin 2 P-Code` in JIAF) matches OCHA COD-AB exactly,
so no normalisation was needed.

Adamawa's observed JIAF Education severity values are **2 (Stress) for
12 LGAs and 3 (Severe) for 9 LGAs** \u2014 consistent with the conflict and
displacement signals we see independently in ACLED and DTM.

## Why this matters as a method demonstration

The progression is itself the point of the exercise:

1. **Detect** the data ceiling using a hard assertion in code
   (`scripts/03_clean_schools.py`: `assert ad_closed == 0`).
2. **Refuse to silently impute**, route the affected LGAs to a separate
   class with an explicit reason field.
3. **Search for a more authoritative source**, validate it against the
   problem (zero nulls, 65/65 LGA coverage, sector-comparable scale).
4. **Swap and document** the change, preserving the previous source as
   context rather than deleting it.

This is the exact judgment chain a programme would need under any
re-targeting of the method to a new country.

## Pipeline enforcement

- `scripts/03_clean_schools.py` keeps the `assert ad_closed == 0`
  assertion. If iMMAP ever publishes a refreshed list with non-zero
  closures in Adamawa, the assertion fires and forces a manual review.
- `scripts/08_clean_education_jiaf.py` asserts `len(df) == 65`,
  `education_severity.isna().sum() == 0`, and the per-state LGA counts
  (Borno 27 / Adamawa 21 / Yobe 17). Any change in the upstream JIAF
  workbook structure that breaks BAY coverage will fire one of these.
- `scripts/06_compute_scores.py` asserts that every LGA has a defined
  composite score after the JIAF merge.
