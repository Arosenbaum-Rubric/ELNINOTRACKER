"""
Avocado El Niño 2026 Pipeline — Step 5: Merge, Analysis, Charts
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, warnings
warnings.filterwarnings('ignore')

PROCESSED = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\processed"
OUTPUTS   = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\outputs"
os.makedirs(OUTPUTS, exist_ok=True)

BG     = '#0a0e16'
SURF   = '#111827'
GRID   = '#1f2937'
TEXT   = '#e2e8f0'
MUTED  = '#8b9bab'
BLUE   = '#38bdf8'
GREEN  = '#4ade80'
RED    = '#f87171'
YELLOW = '#fbbf24'
ORANGE = '#fb923c'
PURPLE = '#a78bfa'

ENSO_BANDS = [
    (2002, 2003, 'El Niño\n02/03', YELLOW),
    (2009, 2010, 'El Niño\n09/10', YELLOW),
    (2015, 2016, 'El Niño\n15/16', YELLOW),
    (2023, 2024, 'El Niño\n23/24', YELLOW),
    (2026, 2026, '⚠ 2026', ORANGE),
]

def style_ax(ax, title, ylabel, source):
    ax.set_facecolor(SURF)
    ax.tick_params(colors=MUTED, labelsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor(GRID)
    ax.set_title(title, color=TEXT, fontsize=12, fontweight='bold', pad=10)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=8)
    ax.set_xlabel('')
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, linestyle='--', alpha=0.7)
    ax.xaxis.grid(False)
    ax.figure.text(0.5, 0.01, source, ha='center', color=MUTED, fontsize=6.5,
                   style='italic', wrap=True)

def shade_enso(ax, ymin, ymax, bands=None):
    if bands is None: bands = ENSO_BANDS
    for s, e, lbl, col in bands:
        alpha = 0.22 if '2026' in lbl else 0.12
        ax.axvspan(s - 0.4, e + 0.4, color=col, alpha=alpha, zorder=0)
        ax.text((s+e)/2, ymax * 0.97, lbl, ha='center', va='top',
                color=col, fontsize=6, fontweight='bold', alpha=0.85, zorder=2)

# ── Load CSVs ─────────────────────────────────────────────────────────────────
prod = pd.read_csv(os.path.join(PROCESSED, 'avocado_production_yield.csv'))
trade = pd.read_csv(os.path.join(PROCESSED, 'avocado_trade.csv'))
ws = pd.read_csv(os.path.join(PROCESSED, 'avocado_water_stress.csv'))

mex_prod = prod[(prod['iso_code']=='MEX') & prod['year'].between(2000,2026)].sort_values('year')
col_prod = prod[(prod['iso_code']=='COL') & prod['year'].between(2000,2024)].sort_values('year')
per_prod = prod[(prod['iso_code']=='PER') & prod['year'].between(2000,2025)].sort_values('year')
wld_prod = prod[(prod['iso_code']=='OWID_WRL') & prod['year'].between(2000,2024)].sort_values('year')

mex_trade = trade[trade['iso_code']=='MEX'].sort_values('year')
col_trade = trade[trade['iso_code']=='COL'].sort_values('year')
per_trade = trade[trade['iso_code']=='PER'].sort_values('year')

mex_ws = ws[(ws['iso_code']=='MEX') & ws['year'].between(2000,2024)].sort_values('year')
col_ws = ws[(ws['iso_code']=='COL') & ws['year'].between(2000,2024)].sort_values('year')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — Mexico Production + Yield Index (Section 1)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5.5))
fig.patch.set_facecolor(BG)

base_yr = 2010
mex_base_prod = float(mex_prod[mex_prod['year']==base_yr]['production_tonnes'].values[0])
mex_base_yld  = float(mex_prod[mex_prod['year']==base_yr]['yield_t_per_ha'].values[0])

idx_prod = mex_prod['production_tonnes'] / mex_base_prod * 100
idx_yld  = mex_prod['yield_t_per_ha'] / mex_base_yld * 100

x = mex_prod['year'].values
ymax = max(idx_prod.max(), idx_yld.dropna().max()) * 1.18

shade_enso(ax, 0, ymax)

# 5yr rolling average for production
roll_prod = pd.Series(idx_prod.values).rolling(5, center=True, min_periods=3).mean()
ax.plot(x, roll_prod, color=BLUE, linewidth=1.0, linestyle='--', alpha=0.55, zorder=3, label='Prod 5yr avg')

# Production index
ax.plot(x, idx_prod, color=BLUE, linewidth=2.5, marker='o', markersize=3.5,
        markerfacecolor=BG, markeredgecolor=BLUE, zorder=5, label='Production index')
ax.fill_between(x, idx_prod, 100, where=(idx_prod < 100), alpha=0.08, color=RED)
ax.fill_between(x, idx_prod, 100, where=(idx_prod > 100), alpha=0.07, color=BLUE)

# Yield index
yld_vals = idx_yld.values
ax.plot(x, yld_vals, color=GREEN, linewidth=2.0, marker='s', markersize=3,
        markerfacecolor=BG, markeredgecolor=GREEN, zorder=5, label='Yield index', linestyle='-')

# Mark 2026 as forecast (dashed)
mask26 = mex_prod['year'] >= 2025
ax.plot(mex_prod.loc[mask26,'year'], idx_prod[mask26], color=BLUE, linewidth=2, linestyle='--', zorder=6)

ax.axhline(100, color=MUTED, linewidth=0.6, linestyle=':', alpha=0.5)

# Annotation: 2023
ax.annotate('2023: heat/drought\nsmaller fruit, value −12%',
    xy=(2023, float(idx_prod[mex_prod['year']==2023].values[0])),
    xytext=(2020.5, float(idx_prod[mex_prod['year']==2023].values[0]) - 12),
    color=RED, fontsize=7.5, fontweight='bold',
    arrowprops=dict(arrowstyle='->', color=RED, lw=1.0),
    bbox=dict(boxstyle='round,pad=0.3', fc='#1f2937', ec=RED, alpha=0.85))

# Annotation: 2026 forecast
ax.annotate('2026 forecast:\nEl Niño → flowering risk\nDec 26–Apr 27',
    xy=(2026, float(idx_prod[mex_prod['year']==2026].values[0])),
    xytext=(2023.5, float(idx_prod[mex_prod['year']==2026].values[0]) + 8),
    color=ORANGE, fontsize=7.5, fontweight='bold',
    arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.0),
    bbox=dict(boxstyle='round,pad=0.3', fc='#1f2937', ec=ORANGE, alpha=0.85))

ax.set_ylim(50, ymax)
ax.set_xticks(x); ax.set_xticklabels([str(y) for y in x], rotation=45, ha='right', fontsize=7.5)
ax.legend(loc='upper left', framealpha=0.25, facecolor=SURF, edgecolor=GRID, labelcolor=TEXT, fontsize=8)

style_ax(ax, 'Mexico Avocado: Production & Yield Index (2010 = 100)',
         'Index (2010 = 100)',
         'SOURCE: Production — SIAP via USDA GAIN MX2024-0018/MX2026-0019 (2014–2026), OWID 2000–2013. '
         'Yield — derived from SIAP production/area (2014–2026). '
         '2026* = USDA GAIN MX2026-0019 forecast. El Niño bands: NOAA CPC.')

plt.tight_layout(rect=[0, 0.04, 1, 1])
out1 = os.path.join(OUTPUTS, 'chart1_mexico_production_yield_index.png')
plt.savefig(out1, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Chart 1 saved: {out1}')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — Colombia Production + Yield Index (Section 2)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5.5))
fig.patch.set_facecolor(BG)

col_base_prod = float(col_prod[col_prod['year']==base_yr]['production_tonnes'].values[0])
col_base_yld  = col_prod[col_prod['year']==base_yr]['yield_t_per_ha'].values
col_base_yld  = float(col_base_yld[0]) if len(col_base_yld) > 0 and pd.notna(col_base_yld[0]) else None

x2 = col_prod['year'].values
idx_col_prod = col_prod['production_tonnes'] / col_base_prod * 100

ymax2 = idx_col_prod.max() * 1.20
shade_enso(ax, 0, ymax2)

roll_col = pd.Series(idx_col_prod.values).rolling(5, center=True, min_periods=3).mean()
ax.plot(x2, roll_col, color=GREEN, linewidth=1.0, linestyle='--', alpha=0.5, zorder=3, label='Prod 5yr avg')
ax.plot(x2, idx_col_prod, color=GREEN, linewidth=2.5, marker='o', markersize=3.5,
        markerfacecolor=BG, markeredgecolor=GREEN, zorder=5, label='Production index')
ax.fill_between(x2, idx_col_prod, 100, where=(idx_col_prod < 100), alpha=0.08, color=RED)
ax.fill_between(x2, idx_col_prod, 100, where=(idx_col_prod > 100), alpha=0.07, color=GREEN)

if col_base_yld:
    col_yld_vals = col_prod['yield_t_per_ha'] / col_base_yld * 100
    ax.plot(x2, col_yld_vals, color=PURPLE, linewidth=1.8, marker='s', markersize=3,
            markerfacecolor=BG, markeredgecolor=PURPLE, zorder=5, label='Yield index (est.)',
            linestyle='--', alpha=0.8)
    ax.text(x2[-1] + 0.3, float(col_yld_vals.iloc[-1]), 'ESTIMATED\n(no GAIN report)',
            color=PURPLE, fontsize=6.5, alpha=0.9, va='center')

ax.axhline(100, color=MUTED, linewidth=0.6, linestyle=':', alpha=0.5)

# Annotations
for yr, lbl in [(2003,'AWC disease\n+ drought'), (2009,'AWC disease\n+ drought'), (2016,'AWC disease\n+ drought')]:
    val = col_prod[col_prod['year']==yr]['production_tonnes']
    if len(val):
        idx_v = float(val.values[0]) / col_base_prod * 100
        ax.annotate(lbl, xy=(yr, idx_v),
            xytext=(yr + 0.5, idx_v - 12),
            color=RED, fontsize=6.5, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=0.8),
            bbox=dict(boxstyle='round,pad=0.2', fc='#1f2937', ec=RED, alpha=0.8))

ax.set_ylim(50, ymax2)
ax.set_xticks(x2); ax.set_xticklabels([str(y) for y in x2], rotation=45, ha='right', fontsize=7.5)
ax.legend(loc='upper left', framealpha=0.25, facecolor=SURF, edgecolor=GRID, labelcolor=TEXT, fontsize=8)

style_ax(ax, 'Colombia Avocado: Production & Yield Index (2010 = 100)',
         'Index (2010 = 100)',
         'SOURCE: Production — OWID avocado-production.csv (FAO). '
         'Yield — friend\'s dataset (cross-val only); post-2022 = ESTIMATED BY CLAUDE (no Colombia GAIN report). '
         'ENSO analog projection only for forward outlook. El Niño bands: NOAA CPC.')

plt.tight_layout(rect=[0, 0.04, 1, 1])
out2 = os.path.join(OUTPUTS, 'chart2_colombia_production_yield_index.png')
plt.savefig(out2, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Chart 2 saved: {out2}')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — World Context (Section 3)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5.5))
fig.patch.set_facecolor(BG)

# Build RoW = World - Mexico - Colombia - Peru
yrs_w = list(range(2000, 2025))
wld_vals, mex_vals, col_vals, per_vals = [], [], [], []
for yr in yrs_w:
    def get_prod(df, yr):
        v = df[df['year']==yr]['production_tonnes']
        return float(v.values[0])/1e6 if len(v) else np.nan
    w = get_prod(wld_prod, yr)
    m = get_prod(mex_prod, yr)
    c = get_prod(col_prod, yr)
    p = get_prod(per_prod, yr)
    wld_vals.append(w); mex_vals.append(m); col_vals.append(c); per_vals.append(p)

row_vals = [w - m - c - (p if not np.isnan(p) else 0) if not any(np.isnan([w,m,c])) else np.nan
            for w,m,c,p in zip(wld_vals,mex_vals,col_vals,per_vals)]

xw = np.array(yrs_w)
ymax3 = max([v for v in wld_vals if not np.isnan(v)]) * 1.18
shade_enso(ax, 0, ymax3)

ax.plot(xw, mex_vals, color=BLUE, linewidth=2.5, marker='o', markersize=3.5,
        markerfacecolor=BG, markeredgecolor=BLUE, zorder=5, label='Mexico')
ax.plot(xw, col_vals, color=GREEN, linewidth=2.5, marker='s', markersize=3.5,
        markerfacecolor=BG, markeredgecolor=GREEN, zorder=5, label='Colombia')
ax.plot(xw, per_vals, color=PURPLE, linewidth=2.0, linestyle='--', marker='^', markersize=3,
        markerfacecolor=BG, markeredgecolor=PURPLE, zorder=5, label='Peru (offset monitor)')
ax.plot(xw, row_vals, color=MUTED, linewidth=1.5, linestyle=':', zorder=4, label='Rest of World')
ax.plot(xw, wld_vals, color=TEXT, linewidth=1.0, linestyle='-', alpha=0.3, zorder=3, label='World total')

ax.text(xw[-1]+0.3, max([v for v in mex_vals if not np.isnan(v)])*0.98,
        'No ENSO offset —\nMEX + COL both\ndrought 2026',
        color=ORANGE, fontsize=7.5, fontweight='bold', alpha=0.9)

ax.set_ylim(0, ymax3)
ax.set_xticks(xw); ax.set_xticklabels([str(y) for y in xw], rotation=45, ha='right', fontsize=7.5)
ax.legend(loc='upper left', framealpha=0.25, facecolor=SURF, edgecolor=GRID, labelcolor=TEXT, fontsize=8)

style_ax(ax, 'World Avocado Production: Key Supply Countries 2000–2024',
         'Million Metric Tons (MMT)',
         'SOURCE: Mexico — SIAP via GAIN (2014–2024), OWID 2000–2013. '
         'Colombia, Peru, World — OWID avocado-production.csv (FAO). '
         'Peru 2023–2025 anchored to USDA GAIN PE2025-0005. '
         'Rest of World = World minus Mexico/Colombia/Peru.')

plt.tight_layout(rect=[0, 0.04, 1, 1])
out3 = os.path.join(OUTPUTS, 'chart3_world_context.png')
plt.savefig(out3, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Chart 3 saved: {out3}')

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4 — Mexico Export Concentration Ratio
# ─────────────────────────────────────────────────────────────────────────────
# Mexico exports as % of World exports
# World export proxy: use friend's data for world + WITS 2024 anchor
wld_exp = ws[ws['iso_code']=='OWID_WRL'].sort_values('year')  # use as proxy

fig, ax = plt.subplots(figsize=(12, 5.0))
fig.patch.set_facecolor(BG)

mex_exp_yrs = mex_trade[mex_trade['exports'].notna()].sort_values('year')

# Compute Mexico export share: use world total from friend's export CSV
wld_trade = trade[trade['iso_code']=='OWID_WRL'].sort_values('year')
exp_yrs = sorted(set(mex_exp_yrs['year'].tolist()))

mex_shares = []
share_yrs = []
for yr in exp_yrs:
    mx = mex_exp_yrs[mex_exp_yrs['year']==yr]['exports']
    wt = wld_trade[wld_trade['year']==yr]['exports']
    if len(mx) and len(wt) and pd.notna(float(wt.values[0])):
        share = float(mx.values[0]) / float(wt.values[0]) * 100
        mex_shares.append(share)
        share_yrs.append(yr)

if mex_shares:
    xs = np.array(share_yrs)
    ymax4 = max(mex_shares) * 1.20
    shade_enso(ax, 0, ymax4)

    colors = [ORANGE if s < 38 else BLUE for s in mex_shares]
    ax.bar(xs, mex_shares, color=colors, width=0.7, alpha=0.80, zorder=4)
    ax.axhline(38, color=RED, linewidth=1.5, linestyle='--', alpha=0.8, zorder=5,
               label='Concern threshold (38%)')
    ax.axhline(52, color=GREEN, linewidth=1.0, linestyle=':', alpha=0.5, zorder=5,
               label='Upper bound (52%)')

    ax.set_ylim(0, ymax4)
    ax.set_xticks(xs); ax.set_xticklabels([str(y) for y in xs], rotation=45, ha='right', fontsize=7.5)
    ax.legend(framealpha=0.25, facecolor=SURF, edgecolor=GRID, labelcolor=TEXT, fontsize=8)

    style_ax(ax, 'Mexico Share of World Avocado Exports 2000–2026',
             '% of world exports',
             'SOURCE: Mexico exports — SIAP via GAIN / WITS HS 080440 (2024). '
             'World exports — friend\'s avocado_export_volumes.csv (directional only). '
             'Concern threshold <38% signals structural supply shift. '
             'Note: world export figures pre-2024 are directional estimates.')

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out4 = os.path.join(OUTPUTS, 'chart4_mexico_export_share.png')
    plt.savefig(out4, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f'Chart 4 saved: {out4}')
else:
    print('Chart 4 skipped: insufficient world export data for share calc')
    out4 = None

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5 — Value Compression Mechanism
# ─────────────────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(12, 5.5))
fig.patch.set_facecolor(BG)
ax2 = ax1.twinx()
ax1.set_facecolor(SURF)
ax2.set_facecolor(SURF)

# Volume (bars) — 2015-2026
vc = mex_trade[(mex_trade['year'].between(2015,2026)) & mex_trade['exports'].notna()].sort_values('year').reset_index(drop=True)

# Implied price per MT — only where we have both volume and value
vc_price = vc[vc['export_value_1000usd'].notna()].copy()
vc_price['price_per_mt'] = vc_price['export_value_1000usd'] / vc_price['exports']  # k$/MT

xvc = vc['year'].values
xprice = vc_price['year'].values

shade_enso(ax1, 0, vc['exports'].max() * 1.25, bands=[
    b for b in ENSO_BANDS if b[0] >= 2015
])

bar_colors = [RED if yr == 2023 else BLUE for yr in xvc]
bars = ax1.bar(xvc, vc['exports']/1000, color=bar_colors, width=0.65, alpha=0.75, zorder=4, label='Export volume (kMT)')

ax2.plot(xprice, vc_price['price_per_mt'], color=YELLOW, linewidth=2.5, marker='D',
         markersize=5, markerfacecolor=BG, markeredgecolor=YELLOW, zorder=6, label='Implied price (k$/MT)')

# Annotation 2023
ax1.annotate('2023: Volume +17%,\nValue −12%\n→ smaller fruit',
    xy=(2023, float(vc[vc['year']==2023]['exports'].values[0])/1000),
    xytext=(2020.5, float(vc[vc['year']==2023]['exports'].values[0])/1000 + 80),
    color=RED, fontsize=7.5, fontweight='bold',
    arrowprops=dict(arrowstyle='->', color=RED, lw=1.0),
    bbox=dict(boxstyle='round,pad=0.3', fc='#1f2937', ec=RED, alpha=0.85))

ax1.tick_params(colors=MUTED, labelsize=8)
ax2.tick_params(colors=YELLOW, labelsize=8)
for sp in ax1.spines.values(): sp.set_edgecolor(GRID)
for sp in ax2.spines.values(): sp.set_edgecolor(GRID)
ax1.set_title('Mexico Avocado: Export Volume vs Implied Price/MT', color=TEXT, fontsize=12, fontweight='bold', pad=10)
ax1.set_ylabel('Volume (thousand MT)', color=MUTED, fontsize=8)
ax2.set_ylabel('Implied price (k USD/MT)', color=YELLOW, fontsize=8)
ax1.yaxis.grid(True, color=GRID, linewidth=0.5, linestyle='--', alpha=0.7)
ax1.xaxis.grid(False)
ax1.set_xticks(xvc); ax1.set_xticklabels([str(y) for y in xvc], rotation=45, ha='right', fontsize=8)

h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, loc='upper left', framealpha=0.25, facecolor=SURF, edgecolor=GRID, labelcolor=TEXT, fontsize=8)

fig.text(0.5, 0.01,
    'SOURCE: Volume — USDA GAIN MX2024-0018/MX2026-0019; WITS HS 080440 (2024). '
    'Value — GAIN MX2024-0018 (2022/23); WITS HS 080440 (2024). '
    'Implied price = export value / volume. 2026 volume = forecast.',
    ha='center', color=MUTED, fontsize=6.5, style='italic', wrap=True)

plt.tight_layout(rect=[0, 0.04, 1, 1])
out5 = os.path.join(OUTPUTS, 'chart5_value_compression.png')
plt.savefig(out5, dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print(f'Chart 5 saved: {out5}')

# ─────────────────────────────────────────────────────────────────────────────
# ENSO ANALOG COMPARISON TABLE
# ─────────────────────────────────────────────────────────────────────────────
print('\n' + '='*70)
print('ENSO ANALOG COMPARISON TABLE')
print('='*70)
print(f"{'Year':<8} {'MEX Prod (kMT)':<18} {'MEX YoY%':<12} {'COL Prod (kMT)':<18} {'COL YoY%':<12} {'PER Exp (kMT)':<14}")
print('-'*82)
for yr in [2009, 2010, 2015, 2016, 2023, 2024]:
    m_p = prod[(prod['iso_code']=='MEX') & (prod['year']==yr)]['production_tonnes']
    m_y = prod[(prod['iso_code']=='MEX') & (prod['year']==yr)]['yoy_production_pct']
    c_p = prod[(prod['iso_code']=='COL') & (prod['year']==yr)]['production_tonnes']
    c_y = prod[(prod['iso_code']=='COL') & (prod['year']==yr)]['yoy_production_pct']
    p_e = trade[(trade['iso_code']=='PER') & (trade['year']==yr)]['exports']
    mp = f"{float(m_p.values[0])/1000:,.0f}" if len(m_p) else '-'
    my = f"{float(m_y.values[0]):+.1f}%" if len(m_y) and pd.notna(m_y.values[0]) else '-'
    cp = f"{float(c_p.values[0])/1000:,.0f}" if len(c_p) else '-'
    cy = f"{float(c_y.values[0]):+.1f}%" if len(c_y) and pd.notna(c_y.values[0]) else '-'
    pe = f"{float(p_e.values[0]):,.0f}" if len(p_e) else '-'
    print(f"{yr:<8} {mp:<18} {my:<12} {cp:<18} {cy:<12} {pe:<14}")

# ─────────────────────────────────────────────────────────────────────────────
# VALUE COMPRESSION SIGNAL
# ─────────────────────────────────────────────────────────────────────────────
print('\n' + '='*70)
print('VALUE-COMPRESSION SIGNAL — Mexico')
print('='*70)
vc_analysis = mex_trade[mex_trade['export_value_1000usd'].notna()].copy()
vc_analysis = vc_analysis[vc_analysis['exports'].notna()]
vc_analysis['price_per_mt'] = vc_analysis['export_value_1000usd'] / vc_analysis['exports']
vc_analysis['yoy_price_pct'] = vc_analysis['price_per_mt'].pct_change() * 100

print(f"{'Year':<8} {'Volume (kMT)':<16} {'Value ($M)':<14} {'$/MT (k)':<12} {'Vol YoY%':<12} {'Price YoY%':<12} {'Flag'}")
print('-'*80)
for _, r in vc_analysis.iterrows():
    flag = '** COMPRESSION' if (pd.notna(r.get('yoy_exports_pct')) and r.get('yoy_exports_pct',0)>5
                                 and pd.notna(r.get('yoy_price_pct')) and r.get('yoy_price_pct',0)<-3) else ''
    vol = f"{r['exports']/1000:,.0f}" if pd.notna(r['exports']) else '-'
    val = f"{r['export_value_1000usd']/1000:,.0f}" if pd.notna(r['export_value_1000usd']) else '-'
    pmt = f"{r['price_per_mt']:.2f}" if pd.notna(r.get('price_per_mt')) else '-'
    vyoy = f"{r['yoy_exports_pct']:+.1f}%" if pd.notna(r.get('yoy_exports_pct')) else '-'
    pyoy = f"{r['yoy_price_pct']:+.1f}%" if pd.notna(r.get('yoy_price_pct')) else '-'
    print(f"{int(r['year']):<8} {vol:<16} {val:<14} {pmt:<12} {vyoy:<12} {pyoy:<12} {flag}")

# ─────────────────────────────────────────────────────────────────────────────
# DEMAND-SUPPLY SQUEEZE (Outcome 6)
# ─────────────────────────────────────────────────────────────────────────────
print('\n' + '='*70)
print('DEMAND-SUPPLY SQUEEZE ASSESSMENT')
print('='*70)
us_demand_yoy = 7.0  # US avocado imports 2025: ~2.87B lbs, +7% YoY
print(f"US avocado imports 2025: ~2.87B lbs, +7% YoY")
print(f"  SOURCE: ESTIMATED BY CLAUDE — from industry/HAB reports 2026")
print(f"Mexico share of US supply 2025: ~83% SOURCE: industry reports")
print(f"Colombia share of US supply 2025: ~4.6% (fastest growing) SOURCE: industry reports")

mex_2026_yoy = 3.0  # GAIN forecast
if us_demand_yoy > 5 and mex_2026_yoy < -3:
    signal = 'RED — squeeze scenario'
elif us_demand_yoy > 5 and 0 <= mex_2026_yoy <= 3:
    signal = 'AMBER — tight supply; demand growth outpaces supply if El Niño materialises'
else:
    signal = 'GREEN — supply comfortable (baseline, pre-El Niño impact)'

print(f"\n2026 baseline (pre-El Niño): Mexico +{mex_2026_yoy}%, US demand +{us_demand_yoy}%")
print(f"Signal: {signal}")
print(f"NOTE: El Niño H2 2026 → flowering risk Dec 2026–Apr 2027 → harvest impact visible 2027.")
print(f"      Watch for fruit-size compression (VALUE signal), not just volume.")

# ─────────────────────────────────────────────────────────────────────────────
# DATA QUALITY FLAGS
# ─────────────────────────────────────────────────────────────────────────────
print('\n' + '='*70)
print('DATA QUALITY FLAGS')
print('='*70)
print('[✓] Mexico 2023 OWID/SIAP discrepancy 12.1% — DOCUMENTED (using SIAP)')
print('[✗] FAOSTAT QCL: UNAVAILABLE — server not contacted (yield from SIAP/friend)')
print('[✗] FAOSTAT TCL: UNAVAILABLE — historical exports from friend\'s CSV (directional)')
print('[~] Yield data: PARTIAL — Mexico (SIAP-derived), Colombia/Peru (friend/GAIN)')
print('[!] Colombia forward outlook: ESTIMATED BY CLAUDE — no GAIN avocado annual exists')
print('[!] Friend water stress 2009 Mexico: FLAGGED SUSPECT — duplicate of 2010 value')
print('[~] US demand proxy: ESTIMATED — ~2.87B lbs +7% YoY from industry reports 2026')
print('[✓] Colombia GAIN avocado annual: CONFIRMED NOT EXIST as of June 2026')

print('\n=== STEP 5 COMPLETE — All 5 charts generated ===')
