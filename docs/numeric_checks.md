# Numeric checks

The pipeline contains hard assertions across `05_clean_boundaries.py`,
`03_clean_schools.py`, `08_clean_education_jiaf.py`, and
`06_compute_scores.py`. Any change in the upstream data that breaks one
of them surfaces immediately on the next run.

## 1. BAY LGA count

`scripts/05_clean_boundaries.py`:

```python
assert len(bay_adm2["features"]) == 65, "expected 65 BAY LGAs"
```

OCHA admin2 has 774 features nationally; filtering to `adm1_name in
{Borno, Adamawa, Yobe}` returns exactly 65 (Borno 27, Adamawa 21, Yobe 17).

## 2. BAY school age population (5 to 14)

`scripts/05_clean_boundaries.py`:

```python
assert total_5_14 == 3_926_751, f"unexpected total: {total_5_14}"
```

UNFPA / NPC 2022 projection, sheet `nga_admpop_adm1_2022`:

| State | Pop 5 to 9 | Pop 10 to 14 | Pop 5 to 14 |
|-------|------------|--------------|-------------|
| Borno | (sums to) | (sums to) | 1,555,673 |
| Adamawa | | | 1,331,643 |
| Yobe | | | 1,039,435 |
| **BAY** | | | **3,926,751** |

This number is cited in the artifact's "displacement at scale" insight panel.

## 3. BO+YO LGA count for the scored set

`scripts/03_clean_schools.py`:

```python
assert len(merged) == 44
```

The historical (pre JIAF) scored set excluded Adamawa (21 LGAs) and
contained BO+YO = 44 LGAs.

## 4. Adamawa LGA count for the validation needed set

`scripts/03_clean_schools.py`:

```python
assert len(ad_out) == 21
```

## 5. Adamawa data ceiling (kept as a regression detector)

`scripts/03_clean_schools.py`:

```python
assert ad_closed == 0, "expected 0 closed schools in Adamawa (data ceiling)"
```

The assertion is kept even though iMMAP no longer drives the composite. It
documents the historical reason JIAF was added. If iMMAP ever publishes a
refreshed school list with non zero closures in Adamawa, this assertion
fails and the pipeline is forced into manual review.

## 6. JIAF BAY coverage (the score driving indicator)

`scripts/08_clean_education_jiaf.py`:

```python
assert len(df) == 65, f"expected 65 BAY LGAs, got {len(df)}"
assert df["education_pin"].isna().sum() == 0, "JIAF Education PiN has nulls in BAY"
assert df["education_severity"].isna().sum() == 0, "JIAF Education severity has nulls in BAY"
assert counts.get("Borno") == 27
assert counts.get("Adamawa") == 21
assert counts.get("Yobe") == 17
```

If OCHA restructures the JIAF workbook (sheet rename, column rename) or
if the BAY scope changes in a future HNO, one of these fires.

## 7. Composite completeness after JIAF swap

`scripts/06_compute_scores.py`:

```python
assert df["education_severity_score_norm"].isna().sum() == 0
assert df["composite_score"].isna().sum() == 0
```

This guarantees every one of the 65 LGAs has a classifiable composite
score. The "validation needed" branch from the prior pipeline is therefore
structurally impossible to reach.

## ACLED sheet name

ACLED's published workbook ships with a default first sheet that contains
the licensing notice ("TOU"). The cleaning script must specify
`sheet_name="Data"` or it will silently parse the wrong sheet.

## DTM sheet name and pcode normalisation

DTM's workbook also requires `sheet_name="Data"`. DTM uses `NGA002001`
style pcodes; OCHA admin codes use `NG002001`. The cleaning script strips
the leading "A" inside the prefix.

## iMMAP encoding

`encoding="latin-1"`. UTF-8 will raise `UnicodeDecodeError`.

## HeiGIT 5 km coverage

HeiGIT publishes one row per (LGA, distance band) only when the band
captures population. An LGA that does not appear at the 5 km band may
either (a) genuinely have no school age population within 5 km, or (b)
have no facility data near it at all. The two cases are not
distinguishable from the published file alone.

For BAY, 30 of 65 LGAs have a 5 km row; the other **35 are dropped from
the access indicator and scored on the remaining 3 indicators using a
pairwise mean** (`skipna=True`). Each row in
`data/clean/lga_priority_scores.csv` carries a `score_basis` column
(`4_indicators` or `3_indicators_no_heigit`) and the count of indicators
used (`indicators_used`), and both are exported into the geojson popup.
See `docs/missing_data_policy.md`.
