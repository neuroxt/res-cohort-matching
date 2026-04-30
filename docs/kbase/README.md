# KBASE (Korean Brain Aging Study) — 데이터 문서 인덱스

KBASE는 SNUBH/SNU 기반의 한국인 뇌 노화/치매 종단 코호트. 임상 + 인지 검사 + APOE + 혈관위험인자 + 멀티모달 MRI/PET을 통합한다. NACC UDS 기반 ADNI/OASIS3와 달리 **자체 한국어 CRF 기반**이며, 통합 export가 `masterfile.{xlsx,csv}` 한 파일로 이미 제공된다.

> **NFS 기준 경로** (macOS 마운트 기준):
> - 임상/메타/이미지: `/Volumes/nfs_storage/KBASE/ORIG/Demo/`
> - 원본 NIfTI: `/Volumes/nfs_storage/KBASE/ORIG/NII/`
> - 처리 출력: `/Volumes/nfs_storage/KBASE/PROC/{AMY_PET,DTI,FLAIR,SWI,T1,T2_STAR,TAU_PET}/`
>
> Windows/Linux는 마운트 root만 본인 환경에 맞게 치환 (예: `Z:\KBASE\...`, `/mnt/nfs/KBASE/...`).

---

## 한 눈에 보기

| 항목 | 값 |
|------|---|
| Subject 키 | `ID` (`SU####` 1850 + `BR####` 219, 총 630 unique) |
| Visit 키 | `K_visit` ∈ {0, 1, 2, 3, 4} (V1/V3은 임상 전용, V0/V2/V4가 imaging visit) |
| 진단 그룹 | NC_청장년 (young NC), NC_고령 (elderly NC), MCI, AD + 소수 PRD/QD/CIND/QD_naMCI |
| Subject-visit 행수 | 2,069 (clinical), 1,195 (APOE/VRF), 1,200 (PiB positivity), 1,292 (master) |
| 등록·추적 기간 | 2014-01 ~ 2021-04 (Ref_dt / 영상 촬영일 기준) |
| 임상 CRF 필드 (Sheet1 codebook) | 302 컬럼 (한국어 라벨 + 영어 변수명 매핑) |
| 핵심 CRF 추출 (simplified sheet) | 16 컬럼 (`a1_*`, `c9_*`, `y2_*`) |
| APOE | `E2/2`, `E2/3`, `E2/4`, `E3/3`, `E3/4`, `E4/4` 슬래시 문자열 (OASIS3 정수 / A4 소문자와 다름) |
| 신경심리검사 (4_NP) | 72 컬럼 (raw + Z-score, KBASE_NP1 + NP2) |
| 혈관위험인자 | 50 컬럼 (6 질환 × 5 sub-field) |
| 모달리티 | PIB / FDG / TAU / T1 / rfMRI / DTI / ASL / FLAIR / SWI |
| 통합 master | `masterfile.{xlsx,csv}` 1,292 행 × 150 컬럼 (4 source 단순 concat) |

---

## 문서 목록

### 시작점

| 문서 | 언제 읽나요? |
|------|-------------|
| [`data_catalog.md`](data_catalog.md) | NFS 원본 파일 + xlsx 시트 + 컬럼 수 3-tier 인벤토리 — KBASE 처음 접할 때 |
| [`protocol.md`](protocol.md) | 코호트 설계 배경, 방문 체계 (V0~V4), 9 모달리티, 등록/추적 기간 |
| [`join_relationships.md`](join_relationships.md) | `(ID, K_visit)` 단일 join 키, master concat 위치, 다른 코호트와 비교 |
| [`master_columns.md`](master_columns.md) | `masterfile.{xlsx,csv}` 150 컬럼 사전 (source 파일별 그룹화) — 통합 분석 시작점 |

### 데이터 종류별

| 문서 | 내용 |
|------|------|
| [`imaging_inventory.md`](imaging_inventory.md) | `1_KBASE1_nifti_0,2,4.xlsx`의 V0/V2/V4 시트 + 모달리티 가용성 인코딩 (`BR####`/`O`/`X`) + protocol sheet |
| [`diagnosis_demographics.md`](diagnosis_demographics.md) | `2_Diag_Demo.xlsx` 3 시트 (simplified 16 cols + Sheet1 302-col codebook + empty Sheet2) + GROUP↔y2_diag 불일치 quirk |
| [`codebook_dx.md`](codebook_dx.md) | `y2_diag` 5코드 + `y2_desc` 19코드 진단명 매핑 (PNG codebook 기준) |
| [`apoe.md`](apoe.md) | `3_APOE.xlsx` 인코딩 + ADNI/OASIS3/A4 cross-cohort APOE 인코딩 비교표 |
| [`neuropsych_battery.md`](neuropsych_battery.md) | `4_NP.xlsx` 72-col 신경심리검사 (KBASE_NP1 + NP2) raw + Z-score + 한국 표준 검사명 매핑 |
| [`vascular_risk_factors.md`](vascular_risk_factors.md) | `5_VascularRF.xlsx` 50 cols + JSON-string 셀 quirk (`'[""]'`, `'["0"]'`) |
| [`pib_positivity.md`](pib_positivity.md) | `추가_1_AB_PiB_positivity.xlsx` SUVR 1.40 cutoff (Inferior Cerebellar reference) + `neg`/`POSITIVE` 대소문자 quirk |

---

## 알려진 limitations & quirks (요약)

문서 작성 시점에 NFS 데이터를 직접 inspect하여 확인된 항목:

1. **GROUP과 y2_diag는 1:1 대응 아님.** GROUP은 imaging-time 임상 그룹 라벨, y2_diag는 formal CRF 진단 코드. 예: GROUP=MCI인데 y2_diag=4(probable AD) 38건 존재. → 분석 시 어느 필드를 ground truth로 쓸지 명시 필요. 상세는 [`diagnosis_demographics.md`](diagnosis_demographics.md#group-vs-y2_diag-mismatch).
2. **GROUP 값 typo**: V2/master에 `_고령`, `고령` (각 1건) — `NC_고령` 의도. clean-up 필요.
3. **APOE missing 569건** — `BLOOD` 시트는 (ID, K_visit) 키지만 V1/V3에는 측정 안 됨. APOE는 정적 변수이므로 V0 값을 forward-fill 권장.
4. **PiB positivity 대소문자**: `neg` (소문자) vs `POSITIVE` (대문자). 합치기 전 `.str.upper()` 또는 `.str.lower()` 필수.
5. **VRF JSON-string cells**: `b03_*_age_no` 등에서 `'[""]'`, `'["0"]'` 형태 — multiselect 필드의 raw export. 정수 변환 시 `ast.literal_eval` 또는 정규식 파싱.
6. **Sheet2 of `2_Diag_Demo.xlsx`는 실제로 비어있음** (`max_row=1, max_col=1`). 동일 디렉토리의 `2_Diag_Demo_sheet3_dx_coding.png`는 Sheet1(codebook) 안에서 `y2_diag`/`y2_desc` 행을 캡처한 이미지로 추정 — 별도 시트 아님.
7. **codebook은 데이터 안에 임베드.** `2_Diag_Demo.xlsx`의 Sheet1(302 cols × 2 rows)이 *데이터가 아닌 한국어 라벨 ↔ 영어 변수명 매핑표*. 별도 codebook PDF는 없음.
8. **csv ↔ xlsx 동일성**: `masterfile.csv`/`masterfile.xlsx`, `추가_1_AB_PiB_positivity.csv`/`.xlsx` 둘 다 컬럼 100% 일치. 파이프라인은 csv 사용 권장 (openpyxl 의존성 회피).
9. **a1_sx 인코딩 미명시**: 0과 1의 의미(M/F)는 codebook에 기재 없음. 분포(0:1209, 1:860)와 한국 임상 컨벤션상 추정 0=Male, 1=Female. 검증 필요시 별도 source 또는 KBASE 운영팀 확인.

---

## 작성 컨벤션

- 한국어 본문 + 영어 기술 용어 (변수명, 검사명, 코드값은 영어 그대로) — 다른 코호트(`docs/oasis3/`, `docs/a4/`) 컨벤션과 동일.
- 모든 사실은 NFS 원본 inspection 결과 기반. 새 사실 추가 시 inspection 명령과 결과 함께 commit.
- 컬럼명은 백틱(`a1_age`)으로 감싸 고정 폭. 한국어 라벨이 있을 땐 슬래시로 병기 (`a1_age` / `연령`).
- "Known limitations" 섹션은 모든 문서에 포함. quirk를 발견하면 즉시 추가.
