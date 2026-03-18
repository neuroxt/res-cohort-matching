# res-cohort-matching

뇌영상 코호트의 임상 데이터 추출 + DICOM/NII 매칭 파이프라인.

LONI에서 제공하는 원본 데이터(R 패키지, CSV)를 Python으로 추출하고,
NFS 서버의 영상 파일과 매칭하여 연구에 바로 사용할 수 있는 통합 CSV를 생성합니다.

---

## 지원 코호트

| 코호트 | 패키지 | 영상 | 상태 |
|--------|--------|------|------|
| **ADNI** GO/1/2/3/4 | `src/adni/` | DICOM | Active |
| **A4/LEARN** | `src/a4/` | NIfTI | Active |
| **NACC** | `src/nacc/` | — | Planned |

---

## 빠른 시작

### 1. 설치

```bash
pip install -e .
```

### 2. ADNI 파이프라인

```bash
# Step 1: .rda → CSV 추출 + ADNIMERGE 빌드 (tables/, ADNIMERGE, UCBERKELEY, birth_dates)
adni-extract --all

# Step 2: DICOM 매칭 → MERGED.csv
adni-match --modality T1,AV45_6MM

# Step 2 (이미 매칭된 CSV가 있다면): MERGED.csv만 재생성
adni-match --merge-only
```

### 3. A4/LEARN 파이프라인

```bash
# 전체 파이프라인 (BASELINE + MERGED + longitudinal + imaging availability)
a4-pipeline

# 특정 모달리티만
a4-pipeline --modality T1,FBP

# 개별 단계만 재생성
a4-pipeline --baseline-only           # BASELINE.csv만
a4-pipeline --longitudinal-only       # MMSE/CDR longitudinal + imaging availability
a4-pipeline --merge-only              # MERGED.csv만
a4-pipeline --inventory-only          # NII inventory만
a4-pipeline --clinical-only           # 임상 테이블만

# amyloidNE (스크리닝 탈락) 포함
a4-pipeline --include-screen-fail
```

---

## 프로젝트 구조

```
res-cohort-matching/
│
├── src/
│   ├── adni/                      # ADNI 코호트
│   │   ├── config.py              #   공통 NFS 경로 설정
│   │   ├── extraction/            #   Part 1: .rda → CSV 추출
│   │   │   ├── build_adnimerge.py #     ADNIMERGE + UCBERKELEY 빌드
│   │   │   ├── rda_converter.py   #     .rda → CSV 일괄 변환
│   │   │   └── cli.py             #     CLI (adni-extract)
│   │   └── matching/              #   Part 2: DICOM 매칭
│   │       ├── config.py          #     모달리티별 설정
│   │       ├── inventory.py       #     DCM 디렉토리 스캔
│   │       ├── matching.py        #     이미지-임상 매칭 로직
│   │       ├── merge.py           #     *_unique.csv → MERGED.csv
│   │       ├── cli.py             #     CLI (adni-match)
│   │       └── reference/         #     레퍼런스 코드 (수정 금지)
│   │
│   └── a4/                        # A4/LEARN 코호트
│       ├── config.py              #   NFS 경로, 모달리티, JSON 필드맵
│       ├── inventory.py           #   NII 폴더 스캔 → JSON inventory
│       ├── clinical.py            #   임상 CSV → 통합 DataFrame
│       ├── pipeline.py            #   모달리티 CSV + merge
│       └── cli.py                 #   CLI (a4-pipeline)
│
├── vendor/                        # 원본 데이터 패키지 (수정 금지)
│   └── ADNIMERGE2/                #   LONI ADNIMERGE2 R 패키지 (v0.1.1)
│
├── scripts/                       # 분석 및 유틸리티 스크립트
├── docs/                          # 데이터 카탈로그, 컬럼 사전 등
└── pyproject.toml
```

---

## NFS 출력 구조

각 코호트의 파이프라인은 NFS 서버에 아래 구조로 결과를 저장합니다.

### ADNI → `ADNI_New/ORIG/DEMO/`

```
DEMO/
├── ADNIMERGE_{DATE}.csv             ADNIMERGE 통합 CSV (23,479행 × 132열)
├── UCBERKELEY*_{DATE}.csv           PET quantification (FDG, AMY, TAU, TAUPVC)
├── birth_dates.csv                  추정 생년월일
│
├── tables/                          .rda → CSV 1:1 변환 (212개)
│   ├── REGISTRY.csv                   방문 레지스트리
│   ├── PTDEMOG.csv                    인구통계
│   ├── APOERES.csv                    APOE 유전형
│   ├── MRIQC.csv                      MRI QC 프로토콜
│   ├── DXSUM.csv                      진단 요약
│   └── ...
│
└── matching/                        DICOM 매칭 결과
    ├── MERGED.csv                     전체 모달리티 통합 (13,042행 × 782열)
    ├── {MOD}_unique.csv               모달리티별 (PTID×VISCODE 중복 제거)
    ├── {MOD}_all.csv                  모달리티별 (전체, 중복 포함)
    ├── dcm_inventory.json             DCM 메타데이터 인벤토리
    └── matching.log
```

### A4/LEARN → `A4/ORIG/DEMO/`

**A4 Study** (Anti-Amyloid Treatment in Asymptomatic Alzheimer's)는 인지적으로 정상이지만
뇌 아밀로이드가 축적된 고령자를 대상으로 한 Phase 3 임상시험입니다 (Solanezumab, Eli Lilly).
**LEARN**은 아밀로이드 음성 대조군의 관찰 연구입니다.

| 코호트 | N | 아밀로이드 | 영상 |
|--------|---|-----------|------|
| **amyloidE** (A4 Trial) | 1,323 | 양성 (SUVr ≥ 1.15) | PET + MRI + Tau PET 서브셋 |
| **LEARN amyloidNE** | 567 | 음성 | PET + MRI |
| **amyloidNE** (screen fail) | 2,596 | 음성 | PET만 (MRI 없음) |

자세한 프로토콜은 [`docs/A4_protocol.md`](docs/A4_protocol.md) 참조.

#### 출력 CSV 안내

파이프라인이 생성하는 CSV를 용도에 따라 골라 쓰세요:

| 파일 | 용도 | 행 단위 | 규모 |
|------|------|---------|------|
| **`BASELINE.csv`** | cross-sectional 분석, 코호트 기술통계 | **피험자당 1행** (BID) | ~1,890행 |
| **`MERGED.csv`** | 전체 세션 longitudinal 분석 | 세션당 1행 (BID × SESSION_CODE) | ~89K행 |
| **`MMSE_longitudinal.csv`** | MMSE 시계열 분석 | 측정당 1행 | ~26K행 |
| **`CDR_longitudinal.csv`** | CDR 시계열 분석 | 측정당 1행 | ~15K행 |
| **`imaging_availability.csv`** | 세션별 영상 보유 현황 | 세션당 1행 | ~11K행 |

> **처음 시작하는 연구자라면** `BASELINE.csv`부터 보세요.
> 피험자당 1행으로 demographics, 아밀로이드 PET, MRI 볼륨, 인지검사, 혈액 바이오마커가 모두 들어있습니다.

#### BASELINE.csv 주요 컬럼

| 컬럼 그룹 | 예시 | 소스 시점 |
|-----------|------|-----------|
| Demographics | PTGENDER, PTAGE, PTEDUCAT, APOEGN | screening |
| Amyloid PET | AMY_STATUS_bl, AMY_SUVR_bl, AMY_CENTILOID_bl | V2 (PET scan) |
| 인지검사 | MMSE, CDGLOBAL, CDRSB | **V6** (randomization) |
| MRI 볼륨 | VMRI_*_bl (50 ROI, NeuroQuant) | V4 (baseline MRI) |
| Tau PET | TAU_*_bl (272 ROI, 서브셋 ~447명) | V4 |
| 혈액 | PTAU217_BL, ROCHE_* (GFAP, NfL, pTau181 등) | screening |
| 영상 경로 | T1_NII_PATH, FBP_NII_PATH, FTP_NII_PATH | V2/V4 |

> **V1~V6 = 하나의 baseline**: A4에서는 screening(V1~V5) + randomization(V6)을 거쳐
> 최종 baseline이 확정됩니다. BASELINE.csv는 이를 피험자당 1행으로 통합한 것입니다.

#### imaging_availability.csv 예시

| BID | SESSION_CODE | DAYS_CONSENT | T1 | FLAIR | FBP | FTP | ... |
|-----|-------------|-------------|----|----|----|----|-----|
| B10081264 | 002 | 0 | 0 | 0 | 1 | 0 | ... |
| B10081264 | 004 | 14 | 1 | 1 | 0 | 1 | ... |
| B10081264 | 027 | 365 | 1 | 1 | 0 | 0 | ... |

1 = 해당 세션에 NII 파일 존재, 0 = 없음. 어떤 피험자가 어떤 시점에 어떤 영상을 보유하는지 한눈에 파악할 수 있습니다.

#### 디렉토리 구조

```
DEMO/matching/
├── BASELINE.csv                     피험자당 1행 baseline (~1,890행 × 371열)
├── MERGED.csv                       전체 세션 통합 (~89K행)
├── MMSE_longitudinal.csv            MMSE 시계열 (~26K행)
├── CDR_longitudinal.csv             CDR 시계열 (~15K행)
├── imaging_availability.csv         영상 보유 현황 (~11K행)
├── {MOD}_unique.csv                 모달리티별 매칭 결과
├── clinical_table.csv               통합 임상 테이블 (중간 산출물)
├── nii_inventory.json               NII 인벤토리
└── a4_pipeline.log
```

---

## `tables/` 디렉토리 안내

`tables/`에 있는 CSV들은 ADNIMERGE2 R 패키지의 `.rda` 파일을 Python(`pyreadr`)으로 변환한 것입니다.
각 테이블의 컬럼 정의와 코딩 규칙을 이해하려면 LONI에서 제공하는 문서를 참조하세요:

| 자료 | 링크 |
|------|------|
| LONI Data Dictionary | https://adni.loni.usc.edu/data-dictionary/ |
| 테이블별 문서 (.html, Methods PDF) | https://adni.bitbucket.io/reference/ |
| ADNIMERGE2 R 패키지 문서 | https://atri-biostats.github.io/ADNIMERGE2 |

> LONI Data Dictionary의 PDF 다운로드에는 LONI 계정이 필요합니다.
> 계정이 없다면 https://ida.loni.usc.edu 에서 신청할 수 있습니다.

---

## 코호트별 상세 문서

### ADNI
| 문서 | 내용 |
|------|------|
| [`src/adni/README.md`](src/adni/README.md) | 데이터 흐름, 12단계 빌드, 매칭 로직, 검증 결과 |
| [`src/adni/extraction/README.md`](src/adni/extraction/README.md) | ADNIMERGE 빌드 상세, 레퍼런스 대비 재현성 검증 |

### A4/LEARN
| 문서 | 내용 |
|------|------|
| [`docs/A4_protocol.md`](docs/A4_protocol.md) | 연구 프로토콜, 코호트 구조, 방문 체계, 영상/바이오마커 |
| [`docs/A4_data_catalog.md`](docs/A4_data_catalog.md) | NFS 93 CSV + 20 PDF 전체 파일 카탈로그 |
| [`docs/A4_column_dictionary.md`](docs/A4_column_dictionary.md) | MERGED.csv 출력 컬럼 사전 |
| [`docs/A4_viscode_reference.md`](docs/A4_viscode_reference.md) | VISCODE ↔ SESSION_CODE 전체 매핑 (152개) |
| [`docs/A4_join_relationships.md`](docs/A4_join_relationships.md) | 파일 간 조인 키·관계도·파이프라인 흐름 |

---

## CLI 명령어 요약

| 명령어 | 설명 |
|--------|------|
| `adni-extract` | ADNIMERGE2 .rda → CSV 추출 (tables, ADNIMERGE, UCBERKELEY, birth_dates) |
| `adni-match` | ADNI DICOM 매칭 → MERGED.csv |
| `a4-pipeline` | A4/LEARN NII inventory + clinical → MERGED.csv |

각 명령어에 `--help`를 붙이면 전체 옵션을 확인할 수 있습니다.

---

## 의존성

| 패키지 | 용도 |
|--------|------|
| numpy | 수치 연산 |
| pandas | 데이터 처리 |
| pydicom | DICOM 메타데이터 추출 (ADNI) |
| pyreadr | .rda 파일 읽기 |
| joblib | 병렬 처리 |

```bash
pip install -e .          # 개발 모드 설치 (의존성 자동 설치)
pip install -r requirements.txt  # 또는 직접 설치
```

Python >= 3.9 필요.
