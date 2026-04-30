# 데이터 카탈로그 / 컬럼 사전 인덱스

ADNI_match repo의 코호트별 데이터 문서 인덱스. 각 코호트마다 NFS 원본 파일 카탈로그, 프로토콜 배경, 컬럼 사전, 조인 관계, 그 외 분석 가이드를 모아두었다.

> **NFS 기준 경로**:
> - ADNI: `/Volumes/nfs_storage/ADNI/...`
> - A4/LEARN: `/Volumes/nfs_storage/A4/ORIG/...`
> - OASIS3: `/Volumes/nfs_storage/OASIS3/ORIG/...`
> - NACC: `/Volumes/nfs_storage/NACC_NEW/ORIG/...`
> - KBASE: `/Volumes/nfs_storage/KBASE/ORIG/Demo/`

---

## 코호트별 문서

### 🧠 A4 / LEARN — Anti-Amyloid Treatment in Asymptomatic AD

A4는 RCT (solanezumab vs placebo, 무작위배정), LEARN은 amyloid-negative observational. 둘 다 PRV2 릴리스(11Aug2025) 기반.

→ **시작 가이드**: [`src/a4/README.md`](../src/a4/README.md)
→ **데이터 디렉터리**: [`docs/a4/`](a4/)

| 문서 | 언제 읽나요? |
|------|-------------|
| [`a4/data_catalog.md`](a4/data_catalog.md) | NFS 원본 파일 카탈로그 (93 CSV + 20 PDF) — 소스 데이터 위치 찾을 때 |
| [`a4/protocol.md`](a4/protocol.md) | 연구 프로토콜, 코호트 구조, 방문 체계 (V1~V9), 영상/바이오마커 — A4 데이터 구조 처음 접할 때 |
| [`a4/baseline_csv.md`](a4/baseline_csv.md) | BASELINE.csv 컬럼 사전 (369열 상세, 알려진 제한사항) — cross-sectional 분석 시작점 |
| [`a4/column_dictionary.md`](a4/column_dictionary.md) | MERGED.csv 출력 컬럼 사전 (~400개) — 특정 컬럼 의미 찾을 때 |
| [`a4/viscode_reference.md`](a4/viscode_reference.md) | VISCODE ↔ SESSION_CODE 매핑 (152개) — SESSION_CODE가 어떤 방문인지 알고 싶을 때 |
| [`a4/join_relationships.md`](a4/join_relationships.md) | 파일 간 조인 키, 관계도 — 파이프라인 로직 이해할 때 |
| [`a4/csv_profiles.md`](a4/csv_profiles.md) | 컬럼 프로파일 (타입, null률, 값 범위) — 데이터 품질 확인할 때 |
| [`a4/tau_suvr_sources.md`](a4/tau_suvr_sources.md) | Tau PET SUVR 3-pipeline 비교 (Stanford / Avid-Clark / PetSurfer) — Tau 분석 소스 선택 시 |

---

### 🧠 OASIS3 — Open Access Series of Imaging Studies, Release 3

WUSTL Knight ADRC의 1,378명 retrospective 통합 (30년+, MRI + PET + clinical/cognitive). 임상 데이터는 NACC UDS 폼 형식.

→ **데이터 디렉터리**: [`docs/oasis3/`](oasis3/)

| 문서 | 언제 읽나요? |
|------|-------------|
| [`oasis3/data_catalog.md`](oasis3/data_catalog.md) | 24 CSV 마스터 인벤토리 — OASIS3 처음 접할 때 |
| [`oasis3/protocol.md`](oasis3/protocol.md) | Knight ADRC 배경, OASIS 시리즈, UDS v2/v3, 모달리티 / PET 트레이서 — 연구 맥락 이해할 때 |
| [`oasis3/uds_forms.md`](oasis3/uds_forms.md) | 17 NACC UDS 폼 (a1-d2) 컬럼 그룹별 요약 + 핵심 컬럼 정의 — 임상 데이터 분석 시 |
| [`oasis3/session_label_reference.md`](oasis3/session_label_reference.md) | session label grammar, FORM 토큰 (USDa3 typo, psychometrics 토큰), days_to_visit 의미 — 라벨 파싱 / 조인 키 만들 때 |
| [`oasis3/demographics.md`](oasis3/demographics.md) | OASIS3_demographics.csv 19컬럼 1:1 사전 — Subject-level baseline 정보 |
| [`oasis3/pet_imaging.md`](oasis3/pet_imaging.md) | PET 3 파일 비교, 트레이서 (PIB/AV45/AV1451/FDG), Centiloid + PUP 방법론 — 아밀로이드/타우 정량 분석 시 |
| [`oasis3/file_index.md`](oasis3/file_index.md) | NIfTI 파일 인벤토리, BIDS 명명, `*_diff` 부호 — 영상-임상 매칭 시 |
| [`oasis3/join_relationships.md`](oasis3/join_relationships.md) | 3-tier 키 계층, 조인 패턴 4종, 카디널리티 — 파이프라인 설계 시 |

---

### 🧠 NACC — National Alzheimer's Coordinating Center

NIA-funded ADRC 네트워크 (29+ centers) 의 NACC UDS 표준 통합 데이터. 2005~ 매년 1회 visit, 분기 freeze. v71 freeze 기준 55,004 subject / 205,909 visit / 6,548 imaged subject. 임상 데이터는 OASIS3와 같은 NACC UDS 표준 — UDS 폼별 컬럼 정의는 [`docs/_shared/nacc_uds_forms.md`](_shared/nacc_uds_forms.md) 한 곳에서 공유한다.

→ **데이터 디렉터리**: [`docs/nacc/`](nacc/)

| 문서 | 언제 읽나요? |
|------|-------------|
| [`nacc/README.md`](nacc/README.md) | NACC 시작점 — NFS 경로, 한 눈에 보기, 다른 코호트와 차이, 알려진 quirks |
| [`nacc/data_catalog.md`](nacc/data_catalog.md) | DEMO/NII_NEW/DCM/ZIP 마스터 인벤토리 — Commercial/Non_Commercial 페어, RDD PDF 10개 |
| [`nacc/protocol.md`](nacc/protocol.md) | 29+ ADRCs 거버넌스, UDS v1→v4 evolution, 분기 freeze, naccdata.org DUA 절차 |
| [`nacc/data_tier_reference.md`](nacc/data_tier_reference.md) | Commercial vs Investigator (Non_Commercial) 컨센트 분리 — 어느 파일 쓸지 결정할 때 |
| [`nacc/merged_csv.md`](nacc/merged_csv.md) | NeuroXT-built `merged.csv` 390-col 사전 (UDS + CSF + Amyloid PET + Tau PET 통합) |
| [`nacc/uds_forms.md`](nacc/uds_forms.md) | NACC bookkeeping 컬럼 (NACCID/NACCADC/PACKET/FORMVER/NACCVNUM), UDS 버전 deltas — 폼-level 사전은 shared 참조 |
| [`nacc/session_label_reference.md`](nacc/session_label_reference.md) | NACC visit/packet 시맨틱 ((NACCID, NACCVNUM, PACKET) 4-tuple, longitudinal 패턴) |
| [`nacc/optional_modules.md`](nacc/optional_modules.md) | FTLD3 / LBD3.1 / CSF (EE2) / SCAN MRI / SCAN PET / ADSP-PHC 122024 (8 도메인) 통합 |
| [`nacc/imaging_inventory.md`](nacc/imaging_inventory.md) | NII_NEW/ 트리, 14+ 모달리티, 6,548 imaged subjects, 임상-영상 5.9% 미스매치 |
| [`nacc/join_relationships.md`](nacc/join_relationships.md) | (NACCID, NACCVNUM, PACKET) 조인 키, merged.csv inner-join 로직, ±90일 윈도우 |

---

### 🧠 KBASE — Korean Brain Aging Study

SNUBH/SNU 기반 한국인 뇌 노화/치매 종단 코호트. 자체 한국어 CRF + 멀티모달 영상. 2014–2021 등록·추적, V0~V4 (V0/V2/V4가 imaging visit, V1/V3 임상 전용). NC 청장년/고령 + MCI + AD + 소수 atypical.

→ **데이터 디렉터리**: [`docs/kbase/`](kbase/)

| 문서 | 언제 읽나요? |
|------|-------------|
| [`kbase/README.md`](kbase/README.md) | KBASE 시작점 — visit schedule, ID 체계 (SU + BR), known quirks 요약 |
| [`kbase/data_catalog.md`](kbase/data_catalog.md) | 7 xlsx + csv 파일 → 시트 → 컬럼 3-tier 인벤토리 |
| [`kbase/protocol.md`](kbase/protocol.md) | 코호트 설계, 9 모달리티, 등록·추적 기간, ADNI/OASIS3/A4 비교 |
| [`kbase/master_columns.md`](kbase/master_columns.md) | `masterfile.{xlsx,csv}` 150-col 사전 (source 그룹화) — 통합 분석 진입점 |
| [`kbase/imaging_inventory.md`](kbase/imaging_inventory.md) | `1_KBASE1_nifti_0,2,4.xlsx` V0/V2/V4 시트 + 모달리티 가용성 인코딩 |
| [`kbase/diagnosis_demographics.md`](kbase/diagnosis_demographics.md) | `2_Diag_Demo.xlsx` simplified + Sheet1 codebook + GROUP↔y2_diag 불일치 quirk |
| [`kbase/codebook_dx.md`](kbase/codebook_dx.md) | `y2_diag` 5코드 + `y2_desc` 19코드 진단명 매핑 |
| [`kbase/apoe.md`](kbase/apoe.md) | `3_APOE.xlsx` 인코딩 + cross-cohort APOE (KBASE/ADNI/OASIS3/A4) 비교 |
| [`kbase/neuropsych_battery.md`](kbase/neuropsych_battery.md) | `4_NP.xlsx` 72-col 신경심리 (KBASE_NP1 + NP2, raw + Z) |
| [`kbase/vascular_risk_factors.md`](kbase/vascular_risk_factors.md) | `5_VascularRF.xlsx` 50 cols + JSON-string 셀 quirk |
| [`kbase/pib_positivity.md`](kbase/pib_positivity.md) | `추가_1_AB_PiB_positivity.xlsx` SUVR 1.40 cutoff + casing quirk |
| [`kbase/join_relationships.md`](kbase/join_relationships.md) | `(ID, K_visit)` 단일 join 키, master concat layout |

---

### 🧠 ADNI / ADNI 4

ADNI는 src 모듈에 가까이 두는 패턴 (ADNIMERGE 빌드 + DICOM 매칭).

| 문서 | 내용 |
|------|------|
| [`src/adni/README.md`](../src/adni/README.md) | 데이터 흐름, 12단계 빌드, 매칭 로직, 검증 결과 |
| [`src/adni/extraction/README.md`](../src/adni/extraction/README.md) | ADNIMERGE 빌드 상세, 레퍼런스 대비 재현성 검증 |

> ADNI 전용 `docs/adni/` 폴더는 아직 없음. 향후 확장 시 같은 패턴으로 추가.

---

## 폴더 구조

```
docs/
├── README.md                          # ← 이 파일 (코호트 인덱스)
├── _shared/                           # NACC↔OASIS3 공통 (NACC UDS 표준)
│   ├── nacc_uds_forms.md              #   17 UDS 폼 (A1–D2) 컬럼 정의
│   └── nacc_session_labels.md         #   PACKET 그래머, missing-code 처리
├── a4/                                # A4/LEARN 문서 (8 files)
│   ├── data_catalog.md
│   ├── protocol.md
│   ├── baseline_csv.md
│   ├── column_dictionary.md
│   ├── viscode_reference.md
│   ├── join_relationships.md
│   ├── csv_profiles.md
│   └── tau_suvr_sources.md
├── oasis3/                            # OASIS3 문서 (8 files; UDS는 _shared 참조)
│   ├── data_catalog.md
│   ├── protocol.md
│   ├── uds_forms.md                   #   OASIS3 overlay (file paths/row counts/USDa3 typo)
│   ├── session_label_reference.md     #   OASIS3 overlay (OAS3xxxx_<token>_d####, 음수 days quirk)
│   ├── demographics.md
│   ├── pet_imaging.md
│   ├── file_index.md
│   └── join_relationships.md
├── nacc/                              # NACC 문서 (10 files)
│   ├── README.md
│   ├── data_catalog.md
│   ├── protocol.md
│   ├── data_tier_reference.md
│   ├── merged_csv.md
│   ├── uds_forms.md                   #   NACC overlay (bookkeeping cols, v3↔v4 deltas)
│   ├── session_label_reference.md     #   NACC overlay (NACCVNUM, PACKET I/F/T)
│   ├── optional_modules.md
│   ├── imaging_inventory.md
│   └── join_relationships.md
└── kbase/                             # KBASE 문서 (12 files)
    ├── README.md
    ├── data_catalog.md
    ├── protocol.md
    ├── join_relationships.md
    ├── master_columns.md
    ├── imaging_inventory.md
    ├── diagnosis_demographics.md
    ├── codebook_dx.md
    ├── apoe.md
    ├── neuropsych_battery.md
    ├── vascular_risk_factors.md
    └── pib_positivity.md
```

> **`_shared/`** 폴더는 cohort-cross-cutting 표준 (NACC UDS 폼 / packet 그래머) 만 담는다. NACC 와 OASIS3 cohort docs 가 함께 참조하며, cohort-specific 사실 (file paths, row counts, session token 변형 등) 은 각 cohort 폴더의 overlay 문서에 둔다.

---

## 문서 작성 컨벤션

새 코호트 문서를 추가할 때 A4/OASIS3 패턴을 따른다:

| 표준 문서 | 역할 | 모방 reference |
|-----------|------|----------------|
| `data_catalog.md` | NFS 원본 파일 마스터 인벤토리 (파일/크기/행/컬럼/한 줄 설명) | A4/OASIS3 둘 다 |
| `protocol.md` | 연구 배경, 코호트 구조, 방문/세션 체계, 모달리티 | A4/OASIS3 둘 다 |
| `column_dictionary.md` 또는 `*_csv.md` | 출력 CSV의 컬럼 사전 | A4 (BASELINE/MERGED) |
| `*_reference.md` | VISCODE/session label 컨벤션 | A4 (viscode), OASIS3 (session_label) |
| `join_relationships.md` | 파일 간 키와 카디널리티 + 조인 패턴 | A4/OASIS3 둘 다 |

스타일:
- 한국어 본문 + 영어 기술 용어 (변수명, CRF명, 코드값은 영어 그대로)
- 표 헤더로 시작, 코딩 값은 실측으로 검증
- DOI / 저널 / 외부 PDF는 inline link로 인용
- "알려진 한계 (Known limitations)" 섹션을 두어 데이터 quirk 명시

> 작성 후 row/column 수 같은 사실은 실제 CSV로 spot-check 후 commit.
