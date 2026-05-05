"""Compute composite priority score per LGA; tercile-classify; Adamawa = validation_needed."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
OUT = CLEAN / "lga_priority_scores.csv"


def main():
    ref = pd.read_csv(CLEAN / "bay_lga_reference.csv")
    conf = pd.read_csv(CLEAN / "conflict_by_lga.csv")[["pcode", "events", "fatalities", "conflict_score_norm"]]
    disp = pd.read_csv(CLEAN / "displacement_by_lga.csv")[["pcode", "idp_individuals", "idp_sites", "displacement_score_norm"]]
    sch = pd.read_csv(CLEAN / "school_disruption_by_lga.csv")[["pcode", "total_schools", "closed_schools", "pct_closed", "school_disruption_score_norm"]]
    acc = pd.read_csv(CLEAN / "access_by_lga.csv")[["pcode", "heigit_data_present", "school_age_population_share", "weak_access_pct", "access_score_norm"]]

    df = ref.merge(conf, on="pcode", how="left") \
            .merge(disp, on="pcode", how="left") \
            .merge(sch, on="pcode", how="left") \
            .merge(acc, on="pcode", how="left")

    assert len(df) == 65

    # Adamawa rows are validation_needed because school disruption indicator is unavailable
    is_adamawa = df["state"] == "Adamawa"

    # composite for non-Adamawa = mean of 4 normalised indicators
    score_cols = ["conflict_score_norm", "displacement_score_norm",
                  "school_disruption_score_norm", "access_score_norm"]
    df["composite_score"] = df[score_cols].mean(axis=1)
    df.loc[is_adamawa, "composite_score"] = pd.NA

    # tercile-classify the BO+YO scored set
    scored = df[~is_adamawa].copy()
    q1, q2 = scored["composite_score"].quantile([1/3, 2/3]).tolist()
    print(f"BO+YO composite score terciles: q1={q1:.3f}, q2={q2:.3f}")

    def classify(x):
        if pd.isna(x):
            return "validation_needed"
        if x >= q2:
            return "high"
        if x >= q1:
            return "medium"
        return "low"

    df["priority_class"] = df["composite_score"].apply(classify)
    df.loc[is_adamawa, "priority_class"] = "validation_needed"

    df["priority_reason"] = ""
    df.loc[is_adamawa, "priority_reason"] = (
        "iMMAP 2019 lists all Adamawa schools as 'Open' (no closed records); "
        "school-disruption indicator unavailable, field validation required."
    )

    print(f"\npriority class counts:")
    print(df["priority_class"].value_counts().to_string())

    print(f"\ntop 5 by composite score:")
    print(df.nlargest(5, "composite_score")[
        ["lga_name", "state", "events", "idp_individuals", "pct_closed", "weak_access_pct", "composite_score", "priority_class"]
    ].to_string(index=False))

    df = df.sort_values(["state", "pcode"]).reset_index(drop=True)
    df.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
