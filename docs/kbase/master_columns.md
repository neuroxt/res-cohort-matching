# `masterfile.{xlsx,csv}` 150-컬럼 사전

`/Volumes/nfs_storage/KBASE/ORIG/Demo/masterfile.xlsx` (881 KB) 또는 `masterfile.csv` (715 KB) — **컬럼·행 100% 동일**, csv 사용 권장 (openpyxl 의존성 회피).

1,292 행 × 150 컬럼. K_visit ∈ {0, 2, 4} (imaging visit 한정). 4개 source 파일을 `(ID, K_visit)` 키로 단순 left-join.

---

## Source-별 컬럼 그룹

| 컬럼 범위 | 출처 | 컬럼 수 | 상세 |
|-----------|------|---------|------|
| 1-16 | `1_KBASE1_nifti_0,2,4.xlsx` (V0+V2+V4 union) | 16 | imaging inventory |
| 17-30 | `2_Diag_Demo.xlsx` simplified (a1_*, c9_*, y2_*) | 14 (`ID`+`K_visit` 제외) | 진단 + demographics + CDR |
| 31-32 | `3_APOE.xlsx` BLOOD | 2 | APOE |
| 33-100 | `4_NP.xlsx` NP | 68 (`ID`+`K_visit`+ `K3_1`/`K3_2` 제외 등 일부 master에서 빠짐) | 신경심리 raw + Z |
| 101-150 | `5_VascularRF.xlsx` Clinical2_B03_VRF | 50 (`ID`+`K_visit` 제외 후 50, `Ref_dt` 포함) | 혈관위험인자 |

> source의 join은 `(ID, K_visit)` left from imaging inventory. 따라서 master는 imaging visit 한정 (V0/V2/V4), V1/V3 임상-only 데이터는 master에 없음.

---

## 컬럼 list (전체 150개, 순서 유지)

```
# 1-16: imaging inventory
ID | K_visit | GROUP |
PiB_PET | FDG_PET | TAU_PET |
PIB | T1 | rfMRI | DTI | ASL | FDG | FLAIR | SWI | TAU | 비고

# 17-30: Diag_Demo simplified (a1_*, c9_*, y2_*)
a1_sx | a1_age | a1_edu |
c9_memory | c9_orientation | c9_judgment | c9_social | c9_family | c9_personal | c9_cdr | c9_sb_total |
y2_diag | y2_desc | y2_desc_details

# 31-32: APOE
Apo E genotyping | ApoE4_positivity

# 33-100: NP (raw + Z)
J1_15s | J1_30s | J1_45s | J1_60s | J1_Tot |
J2_high | J2_mid | J2_low | J2_Tot |
J3 |
J4_1st | J4_2nd | J4_3rd | J4_Tot |
J5 | J6 | J6_storage | J7 | J8 |
K1_W | K1_C | K1_CW | K3_1 | K3_2 |
TMT_A (L11) | TMT_B (L11) | DS_forward (L12) | DS_backward (L12) |
TS1 | TS2 |
L1_rcft_copy | L3_rcft_3min | L8_rcft_30min | L9_rcft_recog |
L2_1 | L2_2 | L2_3 | L2_Tot |
L4_A | L4_B | L4_Tot |
L10_A | L10_B | L10_Tot | L10_recog |
L5 |
L7_1 | L7_3 | L7_4 | L7_5 | L7_6 |
L13 | KART |
J1_Z | J2_Z | J3_Z | J4_Z | J5_Z | J6_Z | J7_Z | J8_Z |
K1_W_Z | K1_C_Z | K1_CW_Z |
TMT_A_z | TMT_B_z |
DS_f_z | DS_b_z |
TS1_Z | TS2_Z

# 101-150: VRF
Ref_dt |
b03_hypertension | b03_hypertension_age | b03_hypertension_age_no |
b03_hypertension_take | b03_hypertension_take_age | b03_hypertension_take_age_no | b03_hypertension_take_rate |
b03_diabetes | b03_diabetes_age | b03_diabetes_age_no |
b03_diabetes_take | b03_diabetes_take_age | b03_diabetes_take_age_no | b03_diabetes_take_kind | b03_diabetes_take_rate |
b03_coronary | b03_coronary_age | b03_coronary_age_no |
b03_coronary_take | b03_coronary_take_age | b03_coronary_take_age_no | b03_coronary_take_rate |
b03_coronary_oper | b03_coronary_oper_age | b03_coronary_oper_age_no |
b03_hyperlipidemia | b03_hyperlipidemia_age | b03_hyperlipidemia_age_no |
b03_hyperlipidemia_take | b03_hyperlipidemia_take_age | b03_hyperlipidemia_take_age_no | b03_hyperlipidemia_take_rate |
b03_cere | b03_cere_age | b03_cere_age_no |
b03_cere_take | b03_cere_take_age | b03_cere_take_age_no | b03_cere_take_rate |
b03_tia | b03_tia_age | b03_tia_age_no |
b03_tia_take | b03_tia_take_age | b03_tia_take_age_no | b03_tia_take_rate |
b03_vascular
```

> imaging inventory 시트의 컬럼명은 `PiB-PET`/`FDG-PET`/`TAU-PET` (대시 포함)이지만 master에서는 `PiB_PET`/`FDG_PET`/`TAU_PET` (언더스코어)로 변환됨. naming 불일치 주의.

---

## 컬럼 설명 (간략)

| 컬럼 | 출처 문서 |
|------|-----------|
| `GROUP`, imaging 가용성 컬럼 | [`imaging_inventory.md`](imaging_inventory.md) |
| `a1_sx`, `a1_age`, `a1_edu`, `c9_*`, `y2_diag`, `y2_desc` | [`diagnosis_demographics.md`](diagnosis_demographics.md), [`codebook_dx.md`](codebook_dx.md) |
| `Apo E genotyping`, `ApoE4_positivity` | [`apoe.md`](apoe.md) |
| `J*_*`, `K*_*`, `L*_*`, `TMT_*`, `DS_*`, `TS*`, `KART`, `*_Z` | [`neuropsych_battery.md`](neuropsych_battery.md) |
| `Ref_dt`, `b03_*` | [`vascular_risk_factors.md`](vascular_risk_factors.md) |

---

## 행수 / unique IDs

| K_visit | rows | unique IDs |
|---------|------|-----------|
| 0 | 644 | 644 |
| 2 | 407 | (V2 imaging X 1건 제외) |
| 4 | 226 | |

총 1,292 rows, 644 unique subjects (imaging baseline 기준).

---

## csv vs xlsx 동등성

```python
import pandas as pd
csv_df = pd.read_csv('/Volumes/nfs_storage/KBASE/ORIG/Demo/masterfile.csv')
xlsx_df = pd.read_excel('/Volumes/nfs_storage/KBASE/ORIG/Demo/masterfile.xlsx')

assert len(csv_df) == len(xlsx_df) == 1292
assert list(csv_df.columns) == list(xlsx_df.columns)  # 150 columns identical order
```

→ pipeline은 csv 사용. xlsx만 있을 때 cell formatting (date formatting 등) 미세 차이 가능 — csv가 ground truth.

---

## 분석 진입점 권장

```python
import pandas as pd

df = pd.read_csv('/Volumes/nfs_storage/KBASE/ORIG/Demo/masterfile.csv')

# typo clean-up
df['GROUP'] = df['GROUP'].replace({'_고령': 'NC_고령', '고령': 'NC_고령'})

# APOE forward-fill (V0 우선)
apoe_cols = ['Apo E genotyping', 'ApoE4_positivity']
df[apoe_cols] = df.sort_values('K_visit').groupby('ID')[apoe_cols].ffill()

# 진단 라벨
df['dx_label'] = df['y2_diag'].map({1: 'NC_young', 2: 'NC_elderly', 3: 'MCI', 4: 'AD_probable', 9: 'Other'})

# baseline 한 visit per subject
baseline = df[df['K_visit'] == 0]
```

---

## 알려진 limitations

1. **`Apo E genotyping` 결측 32건** (master) — APOE 채혈 안 한 subject. ID-단위 forward-fill해도 채혈 자체 안 한 경우엔 NaN.
2. **VRF stringified list** 컬럼 (`b03_*_age_no`) — `'[""]'`/`'["0"]'` 형태. 정수 변환 시 [`vascular_risk_factors.md`](vascular_risk_factors.md) 파싱 가이드 참조.
3. **NP `K3_1`/`K3_2`** 누락 가능성 — 4_NP.xlsx 원본에는 있지만 master 일부 행에서 NaN 비율 매우 높을 수 있음 (NP1 vs NP2 도입 차이). 분석 전 isnull 비율 spot-check 권장.
4. **`y2_desc_details`는 자유 텍스트** — 대부분 빈 값, 일부 한국어 자유 메모. 통계 분석 시 제외.
5. **timestamp 컬럼 (`PiB_PET`, `FDG_PET`, `TAU_PET`, `Ref_dt`)** — xlsx에서는 datetime, csv에서는 string (`'2015-09-10'`). 사용 시 `pd.to_datetime(... errors='coerce')` 권장.
