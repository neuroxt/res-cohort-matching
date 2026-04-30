# NACC 프로토콜 / 코호트 배경

NACC (National Alzheimer's Coordinating Center) 의 운영 모델, UDS 양식의 진화, 분기 freeze 체계, 데이터 접근 절차를 정리한다. NACC 임상 데이터는 OASIS3 와 같은 UDS 표준을 따르므로 폼별 컬럼 정의는 [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) 에서 공유한다 — 본 문서는 NACC 자체의 운영 / 정책 / 시점 측면을 다룬다.

---

## 1. 거버넌스 / 자금

| 항목 | 내용 |
|------|------|
| 운영 기관 | National Alzheimer's Coordinating Center (NACC), University of Washington (Seattle) |
| 자금 | NIA (National Institute on Aging), 2005~ 지속 / 2026 5년 연장 신청 제출 완료 |
| 데이터 수집 네트워크 | 미국 NIA-funded **AD Research Centers (ADRCs)**, **29+ centers** (예: WUSTL Knight ADRC, Mayo Clinic, UCSF, Columbia, Wisconsin, ...) — 각 ADRC는 자체 P30 / P50 grant 운영 |
| 거버넌스 | Steering Committee (각 ADRC PI + NACC), Data Sharing Committee (DSC, 자료 요청 심사) |

각 ADRC는 자기 ADRC 코드 (`NACCADC` 컬럼 in UDS) 로 식별된다. 분석 시 site effect 통제 변수로 사용 가능 (random effect / fixed effect).

---

## 2. UDS (Uniform Data Set) — 표준 임상 평가

NACC가 정의하고 모든 ADRC가 매년 시행하는 표준화 임상 평가 묶음. 양식 자체는 NACC가 발행하는 **공식 RDD (Researcher's Data Dictionary)** 가 ground truth (`DEMO/Data_Directory/uds3-rdd.pdf`).

### 2.1 버전 evolution

| UDS 버전 | 도입 시점 | 주요 변화 |
|----------|----------|----------|
| **v1** | 2005-09 | 최초 도입. A1–C1 + D1 + D2 |
| **v2** | 2008 | A3 (가족력) 확장, B3 (UPDRS optional), 약물 폼 분리 |
| **v3** | 2015-03 | C1 cognitive battery 대폭 교체 (Boston Naming → MINT, Logical Memory → Craft Story, Trail Making 정밀화), D1 syndrome flag (amndem/pca/ppasyn/ftdsyn/lbdsyn) + biomarker contributory flag (amylpet/amylcsf/fdgad/hippatr/taupetad/csftau/...) 추가 |
| **v3.1** | 2017 | MoCA 추가 (`mocacomp` etc.) |
| **v4** | 2024 도입 (rolling) | 인지/기능 평가 일부 modernize, 진단 흐름 정리. v71 freeze에는 일부 v4 visit 포함 (FORMVER=4) |

> 분석 시 visit별 `FORMVER` 컬럼을 확인해 폼 버전을 식별. v2 → v3 전환 시점에 같은 subject가 두 버전 모두 거쳤을 수 있음.

### 2.2 폼 구성 (UDS v3 기준)

폼 단위 정의는 [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) 에 통합. 본 문서에서는 폼 ID 와 역할만 요약:

| 폼 | 역할 |
|----|------|
| A1 | Subject 인구통계 (visit-level) |
| A2 | Co-participant (informant) 인구통계 |
| A3 | 가족력 (Optional) |
| A4 | 약물 (Drug Code + Drug Name 페어) |
| A5 | 건강력 (CVD, neuro, metabolic, psychiatric, sleep, smoking) |
| B1 | 신체검사 |
| B2 | Hachinski Ischemic Score |
| B3 | UPDRS (PD optional) |
| B4 | CDR + MMSE + 1차 진단 |
| B5 | NPI-Q |
| B6 | GDS-15 |
| B7 | FAQ |
| B8 | 신경학적 검사 |
| B9 | Clinician 판정 증상 |
| C1 | 신경심리 battery (v2 + v3 union) |
| C2 | 추가 인지검사 (UDS v3.1+ 추가) |
| D1 | Clinician diagnosis (etiology + biomarker contributory) |
| D2 | Clinician 판정 의학 상태 |

> NACC 임상 데이터는 v71 freeze에서 이 17 폼이 *피험자 × 방문* 단위로 long-format 통합된 `investigator_ftldlbd_nacc71.csv` (205,909 행 × 1,936 열) 로 배포. 이 파일에는 추가로 **FTLD3 모듈** + **LBD3.1 모듈** 변수도 합쳐져 있다.

---

## 3. 옵셔널 모듈

| 모듈 | 폼 패키지 | 시행 조건 |
|------|----------|----------|
| **FTLD3** | FVP (Follow-up Visit Packet) + IVP (Initial Visit Packet) | FTD / PPA / CBS 의심 시 |
| **LBD 3.1** | FVP + IVP | DLB / PD-D / RBD 의심 시 |
| **CSF biomarker (EE2)** | `biomarker-ee2-csf-ded.pdf` | 요추천자 시행한 visit |
| **Imaging metadata (NACC SCAN)** | MRI / Amyloid PET / Tau PET / FDG PET | 영상 제출한 visit |
| **Genetics** | APOE flag + ADSP-PHC 12-2024 | DNA 동의 + 유전 분석 동의 |
| **Neuropathology** | NP form | 부검 동의 + 사망 |

자세한 컬럼 그룹 / 행 수 / RDD 페이지는 [`optional_modules.md`](optional_modules.md) 에 통합.

---

## 4. Visit / Packet 운영 모델

NACC visit는 **연 1회 (±6개월 윈도우)** 시행. 각 visit는 **packet** 단위로 분류:

| PACKET 코드 | 의미 |
|-------------|------|
| `I` | Initial Visit Packet — 신규 등록 후 첫 정식 visit (전체 폼 시행) |
| `F` | Follow-up Visit Packet — 후속 정기 visit (대부분 폼 + 변경분만) |
| `T` | Telephone Follow-up — 일부 인지 평가만 전화로 |

각 visit는 `(NACCID, NACCVNUM, PACKET, FORMVER, VISITMO/DAY/YR)` 로 식별. `NACCVNUM` = 1-based visit number. 분석 시 **`(NACCID, NACCVNUM)`** 페어가 일반적인 visit 키 — `PACKET` 은 visit 종류 구별용.

---

## 5. 분기 freeze 운영

| 항목 | 내용 |
|------|------|
| Cadence | 약 **3개월 (분기)** |
| 최근 freeze | 2025-10 (v71 추정) |
| 다음 freeze | 2026-03 (예정) |
| Freeze 갱신 | 신규 visit 추가 + 기존 visit 데이터 갱신 (재진단, 영상 추가, 부검 결과 update 등) |

> v71 freeze 라는 NACC 내부 버전 표기는 파일명에 `nacc71` 접미사로 노출 (예: `investigator_ftldlbd_nacc71.csv`). 분기 freeze 도중 같은 (NACCID, NACCVNUM) 행이 누적 갱신되므로 **freeze 시점 명시**가 분석 reproducibility에 중요.

---

## 6. 데이터 접근

| 단계 | 내용 |
|------|------|
| 1 | [naccdata.org](https://naccdata.org/requesting-data/nacc-data/) 에서 Quick-Access 요청 |
| 2 | DUA (Data Use Agreement) 서명 (~15분 온라인) |
| 3 | 자료 요청 폼 제출 (목적, 변수 카테고리, 인용 시 acknowledgment 약속) |
| 4 | **승인 후 48시간 이내** 데이터 다운로드 링크 수신 |
| 5 | 새 freeze 갱신 필요 시 같은 절차로 재요청 (수시) |

> NACC는 무료. ADRC 기여 데이터의 통합·관리 비용은 NIA 자금. 사용 시 **`Acknowledgment NACC + 각 ADRC P30/P50 grant`** 인용 필수 (양식은 NACC 공식 사이트).

### 6.1 동의 tier

NACC는 같은 데이터를 **두 가지 동의 tier** 로 배포:

| Tier | 의미 | 사용 권장 |
|------|------|----------|
| **Commercial** | Subject가 산업/상업 사용에 명시적 동의 | 기업/제약 협업 시 |
| **Non_Commercial = Investigator** | 학술 전용 동의 (broader 모집단) | **학술 연구 default** |

자세한 정책 / 어느 쪽 쓸지: [`data_tier_reference.md`](data_tier_reference.md).

---

## 7. 영상 (NACC SCAN)

NACC SCAN 프로젝트 (2020~) 는 ADRC 내원자의 MRI / PET 표준화 정량화 데이터를 별도 워크플로로 운영. 해당 산출물은 NACC core 분기 freeze에 SCAN MRI / SCAN PET CSV 파일로 포함:

| 모달리티 | 파일 | 정량화 방식 |
|---------|------|-------------|
| MRI QC | `*_scan_mriqc_nacc71.csv` | study/series 단위 protocol/QC flag |
| MRI SBM | `*_scan_mrisbm_nacc71.csv` | Surface-Based Morphometry (FreeSurfer-style cortical thickness/volume) |
| Amyloid PET | `*_scan_amyloidpet{gaain,npdka}_nacc71.csv` | GAAIN composite + NPDKA per-region SUVR (FreeSurfer DKT atlas) |
| Tau PET | `*_scan_taupetnpdka_nacc71.csv` | NPDKA per-region SUVR (entorhinal + meta-temporal 추가) |
| FDG PET | `*_scan_fdgpetnpdka_nacc71.csv` | NPDKA per-region SUVR |
| PET QC | `*_scan_petqc_nacc71.csv` | study-level QC pass/fail |

SCAN 파일은 임상 (UDS) 파일과 **별도 NACCVNUM 체계가 아닌 SCAN 자체 SCANDATE / TRACER 키**로 매핑. 임상-영상 join은 `(NACCID, SCANDATE ↔ VISITDATE)` ±윈도우 매칭. 자세한 처리는 [`imaging_inventory.md`](imaging_inventory.md).

NACC SCAN 표준 변수 사전: `DEMO/Data_Directory/SCAN-MRI-Imaging-RDD.pdf` (572 KB).

> NeuroXT 사내에서는 NII_NEW (BIDS-style NIfTI 변환) 도 별도로 보유. NACC가 직접 배포하는 표준 정량화 (SCAN) 와 NeuroXT 자체 파이프라인 산출물이 둘 다 분석에 사용 가능.

---

## 8. ADNI 와의 비교 (요약)

| 항목 | NACC | ADNI |
|------|------|------|
| 중심 데이터 | **임상 / 인지 / 신경병리** (NACC UDS) | **이미징** (MRI, PET) |
| 코호트 설계 | ADRC 내원자 기반 (broad) | 프로토콜 기반 고정 코호트 (CN/MCI/AD) |
| Sites | 29+ ADRCs | 60+ multi-national |
| Freeze | 분기 (~3개월) | 비정기 (이벤트 기반) |
| Genetics | APOE + ADSP-PHC | APOE + WGS |
| 동의 tier | Commercial vs Investigator | 단일 (LONI DUA) |

> NACC ↔ ADNI subject linkage (PTID ↔ NACCID 매핑) 는 별도 cross-cohort 작업이며 본 freeze에는 포함되지 않음.

---

## 9. 인용 / 참고

| 자료 | 링크 |
|------|------|
| NACC 공식 | https://www.naccdata.org/ |
| 데이터 요청 | https://naccdata.org/requesting-data/nacc-data/ |
| UDS v3 RDD | https://files.alz.washington.edu/documentation/uds3-rdd.pdf |
| UDS v3 Forms | https://www.alz.washington.edu/WEB/forms_uds.html |
| UDS v4 Updates | https://naccdata.org/nacc-collaborations/uds4-updates |
| NACC Researcher's Guide | https://www.naccdata.org/the-nacc-researchers-guide |
| NIA — NACC | https://www.nia.nih.gov/research/dn/national-alzheimers-coordinating-center-nacc |
| ADSP-PHC | https://www.niagads.org/adsp/phenotype-harmonization |
| 2024 Anniversary Review | https://pmc.ncbi.nlm.nih.gov/articles/PMC12541278/ |

UDS v3 발표 논문:

> Weintraub S, Besser L, Dodge HH, et al. *Version 3 of the National Alzheimer's Coordinating Center's Uniform Data Set*. **Alzheimer Dis Assoc Disord.** 2018;32(1):10–17.

---

## Known limitations & quirks

1. **UDS 버전 mix.** v71 freeze에는 v1/v2/v3/v4가 혼재. 같은 변수명도 버전에 따라 코딩이 다를 수 있음 (대표 예: c1 cognitive battery는 v2 → v3 전환에서 검사 자체 교체).
2. **분기 freeze 도중 visit 데이터 갱신.** 같은 (NACCID, NACCVNUM) 행이 freeze 사이에 진단/영상/부검 update로 변할 수 있음. 분석 reproducibility = freeze 시점 명시 필수.
3. **ADRC 별 site effect.** `NACCADC` 컬럼으로 식별 가능. multi-site 분석 시 통제 권장.
4. **NACC SCAN ↔ UDS 별도 timeline.** SCAN PET의 `SCANDATE` 와 UDS visit 의 `VISITDATE` 가 같은 visit이라도 며칠~몇 달 차이 가능. join 시 ±90일 윈도우 일반적.
5. **UDS v4 진입 단계.** v71 freeze에 v4 visit 일부 포함되지만 *완전한* v4 column set은 미배포. 자세한 v4 deltas는 차후 RDD 업데이트 후 본 docs에 추가 예정.
6. **부검 (NP) 데이터는 별도 폼.** UDS 폼과 분리되어 `rdd-np.pdf` 에 정의. v71 freeze에 NP 컬럼 일부가 `investigator_ftldlbd_nacc71.csv` 에 통합되어 있을 수 있음 (column scan 검증 필요).

> 검증일 2026-05-01 (freeze v71)
