#!/usr/bin/env python3
"""
remap_proc_viscode.py — N4/VA/FastSurfer → ADNI_n4/ADNI_va/ADNI_seg 통합 + VISCODE 재매핑

소스 디렉토리(N4, VA, FastSurfer)의 VISCODE가 merged_adni4.csv 기반이라 133건 부정확.
T1_all.csv에서 올바른 VISCODE_FIX를 조회하여 대상 디렉토리에 올바른 VISCODE 폴더로 이동.
파일명 suffix도 reorganize_proc_t1.py 형식과 통일.

소스 구조:  {SOURCE}/{PTID}/{old_viscode}/T1/{protocol}/{date}/I{UID}/{file}
대상 구조:  ADNI_{target}/{PTID}/{VISCODE_FIX}/{renamed_file}  (flat)

Usage:
    python scripts/remap_proc_viscode.py --dry-run
    echo "asdzxc1234" | sudo -S python3 scripts/remap_proc_viscode.py --targets N4,VA,FastSurfer --clean-empty
"""
import os, sys, re, argparse, logging, shutil
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

DEFAULT_PROC = '/Volumes/nfs_storage/1_combined/ADNI_New/PROC/T1'
DEFAULT_OUT = '/Volumes/nfs_storage/1_combined/ADNI_New/ORIG/DEMO/ADNI_matching_v4'
LOG_FMT = '%(asctime)s | %(levelname)-5s | %(message)s'

IUID_RE = re.compile(r'^I(\d+)$')
PTID_RE = re.compile(r'^\d{3}_S_\d{4,5}$')

TARGET_MAP = {
    'N4':         {'dest': 'ADNI_n4',  'old_suffix': '_N4.nii.gz',       'new_suffix': '_n4.nii.gz'},
    'VA':         {'dest': 'ADNI_va',  'old_suffix': '_va.csv',          'new_suffix': '_va.csv'},
    'FastSurfer': {'dest': 'ADNI_seg', 'old_suffix': '_FastSurfer.mgz',  'new_suffix': '_seg.mgz'},
}


def build_uid_map(t1_all_csv):
    """T1_all.csv → {(ptid, i_uid_str): viscode_fix} 매핑 생성."""
    df = pd.read_csv(t1_all_csv, usecols=['PTID', 'I_T1', 'VISCODE_FIX'])
    uid_map = {}
    for _, r in df.iterrows():
        ptid = str(r['PTID'])
        viscode = str(r['VISCODE_FIX'])
        if viscode == 'error' or pd.isna(r['I_T1']):
            continue
        uid = str(int(r['I_T1']))
        uid_map[(ptid, uid)] = viscode
    return uid_map


def find_iuid_dirs(base_dir):
    """base_dir 아래에서 I{UID} 디렉토리를 재귀 탐색."""
    results = []
    if not os.path.isdir(base_dir):
        return results
    for root, dirs, _ in os.walk(base_dir):
        for d in dirs:
            m = IUID_RE.match(d)
            if m:
                results.append((m.group(1), os.path.join(root, d)))
    return results


def remove_empty_dirs(path, log):
    """빈 디렉토리를 재귀적으로 삭제 (bottom-up)."""
    removed = 0
    for root, dirs, files in os.walk(path, topdown=False):
        # .DS_Store 같은 시스템 파일만 있으면 빈 폴더 취급
        real_files = [f for f in files if not f.startswith('.')]
        if not dirs and not real_files:
            try:
                # .DS_Store 등 시스템 파일 먼저 삭제
                for f in files:
                    os.remove(os.path.join(root, f))
                os.rmdir(root)
                removed += 1
            except OSError:
                pass
    log.info('  Removed %d empty directories under %s', removed, path)
    return removed


def main():
    ap = argparse.ArgumentParser(description='N4/VA/FastSurfer → ADNI_n4/va/seg 통합 + VISCODE 재매핑')
    ap.add_argument('--proc-dir', default=DEFAULT_PROC,
                    help='PROC/T1 base directory (default: %s)' % DEFAULT_PROC)
    ap.add_argument('--t1-all', default=os.path.join(DEFAULT_OUT, 'T1_all.csv'),
                    help='T1_all.csv path')
    ap.add_argument('--targets', default='N4,VA,FastSurfer',
                    help='Comma-separated source directories (default: N4,VA,FastSurfer)')
    ap.add_argument('--dry-run', action='store_true',
                    help='Preview only, no files moved')
    ap.add_argument('--clean-empty', action='store_true',
                    help='Remove empty directories after moving')
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FMT)
    log = logging.getLogger(__name__)

    # 1. T1_all.csv → UID 매핑
    log.info('Loading T1_all.csv: %s', args.t1_all)
    uid_map = build_uid_map(args.t1_all)
    log.info('UID map entries: %d', len(uid_map))

    # 2. 대상 목록
    targets = [t.strip() for t in args.targets.split(',') if t.strip() in TARGET_MAP]
    if not targets:
        log.error('No valid targets specified. Choose from: %s', ', '.join(TARGET_MAP.keys()))
        sys.exit(1)

    manifest = []
    total_stats = {'moved': 0, 'skipped': 0, 'no_viscode': 0, 'error': 0}

    for source_name in targets:
        cfg = TARGET_MAP[source_name]
        source_root = os.path.join(args.proc_dir, source_name)
        dest_root = os.path.join(args.proc_dir, cfg['dest'])

        log.info('=== %s → %s ===', source_name, cfg['dest'])

        if not os.path.isdir(source_root):
            log.warning('  Source directory not found: %s', source_root)
            continue

        moved = skipped = no_viscode = err = 0

        # PTID 순회
        ptid_dirs = sorted([d for d in os.listdir(source_root) if PTID_RE.match(d)])
        log.info('  PTIDs in source: %d', len(ptid_dirs))

        for ptid in ptid_dirs:
            ptid_path = os.path.join(source_root, ptid)
            if not os.path.isdir(ptid_path):
                continue

            # viscode 폴더 순회 → I{UID} 디렉토리 탐색
            iuid_dirs = find_iuid_dirs(ptid_path)

            for uid, iuid_path in iuid_dirs:
                # T1_all.csv에서 올바른 VISCODE 조회
                correct_viscode = uid_map.get((ptid, uid))
                if not correct_viscode:
                    log.debug('  No VISCODE for %s / I%s', ptid, uid)
                    no_viscode += 1
                    continue

                # 해당 I{UID} 디렉토리 내 파일 처리
                if not os.path.isdir(iuid_path):
                    continue

                files = [f for f in os.listdir(iuid_path) if os.path.isfile(os.path.join(iuid_path, f))]
                target_files = [f for f in files if f.endswith(cfg['old_suffix'])]

                if not target_files:
                    # suffix가 없으면 skip (다른 파일이 남아있을 수 있음)
                    continue

                for fname in target_files:
                    old_path = os.path.join(iuid_path, fname)
                    new_fname = fname.replace(cfg['old_suffix'], cfg['new_suffix'])

                    dest_dir = os.path.join(dest_root, ptid, correct_viscode)
                    dest_path = os.path.join(dest_dir, new_fname)

                    # 이미 존재하면 skip
                    if os.path.exists(dest_path):
                        skipped += 1
                        continue

                    if args.dry_run:
                        log.info('  [DRY] %s → %s', old_path, dest_path)
                        moved += 1
                        manifest.append({
                            'PTID': ptid, 'I_UID': uid,
                            'VISCODE_FIX': correct_viscode,
                            'SOURCE': source_name, 'TARGET': cfg['dest'],
                            'OLD_PATH': old_path, 'NEW_PATH': dest_path,
                            'STATUS': 'dry_run'
                        })
                    else:
                        try:
                            os.makedirs(dest_dir, exist_ok=True)
                            shutil.move(old_path, dest_path)
                            moved += 1
                            manifest.append({
                                'PTID': ptid, 'I_UID': uid,
                                'VISCODE_FIX': correct_viscode,
                                'SOURCE': source_name, 'TARGET': cfg['dest'],
                                'OLD_PATH': old_path, 'NEW_PATH': dest_path,
                                'STATUS': 'moved'
                            })
                        except (OSError, shutil.Error) as exc:
                            log.warning('  MOVE FAIL: %s → %s (%s)', old_path, dest_path, exc)
                            err += 1
                            manifest.append({
                                'PTID': ptid, 'I_UID': uid,
                                'VISCODE_FIX': correct_viscode,
                                'SOURCE': source_name, 'TARGET': cfg['dest'],
                                'OLD_PATH': old_path, 'NEW_PATH': dest_path,
                                'STATUS': 'error: %s' % exc
                            })

        log.info('  DONE %s: moved=%d skipped=%d no_viscode=%d error=%d',
                 source_name, moved, skipped, no_viscode, err)
        total_stats['moved'] += moved
        total_stats['skipped'] += skipped
        total_stats['no_viscode'] += no_viscode
        total_stats['error'] += err

        # 빈 디렉토리 정리
        if args.clean_empty and not args.dry_run:
            remove_empty_dirs(source_root, log)

    # 3. Manifest CSV
    if manifest:
        mpath = os.path.join(args.proc_dir, 'remap_proc_manifest.csv')
        pd.DataFrame(manifest).to_csv(mpath, index=False)
        log.info('Manifest: %s (%d rows)', mpath, len(manifest))

    log.info('TOTAL: moved=%d skipped=%d no_viscode=%d error=%d',
             total_stats['moved'], total_stats['skipped'],
             total_stats['no_viscode'], total_stats['error'])
    log.info('COMPLETE')


if __name__ == '__main__':
    main()
