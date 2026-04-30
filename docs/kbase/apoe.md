# APOE — `3_APOE.xlsx`

`/Volumes/nfs_storage/KBASE/ORIG/Demo/3_APOE.xlsx` (41 KB).

---

## 시트 구성

| 시트 | rows | cols | 내용 |
|------|------|------|------|
| `BLOOD` | 1,195 | 5 | APOE 유전형 (visit-level row, 정적 측정) |

---

## 5 컬럼

| 컬럼 | 타입 | 분포 / 의미 |
|------|------|------------|
| `ID` | str | 627 unique subjects |
| `K_visit` | int | 0:627 / 2:426 / 4:142 (V1/V3 측정 없음) |
| `항목` | str | 대부분 빈 값 (legacy 메모 컬럼) |
| `Apo E genotyping` | str | 슬래시 문자열 — 분포는 아래 |
| `ApoE4_positivity` | float | 0/1 binary, NaN 허용 |

---

## `Apo E genotyping` 분포 (실측)

| 값 | 행수 |
|----|------|
| `E3/3` | 377 |
| `E3/4` | 158 |
| `E2/3` | 52 |
| `E4/4` | 28 |
| `E2/4` | 9 |
| `E2/2` | 2 |
| NaN | 569 |

→ ε4 carrier (E3/4 + E4/4 + E2/4) = **195**. ε4 non-carrier = 431. NaN 569 (대부분 V2/V4 — 정적 측정이라 V0 한 번 측정 후 다른 visit 채혈 안 함).

`ApoE4_positivity`:

| 값 | 행수 | 매핑 |
|----|------|------|
| `0` | 431 | E2/2, E2/3, E3/3 (ε4 없음) |
| `1` | 195 | E2/4, E3/4, E4/4 (ε4 1+ allele) |
| NaN | 569 | genotyping 없음 |

→ `ApoE4_positivity`는 `Apo E genotyping`에서 derive 가능 (`'4' in genotype`). 두 컬럼은 일치 (자체 검증 됨).

---

## 정적 측정 처리 (subject-level forward-fill)

APOE는 평생 변하지 않는 정적 측정. visit-level 행으로 저장돼 있어도 분석 시 **subject-level 단일 값**으로 다뤄야 함.

```python
import pandas as pd
apoe = pd.read_excel('/Volumes/nfs_storage/KBASE/ORIG/Demo/3_APOE.xlsx', sheet_name='BLOOD')

# Subject-level static APOE (V0 우선, 없으면 V2/V4)
apoe_static = (
    apoe.dropna(subset=['Apo E genotyping'])
        .sort_values('K_visit')
        .drop_duplicates('ID', keep='first')
        [['ID', 'Apo E genotyping', 'ApoE4_positivity']]
)

# 다른 파일에 merge할 때
df_clinical = pd.read_excel('.../2_Diag_Demo.xlsx', sheet_name='진단명, CDR, age sx edu')
df = df_clinical.merge(apoe_static, on='ID', how='left')
# V1/V3 행도 APOE 채워짐
```

> master는 visit-level concat이므로 `Apo E genotyping` 컬럼이 V0/V2/V4 행에는 채워져 있고 (각 visit에 채혈했을 때) V0만 있고 V2/V4 NaN일 수 있음. master에서 사용하려면 위와 동일하게 forward-fill 권장.

---

## Cross-cohort APOE 인코딩 비교

cohort 간 pooling 시 가장 자주 마주치는 quirk. 4가지 다른 인코딩이 공존.

| 표준 | KBASE | ADNI | OASIS3 | A4 / LEARN |
|------|-------|------|--------|-----------|
| 컬럼명 | `Apo E genotyping`, `ApoE4_positivity` | `APOE4` (개수: 0/1/2), `APGEN1`+`APGEN2` (allele 1/2) | `APOE` (정수) | `APOEGN` (slash 소문자) |
| 인코딩 형식 | 슬래시 대문자 (`E3/3`, `E3/4`, ...) | allele 정수 쌍 (`APGEN1=3, APGEN2=4`) | 두자리 정수 (`33`, `34`, `22`, ...) | 슬래시 소문자 (`e3/e3`, `e3/e4`) |
| ε4 carrier 표기 | `ApoE4_positivity` (0/1) | `APOE4` (0/1/2 = ε4 allele 개수) | `APOE` 값에서 derive | `APOEGN` 값에서 derive 또는 `apoe4_pos` |
| 결측 표현 | NaN | `APOE4` NaN | `0`, `#N/A`, NaN | NaN |

### 통일 매핑 함수 (cross-cohort용)

```python
def normalize_apoe(genotype, source):
    """
    Returns (allele_pair: str, ε4_count: int) or (None, None) if missing.
    
    예시:
        normalize_apoe('E3/4', 'kbase')   -> ('e3/e4', 1)
        normalize_apoe(34, 'oasis3')      -> ('e3/e4', 1)
        normalize_apoe('e3/e4', 'a4')     -> ('e3/e4', 1)
    """
    if genotype is None or pd.isna(genotype):
        return (None, None)
    
    if source == 'kbase':
        # 'E3/4' -> 'e3/e4'
        s = str(genotype).strip().lower()  # 'e3/4'
        # KBASE는 'E3/4' 형식, 슬래시 뒤에 e prefix 없음
        parts = s.replace('e', '').split('/')
        if len(parts) == 2:
            a, b = sorted([int(parts[0]), int(parts[1])])  # 정렬해서 e2/e4 vs e4/e2 통일
            std = f'e{a}/e{b}'
            count = sum(1 for x in [a, b] if x == 4)
            return (std, count)
    
    if source == 'oasis3':
        # 34 -> 'e3/e4', 33 -> 'e3/e3'
        try:
            n = int(genotype)
            if n == 0: return (None, None)  # OASIS3 결측 코드
            a, b = sorted([n // 10, n % 10])
            return (f'e{a}/e{b}', sum(1 for x in [a, b] if x == 4))
        except (ValueError, TypeError):
            return (None, None)
    
    if source == 'a4':
        # 'e3/e4' or 'E3/E4' -> 'e3/e4'
        s = str(genotype).strip().lower().replace(' ', '')
        # 이미 슬래시 + e prefix
        return (s, s.count('4'))
    
    if source == 'adni':
        # ADNI는 APGEN1/APGEN2 두 컬럼이라 caller가 두 값을 합쳐 전달해야 함
        # genotype = (APGEN1, APGEN2) tuple
        if isinstance(genotype, tuple):
            a, b = sorted(genotype)
            return (f'e{a}/e{b}', sum(1 for x in [a, b] if x == 4))
    
    return (None, None)
```

→ 위 함수로 4 코호트 모두 `('e3/e4', 1)` 같은 표준 표현으로 변환 후 분석.

---

## 알려진 limitations

1. **569건 결측** — V1/V3 visit이거나 채혈 자체 안 함. ID-단위 forward-fill 후에도 채혈 안 한 subject (~17명)는 NaN.
2. **`항목` 컬럼은 대부분 빈 값** — legacy 메모 컬럼. 분석에선 무시.
3. **`Apo E genotyping`과 `ApoE4_positivity` 일치성 검증됨** — 둘 중 하나만 사용해도 ok. 단, 외부 컨센서스 매핑 (`positivity = 'E4' in genotype`)으로 재계산해서 sanity check 권장.
4. **APOE는 모든 visit에 동일 값이어야 함** — 만약 한 subject 내 visit별로 `Apo E genotyping`이 다르면 데이터 입력 오류 (KBASE 운영팀 보고).
