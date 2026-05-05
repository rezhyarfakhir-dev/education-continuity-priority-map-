"""Aggregate IOM DTM Round 50 displacement sites to LGA level for BAY states."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "02_iom_dtm_displacement" / "dtm_nigeria_site_assessment_round50.xlsx"
REF = ROOT / "data" / "clean" / "bay_lga_reference.csv"
OUT = ROOT / "data" / "clean" / "displacement_by_lga.csv"

BAY = ["Borno", "Adamawa", "Yobe"]


def main():
    ref = pd.read_csv(REF)
    df = pd.read_excel(RAW, sheet_name="Data")
    print(f"dtm rows in: {len(df):,}")

    bay = df[df["State"].astype(str).str.strip().isin(BAY)].copy()
    print(f"BAY sites: {len(bay):,}  by state: {bay['State'].value_counts().to_dict()}")

    # find LGA pcode column
    lga_pcode_col = None
    for c in ("LGA code", "LGA Code", "LGA Pcode", "Lga Code"):
        if c in bay.columns:
            lga_pcode_col = c
            break
    assert lga_pcode_col is not None, f"no LGA pcode column in: {list(bay.columns)[:20]}"
    print(f"using lga pcode column: {lga_pcode_col!r}")

    # DTM uses NGA002001; OCHA uses NG002001. Strip leading 'A' inside NGA prefix.
    sample_before = bay[lga_pcode_col].dropna().astype(str).head(3).tolist()
    bay["pcode_norm"] = bay[lga_pcode_col].astype(str).str.replace(r"^NGA", "NG", regex=True)
    sample_after = bay["pcode_norm"].head(3).tolist()
    print(f"pcode sample before: {sample_before}")
    print(f"pcode sample after:  {sample_after}")

    # find IDP individuals column
    idp_col = None
    for c in ("IDP Individuals", "Individuals", "IDPIndividuals"):
        if c in bay.columns:
            idp_col = c
            break
    assert idp_col is not None, f"no IDP individuals column"
    print(f"using IDP column: {idp_col!r}")

    bay[idp_col] = pd.to_numeric(bay[idp_col], errors="coerce").fillna(0)

    agg = bay.groupby("pcode_norm").agg(
        idp_individuals=(idp_col, "sum"),
        idp_sites=(idp_col, "size"),
    ).reset_index().rename(columns={"pcode_norm": "pcode"})

    merged = ref[["pcode", "lga_name", "state"]].merge(agg, on="pcode", how="left")
    merged["idp_individuals"] = merged["idp_individuals"].fillna(0).astype(int)
    merged["idp_sites"] = merged["idp_sites"].fillna(0).astype(int)

    matched = (merged["idp_sites"] > 0).sum()
    print(f"\nLGAs with at least 1 displacement site: {matched} of 65")

    lo, hi = merged["idp_individuals"].min(), merged["idp_individuals"].max()
    merged["displacement_score_norm"] = (
        (merged["idp_individuals"] - lo) / (hi - lo) if hi > lo else 0.0
    )

    print(f"\ntop 5 LGAs by IDP individuals:")
    print(merged.nlargest(5, "idp_individuals")
                [["lga_name", "state", "idp_sites", "idp_individuals"]].to_string(index=False))

    merged = merged.sort_values("pcode").reset_index(drop=True)
    merged.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
