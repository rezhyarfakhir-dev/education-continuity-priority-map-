# Adamawa: validation needed, not classified

## What the data shows

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

## Why this is a data ceiling, not a finding

There is no plausible operational reading in which exactly zero of 4,011
schools across 21 LGAs are closed. The most likely explanation is that
the partner who contributed the Adamawa records to the 2019 sectoral
exercise reported only operational schools, or did not perform the
closure-status field. Either way, the source carries no information about
school disruption in Adamawa.

## What we do about it

We do **not** silently impute. We do **not** drop the LGAs from the map.
We classify the 21 Adamawa LGAs as **validation needed** (grey on the
choropleth) and exclude them from the tercile thresholds. The popup for
each Adamawa LGA contains the explanatory note:

> iMMAP 2019 lists all Adamawa schools as 'Open' (no closed records);
> school-disruption indicator unavailable, field validation required.

This is enforced in code by:

1. `scripts/03_clean_schools.py` — `assert ad_closed == 0` (the assertion
   that detects the ceiling) and a separate output file
   `data/clean/adamawa_validation_needed.csv` listing the 21 LGAs with
   the reason field.
2. `scripts/06_compute_scores.py` — sets `composite_score = NA` and
   `priority_class = "validation_needed"` for any row where `state ==
   "Adamawa"`.

## What this demonstrates about the method

The method is honest about source limits. A scoring pipeline that
silently averaged a `pct_closed = 0.0` for Adamawa would have produced a
clean-looking choropleth with Adamawa appearing as the safest state in
the region — a result that is the opposite of what the conflict and
displacement layers show. Surfacing the ceiling and re-routing those
LGAs to a separate "validation needed" class is what makes the output
defensible.

In any operational deployment, the validation-needed list would be the
priority queue for a short field-validation engagement before the
classification was finalised.
