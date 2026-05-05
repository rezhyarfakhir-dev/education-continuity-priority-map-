"""Build accessibility indicator from HeiGIT 5km share for BAY LGAs.

HeiGIT publishes one row per (LGA, distance band) only when the band actually
captures population. An LGA missing at the 5 km band therefore means 0 % of
the school-age population is within 5 km of an education facility, i.e.
weak_access_pct = 100. We treat missing-at-5km as 0 share (full weak access).
"""

from pathlib import Path
import pandas as pd

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
    print(f"BAY LGAs missing (treated as 0% within 5km = 100% weak access): {missing}")
    for s in ("Borno", "Adamawa", "Yobe"):
        m = merged[(merged['state'] == s) & merged['school_age_population_share'].isna()].shape[0]
        print(f"  {s}: {m} missing")

    merged["heigit_data_present"] = merged["school_age_population_share"].notna()
    merged["school_age_population_share"] = merged["school_age_population_share"].fillna(0.0)
    merged["weak_access_pct"] = 100.0 - merged["school_age_population_share"]

    lo, hi = merged["weak_access_pct"].min(), merged["weak_access_pct"].max()
    merged["access_score_norm"] = (
        (merged["weak_access_pct"] - lo) / (hi - lo) if hi > lo else 0.0
    )

    out = merged[[
        "pcode", "lga_name", "state", "heigit_data_present",
        "school_age_population_share", "weak_access_pct", "access_score_norm",
    ]].sort_values("pcode").reset_index(drop=True)

    print(f"\ntop 5 LGAs with strongest access (lowest weak_access_pct):")
    print(out.nsmallest(5, "weak_access_pct")[
        ["lga_name", "state", "school_age_population_share"]
    ].to_string(index=False))

    out.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
