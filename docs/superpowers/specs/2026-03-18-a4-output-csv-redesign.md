# A4 Output CSV Redesign

## Background

A4/LEARN 파이프라인의 현재 출력은 session-centric MERGED.csv (~65K행) 하나.
회의 결과, baseline 연구자를 위한 피험자당 1행 CSV + longitudinal 인지/영상 CSV를 추가로 생성하기로 결정.

핵심 결정: **V1~V6을 하나의 baseline visit으로 간주**.
- V1: screening cognitive (MMSE eligibility)
- V2: screening PET (FBP, amyloid 판정)
- V4: screening MRI (T1, FLAIR, T2, fMRI, DWI, FTP)
- V6: baseline cognitive (MMSE, CDR — randomization 시점)

## Output Files (5개)

### 1. MERGED.csv (기존 유지)

- **변경 없음** — session-centric, ~65K행
- 인덱스: (BID, SESSION_CODE)
- 전체 세션 × clinical × imaging left-join

### 2. BASELINE.csv (신규)

피험자당 1행. V1~V6 데이터를 best-pick하여 cross-sectional baseline 테이블 생성.

**인덱스**: BID
**행 수**: ~1,890 (amyloidNE 제외 시) / ~4,486 (포함 시, --include-screen-fail)

**컬럼 소스 매핑**:

| 컬럼 그룹 | 소스 session | 소스 테이블 |
|-----------|-------------|------------|
| PTGENDER, PTEDUCAT, APOEGN, AGEYR, Research_Group | — (BID-level) | PTDEMOG, SUBJINFO, demography |
| PTAGE | V6 기준 계산 | AGEYR + DAYS_CONSENT(V6)/365.25 |
| AMY_STATUS, AMY_SUVR | — (BID-level) | PETVADATA |
| AMY_SUVR_CER, AMY_CENTILOID | — (BID-level) | PETSUVR (Composite_Summary) |
| MMSE, CDGLOBAL, CDRSB | **V6** | mmse.csv, cdr.csv (Raw Data) |
| VMRI_* (50 ROI) | V4 | A4_VMRI (VISCODE=4) |
| TAU_* (272 ROI) | V4 | TAUSUVR |
| PTAU217_BL | V6 | biomarker_pTau217.csv |
| ROCHE_* (6 markers) | screening | biomarker_Plasma_Roche_Results.csv |
| T1_NII_PATH | V4 | NII inventory |
| FBP_NII_PATH | V2 | NII inventory |
| FTP_NII_PATH | V4 | NII inventory |
| FLAIR_NII_PATH | V4 | NII inventory |

**생성 로직**:
1. `build_clinical_table()` 결과 (BID 인덱스) 재사용 — 이미 V1~V6 best-pick 로직 포함
2. V6 기준 MMSE/CDR: `build_longitudinal_cognitive()` → V6(SESSION_CODE='006') 필터
3. V4/V2 NII 경로: inventory에서 해당 session 추출
4. PTAGE: session_index에서 V6의 DAYS_CONSENT 사용

**LEARN 차이 처리**:
- LEARN baseline MRI = V6 (A4는 V4). VMRI도 원래 V4 고정이므로 동일.
- LEARN baseline cognitive = V6 (동일).
- V4/V6 차이는 NII_PATH 추출 시에만 영향 — LEARN은 V6에서 MRI 경로 추출.

### 3. MMSE_longitudinal.csv (신규)

전체 방문의 MMSE long-format.

**인덱스**: (BID, SESSION_CODE)
**컬럼**: BID, SESSION_CODE, DAYS_CONSENT, PTAGE, MMSE
**소스**: `DEMO/Clinical/Raw Data/mmse.csv` (26,765행)
**행 수**: ~26K (dropna 후)

**생성 로직**:
1. mmse.csv 로드 → VISCODE → SESSION_CODE 변환
2. SV.csv에서 DAYS_CONSENT 조인
3. SUBJINFO에서 AGEYR → PTAGE 계산
4. (BID, SESSION_CODE) dedup, MMSCORE → MMSE rename

### 4. CDR_longitudinal.csv (신규)

전체 방문의 CDR long-format.

**인덱스**: (BID, SESSION_CODE)
**컬럼**: BID, SESSION_CODE, DAYS_CONSENT, PTAGE, CDGLOBAL, CDRSB
**소스**: `DEMO/Clinical/Raw Data/cdr.csv` (15,511행)
**행 수**: ~15K (dropna 후)

**생성 로직**: MMSE와 동일 패턴. CDSOB → CDRSB rename.

### 5. imaging_availability.csv (신규)

세션별 모달리티 유무 boolean 테이블.

**인덱스**: (BID, SESSION_CODE)
**컬럼**: BID, SESSION_CODE, DAYS_CONSENT, T1, FLAIR, T2_SE, T2_STAR, FMRI_REST, B0CD, FBP, FTP
**값**: 0/1 (해당 세션에 NII 파일 존재 여부)
**소스**: NII inventory (`by_modality` dict)
**행 수**: ~11K (이미징이 있는 세션만)

**생성 로직**:
1. inventory `by_bid_session` 순회
2. 각 (BID, session)에 대해 모달리티별 존재 여부 0/1
3. SV.csv에서 DAYS_CONSENT 조인

## CLI 인터페이스

기존 `a4-pipeline` CLI에 옵션 추가:

```bash
# 전체 파이프라인 (기존 + 신규 4개 CSV 모두 생성)
a4-pipeline

# Baseline CSV만 재생성
a4-pipeline --baseline-only

# Longitudinal CSV만 재생성
a4-pipeline --longitudinal-only
```

신규 CSV는 전체 파이프라인 실행 시 자동 생성. `--merge-only`는 기존 동작 유지.

## 코드 변경

### `src/a4/pipeline.py`

신규 함수 3개:
- `build_baseline_csv()` — clinical + V6 cognitive + inventory → BASELINE.csv
- `build_longitudinal_csvs()` — mmse.csv/cdr.csv → MMSE_longitudinal.csv, CDR_longitudinal.csv
- `build_imaging_availability()` — inventory + SV.csv → imaging_availability.csv

### `src/a4/cli.py`

- `--baseline-only`, `--longitudinal-only` 옵션 추가
- `main()` 파이프라인 단계에 신규 함수 호출 추가

### `src/a4/clinical.py`

- 변경 없음 — 기존 `build_clinical_table()`, `build_longitudinal_cognitive()` 재사용

## 출력 디렉토리

```
A4/ORIG/DEMO/A4_matching_v1/
├── MERGED.csv                    (기존)
├── BASELINE.csv                  (신규)
├── MMSE_longitudinal.csv         (신규)
├── CDR_longitudinal.csv          (신규)
├── imaging_availability.csv      (신규)
├── {MOD}_unique.csv              (기존)
├── clinical_table.csv            (기존)
├── nii_inventory.json            (기존)
└── a4_pipeline.log               (기존)
```

## 검증

1. BASELINE.csv 행 수 = clinical_table BID 수 (amyloidNE 제외 시 ~1,890)
2. BASELINE.csv MMSE = mmse.csv에서 V6 값과 일치
3. MMSE_longitudinal.csv 행 수 ≈ mmse.csv 행 수 (dropna 후)
4. imaging_availability.csv boolean 합계 = inventory modality_counts와 일치
