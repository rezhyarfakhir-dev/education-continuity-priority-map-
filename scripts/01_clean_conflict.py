"""Aggregate ACLED political-violence events to LGA level for BAY states (2020-2026)."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "01_acled_conflict" / "nigeria_political_violence_events_apr2026.xlsx"
REF = ROOT / "data" / "clean" / "bay_lga_reference.csv"
OUT = ROOT / "data" / "clean" / "conflict_by_lga.csv"

BAY = ["Borno", "Adamawa", "Yobe"]
YEAR_FROM = 2020


def main():
    ref = pd.read_csv(REF)
    df = pd.read_excel(RAW, sheet_name="Data")
    print(f"acled rows in: {len(df):,}")

    bay = df[df["Admin1"].isin(BAY) & (df["Year"] >= YEAR_FROM)].copy()
    print(f"BAY rows {YEAR_FROM}-2026: {len(bay):,}")
    print(f"BAY events: {int(bay['Events'].sum()):,}, fatalities: {int(bay['Fatalities'].sum()):,}")

    agg = (
        bay.groupby(["Admin2 Pcode", "Admin2", "Admin1"], as_index=False)
        [["Events", "Fatalities"]]
        .sum()
        .rename(columns={
            "Admin2 Pcode": "pcode",
            "Admin2": "lga_name_acled",
            "Admin1": "state",
            "Events": "events",
            "Fatalities": "fatalities",
        })
    )

    # join onto the 65-LGA reference so LGAs with zero events still appear
    merged = ref[["pcode", "lga_name", "state"]].merge(
        agg[["pcode", "events", "fatalities"]], on="pcode", how="left"
    )
    merged["events"] = merged["events"].fillna(0).astype(int)
    merged["fatalities"] = merged["fatalities"].fillna(0).astype(int)

    assert len(merged) == 65, f"expected 65 LGAs, got {len(merged)}"
    print(f"LGAs with zero events 2020-26: {(merged['events'] == 0).sum()}")

    lo, hi = merged["events"].min(), merged["events"].max()
    merged["conflict_score_norm"] = (merged["events"] - lo) / (hi - lo) if hi > lo else 0.0
    merged = merged.sort_values("pcode").reset_index(drop=True)

    print(f"\ntop 5 LGAs by events:")
    print(merged.nlargest(5, "events")[["lga_name", "state", "events", "fatalities"]].to_string(index=False))

    merged.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
