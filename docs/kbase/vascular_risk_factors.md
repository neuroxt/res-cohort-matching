# 혈관위험인자 — `5_VascularRF.xlsx`

`/Volumes/nfs_storage/KBASE/ORIG/Demo/5_VascularRF.xlsx` (236 KB).

CRF code `B03` (혈관 위험인자 평가). 6 질환 × 5 sub-field + composite score = 50 컬럼.

---

## 시트 구성

| 시트 | rows | cols | 내용 |
|------|------|------|------|
| `Clinical2_B03_VRF` | 1,195 | 50 | 6 질환 × 5 sub-field |
| `memo` | 3 | 4 | partial codebook (헤더 매핑) |

→ K_visit 분포: 0:627 / 2:426 / 4:142 (V0/V2/V4 visit만, V1/V3 측정 없음).

---

## 컬럼 구조 (50 cols)

식별자 + Ref date + 6 질환 × 5 sub-field + 추가 + composite:

| 그룹 | 컬럼 |
|------|------|
| 식별자 | `ID`, `K_visit`, `Ref_dt` |
| 고혈압 | `b03_hypertension`, `b03_hypertension_age`, `b03_hypertension_age_no`, `b03_hypertension_take`, `b03_hypertension_take_age`, `b03_hypertension_take_age_no`, `b03_hypertension_take_rate` |
| 당뇨 | `b03_diabetes`, `b03_diabetes_age`, `b03_diabetes_age_no`, `b03_diabetes_take`, `b03_diabetes_take_age`, `b03_diabetes_take_age_no`, `b03_diabetes_take_kind`, `b03_diabetes_take_rate` |
| 관상동맥 | `b03_coronary`, `b03_coronary_age`, `b03_coronary_age_no`, `b03_coronary_take`, `b03_coronary_take_age`, `b03_coronary_take_age_no`, `b03_coronary_take_rate`, `b03_coronary_oper`, `b03_coronary_oper_age`, `b03_coronary_oper_age_no` |
| 고지혈증 | `b03_hyperlipidemia`, `b03_hyperlipidemia_age`, `b03_hyperlipidemia_age_no`, `b03_hyperlipidemia_take`, `b03_hyperlipidemia_take_age`, `b03_hyperlipidemia_take_age_no`, `b03_hyperlipidemia_take_rate` |
| 뇌혈관질환 | `b03_cere`, `b03_cere_age`, `b03_cere_age_no`, `b03_cere_take`, `b03_cere_take_age`, `b03_cere_take_age_no`, `b03_cere_take_rate` |
| TIA | `b03_tia`, `b03_tia_age`, `b03_tia_age_no`, `b03_tia_take`, `b03_tia_take_age`, `b03_tia_take_age_no`, `b03_tia_take_rate` |
| Composite | `b03_vascular` |

---

## 질환별 sub-field 패턴

각 질환은 다음 sub-field 패턴 (관상동맥 + 당뇨는 추가 컬럼 있음):

| sub-field | 의미 |
|-----------|------|
| `b03_<disease>` | 진단 여부 (0=없음, 1=있음, 9=알 수 없음) |
| `b03_<disease>_age` | 진단 받은 나이 (정수) |
| `b03_<disease>_age_no` | "나이 모름" 플래그. **stringified Python list** quirk — 아래 참조 |
| `b03_<disease>_take` | 약물 복용 여부 (0/1) |
| `b03_<disease>_take_age` | 약물 시작 나이 |
| `b03_<disease>_take_age_no` | "약물 시작 나이 모름" 플래그 |
| `b03_<disease>_take_rate` | 복용 빈도/규칙성 |

**관상동맥 추가**: `b03_coronary_oper`, `b03_coronary_oper_age`, `b03_coronary_oper_age_no` (수술 여부).

**당뇨 추가**: `b03_diabetes_take_kind` (약물 종류 — 인슐린/경구약 등 분류).

---

## 실측 분포

| 컬럼 | 분포 |
|------|------|
| `b03_hypertension` | 0:626 / 1:536 / NaN:33 |
| `b03_diabetes` | 0:958 / 1:204 / NaN:33 |
| `b03_coronary` | 0:1,103 / 1:58 / 9:1 / NaN:33 |
| `b03_hyperlipidemia` | 0:737 / 1:423 / 9:1 / NaN:34 |
| `b03_cere` | 0:1,157 / 1:4 / NaN:34 |
| `b03_tia` | 0:1,156 / 1:5 / NaN:34 |
| `b03_vascular` (composite) | 0:427 / 1:353 / 2:283 / 3:85 / 4:14 / NaN:33 |

→ KBASE 코호트는 ~45% 고혈압, ~17% 당뇨. 뇌혈관/TIA는 매우 드묾 (각 4~5명). composite `b03_vascular`는 **개별 질환 합계** (0~4 또는 5+) 추정.

---

## stringified Python list quirk

`*_age_no` (그리고 일부 다른 sub-field)에서 셀 값이 **Python list literal을 string으로 export**한 형태로 들어있음.

실측 sample (V0):

```
b03_hypertension_age_no: '[""]'
b03_diabetes_age_no:     '[""]'
b03_diabetes_take_age_no: '[""]'
b03_cere_take_age_no:    '["0"]'
```

해석:
- `'[""]'` — 빈 list (no 플래그 미체크)
- `'["0"]'` — `["0"]` list (no 플래그 = 0, 즉 "나이 알고 있음" 또는 의미상 "응답함")

원본 DB는 multiselect/array 필드인데 export 단계에서 JSON-string으로 직렬화된 것으로 추정.

### 파싱 권장

```python
import ast
import pandas as pd

def parse_no_field(cell):
    """Parse stringified list cells like '[""]' or '["0"]' into int or NaN."""
    if pd.isna(cell) or cell in ('', '[""]'):
        return float('nan')
    try:
        parsed = ast.literal_eval(str(cell))
        if isinstance(parsed, list) and parsed:
            v = parsed[0]
            if v in ('', None):
                return float('nan')
            try:
                return int(v)
            except (ValueError, TypeError):
                return float('nan')
        return float('nan')
    except (ValueError, SyntaxError):
        return float('nan')

vrf = pd.read_excel('/Volumes/nfs_storage/KBASE/ORIG/Demo/5_VascularRF.xlsx', sheet_name='Clinical2_B03_VRF')
no_cols = [c for c in vrf.columns if c.endswith('_no')]
for c in no_cols:
    vrf[c] = vrf[c].apply(parse_no_field)
```

---

## `Ref_dt` (Reference date)

| 컬럼 | 타입 | 의미 |
|------|------|------|
| `Ref_dt` | datetime/str | VRF 평가 기준일. baseline 추정 anchor |

실측 범위: 2014-01-21 ~ 2020-02-03. 코호트 등록 + 추적 평가 기간과 일치.

→ master에서 `Ref_dt` 컬럼은 `b03_*` 그룹의 첫 컬럼 (`Ref_dt`)로 들어옴. xlsx에서 datetime, csv export 시 string `'2015-09-10'` 형식.

---

## `memo` 시트

3행 × 4컬럼의 partial codebook:

```
Key |     |     | B03_VRF_심뇌혈관계 공존질환     ← row 1: 헤더
    |     |     | 고혈압 여부                  ← row 2: 첫 변수 한국어 라벨
ID  | K_visit | Ref_dt | b03_hypertension       ← row 3: 영어 변수명
```

→ 매우 간략. 전체 50 컬럼의 한국어 라벨 매핑은 없음. 컬럼명 자체가 self-describing 이라서 codebook 필요성 낮음.

---

## 분석 진입점 권장

```python
import pandas as pd
import ast

vrf = pd.read_excel('/Volumes/nfs_storage/KBASE/ORIG/Demo/5_VascularRF.xlsx', sheet_name='Clinical2_B03_VRF')

# stringified list 파싱
def parse_no_field(cell):
    if pd.isna(cell) or cell in ('', '[""]'): return float('nan')
    try:
        parsed = ast.literal_eval(str(cell))
        return int(parsed[0]) if isinstance(parsed, list) and parsed and parsed[0] not in ('', None) else float('nan')
    except (ValueError, SyntaxError):
        return float('nan')

for c in [c for c in vrf.columns if c.endswith('_no')]:
    vrf[c] = vrf[c].apply(parse_no_field)

# baseline subject별 VRF (V0)
vrf_baseline = vrf[vrf['K_visit'] == 0]

# composite score 분포
vrf_baseline['b03_vascular'].value_counts()
```

---

## 알려진 limitations

1. **stringified list quirk** (`'[""]'`, `'["0"]'`) — `*_age_no`/`*_take_age_no` 컬럼 전반. 정수 변환 전 파싱 필수.
2. **결측 33~34건** — V0에 평가 안 된 subject. 다른 visit (V2/V4)에 측정됐을 수 있음 — ID-단위 forward/backward fill 고려.
3. **`b03_vascular` composite 정의 미문서** — 0~4 분포로 보아 개별 질환 합계 (hypertension + diabetes + coronary + hyperlipidemia 등 일부 합)으로 추정. 정확한 공식은 KBASE 운영팀 확인.
4. **`9` (모름) 코드** — `b03_coronary` 1건, `b03_hyperlipidemia` 1건. 분석 시 NaN으로 처리할지 별도 카테고리로 둘지 결정.
5. **약물 정보 (`*_take`, `*_take_age`, `*_take_rate`) 신뢰도** — 자가 보고 기반. 약물 처방 기록과 cross-check 권장 (NFS에는 없음).
6. **흡연/음주 컬럼 부재** — 표준 vascular RF 평가에 포함되는 흡연/음주 정보가 이 파일에 없음. 별도 CRF 양식이거나 Sheet1 codebook 안에 다른 prefix로 있을 수 있음 (확인 필요).
