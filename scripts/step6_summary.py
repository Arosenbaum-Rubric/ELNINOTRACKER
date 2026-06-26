"""
STEP 6 — STDOUT Summary
Reads all processed files and prints the full pipeline summary.
Also updates pipeline_output.json with step6Summary.
"""

import pandas as pd
import json
import os
import numpy as np
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROC_DIR = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"

# Load all data
civ_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_civ_2000_2024.csv"))
gha_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_ghana_2000_2024.csv"))
world_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_world_context_2000_2024.csv"))
psd_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_psd_2000_2024.csv"))
gain_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_gain_signals.csv"))
eur_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_grindings_europe.csv"))
na_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_grindings_north_america.csv"))
asia_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_grindings_asia.csv"))
analogs_df = pd.read_csv(os.path.join(PROC_DIR, "cocoa_enso_analogs.csv"))

with open(os.path.join(PROC_DIR, "pipeline_output.json"), "r", encoding="utf-8") as f:
    pipeline = json.load(f)

gain_civ = gain_df[gain_df["country"] == "CIV"].iloc[0]
gain_gha = gain_df[gain_df["country"] == "GHA"].iloc[0]

global_sub = world_df[world_df["entity"] == "Global"].sort_values("year")
civ_2024 = civ_df[civ_df["year"] == 2024].iloc[0]
gha_2024 = gha_df[gha_df["year"] == 2024].iloc[0]

# ENSO analog summaries for CIV
civ_analogs = analogs_df[analogs_df["country"] == "CIV"].sort_values("analog_year")
gha_analogs = analogs_df[analogs_df["country"] == "GHA"].sort_values("analog_year")

lines = []
def pr(s=""):
    lines.append(s)
    print(s)

pr("=" * 70)  # ASCII-safe
pr("EL NIÑO COCOA SUPPLY PIPELINE — FULL ANALYSIS SUMMARY")
pr("Pipeline run date: 2026-06-25 | Data through: 2024 (OWID) / MY2024/25 (GAIN)")
pr("=" * 70)  # ASCII-safe

pr()
pr("-" * 70)
pr("SECTION 1: CÔTE D'IVOIRE (CIV) — PRIMARY PRODUCER")
pr("-" * 70)
pr(f"  2024 (calendar year, OWID/FAO):")
pr(f"    Production:   {civ_2024['production_tonnes']:>12,.0f} t  ({civ_2024['production_tonnes']/1000:.1f} kt)")
pr(f"    Yield:        {civ_2024['yield_t_per_ha']:.4f} t/ha")
if civ_2024["yoy_production_pct"] is not None and not (isinstance(civ_2024["yoy_production_pct"], float) and np.isnan(civ_2024["yoy_production_pct"])):
    pr(f"    YoY prod:     {civ_2024['yoy_production_pct']:+.1f}%")
if civ_2024["yoy_yield_pct"] is not None and not (isinstance(civ_2024["yoy_yield_pct"], float) and np.isnan(civ_2024["yoy_yield_pct"])):
    pr(f"    YoY yield:    {civ_2024['yoy_yield_pct']:+.1f}%")
pr()
pr(f"  MY2024/25 (USDA GAIN IV2025-0001):")
pr(f"    Production (MY2023/24 actual):  {gain_civ['production_mmt']:.2f} MMT  (YoY: {gain_civ['yoy_pct']:+.0f}%)")
pr(f"    MY2024/25 revised forecast:     ~1.8 MMT")
pr(f"    Mid-crop 2025 estimate:         ~300,000 MT  (-40% vs avg)")
pr()
pr(f"  Weather signal:")
pr(f"    {gain_civ['weather_signal']}")
pr()
pr(f"  Disease signal:")
pr(f"    {gain_civ['disease_signal']}")
pr()
pr(f"  Forward outlook:")
pr(f"    {gain_civ['forward_outlook']}")
pr(f"  Provenance: {gain_civ['provenance']}")
pr()
pr(f"  Yield deviation flags (yoy_yield < -5%): {civ_df['yield_deviation_flag'].sum()} years out of 24")
civ_flag_years = civ_df[civ_df["yield_deviation_flag"] == True]["year"].tolist()
pr(f"    Flagged years: {civ_flag_years}")

pr()
pr("-" * 70)
pr("SECTION 2: GHANA (GHA) — SECONDARY PRODUCER")
pr("-" * 70)
pr(f"  2024 (calendar year, OWID/FAO):")
pr(f"    Production:   {gha_2024['production_tonnes']:>12,.0f} t  ({gha_2024['production_tonnes']/1000:.1f} kt)")
pr(f"    Yield:        {gha_2024['yield_t_per_ha']:.4f} t/ha")
if gha_2024["yoy_production_pct"] is not None and not (isinstance(gha_2024["yoy_production_pct"], float) and np.isnan(gha_2024["yoy_production_pct"])):
    pr(f"    YoY prod:     {gha_2024['yoy_production_pct']:+.1f}%")
if gha_2024["yoy_yield_pct"] is not None and not (isinstance(gha_2024["yoy_yield_pct"], float) and np.isnan(gha_2024["yoy_yield_pct"])):
    pr(f"    YoY yield:    {gha_2024['yoy_yield_pct']:+.1f}%")
pr()
pr(f"  MY2024/25 (USDA GAIN GH2025-0008):")
pr(f"    Production:   {gain_gha['production_mmt']:.3f} MMT  (YoY: {gain_gha['yoy_pct']:+.0f}%)")
pr(f"    Area:         {gain_gha['area_mha']:.2f} Mha")
pr(f"    Exports:      {gain_gha['exports_mmt']:.3f} MMT  (+55% vs prior year)")
pr(f"    CSSVD ha:     90,000+ ha infected (permanent yield loss)")
pr()
pr(f"  Weather signal:")
pr(f"    {gain_gha['weather_signal']}")
pr()
pr(f"  Disease signal:")
pr(f"    {gain_gha['disease_signal']}")
pr()
pr(f"  Forward outlook:")
pr(f"    {gain_gha['forward_outlook']}")
pr(f"  Provenance: {gain_gha['provenance']}")
pr()
pr(f"  Yield deviation flags (yoy_yield < -5%): {gha_df['yield_deviation_flag'].sum()} years out of 24")
gha_flag_years = gha_df[gha_df["yield_deviation_flag"] == True]["year"].tolist()
pr(f"    Flagged years: {gha_flag_years}")

pr()
pr("-" * 70)
pr("SECTION 3: WORLD CONTEXT (2024, OWID/FAO)")
pr("-" * 70)
global_2024 = global_sub[global_sub["year"] == 2024].iloc[0]
pr(f"  Global total production (7 countries):  {global_2024['production_tonnes']/1000:.1f} kt")
pr()
for iso in ["CIV", "GHA", "IDN", "ECU", "CMR", "NGA", "BRA"]:
    sub = world_df[(world_df["entity"] == iso) & (world_df["year"] == 2024)]
    if not sub.empty:
        row = sub.iloc[0]
        prod = row["production_tonnes"]
        share = prod / global_2024["production_tonnes"] * 100
        pr(f"  {iso:5s}  {prod/1000:7.1f} kt  ({share:.1f}% of tracked global)")

pr()
row_2024 = world_df[(world_df["entity"] == "Rest of World") & (world_df["year"] == 2024)]
if not row_2024.empty:
    pr(f"  Rest of World (CMR+NGA+BRA): {row_2024.iloc[0]['production_tonnes']/1000:.1f} kt")

pr()
pr("-" * 70)
pr("SECTION 4: GRINDINGS (DEMAND SIDE)")
pr("-" * 70)
pr("  Europe (ECA Western Europe grindings index, YTD YoY vs prior year):")
for _, row in eur_df[eur_df["ytd_yoy_pct"].notna()].iterrows():
    idx = row["ytd_yoy_pct"]
    dev = idx - 100
    pr(f"    {row['year_pair']:12s}  YTD index={idx:.1f}%  →  YoY deviation={dev:+.1f}%")
pr()
pr("  North America (NCA / Candy USA):")
for _, row in na_df.iterrows():
    pr(f"    {row['year']} {row['quarter']}:  {row['volume_mt']:>8,.0f} MT  (YoY: {row['yoy_pct']:+.1f}%)")
pr()
pr("  Asia (Cocoa Association of Asia):")
for _, row in asia_df.iterrows():
    pr(f"    {row['year']} {row['quarter']}:  {row['volume_mt']:>8,.0f} MT  (YoY: +{row['yoy_pct']:.1f}%)")
pr()
pr("  Demand read: Europe contracting -6% to -8% YoY. Asia growing +5% YoY.")
pr("  Net: demand destruction in Europe outweighs Asia growth — overall grindings declining.")

pr()
pr("-" * 70)
pr("SECTION 5: SUPPLY/DEMAND BALANCE")
pr("-" * 70)
pr("  Supply signal: DEFICIT CRITICAL")
pr("  Stocks-to-grindings (ICCO, 2023/24): 26.4%  (below 30% critical threshold)")
pr()
pr("  Key drivers:")
pr("    1. CIV MY2023/24 actual: 1.76 MMT  (-24% YoY) — worst in years")
pr("    2. Ghana structural decline: CSSVD disease on 90,000+ ha of productive area")
pr("    3. CIV mid-crop 2025: ~300,000 MT  (-40% below historical avg)")
pr("    4. El Niño-driven weather pattern (Harmattan + brown rot) compounding losses")
pr("    5. EU deforestation regulation (Dec 30 2025) introduces supply chain disruption risk")
pr("    6. European grindings declining -6% to -8% YoY — demand is being rationed")

pr()
pr("-" * 70)
pr("SECTION 6: ENSO ANALOG ANALYSIS")
pr("-" * 70)
pr("  ENSO analog years: 2009, 2010, 2015, 2016, 2023")
pr()
pr("  CIV production during ENSO analogs:")
for _, row in civ_analogs.iterrows():
    yoy_str = f"  YoY: {row['yoy_production_pct']:+.1f}%" if row["yoy_production_pct"] is not None and not (isinstance(row["yoy_production_pct"], float) and np.isnan(row["yoy_production_pct"])) else ""
    pr(f"    {int(row['analog_year'])}: {row['production_t']/1000:7.1f} kt  yield={row['yield_t_per_ha']:.4f} t/ha{yoy_str}")

pr()
pr("  Ghana production during ENSO analogs:")
for _, row in gha_analogs.iterrows():
    yoy_str = f"  YoY: {row['yoy_production_pct']:+.1f}%" if row["yoy_production_pct"] is not None and not (isinstance(row["yoy_production_pct"], float) and np.isnan(row["yoy_production_pct"])) else ""
    pr(f"    {int(row['analog_year'])}: {row['production_t']/1000:7.1f} kt  yield={row['yield_t_per_ha']:.4f} t/ha{yoy_str}")

pr()
pr("  Pattern: ENSO analog years show a consistent yield suppression signal for CIV,")
pr("  with 2023 being the sharpest recent contraction. Ghana's analog years are mixed,")
pr("  reflecting that CSSVD disease is now the dominant structural factor over weather.")

pr()
pr("-" * 70)
pr("SECTION 7: CLAUDE ANALYSIS — 2026 EL NIÑO OUTLOOK")
pr("-" * 70)
pr("  El Niño signal (2026 analog to 2015/16):")
pr("    → West Africa: Harmattan-driven drought risk in Dec-Mar is the key production window")
pr("       for the CIV mid-crop. The 2024/25 mid-crop is already at -40% vs avg, with Harmattan")
pr("       winds having run Dec 2024 – Feb 2025.")
pr("    → Historical analog: 2015/16 El Niño → CIV yield dropped sharply; Ghana ENSO analog")
pr("       2015/2016 showed similar contraction.")
pr()
pr("  Structural factors compounding cyclical El Niño risk:")
pr("    1. CSSVD (Ghana): 90,000+ ha of infected trees must be felled — permanent productive")
pr("       area destruction, not recoverable within one season.")
pr("    2. Brown rot (CIV): Phytophthora spread through western/southwestern growing regions.")
pr("    3. EUDR (EU deforestation regulation): Creates certification compliance friction that")
pr("       could slow exports to EU regardless of production outcome.")
pr()
pr("  Conviction level: HIGH DEFICIT")
pr("    - Two largest producers (CIV + Ghana = ~55% of tracked global supply) both in")
pr("      structural and cyclical decline simultaneously.")
pr("    - Stocks-to-grindings at 26.4% — below the 30% market stress threshold.")
pr("    - Grindings in Europe declining (-6% to -8%) shows demand is already being rationed.")
pr("    - Asia grindings still growing (+5%) but insufficient to offset supply shortfall.")
pr()
pr("  2026 El Niño forecast:")
pr("    → Supply deficit likely to persist or worsen through MY2025/26.")
pr("    → CIV mid-crop 2025 (300k MT) implies MY2024/25 full year well below 1.9 MMT baseline.")
pr("    → Ghana MY2025/26 production 'expected to remain depressed' per GAIN GH2025-0008.")
pr("    → Key monitoring: main crop Sep-Nov 2025 (CIV), COCOBOD season opening (Ghana).")
pr()
pr("  DATA SOURCES USED IN THIS PIPELINE:")
pr("    1. OWID/FAO cocoa-bean-production.csv — historical production 2000-2024")
pr("    2. OWID/FAO cocoa-bean-yields.csv — historical yield 2000-2024")
pr("    3. USDA GAIN IV2025-0001 — CIV MY2024/25 forward signal (Mar 7 2025)")
pr("    4. USDA GAIN GH2025-0008 — Ghana MY2024/25 forward signal (2025)")
pr("    5. ECA (European Cocoa Association) — grindings index Q1 2026, FY2025, FY2024")
pr("    6. NCA (Candy USA) — North America Q1 2026 grindings 106,087 MT (-3.8% YoY)")
pr("    7. Cocoa Association of Asia — Asia Q1 2026 grindings 223,503 MT (+5.2% YoY)")
pr("    8. USDA FAS PSD API — returned HTTP 500 (server down); PSD fields null in output")
pr()
pr("=" * 70)  # ASCII-safe
pr("END OF PIPELINE SUMMARY")
pr("=" * 70)  # ASCII-safe

# Combine into single string
step6_text = "\n".join(lines)

# Update pipeline_output.json with step6Summary
pipeline["step6Summary"] = step6_text
out_json_path = os.path.join(PROC_DIR, "pipeline_output.json")
with open(out_json_path, "w", encoding="utf-8") as f:
    json.dump(pipeline, f, indent=2, ensure_ascii=False)

print(f"\npipeline_output.json updated with step6Summary ({len(step6_text)} chars).")
print(f"Output: {out_json_path}")
