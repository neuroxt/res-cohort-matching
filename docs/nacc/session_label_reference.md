# NACC Visit / Packet / Session 그래머 (NACC-specific overlay)

NACC UDS visit/packet 운영 표준 (PACKET 코드, NACCVNUM 의미, missing-code 처리, 영상-임상 시간 매칭) 은 [`docs/_shared/nacc_session_labels.md`](../_shared/nacc_session_labels.md) 에 통합. 본 overlay 는 NACC 코호트가 freeze 데이터에서 visit 을 *어떻게 키 표현* 하는지 — `(NACCID, NACCVNUM, PACKET, VISITDATE)` 4-tuple 운영 — 만 구체화한다.

---

## 1. NACC visit 키 4-tuple

NACC core 임상 데이터 (`investigator_ftldlbd_nacc71.csv` 외) 는 visit 마다 다음 4-tuple 로 식별:

| 키 | 의미 | 형식 |
|----|------|------|
| `NACCID` | Subject ID | `NACC` + 6 digits (예: `NACC252073`) |
| `NACCVNUM` | Visit sequence (1-based) | 1, 2, 3, ..., 11 (subject 별 max 11회 관찰) |
| `PACKET` | Packet 종류 | `I` / `F` / `T` |
| `VISITMO` + `VISITDAY` + `VISITYR` | 절대 시간 (cross-subject 비교용) | YYYY/MM/DD |

OASIS3 와 달리 NACC 는 **고정 visit code 가 없는 longitudinal cohort** 가 아니다. NACCVNUM 이 subject 내 sequence number 역할을 하며, PACKET 은 visit 종류를 구별한다.

```python
# Visit-level row 식별 (예시)
visit_key = ['NACCID', 'NACCVNUM']
df.set_index(visit_key)
```

---

## 2. PACKET 코드 (NACC freeze 분포)

| PACKET | 의미 | NACC freeze 에서의 일반 비율 |
|--------|------|-----------------------------|
| `I` | Initial Visit Packet (entry visit) | subject 당 1행 — IVP 만 1회 시행 |
| `F` | Follow-up Visit Packet | 매년 1회 (±6개월). subject 당 평균 ~3–5 visit |
| `T` | Telephone Follow-up | 대면 visit 불가 시 대체. 전체 visit 의 일부 |

> 분기 freeze 갱신마다 같은 (NACCID, NACCVNUM) 이 **PACKET 변경 없이** 데이터 update 만 발생할 수 있음 (예: 진단 재판정, 영상 검사 추가 결과). 따라서 **freeze 시점 명시** 가 reproducibility 에 필수.

---

## 3. NACCVNUM longitudinal 처리 패턴

```python
import pandas as pd

df = pd.read_csv("investigator_ftldlbd_nacc71.csv")

# 1. Subject 별 visit 수 분포
visit_counts = df.groupby('NACCID')['NACCVNUM'].max()
print(visit_counts.describe())   # mean ~3.7, max 11+

# 2. Subject 별 baseline visit 만 (NACCVNUM=1)
baseline = df[df['NACCVNUM'] == 1]

# 3. Subject 별 latest visit (가장 큰 NACCVNUM)
latest = df.loc[df.groupby('NACCID')['NACCVNUM'].idxmax()]

# 4. Trajectory: 첫 ↔ 마지막 visit 차이
def visit_span_days(group):
    g = group.sort_values('NACCVNUM')
    first_date = pd.to_datetime(
        f"{g.iloc[0]['VISITYR']}-{g.iloc[0]['VISITMO']:02d}-{g.iloc[0]['VISITDAY']:02d}")
    last_date = pd.to_datetime(
        f"{g.iloc[-1]['VISITYR']}-{g.iloc[-1]['VISITMO']:02d}-{g.iloc[-1]['VISITDAY']:02d}")
    return (last_date - first_date).days

trajectories = df.groupby('NACCID').apply(visit_span_days)
```

---

## 4. PACKET 별 폼 결측 패턴

PACKET 종류에 따라 **시행되지 않는 폼이 다르다**:

| 폼 | IVP (`I`) | FVP (`F`) | TFP (`T`) |
|----|-----------|-----------|----------|
| A1 (인구통계) | ✅ | ✅ | ✅ |
| A2 (informant 인구통계) | ✅ | ✅ | △ (informant 가능 시) |
| A3 (가족력) | △ (optional) | △ | ❌ |
| A4 (약물) | ✅ | ✅ | ✅ |
| A5 (건강력) | ✅ | ✅ | △ |
| B1 (신체검사) | ✅ | ✅ | **❌ 대면 필요** |
| B4 (CDR + MMSE) | ✅ | ✅ | △ |
| B5 (NPI-Q) | ✅ | ✅ | ✅ |
| B7 (FAQ) | ✅ | ✅ | ✅ |
| B8 (신경학적 검사) | ✅ | ✅ | **❌ 대면 필요** |
| B9 (clinician symptoms) | ✅ | ✅ | △ |
| C1 (인지검사) | ✅ | ✅ | △ (전화 가능 검사만) |
| D1 (clinician diagnosis) | ✅ | ✅ | △ |
| D2 (의학 상태) | ✅ | ✅ | △ |
| FTLD3 (FVP/IVP) | △ (FTD 의심 시) | △ | ❌ |
| LBD3.1 (FVP/IVP) | △ (DLB 의심 시) | △ | ❌ |

분석 시:

```python
# Telephone visit 만 필터링
telephone = df[df['PACKET'] == 'T']
# B1 (신체검사) 결측 check
print(telephone['WEIGHT'].isna().sum() / len(telephone))   # → 가까이 1.0 expected
```

---

## 5. NACC 절대 시간 vs 상대 시간

NACC freeze 는 **절대 날짜 (`VISITMO/DAY/YR`) 가 그대로 있다** (de-identification 약함). OASIS3 의 `days_to_visit` 처럼 anchor 기준 상대 일수 변환이 적용되지 않음.

따라서:
- **Cross-subject 동기화 가능** (예: 같은 분기에 visit 한 subject 묶기).
- **Site/year effect 분석 가능** (예: ADRC × visit year).
- 하지만 **개인정보 보호 강화** (publication 시 절대 시간 노출 제한 권장 — 5-year window aggregate 등).

```python
# 분기별 visit 분포
df['VISIT_QUARTER'] = pd.to_datetime(
    df[['VISITYR','VISITMO','VISITDAY']].rename(
        columns={'VISITYR':'year','VISITMO':'month','VISITDAY':'day'})
).dt.to_period('Q')
df.groupby('VISIT_QUARTER').size()
```

---

## 6. Visit ID 가 없다 — `NACCVNUM` + `PACKET` 으로 합성

NACC visit 에는 OASIS3 의 `OASIS_session_label` 같은 **단일 텍스트 ID 가 없다**. 분석 시 필요하면 합성:

```python
df['visit_id'] = df['NACCID'] + '_v' + df['NACCVNUM'].astype(str) + '_' + df['PACKET']
# 예: 'NACC252073_v3_F'
```

---

## 7. 영상 ↔ 임상 visit 매칭

자세한 운영 표준은 [`docs/_shared/nacc_session_labels.md` §6](../_shared/nacc_session_labels.md) 에서 다룬다. NACC SCAN 파일의 `SCANDATE` ↔ UDS visit 의 `VISITDATE` (= `VISITMO/DAY/YR` 합성) 를 ±90일 윈도우로 nearest-match.

NeuroXT-built `merged.csv` 에는 이미 `(NACCID, NACCVNUM)` 단위로 nearest amyloid/tau PET SUVR 이 inner-join 되어 있다 (자세한 컬럼 별 source 매핑은 [`merged_csv.md`](merged_csv.md)).

---

## 8. NACC 5.9% 영상-임상 미스매치 (Issue #7)

NII_NEW/ 에 영상이 있는 6,481 명 중 **381명 (5.9%) 이 임상 데이터가 *전혀* 없음**. 

| 유형 | 인원 | 처리 |
|------|------|------|
| 영상 + 임상 둘 다 | 6,100 | 정상 분석 대상 |
| **영상 only (임상 부재)** | **381 (5.9%)** | `merged.csv` 에 행 없음 — 분석 시 자동 제외되거나 `imaging-only cohort` 로 별도 처리 |
| 임상 only (영상 없음) | ~48,904 | imaging-dependent 분석에서는 자동 제외 |

> 패턴: 임상 데이터가 있으면 거의 100% 채워짐. 없으면 통째로 부재 (binary). 자세한 처리는 [`join_relationships.md`](join_relationships.md) + [`imaging_inventory.md`](imaging_inventory.md).

원인: NACC UDS 파이프라인과 NACC SCAN 파이프라인이 독립 운영. 영상 제출은 자발적이고 기한 없음 → NACCID 만 부여된 상태에서 영상 먼저 제출되는 케이스 발생.

---

## Known limitations & quirks

1. **NACC 는 단일 텍스트 session label 이 없다.** OASIS3 의 `OAS3xxxx_<token>_d####` 같은 합성 키가 없으므로 visit 단위 분석은 `(NACCID, NACCVNUM)` tuple 사용.
2. **PACKET 변경 없이 freeze 사이 데이터 update.** 같은 (NACCID, NACCVNUM, PACKET) 행이 분기 freeze마다 진단/영상/부검 결과가 update 될 수 있다. **freeze 시점 명시** 필수.
3. **Telephone visit 의 결측 처리.** B1, B8 등 대면 필요 폼은 PACKET=T visit에서 통째 결측. 분석 전 PACKET 별 폼 결측 패턴 확인.
4. **NACCVNUM 은 1 부터 — 그러나 항상 IVP 가 NACCVNUM=1 은 아닐 수 있다.** 드물지만 freeze 사이에 IVP 가 추가로 들어와 sequence 번호가 재정렬되는 경우 — `NACCFDYS` (first IVP까지 일수) 로 검증 권장.
5. **절대 날짜 (`VISITMO/DAY/YR`) 노출.** NACC 는 de-identification이 약하다. publication 시 절대 시간 노출 제한 (e.g., 5-year aggregate) 권장.

> 검증일 2026-05-01 (freeze v71)
