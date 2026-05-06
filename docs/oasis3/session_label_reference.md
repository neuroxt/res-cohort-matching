# OASIS3 Session Label & days_to_visit overlay (OASIS3-specific)

OASIS3 임상 데이터는 NACC UDS visit/packet 표준을 따른다. PACKET 코드, NACCVNUM 의미, missing-code 처리, 영상-임상 시간 매칭 등 표준 운영 패턴은 [`docs/_shared/nacc_session_labels.md`](../_shared/nacc_session_labels.md) 에서 다룬다.

본 overlay 는 OASIS3 가 표준 위에 얹는 cohort-specific 사실 — 단일 텍스트 session label 형식, `days_to_visit` 컬럼 의미와 quirk, OASIS3 만의 form 토큰 (USDa3/USDb3 typo, c1 = `psychometrics`), 영상↔임상 매칭 — 을 정리한다.

> OASIS3는 ADNI/A4/NACC 와 달리 **고정 visit code (V1, V2, ...) 가 없다**. 모든 임상/영상 시점은 `(OASISID, days_to_visit)` 페어로 표현되며, 이를 표현하는 단일 텍스트 키가 **OASIS_session_label**이다.

---

## 1. Session Label Grammar

```
OAS3{0001-1379}_{FORM_TOKEN}_d{####}
```

| 위치 | 값 | 예시 |
|------|-----|------|
| Subject | `OAS3` + 4자리 ID (1-padded, 1379까지 — 2025-12 Tau 통합 후 +1; 원본 release는 1378까지) | `OAS30001`, `OAS31379` |
| 구분자 | `_` | |
| FORM_TOKEN | 폼 종류 | `UDSb4`, `USDa3`, `psychometrics`, `AV45`, `PIB` |
| 구분자 | `_` | |
| 일자 prefix | 리터럴 `d` | |
| days_to_visit | 정수 (음수 가능, zero-pad 4자리가 일반적) | `0000`, `0339`, `2430`, `-0002`, `-39520` |

예:
- `OAS30001_UDSb4_d0339` — subject 1, B4(CDR) form, day 339
- `OAS30001_AV45_d2430` — subject 1, AV45 amyloid PET scan, day 2430
- `OAS30290_UDSb4_d-0002` — 음수 days (희귀, 5건만 존재 — 아래 §3 참고)

---

## 2. FORM_TOKEN 표

**파일명과 session label 토큰이 일치하지 않는 경우가 있다** (실측 검증):

| 파일 | 파일명상 폼 | 실제 session label 토큰 | 비고 |
|------|-------------|------------------------|------|
| `OASIS3_UDSa1_participant_demo.csv` | a1 | `UDSa1` | 일치 |
| `OASIS3_UDSa2_cs_demo.csv` | a2 | `UDSa2` | 일치 |
| `OASIS3_UDSa3.csv` | a3 | **`USDa3`** | **`USD` typo** |
| `OASIS3_UDSa4D_med_codes.csv` | a4D | **`UDSa4`** | D suffix 없음 (a4G와 동일 토큰) |
| `OASIS3_UDSa4G_med_names.csv` | a4G | **`UDSa4`** | G suffix 없음 (a4D와 동일 토큰) |
| `OASIS3_UDSa5_health_history.csv` | a5 | `UDSa5` | 일치 |
| `OASIS3_UDSb1_physical_eval.csv` | b1 | `UDSb1` | 일치 |
| `OASIS3_UDSb2_his_cvd.csv` | b2 | `UDSb2` | 일치 |
| `OASIS3_UDSb3.csv` | b3 | **`USDb3`** | **`USD` typo (a3와 동일 패턴)** |
| `OASIS3_UDSb4_cdr.csv` | b4 | `UDSb4` | 일치 |
| `OASIS3_UDSb5_npiq.csv` | b5 | `UDSb5` | 일치 |
| `OASIS3_UDSb6_gds.csv` | b6 | `UDSb6` | 일치 |
| `OASIS3_UDSb7_faq_fas.csv` | b7 | `UDSb7` | 일치 |
| `OASIS3_UDSb8_neuro_exam.csv` | b8 | `UDSb8` | 일치 |
| `OASIS3_UDSb9_symptoms.csv` | b9 | `UDSb9` | 일치 |
| `OASIS3_UDSc1_cognitive_assessments.csv` | c1 | **`psychometrics`** | **`UDSc1` 아님 — 완전히 다른 토큰** |
| `OASIS3_UDSd1_diagnoses.csv` | d1 | `UDSd1` | 일치 |
| `OASIS3_UDSd2_med_conditions.csv` | d2 | `UDSd2` | 일치 |
| PET (centiloid, PET_json, PET_datasetdescription) | — | **트레이서명**: `PIB`, `AV45`, `AV1451`, `FDG` | 폼 자리에 트레이서가 들어감 |
| oasis_file_list NIfTI scan | — | (session label 미제공, `SUB_ID + VISIT + SEQ`만 존재) | `VISIT` = `d####` 또는 `unmatched` |

> **분석 시 주의**:
> - Session label로 폼 종류를 판별할 때 정규식 `_(UDS[a-d][0-9]+|USDa3|USDb3|psychometrics|AV45|AV1451|PIB|FDG)_`로 매칭.
> - a4D vs a4G 구분은 session label만으로 불가능. 파일별로 처리해야 함.
> - 같은 visit에서 여러 폼이 수집되어도 session label은 form별로 고유하므로 visit 묶기는 `(OASISID, days_to_visit)` 사용.

---

## 3. days_to_visit 의미

`days_to_visit` 컬럼 자체와 session label의 `d####` 부분은 **동일 값**이지만, **컬럼의 데이터 타입이 파일마다 다르다** (실측 확인):

| 파일 | days_to_visit 컬럼 형식 |
|------|------------------------|
| a1, a3, a5, b1, b2, b3, b5, b6, b7, b8, b9, d1, d2 | **Zero-padded 4-digit 문자열** (`'0000'`, `'0339'`) |
| b4, c1 | **정수 문자열** (`'0'`, `'14'`, `'339'`) |

> 분석 시 `pd.read_csv(..., dtype={'days_to_visit': 'Int64'})`로 명시적 정수 변환 권장. 그렇지 않으면 같은 visit이지만 `'0000'` ≠ `'0'`이 되어 join 실패.

```python
# 권장 패턴
df = pd.read_csv(file, dtype={'days_to_visit': str})
df['days_to_visit'] = pd.to_numeric(df['days_to_visit'], errors='coerce').astype('Int64')
```

### 기준점

- **`d0000` = subject별 첫 방문일**. 각 subject마다 독립.
- **다른 subject의 `d0000`은 시간적으로 무관**. 절대 날짜 정보 없음 (de-identification).
- 따라서 **cross-subject 동기화는 불가능** — `days_to_visit`만으로 두 subject를 같은 시점에서 비교할 수 없다.

### 일반적 분포 (b4 폼 실측, 8,627행 기준)

| days_to_visit | 행 수 | 비고 |
|---------------|-------|------|
| 0 (`d0000`) | 1,355 | 첫 visit |
| > 0 | 7,266 | 추적 visit |
| < 0 | **5** | 데이터 이상치 (아래 참고) |

### 음수 days_to_visit (이상치)

b4 폼에서 5건만 발견:

| OASISID | session_label | days_to_visit | age at visit |
|---------|---------------|---------------|--------------|
| OAS30290 | `OAS30290_UDSb4_d-0002` | -2 | 47.45 |
| OAS30330 | `OAS30330_UDSb4_d-0101` | -101 | 80.53 |
| OAS30380 | `OAS30380_UDSb4_d-0015` | -15 | 61.39 |
| OAS30753 | `OAS30753_UDSb4_d-39520` | **-39520** | **-47.25** | ← 명백한 데이터 입력 오류 |
| OAS30851 | `OAS30851_UDSb4_d-0001` | -1 | 73.49 |

> 분석 시 `days_to_visit < 0` 또는 `age at visit < 0` 인 행은 필터링하거나 별도 처리 권장.

---

## 4. Multi-form same-day 묶기

같은 visit에서 수집된 여러 폼은 **`(OASISID, days_to_visit)` 페어**로 묶인다. Session label로는 묶을 수 없다 (form 토큰이 다름).

```
OAS30001_UDSa1_d0000      ┐
OAS30001_UDSa5_d0000      │
OAS30001_UDSb1_d0000      │
OAS30001_UDSb4_d0000      ├─ Initial Visit Packet 묶음
OAS30001_USDa3_d0000      │  (subject 1의 첫 방문)
OAS30001_psychometrics_d0000 ┘
```

> b3(UPDRS)와 a3(family history)는 optional module이므로 같은 visit에 항상 존재하지 않는다. 자세한 내용은 [`uds_forms.md`](uds_forms.md).

---

## 5. 영상 ↔ 임상 visit 매칭

### oasis_file_list.csv VISIT 컬럼 분포

42,907 NIfTI 파일 중:

| VISIT 값 | 행 수 | 비고 |
|---------|-------|------|
| `d0000` | 14,238 | First visit 영상이 압도적으로 많음 |
| `unmatched` | 5,223 | **임상 visit과 매칭 실패** — UDS 폼이 없는 시점에 촬영된 스캔 |
| 그 외 `d####` (다양) | 23,446 | follow-up 시점 |

> `unmatched`는 임상 데이터 없이 영상만 존재하는 스캔 (예: 별도 imaging-only sub-study 또는 임상 visit 윈도우 밖 촬영).

### oasis3.csv `*_diff` 컬럼

`oasis3.csv`(8,627행, 10컬럼)의 modality별 `*_diff` 컬럼은 **`*_diff = refdate − scan_date`** (실측 검증):

```
ID         refdate  FDG  FDG_diff   AV45  AV45_diff  MR    MR_diff   PIB    PIB_diff
OAS30001   0        NA   NA         NA    NA         129   -129      NA     NA
OAS30001   722      NA   NA         NA    NA         757   -35       NA     NA
OAS30001   339      NA   NA         NA    NA         NA    NA        423    -84
```

- `MR_diff = -129`: refdate=0, MR=d129이므로 0 − 129 = −129. 즉 **음수 = 영상이 임상 ref보다 *이후*** 촬영됨.
- `MR_diff = -35`: refdate=722, MR=d757이므로 722 − 757 = −35.

| MR_diff 부호 | 해석 |
|--------------|------|
| 0 | 같은 날 |
| 양수 (+N) | 영상이 임상 ref보다 N일 *이전* |
| 음수 (−N) | 영상이 임상 ref보다 N일 *이후* |

자세한 분석 가이드는 [`file_index.md`](file_index.md).

### PET session label vs UDS session label

PET의 session label은 **트레이서가 폼 자리에 들어간다**:

```
OAS30001_AV45_d2430    # AV45 amyloid PET, day 2430
OAS30001_PIB_d4467     # PIB amyloid PET, day 4467
OAS30001_AV1451_d3500  # AV1451 tau PET, day 3500
OAS30001_FDG_d3500     # FDG metabolism PET, day 3500
```

→ PET label과 UDS label은 직접 join 불가. `(OASISID, days_to_visit)`로 가까운 임상 visit과 매칭 (보통 ±90일 윈도우).

---

## 6. 분석 시 권장 정규식 패턴

```python
import re

# 모든 session label에서 (subject, form_token, days) 추출
SESSION_LABEL_RE = re.compile(
    r"^(OAS3\d{4})_"
    r"(UDS[a-d]\d|USDa3|USDb3|psychometrics|AV45|AV1451|PIB|FDG)"
    r"_d(-?\d+)$"
)

m = SESSION_LABEL_RE.match("OAS30001_UDSb4_d0339")
# subject = "OAS30001", form = "UDSb4", days = "0339"
```

### Form token → 파일명 매핑

```python
FORM_TOKEN_TO_FILE = {
    "UDSa1": "OASIS3_UDSa1_participant_demo.csv",
    "UDSa2": "OASIS3_UDSa2_cs_demo.csv",
    "USDa3": "OASIS3_UDSa3.csv",                          # USD typo
    "UDSa4": ["OASIS3_UDSa4D_med_codes.csv",              # 1:N — 둘 다 매칭
              "OASIS3_UDSa4G_med_names.csv"],
    "UDSa5": "OASIS3_UDSa5_health_history.csv",
    "UDSb1": "OASIS3_UDSb1_physical_eval.csv",
    "UDSb2": "OASIS3_UDSb2_his_cvd.csv",
    "USDb3": "OASIS3_UDSb3.csv",                          # USD typo
    "UDSb4": "OASIS3_UDSb4_cdr.csv",
    "UDSb5": "OASIS3_UDSb5_npiq.csv",
    "UDSb6": "OASIS3_UDSb6_gds.csv",
    "UDSb7": "OASIS3_UDSb7_faq_fas.csv",
    "UDSb8": "OASIS3_UDSb8_neuro_exam.csv",
    "UDSb9": "OASIS3_UDSb9_symptoms.csv",
    "psychometrics": "OASIS3_UDSc1_cognitive_assessments.csv",  # 토큰명이 완전히 다름
    "UDSd1": "OASIS3_UDSd1_diagnoses.csv",
    "UDSd2": "OASIS3_UDSd2_med_conditions.csv",
    "AV45": ["OASIS3_amyloid_centiloid.csv",
             "OASIS3_PET_json.csv",
             "OASIS3_PET_datasetdescription.csv"],
    "PIB": ["OASIS3_amyloid_centiloid.csv",
            "OASIS3_PET_json.csv",
            "OASIS3_PET_datasetdescription.csv"],
    "AV1451": ["OASIS3_PET_json.csv",
               "OASIS3_PET_datasetdescription.csv"],     # centiloid에는 없음 (amyloid only)
    "FDG": ["OASIS3_PET_json.csv",
            "OASIS3_PET_datasetdescription.csv"],
}
```

---

## 7. 참고

- `OASIS_session_label`은 form-specific. **Visit 묶기에는 `(OASISID, days_to_visit)` 사용**.
- A3, B3는 optional module → 행 수 4,090. 같은 visit에서 누락될 수 있음.
- C1는 v2(`UDSc1` 미사용) → v3(`psychometrics` 토큰)로 명명 변경됨. UDS v3 명명 컨벤션에서 C1 폼이 "Neuropsychological Battery"이므로 OASIS3 처리 시 `psychometrics`로 통합한 것으로 보임.
- 데이터 입력 오류 (음수 days_to_visit, 음수 age) 5건 존재 — 분석 전 검증 권장.

---

## 8. 참고 문서

| 문서 | 내용 |
|------|------|
| [`docs/_shared/nacc_session_labels.md`](../_shared/nacc_session_labels.md) | NACC UDS visit/packet 표준 (PACKET=I/F/T, missing-code, 영상-임상 시간 매칭) |
| [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) | NACC UDS 17 폼 컬럼 정의 / 코딩 |
| [`uds_forms.md`](uds_forms.md) | OASIS3 폼별 파일명 / 행 수 / OASIS3 session token 표 |
| [`file_index.md`](file_index.md) | OASIS3 NIfTI 파일 인덱스, BIDS 명명, `*_diff` 부호 |
