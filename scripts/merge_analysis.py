"""
Step 5 — Merge all processed data and build five output tables.
"""

import pandas as pd
import numpy as np
import os

PROCESSED = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"

# ── Load inputs ───────────────────────────────────────────────────────────────
psd = pd.read_csv(os.path.join(PROCESSED, "psd_palm_wide.csv"))
mpob = pd.read_csv(os.path.join(PROCESSED, "mpob_annual.csv"))
gain = pd.read_csv(os.path.join(PROCESSED, "gain_indonesia.csv"))

psd_id = psd[psd["country_code"]=="ID"].copy()
psd_my = psd[psd["country_code"]=="MY"].copy()

ENSO_YEARS = {2009, 2010, 2015, 2016, 2023}

# ── Build Malaysia merged (MPOB takes priority over PSD) ──────────────────────
my_merged = psd_my.merge(
    mpob, on="year", how="outer", suffixes=("_psd","_mpob")
).sort_values("year").reset_index(drop=True)

# MPOB cpo_production_malaysia_mt → preferred over PSD production_1000mt
# Convert MPOB mt → 1000mt for comparison
my_merged["production_1000mt_mpob_conv"] = my_merged["cpo_production_malaysia_mt"] / 1000

conflict_mask = (
    my_merged["production_1000mt_mpob_conv"].notna() &
    my_merged["production_1000mt"].notna() &
    ((my_merged["production_1000mt_mpob_conv"] - my_merged["production_1000mt"]).abs() /
     my_merged["production_1000mt"].abs() * 100 > 5)
)
my_merged["mpob_psd_conflict_flag"] = conflict_mask

# MPOB-preferred production (in 1000 MT for consistency)
my_merged["malaysia_production_1000mt"] = np.where(
    my_merged["cpo_production_malaysia_mt"].notna(),
    my_merged["cpo_production_malaysia_mt"] / 1000,
    my_merged["production_1000mt"]
)

# MPOB-preferred yield
my_merged["malaysia_yield_t_per_ha"] = np.where(
    my_merged["ffb_yield_malaysia_t_per_ha"].notna(),
    my_merged["ffb_yield_malaysia_t_per_ha"],
    my_merged["yield_mt_per_ha"]
)

# YoY for merged Malaysia production
my_merged = my_merged.sort_values("year")
my_merged["malaysia_yoy_production_pct"] = my_merged["malaysia_production_1000mt"].pct_change() * 100

# Source label
my_merged["data_source_malaysia"] = np.where(
    my_merged["cpo_production_malaysia_mt"].notna(),
    "MPOB Annual Overview",
    "USDA PSD"
)

# ── OUTPUT 1: palm_supply_shock.csv ──────────────────────────────────────────
years_full = sorted(set(psd_id["year"].tolist() + my_merged["year"].tolist()))
id_map = psd_id.set_index("year")
my_map = my_merged.set_index("year")

shock_rows = []
for yr in years_full:
    id_row = id_map.loc[yr] if yr in id_map.index else None
    my_row = my_map.loc[yr] if yr in my_map.index else None

    id_prod = float(id_row["production_1000mt"]) if id_row is not None and pd.notna(id_row.get("production_1000mt")) else None
    id_yield = float(id_row["yield_mt_per_ha"]) if id_row is not None and pd.notna(id_row.get("yield_mt_per_ha")) else None
    my_prod = float(my_row["malaysia_production_1000mt"]) if my_row is not None and pd.notna(my_row.get("malaysia_production_1000mt")) else None
    my_oer = float(my_row["oer_national_pct_mpob"]) if my_row is not None and pd.notna(my_row.get("oer_national_pct_mpob")) else None
    if my_oer is None:
        my_oer = float(my_row["oer_national_pct"]) if my_row is not None and pd.notna(my_row.get("oer_national_pct")) else None
    my_ffb = float(my_row["malaysia_yield_t_per_ha"]) if my_row is not None and pd.notna(my_row.get("malaysia_yield_t_per_ha")) else None

    id_yoy = float(id_row["yoy_production_pct"]) if id_row is not None and pd.notna(id_row.get("yoy_production_pct")) else None
    my_yoy = float(my_row["malaysia_yoy_production_pct"]) if my_row is not None and pd.notna(my_row.get("malaysia_yoy_production_pct")) else None

    id_yield_flag = bool(id_row["yield_deviation_flag"]) if id_row is not None and pd.notna(id_row.get("yield_deviation_flag")) else False
    my_yield_flag = False
    if my_ffb is not None and my_row is not None:
        prev_yrs = [y for y in years_full if y < yr and y in my_map.index]
        if prev_yrs:
            prev_ffb_row = my_map.loc[prev_yrs[-1]]
            prev_ffb = float(prev_ffb_row["malaysia_yield_t_per_ha"]) if pd.notna(prev_ffb_row.get("malaysia_yield_t_per_ha")) else None
            if prev_ffb and prev_ffb > 0:
                my_yield_flag = (my_ffb - prev_ffb) / prev_ffb * 100 < -5

    combined = None
    if id_prod is not None and my_prod is not None:
        combined = id_prod + my_prod

    id_src = "USDA PSD" if id_row is not None and pd.notna(id_row.get("production_1000mt")) else "N/A"
    my_src = str(my_row["data_source_malaysia"]) if my_row is not None and pd.notna(my_row.get("data_source_malaysia")) else "N/A"

    shock_rows.append({
        "year": yr,
        "indonesia_production_1000mt": id_prod,
        "indonesia_yield_mt_per_ha": id_yield,
        "malaysia_production_1000mt": my_prod,
        "malaysia_oer_pct": my_oer,
        "malaysia_ffb_yield_t_per_ha": my_ffb,
        "combined_production_1000mt": combined,
        "indonesia_yoy_production_pct": id_yoy,
        "malaysia_yoy_production_pct": my_yoy,
        "indonesia_yield_deviation_flag": id_yield_flag,
        "malaysia_yield_deviation_flag": my_yield_flag,
        "enso_analog_flag": yr in ENSO_YEARS,
        "enso_live_warning_2026_flag": yr == 2026,
        "data_source_indonesia": id_src,
        "data_source_malaysia": my_src,
    })

shock = pd.DataFrame(shock_rows)
shock.to_csv(os.path.join(PROCESSED, "palm_supply_shock.csv"), index=False)

# ── OUTPUT 2: palm_malaysia_stocks.csv ────────────────────────────────────────
stocks_cols = ["year","ending_stocks_total_mt","ending_stocks_cpo_mt","ending_stocks_processed_mt","provenance"]
mpob_stocks = mpob[mpob["ending_stocks_total_mt"].notna()][
    ["year","ending_stocks_total_mt","ending_stocks_cpo_mt","ending_stocks_processed_mt","provenance"]
].copy()
mpob_stocks["yoy_stocks_pct"] = mpob_stocks["ending_stocks_total_mt"].pct_change() * 100
mpob_stocks["below_1500_flag"] = mpob_stocks["ending_stocks_total_mt"] < 1500000
mpob_stocks.to_csv(os.path.join(PROCESSED, "palm_malaysia_stocks.csv"), index=False)

# ── OUTPUT 3: palm_malaysia_oer.csv ──────────────────────────────────────────
oer_rows = mpob[mpob["oer_national_pct"].notna()][
    ["year","oer_national_pct","oer_peninsular_pct","oer_sabah_pct","oer_sarawak_pct",
     "ffb_yield_malaysia_t_per_ha","yoy_oer_pct","yoy_ffb_yield_pct","enso_analog_flag","provenance"]
].copy()
oer_rows["below_threshold_flag"] = oer_rows["oer_national_pct"] < 19.5
oer_rows.to_csv(os.path.join(PROCESSED, "palm_malaysia_oer.csv"), index=False)

# ── OUTPUT 4: palm_indonesia_biodiesel.csv ────────────────────────────────────
bio_rows = []
for _, g in gain.iterrows():
    rpt = g["report_number"]
    yr = int(g["report_date"][:4])  # use report year as proxy
    squeeze = (g["biodiesel_mandate_level"] == "B40" and
               bool(g.get("bmkg_drought_forecast") and str(g.get("bmkg_drought_forecast")) not in ["None","nan",""]))
    bio_rows.append({
        "year": yr,
        "mandate_level": g["biodiesel_mandate_level"],
        "biodiesel_volume_bn_liters": g["biodiesel_volume_bn_liters"],
        "industrial_consumption_mmt": g["industrial_consumption_current_mmt"],
        "yoy_industrial_pct": None,
        "squeeze_risk_flag": squeeze,
        "provenance": g["provenance"],
    })

bio = pd.DataFrame(bio_rows).sort_values("year").reset_index(drop=True)
bio["yoy_industrial_pct"] = bio["industrial_consumption_mmt"].pct_change() * 100
bio.to_csv(os.path.join(PROCESSED, "palm_indonesia_biodiesel.csv"), index=False)

# ── OUTPUT 5: palm_exports.csv ────────────────────────────────────────────────
# Indonesia from GAIN PDFs
id_exports = gain[["report_date","exports_current_year_mmt","provenance"]].copy()
id_exports["year"] = id_exports["report_date"].str[:4].astype(int)
id_exports["country"] = "Indonesia"
id_exports["exports_1000mt"] = id_exports["exports_current_year_mmt"] * 1000
id_exports["yoy_exports_pct"] = id_exports["exports_1000mt"].pct_change() * 100
id_exports = id_exports[["year","country","exports_1000mt","yoy_exports_pct","provenance"]]

# Malaysia from MPOB
my_exports = mpob[mpob["exports_palm_oil_mt"].notna()][["year","exports_palm_oil_mt","provenance"]].copy()
my_exports["country"] = "Malaysia"
my_exports["exports_1000mt"] = my_exports["exports_palm_oil_mt"] / 1000
my_exports["yoy_exports_pct"] = my_exports["exports_1000mt"].pct_change() * 100
my_exports = my_exports[["year","country","exports_1000mt","yoy_exports_pct","provenance"]]

exports = pd.concat([id_exports, my_exports], ignore_index=True).sort_values(["year","country"])
exports.to_csv(os.path.join(PROCESSED, "palm_exports.csv"), index=False)

# ── Data quality report ───────────────────────────────────────────────────────
print("\n" + "="*60)
print("DATA QUALITY REPORT")
print("="*60)

def src_counts(df):
    mpob_n = df["provenance"].str.contains("MPOB", na=False).sum() if "provenance" in df else 0
    gain_n = df["provenance"].str.contains("GAIN", na=False).sum() if "provenance" in df else 0
    psd_n  = df["provenance"].str.contains("PSD",  na=False).sum() if "provenance" in df else 0
    est_n  = df["provenance"].str.contains("ESTIMATED", na=False).sum() if "provenance" in df else 0
    return mpob_n, gain_n, psd_n, est_n

for name, df in [
    ("palm_supply_shock.csv", shock),
    ("palm_malaysia_stocks.csv", mpob_stocks),
    ("palm_malaysia_oer.csv", oer_rows),
    ("palm_indonesia_biodiesel.csv", bio),
    ("palm_exports.csv", exports),
]:
    mpob_n, gain_n, psd_n, est_n = src_counts(df)
    nulls = {c: int(df[c].isna().sum()) for c in df.columns if df[c].isna().any()}
    conflicts = int(my_merged["mpob_psd_conflict_flag"].sum()) if name == "palm_supply_shock.csv" else 0
    print(f"\n{name}")
    print(f"  Total rows: {len(df)}")
    print(f"  Rows sourced from MPOB PDF: {mpob_n}")
    print(f"  Rows sourced from USDA GAIN PDF: {gain_n}")
    print(f"  Rows sourced from USDA PSD: {psd_n}")
    print(f"  Rows estimated by Claude: {est_n}")
    if conflicts:
        print(f"  Source conflicts flagged (MPOB vs PSD >5%): {conflicts}")
    if nulls:
        print(f"  Null values: {nulls}")

print("\n" + "="*60)
print(f"All 5 output files written to {PROCESSED}")
print("="*60)
