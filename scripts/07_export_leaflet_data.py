"""Merge priority scores into LGA polygons; emit assets/data.geojson + insights.json."""

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
ASSETS = ROOT / "assets"


def main():
    ASSETS.mkdir(exist_ok=True)
    scores = pd.read_csv(CLEAN / "lga_priority_scores.csv")
    pop = pd.read_csv(CLEAN / "bay_school_age_population.csv")

    # --- LGA polygons with scores baked in ---
    with open(CLEAN / "bay_lga_polygons.geojson", "r", encoding="utf-8") as f:
        polys = json.load(f)

    scored = scores.fillna({"events": 0, "fatalities": 0, "idp_individuals": 0, "idp_sites": 0,
                             "total_schools": 0, "closed_schools": 0,
                             "priority_reason": "", "priority_class": ""}).set_index("pcode").to_dict(orient="index")
    for f in polys["features"]:
        p = f["properties"]
        rec = scored.get(p["adm2_pcode"], {})
        f["properties"] = {
            "pcode": p["adm2_pcode"],
            "lga": p["adm2_name"],
            "state": p["adm1_name"],
            "events": int(rec.get("events", 0) or 0),
            "fatalities": int(rec.get("fatalities", 0) or 0),
            "idp_individuals": int(rec.get("idp_individuals", 0) or 0),
            "idp_sites": int(rec.get("idp_sites", 0) or 0),
            "total_schools": int(rec.get("total_schools", 0) or 0),
            "closed_schools": int(rec.get("closed_schools", 0) or 0),
            "pct_closed": _f(rec.get("pct_closed")),
            "weak_access_pct": _f(rec.get("weak_access_pct")),
            "school_age_within_5km_pct": _f(rec.get("school_age_population_share")),
            "composite_score": _f(rec.get("composite_score")),
            "priority_class": rec.get("priority_class", ""),
            "priority_reason": rec.get("priority_reason", "") or "",
        }
    out_geo = ASSETS / "data.geojson"
    with open(out_geo, "w", encoding="utf-8") as f:
        json.dump(polys, f, separators=(",", ":"), allow_nan=False)
    print(f"wrote {out_geo.name} ({len(polys['features'])} features)")

    # copy state polygons + capitals as-is
    for src_name in ("bay_state_boundaries.geojson", "bay_capitals.geojson"):
        with open(CLEAN / src_name, "r", encoding="utf-8") as f:
            obj = json.load(f)
        with open(ASSETS / src_name.replace("bay_", ""), "w", encoding="utf-8") as f:
            json.dump(obj, f, separators=(",", ":"))
        print(f"wrote {src_name.replace('bay_','')}")

    # --- insights cache for the artifact UI ---
    bo_yo = scores[scores["state"].isin(["Borno", "Yobe"])]
    high = bo_yo[bo_yo["priority_class"] == "high"]
    medium = bo_yo[bo_yo["priority_class"] == "medium"]
    low = bo_yo[bo_yo["priority_class"] == "low"]
    ad = scores[scores["state"] == "Adamawa"]

    borno_events_total = int(scores[scores["state"] == "Borno"]["events"].sum())
    bay_events_total = int(scores["events"].sum())
    borno_share_pct = round(100 * borno_events_total / bay_events_total, 1) if bay_events_total else 0

    bay_idp_total = int(scores["idp_individuals"].sum())

    insights = {
        "total_lgas_bay": int(len(scores)),
        "total_school_age_5_14": int(pop["school_age_5_14"].sum()),
        "school_age_by_state": dict(zip(pop["state"].tolist(), [int(x) for x in pop["school_age_5_14"].tolist()])),
        "scored_lgas": int(len(bo_yo)),
        "validation_needed_lgas": int(len(ad)),
        "priority_counts": {
            "high": int(len(high)),
            "medium": int(len(medium)),
            "low": int(len(low)),
            "validation_needed": int(len(ad)),
        },
        "high_priority_lgas": high.sort_values("composite_score", ascending=False)[
            ["lga_name", "state", "composite_score"]
        ].to_dict(orient="records"),
        "borno_share_of_recent_conflict_pct": borno_share_pct,
        "bay_acled_events_2020_2026": bay_events_total,
        "bay_idp_individuals_dtm_r50": bay_idp_total,
        "data_vintages": {
            "ACLED": "Jan 2020 - Apr 2026",
            "DTM": "Round 50, Oct 2025",
            "iMMAP school list": "Jun 2019",
            "OCHA boundaries": "current",
            "UNFPA population": "2022 projection",
            "HeiGIT accessibility": "Feb 2026",
        },
    }
    with open(ASSETS / "insights.json", "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2, allow_nan=False)
    print(f"wrote insights.json")
    print(json.dumps({k: v for k, v in insights.items() if k != "high_priority_lgas"}, indent=2))


def _f(x):
    if x is None or pd.isna(x):
        return None
    return round(float(x), 2)


if __name__ == "__main__":
    main()
