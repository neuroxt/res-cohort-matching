#!/usr/bin/env python3
"""
reorganize_proc_t1.py — PROC/T1 → {TARGET}/{PTID}/{VISCODE_FIX}/ rename(move) 재구성

T1_all.csv 기반 (NFS 순회 없음). 원본 파일을 VISCODE_FIX 기반 구조로 이동.

Usage:
    python scripts/reorganize_proc_t1.py --targets n4,seg,va
"""
import os, sys, re, argparse, logging, shutil
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

DEFAULT_PROC = '/Volumes/nfs_storage/1_combined/ADNI_New/PROC/T1'
DEFAULT_OUT = '/Volumes/nfs_storage/1_combined/ADNI_New/ORIG/DEMO/ADNI_matching_v4'
LOG_FMT = '%(asctime)s | %(levelname)-5s | %(message)s'

DCM_RE = re.compile(r'/DCM/([^/]+)/(\d{3}_S_\d{4,5})/([^/]+)/(\d{4}-\d{2}-\d{2}[^/]*)/I(\d+)/?$')


def parse_dcm(path):
    m = DCM_RE.search(str(path))
    if not m:
        return None
    return {'source': m.group(1), 'ptid': m.group(2), 'protocol': m.group(3),
            'date_dir': m.group(4), 'i_uid': m.group(5)}


def find_n4(iuid_path, i_uid):
    if not os.path.isdir(iuid_path):
        return None, None
    for f in os.listdir(iuid_path):
        if f.endswith('.nii.gz'):
            return os.path.join(iuid_path, f), f.replace('.nii.gz', '_I%s_n4.nii.gz' % i_uid)
    return None, None


def find_seg(iuid_path, i_uid):
    if not os.path.isdir(iuid_path):
        return None, None
    for d in os.listdir(iuid_path):
        sub = os.path.join(iuid_path, d)
        if os.path.isdir(sub):
            mgz = os.path.join(sub, 'mri', 'aparc.DKTatlas+aseg.deep.mgz')
            if os.path.isfile(mgz):
                return mgz, '%s_I%s_seg.mgz' % (d, i_uid)
    return None, None


def find_va(iuid_path, i_uid):
    if not os.path.isdir(iuid_path):
        return None, None
    for d in os.listdir(iuid_path):
        sub = os.path.join(iuid_path, d)
        if os.path.isdir(sub):
            csv_f = os.path.join(sub, 'va.csv')
            if os.path.isfile(csv_f):
                return csv_f, '%s_I%s_va.csv' % (d, i_uid)
    return None, None


FIND = {'ADNI_n4': find_n4, 'ADNI_seg': find_seg, 'ADNI_va': find_va}
TMAP = {'n4': 'ADNI_n4', 'seg': 'ADNI_seg', 'va': 'ADNI_va'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--proc-dir', default=DEFAULT_PROC)
    ap.add_argument('--t1-all', default=os.path.join(DEFAULT_OUT, 'T1_all.csv'))
    ap.add_argument('--t1-unique', default=os.path.join(DEFAULT_OUT, 'T1_unique.csv'))
    ap.add_argument('--targets', default='n4,seg,va')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--clean-empty', action='store_true',
                    help='Remove empty dirs after move (protocol/date/IUID)')
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FMT)

    # 1. CSV 로드
    df = pd.read_csv(args.t1_all, usecols=['PTID', 'I_T1', 'VISCODE_FIX', 'T1_image_path'])
    entries = []
    for _, r in df.iterrows():
        p = parse_dcm(r['T1_image_path'])
        if p:
            p['viscode'] = str(r['VISCODE_FIX'])
            entries.append(p)
    logging.info('Entries: %d' % len(entries))

    udf = pd.read_csv(args.t1_unique, usecols=['PTID', 'I_T1', 'VISCODE_FIX'])
    sel = {(str(r['PTID']), str(r['VISCODE_FIX']), str(int(r['I_T1']))) for _, r in udf.iterrows()}
    logging.info('Selected: %d' % len(sel))

    targets = [TMAP[t.strip()] for t in args.targets.split(',') if t.strip() in TMAP]
    manifest = []

    for tgt in targets:
        logging.info('=== %s ===' % tgt)
        fn = FIND[tgt]
        out = tgt
        ok = skip = nope = err = move_fail = 0

        for i, e in enumerate(entries):
            vis = e['viscode']
            if vis == 'error':
                err += 1
                continue
            try:
                # B: 이미 이동된 파일 체크 (이전 실행에서 move 완료된 경우)
                new_dir = os.path.join(args.proc_dir, out, e['ptid'], vis)
                if os.path.isdir(new_dir):
                    already = [f for f in os.listdir(new_dir) if ('I%s' % e['i_uid']) in f]
                    if already:
                        skip += 1
                        continue

                iuid_path = os.path.join(args.proc_dir, tgt, e['ptid'], e['protocol'],
                                         e['date_dir'], 'I%s' % e['i_uid'])
                old, newf = fn(iuid_path, e['i_uid'])
                if old is None:
                    nope += 1
                    continue

                new_path = os.path.join(new_dir, newf)

                if os.path.exists(new_path) or os.path.islink(new_path):
                    skip += 1
                    continue

                is_sel = (e['ptid'], vis, e['i_uid']) in sel

                if not args.dry_run:
                    os.makedirs(new_dir, exist_ok=True)
                    try:
                        shutil.move(old, new_path)
                    except (FileNotFoundError, PermissionError, OSError) as exc:
                        logging.warning('  MOVE FAIL: %s (%s)' % (os.path.basename(old), exc))
                        move_fail += 1
                        continue

                ok += 1
                manifest.append({'PTID': e['ptid'], 'VISCODE_FIX': vis, 'I_UID': e['i_uid'],
                                 'PROTOCOL': e['protocol'], 'DATE': e['date_dir'][:10],
                                 'TARGET': tgt, 'OLD_PATH': old, 'NEW_PATH': new_path,
                                 'IS_SELECTED': is_sel})
            except Exception as exc:
                nope += 1

            if (i + 1) % 1000 == 0:
                logging.info('  %d/%d ok=%d skip=%d nope=%d fail=%d' % (i+1, len(entries), ok, skip, nope, move_fail))

        logging.info('  DONE %s: ok=%d skip=%d nope=%d err=%d move_fail=%d' % (tgt, ok, skip, nope, err, move_fail))

    if manifest:
        mpath = os.path.join(args.proc_dir, 'proc_t1_mapping.csv')
        pd.DataFrame(manifest).to_csv(mpath, index=False)
        logging.info('Manifest: %s (%d rows)' % (mpath, len(manifest)))

    # clean-empty: bottom-up 빈 디렉토리 삭제
    if args.clean_empty:
        for tgt in targets:
            base = os.path.join(args.proc_dir, tgt)
            removed = 0
            for dirpath, dirnames, filenames in os.walk(base, topdown=False):
                if dirpath == base:
                    continue
                # os.walk의 dirnames는 삭제 후 갱신 안됨 → os.listdir로 재확인
                try:
                    if not os.listdir(dirpath):
                        os.rmdir(dirpath)
                        removed += 1
                except OSError:
                    pass
            logging.info('  %s: removed %d empty dirs' % (tgt, removed))

    logging.info('COMPLETE')


if __name__ == '__main__':
    main()
