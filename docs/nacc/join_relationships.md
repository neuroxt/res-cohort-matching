# NACC 파일 간 조인 관계 / 카디널리티

NACC v71 freeze 의 파일들이 어떤 키로 연결되며 어떤 카디널리티를 갖는지 정리. 분석 파이프라인 설계 / cross-domain join 시 reference.

---

## 1. Subject / Visit 키 계층

NACC 데이터는 3 단계 키 계층으로 구성:

```
SUBJECT-LEVEL
├── NACCID (unique subject ID)
└── NACCADC (소속 ADRC)

VISIT-LEVEL (most files)
├── NACCID
├── NACCVNUM (1-based sequence)
├── PACKET (I/F/T)
├── FORMVER (1/2/3/4)
└── VISITMO/DAY/YR (절대 일자)

EVENT-LEVEL (NACC SCAN)
├── NACCID
├── SCANDATE (PET/MRI 촬영일)
└── TRACER (PET 만)
```

UDS 임상 데이터는 visit-level. SCAN imaging 데이터는 event-level (NACCVNUM 직접 사용 안 함, SCANDATE↔VISITDATE 시간 매칭).

---

## 2. 핵심 join 키 표

| 파일 페어 | 조인 키 | 카디널리티 | 목적 |
|----------|---------|----------|------|
| `investigator_ftldlbd_nacc71.csv` ↔ `investigator_fcsf_nacc71.csv` | `(NACCID, ?)` — fcsf 가 LP date 기반 | 1 visit 행 ↔ 0–N CSF 행 | UDS visit 에 가까운 CSF 측정값 attach |
| `investigator_ftldlbd_nacc71.csv` ↔ `investigator_mri_nacc71.csv` | `(NACCID, NACCMRDY)` — MRI scan day | 1 visit ↔ 0–N MRI | 전통적 MRI metric attach |
| `investigator_ftldlbd_nacc71.csv` ↔ `investigator_scan_mri_*.csv` | `(NACCID, STUDYDATE ↔ VISITDATE)` | 1 visit ↔ 0–N SCAN MRI | NACC SCAN MRI quantification |
| `investigator_ftldlbd_nacc71.csv` ↔ `investigator_scan_pet_*.csv` | `(NACCID, SCANDATE ↔ VISITDATE)` | 1 visit ↔ 0–N PET | NACC SCAN PET (Amyloid/Tau/FDG) |
| `merged.csv` (NeuroXT) | `(NACCID, NACCVNUM)` | unique | UDS + CSF + Amyloid PET + Tau PET 통합. 이미 inner-join 되어 있음. |

---

## 3. NeuroXT `merged.csv` 의 inner-join 로직 (재구성)

`merged.csv` 가 어떻게 만들어졌는지 source 파일별 매핑:

### Step 1: UDS 임상 (38 cols)
```sql
SELECT
  NACCID, NACCADC, PACKET, FORMVER, VISITMO, VISITDAY, VISITYR, NACCVNUM,
  BIRTHMO, BIRTHYR, SEX, RACE, EDUC, MARISTAT,
  MEMORY, ORIENT, JUDGMENT, COMMUN, HOMEHOBB, PERSCARE,
  CDRSUM, CDRGLOB, COMPORT, CDRLANG,
  NACCMMSE, MOCATOTS, NACCMOCA, NACCTMCI, NACCALZD,
  NACCAGEB, NACCAGE, NACCUDSD,
  NACCACSF, NACCPCSF, NACCTCSF, NACCNMRI, NACCNAPA, NACCNE4S
FROM investigator_ftldlbd_nacc71.csv
-- 행 수: 205,909 (visit-level)
```

### Step 2: VISITDATE / DX derived (2 cols)
- `VISITDATE` = `YYYY-MM-DD` 합성 (`VISITYR`/`VISITMO`/`VISITDAY` 통합)
- `DX` = NeuroXT 통합 진단 라벨 (D1 + B4 dx1 priority 로직)

### Step 3: CSF biomarker (5 cols, LEFT JOIN)
```sql
LEFT JOIN investigator_fcsf_nacc71.csv
  ON NACCID
  WHERE LP_date is NEAREST to VISITDATE
  ANSWER:
    CSFABETA, CSFPTAU, CSFTTAU,
    CSFDATE_MATCH (LP_date),
    CSFDATEDIFF (LP_date − VISITDATE)
```

### Step 4: Amyloid PET (175 cols, LEFT JOIN)
```sql
LEFT JOIN (
  investigator_scan_amyloidpetnpdka_nacc71.csv  -- 172 cols
  + investigator_scan_amyloidpetgaain_nacc71.csv  -- 15 cols (CENTILOIDS, GAAIN_*, AMYLOID_STATUS)
)
  ON NACCID
  WHERE SCANDATE is NEAREST to VISITDATE
  COLUMNS PREFIXED 'AMY/...'
  ADD: AMYDATEDIFF
```

### Step 5: Tau PET (169 cols, LEFT JOIN)
```sql
LEFT JOIN investigator_scan_taupetnpdka_nacc71.csv  -- 171 cols
  ON NACCID
  WHERE SCANDATE is NEAREST to VISITDATE
  COLUMNS PREFIXED 'TAU/...'
  ADD: TAUDATEDIFF
```

### 결과
- 행 수: 205,909 × 1 (UDS visit 수 보존)
- 컬럼 수: 8 (bookkeeping) + 6 (demo) + 10 (CDR) + 14 (cognitive/dx derived) + 1 (VISITDATE) + 1 (DX) + 5 (CSF) + 175 (AMY) + 169 (TAU) = **390 cols**
- Visit 단위 결측 패턴: PET / CSF / MoCA 측정 안 한 visit은 해당 컬럼 NaN.

---

## 4. 시간 매칭 윈도우

NACC 분석에서 흔히 쓰이는 visit ↔ event 매칭 윈도우:

| Event | 권장 윈도우 (visit 기준 ±N일) | 의미 |
|-------|---------------------------|------|
| MRI (volumetry / SBM) | ±90일 | 보통 같은 visit cycle 내 |
| PET (Amyloid / Tau / FDG) | ±90일 (보통) ~ ±180일 (느슨) | 영상 ↔ 임상 cohort 분석 표준 |
| CSF | ±90일 (~±180일) | LP 가 visit 일과 가까운 경우 |

`merged.csv` 의 `*_DATEDIFF` 컬럼으로 window 필터링:

```python
df = pd.read_csv("merged.csv")
df_strict = df[df['AMYDATEDIFF'].abs() <= 90]   # ±90일
```

---

## 5. 영상 ↔ 임상 5.9% 미스매치

NII_NEW/ 영상이 있는 6,481명 중 **381명 (5.9%) 이 임상 데이터 부재** (Issue #7):

| 유형 | 인원 | merged.csv 행 | 처리 권고 |
|------|------|--------------|---------|
| 영상 + 임상 | 6,100 | ✅ 있음 | 정상 분석 |
| 영상 only | 381 | ❌ 없음 | imaging-only cohort 별도 분석 / NACC freeze 갱신 대기 |
| 임상 only | ~48,904 | ✅ 있음 (이미지 컬럼 NaN) | image-required 분석 시 자동 제외 |

```python
# NACC SCAN PET 가 있는 NACCID
amy = pd.read_csv("investigator_scan_amyloidpetnpdka_nacc71.csv", usecols=['NACCID'])
imaged_ids = set(amy['NACCID'].unique())

# UDS clinical 가 있는 NACCID
clinical_ids = set(merged['NACCID'].unique())

both = imaged_ids & clinical_ids
imaging_only = imaged_ids - clinical_ids
clinical_only = clinical_ids - imaged_ids
```

> 5.9% 미스매치는 NII_NEW (전체 영상 — DICOM/NIfTI) 기준. NACC SCAN 정량화 (PET/MRI quantification) 기준 매칭률은 더 높음 (NACC SCAN 은 정식 SCAN 서약 subject 만).

---

## 6. ADRC level 분석 (`NACCADC` 사용)

```python
# ADRC 별 subject 수
adrc_size = merged.groupby('NACCADC')['NACCID'].nunique()

# Site effect 통제 (regression)
import statsmodels.formula.api as smf
model = smf.ols('CDRSUM ~ NACCAGE + SEX + C(NACCADC)', data=merged).fit()
```

> `NACCADC` 외부 매핑 (어느 ADRC인지) 은 NACC DUA에서 별도 요청 필요. 분석에서는 ADRC-anonymized integer 만 사용.

---

## 7. ADSP-PHC 와의 join

ADSP-PHC December 2024 release 는 NACCID 를 직접 키로 사용:

```python
phc = pd.read_csv("ADSP-PHC-.../Imaging_PET/NACC_ADSP_PHC_Amyloid_Simple_2024.csv")
phc_amy = merged.merge(phc, on='NACCID', how='left')

# Return-to-Cohort manifest 로 cross-cohort linkage 확인
manifest = pd.read_excel("NACC_ADSP-PHC_Dec2024_Return-to-Cohort.xlsx")
```

ADSP-PHC harmonized phenotype (예: `PHC_MEM`, `PHC_EXEC`, `PHC_LANG`) 는 다른 ADSP-PHC 코호트 (ADNI, AIBL, HABS-HD, DOD-ADNI 등) 와 **동일 변수명·정의** 사용. cross-cohort 메타분석 시 핵심.

---

## 8. 카디널리티 요약

| 좌측 | 우측 | 카디널리티 |
|------|------|----------|
| `investigator_ftldlbd_nacc71.csv` (visit-level) | `merged.csv` (visit-level) | 1:1 (행 수 같음 205,909) |
| `merged.csv` 1 visit | CSF 측정 | 1:0–1 (visit 마다 CSF 0 또는 1회) |
| `merged.csv` 1 visit | Amyloid PET | 1:0–1 |
| `merged.csv` 1 visit | Tau PET | 1:0–1 |
| 1 NACCID | NACCVNUM | 1:N (subject 마다 1–11 visit) |
| 1 NACCID | SCAN PET (Amyloid) | 1:0–N (longitudinal scan) |
| 1 NACCADC | NACCID | 1:N (ADRC 마다 수십~수천 subject) |

---

## 9. 분석 시 join 순서 권장

1. **UDS clinical 먼저** (`investigator_ftldlbd_nacc71.csv` 또는 `merged.csv`)
2. **CSF / PET 가 필요하면 ±90일 윈도우 inner-join**
3. **ADSP-PHC 가 필요하면 NACCID 로 left-join**
4. **ADRC effect 통제 시 `NACCADC` 를 categorical 로 모델 포함**

---

## Known limitations & quirks

1. **`merged.csv` 는 이미 inner-join 완료 — 추가 join 불필요.** UDS + CSF + Amyloid + Tau 모두 attach.
2. **5.9% 영상-임상 미스매치는 visit 단위 자동 제외.** `merged.csv` 에는 임상 visit 만 들어있어 영상-only 381명이 자연스럽게 제외됨.
3. **시간 매칭 윈도우는 분석 전 결정.** ±90일 (strict) 가 default 권장. 너무 넓으면 cross-disease attribution 오류 위험.
4. **fcsf 컬럼 순서는 `(NACCADC, NACCID)`.** join 시 컬럼명으로 (위치 의존 코드 금지).
5. **NACC SCAN MRI/PET 의 visit 매칭은 NACCVNUM 이 아닌 SCANDATE.** ±윈도우 매칭이 표준.
6. **ADSP-PHC 는 NACCID 직접 사용.** 별도 ID 매핑 없이 left-join 가능.
7. **Tier 간 cross-join 금지.** Investigator 와 Commercial 을 섞어서 union 하면 DUA 위반 — 하나의 분석은 하나의 tier 내부에서만.

> 검증일 2026-05-01 (freeze v71)
