"""
STEP 4 — Grindings (live fetch + seed fallback)
ECA PDFs fetched but not text-extractable.
Seed values used as specified per pipeline instructions.
"""

import pandas as pd
import os

PROC_DIR = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"
os.makedirs(PROC_DIR, exist_ok=True)

# ─── EUROPE (ECA) ─────────────────────────────────────────────────────────────
# PDFs fetched but image-only (not text-extractable). Using confirmed seed values.
europe_rows = [
    {
        "year_pair": "2026/2025",
        "q1_yoy_pct": 92.2,
        "q2_yoy_pct": None,
        "q3_yoy_pct": None,
        "q4_yoy_pct": None,
        "ytd_yoy_pct": 92.2,
        "provenance": "SEED: ECA Q1 2026 confirmed — ECA PDF fetched but image-only",
    },
    {
        "year_pair": "2025/2024",
        "q1_yoy_pct": 95.6,
        "q2_yoy_pct": 92.8,
        "q3_yoy_pct": 95.2,
        "q4_yoy_pct": 91.7,
        "ytd_yoy_pct": 93.9,
        "provenance": "SEED: ECA confirmed — ECA PDF fetched but image-only",
    },
    {
        "year_pair": "2024/2023",
        "q1_yoy_pct": 98.5,
        "q2_yoy_pct": 104.1,
        "q3_yoy_pct": 96.7,
        "q4_yoy_pct": 94.6,
        "ytd_yoy_pct": 98.5,
        "provenance": "SEED: ECA confirmed — ECA PDF fetched but image-only",
    },
    {
        "year_pair": "2023/2022",
        "q1_yoy_pct": None,
        "q2_yoy_pct": None,
        "q3_yoy_pct": None,
        "q4_yoy_pct": None,
        "ytd_yoy_pct": None,
        "provenance": "ESTIMATED BY CLAUDE — ECA fetch failed",
    },
    {
        "year_pair": "2022/2021",
        "q1_yoy_pct": None,
        "q2_yoy_pct": None,
        "q3_yoy_pct": None,
        "q4_yoy_pct": None,
        "ytd_yoy_pct": None,
        "provenance": "ESTIMATED BY CLAUDE — ECA fetch failed",
    },
]

europe_df = pd.DataFrame(europe_rows)
europe_df.to_csv(os.path.join(PROC_DIR, "cocoa_grindings_europe.csv"), index=False)
print(f"Europe grindings: {len(europe_df)} rows written")
print(f"  2026/2025 Q1 YTD: {europe_df[europe_df['year_pair']=='2026/2025']['ytd_yoy_pct'].values[0]}%")
print(f"  2025/2024 YTD:    {europe_df[europe_df['year_pair']=='2025/2024']['ytd_yoy_pct'].values[0]}%")

# ─── NORTH AMERICA (NCA/CANDY USA) ─────────────────────────────────────────────
# Q1 2026 seed confirmed: 106,087 MT, -3.8% YoY (reported by Candy USA)
na_rows = [
    {
        "year": 2026,
        "quarter": "Q1",
        "volume_mt": 106087,
        "yoy_pct": -3.8,
        "provenance": "SEED: NCA Q1 2026 confirmed — Candy USA report (PDF link found, data not extracted from page body)",
    },
]
na_df = pd.DataFrame(na_rows)
na_df.to_csv(os.path.join(PROC_DIR, "cocoa_grindings_north_america.csv"), index=False)
print(f"\nNorth America grindings: {len(na_df)} rows written")
print(f"  2026 Q1: {na_df.iloc[0]['volume_mt']} MT, YoY={na_df.iloc[0]['yoy_pct']}%")

# ─── ASIA ─────────────────────────────────────────────────────────────────────
# Q1 2026 seed confirmed: 223,503 MT, +5.2% YoY
# Asia website shows Q1 2026 as TBU (scheduled Apr 16 2026) — using confirmed seed
asia_rows = [
    {
        "year": 2026,
        "quarter": "Q1",
        "volume_mt": 223503,
        "yoy_pct": 5.2,
        "provenance": "SEED: Asia Q1 2026 confirmed — Cocoa Association of Asia (site shows TBU, seed values used)",
    },
]
asia_df = pd.DataFrame(asia_rows)
asia_df.to_csv(os.path.join(PROC_DIR, "cocoa_grindings_asia.csv"), index=False)
print(f"\nAsia grindings: {len(asia_df)} rows written")
print(f"  2026 Q1: {asia_df.iloc[0]['volume_mt']} MT, YoY=+{asia_df.iloc[0]['yoy_pct']}%")

print("\nAll grindings CSVs written.")
print("Note: ECA PDFs were fetched (200 OK) but are image-only — seed values used.")
print("Note: Candy USA page loaded but Q1 2026 data not in page body — seed used.")
print("Note: Asia site shows Q1 2026 TBU (scheduled Apr 16 2026) — seed used.")
