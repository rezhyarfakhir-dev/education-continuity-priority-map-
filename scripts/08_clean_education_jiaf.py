"""Build per-LGA Education sector indicator from OCHA JIAF Nigeria 2026.

This replaces the iMMAP 2019 school-disruption indicator (which had a
state-wide data ceiling for Adamawa with 0 closed schools) with the
official OCHA / Education Cluster figure agreed for the 2026 HNO:

  - Education sector PiN (people in need)              -> absolute scale
  - Education sector intersectoral severity (1-5)      -> comparative intensity

Severity is the indicator that feeds the composite score (it is a
sector-comparable 1-5 scale across all 65 BAY LGAs with no nulls).
PiN is carried through for popup context only.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "08_jiaf" / "jiaf_nigeria_2026.xlsx"
REF = ROOT / "data" / "clean" / "bay_lga_reference.csv"
OUT = ROOT / "data" / "clean" / "education_jiaf_by_lga.csv"

BAY = ["Borno", "Adamawa", "Yobe"]


def main():
    ref = pd.read_csv(REF)

    pin = pd.read_excel(RAW, sheet_name="WS - 3.1 Overall PiN", header=2)
    sev = pd.read_excel(RAW, sheet_name="WS - 3.2 Intersectoral Severity", header=2)
    print(f"jiaf rows in: pin={len(pin)} sev={len(sev)}")

    pin = pin[pin["Admin 1"].isin(BAY)][["Admin 2 P-Code", "Admin 1", "Admin 2", "Education"]]
    pin = pin.rename(columns={
        "Admin 2 P-Code": "pcode",
        "Admin 1": "state",
        "Admin 2": "lga_name",
        "Education": "education_pin",
    })

    sev = sev[sev["Admin 1"].isin(BAY)][["Admin 2 P-Code", "Education"]]
    sev = sev.rename(columns={
        "Admin 2 P-Code": "pcode",
        "Education": "education_severity",
    })

    df = pin.merge(sev, on="pcode", how="inner")
    print(f"BAY rows after merge: {len(df)} (expected 65)")
    assert len(df) == 65, f"expected 65 BAY LGAs, got {len(df)}"

    # Coverage checks
    assert df["education_pin"].isna().sum() == 0, "JIAF Education PiN has nulls in BAY"
    assert df["education_severity"].isna().sum() == 0, "JIAF Education severity has nulls in BAY"

    # state distribution sanity
    counts = df["state"].value_counts().to_dict()
    assert counts.get("Borno") == 27, counts
    assert counts.get("Adamawa") == 21, counts
    assert counts.get("Yobe") == 17, counts

    # Severity is on a 1-5 ordinal scale; min-max-normalise to [0,1]
    s_lo, s_hi = df["education_severity"].min(), df["education_severity"].max()
    df["education_severity_score_norm"] = (
        (df["education_severity"] - s_lo) / (s_hi - s_lo) if s_hi > s_lo else 0.0
    )

    df["education_pin"] = df["education_pin"].round(0).astype("Int64")
    df["education_severity"] = df["education_severity"].astype(float).round(2)

    # join lga_name from reference (canonical) and discard the JIAF lga_name
    df = df.drop(columns=["lga_name", "state"]).merge(
        ref[["pcode", "lga_name", "state"]], on="pcode", how="left"
    )

    print("\nseverity distribution by state:")
    print(pd.crosstab(df["state"], df["education_severity"], margins=True).to_string())

    print("\ntop 5 LGAs by severity then PiN:")
    print(df.sort_values(["education_severity", "education_pin"], ascending=False).head(5)[
        ["lga_name", "state", "education_pin", "education_severity"]
    ].to_string(index=False))

    df = df[["pcode", "lga_name", "state", "education_pin",
             "education_severity", "education_severity_score_norm"]]
    df = df.sort_values("pcode").reset_index(drop=True)
    df.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.name} ({len(df)} rows)")


if __name__ == "__main__":
    main()
