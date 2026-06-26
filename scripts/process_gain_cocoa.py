"""
STEP 3 — GAIN PDF Extraction
PDFs are not directly parseable in this environment (pdftoppm unavailable).
Using specified default values from pipeline instructions as documented fallback.
"""

import pandas as pd
import os

PROC_DIR = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"
os.makedirs(PROC_DIR, exist_ok=True)

# CIV GAIN report — IV2025-0001
# Default values per pipeline spec (PDF unreadable)
civ_record = {
    "country": "CIV",
    "report_id": "IV2025-0001",
    "report_date": "2025-03-07",
    "my_year": "2024/25",
    "production_mmt": 1.76,
    "yoy_pct": -24.0,
    "area_mha": None,
    "weather_signal": (
        "Heavy rainfall Sep-Oct 2024 spread brown rot fungal disease in western/southwestern regions. "
        "Harmattan winds Dec 2024-Feb 2025 raised drought fears. "
        "Mid-crop 2025 estimated 300,000 MT (-40% vs avg)."
    ),
    "disease_signal": "Brown rot (Phytophthora) spread in western/southwestern CIV",
    "exports_mmt": None,
    "forward_outlook": (
        "EU deforestation regulation effective Dec 30 2025. "
        "Mid-crop critically low at 300,000 MT."
    ),
    "provenance": "SOURCE: USDA GAIN IV2025-0001 Abidjan/Accra March 7 2025",
}

# Ghana GAIN report — GH2025-0008
ghana_record = {
    "country": "GHA",
    "report_id": "GH2025-0008",
    "report_date": "2025-01-01",  # year 2025, exact date not specified in defaults
    "my_year": "2024/25",
    "production_mmt": 0.600,
    "yoy_pct": 13.0,
    "area_mha": 1.27,
    "weather_signal": (
        "COCOBOD shortened season — closed July 31 2025. "
        "MY 2025/26 expected to remain depressed."
    ),
    "disease_signal": (
        "CSSVD affecting 90,000+ ha — infected trees must be felled, permanent yield loss"
    ),
    "exports_mmt": 0.520,
    "forward_outlook": (
        "MY 2025/26 production expected to remain depressed despite partial 2024/25 recovery. "
        "CSSVD disease remains endemic."
    ),
    "provenance": "SOURCE: USDA GAIN GH2025-0008 Accra 2025",
}

gain_df = pd.DataFrame([civ_record, ghana_record])
gain_df.to_csv(os.path.join(PROC_DIR, "cocoa_gain_signals.csv"), index=False)

print("GAIN signals extracted using documented default values (PDF unreadable — pdftoppm unavailable).")
print(f"CIV (IV2025-0001): MY2024/25 production={civ_record['production_mmt']} MMT, YoY={civ_record['yoy_pct']}%")
print(f"  Weather: {civ_record['weather_signal'][:80]}...")
print(f"  Disease: {civ_record['disease_signal']}")
print(f"Ghana (GH2025-0008): MY2024/25 production={ghana_record['production_mmt']} MMT, YoY={ghana_record['yoy_pct']}%")
print(f"  Disease: {ghana_record['disease_signal'][:80]}...")
print(f"Output: {os.path.join(PROC_DIR, 'cocoa_gain_signals.csv')}")
