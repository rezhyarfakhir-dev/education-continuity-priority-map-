"""Compute composite priority score per LGA across all 65 BAY LGAs.

Indicators (each min-max-normalised to [0, 1]):

  1. ACLED political-violence events 2020-2026 (conflict_score_norm)
  2. IOM DTM Round 50 IDP individuals (displacement_score_norm)
  3. OCHA JIAF 2026 Education sector severity (education_severity_score_norm)
  4. Inverse of HeiGIT 5 km school-age accessibility (access_score_norm)
     -- present for 30 of 65 BAY LGAs; null for the other 35

POLICY (revised 2026-05-05): the composite is the **pairwise mean** of
the indicators that are available for each LGA. LGAs without HeiGIT
coverage are scored on the three indicators that are available
(conflict, displacement, severity); they are not penalised by an
imputed worst-case access value, and they are not given a benefit-of-
the-doubt either. The transparency column `score_basis` records which
indicator set each LGA's composite is computed from.

The third indicator was previously derived from iMMAP 2019
`pct_closed`, but iMMAP recorded 0 closed schools state-wide in Adamawa
(a data ceiling, not a finding) which forced 21 LGAs into a separate
"validation needed" class. The OCHA JIAF Education severity layer
covers all 65 BAY LGAs with no nulls and is the official 2026
humanitarian community estimate.

iMMAP school-inventory fields (total_schools, closed_schools, pct_closed)
are still carried through as **context** for popups; they no longer
drive classification.

Rationale documented in `docs/missing_data_policy.md`.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
OUT = CLEAN / "lga_priority_scores.csv"


def main():
    ref = pd.read_csv(CLEAN / "bay_lga_reference.csv")
    conf = pd.read_csv(CLEAN / "conflict_by_lga.csv")[["pcode", "events", "fatalities", "conflict_score_norm"]]
    disp = pd.read_csv(CLEAN / "displacement_by_lga.csv")[["pcode", "idp_individuals", "idp_sites", "displacement_score_norm"]]
    sch = pd.read_csv(CLEAN / "school_disruption_by_lga.csv")[["pcode", "total_schools", "closed_schools", "pct_closed"]]
    acc = pd.read_csv(CLEAN / "access_by_lga.csv")[["pcode", "heigit_data_present", "school_age_population_share", "weak_access_pct", "access_score_norm"]]
    edu = pd.read_csv(CLEAN / "education_jiaf_by_lga.csv")[["pcode", "education_pin", "education_severity", "education_severity_score_norm"]]

    df = ref.merge(conf, on="pcode", how="left") \
            .merge(disp, on="pcode", how="left") \
            .merge(sch, on="pcode", how="left") \
            .merge(acc, on="pcode", how="left") \
            .merge(edu, on="pcode", how="left")

    assert len(df) == 65, f"expected 65 LGAs, got {len(df)}"
    assert df["education_severity_score_norm"].isna().sum() == 0, \
        "JIAF severity must be present for all 65 LGAs"

    # iMMAP fields are now context-only; fill nulls for Adamawa rows
    # (iMMAP did not score them; we no longer pretend it did)
    df["total_schools"] = df["total_schools"].fillna(0).astype(int)
    df["closed_schools"] = df["closed_schools"].fillna(0).astype(int)
    df["pct_closed"] = df["pct_closed"].fillna(0.0)

    # --- composite: pairwise mean of available indicators ---
    score_cols = [
        "conflict_score_norm",
        "displacement_score_norm",
        "education_severity_score_norm",
        "access_score_norm",
    ]
    # mean(skipna=True) is the pandas default; explicit for clarity
    df["composite_score"] = df[score_cols].mean(axis=1, skipna=True)
    df["indicators_used"] = df[score_cols].notna().sum(axis=1).astype(int)
    df["score_basis"] = df["indicators_used"].apply(
        lambda n: "4_indicators" if n == 4 else "3_indicators_no_heigit"
    )
    assert df["composite_score"].isna().sum() == 0, \
        "composite must be defined for all 65 LGAs (3 of 4 indicators always available)"

    print("\nscore_basis distribution:")
    print(df["score_basis"].value_counts().to_string())

    # tercile-classify across the full 65-LGA scored set
    q1, q2 = df["composite_score"].quantile([1/3, 2/3]).tolist()
    print(f"\nBAY composite score terciles: q1={q1:.3f}, q2={q2:.3f}")

    def classify(x):
        if x >= q2:
            return "high"
        if x >= q1:
            return "medium"
        return "low"

    df["priority_class"] = df["composite_score"].apply(classify)

    print("\npriority class counts:")
    print(df["priority_class"].value_counts().to_string())

    print("\nstate x class:")
    print(pd.crosstab(df["state"], df["priority_class"], margins=True).to_string())

    print("\nstate x class x score_basis:")
    print(pd.crosstab(
        [df["state"], df["score_basis"]], df["priority_class"], margins=True,
    ).to_string())

    print("\ntop 10 by composite score:")
    print(df.nlargest(10, "composite_score")[
        ["lga_name", "state", "events", "idp_individuals", "education_severity",
         "weak_access_pct", "score_basis", "composite_score", "priority_class"]
    ].to_string(index=False))

    df = df.sort_values(["state", "pcode"]).reset_index(drop=True)
    df.to_csv(OUT, index=False)
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
