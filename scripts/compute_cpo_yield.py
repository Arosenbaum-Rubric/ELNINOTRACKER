"""
Compute CPO yield (t CPO / ha harvested) for Indonesia, Malaysia, World.
All three on the same metric so they can share a Y-axis.

Sources:
  Indonesia:  USDA PSD — production (attr 28) / area harvested (attr 4)
  Malaysia:   MPOB FFB yield × MPOB OER  (2009–2025, hardcoded from Annual Overview PDFs)
              Fallback USDA PSD for 2005–2008 where OER not available from MPOB
  World avg:  USDA PSD — sum(production) / sum(area harvested) across all countries,
              latest estimate per (market_year, country_code)

Output: structured for copy-paste into JS data block.
"""

import pandas as pd
import numpy as np
import os

RAW = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data"
psd = pd.read_csv(os.path.join(RAW, "psd_oilseeds.csv"), dtype={"Commodity_Code": str})

palm = psd[(psd["Commodity_Code"] == "4243000") &
           (psd["Market_Year"].between(2005, 2026))].copy()

# Latest estimate per (Market_Year, Country_Code, Attribute_ID)
palm_latest = (palm
    .sort_values(["Market_Year", "Country_Code", "Attribute_ID", "Calendar_Year", "Month"])
    .groupby(["Market_Year", "Country_Code", "Attribute_ID"])
    .last()
    .reset_index())

def get_attr(country_code, attr_id):
    sub = palm_latest[(palm_latest["Country_Code"] == country_code) &
                      (palm_latest["Attribute_ID"] == attr_id)]
    return sub.set_index("Market_Year")["Value"]

# ── Indonesia ─────────────────────────────────────────────────────────────────
id_prod = get_attr("ID", 28)   # 1000 MT CPO
id_area = get_attr("ID",  4)   # 1000 ha

id_yield = (id_prod / id_area).round(3)  # MT CPO / ha
print("=== Indonesia (USDA PSD) ===")
for yr, v in id_yield.items():
    print(f"  {{yr:'{yr}', cpo_ha:{v:.3f}, src:'rep'}},  // PSD prod={id_prod[yr]:.0f}kt area={id_area[yr]:.0f}kha")

# ── Malaysia — MPOB-derived where available ───────────────────────────────────
# MPOB Annual Overview PDFs (hardcoded, sourced)
mpob_ffb = {   # t FFB/ha — MPOB Annual Overview PDFs
    2006: 19.06, 2007: 18.35, 2008: 19.55,   # sourced from Overview 2008 (pre-2010 MPOB)
    2010: 18.03, 2011: 19.69,
    2015: 18.48, 2016: 15.91, 2017: 17.89, 2018: 17.16, 2019: 17.19,
    2020: 16.73, 2021: 15.47, 2022: 15.49, 2023: 15.79, 2024: 16.70, 2025: 17.77,
}
mpob_oer = {   # % — MPOB Annual Overview PDFs
    2009: 20.42, 2010: 20.45, 2011: 20.35,
    2015: 20.46, 2016: 20.18, 2017: 19.72, 2018: 19.95, 2019: 20.21,
    2020: 19.92, 2021: 20.01, 2022: 19.70, 2023: 19.86, 2024: 19.67, 2025: 19.74,
}

# USDA PSD Malaysia (fallback)
my_prod_psd = get_attr("MY", 28)
my_area_psd = get_attr("MY",  4)
my_yield_psd = (my_prod_psd / my_area_psd).round(3)

# OER fill for years with FFB but no MPOB OER:
# 2006-2008: use USDA PSD Malaysia yield directly (can't derive CPO yield without OER)
# 2009: have OER but no FFB in mpob_ffb → use USDA PSD
# 2012-2014: have neither in MPOB → interpolate OER between 2011 and 2015, apply to FFB est
# Interpolated OER 2012-2014 (linear 20.35 → 20.46 over 4 steps)
for yr, oer in [(2012, 20.37), (2013, 20.39), (2014, 20.43)]:
    mpob_oer[yr] = oer

# Interpolated FFB 2009, 2012-2014 (from yield trajectory estimates)
mpob_ffb_est = {2009: 17.5, 2012: 19.4, 2013: 19.1, 2014: 18.8}

print("\n=== Malaysia (MPOB-derived where available, USDA PSD fallback) ===")
MY_SRC_NOTE = []
for yr in range(2005, 2027):
    ffb = mpob_ffb.get(yr) or mpob_ffb_est.get(yr)
    oer = mpob_oer.get(yr)
    psd_y = my_yield_psd.get(yr)

    if ffb and oer:
        cpo_ha = round(ffb * oer / 100, 3)
        src = 'rep' if yr in mpob_ffb and yr in mpob_oer else 'est'
        note = f"MPOB FFB={ffb} × OER={oer}%"
    elif ffb and not oer:
        # 2006-2008: have MPOB FFB but no OER → use USDA PSD yield as it's fully sourced
        if psd_y and not np.isnan(psd_y):
            cpo_ha = round(float(psd_y), 3)
            src = 'rep'
            note = f"USDA PSD (MPOB FFB available but no OER pre-2009; PSD={psd_y:.3f})"
        else:
            continue
    elif psd_y and not np.isnan(psd_y):
        cpo_ha = round(float(psd_y), 3)
        src = 'rep'
        note = f"USDA PSD fallback"
    else:
        continue

    print(f"  {{yr:'{yr}', cpo_ha:{cpo_ha}, src:'{src}'}},  // {note}")
    MY_SRC_NOTE.append((yr, cpo_ha, src, note))

# ── World average ─────────────────────────────────────────────────────────────
print("\n=== World average (USDA PSD all countries) ===")
for yr in range(2005, 2027):
    sub = palm_latest[(palm_latest["Market_Year"] == yr)]
    prod28 = sub[sub["Attribute_ID"] == 28]["Value"].sum()
    area4  = sub[sub["Attribute_ID"] == 4]["Value"].sum()
    if area4 > 0:
        world_y = round(prod28 / area4, 3)
        print(f"  {{yr:'{yr}', cpo_ha:{world_y}}},  // prod={prod28:.0f}kt area={area4:.0f}kha")

# ── Cross-validation ──────────────────────────────────────────────────────────
print("\n=== Cross-validation: Malaysia MPOB-derived vs USDA PSD ===")
print(f"{'Year':>6} {'MPOB-derived':>14} {'USDA PSD':>10} {'Diff%':>7}")
for yr, cpo_ha, src, note in MY_SRC_NOTE:
    psd_v = my_yield_psd.get(yr)
    if psd_v and not np.isnan(psd_v):
        diff = (cpo_ha - float(psd_v)) / float(psd_v) * 100
        flag = " *** >10%" if abs(diff) > 10 else (" * >5%" if abs(diff) > 5 else "")
        print(f"{yr:>6} {cpo_ha:>14.3f} {float(psd_v):>10.3f} {diff:>7.1f}%{flag}")
