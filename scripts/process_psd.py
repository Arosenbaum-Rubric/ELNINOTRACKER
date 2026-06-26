"""
Step 2 — USDA PSD Processing for Palm Oil
Filters psd_oilseeds.csv for palm oil (4243000), ID/MY, 2005-2026.
Cross-validates against OWID CSVs.
"""

import pandas as pd
import numpy as np
import os

RAW = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data"
PROCESSED = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"
os.makedirs(PROCESSED, exist_ok=True)

# ── Load PSD ─────────────────────────────────────────────────────────────────
print("Loading PSD CSV...")
psd_all = pd.read_csv(os.path.join(RAW, "psd_oilseeds.csv"), dtype={"Commodity_Code": str})

# Filter: palm oil, ID/MY, 2000-2026
palm = psd_all[
    (psd_all["Commodity_Code"] == "4243000") &
    (psd_all["Country_Code"].isin(["ID", "MY"])) &
    (psd_all["Market_Year"] >= 2000) &
    (psd_all["Market_Year"] <= 2026)
].copy()

print(f"Total PSD rows extracted: {len(palm)}")

# Show available Attribute_IDs to confirm coverage
print("\nAvailable Attribute_IDs (ID+MY, palm oil):")
print(palm[["Attribute_ID","Attribute_Description"]].drop_duplicates().sort_values("Attribute_ID").to_string(index=False))

# ── Take latest estimate per market year ─────────────────────────────────────
# PSD data is published monthly; take the latest Calendar_Year+Month per Market_Year
palm = palm.sort_values(["Market_Year","Country_Code","Attribute_ID","Calendar_Year","Month"])
palm = palm.groupby(["Market_Year","Country_Code","Attribute_ID"]).last().reset_index()

# ── Pivot to wide format ──────────────────────────────────────────────────────
ATTR_MAP = {
    28:  "production_1000mt",
    4:   "area_harvested_1000ha",   # confirmed from data: 4=Area Harvested, 20=Beginning Stocks
    184: "yield_mt_per_ha",
    176: "ending_stocks_1000mt",
    88:  "exports_1000mt",
    125: "total_cons_1000mt",
    140: "industrial_cons_1000mt",
    149: "food_cons_1000mt",
}

wanted = palm[palm["Attribute_ID"].isin(ATTR_MAP.keys())].copy()
wanted["col_name"] = wanted["Attribute_ID"].map(ATTR_MAP)

wide = wanted.pivot_table(
    index=["Market_Year","Country_Code","Country_Name"],
    columns="col_name",
    values="Value",
    aggfunc="last"
).reset_index()
wide.columns.name = None
wide = wide.rename(columns={"Market_Year":"year","Country_Code":"country_code","Country_Name":"country_name"})

# Ensure all columns exist even if missing
for col in ATTR_MAP.values():
    if col not in wide.columns:
        wide[col] = np.nan

# ── YoY calculations ──────────────────────────────────────────────────────────
def yoy(df, col):
    """YoY % change per country sorted by year."""
    df = df.sort_values(["country_code","year"])
    out_col = "yoy_" + col.replace("_1000mt","").replace("_1000ha","").replace("_mt_per_ha","") + "_pct"
    df[out_col] = df.groupby("country_code")[col].pct_change() * 100
    return df, out_col

yoy_cols = {}
for src_col in ["production_1000mt","yield_mt_per_ha","ending_stocks_1000mt","exports_1000mt","industrial_cons_1000mt"]:
    if src_col in wide.columns:
        wide, oc = yoy(wide, src_col)
        yoy_cols[src_col] = oc

# ── Flags ────────────────────────────────────────────────────────────────────
ENSO_YEARS = {2009, 2010, 2015, 2016, 2023}
wide["yield_deviation_flag"] = wide.get("yoy_yield_pct", np.nan) < -5
wide["stocks_threshold_flag"] = (wide["country_code"] == "MY") & (wide["ending_stocks_1000mt"] < 1500)
wide["enso_analog_flag"] = wide["year"].isin(ENSO_YEARS)
wide["enso_live_warning_flag"] = wide["year"] == 2026

# ── Provenance ───────────────────────────────────────────────────────────────
def provenance(row):
    attrs = ", ".join(str(a) for a in ATTR_MAP.keys())
    return (f"SOURCE: USDA PSD psd_oilseeds.csv "
            f"Commodity 4243000 Country {row['country_code']} Year {row['year']}")

wide["provenance"] = wide.apply(provenance, axis=1)

# ── Reorder columns ───────────────────────────────────────────────────────────
base_cols = [
    "year","country_code","country_name",
    "production_1000mt","area_harvested_1000ha","yield_mt_per_ha",
    "ending_stocks_1000mt","exports_1000mt",
    "industrial_cons_1000mt","food_cons_1000mt","total_cons_1000mt",
    "yoy_production_pct","yoy_yield_pct","yoy_stocks_pct","yoy_exports_pct","yoy_industrial_pct",
    "yield_deviation_flag","stocks_threshold_flag","enso_analog_flag","enso_live_warning_flag",
    "provenance"
]
# Only include columns that exist
final_cols = [c for c in base_cols if c in wide.columns]
wide = wide[final_cols]

out_path = os.path.join(PROCESSED, "psd_palm_wide.csv")
new_2000_2004 = wide[wide["year"] < 2005].copy()
print(f"\nNew 2000–2004 rows computed: {len(new_2000_2004)}")
if os.path.exists(out_path):
    existing = pd.read_csv(out_path)
    combined = pd.concat([existing, new_2000_2004], ignore_index=True)
    combined = combined.sort_values(["country_code", "year"]).reset_index(drop=True)
    combined.to_csv(out_path, index=False)
    print(f"psd_palm_wide.csv updated: {len(combined)} total rows ({len(new_2000_2004)} new rows appended)")
else:
    wide.to_csv(out_path, index=False)
    print(f"\npsd_palm_wide.csv saved: {len(wide)} rows")

# ── Country year ranges ───────────────────────────────────────────────────────
for cc, name in [("ID","Indonesia"),("MY","Malaysia")]:
    sub = wide[wide["country_code"]==cc]
    if len(sub):
        print(f"{name} years: {sub['year'].min()}–{sub['year'].max()}")

# ── OWID Cross-Validation ─────────────────────────────────────────────────────
print("\nLoading OWID files...")
owid_prod = pd.read_csv(os.path.join(RAW, "palm-oil-production.csv"))
owid_yields = pd.read_csv(os.path.join(RAW, "palm-oil-yields.csv"))

# Filter IDN, MYS, 2000-2023
owid_prod = owid_prod[
    owid_prod["Code"].isin(["IDN","MYS"]) &
    (owid_prod["Year"] >= 2000) &
    (owid_prod["Year"] <= 2023)
].copy()

ISO3_MAP = {"IDN":"ID","MYS":"MY"}
owid_prod["country_code"] = owid_prod["Code"].map(ISO3_MAP)
owid_prod = owid_prod.rename(columns={
    "Year":"year",
    "Palm oil - Production (tonnes)":"owid_production_tonnes"
})

# Merge with PSD
psd_id_my = wide[wide["country_code"].isin(["ID","MY"]) & wide["year"].isin(owid_prod["year"].unique())][
    ["year","country_code","production_1000mt"]
].copy()
psd_id_my["psd_production_tonnes"] = psd_id_my["production_1000mt"] * 1000

xval = psd_id_my.merge(
    owid_prod[["year","country_code","owid_production_tonnes"]],
    on=["year","country_code"], how="inner"
)
xval["divergence_pct"] = (
    (xval["psd_production_tonnes"] - xval["owid_production_tonnes"]).abs() /
    xval["owid_production_tonnes"] * 100
)
xval["divergence_flag"] = xval["divergence_pct"] > 5

xval = xval[["year","country_code","psd_production_tonnes","owid_production_tonnes","divergence_pct","divergence_flag"]]
xval.to_csv(os.path.join(PROCESSED, "owid_cross_validation.csv"), index=False)

print(f"OWID cross-validation rows: {len(xval)}")
print(f"Divergences >5% flagged: {xval['divergence_flag'].sum()}")
if xval["divergence_flag"].any():
    print("\nDivergent rows:")
    print(xval[xval["divergence_flag"]].to_string(index=False))
