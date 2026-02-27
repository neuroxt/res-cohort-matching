# ADNI_match

ADNI (Alzheimer's Disease Neuroimaging Initiative) GO/1/2/3/4 전체 코호트의
임상 데이터 추출 및 DICOM 영상 매칭 파이프라인.

LONI에서 제공하는 ADNIMERGE2 R 패키지의 .rda 데이터를 Python으로 추출하고,
NFS 서버의 DICOM 파일과 매칭하여 통합 CSV(`MERGED.csv`)를 생성한다.

---

## 프로젝트 구조

```
ADNI_match/
├── ADNIMERGE2/          # LONI ADNIMERGE2 R 패키지 (원본, 수정 금지)
├── adnimerge_py/        # Part 1: .rda → ADNIMERGE CSV 추출
├── adni_matching/       # Part 2: DICOM 매칭 파이프라인
│   └── orig/            #   레퍼런스 코드 (XML 기반, 수정 금지)
├── scripts/             # 검증 및 유틸리티 스크립트
├── docs/                # 검증 리포트
└── ini/                 # 설정 예시
```

---

## 1. ADNIMERGE2 (LONI R 패키지)

LONI ATRI Biostatistics에서 제공하는 R 데이터 패키지.
217개 `.rda` 파일에 ADNI 전체 코호트의 임상, 인지검사, 바이오마커, MRI 용적, PET 데이터가 포함되어 있다.

- **출처**: https://atri-biostats.github.io/ADNIMERGE2
- **버전**: 0.1.1 (2026-01-05)
- **주의**: 이 디렉토리는 원본 그대로 유지하며 수정하지 않는다.

---

## 2. adnimerge_py (ADNIMERGE CSV 추출)

ADNIMERGE2 R 패키지의 빌드 로직을 Python/pandas로 1:1 이식한 패키지.
`.rda` 원본에서 직접 ADNIMERGE CSV를 생성한다.

### 모듈 구성

| 파일 | 역할 |
|------|------|
| `build_adnimerge.py` | 12단계 빌드 프로세스로 ADNIMERGE CSV 생성 |
| `rda_converter.py` | .rda → CSV 일괄 변환 (217개 테이블) |
| `compare_ref.py` | 레퍼런스 CSV 대비 비교 검증 |
| `run.py` | CLI 인터페이스 |

### 12단계 빌드 프로세스

| 단계 | 내용 | 주요 소스 |
|------|------|-----------|
| 1 | 코어 데이터셋 로드 | ADSL, REGISTRY, DXSUM, PTDEMOG 등 22개 |
| 2 | 베이스 프레임 생성 | REGISTRY (VISCODE 표준화) |
| 3 | 인구통계 + EXAMDATE_bl | PTDEMOG, APOERES, ADSL |
| 4 | 진단 (DX, DX_bl) | DXSUM + ARM.rda (EMCI/LMCI/SMC 유지) |
| 5 | 인지검사 점수 | ADAS, MMSE, CDR, MOCA, ECOG 등 |
| 6 | CSF 바이오마커 | UPENNBIOMK_MASTER + ROCHE_ELECSYS |
| 7 | MRI 용적 | UCSFFSX51 (primary) + UCSDVOL (Ventricles) |
| 8 | PET 데이터 | UCBERKELEYFDG_8mm, AMY_6MM, TAU_6MM |
| 9 | 혈장 바이오마커 | UPenn, C2N, Fujirebio, Quanterix, UGOT |
| 10 | 파생 변수 | Baseline coalesce, Month, SITE, mPACC |
| 11 | 132개 컬럼 스키마 선택 | — |
| 12 | CSV 저장 | ADNIMERGE_{DATE}.csv |

### 실행

```bash
# 전체 실행 (rda 변환 + ADNIMERGE + MRIQC + APOERES)
python -m adnimerge_py

# 개별 단계
python -m adnimerge_py --build-adnimerge
python -m adnimerge_py --build-mriqc
python -m adnimerge_py --convert-all

# 옵션
python -m adnimerge_py --rda-dir /path/to/ADNIMERGE2/data --output-dir /path/to/csv --date 260213 -v
```

### 출력

| 파일 | 설명 |
|------|------|
| `ADNIMERGE_{DATE}.csv` | 23,479행 × 132열, 4,498 피험자 |
| `MRIQC_{DATE}.csv` | 90,250행 MRI QC 메타데이터 |
| `APOERES_{DATE}.csv` | 3,008행 APOE 유전형 |
| `tables/*.csv` | 217개 .rda 1:1 CSV 변환 |

상세 설명: [`adnimerge_py/README.md`](adnimerge_py/README.md)

---

## 3. adni_matching (DICOM 매칭 파이프라인)

XML 메타데이터를 완전히 제거하고, 경로 파싱 + ADNIMERGE + MRIQC + pydicom으로
DICOM 영상을 임상 데이터와 매칭하는 v4 파이프라인.

### 모듈 구성

| 파일 | 역할 |
|------|------|
| `config.py` | 모달리티별 설정, 경로, 상수 |
| `inventory.py` | DCM 디렉토리 스캔 → 모달리티별 인벤토리 |
| `matching.py` | 이미지-ADNIMERGE 매칭 (핵심 로직) |
| `merge.py` | `*_unique.csv` → `MERGED.csv` 병합 |
| `run_pipeline.py` | CLI 오케스트레이션 |
| `utils.py` | 로깅, 경로 추출, DICOM 유틸 |

### 매칭 로직

1. DCM 인벤토리에서 모달리티별 피험자/시리즈 수집
2. 경로에서 촬영일(AQUDATE), ImageUID, SeriesUID 추출
3. ADNIMERGE에서 가장 가까운 방문(EXAMDATE) 매칭
4. `VISCODE_FIX = 촬영일 - EXAMDATE_bl` → 표준 방문 시점 매핑 (m000, m006, m012...)
5. MRIQC에서 프로토콜 정보, DCM에서 TE/TR/TI 추출
6. `_all.csv` (전체) → `_unique.csv` (PTID×VISCODE 중복 제거) → `MERGED.csv`

### 지원 모달리티 (12개 + 미실행)

**매칭 완료**: T1, AV45_8MM/6MM, AV1451_8MM/6MM, FBB_6MM, FLAIR, T2_FSE/TSE/STAR, T2_3D, MK6240_6MM

**미실행**: DTI, DTI_MB, FMRI, HIPPO, ASL, NAV4694_6MM, PI2620_6MM

### 실행

```bash
# 전체 파이프라인
python -m adni_matching.run_pipeline --adnimerge /path/to/ADNIMERGE.csv --output /path/to/output

# 특정 모달리티만
python -m adni_matching.run_pipeline --modalities T1 AV45_6MM

# 병합만 (이미 매칭된 CSV가 있을 때)
python -m adni_matching.run_pipeline --merge-only --output /path/to/output
```

### 출력

| 파일 | 설명 |
|------|------|
| `{MOD}_all.csv` | 모달리티별 전체 매칭 결과 (중복 포함) |
| `{MOD}_unique.csv` | PTID×VISCODE 중복 제거 (error 행 제외) |
| `MERGED.csv` | 전체 모달리티 통합 (13,042행 × 782열, 3,278 피험자) |

### `_all.csv` vs `_unique.csv`

- **`_all.csv`**: 매칭된 모든 결과. 동일 피험자-방문에 여러 스캔이 있으면 중복 행 포함, VISCODE 매핑 실패(`error`) 행 포함.
- **`_unique.csv`**: PTID × VISCODE_FIX 조합당 1행만 유지 (중복 시 마지막 항목, error 행 제외). MERGED.csv는 이 파일들을 병합하여 생성.

### 레퍼런스 코드 (`orig/`)

`ADNI.py`와 `params.py`는 XML 기반의 기존 매칭 코드로, 로직 참조용으로만 보관한다. 수정하지 않는다.

---

## 4. scripts (유틸리티)

| 파일 | 역할 |
|------|------|
| `compare_merged.py` | 생성된 MERGED.csv를 레퍼런스와 비교 검증 |
| `remap_proc_viscode.py` | N4/VA/FastSurfer 전처리 결과를 VISCODE 기반으로 재구성 |
| `reorganize_proc_t1.py` | PROC/T1 디렉토리를 PTID/VISCODE_FIX 구조로 재배치 |

---

## 5. Validation (이전 매칭과의 비교)

v4 파이프라인 결과를 기존 XML 기반 매칭 결과(ref)와 비교 검증하였다.
상세 리포트는 `docs/` 디렉토리 참조.

### ADNI1/GO/2/3 (ref 대비)

| 항목 | 결과 |
|------|------|
| 공통 행 (PTID+VISCODE) | 11,692 (ref 커버리지 99.8%) |
| T1 ImageUID 일치 | **100.0%** (11,018/11,021) |
| PET ImageUID 일치 (AV45/AV1451/FBB) | **100.0%** |
| T2_FSE ImageUID 일치 | 99.5% |
| T2_TSE/STAR ImageUID 일치 | 99.9% |
| 촬영일(AQUDATE) 일치 | 전 모달리티 **100.0%** |

### ADNI4 (ref 대비, AQUDATE 기준)

| 모달리티 | 일치율 | 비고 |
|----------|--------|------|
| PET (AV45/AV1451/FBB/MK6240) | **100.0%** | — |
| T2_3D | **100.0%** | — |
| FLAIR | 96.9% | VISCODE 체계 차이 영향 |
| T1 | 89.2% | VISCODE 차이 + 다중 시리즈 선택 차이 |
| T2_STAR | 26.6% | 세션당 최대 10 시리즈, VISCODE 차이 증폭 |

ADNI4의 낮은 일치율은 **VISCODE 체계 차이** (ref: `4_sc/4_init/4_m12`, new: `m000/m003/m012`)에 기인하며, 파이프라인 버그가 아니다.

### 임상 변수 (ADNIMERGE)

| 범주 | 일치율 | 비고 |
|------|--------|------|
| 인구통계 (SITE, PTEDUCAT 등) | **100%** | — |
| 인지검사 (CDRSB, FAQ 등) | **99.9%+** | .rda 데이터 업데이트 |
| DX_bl (기저 진단) | **91.3%** | ARM.rda 연동 (ADNI3 ARM 미포함 8.7%) |
| MRI 용적 (Hippocampus/ICV) | **~93%** | UCSFFSX51 primary (FS 5.1) |
| CSF 바이오마커 | ~7-10% | Luminex→Elecsys 플랫폼 교체 (의도된 변경) |

상세: [`docs/matching_validation_report.md`](docs/matching_validation_report.md), [`docs/column_diff_report.md`](docs/column_diff_report.md)

---

## 의존성

```
pip install -r requirements.txt
```

| 패키지 | 용도 |
|--------|------|
| numpy | 수치 연산 |
| pandas | 데이터 처리 |
| pydicom | DICOM 메타데이터 추출 |
| pyreadr | .rda 파일 읽기 |
| joblib | 병렬 처리 |

---

## 데이터 흐름

```
ADNIMERGE2/data/*.rda (217개)
    │
    ▼  adnimerge_py
ADNIMERGE_{DATE}.csv + MRIQC.csv + APOERES.csv
    │
    ▼  adni_matching
DCM 인벤토리 + ADNIMERGE 매칭
    │
    ▼
{MOD}_all.csv → {MOD}_unique.csv → MERGED.csv
```
