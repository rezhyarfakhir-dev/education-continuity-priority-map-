# IOM DTM, Site Assessment Round 50 (Nigeria)

**File:** `dtm_nigeria_site_assessment_round50.xlsx`
**Source:** International Organization for Migration, Displacement Tracking Matrix (DTM), via HDX
**URL:** https://data.humdata.org/dataset/iom-dtm-nigeria-site-assessment
**Vintage:** Round 50 (October 2025)
**Licence:** Public, use permitted with citation
**Coverage:** displacement sites across Nigeria; we filter to Borno, Adamawa, Yobe.

## Schema (sheet `Data`)
62 columns including `State, State code, LGA, LGA code, Site name, Latitude, Longitude, IDP Households, IDP Individuals, Returnee Households, Returnee Individuals, Total Households, Individuals`.

Each row is one displacement site.

## Notes
- DTM LGA codes use the format `NGA002001` (with leading "A"); OCHA admin codes use `NG002001`. The cleaning script strips the leading "A" to align them.
- 2,241 of 3,128 sites are in BAY (Borno 935, Adamawa 833, Yobe 473).

## Limitations
- Site coverage updates round-to-round; some sites in earlier rounds may have closed or been merged.
- Site-level coordinates are published per IOM DTM standards; we aggregate to LGA level only.

## Used by
`scripts/02_clean_displacement.py` → `data/clean/displacement_by_lga.csv`
