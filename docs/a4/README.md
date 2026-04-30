# A4 / LEARN — 데이터 문서 인덱스

**A4 (Anti-Amyloid Treatment in Asymptomatic Alzheimer's)** 는 Eli Lilly 가 운영한 Phase 3 무작위 임상시험 (solanezumab vs placebo, 2014–2023, 67 sites US/CA/AU/Japan, NCT02008357). cognitively normal 65–85세에서 amyloid PET 양성 (florbetapir SUVr ≥ 1.15) 인 1,323명 (`amyloidE`) 을 무작위 배정. 1차 결과는 **음성** (JAMA Neurology 2020) — solanezumab 가 인지 저하 / amyloid 감소를 유의미하게 늦추지 못함. 이미지/임상 데이터셋은 학술 활용을 위해 release 됨.

**LEARN (Longitudinal Evaluation of Amyloid Risk and Neurodegeneration)** 는 A4와 동일 protocol 의 amyloid-negative 관찰 연구 (Alzheimer's Association + GHR Foundation 운영). 567명. A4 와 LEARN 둘 다 PRV2 release (11Aug2025) 기반.

> **시작 가이드 (파이프라인 + CSV 선택)**: [`src/a4/README.md`](../../src/a4/README.md)
>
> 본 폴더 (`docs/a4/`) 는 출력 CSV 컬럼 사전 / NFS 인벤토리 / 분석 reference 만 다룬다. 파이프라인 사용법 / CSV 선택 / BASELINE 통합 규칙 / ADNI 와의 차이는 위 src 측 README 참조.

> **NFS 기준 경로** (macOS 마운트 기준):
> - 임상 / 메타 / 정량화: `/Volumes/nfs_storage/A4/ORIG/DEMO/`
> - 원본 NIfTI: `/Volumes/nfs_storage/A4/ORIG/NII/` (또는 `Raw Data/` 하위)
> - 파이프라인 출력: `/Volumes/nfs_storage/A4/ORIG/DEMO/matching/`
>
> Windows / Linux 는 마운트 root만 본인 환경에 맞게 치환.

---

## 한 눈에 보기

| 항목 | 값 |
|------|---|
| Subject 키 | `BID` (subject ID) |
| Visit 키 | `(BID, VISCODE)` 또는 `(BID, SESSION_CODE)` (3-digit zero-padded) |
| Visit 체계 | V1–V5 (screening) / V6 (baseline=randomization) / V7–V66 (treatment) / V997 (OLE) / V999 (ET) |
| 진단 그룹 | `amyloidE` (A4 randomized, n=1,323) / `LEARN amyloidNE` (n=567) / `amyloidNE` (screen fail, PET only, n=2,596) |
| Subject 수 | A4 1,890 + LEARN observational; 전체 ~6,945 (PRV2 demographics) |
| BASELINE.csv | ~1,890행 × **369열** (피험자당 1행, V1–V6 통합) |
| MERGED.csv | ~89K행 (전 세션 long-format) |
| VISCODE 매핑 | 152개 (`docs/a4/viscode_reference.md`) |
| 모달리티 | Amyloid PET (florbetapir, 100%) / T1 / FLAIR / Tau PET (FTP, A4 392 + LEARN 55 subset) |
| 동의 | 단일 NIA-A4 access (DUA), commercial / academic 분리 없음 |
| Release | PRV2 11Aug2025 |
| 1차 결과 publication | Sperling et al., *JAMA Neurology* 2023; Tariot et al., *JAMA Neurology* 2020 (futility analysis) |
| Trial registry | [NCT02008357](https://clinicaltrials.gov/study/NCT02008357) |

---

## 문서 목록

### 시작점

| 문서 | 언제 읽나요? |
|------|-------------|
| [`../../src/a4/README.md`](../../src/a4/README.md) | **반드시 먼저** — CSV 선택, 파이프라인 사용법, BASELINE 통합 규칙, ADNI 와의 차이 |
| [`data_catalog.md`](data_catalog.md) | NFS 원본 파일 카탈로그 (93 CSV + 20 PDF) — 소스 데이터 위치 찾을 때 |
| [`protocol.md`](protocol.md) | 연구 프로토콜, 코호트 구조, 방문 체계 (V1~V9), 영상 / 바이오마커 — A4 데이터 구조 처음 접할 때 |
| [`join_relationships.md`](join_relationships.md) | 파일 간 조인 키, 관계도 — 파이프라인 로직 이해할 때 |

### 출력 CSV 사전

| 문서 | 내용 |
|------|------|
| [`baseline_csv.md`](baseline_csv.md) | `BASELINE.csv` 컬럼 사전 (369열 상세, 알려진 제한사항: PTAGE 8.4% NaN, CDR=V1, MMSE=V6) — **cross-sectional 분석 시작점** |
| [`column_dictionary.md`](column_dictionary.md) | `MERGED.csv` 출력 컬럼 사전 (~400개) — 전 세션 long-format 분석 시 |

### 데이터 종류별 reference

| 문서 | 내용 |
|------|------|
| [`viscode_reference.md`](viscode_reference.md) | VISCODE ↔ SESSION_CODE 매핑 (152개 — V1~V5 screening, V6 baseline, V7~V66 treatment, V997 OLE, V999 ET) |
| [`tau_suvr_sources.md`](tau_suvr_sources.md) | Tau PET SUVR 3-pipeline 비교 (Stanford / Avid-Clark / PetSurfer) — Tau 분석 source 선택 시 |
| [`csv_profiles.md`](csv_profiles.md) | 컬럼 프로파일 (타입, null률, 값 범위) — 데이터 품질 확인할 때 |

---

## 다른 코호트와의 차이

| 항목 | A4 / LEARN | NACC | OASIS3 | ADNI | KBASE |
|------|-----------|------|--------|------|-------|
| 코호트 디자인 | **Phase 3 RCT (solanezumab vs placebo)** + observational | 관찰 (29+ ADRCs 통합) | 관찰 (single ADRC retrospective) | 관찰 (multi-site fixed cohort) | 관찰 (single 한국 site) |
| Subject ID | `BID` | `NACCID` (`NACC` + 6 digits) | `OASISID` (`OAS3xxxx`) | `RID` / `PTID` | `SU####` / `BR####` |
| Visit 키 | **`VISCODE` (정수) ↔ `SESSION_CODE` (3-digit string)** | `(NACCID, NACCVNUM, PACKET)` | `(OASISID, days_to_visit)` | `VISCODE` (BL/M06/...) | `K_visit` ∈ {0..4} |
| 임상 framework | **A4 자체** (PACC center-stage, MMSE/CDR baseline-only) | NACC UDS v1–v4 | NACC UDS v2/v3 | ADNI 자체 (subset of UDS) | 한국어 자체 CRF |
| Cognitive primary | **PACC** (Preclinical Alzheimer Cognitive Composite) | UDS C1 battery | UDS C1 battery | ADAS-Cog + MMSE | 한국형 SNSB / NP1+NP2 |
| Amyloid 양성 정의 | **florbetapir SUVr ≥ 1.15** (study-specific) | 코호트 전체 변동 (CL ≥ 24 표준) | PIB / AV45 + PUP | UCBERKELEY centiloid + cutoff | PiB SUVR 1.40 (Inferior Cerebellar) |
| 통합 export | **BASELINE (1 row/subj) + MERGED (all sessions)** | NeuroXT-built `merged.csv` (390 col) | per-form CSVs (24 파일) | `ADNIMERGE.csv` | `masterfile.csv` |
| 동의 tier | 단일 (NIA-A4) | Commercial vs Investigator | 단일 (open + DUA) | 단일 (LONI DUA) | 단일 |
| 운영 기관 | NIA + Eli Lilly + Alzheimer's Association | NIA / NACC | WUSTL Knight ADRC | NIA + 산업 | SNUBH/SNU |

---

## 알려진 limitations & quirks

문서 작성 시점에 NFS 데이터를 직접 inspect 하여 확인된 항목:

1. **Baseline 의 multi-visit 통합.** A4 는 V1 (screening), V2 (PET), V4 (MRI), V6 (randomization) 가 시점이 다른데 `BASELINE.csv` 는 이 모두를 "Baseline" 으로 통합. CDR 은 **V1 값**, MMSE 는 **V6 값**, Amyloid 는 **V2 값**, MRI volumes 는 **V4 값**. 자세한 source 시점은 [`baseline_csv.md`](baseline_csv.md).
2. **LEARN 은 V4 가 아닌 V6 에 MRI 촬영.** 파이프라인이 자동 처리하지만 raw 데이터 분석 시 주의.
3. **`PTAGE` 8.4% NaN (159명).** V6 세션 미시행 (early termination 등) 시 결측. Fallback: `AGEYR` (screening 나이) 을 사용하면 100% 채움.
4. **`CDGLOBAL` 전원 0.0** (A4 등록 기준이 CDR=0). cross-sectional 분류에는 무용. `CDRSB` 가 0~2.0 분포.
5. **Tau PET subset 만.** A4 1,323 중 392명 (29.6%), LEARN 567 중 55명 (9.7%). longitudinal Tau 분석 시 매우 적은 sample.
6. **`amyloidNE` (screen fail) 는 PET only.** 2,596명이지만 MRI / 인지 longitudinal 데이터 없음. amyloid screening 분석에만 사용 가능.
7. **VISCODE 정수 ↔ SESSION_CODE string 변환 주의.** `VISCODE=6` → `SESSION_CODE='006'` (zero-padded). VISCODE 700+ 은 그대로 (`997` → `'997'`).
8. **MMSE = V6 baseline only** (V1 에서는 측정 안 함). longitudinal 인지 trajectory 는 PACC 사용.
9. **A4 release 데이터 = de-identified.** 모든 날짜 = `_DAYS_CONSENT` (동의일 기준 일수) 또는 `_DAYS_T0` (A4 무작위배정일 / LEARN baseline registry 일 기준). 절대 날짜 정보 없음.
10. **ARIA (amyloid-related imaging abnormalities) 발생자.** Solanezumab 군에서 ARIA-E / ARIA-H 발생자 데이터가 release 에 포함됨. 분석 시 별도 카테고리로 처리 권장.
11. **PRV2 = partial release** (screening / baseline 위주). 전체 longitudinal raw 는 `Raw Data/` 디렉토리 참조.

---

## 작성 컨벤션

- 한국어 본문 + 영어 기술 용어 (변수명, CRF명, 코드값은 영어 그대로) — 다른 코호트 컨벤션과 동일.
- 모든 사실은 NFS 원본 inspection 결과 기반. 새 사실 추가 시 inspection 명령과 결과 함께 commit.
- 컬럼명은 백틱 (`BID`) 으로 감싸 고정 폭. 한국어 라벨이 있을 땐 슬래시 병기.
- **파이프라인 / CSV 선택 / 사용 가이드는 `src/a4/README.md` 한 곳**. `docs/a4/` 는 *출력 CSV 컬럼 사전 / 데이터 reference* 전담. 두 README 가 같은 정보를 중복으로 담지 않는다.
- "Known limitations" 섹션은 모든 문서에 포함. quirk 발견 시 즉시 추가.
