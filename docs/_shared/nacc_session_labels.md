# NACC UDS Visit / Packet / Session 그래머 (shared)

> **이 문서는 NACC UDS visit/packet 표준이며 NACC / OASIS3 양쪽이 참조한다.**
> 각 cohort가 visit 키를 어떻게 표현하는지는 cohort overlay 문서:
> - **NACC**: [`docs/nacc/session_label_reference.md`](../nacc/session_label_reference.md) — `(NACCID, NACCVNUM, PACKET, VISITDATE)` 운영 모델
> - **OASIS3**: [`docs/oasis3/session_label_reference.md`](../oasis3/session_label_reference.md) — `OAS3xxxx_<token>_d####` 형식, days_to_visit 음수 quirk 5건

NACC UDS visit는 **연 1회 (±6개월 윈도우)** 시행되며, 각 visit는 packet 단위로 운영된다. 본 문서는 표준 PACKET 코드 / NACCVNUM 의미 / NACC 형식 임상 데이터의 longitudinal 처리 패턴을 다룬다.

---

## 1. PACKET 코드

NACC UDS visit는 packet 종류로 구분:

| PACKET 코드 | 의미 | 시행 형태 | 빈도 |
|-------------|------|-----------|------|
| `I` | **Initial Visit Packet** | 첫 정식 visit (전체 폼 시행) | subject당 1회 (entry visit) |
| `F` | **Follow-up Visit Packet** | 후속 정기 visit (전체 폼 + 변경분) | 매년 1회 (±6개월) |
| `T` | **Telephone Follow-up** | 일부 인지 평가 + interview 만 전화 | 대면 visit 불가 시 대체 |

분기 freeze 도중 같은 `(NACCID, NACCVNUM)` 행이 다른 PACKET 으로 누적될 수 있다 (예: V1 = I, V2 = F, V3 = F, V4 = T).

---

## 2. NACCVNUM (Visit Number)

NACC visit는 1-based 정수 visit number로 식별:

| 컬럼 | 의미 |
|------|------|
| `NACCVNUM` | Visit sequence number per subject. 처음 IVP visit이 1, 각 후속 FVP/TFP visit은 2, 3, ... |
| `NACCAVST` | Available visit count (해당 subject의 누적 visit 수) |
| `NACCNVST` | Total visit count (예측 포함, 일부 freeze에서 보정 값) |
| `NACCDAYS` | First visit (NACCVNUM=1) ↔ current visit 사이 일수 |
| `NACCFDYS` | First visit ↔ first IVP 사이 일수 (visit 1이 IVP가 아닌 경우 — 드물지만 발생) |

> `NACCVNUM` 은 **subject 내부 sequence**. cross-subject 비교 (예: "동시간대 visit 묶기") 에는 사용 불가 — 각 subject 마다 V1 시작 시점이 다르다. cross-subject 비교는 절대 시간 (`VISITMO/DAY/YR`) 기반으로 해야 한다.

---

## 3. Visit-form 묶기

같은 visit에서 여러 폼 (A1, A5, B1, B4, B5, B6, B7, B8, B9, C1, D1, D2 + 옵셔널) 이 동시에 작성된다.

### NACC 단일 통합 파일에서 묶기

NACC v71 freeze 표준 배포 (`investigator_ftldlbd_nacc71.csv`) 는 **모든 폼이 한 행에 통합** (long-format wide-by-form). 따라서 `(NACCID, NACCVNUM)` 으로 visit 단위 row 가 하나만 존재.

```python
# (NACCID, NACCVNUM) 단위 visit-level 분석
visit_df = df.set_index(['NACCID', 'NACCVNUM'])
```

### 형식 분리 파일에서 묶기 (OASIS3 패턴)

OASIS3는 폼별 별도 CSV. 같은 visit 묶기는 cohort-specific 키로 (OASIS3 의 경우 `(OASISID, days_to_visit)`). cohort overlay 문서 참조.

---

## 4. Optional module visit 누락

A3 (가족력), B3 (UPDRS), FTLD3, LBD3.1 등은 optional. 따라서 같은 visit에서 누락 가능. 분석 시 outer join으로 처리.

```python
# A1 (full UDS visit) ⟕ A3 (optional)
combined = a1.merge(a3, on=['NACCID', 'NACCVNUM'], how='left')
# how='left': A3가 없는 visit도 보존
```

---

## 5. NACC missing-code 처리 패턴

```python
import pandas as pd
import numpy as np

NACC_MISSING_INTEGER = [88, 99, 888, 999, 9999]
NACC_NA_TEXT = ['.', 'NA', 'unknown']  # NACC가 free-text에 쓰는 placeholder

# integer/numeric 컬럼
df = df.replace(NACC_MISSING_INTEGER, np.nan)

# text 컬럼
text_cols = df.select_dtypes(include='object').columns
df[text_cols] = df[text_cols].replace(NACC_NA_TEXT, np.nan)
```

> **자릿수 매칭**: `88` 은 2-digit 변수에, `888` 은 3-digit, `999` 은 3-digit, `9999` 는 4-digit (e.g., year). 변수의 max 자릿수에 맞춰 missing-code가 다르다.
>
> 자세한 표는 [NACC UDS-3 RDD](https://files.alz.washington.edu/documentation/uds3-rdd.pdf) 의 "Missing data conventions" 섹션 참조.

---

## 6. 영상 ↔ 임상 visit 매칭

NACC SCAN imaging 정량화 파일 (`*_scan_*_nacc71.csv`) 은 임상 visit number (`NACCVNUM`) 가 아닌 **`SCANDATE`** 기반. 임상-영상 join은 시간 매칭으로 처리:

```python
import pandas as pd

# 임상 (UDS) visit
clin = pd.read_csv("...investigator_ftldlbd_nacc71.csv",
                   usecols=['NACCID', 'NACCVNUM', 'VISITMO', 'VISITDAY', 'VISITYR'])
clin['VISITDATE'] = pd.to_datetime(
    clin[['VISITYR', 'VISITMO', 'VISITDAY']].rename(
        columns={'VISITYR':'year', 'VISITMO':'month', 'VISITDAY':'day'}))

# 영상 (SCAN PET)
amyloid = pd.read_csv("...investigator_scan_amyloidpetnpdka_nacc71.csv",
                      usecols=['NACCID', 'SCANDATE', 'GAAIN_SUMMARY_SUVR'])
amyloid['SCANDATE'] = pd.to_datetime(amyloid['SCANDATE'])

# subject별 nearest visit
joined = pd.merge_asof(
    amyloid.sort_values('SCANDATE'),
    clin.sort_values('VISITDATE').rename(columns={'VISITDATE':'SCANDATE'}),
    on='SCANDATE', by='NACCID',
    direction='nearest', tolerance=pd.Timedelta('90D'))
```

> ±90일 윈도우는 NACC 분석에서 흔히 쓰이는 default. 윈도우 클수록 매칭률 ↑ 정확도 ↓ trade-off.

---

## 7. 자세한 cohort-specific 운영

| Cohort | 특이사항 | overlay 문서 |
|--------|----------|------------|
| NACC | `(NACCID, NACCVNUM, PACKET, VISITMO/DAY/YR)` 4-tuple visit key | [`docs/nacc/session_label_reference.md`](../nacc/session_label_reference.md) |
| OASIS3 | 단일 텍스트 session label (`OAS3xxxx_<token>_d####`), days_to_visit 음수 5건 quirk, c1 = `psychometrics` 토큰 (UDSc1 아님) | [`docs/oasis3/session_label_reference.md`](../oasis3/session_label_reference.md) |
