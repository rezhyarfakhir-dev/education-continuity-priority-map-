"""Build school-disruption indicator from iMMAP 2019 list (BO+YO scored, AD validation-needed)."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "03_immap_schools_2019" / "nga_north_east_school_list_jun2019" / "nga_north_east_education_sector_school_list_19062019.csv"
REF = ROOT / "data" / "clean" / "bay_lga_reference.csv"
OUT_MAIN = ROOT / "data" / "clean" / "school_disruption_by_lga.csv"
OUT_AD = ROOT / "data" / "clean" / "adamawa_validation_needed.csv"

BAY = ["Borno", "Adamawa", "Yobe"]


def main():
    ref = pd.read_csv(REF)
    df = pd.read_csv(RAW, encoding="latin-1", low_memory=False)
    print(f"immap rows in: {len(df):,}")

    bay = df[df["State Name"].isin(BAY)].copy()
    bay["status"] = bay["School Status"].astype(str).str.strip().str.lower().replace({"close": "closed"})
    print(f"BAY rows: {len(bay):,}")
    print("status x state:")
    print(pd.crosstab(bay["State Name"], bay["status"], margins=True).to_string())

    # confirm Adamawa data ceiling
    ad = bay[bay["State Name"] == "Adamawa"]
    ad_closed = (ad["status"] == "closed").sum()
    print(f"\nAdamawa: {len(ad)} schools, {ad_closed} marked closed")
    assert ad_closed == 0, "expected 0 closed schools in Adamawa (data ceiling)"

    # --- BO+YO score ---
    boyo = bay[bay["State Name"].isin(["Borno", "Yobe"])].copy()
    agg = boyo.groupby("LGA Pcode").agg(
        total_schools=("School Name", "size"),
        closed_schools=("status", lambda s: (s == "closed").sum()),
    ).reset_index().rename(columns={"LGA Pcode": "pcode"})
    agg["pct_closed"] = (agg["closed_schools"] / agg["total_schools"]) * 100

    # join onto BO+YO LGAs from reference
    boyo_ref = ref[ref["state"].isin(["Borno", "Yobe"])][["pcode", "lga_name", "state"]]
    merged = boyo_ref.merge(agg, on="pcode", how="left")
    merged["total_schools"] = merged["total_schools"].fillna(0).astype(int)
    merged["closed_schools"] = merged["closed_schools"].fillna(0).astype(int)
    merged["pct_closed"] = merged["pct_closed"].fillna(0.0)

    print(f"\nBO+YO LGAs covered: {len(merged)} (expected 44)")
    assert len(merged) == 44

    lo, hi = merged["pct_closed"].min(), merged["pct_closed"].max()
    merged["school_disruption_score_norm"] = (
        (merged["pct_closed"] - lo) / (hi - lo) if hi > lo else 0.0
    )

    print(f"\ntop 5 BO+YO LGAs by % closed:")
    print(merged.nlargest(5, "pct_closed")
                [["lga_name", "state", "total_schools", "closed_schools", "pct_closed"]].to_string(index=False))

    merged = merged.sort_values("pcode").reset_index(drop=True)
    merged.to_csv(OUT_MAIN, index=False)

    # --- Adamawa validation-needed list ---
    ad_ref = ref[ref["state"] == "Adamawa"][["pcode", "lga_name", "state"]].copy()
    # add school totals for context
    ad_counts = bay[bay["State Name"] == "Adamawa"].groupby("LGA Pcode").size().rename("schools_listed").reset_index()
    ad_counts.columns = ["pcode", "schools_listed"]
    ad_out = ad_ref.merge(ad_counts, on="pcode", how="left")
    ad_out["schools_listed"] = ad_out["schools_listed"].fillna(0).astype(int)
    ad_out["data_status"] = "validation_needed"
    ad_out["reason"] = (
        "iMMAP 2019 lists all 4,011 Adamawa schools as 'Open' with no closed records. "
        "School functionality cannot be inferred; field validation required."
    )
    ad_out = ad_out.sort_values("pcode").reset_index(drop=True)
    print(f"\nAdamawa validation-needed LGAs: {len(ad_out)} (expected 21)")
    assert len(ad_out) == 21
    ad_out.to_csv(OUT_AD, index=False)

    print(f"\nwrote {OUT_MAIN.name} and {OUT_AD.name}")


if __name__ == "__main__":
    main()
