# A4 Output CSV Redesign Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A4 파이프라인에 BASELINE.csv, MMSE/CDR longitudinal, imaging_availability 4개 CSV 출력 추가

**Architecture:** pipeline.py에 3개 신규 함수 추가, cli.py에 2개 CLI 옵션 추가. clinical.py 변경 없음 — 기존 build_clinical_table(), build_longitudinal_cognitive() 재사용.

**Tech Stack:** Python, pandas, existing A4 pipeline infrastructure

**Spec:** `docs/superpowers/specs/2026-03-18-a4-output-csv-redesign.md`

---

## Task 1: `build_baseline_csv()` — BASELINE.csv 생성 함수

**Files:**
- Modify: `src/a4/pipeline.py` (함수 추가)

- [ ] **Step 1: `build_baseline_csv()` 함수 작성**

`pipeline.py` 끝에 추가 (run_pipeline 위, 또는 build_session_merged 뒤):

```python
def build_baseline_csv(clinical: 'pd.DataFrame',
                       long_cognitive: 'pd.DataFrame',
                       session_index: 'pd.DataFrame',
                       inventory: dict,
                       output_dir: str,
                       output_filename: str = 'BASELINE.csv') -> str:
    """피험자당 1행 baseline CSV 생성.

    V1~V6을 하나의 baseline으로 통합:
    - Demographics/Amyloid/VMRI/TAU: clinical_table (이미 BID-level)
    - MMSE/CDR: V6 (SESSION_CODE='006') from long_cognitive
    - PTAGE: session_index V6 기준
    - NII_PATH: inventory에서 V2(FBP), V4(T1/FLAIR/FTP) 추출
      LEARN은 V6에서 MRI 추출

    Args:
        clinical: build_clinical_table() 결과 (BID 인덱스)
        long_cognitive: build_longitudinal_cognitive() 결과
        session_index: build_session_index() 결과
        inventory: build_inventory() 결과
        output_dir: 출력 디렉토리
        output_filename: 출력 파일명

    Returns:
        저장된 CSV 경로
    """
    logging.info('-------------------- BASELINE.csv --------------------')

    base = clinical.copy()
    logging.info('Clinical table: %d BIDs' % len(base))

    # 1. V6 인지점수 (MMSE, CDGLOBAL, CDRSB)
    if long_cognitive is not None and not long_cognitive.empty:
        v6_cog = long_cognitive.xs('006', level='SESSION_CODE', drop_level=True)
        v6_cog = v6_cog[~v6_cog.index.duplicated(keep='first')]
        for col in ['MMSE', 'CDGLOBAL', 'CDRSB']:
            if col in v6_cog.columns:
                base[col] = v6_cog[col]
        logging.info('V6 cognitive: %d BIDs matched' % len(v6_cog))

    # 2. V6 PTAGE (session_index에서 추출)
    if session_index is not None and not session_index.empty:
        try:
            v6_age = session_index.xs('006', level='SESSION_CODE', drop_level=True)
            v6_age = v6_age[~v6_age.index.duplicated(keep='first')]
            if 'PTAGE' in v6_age.columns:
                base['PTAGE'] = v6_age['PTAGE']
                logging.info('V6 PTAGE: %d BIDs matched' % v6_age['PTAGE'].notna().sum())
        except KeyError:
            logging.warning('SESSION_CODE 006 not found in session_index')

    # 3. Baseline NII paths from inventory
    by_modality = inventory.get('by_modality', {})

    # LEARN BIDs (MRI at V6 instead of V4)
    learn_bids = set()
    if 'LRNFLGSNM' in base.columns:
        learn_bids = set(base[base['LRNFLGSNM'].str.upper() == 'Y'].index)
    if 'Research_Group' in base.columns:
        learn_bids |= set(base[base['Research_Group'].str.contains('LEARN', case=False, na=False)].index)

    # Helper: extract NII path for a BID at a specific session
    def _get_nii_path(mod_key, bid, session):
        mod_data = by_modality.get(mod_key, {})
        recs = mod_data.get(bid, [])
        for rec in recs:
            if rec.get('session') == session:
                return rec.get('nii_path', '')
        return ''

    for bid in base.index:
        is_learn = bid in learn_bids
        mri_session = '006' if is_learn else '004'

        for mod, session in [('T1', mri_session), ('FLAIR', mri_session),
                             ('FTP', mri_session), ('FBP', '002')]:
            col = '%s_NII_PATH' % mod
            path = _get_nii_path(mod, bid, session)
            if path:
                base.at[bid, col] = path

    # NII_PATH 컬럼이 없으면 빈 문자열로 생성
    for mod in ['T1', 'FLAIR', 'FTP', 'FBP']:
        col = '%s_NII_PATH' % mod
        if col not in base.columns:
            base[col] = ''

    nii_filled = {mod: base['%s_NII_PATH' % mod].astype(str).ne('').sum()
                  for mod in ['T1', 'FLAIR', 'FTP', 'FBP']}
    logging.info('Baseline NII paths: %s' % nii_filled)

    # 4. 컬럼 정렬 + 저장
    base = _reorder_columns(base)
    base.sort_index(inplace=True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    base.to_csv(output_path)
    logging.info('BASELINE: %d rows, %d cols → %s' % (
        len(base), len(base.columns), output_path))
    logging.info('-----------------------------------------------------\n')

    return output_path
```

- [ ] **Step 2: import 확인**

`pipeline.py` 상단의 기존 import만으로 충분 (os, csv, logging, pd, MODALITY_CONFIG, MERGE_EXCLUDE). 추가 import 불필요.

- [ ] **Step 3: 커밋**

```bash
git add src/a4/pipeline.py
git commit -m "feat(a4): add build_baseline_csv() for per-subject baseline CSV"
```

---

## Task 2: `build_longitudinal_csvs()` — MMSE/CDR longitudinal CSV 생성

**Files:**
- Modify: `src/a4/pipeline.py` (함수 추가)

- [ ] **Step 1: `build_longitudinal_csvs()` 함수 작성**

`pipeline.py`에 추가:

```python
def build_longitudinal_csvs(session_index: 'pd.DataFrame',
                            long_cognitive: 'pd.DataFrame',
                            output_dir: str) -> list:
    """MMSE_longitudinal.csv, CDR_longitudinal.csv 생성.

    long_cognitive (BID+SESSION_CODE 인덱스)에 session_index의
    DAYS_CONSENT, PTAGE를 조인하여 저장.

    Args:
        session_index: build_session_index() 결과
        long_cognitive: build_longitudinal_cognitive() 결과
        output_dir: 출력 디렉토리

    Returns:
        저장된 CSV 경로 리스트
    """
    logging.info('-------------------- Longitudinal CSVs --------------------')
    saved = []

    if long_cognitive is None or long_cognitive.empty:
        logging.warning('No longitudinal cognitive data — skipping')
        return saved

    # session_index에서 DAYS_CONSENT, PTAGE 조인
    time_cols = []
    if session_index is not None and not session_index.empty:
        for col in ['DAYS_CONSENT', 'PTAGE']:
            if col in session_index.columns:
                time_cols.append(col)

    os.makedirs(output_dir, exist_ok=True)

    # MMSE
    if 'MMSE' in long_cognitive.columns:
        mmse = long_cognitive[['MMSE']].dropna(subset=['MMSE']).copy()
        if time_cols:
            mmse = mmse.join(session_index[time_cols], how='left')
        # 컬럼 순서: DAYS_CONSENT, PTAGE, MMSE
        col_order = [c for c in ['DAYS_CONSENT', 'PTAGE', 'MMSE'] if c in mmse.columns]
        mmse = mmse[col_order].sort_index()

        path = os.path.join(output_dir, 'MMSE_longitudinal.csv')
        mmse.to_csv(path)
        logging.info('MMSE_longitudinal: %d rows, %d BIDs → %s' % (
            len(mmse), mmse.index.get_level_values('BID').nunique(), path))
        saved.append(path)

    # CDR
    cdr_cols = [c for c in ['CDGLOBAL', 'CDRSB'] if c in long_cognitive.columns]
    if cdr_cols:
        cdr = long_cognitive[cdr_cols].dropna(subset=cdr_cols, how='all').copy()
        if time_cols:
            cdr = cdr.join(session_index[time_cols], how='left')
        col_order = [c for c in ['DAYS_CONSENT', 'PTAGE'] + cdr_cols if c in cdr.columns]
        cdr = cdr[col_order].sort_index()

        path = os.path.join(output_dir, 'CDR_longitudinal.csv')
        cdr.to_csv(path)
        logging.info('CDR_longitudinal: %d rows, %d BIDs → %s' % (
            len(cdr), cdr.index.get_level_values('BID').nunique(), path))
        saved.append(path)

    logging.info('-----------------------------------------------------\n')
    return saved
```

- [ ] **Step 2: 커밋**

```bash
git add src/a4/pipeline.py
git commit -m "feat(a4): add build_longitudinal_csvs() for MMSE/CDR long-format"
```

---

## Task 3: `build_imaging_availability()` — 영상 가용성 boolean CSV

**Files:**
- Modify: `src/a4/pipeline.py` (함수 추가)

- [ ] **Step 1: `build_imaging_availability()` 함수 작성**

```python
def build_imaging_availability(inventory: dict,
                               session_index: 'pd.DataFrame',
                               output_dir: str,
                               output_filename: str = 'imaging_availability.csv') -> str:
    """세션별 모달리티 유무 boolean CSV 생성.

    Args:
        inventory: build_inventory() 결과
        session_index: build_session_index() 결과 (DAYS_CONSENT 조인용)
        output_dir: 출력 디렉토리
        output_filename: 출력 파일명

    Returns:
        저장된 CSV 경로
    """
    logging.info('-------------------- Imaging Availability --------------------')

    by_bid_session = inventory.get('by_bid_session', {})
    if not by_bid_session:
        logging.warning('No by_bid_session in inventory — skipping')
        return ''

    # 모달리티 목록 (DWI 등 MERGE_EXCLUDE 제외)
    exclude_set = {m.upper() for m in MERGE_EXCLUDE}
    mod_list = [m for m in sorted(MODALITY_CONFIG.keys()) if m.upper() not in exclude_set]

    records = []
    for bid, sessions in by_bid_session.items():
        for session, mods_in_session in sessions.items():
            row = {'BID': bid, 'SESSION_CODE': session}
            for mod in mod_list:
                row[mod] = 1 if mod in mods_in_session else 0
            records.append(row)

    if not records:
        logging.warning('No imaging records — skipping')
        return ''

    df = pd.DataFrame(records)
    df.set_index(['BID', 'SESSION_CODE'], inplace=True)

    # DAYS_CONSENT 조인
    if session_index is not None and not session_index.empty:
        for col in ['DAYS_CONSENT']:
            if col in session_index.columns:
                df = df.join(session_index[[col]], how='left')
                # DAYS_CONSENT를 첫 번째 컬럼으로
                cols = [col] + [c for c in df.columns if c != col]
                df = df[cols]

    df.sort_index(inplace=True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    df.to_csv(output_path)

    n_sessions = len(df)
    n_bids = df.index.get_level_values('BID').nunique()
    mod_sums = {m: df[m].sum() for m in mod_list if m in df.columns}
    logging.info('Imaging availability: %d sessions, %d BIDs' % (n_sessions, n_bids))
    logging.info('  Modality counts: %s' % mod_sums)
    logging.info('  Output: %s' % output_path)
    logging.info('-----------------------------------------------------\n')

    return output_path
```

- [ ] **Step 2: 커밋**

```bash
git add src/a4/pipeline.py
git commit -m "feat(a4): add build_imaging_availability() for modality boolean CSV"
```

---

## Task 4: `run_pipeline()` 통합 + CLI 옵션

**Files:**
- Modify: `src/a4/pipeline.py` — `run_pipeline()` 에 신규 함수 호출 추가
- Modify: `src/a4/cli.py` — `--baseline-only`, `--longitudinal-only` 옵션 + `main()` 호출

- [ ] **Step 1: `run_pipeline()` 에 신규 단계 추가**

`run_pipeline()` 끝에 (merge 이후) 추가:

```python
    # -- 신규 CSV 생성 (session_index 있을 때만) --
    if session_index is not None and not session_index.empty:
        # BASELINE.csv
        build_baseline_csv(clinical, long_cognitive, session_index,
                           inventory, output_dir)

        # MMSE/CDR longitudinal
        build_longitudinal_csvs(session_index, long_cognitive, output_dir)

        # Imaging availability
        build_imaging_availability(inventory, session_index, output_dir)
```

- [ ] **Step 2: `cli.py` — mode group에 신규 옵션 추가**

`parse_args()`의 `mode = parser.add_mutually_exclusive_group()` 블록에 추가:

```python
    mode.add_argument('--baseline-only', action='store_true',
                      help='BASELINE.csv만 재생성')
    mode.add_argument('--longitudinal-only', action='store_true',
                      help='MMSE/CDR longitudinal CSV만 재생성')
```

- [ ] **Step 3: `cli.py` — `main()` 에 신규 모드 핸들러 추가**

`--clinical-only` 블록 아래, 전체 파이프라인 블록 위에 추가:

```python
    # --baseline-only
    if args.baseline_only:
        from .pipeline import build_baseline_csv, build_longitudinal_csvs, build_imaging_availability
        inventory = run_inventory_step(args.output_dir, nfs_base=args.nii_base)
        clinical = run_clinical_step(
            metadata_dir=args.metadata_dir,
            clinical_dir=args.clinical_dir,
            include_screen_fail=args.include_screen_fail,
        )
        if clinical.empty:
            logging.error('Clinical table is empty — aborting')
            sys.exit(1)
        long_cognitive = build_longitudinal_cognitive(clinical_dir=args.clinical_dir)
        session_index = build_session_index(
            clinical_dir=args.clinical_dir,
            metadata_dir=args.metadata_dir,
            allowed_bids=set(clinical.index),
        )
        build_baseline_csv(clinical, long_cognitive, session_index,
                           inventory, args.output_dir)
        return

    # --longitudinal-only
    if args.longitudinal_only:
        from .pipeline import build_longitudinal_csvs, build_imaging_availability
        inventory = run_inventory_step(args.output_dir, nfs_base=args.nii_base)
        long_cognitive = build_longitudinal_cognitive(clinical_dir=args.clinical_dir)
        session_index = build_session_index(
            clinical_dir=args.clinical_dir,
            metadata_dir=args.metadata_dir,
        )
        build_longitudinal_csvs(session_index, long_cognitive, args.output_dir)
        build_imaging_availability(inventory, session_index, args.output_dir)
        return
```

- [ ] **Step 4: `cli.py` import 업데이트**

L32 변경:

```python
# Before:
from .pipeline import run_pipeline, unique_csv_merge

# After:
from .pipeline import (
    run_pipeline, unique_csv_merge,
    build_baseline_csv, build_longitudinal_csvs, build_imaging_availability,
)
```

- [ ] **Step 5: 커밋**

```bash
git add src/a4/pipeline.py src/a4/cli.py
git commit -m "feat(a4): integrate baseline/longitudinal/availability into pipeline + CLI"
```

---

## Task 5: 검증 (NFS 실행)

- [ ] **Step 1: 전체 파이프라인 실행**

```bash
PYTHONPATH=src python -m a4 --output-dir /tmp/a4_test \
  --nii-base /Volumes/nfs_storage-1/A4/ORIG/NII \
  --metadata-dir /Volumes/nfs_storage-1/A4/ORIG/metadata \
  --clinical-dir /Volumes/nfs_storage-1/A4/ORIG/DEMO/Clinical \
  --overwrite
```

- [ ] **Step 2: 출력 파일 검증**

```bash
# 파일 존재 확인
ls -lh /tmp/a4_test/{BASELINE,MMSE_longitudinal,CDR_longitudinal,imaging_availability}.csv

# 행/열 수 확인
python -c "
import pandas as pd
for f in ['BASELINE', 'MMSE_longitudinal', 'CDR_longitudinal', 'imaging_availability']:
    df = pd.read_csv('/tmp/a4_test/%s.csv' % f)
    print('%s: %d rows, %d cols' % (f, len(df), len(df.columns)))
"
```

기대값:
- BASELINE: ~1,890행 (amyloidNE 제외)
- MMSE_longitudinal: ~26K행
- CDR_longitudinal: ~15K행
- imaging_availability: ~11K행

- [ ] **Step 3: BASELINE.csv 데이터 정합성 확인**

```bash
python -c "
import pandas as pd
bl = pd.read_csv('/tmp/a4_test/BASELINE.csv')
print('MMSE non-null:', bl['MMSE'].notna().sum())
print('T1_NII_PATH non-empty:', (bl['T1_NII_PATH'].astype(str) != '').sum())
print('FBP_NII_PATH non-empty:', (bl['FBP_NII_PATH'].astype(str) != '').sum())
print('Columns:', len(bl.columns))
"
```

- [ ] **Step 4: 최종 커밋**

검증 통과 후 NFS 출력 디렉토리에 실행하여 최종 결과 생성.
