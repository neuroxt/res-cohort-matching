# OASIS3 Demographics CSV 컬럼 사전

`OASIS3_demographics.csv`의 컬럼 정의. **피험자당 1행** (subject-level cross-sectional). UDS A1/A2 폼이 visit-level에서 변동 가능 정보(주거·결혼·요양 등급 등)를 추적하는 반면, 이 파일은 변동되지 않는 baseline-level 정보를 담는다.

- **위치**: `/Volumes/nfs_storage/OASIS3/ORIG/DEMO/OASIS3_demographics.csv`
- **규모**: 1,379행 × 19컬럼
- **인덱스**: `OASISID` (unique, e.g., `OAS30001`)

---

## 컬럼 목록

### 식별자 (2 컬럼)

| 컬럼 | 설명 | Fill | 값 / 범위 |
|------|------|------|-----------|
| OASISID | 피험자 ID (unique) | 100% | `OAS30001` ~ `OAS31378` 패턴 |
| Subject_accession | 외부 accession 식별자 | **0%** (전부 빈 값) | 사용되지 않음 (legacy 컬럼) |

### 연령 (2 컬럼)

| 컬럼 | 설명 | Fill | 값 / 범위 |
|------|------|------|-----------|
| AgeatEntry | 연구 등록 시점 나이 (소수점 4자리, 일/365.25 정밀도) | 100% | 42.50 ~ 95.63세 |
| AgeatDeath | 사망 시점 나이 (사망 시만) | 21.8% (300명) | 57.13 ~ 101.85세. 빈 값 = 추적 중 또는 censored. |

> de-identification에서 90+ ceiling 처리는 적용되지 않음 (실측: 95.63 / 101.85). HIPAA Safe Harbor "90 이상은 1개 카테고리"는 NACC 정책이고, OASIS3는 자체 정책으로 정확한 값을 제공하는 것으로 보임. 분석 시 확인 권장.

### 성별 (1 컬럼)

| 컬럼 | 설명 | Fill | 값 |
|------|------|------|-----|
| GENDER | 성별 | 100% | **1=Male, 2=Female** (NACC 표준) |

### 교육·사회경제 (2 컬럼)

| 컬럼 | 설명 | Fill | 값 / 범위 |
|------|------|------|-----------|
| EDUC | 교육 연수 | ~99.9% | 6 ~ 24 (29 1건) |
| SES | Hollingshead Socioeconomic Status | 일부 missing | 1 ~ 5 (1=highest, 5=lowest) |

### 인종·민족 (8 컬럼)

OASIS3 demographics의 race 인코딩은 **4중 표현**되어 있어 일관성 주의:

#### racecode + race 텍스트 (실측 매핑)

| racecode | race 텍스트 | 행 수 | 의미 |
|----------|-------------|-------|------|
| 0 | `Unknown` | 7 | 미보고 |
| 1 | `AIAN` | 1 | American Indian / Alaskan Native |
| 2 | `ASIAN` | 7 | Asian |
| 4 | `Black` | 209 | Black / African American |
| 5 | `White` | 1,151 | White (대다수) |
| 6 | `more than one` | 3 | 다인종 |
| (3은 사용되지 않음) | | | |

#### Race flag 컬럼 (5개)

기본적으로 racecode와 일치하지만 일부 레거시 레코드에서 **빈 값**과 0이 혼재:

| 컬럼 | 설명 | 값 |
|------|------|-----|
| AIAN | American Indian / Alaskan Native flag | 0/1, 일부 빈 값 |
| NHPI | Native Hawaiian / Pacific Islander flag | 0/1, **이 데이터에서 NHPI=1 사례 없음** |
| ASIAN | Asian flag | 0/1, 일부 빈 값 |
| AA | African American flag (= Black) | 0/1, 일부 빈 값 |
| WHITE | White flag | 0/1, 일부 빈 값 |

> "more than one" 카테고리는 두 flag가 모두 1인 경우(예: AIAN=1, WHITE=1, 또는 AIAN=1, AA=1, WHITE=1)로 구분 가능.

#### ETHNIC

| 컬럼 | 설명 | 값 |
|------|------|-----|
| ETHNIC | Hispanic/Latino origin | **0=Not Hispanic, 1=Hispanic, 빈 값=Unknown** |

> 실측: ETHNIC=1 사례 1건 (race=White), ETHNIC 빈 값은 191건 (대부분 racecode 5).

**race × ETHNIC 분포** (실측):

| race | ETHNIC=0 | ETHNIC=1 | ETHNIC=blank |
|------|----------|----------|--------------|
| White | 988 | 1 | 162 |
| Black | 189 | — | 20 |
| ASIAN | 5 | — | 2 |
| AIAN | 1 | — | — |
| more than one | 3 | — | — |
| Unknown | — | — | 7 |

### 가족력 (2 컬럼)

부모의 치매 이력. UDS A3 폼은 longitudinal로 더 상세히 가족력을 추적하지만, 이 컬럼은 cross-sectional 요약.

| 컬럼 | 설명 | 값 / 분포 |
|------|------|-----------|
| daddem | 아버지 치매 여부 | 0=No (901), 1=Yes (277), 5=Unknown (115), 빈 값 (85) |
| momdem | 어머니 치매 여부 | 0=No (668), 1=Yes (551), 5=Unknown (98), 9=N/A (1), 빈 값 (60) |

> 어머니 치매 양성률 (551/1,278 ≈ 43%)이 아버지(277/1,178 ≈ 23%)보다 약 2배 높다 — 여성 평균 수명이 길어 치매 발현률이 높은 일반적 관찰과 일치.

### 우세손 (1 컬럼)

| 컬럼 | 설명 | 값 |
|------|------|-----|
| HAND | Handedness | **R**=오른손잡이, **L**=왼손잡이, **B**=양손잡이, 빈 값=Unknown |

### APOE 유전자형 (1 컬럼)

| 컬럼 | 설명 | 값 |
|------|------|-----|
| APOE | APOE genotype (2자리 정수 표기) | `22, 23, 24, 33, 34, 44`. 추가로 `0`(결측 코드)과 `#N/A`(Excel-style 결측). |

**2자리 정수 인코딩 해석**:

| APOE 값 | Allele 조합 | 분포 의미 |
|---------|-------------|-----------|
| 22 | ε2/ε2 | 가장 희귀, 보호적 |
| 23 | ε2/ε3 | 보호적 (ε2 carrier) |
| 24 | ε2/ε4 | 혼합 |
| 33 | ε3/ε3 | 일반인 표준형 |
| 34 | ε3/ε4 | AD 위험 ↑ |
| 44 | ε4/ε4 | AD 위험 매우 ↑ |
| 0 | (결측) | NACC 코드: APOE 미측정 |
| `#N/A` | (결측) | Excel 출력 잔존 |

> **주의**: `0`과 `#N/A`는 모두 결측 의미이지만 다른 코드로 들어가 있다. 분석 시 `df['APOE'].replace(['0', '#N/A'], pd.NA)` 권장.

---

## 분석 권장 사항

### 1. APOE 정수 → 문자열 변환

```python
APOE_MAP = {22: "e2/e2", 23: "e2/e3", 24: "e2/e4",
            33: "e3/e3", 34: "e3/e4", 44: "e4/e4"}
df['APOE_str'] = pd.to_numeric(df['APOE'], errors='coerce').map(APOE_MAP)
```

### 2. APOE4 carrier 플래그

```python
# ε4 carrier = 24 or 34 or 44
df['APOE4_carrier'] = df['APOE'].isin(['24', '34', '44']).astype(int)
```

### 3. Race 표준화 (race 텍스트 우선, flag는 보조)

```python
# race 텍스트가 가장 일관적
df['race_clean'] = df['race'].fillna('Unknown')
```

### 4. AgeatEntry vs UDS `age at visit`

- `AgeatEntry`: 연구 등록 시점 (보통 첫 UDS visit)
- UDS 폼의 `age at visit`: 해당 visit 시점 나이 (longitudinal)

이 두 컬럼은 첫 visit(`d0000`)에서 거의 일치해야 한다. 차이가 큰 경우(>1년) 데이터 이상 의심.

```python
demo = pd.read_csv("OASIS3_demographics.csv")
b4 = pd.read_csv("OASIS3_UDSb4_cdr.csv")
b4_baseline = b4.query("days_to_visit == 0").rename(columns={"age at visit": "age_b4"})
merged = demo.merge(b4_baseline[['OASISID', 'age_b4']], on='OASISID')
diff = (merged['age_b4'] - merged['AgeatEntry']).abs()
# diff가 0.5세 이상인 경우 검토
```

### 5. Cross-sectional vs Longitudinal demographics

이 파일은 **cross-sectional** (피험자당 1행).
주거·결혼·독립 생활 등 **변동 가능한 정보**는 UDS A1(`OASIS3_UDSa1_participant_demo.csv`)에서 longitudinal로 확인:
- `LIVSIT`, `LIVSITUA` (거주 형태)
- `INDEPEND` (독립성 등급)
- `RESIDENC` (주거 type)
- `MARISTAT` (결혼 상태)

> 따라서 baseline 분석에서는 demographics.csv를 쓰되, "사용자가 nursing home에 들어갔는가?"같은 longitudinal 질문은 A1을 써야 한다.

---

## 알려진 한계

1. **Subject_accession 컬럼 사용되지 않음** (전부 빈 값) — 향후 무시 가능.
2. **APOE 결측 인코딩 비일관** (`0` vs `#N/A`).
3. **NHPI 사례 없음** — 인종 분포가 majority White (83.5%) + Black (15.2%) + 기타 1.3%로 편중되어 있다.
4. **`AgeatDeath` 78.2% missing** — 사망 정보는 retrospective 추적이므로 censored 데이터로 처리.
5. **EDUC 29 1건** — 박사 수준 이상으로 보이나 NACC 표준은 0-25. 분석 시 winsorize 고려.

---

## 참고 문서

| 문서 | 내용 |
|------|------|
| [`OASIS3_data_catalog.md`](OASIS3_data_catalog.md) | 24 CSV 마스터 인벤토리 |
| [`OASIS3_protocol.md`](OASIS3_protocol.md) | 코호트 구조, 진단 그룹, de-identification |
| [`OASIS3_uds_forms.md`](OASIS3_uds_forms.md) | UDS A1(longitudinal demographics 변경) 컬럼 |
| [`OASIS3_join_relationships.md`](OASIS3_join_relationships.md) | demographics → UDS / PET 조인 패턴 |
