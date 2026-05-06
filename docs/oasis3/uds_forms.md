# OASIS3 NACC UDS 폼 overlay (OASIS3-specific)

OASIS3 임상 데이터는 **NACC UDS 표준** 을 따른다. 17 UDS 폼 (A1–D2) 의 **컬럼 정의 / 코딩 / 분석 패턴** 은 모두 [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) 에서 다룬다.

본 overlay 는 OASIS3 가 NACC UDS 표준 위에 얹는 cohort-specific 사실 — 파일명 / 행·열 수 / OASIS3 session label 토큰 (UDS 표준에서 살짝 빗나간 부분 포함) — 만 정리한다.

> **공통 prefix 4 컬럼** (모든 OASIS3 UDS 폼 파일의 처음 4 컬럼):
> - `OASISID` — 피험자 ID (`OAS3xxxx`)
> - `OASIS_session_label` — 세션 라벨 (form-specific 토큰. 자세한 것은 [`session_label_reference.md`](session_label_reference.md))
> - `days_to_visit` — 첫 방문 기준 경과일 (정수, 음수 가능 5건)
> - `age at visit` — 해당 visit 시점 나이 (소수점 둘째자리)

---

## 1. 폼-별 OASIS3 파일 목록

| Form | OASIS3 파일 | 행 | 열 | OASIS3 session token | 비고 |
|------|------------|------|------|---------------------|------|
| A1 | `OASIS3_UDSa1_participant_demo.csv` | 8,500 | 14 | `UDSa1` | 일치 |
| A2 | `OASIS3_UDSa2_cs_demo.csv` | 8,500 | 17 | `UDSa2` | 일치 |
| A3 | `OASIS3_UDSa3.csv` | 4,090 | **398** | **`USDa3`** | **`USD` typo** (UDS 글자 순서 뒤바뀜); optional → 행 수 적음 |
| A4-D | `OASIS3_UDSa4D_med_codes.csv` | 7,617 | 51 | **`UDSa4`** | D suffix 없음 (a4G와 동일 토큰) |
| A4-G | `OASIS3_UDSa4G_med_names.csv` | 7,617 | 51 | **`UDSa4`** | G suffix 없음 (a4D와 동일 토큰) |
| A5 | `OASIS3_UDSa5_health_history.csv` | 8,500 | 72 | `UDSa5` | 일치 |
| B1 | `OASIS3_UDSb1_physical_eval.csv` | 8,627 | 15 | `UDSb1` | 일치 |
| B2 | `OASIS3_UDSb2_his_cvd.csv` | 8,500 | 20 | `UDSb2` | 일치 |
| B3 | `OASIS3_UDSb3.csv` | **4,090** | 32 | **`USDb3`** | `USD` typo (a3와 동일 패턴); optional |
| B4 | `OASIS3_UDSb4_cdr.csv` | **8,627** | 23 | `UDSb4` | 일치 |
| B5 | `OASIS3_UDSb5_npiq.csv` | 8,500 | 29 | `UDSb5` | 일치 |
| B6 | `OASIS3_UDSb6_gds.csv` | 8,500 | 21 | `UDSb6` | 일치 |
| B7 | `OASIS3_UDSb7_faq_fas.csv` | 8,500 | 14 | `UDSb7` | 일치 |
| B8 | `OASIS3_UDSb8_neuro_exam.csv` | 8,500 | 50 | `UDSb8` | 일치 |
| B9 | `OASIS3_UDSb9_symptoms.csv` | 8,500 | 58 | `UDSb9` | 일치 |
| C1 | `OASIS3_UDSc1_cognitive_assessments.csv` | 7,925 | **107** | **`psychometrics`** | **`UDSc1` 아님 — 완전히 다른 토큰** |
| D1 | `OASIS3_UDSd1_diagnoses.csv` | 8,500 | **149** | `UDSd1` | 가장 풍부한 진단 정보 |
| D2 | `OASIS3_UDSd2_med_conditions.csv` | 8,500 | 32 | `UDSd2` | 일치 |

> **OASIS3 임상 데이터는 폼별 별도 CSV** 로 배포된다 (NACC core 가 단일 통합 `investigator_ftldlbd_nacc71.csv` 에 합치는 것과 다름). 폼-form join은 `(OASISID, days_to_visit)` 페어로 묶는다.

---

## 2. OASIS3-specific quirk

### 2.1 Session token typo (USDa3, USDb3)

`OASIS3_UDSa3.csv` 와 `OASIS3_UDSb3.csv` 는 파일명에는 `UDS` 가 정상 표기되지만 session label 토큰은 **`USDa3`, `USDb3`** 로 글자 순서가 뒤바뀐 typo. 분석 시 정규식이 양쪽 다 매칭하도록 작성:

```python
SESSION_FORM_RE = r"(UDS[a-d]\d|USDa3|USDb3|psychometrics|AV45|AV1451|PIB|FDG)"
```

### 2.2 C1 토큰 = `psychometrics`

UDS v3 명명 컨벤션에서 C1 폼이 "Neuropsychological Battery" 이므로 OASIS3 처리 시 토큰을 `psychometrics` 로 통합한 것으로 보임. **`UDSc1` 토큰은 OASIS3 session label에 존재하지 않는다.**

### 2.3 A4-D 와 A4-G 동일 토큰

UDS v3에서 a4 폼이 D(코드) + G(이름) 둘로 분할됐지만 OASIS3 session label에서는 둘 다 `UDSa4`. 따라서 session label 만으로 D vs G 구별 불가. 파일별로 따로 읽고 `(OASISID, days_to_visit)` KEY 로 join.

### 2.4 days_to_visit 음수 (5건)

`UDSb4` 폼에 5건의 음수 days_to_visit 가 존재 (자세한 표는 [`session_label_reference.md`](session_label_reference.md)).

### 2.5 dx1 free text 분포 (실측, b4 폼 8,627행 기준 상위)

| dx1 | 행 수 | 비고 |
|-----|-------|------|
| Cognitively normal | 6,401 | 가장 많음 |
| AD Dementia | 1,145 | NIA-AA criteria |
| uncertain dementia | 475 | |
| Unc: ques. Impairment | 80 | |
| AD dem w/depresss | 71 | AD + 우울 |
| DLBD | 49 | Dementia with Lewy Bodies |
| `.` (period) | 43 | NACC missing notation |
| No dementia | 37 | |
| (그 외 free text 다수) | | 자세한 mapping은 NACC RDD |

> dx1 free text 는 NACC 표준 카테고리에 1:1 mapping 되지 않는다. 일관된 그룹 분류는 D1 binary flag 사용 권장 (자세한 컬럼은 [`docs/_shared/nacc_uds_forms.md` D1 절](../_shared/nacc_uds_forms.md)).

---

## 3. 기타 OASIS3 dataset 특이사항

| 항목 | 값 |
|------|----|
| Cohort | WUSTL Knight ADRC retrospective 통합 (single ADRC, NACCADC = 0001 등가) |
| Subject ID | `OAS3xxxx` (1-padded 4 digits, 1379 subjects — 2025-12 Tau 통합 후 +1; 원본 release 1,378) |
| UDS 버전 | v2 ↔ v3 mix (FORMVER 컬럼 없음 — visit별 검사 셋으로 추정) |
| Optional 모듈 | A3 (4,090행), B3 (4,090행) |
| 폼-form join 키 | `(OASISID, days_to_visit)` |

---

## 4. NACC RDD 외부 참조

NACC RDD 는 OASIS3 코호트 자체에는 동봉되지 않는다 (OASIS3 는 별도 분석 가이드 / Knight ADRC 문서 사용). 외부 다운로드:

- **공식 RDD-UDS-3 PDF**: https://files.alz.washington.edu/documentation/uds3-rdd.pdf
- **NACC Forms documentation**: https://naccdata.org/data-collection/forms-documentation/uds-3
- **UDS v3 발표 논문**: Weintraub S, et al. Alzheimer Dis Assoc Disord 2018;32(1):10-17.

> NACC 코호트 사용자는 NFS의 `NACC_NEW/ORIG/DEMO/Data_Directory/uds3-rdd.pdf` 를 이용. OASIS3 사용자는 위 외부 링크 참고.

---

## 5. 참고 문서

| 문서 | 내용 |
|------|------|
| [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) | NACC UDS 17 폼 컬럼 정의 / 코딩 / 분석 패턴 (NACC↔OASIS3 공통) |
| [`session_label_reference.md`](session_label_reference.md) | OASIS3 session label grammar (`OAS3xxxx_<token>_d####`), days_to_visit 의미 / 음수 quirk |
| [`data_catalog.md`](data_catalog.md) | OASIS3 24 CSV 마스터 인벤토리 |
| [`protocol.md`](protocol.md) | UDS v2 → v3 전환, OASIS3 코호트 구조 |
| [`join_relationships.md`](join_relationships.md) | OASIS3 form-form join, A4 D/G 페어링 |
