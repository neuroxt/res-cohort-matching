#!/usr/bin/env python3
"""
A4/LEARN 데이터 가용성 히트맵 — compact single-axis design

Usage:
    python scripts/a4_availability_figure.py
    python scripts/a4_availability_figure.py --merged-csv /path/to/MERGED.csv
"""

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ──────────────────────────────────────────────────────────────
# VISCODE 정의: 주요 클리닉 방문만 표시 (infusion 제외)
# ──────────────────────────────────────────────────────────────

# A4: screening(1-5) + clinic visits every 12 wks + OLE groups + termination
A4_VISCODES = [1, 2, 4, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42,
               45, 48, 51, 54, 57, 60, 63, 66]
A4_OLE_RANGES = [
    ('OLE-1y', range(67, 79)),   # wk244-288
    ('OLE-2y', range(79, 97)),   # wk292-364
    ('OLE-3y', range(97, 118)),  # wk364-448
]
A4_TERM = [701, 702, 997, 998, 999]

# LEARN: screening(1-3) + every 24 wks + termination
LEARN_VISCODES = [1, 2, 3, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66,
                  72, 78, 84, 90, 96, 102]
LEARN_TERM = [999]

# pTau217 수집 VISCODE (BID-level이므로 이 시점에서만 카운트)
PTAU217_VISCODES_A4 = {6, 9, 66, 997, 999}
PTAU217_VISCODES_LEARN = {1, 24, 66, 999}

# VMRI/TAU baseline VISCODE
VMRI_VISCODE_A4 = 4
VMRI_VISCODE_LEARN = 6
TAU_VISCODE_A4 = 4
TAU_VISCODE_LEARN = 6

# 데이터 타입 정의 (Y축 순서)
DATA_TYPES = [
    # (label, category)
    ('T1', 'MRI'),
    ('FLAIR', 'MRI'),
    ('T2_SE', 'MRI'),
    ('T2_STAR', 'MRI'),
    ('FMRI_REST', 'MRI'),
    ('B0CD', 'MRI'),
    ('FBP', 'PET'),
    ('FTP', 'PET'),
    ('MMSE', 'Cognitive'),
    ('CDR', 'Cognitive'),
    ('pTau217', 'Biomarker'),
    ('Roche Plasma', 'Biomarker'),
    ('VMRI', 'Derived'),
    ('TAU_SUVR', 'Derived'),
    ('Centiloid', 'Derived'),
]

# Phase 색상 (X축 상단 브래킷)
PHASE_COLORS = {
    'Screening': '#4CAF50',
    'Treatment': '#2196F3',
    'OLE': '#FF9800',
    'ET': '#F44336',
}


def viscode_label(v):
    """VISCODE → X축 라벨."""
    if v == 1:
        return 'SCV1'
    elif v == 2:
        return 'SCV2'
    elif v == 3:
        return 'SCV3'
    elif v == 4:
        return 'SCV4'
    elif v == 5:
        return 'SCV5'
    elif v == 6:
        return 'BL'
    elif 7 <= v <= 117:
        wk = (v - 6) * 4
        return f'Wk{wk}'
    elif v == 997:
        return 'OLE-T'
    elif v == 998:
        return 'UNS'
    elif 701 <= v <= 705:
        return f'UNS-{v - 700}'
    elif v == 999:
        return 'ET'
    else:
        return str(v)


def viscode_phase(v):
    """VISCODE → Phase."""
    if v <= 5:
        return 'Screening'
    elif v <= 66:
        return 'Treatment'
    elif v <= 117:
        return 'OLE'
    elif v in (997, 998, 999) or 701 <= v <= 705:
        return 'ET'
    else:
        return 'Other'


def build_viscode_columns(cohort_name, detailed=False):
    """X축 컬럼 정의를 반환: [(label, viscode_or_range), ...]

    detailed=True (A4 only): OLE 구간을 개별 VISCODE로 펼침.
    """
    cols = []
    if cohort_name == 'A4':
        # Screening + Treatment clinic visits (compact/detailed 공통)
        for v in A4_VISCODES:
            cols.append((viscode_label(v), [v]))
        if detailed:
            # OLE: 개별 VISCODE V67-V117
            for v in range(67, 118):
                cols.append((viscode_label(v), [v]))
        else:
            # OLE: 묶음
            for label, vrange in A4_OLE_RANGES:
                cols.append((label, list(vrange)))
        # TERM / Special (compact/detailed 공통)
        for v in A4_TERM:
            cols.append((viscode_label(v), [v]))
    else:  # LEARN
        for v in LEARN_VISCODES:
            cols.append((viscode_label(v), [v]))
        for v in LEARN_TERM:
            cols.append((viscode_label(v), [v]))
    return cols


def count_availability(cohort_df, session_codes, dtype_name, cohort_name):
    """특정 세션 코드 범위에서 데이터 타입의 unique BID 수 반환."""
    sub = cohort_df[cohort_df['SESSION_CODE'].isin(session_codes)]
    if sub.empty:
        return 0

    # Imaging modalities: NII_PATH 존재
    if dtype_name in ('T1', 'FLAIR', 'T2_SE', 'T2_STAR', 'FMRI_REST', 'B0CD', 'FBP', 'FTP'):
        col = f'{dtype_name}_NII_PATH'
        if col not in sub.columns:
            return 0
        return sub.loc[sub[col].notna(), 'BID'].nunique()

    # MMSE (longitudinal, session-level)
    if dtype_name == 'MMSE':
        if 'MMSE' not in sub.columns:
            return 0
        return sub.loc[sub['MMSE'].notna(), 'BID'].nunique()

    # CDR (longitudinal, session-level)
    if dtype_name == 'CDR':
        if 'CDGLOBAL' not in sub.columns:
            return 0
        return sub.loc[sub['CDGLOBAL'].notna(), 'BID'].nunique()

    # pTau217 (BID-level, 수집 VISCODE에서만)
    if dtype_name == 'pTau217':
        expected = PTAU217_VISCODES_A4 if cohort_name == 'A4' else PTAU217_VISCODES_LEARN
        relevant = set(session_codes) & expected
        if not relevant:
            return 0
        sub2 = cohort_df[cohort_df['SESSION_CODE'].isin(relevant)]
        ptau_cols = [c for c in sub2.columns if c.startswith('PTAU217_') and not c.endswith('_LLOQ')]
        if not ptau_cols:
            return 0
        mask = sub2[ptau_cols].notna().any(axis=1)
        return sub2.loc[mask, 'BID'].nunique()

    # Roche Plasma (BID-level, screening VISCODE=1에서만)
    if dtype_name == 'Roche Plasma':
        roche_viscode = 1  # screening only
        if roche_viscode not in session_codes:
            return 0
        sub2 = cohort_df[cohort_df['SESSION_CODE'] == roche_viscode]
        roche_cols = [c for c in sub2.columns
                      if c.startswith('ROCHE_') and not c.endswith('_BLQ_bl')]
        if not roche_cols:
            return 0
        mask = sub2[roche_cols].notna().any(axis=1)
        return sub2.loc[mask, 'BID'].nunique()

    # VMRI (BID-level, baseline VISCODE에서만)
    if dtype_name == 'VMRI':
        bl_v = VMRI_VISCODE_A4 if cohort_name == 'A4' else VMRI_VISCODE_LEARN
        if bl_v not in session_codes:
            return 0
        sub2 = cohort_df[cohort_df['SESSION_CODE'] == bl_v]
        vmri_cols = [c for c in sub2.columns if c.startswith('VMRI_')]
        if not vmri_cols:
            return 0
        mask = sub2[vmri_cols[:3]].notna().any(axis=1)  # check first 3 for speed
        return sub2.loc[mask, 'BID'].nunique()

    # TAU_SUVR (BID-level, baseline VISCODE에서만)
    if dtype_name == 'TAU_SUVR':
        bl_v = TAU_VISCODE_A4 if cohort_name == 'A4' else TAU_VISCODE_LEARN
        if bl_v not in session_codes:
            return 0
        sub2 = cohort_df[cohort_df['SESSION_CODE'] == bl_v]
        tau_cols = [c for c in sub2.columns if c.startswith('TAU_')]
        if not tau_cols:
            return 0
        mask = sub2[tau_cols[:3]].notna().any(axis=1)
        return sub2.loc[mask, 'BID'].nunique()

    # Centiloid (BID-level, baseline VISCODE에서만)
    if dtype_name == 'Centiloid':
        bl_v = 4 if cohort_name == 'A4' else 6  # PET baseline VISCODE
        if bl_v not in session_codes:
            return 0
        sub2 = cohort_df[cohort_df['SESSION_CODE'] == bl_v]
        if 'AMY_CENTILOID_bl' not in sub2.columns:
            return 0
        return sub2.loc[sub2['AMY_CENTILOID_bl'].notna(), 'BID'].nunique()

    return 0


def build_matrix(cohort_df, cohort_name, detailed=False):
    """코호트의 (데이터타입 × VISCODE) 가용성 매트릭스 빌드."""
    viscode_cols = build_viscode_columns(cohort_name, detailed=detailed)
    total_bids = cohort_df['BID'].nunique()

    labels = [vc[0] for vc in viscode_cols]
    dtype_labels = [dt[0] for dt in DATA_TYPES]

    count_matrix = np.zeros((len(DATA_TYPES), len(viscode_cols)), dtype=int)
    pct_matrix = np.zeros((len(DATA_TYPES), len(viscode_cols)), dtype=float)

    for j, (label, session_codes) in enumerate(viscode_cols):
        for i, (dtype_name, _cat) in enumerate(DATA_TYPES):
            n = count_availability(cohort_df, session_codes, dtype_name, cohort_name)
            count_matrix[i, j] = n
            pct_matrix[i, j] = (n / total_bids * 100) if total_bids > 0 else 0

    count_df = pd.DataFrame(count_matrix, index=dtype_labels, columns=labels)
    pct_df = pd.DataFrame(pct_matrix, index=dtype_labels, columns=labels)
    return count_df, pct_df, viscode_cols


def _prune_empty_columns(count_df, pct_df, viscode_cols):
    """모든 데이터 타입에서 count=0인 VISCODE 컬럼 제거."""
    keep_mask = (count_df.sum(axis=0) > 0).values
    kept_labels = [count_df.columns[i] for i, k in enumerate(keep_mask) if k]
    kept_viscodes = [viscode_cols[i] for i, k in enumerate(keep_mask) if k]
    return count_df[kept_labels], pct_df[kept_labels], kept_viscodes


def _format_count(c):
    """카운트를 정확한 숫자로 포맷: 0→''."""
    if c == 0:
        return ''
    return str(c)


def _make_annot(count_df):
    """셀 어노테이션: count만 표시 (간결)."""
    annot = np.empty(count_df.shape, dtype=object)
    for i in range(count_df.shape[0]):
        for j in range(count_df.shape[1]):
            annot[i, j] = _format_count(count_df.iloc[i, j])
    return annot


def plot_heatmap(count_df, pct_df, viscode_cols, cohort_name, total_bids,
                 output_path, dpi=300, detailed=False):
    """Compact single-axis 히트맵 생성 + 저장."""
    ncols = len(count_df.columns)
    nrows = len(count_df.index)

    # ── Figure sizing ──
    if detailed:
        fig_w = max(14, ncols * 0.55 + 4)
    else:
        fig_w = max(14, ncols * 0.75 + 4)
    fig_h = max(7, nrows * 0.65 + 3)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), facecolor='white')

    annot = _make_annot(count_df)

    # ── Font sizes: detailed에서 축소 ──
    annot_fontsize = 5.5 if detailed else 7
    xtick_fontsize = 6 if detailed else 8

    # ── YlOrRd colormap, 0% = 회색 ──
    cmap = plt.cm.YlOrRd.copy()
    cmap.set_under('#F0F0F0')

    sns.heatmap(
        pct_df, ax=ax, annot=annot, fmt='',
        cmap=cmap, vmin=0.5, vmax=100,
        linewidths=0.5, linecolor='white',
        cbar_kws={'label': '% of cohort', 'shrink': 0.6},
        annot_kws={'fontsize': annot_fontsize, 'fontweight': 'bold'},
    )

    # ── Per-cell text color ──
    for idx, txt in enumerate(ax.texts):
        row = idx // ncols
        col = idx % ncols
        if row < pct_df.shape[0] and col < pct_df.shape[1]:
            p = pct_df.iloc[row, col]
            if p == 0:
                txt.set_color('#BDBDBD')
            elif p > 60:
                txt.set_color('white')
            else:
                txt.set_color('#212121')

    # ── Category divider lines + labels (Y축 왼쪽 텍스트, 컬러 적용) ──
    cat_colors = {
        'MRI': '#1E88E5',
        'PET': '#2E7D32',
        'Cognitive': '#E65100',
        'Biomarker': '#7B1FA2',
        'Derived': '#757575',
    }
    categories = [dt[1] for dt in DATA_TYPES]
    cat_groups = {}
    for i, cat in enumerate(categories):
        cat_groups.setdefault(cat, []).append(i)

    prev_cat = categories[0]
    for i, cat in enumerate(categories):
        if cat != prev_cat:
            ax.axhline(y=i, color='#424242', linewidth=1.8)
            prev_cat = cat

    for cat, indices in cat_groups.items():
        mid = (min(indices) + max(indices) + 1) / 2
        color = cat_colors.get(cat, '#9E9E9E')
        ax.text(-0.08, mid, cat, ha='right', va='center',
                fontsize=10, fontweight='bold', color=color,
                transform=ax.get_yaxis_transform(), clip_on=False)

    # ── Phase brackets (X축 상단, ax.text + ax.plot) ──
    phase_groups = {}
    for j, (label, session_codes) in enumerate(viscode_cols):
        v = session_codes[0]
        phase = viscode_phase(v)
        phase_groups.setdefault(phase, []).append(j)

    for phase, indices in phase_groups.items():
        x0 = min(indices)
        x1 = max(indices) + 1
        mid_x = (x0 + x1) / 2
        color = PHASE_COLORS.get(phase, '#9E9E9E')
        # bracket line (above heatmap)
        y_bkt = 1.01
        ax.plot([x0, x0, x1, x1], [y_bkt - 0.02, y_bkt, y_bkt, y_bkt - 0.02],
                color=color, linewidth=2.5, clip_on=False,
                transform=ax.get_xaxis_transform())
        # label
        ax.text(mid_x, y_bkt + 0.01, phase, ha='center', va='bottom',
                fontsize=10, fontweight='bold', color=color,
                transform=ax.get_xaxis_transform(), clip_on=False)

    # ── Milestone vertical lines ──
    milestones = {'BL': 6, '1yr': 27, '2yr': 48, 'Endpoint': 66}
    for ms_name, ms_v in milestones.items():
        for j, (label, session_codes) in enumerate(viscode_cols):
            if ms_v in session_codes:
                ax.axvline(x=j + 0.5, color='#455A64', linewidth=1.2,
                           linestyle=':', alpha=0.5)
                break

    # ── X-axis: label\n(V코드) ──
    x_labels = []
    for label, session_codes in viscode_cols:
        if len(session_codes) == 1:
            v = session_codes[0]
            x_labels.append(f'{label}\n(V{v})')
        else:
            x_labels.append(label)

    ax.set_xticks([i + 0.5 for i in range(ncols)])
    ax.set_xticklabels(x_labels, rotation=45, ha='right', rotation_mode='anchor',
                       fontsize=xtick_fontsize)
    ax.set_xlabel('')

    # ── Y-axis ──
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=10)
    ax.set_ylabel('')

    # ── Title + subtitle ──
    ax.text(0.5, 1.09,
            f'{cohort_name} Data Availability  (N = {total_bids:,})',
            ha='center', fontsize=16, fontweight='bold',
            transform=ax.transAxes)
    ax.text(0.5, 1.06,
            'Session-centric MERGED.csv  |  Color = % of cohort  |  Numbers = subject count',
            ha='center', fontsize=9, color='#616161', style='italic',
            transform=ax.transAxes)

    fig.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  Saved: {output_path}')


def main():
    parser = argparse.ArgumentParser(description='A4/LEARN data availability heatmap')
    parser.add_argument('--merged-csv',
                        default='/Users/jeon-younghoon/Desktop/ADNI_match/output/a4/MERGED.csv',
                        help='Path to session-centric MERGED.csv')
    parser.add_argument('--output-dir', default=None,
                        help='Output directory (default: same as MERGED.csv)')
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--no-prune', action='store_true',
                        help='Do not prune all-zero VISCODE columns')
    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = os.path.dirname(args.merged_csv)

    # Load
    print(f'Loading {args.merged_csv} ...')
    df = pd.read_csv(args.merged_csv, low_memory=False)
    print(f'  {len(df):,} rows, {len(df.columns)} cols, {df["BID"].nunique():,} BIDs')

    # Split cohorts
    a4_df = df[df['Research_Group'] == 'amyloidE'].copy()
    learn_df = df[df['Research_Group'] == 'LEARN amyloidNE'].copy()

    a4_bids = a4_df['BID'].nunique()
    learn_bids = learn_df['BID'].nunique()
    print(f'  A4: {a4_bids:,} BIDs ({len(a4_df):,} rows)')
    print(f'  LEARN: {learn_bids:,} BIDs ({len(learn_df):,} rows)')

    os.makedirs(args.output_dir, exist_ok=True)

    # A4 compact
    print('\nBuilding A4 compact matrix ...')
    a4_count, a4_pct, a4_vc = build_matrix(a4_df, 'A4', detailed=False)
    if not args.no_prune:
        n_before = len(a4_count.columns)
        a4_count, a4_pct, a4_vc = _prune_empty_columns(a4_count, a4_pct, a4_vc)
        print(f'  Pruned {n_before} → {len(a4_count.columns)} VISCODE columns')
    a4_count.to_csv(os.path.join(args.output_dir, 'A4_availability_matrix.csv'))
    plot_heatmap(a4_count, a4_pct, a4_vc, 'A4', a4_bids,
                 os.path.join(args.output_dir, 'A4_data_availability.png'),
                 dpi=args.dpi)

    # A4 detailed
    print('Building A4 detailed matrix ...')
    a4_count_d, a4_pct_d, a4_vc_d = build_matrix(a4_df, 'A4', detailed=True)
    if not args.no_prune:
        n_before = len(a4_count_d.columns)
        a4_count_d, a4_pct_d, a4_vc_d = _prune_empty_columns(a4_count_d, a4_pct_d, a4_vc_d)
        print(f'  Pruned {n_before} → {len(a4_count_d.columns)} VISCODE columns')
    a4_count_d.to_csv(os.path.join(args.output_dir, 'A4_availability_matrix_detailed.csv'))
    plot_heatmap(a4_count_d, a4_pct_d, a4_vc_d, 'A4', a4_bids,
                 os.path.join(args.output_dir, 'A4_data_availability_detailed.png'),
                 dpi=args.dpi, detailed=True)

    # LEARN detailed
    print('Building LEARN detailed matrix ...')
    learn_count_d, learn_pct_d, learn_vc_d = build_matrix(learn_df, 'LEARN')
    if not args.no_prune:
        n_before = len(learn_count_d.columns)
        learn_count_d, learn_pct_d, learn_vc_d = _prune_empty_columns(learn_count_d, learn_pct_d, learn_vc_d)
        print(f'  Pruned {n_before} → {len(learn_count_d.columns)} VISCODE columns')
    learn_count_d.to_csv(os.path.join(args.output_dir, 'LEARN_availability_matrix_detailed.csv'))
    plot_heatmap(learn_count_d, learn_pct_d, learn_vc_d, 'LEARN', learn_bids,
                 os.path.join(args.output_dir, 'LEARN_data_availability_detailed.png'),
                 dpi=args.dpi, detailed=True)

    # LEARN compact
    print('Building LEARN matrix ...')
    learn_count, learn_pct, learn_vc = build_matrix(learn_df, 'LEARN')
    if not args.no_prune:
        n_before = len(learn_count.columns)
        learn_count, learn_pct, learn_vc = _prune_empty_columns(learn_count, learn_pct, learn_vc)
        print(f'  Pruned {n_before} → {len(learn_count.columns)} VISCODE columns')
    learn_count.to_csv(os.path.join(args.output_dir, 'LEARN_availability_matrix.csv'))
    plot_heatmap(learn_count, learn_pct, learn_vc, 'LEARN', learn_bids,
                 os.path.join(args.output_dir, 'LEARN_data_availability.png'),
                 dpi=args.dpi)

    print('\nDone.')


if __name__ == '__main__':
    main()
