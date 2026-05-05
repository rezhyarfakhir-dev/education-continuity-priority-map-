# Method

## Unit of analysis

The Local Government Area (LGA, OCHA admin level 2). 65 LGAs across Borno
(27), Adamawa (21) and Yobe (17). The choice matches the operational unit
used by the Education Cluster, the Education Sector working group in North
East Nigeria, OCHA INFORM Severity, and ACAPS humanitarian access scoring.

## Indicators

| # | Indicator | Source | Score direction |
|---|-----------|--------|-----------------|
| 1 | ACLED political-violence events 2020-2026, count per LGA | ACLED Apr 2026 | higher = more pressure |
| 2 | IDP individuals per LGA | IOM DTM Round 50 (Oct 2025) | higher = more pressure |
| 3 | OCHA JIAF Education sector intersectoral severity (1-5) | OCHA JIAF 2026 HNO | higher = more pressure |
| 4 | School-age population *not* within 5 km of an education facility | HeiGIT (Feb 2026) | higher = more pressure |

Each indicator is min-max-normalised across the scored set:

```
score_norm_i = (x_i - min(x)) / (max(x) - min(x))
```

The composite score is the unweighted mean of the four normalised indicators.
Equal weighting is used because there is no defensible empirical basis to
weight one indicator over another at this stage; weights would be calibrated
in country with the contracting authority before any operational use.

## Classification

The composite score is **tercile-classified** across the full 65-LGA scored
set into high / medium / lower priority. Choropleth colours: red / orange /
yellow.

All 65 LGAs (including the 21 in Adamawa) are scored. The previous
"validation needed" class is no longer required because the OCHA JIAF
Education severity layer covers all of Adamawa with no nulls. See
`adamawa_decision.md` for the history of that decision and why JIAF was
selected.

## Why these four indicators

- **Recent conflict** drives both school closure and population movement.
- **Current displacement** is the most direct proxy for which LGAs are
  hosting school-age children whose education has been interrupted.
- **JIAF Education severity** is the agreed humanitarian community
  estimate for sectoral need; using it means the priority map reflects the
  Education Cluster's own 2026 judgment rather than a derivation from one
  partner's 2019 school inventory.
- **Physical accessibility** captures whether a school exists within walking
  distance, independent of conflict — chronic underprovision compounds
  acute shocks.

## What the score does *not* claim

- It is not a ranking of need within an LGA — wards inside one LGA can vary
  widely. This is acknowledged in the artifact caption.
- It is not predictive — it summarises observed exposure across the
  available data layers.
- It is not weighted by validated outcome data (e.g. enrolment, learning
  outcomes), which are not openly published at LGA level.

## What changes when re-targeted

Targeting the same pipeline at another country requires:

1. Replace `data/raw/05_ocha_boundaries/` with the COD-AB for that country.
2. Replace `data/raw/01_acled_conflict/` with an ACLED export for that country.
3. Replace `data/raw/02_iom_dtm_displacement/` with the relevant DTM round.
4. Replace `data/raw/08_jiaf/` with the JIAF / HNO Education sector PiN +
   Severity workbook for that country (every HNO country publishes one).
5. Replace `data/raw/07_heigit_accessibility/` with the HeiGIT export for
   that ISO3 code.
6. Replace `data/raw/06_unfpa_population/` with the UNFPA / national
   statistical office population file.
7. (Optional) Replace `data/raw/03_immap_schools_2019/` with the local
   school inventory if available; this provides popup context only.
8. Update the BAY filter list at the top of `05_clean_boundaries.py` and
   the name-mapping dictionary in `04_clean_access.py` for the new geography.
9. Re-run `scripts/run_all.py`.

The four assertions in the pipeline (LGA count, BAY total population, BO+YO
LGA count, Adamawa LGA count) are the country-specific integrity checks and
must be updated for the new geography.
