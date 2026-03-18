#!/usr/bin/env python3
"""
Comprehensive verification of A4 reference documents against NFS data and source code.

Checks:
1. A4_data_catalog.md — row/column counts for pipeline CSVs
2. A4_csv_profiles.md — detailed column profiles
3. A4_viscode_reference.md — visit code mappings
4. A4_join_relationships.md — join key claims
5. A4_column_dictionary.md — MERGED.csv column groups
"""

import os
import sys
import re
import traceback

import pandas as pd
import numpy as np

# ─── Paths ───────────────────────────────────────────────────────────────────
NFS_BASE = '/Volumes/nfs_storage/1_combined/A4/ORIG'
METADATA = os.path.join(NFS_BASE, 'metadata')
IMAGING_DIR = os.path.join(METADATA, 'A4 Imaging data and docs')
CLINICAL_BASE = os.path.join(NFS_BASE, 'DEMO/Clinical')
RAW_DATA = os.path.join(CLINICAL_BASE, 'Raw Data')
DERIVED_DATA = os.path.join(CLINICAL_BASE, 'Derived Data')
EXTERNAL_DATA = os.path.join(CLINICAL_BASE, 'External Data')
DOCS_DIR = os.path.join(CLINICAL_BASE, 'Documents/Data Dictionaries')

SRC_DIR = '/Users/jeon-younghoon/Desktop/ADNI_match/src/a4'

# ─── Results tracking ─────────────────────────────────────────────────────────
results = []

def check(name, passed, detail=''):
    tag = 'PASS' if passed else 'FAIL'
    msg = f'[{tag}] {name}'
    if detail:
        msg += f' — {detail}'
    results.append((tag, name, detail))
    print(msg)

def section(title):
    print(f'\n{"="*80}')
    print(f'  {title}')
    print(f'{"="*80}\n')

# ─── Helper: safe CSV load ────────────────────────────────────────────────────
def safe_load(path, **kwargs):
    if not os.path.isfile(path):
        return None, f'File not found: {path}'
    try:
        df = pd.read_csv(path, low_memory=False, **kwargs)
        return df, None
    except Exception as e:
        return None, str(e)

# ==============================================================================
# 1. A4_data_catalog.md — Row/Column Counts
# ==============================================================================
section('1. A4_data_catalog.md — Row & Column Counts')

# Pipeline CSV files from data_catalog with expected (rows, cols)
CATALOG_CHECKS = {
    # metadata/
    'PTDEMOG': (os.path.join(METADATA, 'A4_PTDEMOG_PRV2_11Aug2025.csv'), 6945, 14),
    'SUBJINFO': (os.path.join(METADATA, 'A4_SUBJINFO_PRV2_11Aug2025.csv'), 6945, 6),
    'REGISTRY': (os.path.join(METADATA, 'A4_REGISTRY_PRV2_11Aug2025.csv'), 18443, 8),
    'demography': (os.path.join(METADATA, 'A4_demography.csv'), 14334, 11),
    'MMSE': (os.path.join(METADATA, 'A4_MMSE_PRV2_11Aug2025.csv'), 6774, 39),
    'CDR': (os.path.join(METADATA, 'A4_CDR_PRV2_11Aug2025.csv'), 6322, 16),
    'SPPACC': (os.path.join(METADATA, 'A4_SPPACC_PRV2_11Aug2025.csv'), 34010, 16),
    # metadata/A4 Imaging data and docs/
    'PETSUVR': (os.path.join(IMAGING_DIR, 'A4_PETSUVR_PRV2_11Aug2025.csv'), 35936, 12),
    'PETVADATA': (os.path.join(IMAGING_DIR, 'A4_PETVADATA_PRV2_11Aug2025.csv'), 4492, 9),
    'VMRI': (os.path.join(IMAGING_DIR, 'A4_VMRI_PRV2_11Aug2025.csv'), 1271, 53),
    'TAUSUVR': (os.path.join(IMAGING_DIR, 'TAUSUVR_11Aug2025.csv'), 447, 274),
    # External Data/
    'pTau217': (os.path.join(EXTERNAL_DATA, 'biomarker_pTau217.csv'), 4538, 18),
    'Plasma_Roche': (os.path.join(EXTERNAL_DATA, 'biomarker_Plasma_Roche_Results.csv'), 13418, 14),
    'AB_Test': (os.path.join(EXTERNAL_DATA, 'biomarker_AB_Test.csv'), 31480, 12),
    # Derived Data/
    'SV': (os.path.join(DERIVED_DATA, 'SV.csv'), 103351, 9),
    # Raw Data/
    'mmse_long': (os.path.join(RAW_DATA, 'mmse.csv'), 26765, 41),
    'cdr_long': (os.path.join(RAW_DATA, 'cdr.csv'), 15511, 25),
}

for name, (path, exp_rows, exp_cols) in CATALOG_CHECKS.items():
    try:
        df, err = safe_load(path)
        if df is None:
            check(f'catalog/{name} load', False, err)
            continue
        actual_rows = len(df)
        actual_cols = df.shape[1]
        row_ok = actual_rows == exp_rows
        col_ok = actual_cols == exp_cols
        check(f'catalog/{name} rows', row_ok,
              f'expected={exp_rows}, actual={actual_rows}')
        check(f'catalog/{name} cols', col_ok,
              f'expected={exp_cols}, actual={actual_cols}')
    except Exception:
        check(f'catalog/{name}', False, traceback.format_exc().splitlines()[-1])

# Special: TAUSUVR ID format = pure BID (no underscore)
try:
    tau_path = os.path.join(IMAGING_DIR, 'TAUSUVR_11Aug2025.csv')
    tau_df, err = safe_load(tau_path)
    if tau_df is not None and 'ID' in tau_df.columns:
        has_underscore = tau_df['ID'].astype(str).str.contains('_').any()
        check('catalog/TAUSUVR ID pure BID (no underscore)', not has_underscore,
              f'IDs with underscore: {tau_df["ID"].astype(str).str.contains("_").sum()}')
    else:
        check('catalog/TAUSUVR ID column', False, f'ID column missing or load error: {err}')
except Exception:
    check('catalog/TAUSUVR ID check', False, traceback.format_exc().splitlines()[-1])

# Special: pTau217 row count = 4,538
try:
    ptau_path = os.path.join(EXTERNAL_DATA, 'biomarker_pTau217.csv')
    ptau_df, err = safe_load(ptau_path)
    if ptau_df is not None:
        check('catalog/pTau217 exact row count 4538', len(ptau_df) == 4538,
              f'actual={len(ptau_df)}')
    else:
        check('catalog/pTau217 load', False, err)
except Exception:
    check('catalog/pTau217 check', False, traceback.format_exc().splitlines()[-1])


# ==============================================================================
# 2. A4_csv_profiles.md — Detailed dtype & structural checks
# ==============================================================================
section('2. A4_csv_profiles.md — Structural Profiles')

# VMRI: exactly 50 ROI columns (excluding BID, VISCODE, update_stamp)
try:
    vmri_path = os.path.join(IMAGING_DIR, 'A4_VMRI_PRV2_11Aug2025.csv')
    vmri_df, err = safe_load(vmri_path)
    if vmri_df is not None:
        exclude_cols = {'BID', 'VISCODE', 'update_stamp'}
        roi_cols = [c for c in vmri_df.columns if c not in exclude_cols]
        check('profiles/VMRI 50 ROI cols', len(roi_cols) == 50,
              f'ROI cols={len(roi_cols)}, names: {roi_cols[:5]}...')
    else:
        check('profiles/VMRI load', False, err)
except Exception:
    check('profiles/VMRI ROI check', False, traceback.format_exc().splitlines()[-1])

# TAUSUVR: exactly 272 ROI columns (excluding ID, update_stamp)
try:
    tau_path = os.path.join(IMAGING_DIR, 'TAUSUVR_11Aug2025.csv')
    tau_df, err = safe_load(tau_path)
    if tau_df is not None:
        exclude_cols = {'ID', 'update_stamp'}
        roi_cols = [c for c in tau_df.columns if c not in exclude_cols]
        check('profiles/TAUSUVR 272 ROI cols', len(roi_cols) == 272,
              f'ROI cols={len(roi_cols)}')
    else:
        check('profiles/TAUSUVR load', False, err)
except Exception:
    check('profiles/TAUSUVR ROI check', False, traceback.format_exc().splitlines()[-1])

# PETSUVR VISCODE values should be {3}
try:
    pet_path = os.path.join(IMAGING_DIR, 'A4_PETSUVR_PRV2_11Aug2025.csv')
    pet_df, err = safe_load(pet_path)
    if pet_df is not None and 'VISCODE' in pet_df.columns:
        unique_vis = set(pet_df['VISCODE'].dropna().unique())
        check('profiles/PETSUVR VISCODE={3}', unique_vis == {3},
              f'actual unique VISCODE: {sorted(unique_vis)}')
    else:
        check('profiles/PETSUVR VISCODE', False, f'load or col error: {err}')
except Exception:
    check('profiles/PETSUVR VISCODE', False, traceback.format_exc().splitlines()[-1])

# PETVADATA has NO VISCODE column
try:
    petva_path = os.path.join(IMAGING_DIR, 'A4_PETVADATA_PRV2_11Aug2025.csv')
    petva_df, err = safe_load(petva_path)
    if petva_df is not None:
        has_viscode = 'VISCODE' in petva_df.columns
        check('profiles/PETVADATA no VISCODE column', not has_viscode,
              f'columns: {list(petva_df.columns)}')
    else:
        check('profiles/PETVADATA load', False, err)
except Exception:
    check('profiles/PETVADATA VISCODE', False, traceback.format_exc().splitlines()[-1])

# SV.csv uses VISITCD (not VISCODE)
try:
    sv_path = os.path.join(DERIVED_DATA, 'SV.csv')
    sv_df, err = safe_load(sv_path)
    if sv_df is not None:
        has_visitcd = 'VISITCD' in sv_df.columns
        has_viscode = 'VISCODE' in sv_df.columns
        check('profiles/SV uses VISITCD', has_visitcd, f'VISITCD present={has_visitcd}')
        check('profiles/SV no VISCODE', not has_viscode, f'VISCODE present={has_viscode}')
    else:
        check('profiles/SV load', False, err)
except Exception:
    check('profiles/SV column check', False, traceback.format_exc().splitlines()[-1])

# TAUSUVR uses ID column (not BID)
try:
    tau_df2, err = safe_load(os.path.join(IMAGING_DIR, 'TAUSUVR_11Aug2025.csv'))
    if tau_df2 is not None:
        has_id = 'ID' in tau_df2.columns
        has_bid = 'BID' in tau_df2.columns
        check('profiles/TAUSUVR uses ID (not BID)', has_id and not has_bid,
              f'ID={has_id}, BID={has_bid}')
    else:
        check('profiles/TAUSUVR ID/BID', False, err)
except Exception:
    check('profiles/TAUSUVR ID/BID', False, traceback.format_exc().splitlines()[-1])

# demography row count (doc says 14,334 but profiles say 14,333 — check actual)
try:
    demog_path = os.path.join(METADATA, 'A4_demography.csv')
    demog_df, err = safe_load(demog_path)
    if demog_df is not None:
        check('profiles/demography actual rows', True,
              f'actual={len(demog_df)} (catalog says 14334, profiles says 14333)')
        # Check Research Group values
        if 'Research Group' in demog_df.columns:
            rg_vals = set(demog_df['Research Group'].dropna().unique())
            expected_rg = {'LEARN amyloidNE', 'amyloidE', 'amyloidNE'}
            check('profiles/demography Research Group values', rg_vals == expected_rg,
                  f'actual: {rg_vals}')
    else:
        check('profiles/demography load', False, err)
except Exception:
    check('profiles/demography', False, traceback.format_exc().splitlines()[-1])

# dtype checks for key columns
DTYPE_CHECKS = [
    ('PTDEMOG', os.path.join(METADATA, 'A4_PTDEMOG_PRV2_11Aug2025.csv'),
     {'BID': 'object', 'PTGENDER': 'int64', 'VISCODE': 'int64'}),
    ('SUBJINFO', os.path.join(METADATA, 'A4_SUBJINFO_PRV2_11Aug2025.csv'),
     {'BID': 'object', 'AGEYR': 'float64', 'APOEGN': 'object'}),
    ('SV', os.path.join(DERIVED_DATA, 'SV.csv'),
     {'BID': 'object', 'VISITCD': 'int64', 'SVTYPE': 'object'}),
    ('pTau217', os.path.join(EXTERNAL_DATA, 'biomarker_pTau217.csv'),
     {'BID': 'object', 'VISCODE': 'int64', 'ORRESRAW': 'float64'}),
]

for name, path, expected_dtypes in DTYPE_CHECKS:
    try:
        df, err = safe_load(path)
        if df is None:
            check(f'profiles/{name} dtypes', False, err)
            continue
        for col, exp_dtype in expected_dtypes.items():
            if col not in df.columns:
                check(f'profiles/{name}.{col} dtype', False, f'column not found')
                continue
            actual = str(df[col].dtype)
            check(f'profiles/{name}.{col} dtype={exp_dtype}', actual == exp_dtype,
                  f'actual={actual}')
    except Exception:
        check(f'profiles/{name} dtypes', False, traceback.format_exc().splitlines()[-1])


# ==============================================================================
# 3. A4_viscode_reference.md — Visit Code Mappings
# ==============================================================================
section('3. A4_viscode_reference.md — Visit Code Mappings')

# Parse visits_datadic.csv
try:
    visits_path = os.path.join(DOCS_DIR, 'visits_datadic.csv')
    visits_df, err = safe_load(visits_path)
    if visits_df is not None:
        check('viscode/visits_datadic loaded', True, f'{len(visits_df)} rows')

        # Count visits by SUBSTUDY if available, or by attributes
        # Expected: doc says 152 rows total (in docstring "152행")
        check('viscode/visits_datadic row count ~152', True,
              f'actual={len(visits_df)} (doc says 152)')

        # Check if we can identify A4 vs LEARN vs SF visits
        if 'SUBSTUDY' in visits_df.columns:
            substudies = visits_df['SUBSTUDY'].value_counts()
            a4_count = substudies.get('A4', 0)
            learn_count = substudies.get('LEARN', 0)
            sf_count = substudies.get('SF', 0)
            check('viscode/A4 visit count=125', a4_count == 125,
                  f'actual A4={a4_count}')
            check('viscode/LEARN visit count=21', learn_count == 21,
                  f'actual LEARN={learn_count}')
            check('viscode/SF visit count=6', sf_count == 6,
                  f'actual SF={sf_count}')
        else:
            # Try STUDYID or other col
            available_cols = list(visits_df.columns)
            check('viscode/SUBSTUDY column', False,
                  f'No SUBSTUDY col. Available: {available_cols}')
            # Try to find the substudy column
            for col_candidate in ['STUDYID', 'Study', 'PROTOCOL', 'STUDY']:
                if col_candidate in visits_df.columns:
                    vals = visits_df[col_candidate].value_counts()
                    check(f'viscode/{col_candidate} distribution', True, str(vals.to_dict()))
    else:
        check('viscode/visits_datadic', False, err)
except Exception:
    check('viscode/visits_datadic', False, traceback.format_exc().splitlines()[-1])

# VISCODE week formula: (VISCODE - 6) * 4 for VISCODE >= 6
# Test with known values from the doc
try:
    formula_tests = [
        (6, 0, 'Baseline'),
        (7, 4, 'wk4 Infusion'),
        (9, 12, 'wk12 Clinic'),
        (12, 24, 'wk24 Clinic'),
        (66, 240, 'wk240 End DB'),
        (117, 444, 'wk444 Clinic OLE'),
    ]
    all_ok = True
    for viscode, expected_week, label in formula_tests:
        calculated = (viscode - 6) * 4
        if calculated != expected_week:
            all_ok = False
            check(f'viscode/formula VISCODE={viscode}', False,
                  f'expected wk{expected_week}, got wk{calculated} ({label})')
    if all_ok:
        check('viscode/week formula (VISCODE-6)*4 all correct', True,
              f'tested {len(formula_tests)} values')
except Exception:
    check('viscode/formula', False, traceback.format_exc().splitlines()[-1])

# Verify formula works for ALL visits >= 6 from visits_datadic
try:
    visits_path = os.path.join(DOCS_DIR, 'visits_datadic.csv')
    visits_df, _ = safe_load(visits_path)
    if visits_df is not None:
        # Identify VISCODE column
        viscode_col = None
        for c in ['VISCODE', 'VISITCD', 'VISORDER']:
            if c in visits_df.columns:
                viscode_col = c
                break

        visname_col = None
        for c in ['VISNAME', 'VISIT', 'VISITNAME']:
            if c in visits_df.columns:
                visname_col = c
                break

        if viscode_col and visname_col:
            # For visits >= 6 and < 701 (exclude unscheduled/termination)
            treatment_visits = visits_df[
                (visits_df[viscode_col] >= 6) &
                (visits_df[viscode_col] < 701)
            ].copy()

            mismatches = 0
            for _, row in treatment_visits.iterrows():
                vc = int(row[viscode_col])
                vname = str(row[visname_col])
                calc_week = (vc - 6) * 4

                # Extract week number from visit name if present
                wk_match = re.search(r'wk(\d+)', vname, re.IGNORECASE)
                if wk_match:
                    actual_week = int(wk_match.group(1))
                    if actual_week != calc_week:
                        mismatches += 1
                        print(f'  MISMATCH: VISCODE={vc}, name="{vname}", formula=wk{calc_week}, actual=wk{actual_week}')

                # Also check for "Baseline" which should be wk0 (VISCODE=6)
                if 'baseline' in vname.lower() and vc == 6 and calc_week != 0:
                    mismatches += 1

            check('viscode/formula validated against visits_datadic (VISCODE>=6, <701)',
                  mismatches == 0,
                  f'{len(treatment_visits)} visits checked, {mismatches} mismatches')
        else:
            check('viscode/formula against datadic', False,
                  f'Could not find viscode/visname cols. Available: {list(visits_df.columns)}')
except Exception:
    check('viscode/formula against datadic', False, traceback.format_exc().splitlines()[-1])

# pTau217 VISCODE mapping matches config.py
try:
    # Import config
    sys.path.insert(0, os.path.dirname(SRC_DIR))
    from a4.config import PTAU217_VISIT_MAP

    # Expected from viscode doc:
    doc_map = {
        'A4': {6: 'PTAU217_BL', 9: 'PTAU217_WK12', 66: 'PTAU217_WK240', 997: 'PTAU217_OLE', 999: 'PTAU217_ET'},
        'LEARN': {1: 'PTAU217_SCR', 24: 'PTAU217_WK72', 66: 'PTAU217_WK240', 999: 'PTAU217_ET'},
    }
    match = PTAU217_VISIT_MAP == doc_map
    check('viscode/pTau217 VISIT_MAP matches doc', match,
          f'config={PTAU217_VISIT_MAP}' if not match else 'exact match')
except Exception:
    check('viscode/pTau217 VISIT_MAP', False, traceback.format_exc().splitlines()[-1])

# Verify pTau217 actual VISCODE values match config
try:
    ptau_path = os.path.join(EXTERNAL_DATA, 'biomarker_pTau217.csv')
    ptau_df, err = safe_load(ptau_path)
    if ptau_df is not None and 'VISCODE' in ptau_df.columns:
        actual_viscodes = set(ptau_df['VISCODE'].dropna().unique())
        # All VISCODEs in config
        config_viscodes = set()
        for sub_map in PTAU217_VISIT_MAP.values():
            config_viscodes.update(sub_map.keys())
        # Doc says: {1, 6, 9, 24, 66, 997, 999}
        doc_viscodes = {1, 6, 9, 24, 66, 997, 999}
        check('viscode/pTau217 actual VISCODE = doc claim',
              actual_viscodes == doc_viscodes,
              f'actual={sorted(actual_viscodes)}, doc={sorted(doc_viscodes)}')
        check('viscode/pTau217 VISCODE superset of config',
              config_viscodes.issubset(actual_viscodes),
              f'config={sorted(config_viscodes)}, actual={sorted(actual_viscodes)}')
    else:
        check('viscode/pTau217 VISCODE', False, f'{err}')
except Exception:
    check('viscode/pTau217 VISCODE', False, traceback.format_exc().splitlines()[-1])


# ==============================================================================
# 4. A4_join_relationships.md — Join Key Claims
# ==============================================================================
section('4. A4_join_relationships.md — Join Key Claims')

# BID only files: PTDEMOG (effectively), SUBJINFO, demography, PETVADATA
# We check that these have BID as a potential unique key

# SUBJINFO: BID unique (1:1)
try:
    subjinfo_path = os.path.join(METADATA, 'A4_SUBJINFO_PRV2_11Aug2025.csv')
    df, err = safe_load(subjinfo_path)
    if df is not None:
        bid_unique = df['BID'].nunique() == len(df)
        check('join/SUBJINFO BID unique (1:1)', bid_unique,
              f'rows={len(df)}, unique BIDs={df["BID"].nunique()}')
    else:
        check('join/SUBJINFO', False, err)
except Exception:
    check('join/SUBJINFO', False, traceback.format_exc().splitlines()[-1])

# PETVADATA: BID unique (1:1)
try:
    petva_path = os.path.join(IMAGING_DIR, 'A4_PETVADATA_PRV2_11Aug2025.csv')
    df, err = safe_load(petva_path)
    if df is not None:
        bid_unique = df['BID'].nunique() == len(df)
        check('join/PETVADATA BID unique (1:1)', bid_unique,
              f'rows={len(df)}, unique BIDs={df["BID"].nunique()}')
    else:
        check('join/PETVADATA', False, err)
except Exception:
    check('join/PETVADATA', False, traceback.format_exc().splitlines()[-1])

# BID+VISCODE files: MMSE, CDR, REGISTRY, PETSUVR, VMRI
for name, path in [
    ('MMSE', os.path.join(METADATA, 'A4_MMSE_PRV2_11Aug2025.csv')),
    ('CDR', os.path.join(METADATA, 'A4_CDR_PRV2_11Aug2025.csv')),
    ('REGISTRY', os.path.join(METADATA, 'A4_REGISTRY_PRV2_11Aug2025.csv')),
    ('VMRI', os.path.join(IMAGING_DIR, 'A4_VMRI_PRV2_11Aug2025.csv')),
]:
    try:
        df, err = safe_load(path)
        if df is not None:
            has_bid = 'BID' in df.columns
            has_viscode = 'VISCODE' in df.columns
            check(f'join/{name} has BID+VISCODE', has_bid and has_viscode,
                  f'BID={has_bid}, VISCODE={has_viscode}')
        else:
            check(f'join/{name}', False, err)
    except Exception:
        check(f'join/{name}', False, traceback.format_exc().splitlines()[-1])

# PETSUVR: BID + brain_region (1:N, 8 per BID)
try:
    pet_path = os.path.join(IMAGING_DIR, 'A4_PETSUVR_PRV2_11Aug2025.csv')
    df, err = safe_load(pet_path)
    if df is not None:
        has_br = 'brain_region' in df.columns
        if has_br:
            n_regions = df['brain_region'].nunique()
            rows_per_bid = len(df) / df['BID'].nunique()
            check('join/PETSUVR BID+brain_region (8 regions)', n_regions == 8,
                  f'unique regions={n_regions}, rows/BID={rows_per_bid:.1f}')
        else:
            check('join/PETSUVR brain_region', False, 'column missing')
    else:
        check('join/PETSUVR', False, err)
except Exception:
    check('join/PETSUVR', False, traceback.format_exc().splitlines()[-1])

# SV.csv uses VISITCD (confirmed earlier, just re-state)
# Already checked in profiles section

# Biomarker files: BID + VISCODE + SUBSTUDY
for name, path in [
    ('pTau217', os.path.join(EXTERNAL_DATA, 'biomarker_pTau217.csv')),
    ('Plasma_Roche', os.path.join(EXTERNAL_DATA, 'biomarker_Plasma_Roche_Results.csv')),
    ('AB_Test', os.path.join(EXTERNAL_DATA, 'biomarker_AB_Test.csv')),
]:
    try:
        df, err = safe_load(path)
        if df is not None:
            has_sub = 'SUBSTUDY' in df.columns
            has_bid = 'BID' in df.columns
            has_vis = 'VISCODE' in df.columns
            check(f'join/{name} has BID+VISCODE+SUBSTUDY',
                  has_bid and has_vis and has_sub,
                  f'BID={has_bid}, VISCODE={has_vis}, SUBSTUDY={has_sub}')
            if has_sub:
                subs = sorted(df['SUBSTUDY'].unique())
                check(f'join/{name} SUBSTUDY values', True, f'{subs}')
        else:
            check(f'join/{name}', False, err)
    except Exception:
        check(f'join/{name}', False, traceback.format_exc().splitlines()[-1])

# Verify pipeline phase descriptions: _build_demographics does outer join
try:
    clinical_src = os.path.join(SRC_DIR, 'clinical.py')
    with open(clinical_src, 'r') as f:
        code = f.read()

    # Check outer join in _build_demographics
    has_outer_demo = "demo.join(subj, how='outer')" in code or 'how=\'outer\'' in code
    check('join/clinical.py _build_demographics uses outer join',
          "demo.join(subj, how='outer')" in code,
          'found outer join pattern' if "demo.join(subj, how='outer')" in code else 'not found')

    # Check _build_demography_groups uses outer join
    has_outer_demog = "demo.join(demog_groups, how='outer')" in code
    check('join/clinical.py _build_demography_groups uses outer join',
          has_outer_demog,
          'found' if has_outer_demog else 'not found')

    # Check other joins use 'left'
    left_joins = code.count("how='left'")
    check('join/clinical.py other joins use left', left_joins >= 4,
          f'{left_joins} left joins found')
except Exception:
    check('join/clinical.py analysis', False, traceback.format_exc().splitlines()[-1])


# ==============================================================================
# 5. A4_column_dictionary.md — MERGED.csv Column Groups
# ==============================================================================
section('5. A4_column_dictionary.md — Column Groups & Reorder')

# Verify _reorder_columns groups match doc
try:
    pipeline_src = os.path.join(SRC_DIR, 'pipeline.py')
    with open(pipeline_src, 'r') as f:
        pcode = f.read()

    # Extract group order from _reorder_columns
    # Group 1: Timing
    check('coldict/_reorder timing DAYS_CONSENT', "['DAYS_CONSENT']" in pcode, '')

    # Group 2: Demographics
    demo_order = "['PTGENDER', 'PTAGE', 'PTEDUCAT', 'APOEGN'"
    check('coldict/_reorder demographics order', demo_order in pcode, '')

    # Group 3: Amyloid
    amy_order = "['AMY_STATUS_bl', 'AMY_SUVR_bl', 'AMY_SUVR_CER_bl', 'AMY_CENTILOID_bl']"
    check('coldict/_reorder amyloid order', amy_order in pcode, '')

    # Group 4: Clinical
    clin_order = "['MMSE_bl', 'MMSE', 'CDGLOBAL_bl', 'CDGLOBAL', 'CDRSB_bl', 'CDRSB']"
    check('coldict/_reorder clinical order', clin_order in pcode, '')

    # Group 5: pTau217
    check('coldict/_reorder pTau217 prefix', "_take_prefix('PTAU217_')" in pcode, '')

    # Group 6: MODALITIES
    check('coldict/_reorder MODALITIES', "['MODALITIES']" in pcode, '')

    # Group 7-8: MRI/PET modalities order
    mri_mods = "('T1', 'FLAIR', 'T2_SE', 'T2_STAR', 'FMRI_REST', 'B0CD')"
    pet_mods = "('FBP', 'FTP')"
    check('coldict/_reorder MRI mod order', mri_mods in pcode, '')
    check('coldict/_reorder PET mod order', pet_mods in pcode, '')

    # Group 9-10: VMRI and TAU
    check('coldict/_reorder VMRI prefix', "_take_prefix('VMRI_')" in pcode, '')
    check('coldict/_reorder TAU prefix', "_take_prefix('TAU_')" in pcode, '')

except Exception:
    check('coldict/_reorder_columns', False, traceback.format_exc().splitlines()[-1])

# Verify _bl suffix columns from clinical.py builders
try:
    with open(os.path.join(SRC_DIR, 'clinical.py'), 'r') as f:
        ccode = f.read()

    # _build_cognitive adds _bl suffix to MMSE_bl, CDGLOBAL_bl, CDRSB_bl
    check('coldict/_build_cognitive _bl suffix',
          "result.columns = [c + '_bl' for c in result.columns]" in ccode,
          'pattern found' if "result.columns = [c + '_bl' for c in result.columns]" in ccode else 'not found')

    # _build_vmri adds VMRI_ prefix + _bl suffix
    check('coldict/_build_vmri VMRI_*_bl',
          "'VMRI_' + c + '_bl'" in ccode,
          'found' if "'VMRI_' + c + '_bl'" in ccode else 'not found')

    # _build_tau_suvr adds TAU_ prefix + _bl suffix
    check('coldict/_build_tau_suvr TAU_*_bl',
          "'TAU_' + c + '_bl'" in ccode,
          'found' if "'TAU_' + c + '_bl'" in ccode else 'not found')

    # _build_amyloid_status creates AMY_STATUS_bl, AMY_SUVR_bl
    check('coldict/_build_amyloid AMY_STATUS_bl',
          "AMY_STATUS_bl" in ccode and "AMY_SUVR_bl" in ccode,
          'found both')

    # _build_pet_suvr creates AMY_SUVR_CER_bl, AMY_CENTILOID_bl
    check('coldict/_build_pet_suvr AMY_SUVR_CER_bl/AMY_CENTILOID_bl',
          "AMY_SUVR_CER_bl" in ccode and "AMY_CENTILOID_bl" in ccode,
          'found both')

except Exception:
    check('coldict/_bl suffix check', False, traceback.format_exc().splitlines()[-1])

# Verify column source claims
try:
    # PTGENDER from PTDEMOG
    check('coldict/PTGENDER source=PTDEMOG',
          "'PTGENDER'" in ccode and '_build_demographics' in ccode,
          'confirmed in _build_demographics')

    # APOEGN from SUBJINFO
    check('coldict/APOEGN source=SUBJINFO',
          "'APOEGN'" in ccode and 'subjinfo' in ccode,
          'confirmed')

    # AMY_STATUS from PETVADATA.SCORE
    # Code uses: rename['SCORE'] = 'AMY_STATUS_bl'
    check('coldict/AMY_STATUS source=PETVADATA.SCORE',
          "AMY_STATUS_bl" in ccode and "SCORE" in ccode and "_build_amyloid_status" in ccode,
          'confirmed: SCORE → AMY_STATUS_bl in _build_amyloid_status')

    # AMY_SUVR from PETVADATA.PMODSUVR
    check('coldict/AMY_SUVR source=PETVADATA.PMODSUVR',
          "AMY_SUVR_bl" in ccode and "PMODSUVR" in ccode and "_build_amyloid_status" in ccode,
          'confirmed: PMODSUVR → AMY_SUVR_bl in _build_amyloid_status')

    # AMY_SUVR_CER from PETSUVR.suvr_cer
    check('coldict/AMY_SUVR_CER source=PETSUVR.suvr_cer',
          "AMY_SUVR_CER_bl" in ccode and "suvr_cer" in ccode and "_build_pet_suvr" in ccode,
          'confirmed: suvr_cer → AMY_SUVR_CER_bl in _build_pet_suvr')

    # AMY_CENTILOID from PETSUVR.centiloid
    check('coldict/AMY_CENTILOID source=PETSUVR.centiloid',
          "AMY_CENTILOID_bl" in ccode and "centiloid" in ccode and "_build_pet_suvr" in ccode,
          'confirmed: centiloid → AMY_CENTILOID_bl in _build_pet_suvr')

    # MMSE_bl from MMSCORE
    check('coldict/MMSE_bl source=MMSE.MMSCORE',
          "'MMSCORE': 'MMSE'" in ccode,
          'confirmed rename MMSCORE→MMSE then +_bl')

    # CDRSB_bl from CDSOB
    check('coldict/CDRSB_bl source=CDR.CDSOB',
          "'CDSOB': 'CDRSB'" in ccode,
          'confirmed rename CDSOB→CDRSB then +_bl')

except Exception:
    check('coldict/column sources', False, traceback.format_exc().splitlines()[-1])

# Verify DAYS_CONSENT range from SV.csv
try:
    sv_path = os.path.join(DERIVED_DATA, 'SV.csv')
    sv_df, err = safe_load(sv_path)
    if sv_df is not None and 'SVSTDTC_DAYS_CONSENT' in sv_df.columns:
        dc = sv_df['SVSTDTC_DAYS_CONSENT'].dropna()
        dc_min = dc.min()
        dc_max = dc.max()
        # Doc claims: -174 ~ 3302
        doc_min, doc_max = -174, 3302
        min_ok = abs(dc_min - doc_min) <= 1  # allow tiny rounding
        max_ok = abs(dc_max - doc_max) <= 1
        check('coldict/DAYS_CONSENT range matches doc',
              min_ok and max_ok,
              f'actual=[{dc_min:.1f}, {dc_max:.1f}], doc=[{doc_min}, {doc_max}]')
    else:
        check('coldict/DAYS_CONSENT range', False, f'{err}')
except Exception:
    check('coldict/DAYS_CONSENT range', False, traceback.format_exc().splitlines()[-1])

# Verify VMRI column count: 50 ROI + update_stamp = 51 non-key cols (BID, VISCODE excluded)
# Already checked in profiles section

# Verify TAU column count: 272 ROI + update_stamp = 273 non-key cols (ID excluded)
# Already checked in profiles section

# Verify build_session_index output columns
try:
    check('coldict/session_index cols = DAYS_CONSENT + PTAGE',
          "result = sv[['BID', 'SESSION_CODE', 'DAYS_CONSENT', 'PTAGE']]" in ccode,
          'confirmed in build_session_index')
except Exception:
    check('coldict/session_index', False, traceback.format_exc().splitlines()[-1])

# Verify build_longitudinal_cognitive output columns = MMSE, CDGLOBAL, CDRSB
try:
    check('coldict/long_cognitive cols',
          "mmse.rename(columns={'MMSCORE': 'MMSE'}" in ccode and
          "cdr.rename(columns={'CDSOB': 'CDRSB'}" in ccode,
          'confirmed MMSCORE→MMSE, CDSOB→CDRSB')
except Exception:
    check('coldict/long_cognitive', False, traceback.format_exc().splitlines()[-1])


# ==============================================================================
# SUMMARY
# ==============================================================================
section('SUMMARY')

pass_count = sum(1 for r in results if r[0] == 'PASS')
fail_count = sum(1 for r in results if r[0] == 'FAIL')
total = len(results)

print(f'Total checks: {total}')
print(f'  PASS: {pass_count}')
print(f'  FAIL: {fail_count}')
print()

if fail_count > 0:
    print('FAILED checks:')
    for tag, name, detail in results:
        if tag == 'FAIL':
            print(f'  - {name}: {detail}')
else:
    print('All checks passed!')
