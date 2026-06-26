"""
Generate three palm oil production charts for the El Niño dashboard.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import os

RAW       = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data"
PROCESSED = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"
CHARTS    = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\charts"
os.makedirs(CHARTS, exist_ok=True)

# ── Style ─────────────────────────────────────────────────────────────────────
BG       = '#0a0e16'
SURFACE  = '#111827'
GRID     = '#1f2937'
TEXT     = '#e2e8f0'
MUTED    = '#8b9bab'
BLUE     = '#38bdf8'
GREEN    = '#4ade80'
RED      = '#f87171'
YELLOW   = '#fbbf24'
ORANGE   = '#fb923c'

def style_ax(ax, title, ylabel, source):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=MUTED, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.set_title(title, color=TEXT, fontsize=13, fontweight='bold', pad=12)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9)
    ax.set_xlabel('')
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, linestyle='--', alpha=0.8)
    ax.xaxis.grid(False)
    ax.tick_params(axis='x', rotation=45)
    ax.figure.text(0.5, 0.01, source, ha='center', color=MUTED, fontsize=7,
                   style='italic', wrap=True)

def shade_psd_only(ax, ymax):
    """Shade 2000-2009 as USDA PSD-only era (no MPOB regional data)."""
    ax.axvspan(1999.6, 2009.4, color='#6b7280', alpha=0.09, zorder=-1)
    ax.text(2004.5, ymax * 0.92, 'PSD\nonly', ha='center', va='top',
            color='#9ca3af', fontsize=6, style='italic', alpha=0.7)

def shade_enso(ax, ymin, ymax):
    """Shade El Niño event bands."""
    events = [
        (2009, 2010, 'El Niño\n09/10'),
        (2015, 2016, 'El Niño\n15/16'),
        (2023, 2024, 'El Niño\n23/24'),
        (2026, 2026, '⚠ 2026'),
    ]
    for start, end, label in events:
        color = ORANGE if '2026' in label else '#fbbf24'
        alpha = 0.18 if '2026' in label else 0.12
        ax.axvspan(start - 0.4, end + 0.4, color=color, alpha=alpha, zorder=0)
        ax.text((start + end) / 2, ymax * 0.98, label,
                ha='center', va='top', color=color, fontsize=6.5,
                fontweight='bold', alpha=0.85)

# ── Load data ─────────────────────────────────────────────────────────────────
psd_all = pd.read_csv(os.path.join(RAW, 'psd_oilseeds.csv'), dtype={'Commodity_Code': str})
mpob    = pd.read_csv(os.path.join(PROCESSED, 'mpob_annual.csv'))
shock   = pd.read_csv(os.path.join(PROCESSED, 'palm_supply_shock.csv'))

# Global CPO production from PSD — take latest estimate per market year
palm_global = psd_all[
    (psd_all['Commodity_Code'] == '4243000') &
    (psd_all['Attribute_ID'] == 28) &
    (psd_all['Market_Year'].between(2000, 2026))
].copy()
palm_global = palm_global.sort_values(['Market_Year', 'Calendar_Year', 'Month'])
palm_global = palm_global.groupby('Market_Year')['Value'].sum().reset_index()
# Value is sum of all countries in 1000 MT
palm_global = palm_global.rename(columns={'Market_Year': 'year', 'Value': 'global_1000mt'})
palm_global['global_mmt'] = palm_global['global_1000mt'] / 1000

# Indonesia and Malaysia production (MPOB priority for Malaysia)
mpob_idx = mpob.set_index('year')
shock_idx = shock.set_index('year')

years = list(range(2000, 2027))

id_mmt, my_mmt = [], []
for yr in years:
    row = shock_idx.loc[yr] if yr in shock_idx.index else None
    id_mmt.append(row['indonesia_production_1000mt'] / 1000 if row is not None and pd.notna(row.get('indonesia_production_1000mt')) else None)
    my_mmt.append(row['malaysia_production_1000mt'] / 1000 if row is not None and pd.notna(row.get('malaysia_production_1000mt')) else None)

df = pd.DataFrame({'year': years, 'id_mmt': id_mmt, 'my_mmt': my_mmt})
df = df.merge(palm_global[['year', 'global_mmt']], on='year', how='left')

x = df['year'].values

# ── Chart 1: Global CPO Production ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5.5))
fig.patch.set_facecolor(BG)

ymax = df['global_mmt'].max() * 1.12
shade_psd_only(ax, ymax)
shade_enso(ax, 0, ymax)

ax.plot(x, df['global_mmt'], color=BLUE, linewidth=2.5, marker='o',
        markersize=4, markerfacecolor=BG, markeredgecolor=BLUE, zorder=5)

# Fill under line
ax.fill_between(x, df['global_mmt'], alpha=0.08, color=BLUE)

# 2026 is forecast — dashed
mask_fore = df['year'] >= 2025
ax.plot(df.loc[mask_fore, 'year'], df.loc[mask_fore, 'global_mmt'],
        color=BLUE, linewidth=2.0, linestyle='--', zorder=6)

ax.set_ylim(0, ymax)
ax.set_xticks(x)
ax.set_xticklabels([str(y) for y in x], rotation=45, ha='right', fontsize=8)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}'))

style_ax(ax, 'Global CPO Production 2000–2026',
         'Million MT',
         'SOURCE: USDA PSD psd_oilseeds.csv — Commodity 4243000 (Palm Oil), Attribute 28 (Production), all countries. '
         '2026 = latest USDA forecast. El Niño bands: NOAA CPC. '
         '2000–2009: USDA PSD source only — no MPOB regional breakdown available for these years.')

plt.tight_layout(rect=[0, 0.04, 1, 1])
out1 = os.path.join(CHARTS, 'palm_world_production.png')
plt.savefig(out1, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Saved: {out1}')

# ── Chart 2: Indonesia vs Malaysia ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5.5))
fig.patch.set_facecolor(BG)

ymax2 = max(df['id_mmt'].max(), df['my_mmt'].max()) * 1.25
shade_psd_only(ax, ymax2)
shade_enso(ax, 0, ymax2)

# Indonesia
ax.plot(x, df['id_mmt'], color=BLUE, linewidth=2.5, marker='o',
        markersize=4, markerfacecolor=BG, markeredgecolor=BLUE, zorder=5, label='Indonesia')
ax.fill_between(x, df['id_mmt'], alpha=0.07, color=BLUE)

# Malaysia
ax.plot(x, df['my_mmt'], color=GREEN, linewidth=2.5, marker='s',
        markersize=4, markerfacecolor=BG, markeredgecolor=GREEN, zorder=5, label='Malaysia')
ax.fill_between(x, df['my_mmt'], alpha=0.07, color=GREEN)

# Dashed 2025-2026 for both
for col, clr in [('id_mmt', BLUE), ('my_mmt', GREEN)]:
    ax.plot(df.loc[mask_fore, 'year'], df.loc[mask_fore, col],
            color=clr, linewidth=2.0, linestyle='--', zorder=6)

# Annotation 2016
my_2016 = float(df.loc[df['year'] == 2016, 'my_mmt'].values[0])
id_2016 = float(df.loc[df['year'] == 2016, 'id_mmt'].values[0])
ax.annotate('MY −13.2%\nmasked by\nID +12.5%',
            xy=(2016, (my_2016 + id_2016) / 2),
            xytext=(2016.6, (my_2016 + id_2016) / 2 + 3.5),
            color=YELLOW, fontsize=7.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=YELLOW, lw=1.2),
            bbox=dict(boxstyle='round,pad=0.3', fc='#1f2937', ec=YELLOW, alpha=0.85))

# Annotation 2026
id_2026 = float(df.loc[df['year'] == 2026, 'id_mmt'].dropna().values[0]) if 2026 in df['year'].values else None
if id_2026:
    ax.annotate('⚠ BMKG drought\nwarning active',
                xy=(2026, id_2026),
                xytext=(2025.0, id_2026 + 4),
                color=ORANGE, fontsize=7.5, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3', fc='#1f2937', ec=ORANGE, alpha=0.85))

ax.set_ylim(0, ymax2)
ax.set_xticks(x)
ax.set_xticklabels([str(y) for y in x], rotation=45, ha='right', fontsize=8)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}'))

leg = ax.legend(loc='upper left', framealpha=0.2, facecolor=SURFACE,
                edgecolor=GRID, labelcolor=TEXT, fontsize=9)

style_ax(ax, 'Indonesia vs Malaysia CPO Production 2000–2026',
         'Million MT',
         'SOURCE: Indonesia — USDA PSD commodity 4243000. '
         'Malaysia — MPOB Annual Overview PDFs 2010–2025; USDA PSD otherwise. '
         '2026 = forecast. El Niño bands: NOAA CPC. '
         '2000–2009: USDA PSD source only — no MPOB regional breakdown available for these years.')

plt.tight_layout(rect=[0, 0.04, 1, 1])
out2 = os.path.join(CHARTS, 'palm_indonesia_malaysia.png')
plt.savefig(out2, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Saved: {out2}')

# ── Chart 3: Share of Global Supply ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5.5))
fig.patch.set_facecolor(BG)

df2 = df.dropna(subset=['global_mmt']).copy()
df2['id_share'] = df2['id_mmt'] / df2['global_mmt'] * 100
df2['my_share'] = df2['my_mmt'] / df2['global_mmt'] * 100
df2['row_share'] = 100 - df2['id_share'] - df2['my_share']
df2 = df2.sort_values('year')

x2 = df2['year'].values
ymax3 = 105
shade_psd_only(ax, ymax3)
shade_enso(ax, 0, ymax3)

ax.stackplot(x2,
             df2['row_share'], df2['my_share'], df2['id_share'],
             labels=['Rest of World', 'Malaysia', 'Indonesia'],
             colors=['#374151', GREEN, BLUE],
             alpha=0.85, zorder=3)

# Share labels at endpoints
def label_endpoint(yr, series, color, offset=0):
    val = float(df2.loc[df2['year'] == yr, series].values[0])
    ax.text(yr + 0.1, val / 2 if series == 'id_share' else None,
            f'{val:.0f}%', color=color, fontsize=7.5, va='center')

# Label 2000 and 2025 share values
for yr, side in [(2000, 'left'), (2025, 'right')]:
    row = df2[df2['year'] == yr]
    if len(row) == 0:
        continue
    ids = float(row['id_share'].values[0])
    mys = float(row['my_share'].values[0])
    rows_ = float(row['row_share'].values[0])
    xpos = yr + (0.3 if side == 'right' else -0.3)
    ha = 'left' if side == 'right' else 'right'
    ax.text(xpos, ids / 2,              f'{ids:.0f}%', color=TEXT, fontsize=7.5, ha=ha, va='center', fontweight='bold')
    ax.text(xpos, ids + mys / 2,        f'{mys:.0f}%', color=TEXT, fontsize=7.5, ha=ha, va='center', fontweight='bold')
    ax.text(xpos, ids + mys + rows_ / 2,f'{rows_:.0f}%', color=MUTED, fontsize=7.5, ha=ha, va='center')

ax.set_ylim(0, 101)
ax.set_xticks(x2)
ax.set_xticklabels([str(y) for y in x2], rotation=45, ha='right', fontsize=8)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:.0f}%'))

leg = ax.legend(loc='lower left', framealpha=0.25, facecolor=SURFACE,
                edgecolor=GRID, labelcolor=TEXT, fontsize=9, reverse=True)

style_ax(ax, 'Indonesia & Malaysia Share of Global CPO Supply 2000–2026',
         '% of global production',
         'SOURCE: Indonesia + Malaysia — USDA PSD + MPOB Annual Overviews. '
         'Global total — USDA PSD commodity 4243000 all countries. '
         'Rest of World = residual. 2026 = forecast. '
         '2000–2009: USDA PSD source only — no MPOB regional breakdown available for these years.')

plt.tight_layout(rect=[0, 0.04, 1, 1])
out3 = os.path.join(CHARTS, 'palm_share_of_world.png')
plt.savefig(out3, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Saved: {out3}')

print('\nAll 3 charts generated successfully.')
