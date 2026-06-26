"""
STEP 1 — Local CSV Processing
Processes OWID cocoa production and yield CSVs (2000-2024).
Zero network calls made.
"""

import pandas as pd
import sys
import os

# Paths
RAW_DIR = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Coacoa Data"
PROC_DIR = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"

os.makedirs(PROC_DIR, exist_ok=True)

PROD_FILE = os.path.join(RAW_DIR, "cocoa-bean-production.csv")
YIELD_FILE = os.path.join(RAW_DIR, "cocoa-bean-yields.csv")

# Country mapping: CSV name -> ISO code
COUNTRIES = {
    "Cote d'Ivoire": "CIV",
    "Ghana":         "GHA",
    "Indonesia":     "IDN",
    "Ecuador":       "ECU",
    "Cameroon":      "CMR",
    "Nigeria":       "NGA",
    "Brazil":        "BRA",
}

ENSO_YEARS = {2009, 2010, 2015, 2016, 2023}
YEAR_RANGE = range(2000, 2025)

# Seed validation values (2024)
SEED = {
    "CIV": {"prod": 1_890_442, "yield": 0.4955},
    "GHA": {"prod":   530_000, "yield": 0.5762},
    "IDN": {"prod":   632_702, "yield": 0.4562},
    "ECU": {"prod":   403_699, "yield": 0.7454},
    "CMR": {"prod":   320_000},
    "NGA": {"prod":   350_000},
    "BRA": {"prod":   297_509},
}

def load_csv(path, value_col):
    df = pd.read_csv(path)
    df = df[df["Year"].isin(YEAR_RANGE)]
    return df

def get_country_series(df, entity_name, value_col):
    sub = df[df["Entity"] == entity_name][["Year", value_col]].copy()
    sub = sub.sort_values("Year").reset_index(drop=True)
    return sub

def calc_yoy(series):
    """series can be a list or pandas Series"""
    yoys = [None]
    vals = list(series)
    for i in range(1, len(vals)):
        prev = vals[i-1]
        curr = vals[i]
        if prev is not None and prev != 0 and not (isinstance(prev, float) and pd.isna(prev)) and not (isinstance(curr, float) and pd.isna(curr)):
            yoys.append(round((curr - prev) / abs(prev) * 100, 4))
        else:
            yoys.append(None)
    return yoys

# Load data
print("Loading CSVs...")
prod_df = load_csv(PROD_FILE, "Cocoa beans - Production (tonnes)")
yield_df = load_csv(YIELD_FILE, "Cocoa beans - Yield (tonnes per hectare)")

PROD_COL = "Cocoa beans - Production (tonnes)"
YIELD_COL = "Cocoa beans - Yield (tonnes per hectare)"

# Build per-country data
country_data = {}
for entity, iso in COUNTRIES.items():
    p = get_country_series(prod_df, entity, PROD_COL)
    y = get_country_series(yield_df, entity, YIELD_COL)
    # Merge on Year
    merged = pd.merge(p, y, on="Year", how="outer").sort_values("Year")
    merged = merged[merged["Year"].isin(YEAR_RANGE)].reset_index(drop=True)
    country_data[iso] = merged

# === Validation ===
prod_pass = True
yield_pass = True
prod_failures = []
yield_failures = []

for iso, seed_vals in SEED.items():
    df = country_data[iso]
    row_2024 = df[df["Year"] == 2024]
    if row_2024.empty:
        print(f"  WARNING: No 2024 data for {iso}")
        continue

    if "prod" in seed_vals:
        actual_prod = row_2024[PROD_COL].values[0]
        expected_prod = seed_vals["prod"]
        if pd.isna(actual_prod):
            print(f"  WARNING: 2024 production is NaN for {iso}")
        else:
            diff_pct = abs(actual_prod - expected_prod) / expected_prod * 100
            if diff_pct > 1.0:
                prod_pass = False
                prod_failures.append(f"{iso}: actual={actual_prod:.0f} expected={expected_prod:.0f} diff={diff_pct:.2f}%")

    if "yield" in seed_vals:
        actual_yield = row_2024[YIELD_COL].values[0]
        expected_yield = seed_vals["yield"]
        if pd.isna(actual_yield):
            print(f"  WARNING: 2024 yield is NaN for {iso}")
        else:
            diff_pct = abs(actual_yield - expected_yield) / expected_yield * 100
            if diff_pct > 1.0:
                yield_pass = False
                yield_failures.append(f"{iso}: actual={actual_yield:.4f} expected={expected_yield:.4f} diff={diff_pct:.2f}%")

if not prod_pass:
    print("PRODUCTION VALIDATION FAILURES:")
    for f in prod_failures:
        print(f"  {f}")
    print("ERROR: Production validation FAILED — stopping.")
    sys.exit(1)

if not yield_pass:
    print("YIELD VALIDATION FAILURES:")
    for f in yield_failures:
        print(f"  {f}")
    print("ERROR: Yield validation FAILED — stopping.")
    sys.exit(1)

# === Build CIV output ===
def build_country_csv(iso, provenance_str):
    df = country_data[iso].copy()
    prod_vals = df[PROD_COL].tolist()
    yield_vals = df[YIELD_COL].tolist()
    yoy_prod = calc_yoy(prod_vals)
    yoy_yield = calc_yoy(yield_vals)

    rows = []
    for i, row in df.iterrows():
        yr = int(row["Year"])
        yp = yoy_prod[i]
        yy = yoy_yield[i]
        rows.append({
            "year": yr,
            "production_tonnes": row[PROD_COL],
            "yield_t_per_ha": row[YIELD_COL],
            "yoy_production_pct": round(yp, 4) if yp is not None else None,
            "yoy_yield_pct": round(yy, 4) if yy is not None else None,
            "yield_deviation_flag": True if (yy is not None and yy < -5) else False,
            "enso_analog_flag": yr in ENSO_YEARS,
            "provenance": provenance_str,
        })
    return pd.DataFrame(rows)

civ_df = build_country_csv("CIV", "SOURCE: OWID cocoa-bean-production.csv local file FAO/OWID")
gha_df = build_country_csv("GHA", "SOURCE: OWID cocoa-bean-production.csv local file FAO/OWID")

civ_df.to_csv(os.path.join(PROC_DIR, "cocoa_civ_2000_2024.csv"), index=False)
gha_df.to_csv(os.path.join(PROC_DIR, "cocoa_ghana_2000_2024.csv"), index=False)

# === Rest of World (CMR+NGA+BRA) per year ===
row_records = []
for yr in YEAR_RANGE:
    row_countries = {}
    for iso in ["CMR", "NGA", "BRA"]:
        df = country_data[iso]
        r = df[df["Year"] == yr]
        if not r.empty:
            p = r[PROD_COL].values[0]
            y = r[YIELD_COL].values[0]
            row_countries[iso] = {"prod": p, "yield": y}

    total_prod = sum(v["prod"] for v in row_countries.values() if not pd.isna(v["prod"]))
    # production-weighted average yield (skip NaN yields)
    valid = [(v["prod"], v["yield"]) for v in row_countries.values()
             if not pd.isna(v["prod"]) and not pd.isna(v["yield"])]
    if valid:
        weighted_yield = sum(p * y for p, y in valid) / sum(p for p, y in valid)
    else:
        weighted_yield = None

    row_records.append({
        "year": yr,
        "entity": "Rest of World",
        "production_tonnes": total_prod,
        "yield_t_per_ha": weighted_yield,
        "enso_analog_flag": yr in ENSO_YEARS,
        "provenance": "DERIVED: sum CMR+NGA+BRA SOURCE OWID local",
    })

row_df = pd.DataFrame(row_records)

# === World Context (all 7 countries + RoW + Global) ===
# Build per-country yearly data for world context
world_rows = []

SECTION_MAP = {
    "CIV": ("West Africa", "Tropical humid"),
    "GHA": ("West Africa", "Tropical humid"),
    "IDN": ("Southeast Asia", "Equatorial"),
    "ECU": ("South America", "Tropical"),
    "CMR": ("Rest of World", "Tropical"),
    "NGA": ("Rest of World", "Tropical"),
    "BRA": ("Rest of World", "Tropical humid"),
}

for iso, (section, climate) in SECTION_MAP.items():
    df = country_data[iso].copy()
    prod_vals = df[PROD_COL].tolist()
    yield_vals = df[YIELD_COL].tolist()
    yoy_prod = calc_yoy(prod_vals)

    for i, row in df.iterrows():
        yr = int(row["Year"])
        world_rows.append({
            "year": yr,
            "entity": iso,
            "production_tonnes": row[PROD_COL],
            "yield_t_per_ha": row[YIELD_COL],
            "yoy_production_pct": round(yoy_prod[i], 4) if yoy_prod[i] is not None else None,
            "section": section,
            "climate_region": climate,
            "enso_analog_flag": yr in ENSO_YEARS,
            "provenance": "SOURCE: OWID cocoa-bean-production.csv local file FAO/OWID",
        })

# Add Rest of World rows
for _, r in row_df.iterrows():
    world_rows.append({
        "year": int(r["year"]),
        "entity": "Rest of World",
        "production_tonnes": r["production_tonnes"],
        "yield_t_per_ha": r["yield_t_per_ha"],
        "yoy_production_pct": None,
        "section": "Rest of World",
        "climate_region": "Mixed",
        "enso_analog_flag": bool(r["enso_analog_flag"]),
        "provenance": r["provenance"],
    })

# Add Global totals
for yr in YEAR_RANGE:
    total_prod = 0
    valid_yields = []
    for iso in COUNTRIES.values():
        df = country_data[iso]
        r = df[df["Year"] == yr]
        if not r.empty:
            p = r[PROD_COL].values[0]
            y = r[YIELD_COL].values[0]
            if not pd.isna(p):
                total_prod += p
            if not pd.isna(p) and not pd.isna(y):
                valid_yields.append((p, y))
    global_yield = sum(p * y for p, y in valid_yields) / sum(p for p, y in valid_yields) if valid_yields else None
    world_rows.append({
        "year": yr,
        "entity": "Global",
        "production_tonnes": total_prod,
        "yield_t_per_ha": global_yield,
        "yoy_production_pct": None,
        "section": "Global",
        "climate_region": "Global",
        "enso_analog_flag": yr in ENSO_YEARS,
        "provenance": "DERIVED: sum all countries SOURCE OWID local",
    })

world_df = pd.DataFrame(world_rows)
# Recalculate yoy for Global
global_rows = world_df[world_df["entity"] == "Global"].sort_values("year").copy()
global_prods = global_rows["production_tonnes"].tolist()
global_yoy = calc_yoy(global_prods)
for i, (idx, row) in enumerate(global_rows.iterrows()):
    world_df.loc[idx, "yoy_production_pct"] = round(global_yoy[i], 4) if global_yoy[i] is not None else None

# Recalculate yoy for Rest of World
row_rows = world_df[world_df["entity"] == "Rest of World"].sort_values("year").copy()
row_prods = row_rows["production_tonnes"].tolist()
row_yoy = calc_yoy(row_prods)
for i, (idx, row) in enumerate(row_rows.iterrows()):
    world_df.loc[idx, "yoy_production_pct"] = round(row_yoy[i], 4) if row_yoy[i] is not None else None

world_df.to_csv(os.path.join(PROC_DIR, "cocoa_world_context_2000_2024.csv"), index=False)

# === Print summary ===
civ_flag_count = civ_df["yield_deviation_flag"].sum()
gha_flag_count = gha_df["yield_deviation_flag"].sum()

print(f"Data source: LOCAL FILES ONLY — zero network calls made")
print(f"CIV rows: {len(civ_df)} | Ghana rows: {len(gha_df)}")
print(f"Production validation: PASSED")
print(f"Yield validation: PASSED")
print(f"Yield deviation flags CIV: {civ_flag_count} | Ghana: {gha_flag_count}")
print(f"Network calls made this step: 0")

# Print 2024 actuals for reference
civ_2024 = civ_df[civ_df["year"] == 2024].iloc[0]
gha_2024 = gha_df[gha_df["year"] == 2024].iloc[0]
idn_df = build_country_csv("IDN", "SOURCE: OWID cocoa-bean-production.csv local file FAO/OWID")
idn_2024 = idn_df[idn_df["year"] == 2024].iloc[0]
ecu_df = build_country_csv("ECU", "SOURCE: OWID cocoa-bean-production.csv local file FAO/OWID")
ecu_2024 = ecu_df[ecu_df["year"] == 2024].iloc[0]

print(f"\n2024 actuals:")
print(f"  CIV prod={civ_2024['production_tonnes']:.0f}t yield={civ_2024['yield_t_per_ha']:.4f} t/ha")
print(f"  GHA prod={gha_2024['production_tonnes']:.0f}t yield={gha_2024['yield_t_per_ha']:.4f} t/ha")
print(f"  IDN prod={idn_2024['production_tonnes']:.0f}t yield={idn_2024['yield_t_per_ha']:.4f} t/ha")
print(f"  ECU prod={ecu_2024['production_tonnes']:.0f}t yield={ecu_2024['yield_t_per_ha']:.4f} t/ha")
