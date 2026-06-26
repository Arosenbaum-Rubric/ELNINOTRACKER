"""
STEP 5 — Merge and Analysis
Reads all processed CSVs, generates charts, ENSO analog CSV, and pipeline_output.json.
"""

import pandas as pd
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

PROC_DIR = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"
CHARTS_DIR = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

ENSO_YEARS = {2009, 2010, 2015, 2016, 2023}
BG_COLOR = "#0a0e16"
GRID_COLOR = "#2a2e36"
TEXT_COLOR = "#e0e4ef"
ACCENT1 = "#4da6ff"
ACCENT2 = "#ffb347"
ACCENT3 = "#7cfc00"
ACCENT4 = "#ff6b6b"
ENSO_COLOR = "#ff6b6b"

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
civ_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_civ_2000_2024.csv"))
gha_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_ghana_2000_2024.csv"))
world_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_world_context_2000_2024.csv"))
psd_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_psd_2000_2024.csv"))
gain_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_gain_signals.csv"))
eur_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_grindings_europe.csv"))
na_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_grindings_north_america.csv"))
asia_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_grindings_asia.csv"))

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────
def shade_enso_years(ax, years, ymin, ymax, alpha=0.18):
    for yr in years:
        if yr in [int(y) for y in years]:
            ax.axvspan(yr - 0.4, yr + 0.4, ymin=0, ymax=1,
                       color=ENSO_COLOR, alpha=alpha, zorder=0)

def set_dark_style(fig, axes):
    fig.patch.set_facecolor(BG_COLOR)
    for ax in (axes if hasattr(axes, '__iter__') else [axes]):
        ax.set_facecolor(BG_COLOR)
        ax.tick_params(colors=TEXT_COLOR)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color(TEXT_COLOR)
        ax.spines['bottom'].set_color(GRID_COLOR)
        ax.spines['top'].set_color(GRID_COLOR)
        ax.spines['left'].set_color(GRID_COLOR)
        ax.spines['right'].set_color(GRID_COLOR)
        ax.grid(True, color=GRID_COLOR, linewidth=0.5, linestyle='--', alpha=0.7)
        for tick in ax.get_xticklabels():
            tick.set_color(TEXT_COLOR)
        for tick in ax.get_yticklabels():
            tick.set_color(TEXT_COLOR)

# ─── CHART 1: CIV Production + Yield ─────────────────────────────────────────
print("Generating cocoa_civ.png...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Côte d'Ivoire — Cocoa Production & Yield (2000–2024)", color=TEXT_COLOR, fontsize=13)

years_civ = civ_df["year"].tolist()
prods_civ = (civ_df["production_tonnes"] / 1000).tolist()
yields_civ = civ_df["yield_t_per_ha"].tolist()

# Shade ENSO years
for ax in [ax1, ax2]:
    for yr in ENSO_YEARS:
        if yr in years_civ:
            ax.axvspan(yr - 0.4, yr + 0.4, color=ENSO_COLOR, alpha=0.15, zorder=0)

ax1.bar(years_civ, prods_civ, color=ACCENT1, alpha=0.85, width=0.7)
ax1.set_title("Production (kt)", color=TEXT_COLOR)
ax1.set_xlabel("Year")
ax1.set_ylabel("Thousand Tonnes")
for yr in [2015, 2016, 2023]:
    if yr in years_civ:
        idx = years_civ.index(yr)
        ax1.annotate(str(yr), xy=(yr, prods_civ[idx]),
                     xytext=(yr, prods_civ[idx] + 30),
                     color=ENSO_COLOR, fontsize=8, ha='center')

ax2.plot(years_civ, yields_civ, color=ACCENT2, linewidth=1.8, marker='o', markersize=3)
ax2.set_title("Yield (t/ha)", color=TEXT_COLOR)
ax2.set_xlabel("Year")
ax2.set_ylabel("Tonnes per Hectare")
for yr in [2015, 2016, 2023]:
    if yr in years_civ:
        idx = years_civ.index(yr)
        ax2.annotate(str(yr), xy=(yr, yields_civ[idx]),
                     xytext=(yr, yields_civ[idx] + 0.01),
                     color=ENSO_COLOR, fontsize=8, ha='center')

enso_patch = mpatches.Patch(color=ENSO_COLOR, alpha=0.3, label='ENSO Analog Year')
for ax in [ax1, ax2]:
    ax.legend(handles=[enso_patch], facecolor=BG_COLOR, edgecolor=GRID_COLOR,
              labelcolor=TEXT_COLOR, fontsize=8)
    ax.set_xticks(years_civ[::2])
    ax.tick_params(axis='x', rotation=45)

set_dark_style(fig, [ax1, ax2])
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "cocoa_civ.png"), dpi=120, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  cocoa_civ.png saved.")

# ─── CHART 2: Ghana Production + Yield ────────────────────────────────────────
print("Generating cocoa_ghana.png...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Ghana — Cocoa Production & Yield (2000–2024)", color=TEXT_COLOR, fontsize=13)

years_gha = gha_df["year"].tolist()
prods_gha = (gha_df["production_tonnes"] / 1000).tolist()
yields_gha = gha_df["yield_t_per_ha"].tolist()

for ax in [ax1, ax2]:
    for yr in ENSO_YEARS:
        if yr in years_gha:
            ax.axvspan(yr - 0.4, yr + 0.4, color=ENSO_COLOR, alpha=0.15, zorder=0)

ax1.bar(years_gha, prods_gha, color=ACCENT3, alpha=0.85, width=0.7)
ax1.set_title("Production (kt)", color=TEXT_COLOR)
ax1.set_xlabel("Year")
ax1.set_ylabel("Thousand Tonnes")

# Annotate 2020 record high
if 2020 in years_gha:
    idx = years_gha.index(2020)
    ax1.annotate("2020\nRecord", xy=(2020, prods_gha[idx]),
                 xytext=(2018, prods_gha[idx] + 20),
                 color=ACCENT2, fontsize=8, ha='center',
                 arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=1))

# Annotate CSSVD impact
if 2023 in years_gha:
    idx = years_gha.index(2023)
    ax1.annotate("CSSVD\ncrisis", xy=(2023, prods_gha[idx]),
                 xytext=(2021, prods_gha[idx] - 60),
                 color=ENSO_COLOR, fontsize=8, ha='center',
                 arrowprops=dict(arrowstyle='->', color=ENSO_COLOR, lw=1))

ax2.plot(years_gha, yields_gha, color=ACCENT4, linewidth=1.8, marker='o', markersize=3)
ax2.set_title("Yield (t/ha)", color=TEXT_COLOR)
ax2.set_xlabel("Year")
ax2.set_ylabel("Tonnes per Hectare")

enso_patch = mpatches.Patch(color=ENSO_COLOR, alpha=0.3, label='ENSO Analog Year')
for ax in [ax1, ax2]:
    ax.legend(handles=[enso_patch], facecolor=BG_COLOR, edgecolor=GRID_COLOR,
              labelcolor=TEXT_COLOR, fontsize=8)
    ax.set_xticks(years_gha[::2])
    ax.tick_params(axis='x', rotation=45)

set_dark_style(fig, [ax1, ax2])
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "cocoa_ghana.png"), dpi=120, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  cocoa_ghana.png saved.")

# ─── CHART 3: World Context ────────────────────────────────────────────────────
print("Generating cocoa_world_context.png...")
fig, ax = plt.subplots(figsize=(14, 6))
fig.suptitle("Global Cocoa Production by Country (2000–2024)", color=TEXT_COLOR, fontsize=13)

country_colors = {
    "CIV": ACCENT1,
    "GHA": ACCENT3,
    "IDN": ACCENT2,
    "ECU": ACCENT4,
}
country_labels = {"CIV": "Côte d'Ivoire", "GHA": "Ghana", "IDN": "Indonesia", "ECU": "Ecuador"}

for yr in ENSO_YEARS:
    ax.axvspan(yr - 0.4, yr + 0.4, color=ENSO_COLOR, alpha=0.1, zorder=0)

for iso, color in country_colors.items():
    sub = world_df[world_df["entity"] == iso].sort_values("year")
    if not sub.empty:
        years = sub["year"].tolist()
        prods = (sub["production_tonnes"] / 1000).tolist()
        ax.plot(years, prods, color=color, linewidth=1.8, marker='o', markersize=3,
                label=country_labels[iso])

ax.set_xlabel("Year", color=TEXT_COLOR)
ax.set_ylabel("Thousand Tonnes", color=TEXT_COLOR)
ax.legend(facecolor=BG_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
ax.set_xticks(list(range(2000, 2025, 2)))
ax.tick_params(axis='x', rotation=45)

set_dark_style(fig, [ax])
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR, "cocoa_world_context.png"), dpi=120, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("  cocoa_world_context.png saved.")

# ─── ENSO ANALOGS CSV ─────────────────────────────────────────────────────────
print("\nBuilding ENSO analogs CSV...")
analog_rows = []
for iso in ["CIV", "GHA", "IDN", "ECU", "CMR", "NGA", "BRA"]:
    if iso == "CIV":
        df = civ_df
        prov_src = "SOURCE: OWID cocoa-bean-production.csv local file FAO/OWID"
    elif iso == "GHA":
        df = gha_df
        prov_src = "SOURCE: OWID cocoa-bean-production.csv local file FAO/OWID"
    else:
        sub = world_df[world_df["entity"] == iso].sort_values("year")
        df = sub.rename(columns={"production_tonnes": "production_tonnes",
                                  "yield_t_per_ha": "yield_t_per_ha",
                                  "yoy_production_pct": "yoy_production_pct"})
        prov_src = "SOURCE: OWID cocoa-bean-production.csv local file FAO/OWID"

    section_map = {
        "CIV": "West Africa", "GHA": "West Africa",
        "IDN": "Southeast Asia", "ECU": "South America",
        "CMR": "Rest of World", "NGA": "Rest of World", "BRA": "Rest of World",
    }

    if iso in ["CIV", "GHA"]:
        enso_rows = df[df["enso_analog_flag"] == True]
        for _, row in enso_rows.iterrows():
            analog_rows.append({
                "section": section_map[iso],
                "country": iso,
                "analog_year": int(row["year"]),
                "production_t": row["production_tonnes"],
                "yield_t_per_ha": row["yield_t_per_ha"],
                "yoy_production_pct": row.get("yoy_production_pct", None),
                "provenance": prov_src,
            })
    else:
        for _, row in df.iterrows():
            if row.get("enso_analog_flag", False) or row.get("year") in ENSO_YEARS:
                yr = int(row["year"])
                if yr in ENSO_YEARS:
                    analog_rows.append({
                        "section": section_map[iso],
                        "country": iso,
                        "analog_year": yr,
                        "production_t": row["production_tonnes"],
                        "yield_t_per_ha": row["yield_t_per_ha"],
                        "yoy_production_pct": row.get("yoy_production_pct", None),
                        "provenance": prov_src,
                    })

analogs_df = pd.DataFrame(analog_rows)
analogs_df.to_csv(os.path.join(PROC_DIR, "cocoa_enso_analogs.csv"), index=False)
print(f"  ENSO analogs: {len(analogs_df)} rows written")

# ─── BUILD pipeline_output.json ───────────────────────────────────────────────
print("\nBuilding pipeline_output.json...")

def fmt_kt(v):
    """Convert tonnes to kt, round to 1 decimal."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return round(float(v) / 1000, 3)

def fmt_float(v, ndigits=4):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return round(float(v), ndigits)

def country_prod_list(df, iso_label):
    rows = []
    for _, row in df.sort_values("year").iterrows():
        rows.append({
            "yr": str(int(row["year"])),
            "kt": fmt_kt(row["production_tonnes"]),
            "src": "rep",
            "note": "SOURCE: OWID local",
        })
    return rows

def world_prod_list():
    rows = []
    global_sub = world_df[world_df["entity"] == "Global"].sort_values("year")
    for _, row in global_sub.iterrows():
        rows.append({
            "yr": str(int(row["year"])),
            "kt": fmt_kt(row["production_tonnes"]),
            "src": "rep",
            "note": "DERIVED: sum all 7 countries SOURCE OWID local",
        })
    return rows

def country_prod_by_iso(iso):
    sub = world_df[world_df["entity"] == iso].sort_values("year")
    rows = []
    for _, row in sub.iterrows():
        rows.append({
            "yr": str(int(row["year"])),
            "kt": fmt_kt(row["production_tonnes"]),
            "src": "rep",
            "note": "SOURCE: OWID local",
        })
    return rows

# yield trajectory: global production-weighted avg yield, 2000-2024
def yield_trajectory():
    rows = []
    global_sub = world_df[world_df["entity"] == "Global"].sort_values("year")
    prev_yield = None
    for _, row in global_sub.iterrows():
        yr = str(int(row["year"]))
        abs_yield = fmt_float(row.get("yield_t_per_ha"), 4)
        if prev_yield is not None and abs_yield is not None and prev_yield != 0:
            yoy = round((abs_yield - prev_yield) / abs(prev_yield) * 100, 2)
        else:
            yoy = None
        rows.append({
            "yr": yr,
            "yoy": yoy,
            "abs": f"{abs_yield:.4f} t/ha" if abs_yield is not None else None,
            "src": "rep",
            "note": "SOURCE: OWID cocoa-bean-yields.csv production-weighted global avg",
        })
        prev_yield = abs_yield
    return rows

# Grindings trajectory: ECA YTD YoY% for each year pair
# Convert ECA index (e.g. 93.9) to YoY% deviation: (93.9 - 100) = -6.1%
def grindings_trajectory():
    rows = []
    eur_sorted = eur_df[eur_df["ytd_yoy_pct"].notna()].sort_values("year_pair", ascending=False)
    for _, row in eur_sorted.iterrows():
        ytd_index = row["ytd_yoy_pct"]
        # ytd_yoy_pct is an index (e.g. 93.9 = 93.9% of prior year = -6.1% YoY)
        yoy_dev = round(ytd_index - 100, 2)
        rows.append({
            "yr": row["year_pair"],
            "yoy": yoy_dev,
            "abs": "~EUR",
            "src": "rep",
            "note": f"ECA {row['year_pair']} YTD index={ytd_index}%",
        })
    return rows

# Stocks trajectory (from ICCO / supply knowledge)
stocks_trajectory = [
    {
        "yr": "2023/24",
        "yoy": None,
        "abs": "26.4%",
        "src": "rep",
        "note": "ICCO — below 30% threshold",
    }
]

# Forward trajectory (GAIN signals)
gain_civ = gain_df[gain_df["country"] == "CIV"].iloc[0]
gain_gha = gain_df[gain_df["country"] == "GHA"].iloc[0]

forward_trajectory = [
    {
        "yr": "MY2024/25",
        "yoy": -24,
        "abs": "1.76 MMT",
        "src": "rep",
        "note": (
            "USDA GAIN IV2025-0001: CIV MY2023/24 actual -24%. "
            "Harmattan + brown rot. Mid-crop 2025 est 300k MT (-40% vs avg)"
        ),
    },
    {
        "yr": "MY2025/26",
        "yoy": None,
        "abs": "600k MT",
        "src": "rep",
        "note": (
            "USDA GAIN GH2025-0008: Ghana MY2024/25 +13% recovery but "
            "CSSVD 90k+ ha. MY2025/26 expected depressed."
        ),
    },
]

# GAIN summaries
gain_civ_summary = (
    "CIV MY2024/25 production revised to ~1.8 MMT. MY2023/24 actual: 1.76 MMT (-24% vs MY2022/23). "
    "Weather: Heavy rainfall Sep-Oct 2024 spread brown rot (Phytophthora) fungal disease in western/southwestern regions. "
    "Harmattan winds Dec 2024-Feb 2025 raised drought fears for mid-crop. "
    "Mid-crop 2025 estimated at only 300,000 MT (-40% below average). "
    "Disease: Brown rot spread in western/southwestern CIV, compounding yield losses. "
    "Structural risk: EU deforestation regulation effective Dec 30 2025 may disrupt supply chains. "
    "Source: USDA GAIN IV2025-0001, Abidjan/Accra, March 7 2025."
)

gain_gha_summary = (
    "Ghana MY2024/25 production estimated at 600,000 MT (+13% recovery from prior year trough). "
    "Area: 1.27 Mha. COCOBOD shortened the buying season — closed July 31 2025. "
    "Disease: CSSVD (Cocoa Swollen Shoot Virus Disease) affecting 90,000+ ha; "
    "infected trees must be felled, causing permanent yield loss. "
    "Exports MY2024/25: ~520,000 MT (+55% vs prior year, recovery-driven). "
    "Forward: MY2025/26 production expected to remain depressed despite partial 2024/25 recovery. "
    "CSSVD remains endemic and continues to erode productive area. "
    "Source: USDA GAIN GH2025-0008, Accra, 2025."
)

pipeline_output = {
    "countryProd": {
        "civ": country_prod_list(civ_df, "CIV"),
        "gha": country_prod_list(gha_df, "GHA"),
        "ecu": country_prod_by_iso("ECU"),
        "idn": country_prod_by_iso("IDN"),
        "wld": world_prod_list(),
    },
    "yieldTrajectory": yield_trajectory(),
    "grindingsTrajectory": grindings_trajectory(),
    "stocksTrajectory": stocks_trajectory,
    "forwardTrajectory": forward_trajectory,
    "gainCivSummary": gain_civ_summary,
    "gainGhaSummary": gain_gha_summary,
    "supplySignal": "DEFICIT CRITICAL",
    "stocksToGrindings": 0.264,
    "step6Summary": "",  # filled in step 6
}

# Write preliminary JSON (step6Summary will be appended after step 6)
out_json_path = os.path.join(PROC_DIR, "pipeline_output.json")
with open(out_json_path, "w", encoding="utf-8") as f:
    json.dump(pipeline_output, f, indent=2, ensure_ascii=False)

print(f"  pipeline_output.json written: {out_json_path}")
print(f"\nData shapes:")
print(f"  countryProd.civ: {len(pipeline_output['countryProd']['civ'])} entries")
print(f"  countryProd.gha: {len(pipeline_output['countryProd']['gha'])} entries")
print(f"  countryProd.ecu: {len(pipeline_output['countryProd']['ecu'])} entries")
print(f"  countryProd.idn: {len(pipeline_output['countryProd']['idn'])} entries")
print(f"  countryProd.wld: {len(pipeline_output['countryProd']['wld'])} entries")
print(f"  yieldTrajectory: {len(pipeline_output['yieldTrajectory'])} entries")
print(f"  grindingsTrajectory: {len(pipeline_output['grindingsTrajectory'])} entries")
print(f"  forwardTrajectory: {len(pipeline_output['forwardTrajectory'])} entries")

print("\nFirst 5 rows of countryProd.civ:")
for row in pipeline_output["countryProd"]["civ"][:5]:
    print(f"  {row}")

print("\ngrindingsTrajectory:")
for row in pipeline_output["grindingsTrajectory"]:
    print(f"  {row}")
