"""
Peru Avocado Water Stress — chart + CSV generator
Identifies coastal vs national file by 1991-2020 mean, then produces:
  outputs/peru_chart5_water_stress.png
  outputs/peru_water_stress.csv
"""
import glob, os, csv
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.join(BASE, '..', '..', '..')   # ELNINO tracker root
OUT = os.path.join(PROJECT, 'outputs')
os.makedirs(OUT, exist_ok=True)

# ── 1. Load both CSVs ────────────────────────────────────────────────────────
patterns = ['observed-timeseries*', 'precip*', 'rainfall*']
files = []
for p in patterns:
    files += glob.glob(os.path.join(BASE, p))
files = sorted(set(files))
assert len(files) == 2, f"Expected 2 files, found {len(files)}: {files}"

dfs = []
for f in files:
    df = pd.read_csv(f)
    df.columns = ['year', 'precip_mm', 'smooth']
    df['year'] = df['year'].astype(int)
    df['file'] = os.path.basename(f)
    dfs.append(df)

# ── 2. Identify coastal vs national by 1991-2020 mean ───────────────────────
COASTAL_BASELINE = 544.0
NATIONAL_BASELINE = 1606.0

for df in dfs:
    ref = df[(df['year'] >= 1991) & (df['year'] <= 2020)]['precip_mm'].mean()
    df['_ref_mean'] = ref

coastal_df = min(dfs, key=lambda d: abs(d['_ref_mean'].iloc[0] - COASTAL_BASELINE))
national_df = max(dfs, key=lambda d: d['_ref_mean'].iloc[0])

print(f"Coastal file:  {coastal_df['file'].iloc[0]}  (1991-2020 mean = {coastal_df['_ref_mean'].iloc[0]:.1f} mm)")
print(f"National file: {national_df['file'].iloc[0]}  (1991-2020 mean = {national_df['_ref_mean'].iloc[0]:.1f} mm)")

# ── 3. Filter to 2000–2024 ───────────────────────────────────────────────────
c = coastal_df[(coastal_df['year'] >= 2000) & (coastal_df['year'] <= 2024)].copy()
n = national_df[(national_df['year'] >= 2000) & (national_df['year'] <= 2024)].copy()

c['pct_coastal']  = (c['precip_mm'] - COASTAL_BASELINE)  / COASTAL_BASELINE  * 100
n['pct_national'] = (n['precip_mm'] - NATIONAL_BASELINE) / NATIONAL_BASELINE * 100

# ── 4. Thresholds & flags ────────────────────────────────────────────────────
FLOOD_THRESH  = +50.0
DROUGHT_THRESH = -30.0
ENSO_YEARS = {2009, 2010, 2015, 2016, 2017, 2023, 2024}
ELNINO_SHADE = {2015, 2016, 2017}
LANINA_SHADE  = {2021, 2022, 2024}

c['flooding_risk_flag'] = (c['pct_coastal'] > FLOOD_THRESH).astype(int)
c['drought_flag']       = (c['pct_coastal'] < DROUGHT_THRESH).astype(int)
c['enso_analog_flag']   = c['year'].isin(ENSO_YEARS).astype(int)

# ── 5. Build chart ────────────────────────────────────────────────────────────
BG   = '#0a0e16'
GRID = '#1b232d'

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

years = c['year'].values
pct_c = c['pct_coastal'].values
pct_n = n['pct_national'].values

# Shade ENSO bands
for yr in years:
    if yr in ELNINO_SHADE:
        ax.axvspan(yr - 0.5, yr + 0.5, color='#fbbf24', alpha=0.12, zorder=0)
    elif yr in LANINA_SHADE:
        ax.axvspan(yr - 0.5, yr + 0.5, color='#38bdf8', alpha=0.10, zorder=0)

# Threshold lines
ax.axhline(FLOOD_THRESH,   color='#60a5fa', linewidth=1, linestyle='--', alpha=0.7, zorder=1)
ax.axhline(DROUGHT_THRESH, color='#f87171', linewidth=1, linestyle='--', alpha=0.7, zorder=1)
ax.axhline(0, color='#475569', linewidth=0.8, linestyle='-', alpha=0.5, zorder=1)

# Bars — blue positive (flooding risk), red negative (drought)
bar_colors = ['#3b82f6' if v >= 0 else '#ef4444' for v in pct_c]
# Stronger shade for threshold exceedances
bar_colors = ['#1d4ed8' if v > FLOOD_THRESH else ('#991b1b' if v < DROUGHT_THRESH else c) for v, c in zip(pct_c, bar_colors)]
bars = ax.bar(years, pct_c, color=bar_colors, width=0.7, zorder=2, alpha=0.85)

# National line overlay
ax.plot(years, pct_n, color='#94a3b8', linewidth=1.2, linestyle=':', alpha=0.75, zorder=3, label='National avg anomaly %')

# Annotations
for yr, val, label_str in [
    (2017, c.loc[c['year']==2017, 'pct_coastal'].values[0], "El Niño Costero\n+92% flooding"),
    (2024, c.loc[c['year']==2024, 'pct_coastal'].values[0], "La Niña\n−38% cold"),
]:
    offset = 14 if val >= 0 else -18
    ax.annotate(
        label_str,
        xy=(yr, val), xytext=(yr, val + offset),
        ha='center', va='bottom' if val >= 0 else 'top',
        fontsize=7.5, color='#e2e8f0',
        arrowprops=dict(arrowstyle='->', color='#e2e8f0', lw=0.8),
    )

# Threshold labels
ax.text(2000.2, FLOOD_THRESH + 1.5, '+50% flooding risk', color='#60a5fa', fontsize=7.5, va='bottom', alpha=0.85)
ax.text(2000.2, DROUGHT_THRESH - 1.5, '−30% drought stress', color='#f87171', fontsize=7.5, va='top', alpha=0.85)

# Axes styling
ax.set_xlim(1999.3, 2024.7)
ax.set_xticks(years)
ax.set_xticklabels([str(y) for y in years], rotation=60, ha='right', color='#8b9bab', fontsize=8)
ax.set_ylabel('Precip. anomaly %\nvs baseline', color='#8b9bab', fontsize=9)
ax.tick_params(axis='y', colors='#8b9bab', labelsize=8)
ax.spines[:].set_color(GRID)
ax.grid(axis='y', color=GRID, linewidth=0.7, zorder=0)

# Legend
legend_items = [
    mpatches.Patch(color='#3b82f6', alpha=0.85, label='Coastal anomaly (flooding risk zone)'),
    mpatches.Patch(color='#ef4444', alpha=0.85, label='Coastal anomaly (drought zone)'),
    plt.Line2D([0],[0], color='#94a3b8', linewidth=1.2, linestyle=':', label=f'National avg anomaly (ref, baseline {NATIONAL_BASELINE:.0f}mm)'),
    mpatches.Patch(color='#fbbf24', alpha=0.35, label='El Niño analog years (2015–2017)'),
    mpatches.Patch(color='#38bdf8', alpha=0.30, label='La Niña analog years (2021,2022,2024)'),
]
ax.legend(handles=legend_items, loc='upper left', framealpha=0.2, fontsize=7.5,
          facecolor=BG, edgecolor=GRID, labelcolor='#cbd5e1')

title = (
    "Peru Avocado Regions — Coastal Precipitation Anomaly 2000–2024\n"
    f"(La Libertad/Lambayeque baseline {COASTAL_BASELINE:.0f}mm  |  National reference {NATIONAL_BASELINE:.0f}mm)\n"
    "Blue = Flooding Risk  |  Red = Drought Stress  |  Yellow = El Niño  |  Light Blue = La Niña"
)
ax.set_title(title, color='#e2e8f0', fontsize=9.5, pad=12, loc='left')

plt.tight_layout()
chart_path = os.path.join(OUT, 'peru_chart5_water_stress.png')
plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print(f"Chart saved: {chart_path}")

# ── 6. Build output CSV ───────────────────────────────────────────────────────
# Merge coastal + national on year
merged = c.merge(n[['year','precip_mm','pct_national']], on='year', suffixes=('_coastal','_national'))
merged.rename(columns={'precip_mm_coastal':'precip_mm_coastal','precip_mm_national':'precip_mm_national'}, inplace=True)

csv_path = os.path.join(OUT, 'peru_water_stress.csv')
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow([
        'year','country','iso_code','commodity','climate_region',
        'precip_mm_coastal','precip_mm_national',
        'pct_anomaly_coastal','pct_anomaly_national',
        'flooding_risk_flag','drought_flag','enso_analog_flag','provenance'
    ])
    for _, row in merged.iterrows():
        w.writerow([
            int(row['year']),
            'Peru', 'PER', 'Avocado', 'Peru-Coastal-La-Libertad-Lambayeque',
            round(row['precip_mm_coastal'], 2),
            round(row['precip_mm_national'], 2),
            round(row['pct_coastal'], 2),
            round(row['pct_national'], 2),
            int(row['flooding_risk_flag']),
            int(row['drought_flag']),
            int(row['enso_analog_flag']),
            'SOURCE: World Bank CCKP coastal CSV + national CSV'
        ])
print(f"CSV saved: {csv_path}")
print("\nCoastal anomaly summary (2000-2024):")
for _, row in merged.iterrows():
    flags = []
    if row['flooding_risk_flag']: flags.append('FLOOD')
    if row['drought_flag']: flags.append('DROUGHT')
    if row['enso_analog_flag']: flags.append('ENSO')
    print(f"  {int(row['year'])}: {row['pct_coastal']:+.1f}%  {'  '.join(flags)}")
