# KBASE 조인 관계

## 핵심: `(ID, K_visit)` 단일 키

KBASE의 가장 큰 architectural 장점 — **모든 임상/메타 파일이 동일한 `(ID, K_visit)` composite key**를 공유. ADNI(`PTID + VISCODE_FIX` + 별도 imaging matching)나 OASIS3(`OASISID + days_to_visit` + session label) 대비 join이 trivial.

```
ID         K_visit   ⇒   모든 파일에서 동일 의미
SU0001     0          baseline 한 사람의 한 visit
SU0001     2          같은 사람 V2 imaging visit
BR0001     0          다른 namespace의 다른 사람
```

- `ID` ∈ {`SU####`, `BR####`} — 두 prefix는 별개 namespace (SU0001 ≠ BR0001).
- `K_visit` ∈ {0, 1, 2, 3, 4} — 정수, 모든 파일 일관.

---

## 파일별 키 가용 visit

| 파일 | K_visit 가용 | 비고 |
|------|--------------|------|
| `2_Diag_Demo.xlsx` (simplified) | **0/1/2/3/4** | 매 visit |
| `4_NP.xlsx` (NP) | **0/1/2/3/4** | 매 visit |
| `1_KBASE1_nifti_0,2,4.xlsx` (V0/V2/V4 시트) | **0/2/4** | imaging visit만 |
| `3_APOE.xlsx` (BLOOD) | **0/2/4** | 채혈 visit만. 정적 측정이라 V0 forward-fill 권장 |
| `5_VascularRF.xlsx` (Clinical2_B03_VRF) | **0/2/4** | imaging visit만 |
| `추가_1_AB_PiB_positivity.xlsx` (Sheet2) | **0/2/4** | PiB 촬영 visit만 |
| `masterfile.{xlsx,csv}` | **0/2/4** | imaging visit만 (V1/V3 행 없음) |

→ V1/V3 임상 데이터는 **master에 없음**. V1/V3까지 포함한 longitudinal 분석은 `2_Diag_Demo.xlsx` + `4_NP.xlsx`를 직접 join 해서 사용.

---

## Master concat layout

`masterfile.xlsx`/`masterfile.csv` (1,292 행 × 150 컬럼)는 4개 source의 단순 left-join 산물:

```
columns 1-16    ← 1_KBASE1_nifti_0,2,4.xlsx (V0/V2/V4 시트 union, 16 cols)
columns 17-30   ← 2_Diag_Demo.xlsx simplified (a1_*, c9_*, y2_*, 14 cols)
columns 31-32   ← 3_APOE.xlsx (Apo E genotyping, ApoE4_positivity)
columns 33-100  ← 4_NP.xlsx (72 cols 중 ID/K_visit 제외 70개. 단 master에선 raw subtests + Z 일부만 노출)
columns 101-150 ← 5_VascularRF.xlsx (Clinical2_B03_VRF 50 cols 중 ID/K_visit 제외)
```

`(ID, K_visit)` 키는 imaging inventory 기준 (V0/V2/V4 합 1,292 행). source 파일에 (ID, K_visit) 매칭이 없으면 NaN.

→ Master는 **imaging visit 한정 통합본**. NP/Diag_Demo의 V1/V3 행은 master에 없음. csv vs xlsx는 컬럼·행 100% 일치.

---

## Subject ID prefix 분포

| Prefix | Diag_Demo (rows / unique IDs) | Master (rows / unique IDs) |
|--------|-------------------------------|----------------------------|
| `SU` | 1,850 / ~514 | 1,157 / ~512 |
| `BR` | 219 / ~116 | 135 / ~132 |

- SU와 BR은 별개 모집 코호트로 추정 (KBASE 운영팀 문의로 확정 권장).
- Cross-cohort 분석 시 `df['cohort_subprefix'] = df['ID'].str[:2]`로 구분 가능.
- pooled 분석 시 prefix 그대로 사용해도 안전 (SU0001 vs BR0001은 다른 사람).

---

## Row count reconciliation

| 파일 | 가용 visit 합 | 실측 행수 | 차이 분석 |
|------|--------------|----------|-----------|
| Diag_Demo, NP | 627+497+426+377+142 = 2,069 | 2,069 | 일치 ✓ |
| imaging V0+V2+V4 | 644+408+240 = 1,292 | 1,292 | 일치 ✓ |
| APOE, VRF | 627+426+142 = 1,195 | 1,195 | 일치 ✓ |
| 추가_1 PiB positivity | 643+372+185 = 1,200 | 1,200 | 일치 ✓ |
| masterfile | (imaging와 동일해야) 1,292 | 1,292 | 일치 ✓ |

**imaging vs Diag_Demo unique ID 차이**:
- imaging V0/V2/V4 합 unique ID = 644 (V0 단독)
- Diag_Demo unique ID = 630
- → imaging에는 있지만 임상 CRF에 없는 subject 14명 존재 (또는 그 반대). pooling 전 set difference 확인 권장:
  ```python
  set_img = pd.concat([V0_df, V2_df, V4_df])['ID'].unique()
  set_clin = diag_demo_df['ID'].unique()
  print(set(set_img) - set(set_clin))  # imaging만 있는 ID
  print(set(set_clin) - set(set_img))  # clinical만 있는 ID
  ```

**APOE/VRF vs imaging unique ID 차이**:
- imaging unique ID = 644
- APOE/VRF unique ID = 627
- → imaging은 있는데 APOE/VRF가 없는 subject 17명. 채혈 declined 또는 다른 이유로 추정.

---

## 권장 join pattern

### 패턴 A: master 그대로 사용 (imaging visit 분석)

```python
import pandas as pd
master = pd.read_csv('/Volumes/nfs_storage/KBASE/ORIG/Demo/masterfile.csv')
# 1292 × 150, K_visit ∈ {0, 2, 4}
```

→ Cross-sectional 또는 V0/V2/V4 한정 longitudinal 분석에 적합. 단순.

### 패턴 B: V1/V3 포함 longitudinal

```python
diag = pd.read_excel('.../2_Diag_Demo.xlsx', sheet_name='진단명, CDR, age sx edu')
np_  = pd.read_excel('.../4_NP.xlsx', sheet_name='NP')
df = diag.merge(np_, on=['ID', 'K_visit'], how='outer')
# 2069 × ~85, K_visit ∈ {0, 1, 2, 3, 4}
```

→ MMSE/CDR longitudinal trajectory 분석에 사용. APOE는 ID 단위로 forward-fill:

```python
apoe = pd.read_excel('.../3_APOE.xlsx', sheet_name='BLOOD')
# subject-level APOE (V0 우선)
apoe_static = apoe.sort_values('K_visit').drop_duplicates('ID', keep='first')[
    ['ID', 'Apo E genotyping', 'ApoE4_positivity']
]
df = df.merge(apoe_static, on='ID', how='left')
```

### 패턴 C: cross-cohort merge (KBASE × ADNI/OASIS3)

`(ID, K_visit)` 키는 KBASE 내부에서만 의미. Cross-cohort 시:
- Subject 단위로 `cohort_id` 컬럼 추가 (`KBASE`/`ADNI`/`OASIS3`/`A4`).
- Visit 단위는 직접 매핑 안 됨 → 시간 기반 (`days_from_baseline`) 또는 visit number 표준화 필요.
- APOE 인코딩 통일 (KBASE `E3/3` → ADNI/OASIS3 `33` → A4 `e3/e3`).

상세 cross-cohort 가이드는 [`apoe.md`](apoe.md), [`master_columns.md`](master_columns.md).

---

## 알려진 join quirk

1. **APOE를 visit-level로 merge하면 V1/V3에 NaN 발생** — 정적 측정이므로 ID 단위 forward-fill 필수.
2. **GROUP은 visit별로 다를 수 있음** — imaging time 임상 분류라서 V0=NC였다가 V4=MCI로 바뀔 수 있음. y2_diag도 마찬가지. 분석 시 어느 visit 기준 진단을 쓸지 명시.
3. **Master는 imaging visit 한정** — V1/V3 임상 데이터를 그리려면 master 말고 source 파일 직접 join.
4. **`a1_age`는 매 visit 갱신됨** — 첫 visit 나이 = `df.sort_values('K_visit').drop_duplicates('ID', keep='first')['a1_age']`.
5. **imaging 가용성 컬럼은 cell value 자체가 키** — `V0[T1]` 셀 값이 `BR0001`이면 그 subject가 V0에서 T1 촬영함, 파일 검색 시 그 ID로 매칭. `O`나 `X`는 가용성 플래그 (legacy/no). [`imaging_inventory.md`](imaging_inventory.md) 참조.
