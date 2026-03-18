"""
pipeline.py — A4/LEARN 메인 파이프라인

NII inventory + clinical table → 모달리티별 CSV → MERGED.csv

ADNI 매칭과의 핵심 차이:
- 날짜 매칭 불필요 (NII session_code로 직접 조인)
- regex 분류 불필요 (폴더명 = 모달리티)
- 시리즈 선택 불필요 (모달리티별 1개 primary .nii.gz)
"""

import os
import csv
import logging
from glob import glob

import pandas as pd

from .config import MODALITY_CONFIG, MERGE_EXCLUDE


def build_modality_csv(modality: str,
                       inventory: dict,
                       clinical: pd.DataFrame,
                       output_dir: str,
                       session_ages: pd.DataFrame = None,
                       long_cognitive: pd.DataFrame = None,
                       overwrite: bool = False) -> str:
    """단일 모달리티에 대해 inventory + clinical 조인 → {MOD}_unique.csv 저장.

    Args:
        modality: 모달리티 키 (e.g., 'T1', 'FBP')
        inventory: build_inventory() 결과
        clinical: build_clinical_table() 결과 (BID 인덱스)
        output_dir: 출력 디렉토리
        session_ages: build_session_age_table() 결과 (BID+SESSION_CODE 인덱스)
        long_cognitive: build_longitudinal_cognitive() 결과 (BID+SESSION_CODE 인덱스)
        overwrite: 기존 파일 덮어쓰기

    Returns:
        저장된 CSV 경로 (레코드 없으면 '')
    """
    output_path = os.path.join(output_dir, '%s_unique.csv' % modality)
    if os.path.isfile(output_path) and not overwrite:
        logging.info('%s: already exists, skipping (use --overwrite)' % modality)
        return output_path

    mod_config = MODALITY_CONFIG.get(modality)
    if mod_config is None:
        logging.warning('Unknown modality: %s' % modality)
        return ''

    by_modality = inventory.get('by_modality', {})
    mod_data = by_modality.get(modality, {})

    if not mod_data:
        logging.warning('%s: no records in inventory' % modality)
        return ''

    # 레코드 수집
    records = []
    for bid, image_list in mod_data.items():
        for rec in image_list:
            row = {
                'BID': bid,
                'SESSION_CODE': rec['session'],
                'MODALITY': modality,
                'NII_PATH': rec.get('nii_path', ''),
            }

            # JSON sidecar 메타데이터
            json_meta = rec.get('json_meta', {})
            for field_name, value in json_meta.items():
                col = 'protocol/%s/%s' % (modality, field_name)
                row[col] = value

            # Clinical 데이터 조인 (BID 기준)
            if bid in clinical.index:
                clin_row = clinical.loc[bid]
                if isinstance(clin_row, pd.DataFrame):
                    clin_row = clin_row.iloc[0]
                for col_name, val in clin_row.items():
                    if pd.notna(val):
                        row[col_name] = val
                    else:
                        row[col_name] = ''

            records.append(row)

    if not records:
        logging.warning('%s: no records after processing' % modality)
        return ''

    df = pd.DataFrame(records)
    df.set_index(['BID', 'SESSION_CODE'], inplace=True)

    # 세션별 나이 덮어쓰기 (static PTAGE → dynamic)
    if session_ages is not None and not session_ages.empty and 'PTAGE' in df.columns:
        matched = session_ages.reindex(df.index)
        mask = matched['PTAGE'].notna()
        df.loc[mask, 'PTAGE'] = matched.loc[mask, 'PTAGE']
        logging.info('%s: updated PTAGE for %d / %d rows' % (modality, mask.sum(), len(df)))

    # Longitudinal cognitive 조인
    if long_cognitive is not None and not long_cognitive.empty:
        df = df.join(long_cognitive, how='left')
        for col in ['MMSE', 'CDGLOBAL', 'CDRSB']:
            if col in df.columns:
                filled = df[col].notna().sum()
                logging.info('%s: %s filled for %d / %d rows' % (modality, col, filled, len(df)))

    # 중복 인덱스 제거 (첫 번째 유지)
    n_before = len(df)
    df = df[~df.index.duplicated(keep='first')]
    if len(df) < n_before:
        logging.warning('%s: dropped %d duplicate BID+SESSION rows' % (modality, n_before - len(df)))

    df.sort_index(inplace=True)

    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(output_path, quoting=csv.QUOTE_NONNUMERIC)
    logging.info('%s: saved %d rows → %s' % (modality, len(df), output_path))

    return output_path


def _reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """MERGED.csv 컬럼을 논리적 그룹 순서로 재배치.

    순서: ID/Visit → Demographics → Amyloid → Clinical → pTau217
         → MRI protocols → PET protocols → VMRI → Tau SUVR → 나머지
    """
    cols = list(df.columns)
    used = set()

    def _take(names):
        out = [c for c in names if c in cols and c not in used]
        used.update(out)
        return out

    def _take_prefix(prefix):
        out = [c for c in cols if c.startswith(prefix) and c not in used]
        used.update(out)
        return out

    ordered = []

    # 1. Timing
    ordered += _take(['DAYS_CONSENT'])

    # 2. Demographics
    ordered += _take(['PTGENDER', 'PTAGE', 'PTEDUCAT', 'APOEGN',
                       'AGEYR', 'LRNFLGSNM', 'Research_Group'])

    # 3. Amyloid
    ordered += _take(['AMY_STATUS_bl', 'AMY_SUVR_bl', 'AMY_SUVR_CER_bl', 'AMY_CENTILOID_bl'])

    # 4. Clinical (baseline + longitudinal)
    ordered += _take(['MMSE_bl', 'MMSE', 'CDGLOBAL_bl', 'CDGLOBAL', 'CDRSB_bl', 'CDRSB'])

    # 5. pTau217
    ordered += _take_prefix('PTAU217_')

    # 5b. Roche plasma biomarkers
    ordered += _take_prefix('ROCHE_')

    # 6. Modality / path (session-centric or legacy)
    ordered += _take(['MODALITIES'])          # session-centric
    ordered += _take(['MODALITY', 'NII_PATH'])  # legacy per-modality CSV

    # 7. MRI: per-modality NII path + protocols
    for mod in ('T1', 'FLAIR', 'T2_SE', 'T2_STAR', 'FMRI_REST', 'B0CD'):
        ordered += _take(['%s_NII_PATH' % mod])
        ordered += _take_prefix('protocol/%s/' % mod)

    # 8. PET: per-modality NII path + protocols
    for mod in ('FBP', 'FTP'):
        ordered += _take(['%s_NII_PATH' % mod])
        ordered += _take_prefix('protocol/%s/' % mod)

    # 9. VMRI
    ordered += _take_prefix('VMRI_')

    # 10. Tau SUVR
    ordered += _take_prefix('TAU_')

    # 11. Remainder
    ordered += [c for c in cols if c not in used]

    return df[ordered]


def build_session_merged(session_index: 'pd.DataFrame',
                         clinical: 'pd.DataFrame',
                         long_cognitive: 'pd.DataFrame',
                         inventory: dict,
                         output_dir: str,
                         exclude_modalities: list = None,
                         output_filename: str = 'MERGED.csv') -> str:
    """Session-centric MERGED.csv 빌더.

    SV.csv 전체 세션을 기준으로 clinical/imaging을 left-join.
    기존 unique_csv_merge()가 이미징 세션만 포함하는 것과 달리,
    인지 평가만 있는 세션도 포함됨.

    Args:
        session_index: build_session_index() 결과 (BID+SESSION_CODE 인덱스)
        clinical: build_clinical_table() 결과 (BID 인덱스)
        long_cognitive: build_longitudinal_cognitive() 결과 (BID+SESSION_CODE 인덱스)
        inventory: build_inventory() 결과
        output_dir: 출력 디렉토리
        exclude_modalities: 제외할 모달리티
        output_filename: 출력 파일명

    Returns:
        저장된 CSV 경로
    """
    logging.info('-------------------- Session-centric MERGED --------------------')

    # 1. session_index 복사 → base
    base = session_index.copy()
    logging.info('Session index: %d rows' % len(base))

    # 2. BID-level clinical left-join (PTAGE 제외 — session_index의 세션별 PTAGE 우선)
    if not clinical.empty:
        clin_cols = [c for c in clinical.columns if c != 'PTAGE']
        if clin_cols:
            base = base.join(clinical[clin_cols], on='BID', how='left')
        logging.info('After clinical join: %d cols' % len(base.columns))

    # 3. Longitudinal cognitive left-join
    if long_cognitive is not None and not long_cognitive.empty:
        base = base.join(long_cognitive, how='left')
        for col in ['MMSE', 'CDGLOBAL', 'CDRSB']:
            if col in base.columns:
                filled = base[col].notna().sum()
                logging.info('  %s filled: %d / %d rows' % (col, filled, len(base)))

    # 4. 모달리티별 이미징 데이터 left-join
    by_modality = inventory.get('by_modality', {})
    exclude_set = {m.upper() for m in (exclude_modalities or [])}
    modalities_joined = []

    for mod_key in sorted(MODALITY_CONFIG.keys()):
        if mod_key.upper() in exclude_set:
            continue
        mod_data = by_modality.get(mod_key, {})
        if not mod_data:
            continue

        # inventory dict → DataFrame
        records = []
        for bid, image_list in mod_data.items():
            for rec in image_list:
                row = {
                    'BID': bid,
                    'SESSION_CODE': rec['session'],
                    '%s_NII_PATH' % mod_key: rec.get('nii_path', ''),
                }
                # JSON sidecar 메타데이터
                json_meta = rec.get('json_meta', {})
                for field_name, value in json_meta.items():
                    row['protocol/%s/%s' % (mod_key, field_name)] = value
                records.append(row)

        if not records:
            continue

        mod_df = pd.DataFrame(records)
        mod_df = mod_df.drop_duplicates(subset=['BID', 'SESSION_CODE'], keep='first')
        mod_df.set_index(['BID', 'SESSION_CODE'], inplace=True)

        base = base.join(mod_df, how='left')
        modalities_joined.append(mod_key)
        n_filled = base['%s_NII_PATH' % mod_key].notna().sum()
        logging.info('  %s joined: %d sessions with imaging' % (mod_key, n_filled))

    # 5. MODALITIES 컬럼 생성 (해당 세션에 존재하는 모달리티 comma-separated)
    nii_cols = ['%s_NII_PATH' % m for m in modalities_joined if '%s_NII_PATH' % m in base.columns]
    if nii_cols:
        def _modalities_str(row):
            mods = []
            for m in modalities_joined:
                col = '%s_NII_PATH' % m
                if col in row.index and pd.notna(row[col]) and row[col] != '':
                    mods.append(m)
            return ','.join(mods) if mods else ''
        base['MODALITIES'] = base.apply(_modalities_str, axis=1)
        # 빈 문자열 → NaN (CSV 정합성)
        base['MODALITIES'] = base['MODALITIES'].replace('', pd.NA)

    # 6. 컬럼 정렬 + 저장
    base = _reorder_columns(base)
    base.sort_index(inplace=True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    base.to_csv(output_path)
    logging.info('Session-centric MERGED: %d rows, %d cols → %s' % (
        len(base), len(base.columns), output_path))
    logging.info('-----------------------------------------------------\n')

    return output_path


def unique_csv_merge(output_directory: str,
                     output_filename: str = 'MERGED.csv',
                     exclude_modalities: list = None):
    """*_unique.csv 파일들을 BID+SESSION_CODE 기준으로 병합.

    ADNI merge.py와 동일 로직이나 인덱스 키가 BID+SESSION_CODE.

    Args:
        output_directory: *_unique.csv 파일이 있는 디렉토리
        output_filename: 출력 파일명 (기본: MERGED.csv)
        exclude_modalities: 제외할 모달리티 (e.g., ['DWI'])
    """
    logging.info('-------------------- A4 Unique CSV Merge --------------------')
    output_path = os.path.join(output_directory, output_filename)

    flist = sorted(glob(os.path.join(output_directory, '*_unique.csv')))

    # 제외 모달리티 필터링
    if exclude_modalities:
        exclude_set = {m.upper() for m in exclude_modalities}
        flist = [f for f in flist if
                 os.path.basename(f).replace('_unique.csv', '').upper() not in exclude_set]

    if not flist:
        logging.warning('No *_unique.csv files found in %s' % output_directory)
        return

    # 로드 + 행 수 기준 정렬 (중복 인덱스 제거)
    df_list = []
    for f in flist:
        logging.info('input csv: %s' % f)
        df = pd.read_csv(f, low_memory=False).set_index(['BID', 'SESSION_CODE'])
        n_before = len(df)
        df = df[~df.index.duplicated(keep='first')]
        if len(df) < n_before:
            logging.warning('  dropped %d duplicate index rows in %s' % (
                n_before - len(df), os.path.basename(f)))
        df_list.append(df)
    df_meta = pd.DataFrame(dict(df=df_list, path=flist), index=[len(e) for e in df_list])
    df_meta.sort_index(ascending=False, inplace=True)

    # 가장 큰 CSV로 초기화
    init_df = df_meta.df.iloc[0]
    logging.info('')
    logging.info('init csv: %s, current shape: %s' % (df_meta.path.iloc[0], str(init_df.shape)))

    # 나머지 CSV 순차 병합
    for i, row in df_meta.iloc[1:].iterrows():
        drop_columns = list(set(init_df.columns).intersection(set(row.df.columns)))
        new_index = row.df.index.difference(init_df.index).unique()
        init_df = init_df.join(row.df.drop(drop_columns, axis=1), how='outer')
        init_df = init_df[~init_df.index.duplicated(keep='first')]
        if len(new_index) > 0:
            init_df.loc[new_index] = row.df.loc[new_index]
        logging.info('merge csv: %s, current shape: %s' % (row.path, str(init_df.shape)))

    init_df = _reorder_columns(init_df)
    init_df.sort_index().to_csv(output_path)
    logging.info('Output saved at %s' % output_path)
    logging.info('-----------------------------------------------------\n')


def build_imaging_availability(inventory: dict,
                               session_index: 'pd.DataFrame',
                               output_dir: str,
                               output_filename: str = 'imaging_availability.csv') -> str:
    """세션별 모달리티 유무 boolean CSV 생성."""
    logging.info('-------------------- Imaging Availability --------------------')

    by_bid_session = inventory.get('by_bid_session', {})
    if not by_bid_session:
        logging.warning('No by_bid_session in inventory — skipping')
        return ''

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

    if session_index is not None and not session_index.empty:
        if 'DAYS_CONSENT' in session_index.columns:
            df = df.join(session_index[['DAYS_CONSENT']], how='left')
            cols = ['DAYS_CONSENT'] + [c for c in df.columns if c != 'DAYS_CONSENT']
            df = df[cols]

    df.sort_index(inplace=True)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    df.to_csv(output_path)

    n_sessions = len(df)
    n_bids = df.index.get_level_values('BID').nunique()
    mod_sums = {m: int(df[m].sum()) for m in mod_list if m in df.columns}
    logging.info('Imaging availability: %d sessions, %d BIDs' % (n_sessions, n_bids))
    logging.info('  Modality counts: %s' % mod_sums)
    logging.info('  Output: %s' % output_path)
    logging.info('-----------------------------------------------------\n')

    return output_path


def build_longitudinal_csvs(session_index: 'pd.DataFrame',
                            long_cognitive: 'pd.DataFrame',
                            output_dir: str) -> list:
    """MMSE_longitudinal.csv, CDR_longitudinal.csv 생성.

    long_cognitive에 session_index의 DAYS_CONSENT, PTAGE를 조인하여 저장.
    """
    logging.info('-------------------- Longitudinal CSVs --------------------')
    saved = []

    if long_cognitive is None or long_cognitive.empty:
        logging.warning('No longitudinal cognitive data — skipping')
        return saved

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
    """
    logging.info('-------------------- BASELINE.csv --------------------')

    base = clinical.copy()
    # screening _bl 인지점수 제거 — V6 값으로 대체
    for drop_col in ['MMSE_bl', 'CDGLOBAL_bl', 'CDRSB_bl']:
        if drop_col in base.columns:
            base.drop(columns=[drop_col], inplace=True)
    logging.info('Clinical table: %d BIDs' % len(base))

    # 1. V6 인지점수 (MMSE는 V6, CDR은 V1 — A4 프로토콜상 CDR은 V6에서 미측정)
    if long_cognitive is not None and not long_cognitive.empty:
        # MMSE: V6 (randomization)
        try:
            v6_cog = long_cognitive.xs('006', level='SESSION_CODE', drop_level=True)
            v6_cog = v6_cog[~v6_cog.index.duplicated(keep='first')]
            if 'MMSE' in v6_cog.columns:
                base['MMSE'] = v6_cog['MMSE']
            logging.info('V6 MMSE: %d BIDs matched' % v6_cog['MMSE'].notna().sum()
                         if 'MMSE' in v6_cog.columns else 0)
        except KeyError:
            logging.warning('SESSION_CODE 006 not found in long_cognitive')

        # CDR: V1 (screening — A4 프로토콜에서 CDR은 V1에서만 측정)
        try:
            v1_cog = long_cognitive.xs('001', level='SESSION_CODE', drop_level=True)
            v1_cog = v1_cog[~v1_cog.index.duplicated(keep='first')]
            for col in ['CDGLOBAL', 'CDRSB']:
                if col in v1_cog.columns:
                    base[col] = v1_cog[col]
            logging.info('V1 CDR: %d BIDs matched' % v1_cog['CDGLOBAL'].notna().sum()
                         if 'CDGLOBAL' in v1_cog.columns else 0)
        except KeyError:
            logging.warning('SESSION_CODE 001 not found in long_cognitive')

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

    def _get_nii_path(mod_key, bid, session):
        mod_data = by_modality.get(mod_key, {})
        recs = mod_data.get(bid, [])
        for rec in recs:
            if rec.get('session') == session:
                return rec.get('nii_path', '')
        return ''

    for mod in ['T1', 'FLAIR', 'FTP', 'FBP']:
        col = '%s_NII_PATH' % mod
        base[col] = ''

    for bid in base.index:
        is_learn = bid in learn_bids
        mri_session = '006' if is_learn else '004'

        for mod, session in [('T1', mri_session), ('FLAIR', mri_session),
                             ('FTP', mri_session), ('FBP', '002')]:
            path = _get_nii_path(mod, bid, session)
            if path:
                base.at[bid, '%s_NII_PATH' % mod] = path

    # 빈 문자열 → NaN (MERGED.csv와 일관성)
    for mod in ['T1', 'FLAIR', 'FTP', 'FBP']:
        col = '%s_NII_PATH' % mod
        base[col] = base[col].replace('', pd.NA)

    nii_filled = {mod: base['%s_NII_PATH' % mod].notna().sum()
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


def run_pipeline(inventory: dict,
                 clinical: pd.DataFrame,
                 output_dir: str,
                 modalities: list = None,
                 overwrite: bool = False,
                 skip_merge: bool = False,
                 session_ages: pd.DataFrame = None,
                 long_cognitive: pd.DataFrame = None,
                 session_index: pd.DataFrame = None):
    """전체 파이프라인 실행.

    Args:
        inventory: build_inventory() 결과
        clinical: build_clinical_table() 결과
        output_dir: 출력 디렉토리
        modalities: 처리할 모달리티 (None이면 인벤토리에 있는 전체)
        overwrite: 기존 결과 덮어쓰기
        skip_merge: merge 단계 건너뛰기
        session_ages: build_session_age_table() 결과 (세션별 PTAGE)
        long_cognitive: build_longitudinal_cognitive() 결과 (세션별 인지 평가)
        session_index: build_session_index() 결과 (전체 세션 인덱스).
                       제공 시 session-centric MERGED.csv 생성.
    """
    if modalities is None:
        # 인벤토리에 실제 데이터가 있는 모달리티만
        modalities = [m for m in MODALITY_CONFIG
                      if inventory.get('by_modality', {}).get(m)]

    logging.info('Processing %d modalities: %s' % (len(modalities), ', '.join(modalities)))

    for mod in modalities:
        build_modality_csv(mod, inventory, clinical, output_dir,
                          session_ages=session_ages,
                          long_cognitive=long_cognitive,
                          overwrite=overwrite)

    if not skip_merge:
        if session_index is not None and not session_index.empty:
            build_session_merged(session_index, clinical, long_cognitive,
                                 inventory, output_dir,
                                 exclude_modalities=MERGE_EXCLUDE)
        else:
            unique_csv_merge(output_dir, exclude_modalities=MERGE_EXCLUDE)

    # 신규 CSV 생성 (session_index 있을 때만)
    if session_index is not None and not session_index.empty:
        build_baseline_csv(clinical, long_cognitive, session_index,
                           inventory, output_dir)
        build_longitudinal_csvs(session_index, long_cognitive, output_dir)
        build_imaging_availability(inventory, session_index, output_dir)
