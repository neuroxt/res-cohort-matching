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

A4(아밀로이드 양성 임상시험) + LEARN(아밀로이드 음성 관찰연구). NIfTI 기반.

> **A4 데이터를 처음 쓰신다면** [`src/a4/README.md`](src/a4/README.md)를 먼저 읽어주세요.
> 어떤 CSV를 써야 하는지, 어떤 문서를 참고해야 하는지 안내되어 있습니다.
> A4는 V1~V6을 하나의 **Baseline**으로 통합하여 사용합니다 (상세는 위 링크 참조).

```
DEMO/matching/
├── BASELINE.csv                     피험자당 1행 baseline (~1,890행)
├── MERGED.csv                       전체 세션 통합 (~89K행)
├── MMSE/CDR_longitudinal.csv        시계열 인지검사
├── imaging_availability.csv         세션별 영상 보유 현황
├── nii_inventory.json               NII 인벤토리
└── unique/                          모달리티별 매칭 결과
    ├── T1_unique.csv
    └── ...
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
| [`src/a4/README.md`](src/a4/README.md) | **시작 가이드** — CSV 선택, 참고 문서, BASELINE 상세, ADNI 차이점 |
| [`docs/a4/baseline_csv.md`](docs/a4/baseline_csv.md) | BASELINE.csv 컬럼 사전 (369열 상세, 알려진 제한사항) |
| [`docs/a4/protocol.md`](docs/a4/protocol.md) | 연구 프로토콜, 코호트 구조, 방문 체계, 영상/바이오마커 |
| [`docs/a4/column_dictionary.md`](docs/a4/column_dictionary.md) | MERGED.csv 출력 컬럼 사전 |
| [`docs/a4/data_catalog.md`](docs/a4/data_catalog.md) | NFS 원본 파일 카탈로그 |
| [`docs/a4/viscode_reference.md`](docs/a4/viscode_reference.md) | VISCODE <-> SESSION_CODE 매핑 |
| [`docs/a4/join_relationships.md`](docs/a4/join_relationships.md) | 파일 간 조인 키, 관계도 |

### OASIS3
| 문서 | 내용 |
|------|------|
| [`docs/oasis3/data_catalog.md`](docs/oasis3/data_catalog.md) | 24 CSV 마스터 인벤토리 |
| [`docs/oasis3/protocol.md`](docs/oasis3/protocol.md) | Knight ADRC, OASIS 시리즈, NACC UDS v2/v3, 모달리티/트레이서 |
| [`docs/oasis3/uds_forms.md`](docs/oasis3/uds_forms.md) | 17 UDS 폼 컬럼 그룹별 요약 + 핵심 컬럼 정의 |
| [`docs/oasis3/session_label_reference.md`](docs/oasis3/session_label_reference.md) | session label grammar, FORM 토큰, days_to_visit 의미 |
| [`docs/oasis3/demographics.md`](docs/oasis3/demographics.md) | OASIS3_demographics.csv 19컬럼 1:1 사전 |
| [`docs/oasis3/pet_imaging.md`](docs/oasis3/pet_imaging.md) | PET 3 파일, 트레이서, Centiloid + PUP |
| [`docs/oasis3/file_index.md`](docs/oasis3/file_index.md) | NIfTI 인벤토리 + 세션 매칭 |
| [`docs/oasis3/join_relationships.md`](docs/oasis3/join_relationships.md) | 키 계층, 조인 패턴, 카디널리티 |

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
