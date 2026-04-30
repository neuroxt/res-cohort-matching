# KBASE 프로토콜

> 이 문서는 NFS의 데이터 inspection으로부터 추론한 내용. KBASE 공식 publication과 비교 검증 권장.

## 코호트 개요

KBASE (Korean Brain Aging Study, 한국인뇌노화연구) — 정상 노화에서 치매까지의 인지 spectrum을 종단적으로 추적하는 한국인 코호트. 구성:

| 그룹 | 정의 (y2_diag) | y2_desc | 분포 (master) |
|------|---------------|---------|--------------|
| `NC_청장년` (young NC) | 1: 청장년 정상인 | 10 | 102 |
| `NC_고령` (elderly NC) | 2: 고령 정상인 | 20 | 675 |
| `MCI` | 3: 경도인지장애 [기억상실성] | 30, 31 (aMCI-S/M) + non-amnestic 32, 33, 34 | 329 |
| `AD` | 4: NIA-AA 유력 알츠하이머병 치매 | 40 | 178 |
| 기타 | 9: 기타 | 41 (possible AD), 50/51 (VD), 60/61 (DLB), 62/63 (PDD), 70/71/72 (FTD/PNA/SD), 99 (other) | 5 (PRD/QD/CIND/QD_naMCI) + dirty 3 |

> **중요**: GROUP은 imaging 시점 임상 그룹 라벨, y2_diag/y2_desc는 formal CRF 진단 코드. **두 필드는 1:1 대응 아님**. 상세는 [`diagnosis_demographics.md`](diagnosis_demographics.md#group-vs-y2_diag-mismatch).

---

## 방문 체계 (visit schedule)

| K_visit | imaging? | rows (Diag_Demo) | 의미 |
|---------|----------|------------------|------|
| 0 | ✓ | 627 | baseline (V0) |
| 1 | ✗ | 497 | clinical-only (V1) |
| 2 | ✓ | 426 | imaging follow-up #1 (V2) |
| 3 | ✗ | 377 | clinical-only (V3) |
| 4 | ✓ | 142 | imaging follow-up #2 (V4) |

- **V1/V3은 임상 전용** — APOE/VRF/imaging inventory 파일에 없음. NP/CDR/age는 매 방문 측정.
- **V0/V2/V4가 imaging visit** — 영상 가용성, APOE 채혈, VRF 평가, PiB positivity가 이 visit에만 존재.
- 방문당 평균 인터벌 ≈ 2년 (V0 → V2: 약 2년, V2 → V4: 약 2년 — 영상 촬영일 기반 추론).
- `1_KBASE1_nifti_0,2,4.xlsx` 파일명의 `0,2,4`는 imaging visit 번호.

**Visit 누적 분포** (per Diag_Demo):

| visit 횟수 | subjects |
|-----------|----------|
| 1 | 103 |
| 2 | 86 |
| 3 | 94 |
| 4 | 223 |
| 5 | 124 |

→ 대부분 4~5 visit 추적. 총 subject-visit 행 = 103×1 + 86×2 + 94×3 + 223×4 + 124×5 = **2,069** ✓

---

## 등록 및 추적 기간

| 마일스톤 | 첫 날짜 | 마지막 날짜 |
|---------|---------|-------------|
| Ref_dt (VRF 평가일, baseline 추정) | 2014-01-21 | 2020-02-03 |
| V0 PiB-PET 촬영일 | 2014-04-30 | 2020-09-01 |
| V2 PiB-PET 촬영일 | 2016-10-28 | 2021-04-20 |
| V4 PiB-PET 촬영일 | 2018-10-31 | 2021-04-13 |

→ 코호트 등록 기간 ~6년 (2014–2020), 마지막 데이터 시점 2021-04. 그 이후 데이터는 이 NFS export 시점 (2025-06)까지 미반영.

---

## 영상 모달리티 (9종)

| 모달리티 | scanner protocol string (`protocol` sheet) | 비고 |
|---------|--------------------------------------------|------|
| PIB | `HEAD C-11 PIB PET BRAIN AC image` | C-11 PiB amyloid PET |
| T1 | `HEAD TFL3D SAG 208 SLAB` | structural MRI |
| rfMRI | `HEAD rfMRI 116 phase bold moco` | resting-state fMRI |
| DTI | `TRUE AXL dti 67d TDI B1000 SCH` | diffusion tensor imaging |
| ASL | `Head ep2d tra pasl` | arterial spin labeling |
| FDG | `HEAD PET Brain (f-18 FDG) AC image` | F-18 FDG metabolic PET |
| FLAIR | `Head T2 spc fl sag` | T2 FLAIR |
| SWI | `SWI image` | susceptibility-weighted imaging |
| TAU | `T37 F18 Brain PET` | F-18 tau PET (후기 도입, V0/V2/V4 합 275 scan) |

가용성 인코딩 + V별 분포는 [`imaging_inventory.md`](imaging_inventory.md).

JSON sidecar (BIDS 메타) — `JSON_Files/<modality>/{ID}_{modality}_V{visit}.json` 패턴, 7,497 파일. 표준 dcm2niix 출력 (RepetitionTime, EchoTime, MagneticFieldStrength, Manufacturer 등 30+ key).

---

## 임상/인지 평가 항목

| 도메인 | 파일 | 컬럼 |
|--------|------|------|
| 인구학 | 2_Diag_Demo (simplified) | `a1_sx`, `a1_age`, `a1_edu` |
| 진단 | 2_Diag_Demo (simplified) | `y2_diag`, `y2_desc`, `y2_desc_details` |
| CDR | 2_Diag_Demo (simplified) | `c9_memory`, `c9_orientation`, `c9_judgment`, `c9_social`, `c9_family`, `c9_personal`, `c9_cdr`, `c9_sb_total` |
| 신경심리 | 4_NP | 72 cols (KBASE_NP1 + NP2, raw + Z) |
| APOE | 3_APOE | `Apo E genotyping`, `ApoE4_positivity` |
| 혈관위험 | 5_VascularRF | 50 cols (6 질환 × 5 sub-field + composite) |
| Amyloid PET 양성 | 추가_1 | `Positivity_1of4` |
| 영상 가용성 | 1_KBASE1_nifti_0,2,4 | 9 모달리티 컬럼 |
| **통합** | **masterfile** | **150 cols (위 전부)** |

전체 CRF는 `2_Diag_Demo.xlsx`의 Sheet1(302 cols × 2 rows codebook)에 기재 — simplified/master에 노출되지 않은 변수도 다수 (예: 가족력, 직업, 우울증 GDS-30 전체 항목, 운동 검사 등). 노출 안 된 컬럼이 필요하면 KBASE 운영팀에 raw CRF 요청.

---

## 처리 출력 (PROC/)

`/Volumes/nfs_storage/KBASE/PROC/` 하위 7 모달리티별 디렉토리:

```
PROC/
├── AMY_PET/      ← PIB amyloid PET 처리 출력 (SUVR, centiloid 등 추정)
├── DTI/
├── FLAIR/
├── SWI/
├── T1/           ← FreeSurfer/structural 출력 (추정)
├── T2_STAR/
└── TAU_PET/
```

**PET 처리 코드**: `Demo/PET_Processing_Code/`에 3개 Python orchestration script (`make_run.py`, `make_bash_run.py`, `make_final_script.py`)만 남아 있음.

> 처리 출력 디렉토리 내부 구조는 이 문서 작성 시점에 미조사. 분석 시작 전에 실제 디렉토리 inspection 권장.

---

## 비교: KBASE vs ADNI / OASIS3 / A4

| 항목 | KBASE | ADNI | OASIS3 | A4 / LEARN |
|------|-------|------|--------|-----------|
| 인종/지역 | 한국 | 미국 (백인 중심) | 미국 (WUSTL Knight ADRC) | 미국 (다기관 RCT) |
| Subject namespace | `SU####` + `BR####` | `RID` (정수) | `OASISID` (`OAS3xxxx`) | `BID` |
| Visit key | `K_visit` (0/1/2/3/4) | `VISCODE` (`bl`, `m06`, ...) | session label + `days_to_visit` | `VISCODE` (`SC`, `BL`, `V1`...`V6`) |
| CRF 표준 | 자체 한국어 CRF | NACC UDS v3 | NACC UDS v2/v3 | A4 RCT 프로토콜 |
| APOE 인코딩 | `E3/3` (slash) | `33` (정수) | `33` (정수) | `e3/e3` (소문자 slash) |
| 진단 코드 | `y2_diag` (5) + `y2_desc` (19) | `DX` (CN/MCI/AD) | `RACCDIAG`, `NACCETPR` | `Research_Group` (LEARN/A4) + `DX_DEC` |
| 통합 master | `masterfile.{xlsx,csv}` 1,292 × 150 | `ADNIMERGE.csv` 23,479 × 132 | (없음, 사용자가 build) | `MERGED.csv` ~89K × ~400 |
| 데이터 사전 | xlsx 안의 codebook (Sheet1) | LONI Data Dictionary (외부 PDF) | NACC UDS PDF (외부) | `docs/a4/baseline_csv.md` 포함 |

KBASE는 **한 파일에 통합 master가 이미 있다는 점**과 **CRF 표준이 한국어 자체 양식**이라는 점이 가장 큰 차별점. ADNI/OASIS3와 cross-cohort 분석 시 컬럼 이름·인코딩 매핑 테이블이 반드시 필요. 자세한 매핑 가이드는 [`master_columns.md`](master_columns.md), [`apoe.md`](apoe.md).
