"""
verify_adnimerge_1toN.py — ADNIMERGE 1:N 할당 검증

하나의 ADNIMERGE row가 여러 MERGED.csv row에 할당되는지 검증.

메커니즘:
  nearest_adnimerge()는 AQUDATE와 가장 가까운 EXAMDATE 행 선택 → clinical values 복사
  calc_viscode()는 AQUDATE - EXAMDATE_bl로 VISCODE_FIX 결정
  → 동일 ADNIMERGE row의 clinical values가 서로 다른 VISCODE_FIX에 복제 가능

검증 항목:
  A. ADNIMERGE row 재사용 빈도 (clinical fingerprint 기반)
  B. Phantom VISCODE_FIX (ADNIMERGE에 없는 조합)
  C. COLPROT별 분포
  D. Clinical 값 정확성 (시점 불일치)
  E. ref vs new 비교 (둘 다 지정 시)

Usage:
  python scripts/verify_adnimerge_1toN.py \\
    --merged output/ADNI_matching_v4/MERGED.csv \\
    --adnimerge csv/ADNIMERGE_260213.csv \\
    --label "new"

  python scripts/verify_adnimerge_1toN.py \\
    --merged output/ADNI_matching_v4/MERGED.csv \\
    --adnimerge csv/ADNIMERGE_260213.csv \\
    --merged2 /Volumes/nfs_storage-1/1_combined/ADNI/ORIG/DEMO/ADNI_matching_240826/MERGED.csv \\
    --adnimerge2 csv/ref/ADNIMERGE_240821.csv \\
    --label "new" --label2 "ref" \\
    --markdown result_1toN.md
"""

import argparse
import sys
from io import StringIO

import pandas as pd
import numpy as np


# ─── Clinical fingerprint columns ───────────────────────────────────────────
FINGERPRINT_COLS = ['EXAMDATE', 'MMSE', 'CDRSB', 'DX']


def _normalize_viscode(v: str) -> str:
    """VISCODE 형식 정규화: bl→m000, m03→m003, m006→m006 등.
    ADNIMERGE는 'bl','m03','m06','m12' 형식, VISCODE_FIX는 'm000','m003','m006' 형식.
    """
    v = str(v).strip()
    if v == 'bl':
        return 'm000'
    if v.startswith('m'):
        num = v[1:]
        try:
            return 'm%03d' % int(num)
        except ValueError:
            return v
    return v


def _make_fingerprint(row):
    """(EXAMDATE, MMSE, CDRSB, DX) 튜플 생성 — NaN 제외."""
    vals = []
    for c in FINGERPRINT_COLS:
        v = row.get(c)
        if pd.notna(v) and str(v).strip():
            vals.append(str(v).strip())
    return tuple(vals) if vals else None


def analyze(merged_path: str, adnimerge_path: str, label: str) -> dict:
    """단일 (MERGED, ADNIMERGE) 쌍에 대한 1:N 검증."""
    merged = pd.read_csv(merged_path, low_memory=False)
    adnimerge = pd.read_csv(adnimerge_path, low_memory=False)

    results = {'label': label}

    # ── 기본 통계 ─────────────────────────────────────────────────
    results['total_merged_rows'] = len(merged)
    results['total_ptids'] = merged['PTID'].nunique()
    results['total_adnimerge_rows'] = len(adnimerge)

    # ── A. ADNIMERGE row 재사용 빈도 ──────────────────────────────
    merged['_clin_fp'] = merged.apply(_make_fingerprint, axis=1)
    has_fp = merged[merged['_clin_fp'].notna()].copy()

    # (PTID, fingerprint) 별 VISCODE_FIX 수
    grouped = has_fp.groupby(['PTID', '_clin_fp'])['VISCODE_FIX'].nunique()
    one_to_n = grouped[grouped > 1]

    results['unique_clinical_fingerprints'] = len(grouped)
    results['one_to_n_cases'] = len(one_to_n)

    # 영향받는 MERGED 행 수 계산
    if len(one_to_n) > 0:
        otn_keys = set(one_to_n.index)
        affected_mask = has_fp.apply(
            lambda r: (r['PTID'], r['_clin_fp']) in otn_keys, axis=1)
        results['affected_merged_rows'] = int(affected_mask.sum())
    else:
        results['affected_merged_rows'] = 0

    results['affected_pct'] = (
        results['affected_merged_rows'] / results['total_merged_rows'] * 100
        if results['total_merged_rows'] > 0 else 0
    )

    # 1:N 분포 (N=2,3,4,...별 건수)
    if len(one_to_n) > 0:
        n_dist = one_to_n.value_counts().sort_index()
        results['n_distribution'] = {int(k): int(v) for k, v in n_dist.items()}
    else:
        results['n_distribution'] = {}

    # 1:N 상위 예시 (최대 10건)
    examples = []
    if len(one_to_n) > 0:
        for (ptid, fp), n_viscodes in one_to_n.nlargest(10).items():
            mask = (has_fp['PTID'] == ptid) & (has_fp['_clin_fp'] == fp)
            viscodes = sorted(has_fp.loc[mask, 'VISCODE_FIX'].unique())
            examdate = fp[0] if fp else ''
            examples.append({
                'PTID': ptid,
                'EXAMDATE': examdate,
                'N_VISCODES': int(n_viscodes),
                'VISCODES': ', '.join(str(v) for v in viscodes),
            })
    results['examples'] = examples

    # ── B. Phantom VISCODE_FIX ────────────────────────────────────
    # VISCODE 형식 정규화: ADNIMERGE 'bl/m03/m06' → 'm000/m003/m006'
    merged_pairs = set(zip(merged['PTID'], merged['VISCODE_FIX'].astype(str)))
    adni_pairs = set(zip(adnimerge['PTID'],
                         adnimerge['VISCODE'].astype(str).apply(_normalize_viscode)))
    phantom = merged_pairs - adni_pairs
    results['phantom_viscode_fix'] = len(phantom)
    results['phantom_pct'] = (
        len(phantom) / len(merged_pairs) * 100
        if len(merged_pairs) > 0 else 0
    )

    # Phantom 상위 예시
    phantom_examples = []
    phantom_list = sorted(phantom)[:20]
    for ptid, viscode in phantom_list:
        phantom_examples.append({'PTID': ptid, 'VISCODE_FIX': viscode})
    results['phantom_examples'] = phantom_examples

    # ── C. COLPROT별 분포 ─────────────────────────────────────────
    colprot_stats = {}
    if 'COLPROT' in merged.columns:
        for colprot, grp in merged.groupby('COLPROT'):
            grp = grp.copy()
            grp['_clin_fp'] = grp.apply(_make_fingerprint, axis=1)
            grp_fp = grp[grp['_clin_fp'].notna()]
            g = grp_fp.groupby(['PTID', '_clin_fp'])['VISCODE_FIX'].nunique()
            otn = g[g > 1]

            # Phantom for this COLPROT (adni_pairs already normalized above)
            cp_merged_pairs = set(zip(grp['PTID'], grp['VISCODE_FIX'].astype(str)))
            cp_phantom = cp_merged_pairs - adni_pairs  # uses normalized adni_pairs

            colprot_stats[str(colprot)] = {
                'total_rows': len(grp),
                'one_to_n_cases': len(otn),
                'affected_rows': int(
                    grp_fp.apply(
                        lambda r: (r['PTID'], r['_clin_fp']) in set(otn.index),
                        axis=1
                    ).sum()
                ) if len(otn) > 0 else 0,
                'phantom': len(cp_phantom),
            }
    results['by_colprot'] = colprot_stats

    # ── D. Clinical 값 정확성 (시점 불일치) ────────────────────────
    # MERGED의 (PTID, VISCODE_FIX) vs ADNIMERGE의 (PTID, VISCODE)에서 MMSE 비교
    # VISCODE 정규화 후 비교
    adni_lookup = {}
    for _, row in adnimerge.iterrows():
        key = (row['PTID'], _normalize_viscode(str(row['VISCODE'])))
        adni_lookup[key] = {
            'MMSE': row.get('MMSE'),
            'CDRSB': row.get('CDRSB'),
            'DX': row.get('DX'),
            'EXAMDATE': row.get('EXAMDATE'),
        }

    mmse_match = 0
    mmse_mismatch = 0
    mmse_mismatch_examples = []

    for _, row in merged.iterrows():
        ptid = row.get('PTID', '')
        viscode = str(row.get('VISCODE_FIX', ''))
        key = (ptid, viscode)
        adni_row = adni_lookup.get(key)
        if adni_row is None:
            continue

        m_mmse = row.get('MMSE')
        a_mmse = adni_row['MMSE']

        if pd.isna(m_mmse) and pd.isna(a_mmse):
            continue
        if pd.isna(m_mmse) or pd.isna(a_mmse):
            mmse_mismatch += 1
            if len(mmse_mismatch_examples) < 10:
                mmse_mismatch_examples.append({
                    'PTID': ptid, 'VISCODE_FIX': viscode,
                    'MERGED_MMSE': str(m_mmse), 'ADNIMERGE_MMSE': str(a_mmse),
                    'MERGED_EXAMDATE': str(row.get('EXAMDATE', '')),
                    'ADNIMERGE_EXAMDATE': str(adni_row['EXAMDATE']),
                })
            continue

        try:
            if float(m_mmse) == float(a_mmse):
                mmse_match += 1
            else:
                mmse_mismatch += 1
                if len(mmse_mismatch_examples) < 10:
                    mmse_mismatch_examples.append({
                        'PTID': ptid, 'VISCODE_FIX': viscode,
                        'MERGED_MMSE': str(m_mmse), 'ADNIMERGE_MMSE': str(a_mmse),
                        'MERGED_EXAMDATE': str(row.get('EXAMDATE', '')),
                        'ADNIMERGE_EXAMDATE': str(adni_row['EXAMDATE']),
                    })
        except (ValueError, TypeError):
            pass

    results['clinical_mmse_match'] = mmse_match
    results['clinical_mmse_mismatch'] = mmse_mismatch
    results['clinical_mismatch_pct'] = (
        mmse_mismatch / (mmse_match + mmse_mismatch) * 100
        if (mmse_match + mmse_mismatch) > 0 else 0
    )
    results['mmse_mismatch_examples'] = mmse_mismatch_examples

    # Cleanup temp column
    merged.drop('_clin_fp', axis=1, inplace=True, errors='ignore')

    return results


def print_results(r: dict, file=None):
    """결과를 stdout에 표 형태로 출력."""
    out = file or sys.stdout

    print(f"\n{'='*70}", file=out)
    print(f"  ADNIMERGE 1:N 할당 검증 — [{r['label']}]", file=out)
    print(f"{'='*70}", file=out)

    print(f"\n{'─'*40}", file=out)
    print(f"  기본 통계", file=out)
    print(f"{'─'*40}", file=out)
    print(f"  MERGED.csv 총 행 수:           {r['total_merged_rows']:>8,}", file=out)
    print(f"  MERGED.csv 피험자 수:          {r['total_ptids']:>8,}", file=out)
    print(f"  ADNIMERGE 총 행 수:            {r['total_adnimerge_rows']:>8,}", file=out)

    print(f"\n{'─'*40}", file=out)
    print(f"  A. ADNIMERGE row 재사용 (1:N)", file=out)
    print(f"{'─'*40}", file=out)
    print(f"  고유 clinical fingerprint 수:  {r['unique_clinical_fingerprints']:>8,}", file=out)
    print(f"  1:N 재사용 ADNIMERGE 행:       {r['one_to_n_cases']:>8,}", file=out)
    print(f"  영향받는 MERGED 행:            {r['affected_merged_rows']:>8,}  ({r['affected_pct']:.1f}%)", file=out)

    if r['n_distribution']:
        print(f"\n  N값 분포:", file=out)
        for n, count in sorted(r['n_distribution'].items()):
            print(f"    N={n}: {count}건", file=out)

    if r['examples']:
        print(f"\n  상위 예시 (최대 10건):", file=out)
        print(f"  {'PTID':<16} {'EXAMDATE':<12} {'N':>3}  VISCODES", file=out)
        for ex in r['examples']:
            print(f"  {ex['PTID']:<16} {ex['EXAMDATE']:<12} {ex['N_VISCODES']:>3}  {ex['VISCODES']}", file=out)

    print(f"\n{'─'*40}", file=out)
    print(f"  B. Phantom VISCODE_FIX", file=out)
    print(f"{'─'*40}", file=out)
    print(f"  ADNIMERGE에 없는 조합 수:      {r['phantom_viscode_fix']:>8,}  ({r['phantom_pct']:.1f}%)", file=out)

    if r['phantom_examples']:
        print(f"\n  예시 (최대 20건):", file=out)
        for ex in r['phantom_examples'][:10]:
            print(f"    {ex['PTID']:<16} {ex['VISCODE_FIX']}", file=out)

    print(f"\n{'─'*40}", file=out)
    print(f"  C. COLPROT별 분포", file=out)
    print(f"{'─'*40}", file=out)
    if r['by_colprot']:
        print(f"  {'COLPROT':<10} {'Rows':>8} {'1:N cases':>10} {'Affected':>10} {'Phantom':>8}", file=out)
        for cp, stats in sorted(r['by_colprot'].items()):
            print(f"  {cp:<10} {stats['total_rows']:>8,} {stats['one_to_n_cases']:>10,} "
                  f"{stats['affected_rows']:>10,} {stats['phantom']:>8,}", file=out)
    else:
        print(f"  (COLPROT 컬럼 없음)", file=out)

    print(f"\n{'─'*40}", file=out)
    print(f"  D. Clinical 값 정확성 (MMSE)", file=out)
    print(f"{'─'*40}", file=out)
    print(f"  MMSE 일치:                     {r['clinical_mmse_match']:>8,}", file=out)
    print(f"  MMSE 불일치:                   {r['clinical_mmse_mismatch']:>8,}  ({r['clinical_mismatch_pct']:.1f}%)", file=out)

    if r['mmse_mismatch_examples']:
        print(f"\n  불일치 예시 (최대 10건):", file=out)
        print(f"  {'PTID':<16} {'VISCODE':>8} {'M_MMSE':>7} {'A_MMSE':>7} {'M_EXAMDATE':<12} {'A_EXAMDATE':<12}", file=out)
        for ex in r['mmse_mismatch_examples']:
            print(f"  {ex['PTID']:<16} {ex['VISCODE_FIX']:>8} {ex['MERGED_MMSE']:>7} "
                  f"{ex['ADNIMERGE_MMSE']:>7} {ex['MERGED_EXAMDATE']:<12} {ex['ADNIMERGE_EXAMDATE']:<12}", file=out)

    print(file=out)


def format_markdown(results_list: list) -> str:
    """결과를 Issue 코멘트용 markdown으로 포맷."""
    buf = StringIO()

    buf.write("## ADNIMERGE 1:N 할당 검증 결과\n\n")
    buf.write("`nearest_adnimerge()`가 하나의 ADNIMERGE row를 여러 VISCODE_FIX에 할당하는 현상을 검증.\n\n")

    for r in results_list:
        buf.write(f"### [{r['label']}]\n\n")

        # 요약 테이블
        buf.write("| 지표 | 값 |\n")
        buf.write("|------|----|\n")
        buf.write(f"| MERGED.csv 총 행 수 | {r['total_merged_rows']:,} |\n")
        buf.write(f"| MERGED.csv 피험자 수 | {r['total_ptids']:,} |\n")
        buf.write(f"| ADNIMERGE 총 행 수 | {r['total_adnimerge_rows']:,} |\n")
        buf.write(f"| 고유 clinical fingerprint 수 | {r['unique_clinical_fingerprints']:,} |\n")
        buf.write(f"| **1:N 재사용 ADNIMERGE 행** | **{r['one_to_n_cases']:,}** |\n")
        buf.write(f"| **영향받는 MERGED 행** | **{r['affected_merged_rows']:,} ({r['affected_pct']:.1f}%)** |\n")
        buf.write(f"| Phantom VISCODE_FIX | {r['phantom_viscode_fix']:,} ({r['phantom_pct']:.1f}%) |\n")
        buf.write(f"| MMSE 일치 | {r['clinical_mmse_match']:,} |\n")
        buf.write(f"| MMSE 불일치 | {r['clinical_mmse_mismatch']:,} ({r['clinical_mismatch_pct']:.1f}%) |\n")
        buf.write("\n")

        # N 분포
        if r['n_distribution']:
            buf.write("**1:N 분포:**\n\n")
            buf.write("| N (VISCODE 수) | 건수 |\n")
            buf.write("|:-:|:-:|\n")
            for n, count in sorted(r['n_distribution'].items()):
                buf.write(f"| {n} | {count} |\n")
            buf.write("\n")

        # COLPROT별
        if r['by_colprot']:
            buf.write("**COLPROT별 분포:**\n\n")
            buf.write("| COLPROT | Rows | 1:N cases | Affected rows | Phantom |\n")
            buf.write("|---------|-----:|----------:|--------------:|--------:|\n")
            for cp, stats in sorted(r['by_colprot'].items()):
                buf.write(f"| {cp} | {stats['total_rows']:,} | {stats['one_to_n_cases']:,} | "
                          f"{stats['affected_rows']:,} | {stats['phantom']:,} |\n")
            buf.write("\n")

        # 1:N 예시
        if r['examples']:
            buf.write("<details>\n<summary>1:N 상위 예시 (접기)</summary>\n\n")
            buf.write("| PTID | EXAMDATE | N | VISCODES |\n")
            buf.write("|------|----------|:-:|----------|\n")
            for ex in r['examples']:
                buf.write(f"| {ex['PTID']} | {ex['EXAMDATE']} | {ex['N_VISCODES']} | {ex['VISCODES']} |\n")
            buf.write("\n</details>\n\n")

        # MMSE 불일치 예시
        if r['mmse_mismatch_examples']:
            buf.write("<details>\n<summary>MMSE 불일치 예시 (접기)</summary>\n\n")
            buf.write("| PTID | VISCODE_FIX | MERGED MMSE | ADNIMERGE MMSE | MERGED EXAMDATE | ADNIMERGE EXAMDATE |\n")
            buf.write("|------|-------------|:-----------:|:--------------:|-----------------|--------------------|\n")
            for ex in r['mmse_mismatch_examples']:
                buf.write(f"| {ex['PTID']} | {ex['VISCODE_FIX']} | {ex['MERGED_MMSE']} | "
                          f"{ex['ADNIMERGE_MMSE']} | {ex['MERGED_EXAMDATE']} | {ex['ADNIMERGE_EXAMDATE']} |\n")
            buf.write("\n</details>\n\n")

    # 해석
    buf.write("### 해석\n\n")
    buf.write("**메커니즘**: `nearest_adnimerge()`와 `calc_viscode()`가 독립적으로 동작:\n")
    buf.write("1. `nearest_adnimerge()`: AQUDATE와 가장 가까운 ADNIMERGE EXAMDATE 행 선택 → clinical values 복사\n")
    buf.write("2. `calc_viscode()`: `AQUDATE - EXAMDATE_bl`로 VISCODE_FIX 결정\n\n")
    buf.write("→ Subject에 ADNIMERGE visit이 적고 이미지가 여러 시점에 있으면, "
              "동일 ADNIMERGE row의 clinical values가 서로 다른 VISCODE_FIX 행에 복제됨.\n\n")
    buf.write("**Phantom VISCODE_FIX**: `calc_viscode()`가 MONTH_KEYS에서 가장 가까운 표준 방문 시점을 선택하므로, "
              "ADNIMERGE에 실제로 존재하지 않는 VISCODE가 생성될 수 있음 (예: m003, m009).\n\n")
    buf.write("**MMSE 불일치**: `nearest_adnimerge()`가 다른 시점의 ADNIMERGE row를 가져온 경우, "
              "MERGED의 VISCODE_FIX에 해당하는 ADNIMERGE row의 MMSE와 다를 수 있음.\n")

    return buf.getvalue()


def main():
    parser = argparse.ArgumentParser(description='ADNIMERGE 1:N 할당 검증')
    parser.add_argument('--merged', required=True, help='MERGED.csv 경로')
    parser.add_argument('--adnimerge', required=True, help='ADNIMERGE CSV 경로')
    parser.add_argument('--label', default='primary', help='결과 레이블')
    parser.add_argument('--merged2', help='비교 대상 MERGED.csv 경로 (선택)')
    parser.add_argument('--adnimerge2', help='비교 대상 ADNIMERGE CSV 경로 (선택)')
    parser.add_argument('--label2', default='secondary', help='비교 대상 레이블')
    parser.add_argument('--markdown', help='Markdown 출력 파일 경로')
    args = parser.parse_args()

    results_list = []

    print(f"Analyzing [{args.label}]: {args.merged}")
    r1 = analyze(args.merged, args.adnimerge, args.label)
    results_list.append(r1)
    print_results(r1)

    if args.merged2 and args.adnimerge2:
        print(f"Analyzing [{args.label2}]: {args.merged2}")
        r2 = analyze(args.merged2, args.adnimerge2, args.label2)
        results_list.append(r2)
        print_results(r2)

    if args.markdown:
        md = format_markdown(results_list)
        with open(args.markdown, 'w') as f:
            f.write(md)
        print(f"\nMarkdown saved: {args.markdown}")


if __name__ == '__main__':
    main()
