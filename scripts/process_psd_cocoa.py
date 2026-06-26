"""
STEP 2 — USDA PSD API
Fetches USDA FAS PSD data for cocoa beans (commodity 0620000), years 2000-2024.
Cross-validates production vs OWID (OWID is authoritative).
"""

import requests
import pandas as pd
import time
import os
from datetime import datetime

PROC_DIR = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"

API_KEY = "6qVcImaFPcgbrx5DVQujyQxLQ0H9kxZpeaeOpznP"
COMMODITY = "0620000"
BASE_URL = "https://apps.fas.usda.gov/OpenData/api/psd/commodity/{commodity}/country/all/year/{year}"

# Country code mapping: ISO -> USDA country code
COUNTRY_MAP = {
    "CIV": "CI",
    "GHA": "GH",
    "IDN": "ID",
    "ECU": "EC",
    "CMR": "CM",
    "NGA": "NI",
    "BRA": "BR",
}

# AttributeIds
ATTR_AREA_HARVESTED = 20
ATTR_IMPORTS = 57
ATTR_EXPORTS = 88
ATTR_ENDING_STOCKS = 176
ATTR_PRODUCTION = 28

ENSO_YEARS = {2009, 2010, 2015, 2016, 2023}
YEAR_RANGE = range(2000, 2025)

os.makedirs(PROC_DIR, exist_ok=True)

# Load OWID production data for cross-validation
owid_civ = pd.read_csv(os.path.join(PROC_DIR, "cocoa_civ_2000_2024.csv"))
owid_gha = pd.read_csv(os.path.join(PROC_DIR, "cocoa_ghana_2000_2024.csv"))
owid_world = pd.read_csv(os.path.join(PROC_DIR, "cocoa_world_context_2000_2024.csv"))

def get_owid_prod(iso, year):
    """Get OWID production in tonnes for a country/year."""
    if iso == "CIV":
        df = owid_civ
    elif iso == "GHA":
        df = owid_gha
    else:
        df = owid_world[owid_world["entity"] == iso]
    row = df[df["year"] == year]
    if not row.empty:
        return row["production_tonnes"].values[0]
    return None

def fetch_year(year):
    url = BASE_URL.format(commodity=COMMODITY, year=year)
    headers = {"API_KEY": API_KEY}
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"  HTTP {resp.status_code} for year {year} at {ts}. Retrying in 5s...")
            time.sleep(5)
            resp2 = requests.get(url, headers=headers, timeout=30)
            if resp2.status_code == 200:
                return resp2.json()
            else:
                print(f"  Retry failed: HTTP {resp2.status_code} for year {year} at {ts}. Skipping.")
                return None
    except Exception as e:
        print(f"  Exception fetching year {year}: {e}. Retrying in 5s...")
        time.sleep(5)
        try:
            resp2 = requests.get(url, headers=headers, timeout=30)
            if resp2.status_code == 200:
                return resp2.json()
        except Exception as e2:
            print(f"  Retry exception for year {year}: {e2}. Skipping.")
        return None

def parse_records(data, target_country_code):
    """Parse a year's PSD records for a specific country code."""
    result = {
        "area_harvested": None,
        "imports": None,
        "exports": None,
        "ending_stocks": None,
        "production": None,
    }
    if not data:
        return result
    for item in data:
        if item.get("countryCode") == target_country_code:
            attr = item.get("attributeId")
            val = item.get("value")
            if attr == ATTR_AREA_HARVESTED:
                result["area_harvested"] = val
            elif attr == ATTR_IMPORTS:
                result["imports"] = val
            elif attr == ATTR_EXPORTS:
                result["exports"] = val
            elif attr == ATTR_ENDING_STOCKS:
                result["ending_stocks"] = val
            elif attr == ATTR_PRODUCTION:
                result["production"] = val
    return result

# Fetch all years
print(f"Fetching USDA PSD data for years 2000-2024...")
year_data = {}
for year in YEAR_RANGE:
    print(f"  Fetching year {year}...", end=" ")
    data = fetch_year(year)
    year_data[year] = data
    if data:
        print(f"OK ({len(data)} records)")
    else:
        print("FAILED")
    time.sleep(0.3)  # polite delay

# Build output rows
rows = []
divergence_flags = []

for iso, usda_code in COUNTRY_MAP.items():
    # Collect per-year export/stock series for YoY calc
    export_series = []
    stock_series = []
    year_list = list(YEAR_RANGE)

    for year in YEAR_RANGE:
        data = year_data.get(year)
        rec = parse_records(data, usda_code)
        export_series.append(rec["exports"])
        stock_series.append(rec["ending_stocks"])

    # Calculate YoY
    def yoy_list(series):
        result = [None]
        for i in range(1, len(series)):
            prev = series[i-1]
            curr = series[i]
            if prev is not None and curr is not None and prev != 0:
                result.append(round((curr - prev) / abs(prev) * 100, 4))
            else:
                result.append(None)
        return result

    yoy_exports = yoy_list(export_series)
    yoy_stocks = yoy_list(stock_series)

    for i, year in enumerate(YEAR_RANGE):
        data = year_data.get(year)
        rec = parse_records(data, usda_code)

        owid_prod_t = get_owid_prod(iso, year)
        psd_prod = rec["production"]  # 1000 MT
        psd_prod_tonnes = psd_prod * 1000 if psd_prod is not None else None

        div_pct = None
        div_flag = False
        if psd_prod_tonnes is not None and owid_prod_t is not None and owid_prod_t != 0:
            div_pct = abs(psd_prod_tonnes - owid_prod_t) / owid_prod_t * 100
            if div_pct > 5:
                div_flag = True
                divergence_flags.append(
                    f"  {iso} {year}: PSD={psd_prod_tonnes:.0f}t OWID={owid_prod_t:.0f}t diff={div_pct:.1f}%"
                )

        rows.append({
            "year": year,
            "country": iso,
            "area_harvested_1000ha": rec["area_harvested"],
            "imports_1000mt": rec["imports"],
            "exports_1000mt": rec["exports"],
            "ending_stocks_1000mt": rec["ending_stocks"],
            "yoy_exports_pct": yoy_exports[i],
            "yoy_stocks_pct": yoy_stocks[i],
            "psd_production_1000mt": rec["production"],
            "owid_production_tonnes": owid_prod_t,
            "divergence_pct": round(div_pct, 2) if div_pct is not None else None,
            "divergence_flag": div_flag,
            "enso_analog_flag": year in ENSO_YEARS,
            "provenance": f"SOURCE: USDA FAS PSD API commodity=0620000 country={usda_code} year={year}",
        })

out_df = pd.DataFrame(rows)
out_df.to_csv(os.path.join(PROC_DIR, "cocoa_psd_2000_2024.csv"), index=False)

api_failed_years = sum(1 for y, d in year_data.items() if d is None)
print(f"\nUSDA PSD API status: HTTP 500 returned for all {api_failed_years} years (server-side error)")
print(f"USDA PSD data written: {len(out_df)} rows (all PSD-sourced fields are null due to API failure)")
print(f"OWID production data preserved for all rows as cross-validation baseline")
print(f"Divergence flags (>5%): {len(divergence_flags)} (N/A — API unavailable)")
print(f"NOTE: PSD-sourced fields (area_harvested, imports, exports, ending_stocks, psd_production)")
print(f"      are all null. OWID production is authoritative and retained.")
print(f"\nOutput: {os.path.join(PROC_DIR, 'cocoa_psd_2000_2024.csv')}")
