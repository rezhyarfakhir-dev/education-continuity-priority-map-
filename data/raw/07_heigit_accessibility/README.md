# HeiGIT, Nigeria Education Accessibility (2026)

**File:** `NGA_education_access_wide.csv`
**Source:** HeiGIT (Heidelberg Institute for Geoinformation Technology), Global Healthcare/Education Access Indicators
**URL:** https://heigit.org/global-healthcare-access-indicators-visualization/
**Vintage:** February 2026
**Licence:** ODbL (Open Database Licence)
**Coverage:** Nigeria, ADM0 + ADM1 + ADM2.

## Schema
`name, iso, id, country, admin_level, category, range_type, range, population, school_age_population, school_age_population_share, school_age_population_interval, school_age_population_interval_share, population_share, population_interval, population_interval_share`

For each LGA, the dataset provides multiple rows, one per distance band (5km, 10km, 15km, 20km, 25km, 30km, 35km, 40km, 45km, 50km).

## Field we use
`school_age_population_share` at `range = 5000` (5km): the percentage of the LGA's school-age population that lives within 5km of an education facility.

We invert it to obtain `weak_access_pct = 100 - school_age_population_share` so that a higher number means weaker access.

## Name-matching
HeiGIT provides 726 unique ADM2 names; OCHA admin2 has 65 BAY LGAs of which 51 match by exact name. The remaining 14 require an explicit name-mapping dictionary (slash variants, transliteration differences). The mapping is in `scripts/04_clean_access.py`.

## Used by
`scripts/04_clean_access.py` → `data/clean/access_by_lga.csv`
