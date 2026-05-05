# Numeric checks

The pipeline contains four hard assertions. Any change in the upstream
data that breaks one of them surfaces immediately on the next run.

## 1. BAY LGA count

`scripts/05_clean_boundaries.py`:

```python
assert len(bay_adm2["features"]) == 65, "expected 65 BAY LGAs"
```

OCHA admin2 has 774 features nationally; filtering to `adm1_name in
{Borno, Adamawa, Yobe}` returns exactly 65 (Borno 27, Adamawa 21, Yobe 17).

## 2. BAY school-age population (5-14)

`scripts/05_clean_boundaries.py`:

```python
assert total_5_14 == 3_926_751, f"unexpected total: {total_5_14}"
```

UNFPA / NPC 2022 projection, sheet `nga_admpop_adm1_2022`:

| State | Pop 5-9 | Pop 10-14 | Pop 5-14 |
|-------|---------|-----------|----------|
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

The scored set excludes Adamawa (21 LGAs) and contains BO+YO = 44 LGAs.

## 4. Adamawa LGA count for the validation-needed set

`scripts/03_clean_schools.py`:

```python
assert len(ad_out) == 21
```

## 5. Adamawa data ceiling

`scripts/03_clean_schools.py`:

```python
assert ad_closed == 0, "expected 0 closed schools in Adamawa (data ceiling)"
```

This is the assertion that *fires the validation_needed branch*. If iMMAP
ever publishes a refreshed school list with non-zero closures in Adamawa,
this assertion will fail and the script must be re-evaluated.

## ACLED sheet name

ACLED's published workbook ships with a default first sheet that contains
the licensing notice ("TOU"). The cleaning script must specify
`sheet_name="Data"` or it will silently parse the wrong sheet.

## DTM sheet name + pcode normalisation

DTM's workbook also requires `sheet_name="Data"`. DTM uses `NGA002001`-style
pcodes; OCHA admin codes use `NG002001`. The cleaning script strips the
leading "A" inside the prefix.

## iMMAP encoding

`encoding="latin-1"`. UTF-8 will raise `UnicodeDecodeError`.

## HeiGIT 5 km coverage

HeiGIT publishes one row per (LGA, distance band) only when the band
captures population. An LGA that does not appear at the 5 km band has 0 %
of its school-age population within 5 km, i.e. weak access = 100 %. The
cleaning script treats a missing 5 km row as 0 % share rather than as a
match failure.
