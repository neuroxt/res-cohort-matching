# KBASE 데이터 카탈로그

`/Volumes/nfs_storage/KBASE/ORIG/Demo/` 안의 모든 임상/메타 파일을 **파일 → 시트 → 컬럼** 3 계층으로 정리. xlsx multi-sheet 특성상 단일 file-level 인벤토리만으로는 부족해서 시트별 분해 필수.

> 모든 경로는 macOS NFS 마운트 기준. 본인 환경 mount root 치환 (Windows `Z:\KBASE\`, Linux `/mnt/nfs/KBASE/`).

---

## 디렉토리 layout

```
/Volumes/nfs_storage/KBASE/
├── ORIG/
│   ├── Demo/                                ← 임상 + 메타 + JSON sidecar (이 문서 범위)
│   │   ├── 1_KBASE1_nifti_0,2,4.xlsx       ← 영상 가용성 (V0/V2/V4)
│   │   ├── 2_Diag_Demo.xlsx                ← 진단 + demographics + 302-col codebook
│   │   ├── 3_APOE.xlsx                     ← APOE genotype
│   │   ├── 4_NP.xlsx                       ← 신경심리검사 72 cols
│   │   ├── 5_VascularRF.xlsx               ← 혈관위험인자 50 cols
│   │   ├── masterfile.xlsx                 ← 통합 (xlsx)
│   │   ├── masterfile.csv                  ← 통합 (csv, xlsx와 100% 동일)
│   │   ├── 추가_1_AB_PiB_positivity.xlsx    ← 추가 amyloid positivity
│   │   ├── 추가_1_AB_PiB_positivity.csv     ← 동일 (csv 미러)
│   │   ├── 2_Diag_Demo_sheet3_dx_coding.png ← Sheet1 codebook의 y2_diag 부분 캡처
│   │   ├── JSON_Files/                      ← BIDS sidecar JSON (modality/visit별)
│   │   │   ├── DTI/      (1,193 json)
│   │   │   ├── FDG/      (1,220 json)
│   │   │   ├── PIB/      (1,197 json)
│   │   │   ├── rfMRI/    (1,195 json)
│   │   │   ├── T1/       (1,198 json)
│   │   │   ├── T2_FLAIR/ (1,219 json)
│   │   │   └── TAU/      (  275 json)        ← 후기 도입
│   │   └── PET_Processing_Code/             ← Python orchestration only
│   │       ├── make_run.py                 (orchestration)
│   │       ├── make_bash_run.py
│   │       └── make_final_script.py
│   │
│   └── NII/                                 ← 원본 NIfTI (별도 문서)
│
└── PROC/                                    ← 처리 출력 (별도 문서)
    ├── AMY_PET/    DTI/    FLAIR/    SWI/
    └── T1/         T2_STAR/ TAU_PET/
```

> **주의**: NFS 상에는 PDF/README/data dictionary 별도 파일이 **없다**. 모든 컬럼 의미는 (1) `2_Diag_Demo.xlsx`의 Sheet1 codebook과 (2) 변수명 자체(`a1_age`, `c9_cdr` 등)에서 유추하거나 (3) KBASE 운영팀에 직접 확인.
>
> **무시할 파일**: `._*` (macOS resource fork), `~$*` (Excel lock). 자동 파싱 시 필터링 필수.

---

## xlsx 파일별 시트 인벤토리

### `1_KBASE1_nifti_0,2,4.xlsx` (130 KB)

영상 가용성 inventory. 파일명의 `0,2,4`는 visit 번호 (V0/V2/V4 = imaging visit). V1/V3은 임상 전용이라 이 파일에 없음.

| 시트 | 행수 | 컬럼수 | 핵심 |
|------|------|--------|------|
| `V0` | 644 (data) | 16 | baseline imaging. GROUP 분포: NC_고령 306 / MCI 164 / AD 100 / NC_청장년 74 |
| `V2` | 408 (data) | 16 | 2년 추적. typo: `_고령` 1, `고령` 1, `''` 1 행 |
| `V4` | 240 (data) | 16 | 4년 추적. 소수 진단 등장: PRD 2, QD 1, CIND 1, QD_naMCI 1 |
| `protocol` | 13 | 11 | 모달리티 short-code ↔ scanner protocol string (예: `"HEAD C-11 PIB PET BRAIN AC image"` → `pib`) |
| `NOTE` | 9 | 0 | 빈 시트 (작성용 placeholder 추정) |

**16 컬럼** (V0/V2/V4 동일):
`GROUP | ID | K_visit | PiB-PET | FDG-PET | TAU-PET | PIB | T1 | rfMRI | DTI | ASL | FDG | FLAIR | SWI | TAU | 비고`

- `PiB-PET`/`FDG-PET`/`TAU-PET` 3 컬럼은 **촬영일** (datetime). `TAU-PET`엔 `N` (촬영 안 됨) 또는 빈 값 가능.
- 그 다음 9 컬럼 (`PIB`~`TAU`)은 **모달리티 가용성**:
  - `BR####` 또는 `SU####` (subject ID 그대로 들어감) → 가용 + 파일 키
  - `O` → 가용 (older notation, 주로 V0의 PIB)
  - `X` → 미촬영
  - 빈 값 → 프로토콜 미해당
- `비고` → 자유 텍스트 메모 (예: `fs error`)

상세는 [`imaging_inventory.md`](imaging_inventory.md).

---

### `2_Diag_Demo.xlsx` (179 KB)

진단 + demographics + 통합 codebook. **Sheet1이 데이터가 아니라 codebook**이라는 점이 핵심 quirk.

| 시트 | 행수 | 컬럼수 | 내용 |
|------|------|--------|------|
| `진단명, CDR, age sx edu` | 2,069 | 16 | **simplified 임상 데이터**. 실제 분석 진입점 |
| `Sheet1` | 2 | 302 | **codebook**. row1 한국어 라벨, row2 영어 변수명. 데이터 아님 |
| `Sheet2` | 1 | 1 | **빈 시트** (`max_row=1, max_col=1`, 데이터 없음) |

**simplified 16 컬럼**:
`ID | K_visit | a1_sx | a1_age | a1_edu | c9_memory | c9_orientation | c9_judgment | c9_social | c9_family | c9_personal | c9_cdr | c9_sb_total | y2_diag | y2_desc | y2_desc_details`

| 컬럼 | 타입 | 값 분포 / 비고 |
|------|------|---------------|
| `ID` | str | `SU####` 1850 + `BR####` 219, 630 unique subjects |
| `K_visit` | int | 0:627 / 1:497 / 2:426 / 3:377 / 4:142 |
| `a1_sx` | int | 0:1209 / 1:860 — **인코딩 codebook 미명시** (추정 0=M, 1=F) |
| `a1_age` | int | 21~93, 평균 70.8 |
| `a1_edu` | int | 0~25년, 평균 11.2 |
| `c9_memory`~`c9_personal` | float | CDR 6 박스 점수 (0/0.5/1/2/3) |
| `c9_cdr` | float | global CDR. 분포 0:1173 / 0.5:581 / 1:254 / 2:54 / 3:7 |
| `c9_sb_total` | float | sum of boxes (0~21) |
| `y2_diag` | int | 5 코드 (1/2/3/4/9). 매핑 → [`codebook_dx.md`](codebook_dx.md) |
| `y2_desc` | float | 19 코드 (10/20/30/31/32/33/34/40/41/50/51/60/61/62/63/70/71/72/99). 매핑 → [`codebook_dx.md`](codebook_dx.md) |
| `y2_desc_details` | str | 자유 텍스트 (대부분 빈 값) |

**Sheet1 codebook** — 302 열의 **한국어 라벨 ↔ 영어 변수명 매핑**. CRF 전체 변수의 사전. simplified 시트와 master에는 그중 일부만 노출됨. 상세는 [`diagnosis_demographics.md`](diagnosis_demographics.md#sheet1-codebook).

---

### `3_APOE.xlsx` (41 KB)

| 시트 | 행수 | 컬럼수 | 내용 |
|------|------|--------|------|
| `BLOOD` | 1,195 | 5 | APOE genotype (visit-level row, 정적 측정) |

**5 컬럼**: `ID | K_visit | 항목 | Apo E genotyping | ApoE4_positivity`

| 컬럼 | 분포 |
|------|------|
| `K_visit` | 0:627 / 2:426 / 4:142 (V1/V3은 측정 없음) |
| `항목` | 대부분 빈 값 |
| `Apo E genotyping` | NaN:569 / `E3/3`:377 / `E3/4`:158 / `E2/3`:52 / `E4/4`:28 / `E2/4`:9 / `E2/2`:2 |
| `ApoE4_positivity` | NaN:569 / 0:431 / 1:195 |

**인코딩 quirk**: `E3/3` 슬래시 문자열. ADNI(`33`/`34` 정수) ↔ A4(`e3/e4` 소문자) ↔ KBASE(`E3/3` 대문자+슬래시) 모두 다름. 상세는 [`apoe.md`](apoe.md).

---

### `4_NP.xlsx` (920 KB)

신경심리검사 종합. **가장 큰 임상 파일**.

| 시트 | 행수 | 컬럼수 | 내용 |
|------|------|--------|------|
| `NP` | 2,069 | 72 | 검사 raw 점수 + Z-score |
| `NP memo` | 61 | 54 | 검사명 ↔ 한국어 설명 hierarchical codebook |

**72 컬럼 그룹** (KBASE_NP1 + NP2 통합):

| 그룹 | 컬럼 | 검사명 |
|------|------|--------|
| 식별자 | `ID`, `K_visit` | |
| J1 (4) | `J1_15s`, `J1_30s`, `J1_45s`, `J1_60s`, `J1_Tot` | 언어 유창성 (동물범주, 1분) |
| J2 (4) | `J2_high`, `J2_mid`, `J2_low`, `J2_Tot` | Boston Naming (고/중/저빈도) |
| J3 (1) | `J3` | MMSE-KC 총점 |
| J4 (4) | `J4_1st`, `J4_2nd`, `J4_3rd`, `J4_Tot` | 단어목록기억 (immediate, 3시행) |
| J5 (1) | `J5` | 구성행동 (immediate) |
| J6 (2) | `J6`, `J6_storage` | 단어목록회상 (delayed) + 저장률 |
| J7, J8 (2) | `J7`, `J8` | 단어목록재인, 구성회상 |
| K1 (3) | `K1_W`, `K1_C`, `K1_CW` | Stroop (Word / Color / Color-Word) |
| K3 (2) | `K3_1`, `K3_2` | Clox 1/2 |
| TMT (2) | `TMT_A (L11)`, `TMT_B (L11)` | Trail Making A/B 소요시간 |
| Digit Span (2) | `DS_forward (L12)`, `DS_backward (L12)` | |
| TS (2) | `TS1`, `TS2` | Total score (NP1 / NP2) |
| RCFT (4) | `L1_rcft_copy`, `L3_rcft_3min`, `L8_rcft_30min`, `L9_rcft_recog` | Rey Complex Figure |
| L2 COWAT (4) | `L2_1`, `L2_2`, `L2_3`, `L2_Tot` | 음소 유창성 (ㄱ/ㅇ/ㅅ/총합) |
| L4 / L10 (8) | `L4_A`, `L4_B`, `L4_Tot`, `L10_A`, `L10_B`, `L10_Tot`, `L10_recog` | WMS-IV-K Logical Memory (immediate / delayed / recog) |
| L5 (1) | `L5` | WAIS-IV-K 토막짜기 |
| L7 FAB (5) | `L7_1`, `L7_3`, `L7_4`, `L7_5`, `L7_6` | Frontal Assessment Battery |
| L13, KART (2) | `L13`, `KART` | Anosognosia, KART |
| Z-scores (17) | `J1_Z`, `J2_Z`, `J3_Z`, `J4_Z`, `J5_Z`, `J6_Z`, `J7_Z`, `J8_Z`, `K1_W_Z`, `K1_C_Z`, `K1_CW_Z`, `TMT_A_z`, `TMT_B_z`, `DS_f_z`, `DS_b_z`, `TS1_Z`, `TS2_Z` | 표준화 점수 |

상세는 [`neuropsych_battery.md`](neuropsych_battery.md).

---

### `5_VascularRF.xlsx` (236 KB)

| 시트 | 행수 | 컬럼수 | 내용 |
|------|------|--------|------|
| `Clinical2_B03_VRF` | 1,195 | 50 | 6 질환 × 5 sub-field + composite VRF score |
| `memo` | 3 | 4 | partial codebook |

**구조**: `ID | K_visit | Ref_dt` + 6 질환(`b03_hypertension`, `b03_diabetes`, `b03_coronary`, `b03_hyperlipidemia`, `b03_cere` (cerebrovascular), `b03_tia`) × 5 sub-fields(`*_age`, `*_age_no`, `*_take`, `*_take_age`, `*_take_age_no`, `*_take_rate`) + `b03_coronary_oper*`(2) + `b03_diabetes_take_kind` + `b03_vascular`(composite 0~4).

**셀 값 quirk**: `*_age_no` 컬럼에 `'[""]'` 또는 `'["0"]'` 같은 **stringified Python list** 들어있음. 원본 DB의 multiselect 필드 export 산물. 정수 변환 시 `ast.literal_eval` 필요. 상세는 [`vascular_risk_factors.md`](vascular_risk_factors.md).

---

### `masterfile.xlsx` / `masterfile.csv` (881 KB / 715 KB)

**통합 master**. 1 시트, 1,292 행 × 150 컬럼. csv ↔ xlsx **100% 컬럼 일치**.

150 컬럼 = imaging inventory (1-16) + Diag_Demo simplified (17-30) + APOE (31-32) + NP raw + Z (33-100) + VRF (101-150). 단순 `(ID, K_visit)` 키 concat. 상세 컬럼 사전은 [`master_columns.md`](master_columns.md).

| K_visit | rows |
|---------|------|
| 0 | 644 |
| 2 | 407 |
| 4 | 226 |

→ V1/V3 (clinical-only) 행은 master에 없음. **master는 imaging visit 한정**이라는 점 주의.

---

### `추가_1_AB_PiB_positivity.xlsx` / `.csv` (33 KB / 18 KB)

| 시트 | 행수 | 컬럼수 | 내용 |
|------|------|--------|------|
| `memo` | 6 | 1 | 방법론: PiB PET, Inferior Cerebellar reference, SUVR > 1.40 cutoff |
| `Sheet2` | 1,200 | 3 | `ID | K_visit | Positivity_1of4` |

`Positivity_1of4` 분포: `neg` 822 / `POSITIVE` 378. **대소문자 불일치 quirk** (소문자 vs 대문자 혼재). 합치기 전 case 통일 필수. 상세는 [`pib_positivity.md`](pib_positivity.md).

---

## 행수 sanity table

| 파일 (시트) | rows | unique IDs | K_visit 분포 |
|-------------|------|------------|----------------|
| 2_Diag_Demo (simplified) | 2,069 | 630 | 0:627 / 1:497 / 2:426 / 3:377 / 4:142 |
| 4_NP (NP) | 2,069 | 630 | 0:627 / 1:497 / 2:426 / 3:377 / 4:142 |
| 1_KBASE1_nifti V0+V2+V4 | 644+408+240=1,292 | — | 0:644 / 2:408 / 4:240 |
| 3_APOE (BLOOD) | 1,195 | 627 | 0:627 / 2:426 / 4:142 |
| 5_VRF (Clinical2_B03_VRF) | 1,195 | 627 | 0:627 / 2:426 / 4:142 |
| 추가_1 (Sheet2) | 1,200 | 643 | 0:643 / 2:372 / 4:185 |
| masterfile | 1,292 | 644 | 0:644 / 2:407 / 4:226 |

**관찰**:
- Diag_Demo와 NP 행수 동일 (2,069) — 두 파일은 모든 visit (V0~V4) 포함.
- APOE/VRF는 1,195 — V0/V2/V4만 (1,195 vs 645+426+142=1,195 ✓).
- imaging V0/V2/V4 합 1,292 — masterfile 1,292와 일치.
- imaging은 644 unique ID이지만 APOE/VRF는 627 (17명 imaging만 있고 APOE 채혈 안 함).
- 추가_1 PiB positivity 643 ID — imaging과 거의 일치 (1명 차이).

행수 mismatch 분석은 [`join_relationships.md`](join_relationships.md#row-count-reconciliation) 참조.
