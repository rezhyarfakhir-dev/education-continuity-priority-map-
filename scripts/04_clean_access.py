"""Build accessibility indicator from HeiGIT 5km share for BAY LGAs.

HeiGIT publishes one row per (LGA, distance band) only when the band
actually captures population. Of the 774 Nigerian LGAs, only 447 appear
at the 5 km band; for the BAY region 30 of 65 LGAs have a 5 km record
and 35 do not.

POLICY (revised 2026-05-05): missing 5 km data is treated as **null**,
not as worst case. The earlier policy filled missing values with
weak_access_pct = 100 % (worst case), which mechanically inflated
composite scores for any LGA outside HeiGIT coverage. The new policy
emits NaN; downstream `06_compute_scores.py` then takes a *pairwise
mean* of the indicators that are available for each LGA. Coverage is
recorded transparently in `heigit_data_present`.

Rationale documented in `docs/missing_data_policy.md`.
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "07_heigit_accessibility" / "NGA_education_access_wide.csv"
REF = ROOT / "data" / "clean" / "bay_lga_reference.csv"
OUT = ROOT / "data" / "clean" / "access_by_lga.csv"

NAME_MAP = {
    "Askira Uba": "Askira/Uba",
}


def main():
    ref = pd.read_csv(REF)
    df = pd.read_csv(RAW)
    print(f"heigit rows in: {len(df):,}")

    adm2 = df[(df["admin_level"] == "ADM2") & (df["range"] == 5000)].copy()
    print(f"ADM2 rows at 5km: {len(adm2)} (national)")
    print(f"ADM2 unique names at 5km: {adm2['name'].nunique()} of 774 total LGAs")

    adm2["name_mapped"] = adm2["name"].astype(str).str.strip().replace(NAME_MAP)
    adm2 = adm2.drop_duplicates(subset=["name_mapped"], keep="first")

    merged = ref.merge(
        adm2[["name_mapped", "school_age_population_share"]],
        left_on="lga_name", right_on="name_mapped", how="left",
    ).drop(columns=["name_mapped"])

    matched = merged["school_age_population_share"].notna().sum()
    missing = 65 - matched
    print(f"\nBAY LGAs with HeiGIT 5km record: {matched} / 65")
    print(f"BAY LGAs missing (treated as NULL, dropped from access mean): {missing}")
    for s in ("Borno", "Adamawa", "Yobe"):
        m = merged[(merged['state'] == s) & merged['school_age_population_share'].isna()].shape[0]
        print(f"  {s}: {m} missing")

    merged["heigit_data_present"] = merged["school_age_population_share"].notna()
    # NEW POLICY: do NOT fill missing values. Leave NaN so composite uses pairwise mean.
    merged["weak_access_pct"] = 100.0 - merged["school_age_population_share"]

    # Normalise only over rows that have data; null stays null.
    present = merged[merged["heigit_data_present"]]
    if len(present) > 0:
        lo, hi = present["weak_access_pct"].min(), present["weak_access_pct"].max()
        if hi > lo:
            merged["access_score_norm"] = np.where(
                merged["heigit_data_present"],
                (merged["weak_access_pct"] - lo) / (hi - lo),
                np.nan,
            )
        else:
            merged["access_score_norm"] = np.where(
                merged["heigit_data_present"], 0.0, np.nan,
            )
    else:
        merged["access_score_norm"] = np.nan

    out = merged[[
        "pcode", "lga_name", "state", "heigit_data_present",
        "school_age_population_share", "weak_access_pct", "access_score_norm",
    ]].sort_values("pcode").reset_index(drop=True)

    print(f"\ntop 5 LGAs with strongest access (lowest weak_access_pct):")
    print(out.dropna(subset=["weak_access_pct"]).nsmallest(5, "weak_access_pct")[
        ["lga_name", "state", "school_age_population_share"]
    ].to_string(index=False))

    out.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
