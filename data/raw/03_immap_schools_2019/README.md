# iMMAP, North East Nigeria School List (2019)

**File:** `nga_north_east_school_list_jun2019/nga_north_east_education_sector_school_list_19062019.csv`
**Source:** iMMAP, Education Sector working group, via HDX
**URL:** https://data.humdata.org/dataset/north-east-nigeria-education-sector-school-list
**Vintage:** 19 June 2019
**Licence:** Creative Commons Attribution
**Coverage:** Borno, Adamawa, Yobe, 7,229 schools

## Schema
`State Pcode, State Name, LGA Pcode, LGA Name, Ward Name, School Name, School Level, School Type, School Status`

`School Status` values (after normalisation): `open`, `closed`.
- Borno reports both `open` and `closed`.
- Yobe reports `open` and a value `Close` that we normalise to `closed`.
- Adamawa reports only `Open` for all 4,011 schools, this is the data ceiling that drives the "validation needed" classification.

## Limitations
- Six years old. School status, in particular, is the weakest layer in the pipeline.
- The Adamawa records do not distinguish open from closed schools, so this source cannot support an Adamawa school-disruption score.
- File encoding is latin-1.

## Used by
`scripts/03_clean_schools.py` → `data/clean/school_disruption_by_lga.csv` (BO+YO) and `data/clean/adamawa_validation_needed.csv`
