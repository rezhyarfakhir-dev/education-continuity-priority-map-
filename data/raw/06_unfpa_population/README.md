# UNFPA — Nigeria Population by Age and Sex (2022)

**File:** `nga_admpop_2022.xlsx`
**Source:** UNFPA / National Population Commission of Nigeria, via HDX
**URL:** https://data.humdata.org/dataset/cod-ps-nga
**Vintage:** 2022 projection (baseline 2006 census)
**Licence:** Open
**Coverage:** national, ADM0 + ADM1 (state-level only — there is no ADM2/LGA breakdown in this dataset).

## Sheets used
`nga_admpop_adm1_2022` (37 rows = 36 states + FCT) — we filter to BAY 3.

## Fields used
`ADM1_EN, T_TL` (total population), `T_05_09`, `T_10_14`. We sum `T_05_09 + T_10_14` to get the school-age population (5-14).

## Why state-level only
This dataset does not provide an LGA breakdown. We therefore use it as state-level context (one number per state) rather than as an indicator in the per-LGA composite score.

## BAY school-age 5-14 (verified)
- Borno: 1,555,673
- Adamawa: 1,331,643
- Yobe: 1,039,435
- **Total: 3,926,751**

This is the number cited in the artifact's insight panels.

## Used by
`scripts/05_clean_boundaries.py` → `data/clean/bay_school_age_population.csv`
