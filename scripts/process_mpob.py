"""
Step 3b — Add derived metrics and flags to mpob_annual.csv.
"""

import pandas as pd
import numpy as np
import os

PROCESSED = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"
path = os.path.join(PROCESSED, "mpob_annual.csv")

mpob = pd.read_csv(path).sort_values("year").reset_index(drop=True)

# YoY calculations
for col, out_col in [
    ("cpo_production_malaysia_mt", "yoy_cpo_production_pct"),
    ("ffb_yield_malaysia_t_per_ha",  "yoy_ffb_yield_pct"),
    ("oer_national_pct",             "yoy_oer_pct"),
    ("ending_stocks_total_mt",       "yoy_stocks_pct"),
]:
    mpob[out_col] = mpob[col].pct_change() * 100

# Flags
mpob["oer_deviation_flag"] = mpob["oer_national_pct"] < 19.5
mpob["enso_analog_flag"] = mpob["year"].isin([2010, 2015, 2016])

mpob.to_csv(path, index=False)

print("mpob_annual.csv updated with derived metrics.")
print(f"Rows: {len(mpob)}")
print("\nYoY CPO production and FFB yield summary:")
print(mpob[["year","cpo_production_malaysia_mt","yoy_cpo_production_pct",
            "ffb_yield_malaysia_t_per_ha","yoy_ffb_yield_pct",
            "oer_national_pct","oer_deviation_flag","enso_analog_flag"]].to_string(index=False))
