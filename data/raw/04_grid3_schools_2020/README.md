# GRID3 — Nigeria Education Facilities (2020)

**File:** `nga_grid3_education_facilities.xlsx`
**Source:** GRID3 (Geo-Referenced Infrastructure and Demographic Data for Development)
**URL:** https://data.grid3.org/datasets/GRID3::nigeria-education-facilities
**Vintage:** 2020
**Licence:** CC BY 4.0
**Coverage:** national; 204,513 facilities, but only Adamawa (6,195) and Yobe (1,832) in BAY — Borno is not present.

## Schema
`id, state_code, source, name, ward_code, category, subtype, management, education, poi_type, no_of_teac, no_of_stud, global_id, layer`

`state_code` uses two-letter codes: `BO` (Borno — absent), `AD`, `YO`.

## Why we don't use it as a primary score input
- Missing Borno makes it unsuitable as the school-disruption indicator (which must cover all 65 BAY LGAs).
- We retain it in the repo as a reference inventory and as a possible cross-check for school presence in Adamawa and Yobe.

## Used by
Not currently consumed by the cleaning pipeline. Held in the repo for transparency and for any future cross-check of school presence.
