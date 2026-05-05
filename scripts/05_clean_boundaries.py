"""Build the BAY master reference table and trimmed GeoJSONs from OCHA + UNFPA."""

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_OCHA = ROOT / "data" / "raw" / "05_ocha_boundaries" / "nga_admin_boundaries.geojson"
RAW_UNFPA = ROOT / "data" / "raw" / "06_unfpa_population" / "nga_admpop_2022.xlsx"
OUT = ROOT / "data" / "clean"

BAY = ["Borno", "Adamawa", "Yobe"]


def load_geojson(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_features(gj, predicate):
    return {
        "type": "FeatureCollection",
        "features": [f for f in gj["features"] if predicate(f["properties"])],
    }


def trim_props(features, keep):
    for f in features:
        p = f["properties"]
        f["properties"] = {k: p.get(k) for k in keep}
    return features


def main():
    # --- 1. ADM2 (LGA polygons) ---
    adm2 = load_geojson(RAW_OCHA / "nga_admin2.geojson")
    print(f"adm2 features: {len(adm2['features'])}")

    bay_adm2 = filter_features(adm2, lambda p: p.get("adm1_name") in BAY)
    print(f"BAY LGA features: {len(bay_adm2['features'])}")
    assert len(bay_adm2["features"]) == 65, "expected 65 BAY LGAs"

    # build the master reference table from properties
    rows = []
    for f in bay_adm2["features"]:
        p = f["properties"]
        rows.append({
            "pcode": p["adm2_pcode"],
            "lga_name": p["adm2_name"],
            "state": p["adm1_name"],
            "area_km2": p.get("area_sqkm"),
            "center_lat": p.get("center_lat"),
            "center_lon": p.get("center_lon"),
        })
    ref = pd.DataFrame(rows).sort_values("pcode").reset_index(drop=True)
    print(f"\nreference table: {len(ref)} rows")
    print(ref["state"].value_counts().to_string())
    ref.to_csv(OUT / "bay_lga_reference.csv", index=False)

    # trim polygon properties for the map
    keep = ["adm2_pcode", "adm2_name", "adm1_name"]
    bay_adm2["features"] = trim_props(bay_adm2["features"], keep)
    with open(OUT / "bay_lga_polygons.geojson", "w", encoding="utf-8") as f:
        json.dump(bay_adm2, f, separators=(",", ":"))

    # --- 2. ADM1 (state polygons) ---
    adm1 = load_geojson(RAW_OCHA / "nga_admin1.geojson")
    bay_adm1 = filter_features(adm1, lambda p: p.get("adm1_name") in BAY)
    bay_adm1["features"] = trim_props(bay_adm1["features"], ["adm1_pcode", "adm1_name"])
    with open(OUT / "bay_state_boundaries.geojson", "w", encoding="utf-8") as f:
        json.dump(bay_adm1, f, separators=(",", ":"))
    print(f"BAY state polygons: {len(bay_adm1['features'])}")

    # --- 3. Capitals (filter to BAY state capitals) ---
    caps = load_geojson(RAW_OCHA / "nga_admincapitals.geojson")
    target_caps = {"Maiduguri", "Yola", "Damaturu"}
    # try common name fields
    bay_caps_features = []
    for f in caps["features"]:
        p = f["properties"]
        for field in ("name", "settlement", "capital", "adm2_name", "city"):
            if p.get(field) in target_caps:
                f["properties"] = {"name": p[field]}
                bay_caps_features.append(f)
                break
    if not bay_caps_features:
        # fallback: search any string property
        for f in caps["features"]:
            for v in f["properties"].values():
                if isinstance(v, str) and v in target_caps:
                    f["properties"] = {"name": v}
                    bay_caps_features.append(f)
                    break
    bay_caps = {"type": "FeatureCollection", "features": bay_caps_features}
    with open(OUT / "bay_capitals.geojson", "w", encoding="utf-8") as f:
        json.dump(bay_caps, f, separators=(",", ":"))
    print(f"BAY capitals: {len(bay_caps['features'])} (target: 3)")

    # --- 4. UNFPA school-age population by state ---
    pop = pd.read_excel(RAW_UNFPA, sheet_name="nga_admpop_adm1_2022")
    bay_pop = pop[pop["ADM1_EN"].isin(BAY)].copy()
    bay_pop["school_age_5_14"] = bay_pop["T_05_09"] + bay_pop["T_10_14"]
    out_pop = bay_pop[["ADM1_EN", "T_TL", "T_05_09", "T_10_14", "school_age_5_14"]].rename(
        columns={"ADM1_EN": "state", "T_TL": "total_pop", "T_05_09": "pop_5_9", "T_10_14": "pop_10_14"}
    ).sort_values("state").reset_index(drop=True)
    out_pop.to_csv(OUT / "bay_school_age_population.csv", index=False)

    total_5_14 = int(out_pop["school_age_5_14"].sum())
    print(f"\nBAY school-age 5-14 by state:")
    print(out_pop[["state", "school_age_5_14"]].to_string(index=False))
    print(f"BAY total 5-14: {total_5_14:,}")
    assert total_5_14 == 3_926_751, f"unexpected total: {total_5_14}"

    print("\nwrote bay_lga_reference.csv, bay_lga_polygons.geojson, "
          "bay_state_boundaries.geojson, bay_capitals.geojson, bay_school_age_population.csv")


if __name__ == "__main__":
    main()
