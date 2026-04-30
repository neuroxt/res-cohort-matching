# OASIS3 파일 간 조인 관계

OASIS3 24개 CSV를 결합할 때 사용하는 키, 카디널리티(1:1 / 1:N), 분석 시 권장 조인 패턴.

> 현재 OASIS3 전용 파이프라인 코드는 미구현. 이 문서는 향후 분석/파이프라인 작성 시 참조용 설계 가이드이다.

---

## 1. 키 계층

OASIS3는 **3-tier 키 계층**으로 데이터가 연결된다:

```
Tier 1: Subject-level             Tier 2: Visit-level                Tier 3: File-level
─────────────────────             ──────────────────────             ───────────────────
OASISID                           (OASISID, days_to_visit)            OASIS_session_label
"OAS30001"                        ("OAS30001", 339)                   "OAS30001_UDSb4_d0339"
                                                                      "OAS30001_AV45_d2430"
```

| 키 | 사용 파일 | 카디널리티 |
|-----|-----------|-----------|
| **OASISID** | OASIS3_demographics | 1행 / subject |
| **(OASISID, days_to_visit)** | 모든 UDS 폼 (a1-d2), oasis3.csv | 일반적으로 1행 / (subject, visit) |
| **OASIS_session_label** | UDS 폼 + amyloid_centiloid + PET_json + PET_datasetdescription | form-specific (1 폼당 1행) |
| **(SUB_ID, VISIT, SEQ)** | oasis_file_list | 1:N (sequence별 multi-file 가능) |

> Session label은 **form-specific**. 따라서 같은 visit의 여러 폼을 묶을 때는 session label이 아닌 `(OASISID, days_to_visit)` 페어를 사용해야 한다.

---

## 2. 파일별 키 / 카디널리티 표

| 파일 | 인덱스 키 | 카디널리티 |
|------|-----------|-----------|
| OASIS3_demographics | OASISID | 1행/subject |
| OASIS3_UDSa1_participant_demo | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSa2_cs_demo | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSa3 (USDa3) | OASISID + days_to_visit | 1행/visit (optional, baseline 위주) |
| OASIS3_UDSa4D_med_codes | OASISID + days_to_visit | 1행/visit (a4G와 페어) |
| OASIS3_UDSa4G_med_names | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSa5_health_history | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSb1_physical_eval | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSb2_his_cvd | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSb3 (USDb3) | OASISID + days_to_visit | 1행/visit (optional, PD module) |
| OASIS3_UDSb4_cdr | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSb5_npiq | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSb6_gds | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSb7_faq_fas | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSb8_neuro_exam | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSb9_symptoms | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSc1_cognitive_assessments (psychometrics) | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSd1_diagnoses | OASISID + days_to_visit | 1행/visit |
| OASIS3_UDSd2_med_conditions | OASISID + days_to_visit | 1행/visit |
| OASIS3_amyloid_centiloid | subject_id + oasis_session_id | 1행/scan (~1.4 scan/subject) |
| OASIS3_PET_json | subject_id + session_id (+ filename) | 1행/scan (multi-run 시 multiple) |
| OASIS3_PET_datasetdescription | OASIS_ID + session_id | 1행/session |
| oasis3.csv | ID + refdate | 1행/(subject × visit) |
| oasis_file_list | SUB_ID + VISIT + SEQ + PATH | 1:N (file 단위) |

---

## 3. 권장 조인 패턴

### Pattern A — Cross-sectional baseline analysis

Subject당 1행으로 demographics + first-visit UDS + first amyloid PET을 결합.

```python
import pandas as pd

demo = pd.read_csv("OASIS3_demographics.csv")
b4 = pd.read_csv("OASIS3_UDSb4_cdr.csv")
d1 = pd.read_csv("OASIS3_UDSd1_diagnoses.csv")
centiloid = pd.read_csv("OASIS3_amyloid_centiloid.csv")

# (1) UDS 폼: 첫 visit (days_to_visit 최소값) 추출
b4_first = (b4.sort_values('days_to_visit')
              .drop_duplicates('OASISID', keep='first')
              [['OASISID', 'CDRTOT', 'CDRSUM', 'MMSE', 'dx1']])

d1_first = (d1.sort_values('days_to_visit')
              .drop_duplicates('OASISID', keep='first')
              [['OASISID', 'NORMCOG', 'DEMENTED', 'PROBAD', 'POSSAD',
                'MCIAMEM', 'MCIAPLUS', 'amndem']])

# (2) Centiloid: 첫 amyloid PET 추출
centiloid['day'] = centiloid['oasis_session_id'].str.extract(r'_d(\d+)$')[0].astype(int)
amy_first = (centiloid.sort_values('day')
                      .drop_duplicates('subject_id', keep='first')
                      [['subject_id', 'tracer', 'Centiloid_fSUVR_TOT_CORTMEAN']]
                      .rename(columns={'subject_id': 'OASISID',
                                       'Centiloid_fSUVR_TOT_CORTMEAN': 'centiloid_baseline'}))

# (3) Outer join 모두
baseline = (demo
            .merge(b4_first, on='OASISID', how='left')
            .merge(d1_first, on='OASISID', how='left')
            .merge(amy_first, on='OASISID', how='left'))
```

### Pattern B — Longitudinal UDS analysis

같은 visit의 여러 폼을 한 행에 합치기. `(OASISID, days_to_visit)` 키 사용.

```python
KEY = ['OASISID', 'days_to_visit']

forms = {
    'b4': pd.read_csv("OASIS3_UDSb4_cdr.csv")[KEY + ['CDRTOT', 'MMSE', 'dx1']],
    'b5': pd.read_csv("OASIS3_UDSb5_npiq.csv")[KEY + ['DEL', 'DEPD', 'AGIT', 'APA']],
    'b6': pd.read_csv("OASIS3_UDSb6_gds.csv")[KEY + ['GDS']],
    'b7': pd.read_csv("OASIS3_UDSb7_faq_fas.csv")[KEY + ['BILLS', 'TAXES', 'SHOPPING', 'MEALPREP']],
    'c1': pd.read_csv("OASIS3_UDSc1_cognitive_assessments.csv")[KEY + ['ANIMALS', 'TRAILA', 'tmb']],
    'd1': pd.read_csv("OASIS3_UDSd1_diagnoses.csv")[KEY + ['NORMCOG', 'DEMENTED', 'PROBAD']],
}

# 차례로 outer join (모든 visit 보존)
visit_long = forms['b4']
for name in ['b5', 'b6', 'b7', 'c1', 'd1']:
    visit_long = visit_long.merge(forms[name], on=KEY, how='outer')

# Subject별로 정렬 + 시간 순 인덱스
visit_long = visit_long.sort_values(KEY).reset_index(drop=True)
```

> **주의**: `OASIS3_UDSa3.csv`(USDa3, 4,090행)와 `OASIS3_UDSb3.csv`(USDb3, 4,090행)는 optional module이라 일부 visit에 없음. Outer join으로 합쳐야 missing이 NaN으로 표시됨.

### Pattern C — Imaging-clinical 매칭

`oasis3.csv`로 임상 visit에 가장 가까운 영상을 찾고, 시간 윈도우 필터링.

```python
oasis3 = pd.read_csv("oasis3.csv")  # ID, refdate, FDG, FDG_diff, AV45, AV45_diff, MR, MR_diff, PIB, PIB_diff
b4 = pd.read_csv("OASIS3_UDSb4_cdr.csv")

# 임상 visit ↔ 영상 (refdate ↔ days_to_visit)
matched = b4.merge(
    oasis3,
    left_on=['OASISID', 'days_to_visit'],
    right_on=['ID', 'refdate'],
    how='left'
)

# ±90일 안에 MR이 있는 임상 visit
mr_window = matched[matched['MR_diff'].abs() <= 90]
```

### Pattern D — PET → NIfTI 경로 추적

```python
centiloid = pd.read_csv("OASIS3_amyloid_centiloid.csv")
file_list = pd.read_csv("oasis_file_list.csv")

# session_id를 (sub, tracer, day)로 분리
centiloid[['sub', 'tracer', 'day']] = (
    centiloid['oasis_session_id']
    .str.extract(r'^(OAS3\d+)_(AV45|PIB)_d(\d+)$')
)
centiloid['day'] = centiloid['day'].astype(int)
file_list['day'] = file_list['VISIT'].str.lstrip('d').astype('Int64')

# PET NIfTI 매칭
pet_files = file_list[file_list['SEQ'].isin(['AV45', 'PIB'])]
merged = centiloid.merge(
    pet_files,
    left_on=['sub', 'tracer', 'day'],
    right_on=['SUB_ID', 'SEQ', 'day'],
    how='left'
)
# merged['PATH'] 가 NIfTI 경로 (Windows 매핑 → macOS 경로 변환 필요)
```

> **주의**: `oasis_file_list.csv`의 VISIT(폴더 day)와 centiloid의 session day가 정확히 일치하지 않을 수 있다 (폴더 grouping 규칙 다름). Mismatch 시 파일명에서 day 추출 fallback. 자세한 내용은 [`OASIS3_file_index.md`](OASIS3_file_index.md).

---

## 4. 조인 다이어그램

```
            ┌──────────────────────────────────────────┐
            │  Tier 1: Subject-level                   │
            │  OASISID                                 │
            └──────────────┬───────────────────────────┘
                           │
                           ▼
       ┌─────────────────────────────────────────────┐
       │  OASIS3_demographics  (1 row / subject)     │
       │  AgeatEntry, GENDER, EDUC, race, APOE, ...  │
       └──────────────┬──────────────────────────────┘
                      │ merge on OASISID
                      ▼
       ┌─────────────────────────────────────────────┐
       │  Tier 2: Visit-level                        │
       │  (OASISID, days_to_visit)                   │
       │                                             │
       │  ┌──────────────────────────────────────┐  │
       │  │  UDS A-forms (a1, a2, a3, a4D, a4G,  │  │
       │  │   a5)                                │  │
       │  │  outer join across forms             │  │
       │  └──────────────────────────────────────┘  │
       │                                             │
       │  ┌──────────────────────────────────────┐  │
       │  │  UDS B-forms (b1-b9)                 │  │
       │  └──────────────────────────────────────┘  │
       │                                             │
       │  ┌──────────────────────────────────────┐  │
       │  │  UDS C/D-forms (c1, d1, d2)          │  │
       │  └──────────────────────────────────────┘  │
       │                                             │
       │  ┌──────────────────────────────────────┐  │
       │  │  oasis3.csv (refdate ↔ scan diff)    │  │
       │  └──────────────────────────────────────┘  │
       └──────────────┬──────────────────────────────┘
                      │ merge on (subject, day) via session_label
                      ▼
       ┌─────────────────────────────────────────────┐
       │  Tier 3: File/scan-level                    │
       │  OASIS_session_label / file path            │
       │                                             │
       │  ┌──────────────────────────────────────┐  │
       │  │  PET CSVs (centiloid, PET_json,      │  │
       │  │   PET_datasetdescription)            │  │
       │  └──────────────────────────────────────┘  │
       │                                             │
       │  ┌──────────────────────────────────────┐  │
       │  │  oasis_file_list (NIfTI 인벤토리)    │  │
       │  └──────────────────────────────────────┘  │
       └─────────────────────────────────────────────┘
```

---

## 5. 행 수 차이로 본 카디널리티 패턴

| 행 수 그룹 | 폼 / 파일 | 의미 |
|------------|-----------|------|
| 8,627 | b1, b4, oasis3.csv | 모든 임상 visit (주력 longitudinal 폼) |
| 8,500 | a1, a2, a4D, a4G, a5, b2, b5, b6, b7, b8, b9, d1, d2 | 표준 longitudinal (visit 수가 일관됨) |
| 7,925 | c1 | Cognitive battery 일부 visit 누락 |
| 7,617 | a4D, a4G | 약물 정보 일부 visit 미수집 |
| 4,090 | a3 (USDa3), b3 (USDb3) | **Optional module** (a3=가족력 baseline 위주, b3=PD module) |
| 1,894 | amyloid_centiloid | Amyloid PET 스캔 |
| 2,158 | PET_json | 모든 PET 스캔 (FDG 포함) |
| 1,379 | demographics | Subject 수 |
| 42,907 | oasis_file_list | NIfTI file 수 (1 scan = multi-file 일반적) |

---

## 6. 주의사항

### Optional UDS modules

- **A3 (가족력)**: 일반적으로 baseline에서만 작성, 변경 시에만 갱신. 결과적으로 4,090행 (≈ 1.5 visits/subject 평균).
- **B3 (UPDRS)**: PD 의심 시에만 시행. 4,090행.
- 이 두 폼은 outer join 시 NaN 비율이 높음 → 분석 코드에서 명시적 처리 필요.

### a4D vs a4G 페어링

- 두 파일 행 수 동일 (7,617행) — `(OASISID, days_to_visit)` 페어로 정확히 1:1 매칭 가능.
- 같은 visit의 약물 코드(`drug1-46`)와 약물명(`meds_1-46`)이 같은 인덱스 위치에 들어감.
- 분석 시 long-format으로 풀어 두 파일을 join하는 게 권장.

```python
a4d = pd.read_csv("OASIS3_UDSa4D_med_codes.csv")
a4g = pd.read_csv("OASIS3_UDSa4G_med_names.csv")

KEY = ['OASISID', 'days_to_visit']
a4d_long = a4d.melt(id_vars=KEY + ['anymeds'], var_name='slot', value_name='code')
a4d_long['slot_num'] = a4d_long['slot'].str.extract(r'drug(\d+)').astype(int)

a4g_long = a4g.melt(id_vars=KEY + ['anymeds'], var_name='slot', value_name='name')
a4g_long['slot_num'] = a4g_long['slot'].str.extract(r'meds_(\d+)').astype(int)

meds = a4d_long.merge(a4g_long[['OASISID', 'days_to_visit', 'slot_num', 'name']],
                     on=['OASISID', 'days_to_visit', 'slot_num'])
```

### `*_diff` 부호 컨벤션 (oasis3.csv)

```
*_diff = refdate − scan_date
```

음수 = 영상이 임상 ref보다 *이후* 촬영. 자세한 내용은 [`OASIS3_file_index.md`](OASIS3_file_index.md).

### Centiloid는 amyloid 전용

- AV1451 (tau), FDG (metabolism)는 `OASIS3_amyloid_centiloid.csv`에 없음.
- AV1451 정량은 NIfTI를 별도 파이프라인 (FreeSurfer + 자체 SUVR) 으로 처리.

### `psychometrics` 토큰

- C1 cognitive battery의 session label은 `OAS30001_psychometrics_d0339` 형식.
- 다른 UDS 폼이 `UDSx{숫자}` 토큰을 쓰는 것과 다름. 정규식 매칭 시 주의.
- 자세한 내용은 [`OASIS3_session_label_reference.md`](OASIS3_session_label_reference.md).

### 데이터 입력 오류 5건

- b4 폼에 `days_to_visit < 0`인 행 5건 (예: `OAS30753_UDSb4_d-39520`, age=-47.25).
- 분석 전 필터링 권장: `df.query("days_to_visit >= 0 and `age at visit` >= 0")`.

### `days_to_visit` 데이터 타입 불일치

파일별로 컬럼 형식이 다르다:
- 대부분 폼: zero-padded 4자리 문자열 (`'0000'`)
- b4, c1: 정수 문자열 (`'0'`)

```python
# 모든 폼 join 전에 정수로 통일
KEY_DTYPE = {'days_to_visit': str}
df = pd.read_csv(file, dtype=KEY_DTYPE)
df['days_to_visit'] = pd.to_numeric(df['days_to_visit'], errors='coerce').astype('Int64')
```

자세한 내용은 [`OASIS3_session_label_reference.md`](OASIS3_session_label_reference.md).

---

## 참고 문서

| 문서 | 내용 |
|------|------|
| [`OASIS3_data_catalog.md`](OASIS3_data_catalog.md) | 24 CSV 마스터 인벤토리 |
| [`OASIS3_session_label_reference.md`](OASIS3_session_label_reference.md) | session label grammar (FORM 토큰 변종 포함) |
| [`OASIS3_uds_forms.md`](OASIS3_uds_forms.md) | 폼별 컬럼 그룹 + 핵심 컬럼 정의 |
| [`OASIS3_demographics.md`](OASIS3_demographics.md) | demographics 컬럼 사전 |
| [`OASIS3_pet_imaging.md`](OASIS3_pet_imaging.md) | PET 트레이서, Centiloid |
| [`OASIS3_file_index.md`](OASIS3_file_index.md) | NIfTI inventory, BIDS 명명 |
