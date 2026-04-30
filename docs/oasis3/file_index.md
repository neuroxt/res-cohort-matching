# OASIS3 영상 파일 / 세션 인덱스 참조

OASIS3 영상 데이터의 인벤토리는 두 CSV로 관리된다:

| 파일 | 설명 |
|------|------|
| `oasis_file_list.csv` | **NIfTI 파일 단위** 인덱스 — 42,907 개별 파일 |
| `oasis3.csv` | **(subject, refdate) × modality** collapsed 인덱스 — 8,627행 |

이 문서는 두 파일의 컬럼 의미, PATH 컨벤션, 영상-임상 visit 매칭 규칙을 정리한다.

---

## 1. `oasis_file_list.csv` — NIfTI 파일 인벤토리

42,907행 × 5컬럼. NFS 위에 존재하는 모든 NIfTI 파일(및 일부 sidecar)을 1행에 1파일로 나열.

### 컬럼

| 컬럼 | 설명 | 값 |
|------|------|-----|
| COHORT | 코호트 식별자 | 항상 `OASIS3` |
| SUB_ID | 피험자 ID | `OAS3xxxx` 패턴 (e.g., `OAS31039`) |
| VISIT | 임상 visit 그룹 (폴더 분류 기준) | `d####` 또는 `unmatched` |
| SEQ | 모달리티 토큰 | T1w, T2w, FLAIR, asl, pasl, bold, dwi, swi, T2star, GRE, angio, fieldmap, minIP, PIB, AV45, AV1451, FDG |
| PATH | 파일 절대경로 | Windows mapping `Z:\1_combined\OASIS3\ORIG\NII\...` |

### VISIT 컬럼 분포 (실측)

| VISIT | 행 수 | 비고 |
|-------|-------|------|
| `d0000` | 14,238 | 첫 visit 영상이 압도적 (33%) |
| `unmatched` | 5,223 | **임상 visit 그룹에 매칭 실패** (12%) |
| 그 외 `d####` | 23,446 | follow-up 시점 (55%) |

> `unmatched` = 임상 visit 윈도우 안에 매칭되지 않는 영상 스캔. 임상 데이터 없이 영상만 존재하는 시점.

### SEQ 모달리티 분포 (실측)

```
dwi:      12,915   (가장 많음 — 평균 multi-shell × multi-volume)
bold:      5,114
T1w:       4,116
T2w:       4,051
fieldmap:  3,819
T2star:    2,350
FLAIR:     1,381
asl:       1,337
GRE:       1,326
PIB:       1,248   (PET amyloid)
minIP:     1,231
swi:       1,229
angio:       896
AV45:        780   (PET amyloid)
AV1451:      763   (PET tau)
pasl:        223
FDG:         127   (PET metabolism)
─────────────────
TOTAL:    42,907
```

### PATH 컨벤션

```
Z:\1_combined\OASIS3\ORIG\NII\oasis_{batch}\{SUB_ID}\{VISIT}\{SEQ}\sub_{SUB_ID}_ses_{actual_day}_{...}_{ext}
```

#### macOS NFS 마운트 변환

```
Z:\1_combined\OASIS3\ORIG\NII\...    →    /Volumes/nfs_storage/OASIS3/ORIG/NII/...
```

> NFS 마운트는 `1_combined` prefix 없이 `OASIS3/ORIG/NII/...`로 시작. **사용자가 처음 언급한 `1_combined/OASIS3/ORIG/DEMO`는 Windows 매핑**이다.

#### batch 식별자

실측: 모든 파일이 `oasis_1117` 단일 batch에 속함. (다른 batch 식별자가 없음 — 향후 추가될 가능성 있음.)

#### 폴더 day vs 파일명 day 차이

실제 PATH 예시 (subject `OAS31039`, VISIT 그룹 `d1182`):

```
Z:\...\OAS31039\d1182\T1w\sub_OAS31039_ses_d1184_T1w.nii.gz
Z:\...\OAS31039\d1182\AV1451\sub_OAS31039_ses_d1182_acq_AV1451_run_01_pet.nii.gz
Z:\...\OAS31039\d1182\asl\sub_OAS31039_ses_d1184_asl.nii.gz
Z:\...\OAS31039\d1182\dwi\sub_OAS31039_ses_d1184_run_01_dwi.nii.gz
Z:\...\OAS31039\d1182\FLAIR\sub_OAS31039_ses_d1184_FLAIR.nii.gz
```

**폴더의 VISIT(`d1182`)와 파일명의 day(`d1184`)는 다를 수 있다.**

- **VISIT 폴더 day** = 이 visit 그룹의 *대표 일자* (가장 가까운 임상 ref 또는 imaging session 시작일)
- **파일명 `ses_d####`** = 해당 NIfTI의 *실제 스캔 일자*
- 같은 imaging session 안에서도 여러 일에 걸쳐 촬영된 경우(예: AV1451 PET이 d1182에 촬영, MRI는 d1184에 촬영) — 그래도 같은 VISIT 그룹으로 묶임 (해당 예: 2일 차이)

> 분석 시 정확한 스캔 일자가 필요하면 **파일명에서 추출** (`ses_d(\d+)` 정규식). VISIT 컬럼은 visit grouping에 사용.

#### BIDS 명명 컨벤션

BIDS 1.0+ 표준을 따름:
- `sub-{SUB_ID}_ses-{day}_{modality}.nii.gz` — 기본
- `sub-{SUB_ID}_ses-{day}_acq-{label}_{modality}.nii.gz` — acquisition variant 명시 (예: `acq-TSE_T2w`, `acq-TOF_angio`, `acq-AV1451_pet`)
- `sub-{SUB_ID}_ses-{day}_run-{N}_{modality}.nii.gz` — 같은 modality 다회 촬영
- `sub-{SUB_ID}_ses-{day}_echo-{N}_{modality}.nii.gz` — multi-echo (fieldmap)
- `sub-{SUB_ID}_ses-{day}_task-{name}_run-{N}_bold.nii.gz` — fMRI task labeling
- DWI sidecar: `.bvec`, `.bval`, `.json` (BIDS 표준)

> 단, OASIS3 파일들은 **BIDS 표준의 `sub-`/`ses-` prefix 대신 `sub_`/`ses_` underscore**를 사용한다 (BIDS 비표준). 파싱 시 주의.

---

## 2. `oasis3.csv` — Subject × visit × modality (collapsed)

8,627행 × 10컬럼. 각 행은 한 subject의 한 임상 visit 시점에서 어떤 modality 영상이 가까이 촬영되었는지 보여주는 wide-format inventory.

### 컬럼

| 컬럼 | 설명 |
|------|------|
| ID | OASISID (e.g., `OAS30001`) |
| refdate | 임상 ref date (`days_to_visit` 정수) |
| FDG | 가까운 FDG PET 스캔의 days_to_visit (없으면 빈 값) |
| FDG_diff | `refdate − FDG` (음수 = scan이 ref 이후) |
| AV45 | 가까운 AV45 PET 스캔의 days_to_visit |
| AV45_diff | `refdate − AV45` |
| MR | 가까운 MR 스캔의 days_to_visit |
| MR_diff | `refdate − MR` |
| PIB | 가까운 PIB PET 스캔의 days_to_visit |
| PIB_diff | `refdate − PIB` |

> `MR`은 모든 MRI sequence를 아우르는 통합 컬럼. T1w/FLAIR/DWI 등 개별 modality 구분은 `oasis_file_list.csv`로 다시 매핑 필요.
>
> AV1451(tau PET) 컬럼은 **이 파일에 없다**. AV1451 스캔 매칭은 `oasis_file_list.csv`로 별도 처리.

### `*_diff` 부호 컨벤션 (실측 확인)

```
diff = refdate − scan_date
```

| diff 값 | 해석 |
|---------|------|
| 0 | 같은 날 |
| 양수 (+N) | 영상이 임상 ref 시점보다 **N일 이전** |
| 음수 (−N) | 영상이 임상 ref 시점보다 **N일 이후** |

실측 예 (`OAS30001`):

| refdate | MR | MR_diff | 산식 검증 |
|---------|-----|---------|-----------|
| 0 | 129 | −129 | 0 − 129 = −129 ✓ |
| 722 | 757 | −35 | 722 − 757 = −35 ✓ |
| 2181 | 2430 | −249 | 2181 − 2430 = −249 ✓ |
| 3025 | 3132 | −107 | 3025 − 3132 = −107 ✓ |

### Modality 매칭 분포 (실측)

각 행에서 채워진 modality 컬럼 수 분포:

| 채워진 modality 수 | 행 수 | 비고 |
|--------------------|-------|------|
| 0 | 5,696 | 임상 visit만 있고 영상 없음 (대다수) |
| 1 | 1,142 | 단일 modality 매칭 |
| 2 | 1,573 | 두 modality 매칭 |
| 3 | 200 | 세 modality 매칭 |
| 4 | 15 | 네 modality (FDG + AV45 + MR + PIB) 모두 매칭 — 매우 희귀 |

> 대부분의 임상 visit은 **영상 없음** (66%). 이는 OASIS3가 임상 follow-up이 더 빈번하고 영상은 longitudinal 간격이 길기 때문.

---

## 3. 영상 ↔ 임상 join 패턴

### 패턴 A: 임상 visit 기준 가장 가까운 영상 찾기

`oasis3.csv`를 사용해 (subject, refdate) 기준으로 영상 매칭. ±90일 윈도우가 일반적:

```python
import pandas as pd

oasis3 = pd.read_csv("oasis3.csv")

# refdate 기준 ±90일 안에 MR이 있는 visit
oasis3['mr_within_90d'] = oasis3['MR_diff'].abs() <= 90
mr_matched = oasis3[oasis3['MR'].notna() & oasis3['mr_within_90d']]
```

### 패턴 B: 영상 기준 가장 가까운 임상 visit 찾기

`oasis_file_list.csv`의 VISIT 그룹을 사용. VISIT가 이미 가장 가까운 임상 visit으로 매칭되어 있다 (`unmatched`는 매칭 실패):

```python
file_list = pd.read_csv("oasis_file_list.csv")
b4 = pd.read_csv("OASIS3_UDSb4_cdr.csv")

# T1w 파일 + 해당 visit의 CDR 정보
t1_files = file_list[(file_list['SEQ'] == 'T1w') & (file_list['VISIT'] != 'unmatched')]
t1_files['days_to_visit'] = t1_files['VISIT'].str.lstrip('d').astype(int)

merged = t1_files.merge(
    b4[['OASISID', 'days_to_visit', 'CDRTOT', 'MMSE']],
    left_on=['SUB_ID', 'days_to_visit'],
    right_on=['OASISID', 'days_to_visit'],
    how='left'
)
```

### 패턴 C: PET centiloid → NIfTI 경로 매칭

```python
centiloid = pd.read_csv("OASIS3_amyloid_centiloid.csv")
# session_id 예: OAS30001_AV45_d2430

# session_id를 (sub, tracer, day)로 분리
centiloid[['sub', 'tracer', 'day']] = (
    centiloid['oasis_session_id']
    .str.extract(r'^(OAS3\d+)_(AV45|PIB|FDG)_d(\d+)$')
)
centiloid['day'] = centiloid['day'].astype(int)

# oasis_file_list에서 해당 PET NIfTI 찾기
file_list['day'] = file_list['VISIT'].str.lstrip('d').astype('Int64')
pet_files = file_list[file_list['SEQ'].isin(['AV45', 'PIB', 'FDG'])]

merged = centiloid.merge(
    pet_files,
    left_on=['sub', 'tracer', 'day'],
    right_on=['SUB_ID', 'SEQ', 'day'],
    how='left'
)
# merged['PATH'] 가 NIfTI 경로
```

> 단, 폴더 day(VISIT)와 파일명 day(`ses_d####`)이 다를 수 있으므로 정확한 매칭이 안 될 수 있다. 그 경우 파일명에서 day를 추출하여 fallback 매칭 권장.

---

## 4. 알려진 한계

1. **`unmatched` 5,223 파일 (12%)**: 임상 visit 그룹에 매칭되지 않음. 대부분 imaging-only sub-study 또는 임상 visit 윈도우 밖 촬영.
2. **VISIT 폴더 day와 파일명 day 차이**: 폴더는 visit grouping, 파일명은 실제 스캔 일자. 정밀 분석 시 파일명을 사용.
3. **batch 식별자 단일**: 현재 모두 `oasis_1117`. 향후 batch 추가 가능성.
4. **AV1451은 `oasis3.csv`에 컬럼 없음**: tau PET는 `oasis_file_list.csv`로만 매칭.
5. **DWI는 multi-shell × multi-volume으로 파일 수가 많음**: `dwi` SEQ가 12,915 행 (전체 30%). 분석 시 file-level 대신 session-level (per-subject-per-day) aggregation 권장.

---

## 참고 문서

| 문서 | 내용 |
|------|------|
| [`data_catalog.md`](data_catalog.md) | 24 CSV 마스터 인벤토리 |
| [`session_label_reference.md`](session_label_reference.md) | session label grammar, days_to_visit 의미 |
| [`pet_imaging.md`](pet_imaging.md) | PET 트레이서, Centiloid, PUP 파이프라인 |
| [`join_relationships.md`](join_relationships.md) | 전체 조인 패턴 |
