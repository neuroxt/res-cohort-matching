#!/usr/bin/env python3
"""
reorganize_nii_by_viscode.py — ADNI_New NII 트리를 PTID/VISCODE_FIX/MODALITY 레이아웃으로 재배치

현재 소스 레이아웃 (수집 구조):
    NII_ROOT/{TOP_MOD}/{PTID}/{PROTOCOL}/{YYYY-MM-DD_HH_MM_SS.0}/I{UID}/
        ├── ADNI_{PTID}_{MR|PT}_{PROTOCOL}_br_raw*.nii.gz
        └── ADNI_{PTID}_{MR|PT}_{PROTOCOL}_br_raw*.json

타겟 레이아웃 (참조 1_combined/ADNI 스타일, in-place):
    NII_ROOT/{PTID}/{VISCODE_FIX}/{MODALITY}/<원본 파일명>

진실 소스: matching 출력 디렉토리의 {MODALITY}_all.csv (19개). _unique.csv는
(PTID, VISCODE_FIX) 중복 제거해서 대체 series가 잘려나가므로 사용하지 않음.

Usage:
    # 1) Dry run
    python scripts/reorganize_nii_by_viscode.py \\
        --nii-root /Volumes/nfs_storage/ADNI_New/ORIG/NII \\
        --matching-dir /Volumes/nfs_storage/ADNI_New/ORIG/DEMO/matching \\
        --dry-run

    # 2) 소규모부터 실제 이동
    python scripts/reorganize_nii_by_viscode.py \\
        --nii-root /Volumes/nfs_storage/ADNI_New/ORIG/NII \\
        --matching-dir /Volumes/nfs_storage/ADNI_New/ORIG/DEMO/matching \\
        --modality PI2620_6MM,NAV4694_6MM,MK6240_6MM

    # 3) 전체 모달리티
    python scripts/reorganize_nii_by_viscode.py \\
        --nii-root /Volumes/nfs_storage/ADNI_New/ORIG/NII \\
        --matching-dir /Volumes/nfs_storage/ADNI_New/ORIG/DEMO/matching

    # 4) 빈 수집-구조 디렉토리 정리
    python scripts/reorganize_nii_by_viscode.py ... --clean-empty
"""
from __future__ import annotations

import argparse
import logging
import os
import re
import shutil
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd


def _now() -> float:
    return time.monotonic()

LOG_FMT = '%(asctime)s | %(levelname)-5s | %(message)s'

# 매칭 파이프라인이 만들어내는 19개 정식 모달리티
# (src/adni/matching/config.py MODALITY_CONFIG 기준)
ALL_MODALITIES = [
    'T1',
    'T2_FSE', 'T2_TSE', 'T2_STAR', 'T2_3D',
    'FLAIR',
    'FMRI',
    'DTI', 'DTI_MB',
    'AV45_6MM', 'AV45_8MM',
    'AV1451_6MM', 'AV1451_8MM',
    'FBB_6MM',
    'HIPPO', 'ASL',
    'MK6240_6MM', 'NAV4694_6MM', 'PI2620_6MM',
]

# 소스 상위 폴더 (수집 단계 — 정식 모달리티와 1:1 아님)
DEFAULT_TOP_MODS = ['T1', 'T2', 'DTI', 'fMRI', 'MRI', 'PET']

# 정식 모달리티 → 스캔해야 할 TOP_MOD 폴더 후보 집합.
# MRI/ 는 ADNI4 혼합 폴더라 거의 모든 MR 모달리티가 들어있을 수 있음.
MODALITY_TO_TOP_MODS: dict[str, list[str]] = {
    'T1':          ['T1', 'MRI'],
    'FLAIR':       ['T2', 'MRI'],
    'T2_FSE':      ['T2'],
    'T2_TSE':      ['T2'],
    'T2_STAR':     ['T2', 'MRI'],
    'T2_3D':       ['MRI'],
    'HIPPO':       ['MRI'],
    'ASL':         ['MRI'],
    'DTI':         ['DTI', 'MRI'],
    'DTI_MB':      ['DTI', 'MRI'],
    'FMRI':        ['fMRI', 'MRI'],
    'AV45_6MM':    ['PET'],
    'AV45_8MM':    ['PET'],
    'AV1451_6MM':  ['PET'],
    'AV1451_8MM':  ['PET'],
    'FBB_6MM':     ['PET'],
    'MK6240_6MM':  ['PET'],
    'NAV4694_6MM': ['PET'],
    'PI2620_6MM':  ['PET'],
}


def derive_top_mods(modalities: list[str]) -> list[str]:
    """선택된 modality 기반으로 스캔할 TOP_MOD 폴더 집합 도출."""
    tops: set[str] = set()
    for m in modalities:
        for t in MODALITY_TO_TOP_MODS.get(m, []):
            tops.add(t)
    # 기본 순서 보존
    return [t for t in DEFAULT_TOP_MODS if t in tops]

IUID_DIR_RE = re.compile(r'^I(\d+)$')
PTID_RE = re.compile(r'\d{3}_S_\d{4,5}')


# =============================================================================
# Helpers
# =============================================================================

def _normalize_uid(val) -> str:
    """IUID 값을 정규화된 문자열로 (numpy float/int/str 대응).

    `int(float(val))` 패턴은 src/adni/matching/matching.py의 _normalize_uid와 동일.
    """
    if val is None:
        return ''
    try:
        if pd.isna(val):
            return ''
    except (TypeError, ValueError):
        pass
    try:
        return str(int(float(val)))
    except (ValueError, TypeError):
        s = str(val).strip()
        return s


def build_lookup(matching_dir: str, modalities: list[str], log: logging.Logger):
    """19개 {MODALITY}_all.csv에서 (PTID, IUID) → [(VISCODE_FIX, MODALITY), ...] 매핑 구축.

    Returns:
        lookup: dict[(ptid, iuid_str)] -> list of (viscode_fix, modality)
        stats: per-modality 매핑 개수 dict
    """
    lookup: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    stats = {}

    for mod in modalities:
        csv_path = os.path.join(matching_dir, f'{mod}_all.csv')
        if not os.path.isfile(csv_path):
            log.warning('  %s_all.csv not found — skipping', mod)
            stats[mod] = 0
            continue

        iuid_col = f'I_{mod}'
        try:
            df = pd.read_csv(
                csv_path,
                usecols=['PTID', 'VISCODE_FIX', iuid_col],
                low_memory=False,
            )
        except ValueError as exc:
            log.error('  %s: required column missing (%s)', csv_path, exc)
            stats[mod] = 0
            continue

        valid = 0
        viscode_err = 0
        for _, r in df.iterrows():
            ptid = str(r['PTID']).strip() if not pd.isna(r['PTID']) else ''
            viscode = str(r['VISCODE_FIX']).strip() if not pd.isna(r['VISCODE_FIX']) else ''
            iuid = _normalize_uid(r[iuid_col])

            if not ptid or not iuid:
                continue
            if not viscode or viscode == 'error':
                viscode_err += 1
                continue

            lookup[(ptid, iuid)].append((viscode, mod))
            valid += 1

        stats[mod] = valid
        log.info('  %-14s %6d valid (viscode_error: %d, total rows: %d)',
                 mod, valid, viscode_err, len(df))

    # 다중 매칭 (동일 IUID → 여러 modality)
    multi = sum(1 for v in lookup.values() if len(v) > 1)
    if multi:
        log.info('  Multi-modality IUIDs: %d (same UID matched to >1 modality)', multi)

    return dict(lookup), stats


def _scan_ptid_folder(ptid_path: str) -> list[tuple[str, str, str]]:
    """PTID 폴더 아래에서 I{UID} 리프 디렉토리를 구조화된 3단계 scandir로 수집.

    예상 구조: {PTID}/{PROTOCOL}/{DATETIME}/I{UID}/
    3단계 scandir은 os.walk 대비 NFS stat 호출을 크게 줄임 (inventory.py 패턴).

    Returns:
        list of (ptid_name, iuid_str, iuid_path)
    """
    ptid_name = os.path.basename(ptid_path.rstrip(os.sep))
    results: list[tuple[str, str, str]] = []
    try:
        with os.scandir(ptid_path) as protos:
            for proto in protos:
                if not proto.is_dir(follow_symlinks=True):
                    continue
                try:
                    with os.scandir(proto.path) as dts:
                        for dt in dts:
                            if not dt.is_dir(follow_symlinks=True):
                                continue
                            try:
                                with os.scandir(dt.path) as uids:
                                    for uid_entry in uids:
                                        if not uid_entry.is_dir(follow_symlinks=True):
                                            continue
                                        m = IUID_DIR_RE.match(uid_entry.name)
                                        if m:
                                            results.append(
                                                (ptid_name, m.group(1), uid_entry.path))
                            except OSError:
                                pass
                except OSError:
                    pass
    except OSError:
        pass
    return results


def collect_iuid_dirs(
    nii_root: str,
    top_mods: list[str],
    log: logging.Logger,
    ptid_workers: int = 8,
):
    """{nii_root}/{TOP_MOD}/{PTID}/{PROTOCOL}/{DATETIME}/I{UID}/ 리프 디렉토리 수집.

    PTID 레벨 병렬 스캔. 재배치된 `{PTID}/` 루트(이미 타겟 레이아웃인 경로)는
    TOP_MOD 필터로 자연 배제 (TOP_MOD ∉ PTID 패턴).

    Yields:
        (ptid, iuid_str, iuid_path)
    """
    for top in top_mods:
        top_path = os.path.join(nii_root, top)
        if not os.path.isdir(top_path):
            log.debug('  TOP dir missing: %s', top_path)
            continue

        # 이 top에 속한 PTID 폴더 수집
        try:
            ptid_paths = [
                entry.path
                for entry in os.scandir(top_path)
                if entry.is_dir(follow_symlinks=True)
                and PTID_RE.fullmatch(entry.name)
            ]
        except OSError as exc:
            log.warning('  Cannot list %s: %s', top_path, exc)
            continue

        ptid_paths.sort()
        log.info('Scanning %s/ (%d PTIDs, %d workers)',
                 top, len(ptid_paths), ptid_workers)

        if ptid_workers <= 1 or len(ptid_paths) <= 1:
            for pp in ptid_paths:
                for row in _scan_ptid_folder(pp):
                    yield row
            continue

        with ThreadPoolExecutor(max_workers=ptid_workers) as ex:
            futures = [ex.submit(_scan_ptid_folder, pp) for pp in ptid_paths]
            for fut in as_completed(futures):
                try:
                    rows = fut.result()
                except Exception as exc:
                    log.warning('  PTID scan error: %s', exc)
                    continue
                for row in rows:
                    yield row


def collect_payload_files(iuid_dir: str) -> list[str]:
    """I{UID} 폴더 안의 .nii.gz + 동일 이름 .json 수집. 파일명 순 정렬."""
    if not os.path.isdir(iuid_dir):
        return []
    try:
        entries = os.listdir(iuid_dir)
    except OSError:
        return []
    wanted = []
    for name in entries:
        full = os.path.join(iuid_dir, name)
        if not os.path.isfile(full):
            continue
        # BIDS NII + sidecar만 이동. DICOM 파편이나 .DS_Store 등은 건드리지 않음.
        if name.endswith('.nii.gz') or name.endswith('.nii') or name.endswith('.json'):
            wanted.append(full)
    wanted.sort()
    return wanted


def _insert_iuid_suffix(fname: str, iuid: str) -> str:
    """파일명에 `_I{UID}` suffix를 삽입해 동일 폴더 내 여러 series 충돌 방지.

    예: ADNI_003_..._br_raw.nii.gz → ADNI_003_..._br_raw_I1456648.nii.gz
        foo.nii → foo_I123.nii
        foo.json → foo_I123.json
    """
    # 이미 IUID가 들어 있으면 그대로
    if f'_I{iuid}' in fname:
        return fname
    for ext in ('.nii.gz', '.nii.json', '.nii', '.json'):
        if fname.endswith(ext):
            stem = fname[: -len(ext)]
            return f'{stem}_I{iuid}{ext}'
    # 알 수 없는 확장자
    return f'{fname}_I{iuid}'


def _process_iuid(
    ptid: str,
    iuid: str,
    iuid_path: str,
    targets: list[tuple[str, str]],
    nii_root: str,
    dry_run: bool,
) -> tuple[list[dict], dict]:
    """단일 IUID 폴더 처리 — collect_payload_files + move/copy + manifest rows 생성.

    스레드 워커에서 호출. 카운터는 로컬 dict로 반환해서 메인이 합산.

    Returns:
        (manifest_rows, counter_stats)
        counter_stats 구조: {'moved', 'copied', 'already_exists', 'no_files',
                              'errors', 'per_mod': {modality: count}}
    """
    rows: list[dict] = []
    stats = {
        'moved': 0, 'copied': 0, 'already_exists': 0,
        'no_files': 0, 'errors': 0,
        'per_mod': defaultdict(int),
    }

    payload = collect_payload_files(iuid_path)
    if not payload:
        stats['no_files'] += 1
        return rows, stats

    n = len(targets)
    for i, (viscode, modality) in enumerate(targets):
        is_last = (i == n - 1)
        op = 'move' if is_last else 'copy'
        dest_dir = os.path.join(nii_root, ptid, viscode, modality)

        for src_path in list(payload):
            fname = os.path.basename(src_path)
            # 항상 IUID suffix를 박아 넣음: (PTID, VISCODE, MOD) 폴더 내 충돌 방지.
            # 재실행 시 같은 src → 같은 dst로 idempotent.
            fname = _insert_iuid_suffix(fname, iuid)
            dst_path = os.path.join(dest_dir, fname)

            if os.path.exists(dst_path):
                stats['already_exists'] += 1
                rows.append({
                    'ptid': ptid, 'iuid': iuid,
                    'viscode_fix': viscode, 'modality': modality,
                    'src_path': src_path, 'dst_path': dst_path,
                    'op': op, 'status': 'already_exists', 'error': '',
                })
                continue

            if dry_run:
                stats['moved' if is_last else 'copied'] += 1
                stats['per_mod'][modality] += 1
                rows.append({
                    'ptid': ptid, 'iuid': iuid,
                    'viscode_fix': viscode, 'modality': modality,
                    'src_path': src_path, 'dst_path': dst_path,
                    'op': op, 'status': 'dry_run', 'error': '',
                })
                continue

            try:
                os.makedirs(dest_dir, exist_ok=True)
                if is_last:
                    shutil.move(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)
            except (OSError, shutil.Error) as exc:
                stats['errors'] += 1
                rows.append({
                    'ptid': ptid, 'iuid': iuid,
                    'viscode_fix': viscode, 'modality': modality,
                    'src_path': src_path, 'dst_path': dst_path,
                    'op': op, 'status': 'error', 'error': str(exc),
                })
                continue

            stats['moved' if is_last else 'copied'] += 1
            stats['per_mod'][modality] += 1
            rows.append({
                'ptid': ptid, 'iuid': iuid,
                'viscode_fix': viscode, 'modality': modality,
                'src_path': src_path, 'dst_path': dst_path,
                'op': op, 'status': op + 'd', 'error': '',
            })

    return rows, stats


def remove_empty_dirs(root: str, log: logging.Logger) -> int:
    """bottom-up으로 빈 디렉토리 제거. .DS_Store만 있으면 빈 것으로 간주."""
    if not os.path.isdir(root):
        return 0
    removed = 0
    for cur, dirs, files in os.walk(root, topdown=False):
        real_files = [f for f in files if not f.startswith('.')]
        if dirs or real_files:
            continue
        try:
            for f in files:
                try:
                    os.remove(os.path.join(cur, f))
                except OSError:
                    pass
            os.rmdir(cur)
            removed += 1
        except OSError:
            pass
    log.info('  Removed %d empty directories under %s', removed, root)
    return removed


# =============================================================================
# Main
# =============================================================================

def main():
    ap = argparse.ArgumentParser(
        description='Reorganize ADNI_New NII tree to PTID/VISCODE_FIX/MODALITY (in-place, move)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument('--nii-root', required=True,
                    help='NII tree root (e.g., /Volumes/nfs_storage/ADNI_New/ORIG/NII)')
    ap.add_argument('--matching-dir', required=True,
                    help='Directory containing {MODALITY}_all.csv files')
    ap.add_argument('--modality', default=None,
                    help='Comma-separated modalities to process (default: all 19)')
    ap.add_argument('--top-mods', default=None,
                    help='Source top-level folders to scan (default: auto-derived from --modality)')
    ap.add_argument('--scan-workers', type=int, default=8,
                    help='PTID-level parallel scan threads per top-mod folder')
    ap.add_argument('--move-workers', type=int, default=16,
                    help='Parallel worker threads for move/copy operations')
    ap.add_argument('--dry-run', action='store_true',
                    help='Preview only; no file operations')
    ap.add_argument('--clean-empty', action='store_true',
                    help='After moving, remove empty source subdirectories')
    ap.add_argument('--manifest', default=None,
                    help='Manifest CSV path (default: <matching-dir>/nii_reorganize_manifest.csv)')
    ap.add_argument('-v', '--verbose', action='store_true')
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format=LOG_FMT,
    )
    log = logging.getLogger('reorganize_nii')

    # --- 검증 ---
    if not os.path.isdir(args.nii_root):
        log.error('NII root not found: %s', args.nii_root)
        sys.exit(1)
    if not os.path.isdir(args.matching_dir):
        log.error('Matching dir not found: %s', args.matching_dir)
        sys.exit(1)

    modalities = (
        [m.strip() for m in args.modality.split(',') if m.strip()]
        if args.modality else ALL_MODALITIES
    )
    unknown = [m for m in modalities if m not in ALL_MODALITIES]
    if unknown:
        log.error('Unknown modalities: %s (valid: %s)', unknown, ', '.join(ALL_MODALITIES))
        sys.exit(1)

    if args.top_mods:
        top_mods = [t.strip() for t in args.top_mods.split(',') if t.strip()]
    else:
        top_mods = derive_top_mods(modalities) or DEFAULT_TOP_MODS

    manifest_path = args.manifest or os.path.join(
        args.matching_dir, 'nii_reorganize_manifest.csv')

    log.info('=' * 70)
    log.info('reorganize_nii_by_viscode')
    log.info('=' * 70)
    log.info('NII root     : %s', args.nii_root)
    log.info('Matching dir : %s', args.matching_dir)
    log.info('Modalities   : %s', ', '.join(modalities))
    log.info('Top-mods     : %s', ', '.join(top_mods))
    log.info('Dry-run      : %s', args.dry_run)
    log.info('Clean-empty  : %s', args.clean_empty)
    log.info('Manifest     : %s', manifest_path)
    log.info('')

    # --- 1. Lookup 빌드 ---
    log.info('Building (PTID, IUID) → [(VISCODE_FIX, MODALITY), ...] lookup...')
    lookup, stats = build_lookup(args.matching_dir, modalities, log)
    log.info('Lookup size: %d unique (PTID, IUID) keys', len(lookup))
    log.info('')

    if not lookup:
        log.error('Empty lookup — nothing to do')
        sys.exit(2)

    # --- 2. IUID 디렉토리 스캔 (병렬, 결과를 리스트로 수집) ---
    log.info('Phase 1: scanning NII tree...')
    scan_start = _now()
    scanned_items: list[tuple[str, str, str]] = []
    for ptid, iuid, iuid_path in collect_iuid_dirs(
        args.nii_root, top_mods, log, ptid_workers=args.scan_workers
    ):
        scanned_items.append((ptid, iuid, iuid_path))
    scan_elapsed = _now() - scan_start
    log.info('Phase 1 done: %d IUID dirs in %.1fs', len(scanned_items), scan_elapsed)

    # --- 3. 병렬 move/copy ---
    log.info('Phase 2: processing (move/copy) with %d workers...', args.move_workers)
    counters = {
        'scanned': len(scanned_items),
        'matched': 0,
        'moved': 0,
        'copied': 0,
        'already_exists': 0,
        'unmatched': 0,
        'no_files': 0,
        'errors': 0,
    }
    per_modality_moved: dict[str, int] = defaultdict(int)
    manifest_rows: list[dict] = []

    # 매칭 없는 항목 먼저 카운트만
    matched_items: list[tuple[str, str, str, list[tuple[str, str]]]] = []
    for ptid, iuid, iuid_path in scanned_items:
        targets = lookup.get((ptid, iuid))
        if not targets:
            counters['unmatched'] += 1
            if args.verbose:
                log.debug('  UNMATCHED %s / I%s', ptid, iuid)
            continue
        counters['matched'] += 1
        matched_items.append((ptid, iuid, iuid_path, targets))

    log.info('  matched=%d unmatched=%d', counters['matched'], counters['unmatched'])

    # 병렬 실행
    process_start = _now()
    done = 0
    total = len(matched_items)

    def _submit_batch(executor):
        return {
            executor.submit(
                _process_iuid,
                ptid, iuid, iuid_path, targets,
                args.nii_root, args.dry_run,
            ): (ptid, iuid)
            for ptid, iuid, iuid_path, targets in matched_items
        }

    if args.move_workers <= 1:
        # 직렬 (디버그용)
        for ptid, iuid, iuid_path, targets in matched_items:
            rows, cstats = _process_iuid(
                ptid, iuid, iuid_path, targets, args.nii_root, args.dry_run)
            manifest_rows.extend(rows)
            for k, v in cstats.items():
                if k == 'per_mod':
                    for mk, mv in v.items():
                        per_modality_moved[mk] += mv
                else:
                    counters[k] += v
            done += 1
            if done % 500 == 0:
                rate = done / max(1.0, _now() - process_start)
                eta_s = (total - done) / rate if rate > 0 else 0
                log.info('  progress: done=%d/%d rate=%.1f/s eta=%.0fs',
                         done, total, rate, eta_s)
    else:
        with ThreadPoolExecutor(max_workers=args.move_workers) as ex:
            futures = _submit_batch(ex)
            for fut in as_completed(futures):
                try:
                    rows, cstats = fut.result()
                except Exception as exc:
                    counters['errors'] += 1
                    log.warning('  worker error: %s', exc)
                    continue
                manifest_rows.extend(rows)
                for k, v in cstats.items():
                    if k == 'per_mod':
                        for mk, mv in v.items():
                            per_modality_moved[mk] += mv
                    else:
                        counters[k] += v
                done += 1
                if done % 500 == 0:
                    rate = done / max(1.0, _now() - process_start)
                    eta_s = (total - done) / rate if rate > 0 else 0
                    log.info('  progress: done=%d/%d rate=%.1f/s eta=%.0fs',
                             done, total, rate, eta_s)

    log.info('Phase 2 done in %.1fs', _now() - process_start)

    # --- 3. Manifest CSV ---
    if manifest_rows:
        try:
            os.makedirs(os.path.dirname(manifest_path) or '.', exist_ok=True)
            pd.DataFrame(manifest_rows).to_csv(manifest_path, index=False)
            log.info('Manifest: %s (%d rows)', manifest_path, len(manifest_rows))
        except OSError as exc:
            log.error('Failed to write manifest %s: %s', manifest_path, exc)

    # --- 4. Summary ---
    log.info('')
    log.info('=' * 70)
    log.info('SUMMARY')
    log.info('=' * 70)
    for k in ('scanned', 'matched', 'moved', 'copied',
              'already_exists', 'unmatched', 'no_files', 'errors'):
        log.info('  %-15s %d', k, counters[k])
    log.info('')
    log.info('Per-modality moved+copied:')
    for mod in modalities:
        planned = stats.get(mod, 0)
        actual = per_modality_moved.get(mod, 0)
        log.info('  %-14s actual=%-6d planned=%d', mod, actual, planned)

    # --- 5. Clean empty ---
    if args.clean_empty and not args.dry_run:
        log.info('')
        log.info('Cleaning empty source directories...')
        for top in top_mods:
            remove_empty_dirs(os.path.join(args.nii_root, top), log)

    log.info('')
    log.info('COMPLETE')


if __name__ == '__main__':
    main()
