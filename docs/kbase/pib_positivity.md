# PiB Amyloid Positivity (추가 파일)

`/Volumes/nfs_storage/KBASE/ORIG/Demo/추가_1_AB_PiB_positivity.xlsx` (33 KB) / `.csv` (18 KB).

KBASE의 amyloid PET (PiB) **양성/음성 판정 결과**. 후기 추가 (`추가_1_*` prefix) — 핵심 5개 파일에 포함되지 않은 보충 데이터.

---

## 시트 구성

| 시트 | rows | cols | 내용 |
|------|------|------|------|
| `memo` | 6 | 1 | **방법론 노트** |
| `Sheet2` | 1,200 | 3 | **양성 판정 결과** |

→ K_visit 분포: 0:643 / 2:372 / 4:185 (V0/V2/V4 PiB 촬영 visit만).

→ 643 unique IDs. imaging V0 unique 644와 1명 차이.

---

## 방법론 (memo 시트)

```
1. PiB PET
2. Reference region: Inferior Cerebellar
3. Positive cut-off: SUVR > 1.40
4. (4번 항목 — memo 시트엔 row 4 비어 있음 또는 미기록)
5. (...)
```

요약:
- **트레이서**: C-11 PiB (Pittsburgh Compound B)
- **Reference region**: Inferior Cerebellar (소뇌 하부)
- **Positive cutoff**: SUVR > 1.40
- **Cortical region** (`Positivity_1of4`의 "1of4"가 의미): 4개 cortical 영역(예: precuneus, frontal, parietal, temporal) 중 1개 이상이 cutoff 초과 시 positive — 정확한 4 영역 정의는 memo에 미명시. KBASE 운영팀 또는 PET processing code 확인 필요.

> "1 of 4" rule은 표준 amyloid PET 양성 판정 컨벤션 중 하나. ADNI는 표준 cortical composite (frontal/temporal/parietal/cingulate) SUVR 1.11 cutoff (PiB) 또는 1.10 (FBP)을 사용 — KBASE의 1.40 cutoff는 reference region 차이 (Inferior Cerebellar) 때문에 더 높음.

---

## `Sheet2` — 결과 컬럼 (3개)

| 컬럼 | 타입 | 의미 / 분포 |
|------|------|-------------|
| `ID` | str | Subject ID |
| `K_visit` | int | 0/2/4 |
| `Positivity_1of4` | str | `neg` (822) / `POSITIVE` (378) |

→ 양성 비율: 378 / 1,200 = **31.5%** (visit-level). subject-level 비율은 baseline (V0) 기준 별도 산출 필요.

---

## ⚠ Casing quirk

`Positivity_1of4` 값이 **대소문자 혼재**:

- 음성: `neg` (소문자)
- 양성: `POSITIVE` (대문자)

→ DB export 단계에서 두 문자열이 다른 source(예: 한 batch는 소문자, 다른 batch는 대문자)에서 왔거나 수동 입력 시 통일 안 됨. **합치기 전 case 통일 필수**.

```python
import pandas as pd
df = pd.read_excel('/Volumes/nfs_storage/KBASE/ORIG/Demo/추가_1_AB_PiB_positivity.xlsx', sheet_name='Sheet2')
# 표준화
df['amyloid_pos'] = df['Positivity_1of4'].str.lower().map({'neg': 0, 'positive': 1})
# 또는 binary str
df['amyloid_pos_str'] = df['Positivity_1of4'].str.lower()  # 'neg' / 'positive'
```

---

## csv ↔ xlsx 동등성

- `추가_1_AB_PiB_positivity.csv` (18 KB)
- `추가_1_AB_PiB_positivity.xlsx` (33 KB)

→ 동일 데이터, csv 권장 (한국어 파일명이지만 utf-8로 정상 read).

---

## 다른 cohort와 비교

| cohort | tracer | reference region | cutoff | column |
|--------|--------|------------------|--------|--------|
| KBASE | PiB | **Inferior Cerebellar** | **SUVR > 1.40** (1 of 4 cortical regions) | `Positivity_1of4` (`neg`/`POSITIVE`) |
| ADNI | PiB / AV45 / FBB | whole cerebellum | PiB SUVR > 1.5 (region-dependent), AV45 > 1.11, centiloid > 24 | `AMYLOID_STATUS` (positive/negative) |
| OASIS3 | PiB / AV45 | cerebellum (PUP/freesurfer) | Centiloid 기반 | `Centiloid_fSUVR_TOT_CORTMEAN` |
| A4 | FBP (florbetapir) | whole cerebellum | SUVR > 1.10 또는 Centiloid > 15 | `AMY_STATUS_bl`, `AMY_CENTILOID_bl`, `AMY_SUVR_bl` |

→ KBASE의 1.40 cutoff은 Inferior Cerebellar reference region 때문에 다른 코호트보다 높음. 직접 SUVR 비교 시 reference region 차이 반드시 명시.

> KBASE의 raw SUVR 값은 이 파일에 없음 — 양성/음성 판정만. raw SUVR이 필요하면 `/Volumes/nfs_storage/KBASE/PROC/AMY_PET/` 처리 출력 또는 PET processing code 확인 필요.

---

## 분석 진입점 권장

```python
import pandas as pd

amy = pd.read_csv('/Volumes/nfs_storage/KBASE/ORIG/Demo/추가_1_AB_PiB_positivity.csv')

# Casing 통일
amy['amyloid_pos'] = amy['Positivity_1of4'].str.lower().map({'neg': 0, 'positive': 1})

# baseline (V0) 기준 amyloid status (subject-level)
amy_baseline = amy[amy['K_visit'] == 0][['ID', 'amyloid_pos']].rename(columns={'amyloid_pos': 'amyloid_pos_bl'})

# master에 merge
master = pd.read_csv('/Volumes/nfs_storage/KBASE/ORIG/Demo/masterfile.csv')
master = master.merge(amy_baseline, on='ID', how='left')

# 진단 × amyloid status 분포
master.groupby(['GROUP', 'amyloid_pos_bl']).size()
```

---

## 알려진 limitations

1. **Casing 혼재** (`neg` vs `POSITIVE`) — 합치기 전 case 통일 필수.
2. **방법론 memo 미완성** — memo 시트 row 4~6은 비어 있거나 일부만 기재. "1 of 4" cortical region의 정확한 정의 확인 필요 (PET processing code 또는 KBASE 운영팀).
3. **raw SUVR 부재** — 양성/음성 판정만 있고 정량 값은 없음. dose-response 또는 cutoff 변경 시 sensitivity analysis 시 PROC/AMY_PET 출력 필요.
4. **643 vs 644 unique ID** — imaging inventory V0 unique 644와 1명 차이. 누락된 1명 누군지 확인 필요 (`set(imaging_v0_ids) - set(amy_v0_ids)`).
5. **별도 amyloid PET (FBP, FBB) 없음** — KBASE는 PiB 만 사용. ADNI/A4와 cross-cohort 비교 시 트레이서 차이 보정 (centiloid 변환) 필요.
6. **TAU 양성 판정 별도 파일 부재** — Tau PET은 `1_KBASE1_nifti_0,2,4.xlsx`에 가용성만 있음. Tau positivity / SUVR 정량 데이터는 NFS의 다른 위치 또는 PROC/TAU_PET/ 확인 필요.
