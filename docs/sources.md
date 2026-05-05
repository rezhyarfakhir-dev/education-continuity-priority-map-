# Sources

Each `data/raw/0X_*/README.md` contains the full per source detail (URL,
vintage, schema, licence, limitations). This file is the consolidated
overview.

| # | Source | File | Vintage | Licence |
|---|--------|------|---------|---------|
| 01 | ACLED political violence events, Nigeria | `nigeria_political_violence_events_apr2026.xlsx` | Apr 2026 | CC BY-NC-SA 4.0 |
| 02 | IOM DTM Site Assessment, Nigeria, Round 50 | `dtm_nigeria_site_assessment_round50.xlsx` | Oct 2025 | Open with citation |
| 03 | iMMAP / Education Sector school list, North East Nigeria *(context only; superseded by 08)* | `nga_north_east_education_sector_school_list_19062019.csv` | Jun 2019 | CC BY |
| 04 | GRID3 Nigeria education facilities (reference, not in score) | `nga_grid3_education_facilities.xlsx` | 2020 | CC BY 4.0 |
| 05 | OCHA Nigeria COD-AB administrative boundaries | `nga_admin_boundaries.xlsx` plus `.geojson/` | current | CC BY-IGO |
| 06 | UNFPA / NPC Nigeria population by age and sex | `nga_admpop_2022.xlsx` | 2022 projection | Open |
| 07 | HeiGIT Global Education Accessibility Indicators, Nigeria | `NGA_education_access_wide.csv` | Feb 2026 | ODbL |
| 08 | **OCHA JIAF Nigeria 2026, Education sector PiN and Severity** | `jiaf_nigeria_2026.xlsx` | 2026 HNO | Open with citation |

All eight sources were retrieved during late April and early May 2026. The
exact files used to compute the published map are stored under `data/raw/`
in this repository.

Source 03 (iMMAP) was originally the third indicator but contained a state
wide data ceiling for Adamawa: zero closures were recorded across all 21
LGAs. Source 08 (OCHA JIAF) is the current third indicator and resolves
that ceiling. Source 03 fields are still carried through to the popup as
context but no longer drive the composite score. See `adamawa_decision.md`.

## Citation guidance for re-use

If you re-use the cleaned outputs in `data/clean/` or the figures shown on
the published page, please cite the upstream source for that indicator
(per the table above) in addition to this repository.
