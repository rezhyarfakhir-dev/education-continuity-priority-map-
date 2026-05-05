# OCHA, Nigeria Administrative Boundaries (COD-AB)

**Files:**
- `nga_admin_boundaries.xlsx`, tabular reference for all admin levels
- `nga_admin_boundaries.geojson/`, GeoJSON files for ADM0, ADM1, ADM2, ADM3, capitals, lines, points, senatorial districts (English and `_em` non-English variants)

**Source:** OCHA Nigeria, COD-AB (Common Operational Datasets, Administrative Boundaries)
**URL:** https://data.humdata.org/dataset/cod-ab-nga
**Vintage:** current (last refresh prior to access on May 2026)
**Licence:** CC BY-IGO

## What we use
- `nga_admin2.geojson` (774 features), ADM2 = LGA polygons; we filter to the 65 BAY LGAs.
- `nga_admin1.geojson` (37 features), state polygons; we filter to BAY 3.
- `nga_admincapitals.geojson` (714 points), used to extract Maiduguri, Yola, Damaturu.

## Schema (admin2 properties)
`adm2_name, adm2_pcode, adm1_name, adm1_pcode, adm0_name, adm0_pcode, area_sqkm, center_lat, center_lon, …`

`adm2_pcode` (e.g. `NG002001`) is the join key for every other dataset in this repo.

## Used by
`scripts/05_clean_boundaries.py` → master reference table and trimmed GeoJSONs in `data/clean/`.
