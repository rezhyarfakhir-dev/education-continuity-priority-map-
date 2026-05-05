# 08, OCHA JIAF Nigeria 2026 (Humanitarian Needs PiN and Severity)

## Source

- **Publisher:** UN OCHA Nigeria, in coordination with the Humanitarian
  Country Team and all sector Clusters (Education, Health, WASH, Food
  Security, Shelter, Protection, etc.).
- **Methodology:** Joint Intersectoral Analysis Framework (JIAF 2.0).
  See `JIAF-2-Technical-Manual_Final-for-2025-HPC.pdf` on the same
  HDX page.
- **HDX dataset:** https://data.humdata.org/dataset/nga-jiaf-humanitarian-needs-pin-and-severity
- **Direct file:** https://data.humdata.org/dataset/608e1e20-c459-4afc-9f73-f2ad6ce4d782/resource/66b7a3d5-7536-439e-9469-b433619f7b08/download/jiaf_nigeria_2026.xlsx
- **Vintage:** 2026 HNO cycle (downloaded 5 May 2026)
- **Licence:** Open with citation (UN OCHA / HDX standard)

## File saved

```
jiaf_nigeria_2026.xlsx        ~146 KB
```

## Sheets used

| Sheet | Header row | Used columns |
|---|---|---|
| `WS - 3.1 Overall PiN` | row index 2 | `Admin 1`, `Admin 2 P-Code`, `Education` |
| `WS - 3.2 Intersectoral Severity` | row index 2 | `Admin 1`, `Admin 2 P-Code`, `Education` |

The spreadsheet has two header rows above the data and one section header
above that (group labels span columns). When loading, pass `header=2`.

## Coverage of the BAY scope

| State | LGAs in JIAF 2026 | Education PiN nulls | Education Severity nulls |
|---|---|---|---|
| Borno | 27 | 0 | 0 |
| Adamawa | 21 | 0 | 0 |
| Yobe | 17 | 0 | 0 |
| **BAY total** | **65** | **0** | **0** |

This is the dataset that **resolves the Adamawa data ceiling** present in
the iMMAP 2019 school list (source 03). See `docs/adamawa_decision.md`.

## Key fields

- **Education PiN:** Education sector "People in Need" estimate (count of
  individuals identified by the Education Cluster as needing assistance).
- **Education Severity:** Education sector intersectoral severity score
  on the standard humanitarian 1 to 5 scale: 1 = Minimal, 2 = Stress,
  3 = Severe, 4 = Extreme, 5 = Catastrophic.

In the BAY scope the observed Education Severity values are 2, 3, and 4.
Adamawa LGAs span 2 and 3, which is consistent with the conflict and
displacement signal seen independently.

## How it is used in this pipeline

`scripts/08_clean_education_jiaf.py` produces
`data/clean/education_jiaf_by_lga.csv`. The min max normalised severity
score (`education_severity_score_norm`) is **the third indicator** in the
composite priority score (replacing the iMMAP `pct_closed` indicator).
The raw `education_pin` field is carried through to the published popup
as a context number.

## Pcode format

`Admin 2 P-Code` matches OCHA COD-AB exactly (`NG002001` style); no
normalisation needed.

## Provenance note

JIAF outputs are the *agreed* humanitarian community estimate for the year:
the figure used by donors, OCHA pooled funds, the Education Cluster's own
HRP project sheets, and partner allocations. Using this indicator means
the priority map reflects the humanitarian system's own sectoral judgment,
not a derivation from one partner's school inventory.
