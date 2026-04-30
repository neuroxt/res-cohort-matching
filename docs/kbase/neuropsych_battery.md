# 신경심리검사 — `4_NP.xlsx`

`/Volumes/nfs_storage/KBASE/ORIG/Demo/4_NP.xlsx` (920 KB) — KBASE에서 가장 큰 임상 파일.

KBASE의 신경심리 평가는 **KBASE_NP1 + NP2 두 배터리를 통합**. NP1은 표준 코어 검사들, NP2는 추가 검사 set. 두 배터리 결과가 한 시트에 합쳐져 있고, raw + Z-score 모두 제공.

---

## 시트 구성

| 시트 | rows | cols | 내용 |
|------|------|------|------|
| `NP` | 2,069 | 72 | raw subtests + Z-scores |
| `NP memo` | 61 | 54 | hierarchical 한국어 codebook (검사명 ↔ 측정 항목) |

→ 행 수 2,069 = K_visit 0/1/2/3/4 모든 visit 포함 (Diag_Demo와 동일).

---

## NP1 vs NP2 구분

`NP memo` 시트의 row 1 텍스트:
- `KBASE_NP1에 속해있는 검사 목록` (col 1~24)
- `KBASE_NP2에 속해있는 검사 목록` (col 25~52)
- `왼쪽 변수들에 대한 Z 스코어` (col 53~)

→ 컬럼 위치로 NP1 / NP2 구분. 단 `NP` 시트의 헤더는 검사명만 있고 NP1/NP2 라벨은 없으므로, 각 컬럼이 어느 배터리에 속하는지는 `NP memo` 시트로 cross-reference.

> **핵심 quirk**: NP1 검사가 NP2 배터리에는 없을 수 있고 그 반대도 마찬가지. 한 subject가 NP1 또는 NP2 중 한쪽만 받으면 다른 쪽 검사는 NaN. 분석 시 isnull 패턴으로 어느 배터리를 받았는지 추론 가능.

---

## 72 컬럼 그룹 (NP 시트)

### 1. 식별자 (2)

| 컬럼 | 의미 |
|------|------|
| `ID` | Subject ID |
| `K_visit` | Visit (0/1/2/3/4) |

### 2. 언어 유창성 — J1 (5 컬럼)

**검사**: 동물범주 1분간 말하기. 0-15초/16-30초/31-45초/46-60초로 나눠 응답수 카운트.

| 컬럼 | 측정 |
|------|------|
| `J1_15s` | 0–15초 응답 수 |
| `J1_30s` | 16–30초 응답 수 |
| `J1_45s` | 31–45초 응답 수 |
| `J1_60s` | 46–60초 응답 수 |
| `J1_Tot` | 전체 합계 (1분간 응답한 단어 수) |

### 3. Boston Naming — J2 (4 컬럼)

| 컬럼 | 측정 |
|------|------|
| `J2_high` | 고빈도 단어 |
| `J2_mid` | 중빈도 단어 |
| `J2_low` | 저빈도 단어 |
| `J2_Tot` | 전체 합 |

### 4. MMSE-KC — J3 (1 컬럼)

| 컬럼 | 측정 |
|------|------|
| `J3` | MMSE-KC 최종 총점 (0~30) |

### 5. 단어목록기억 (immediate) — J4 (4 컬럼)

| 컬럼 | 측정 |
|------|------|
| `J4_1st` | 시행 1 회상 단어 수 |
| `J4_2nd` | 시행 2 회상 단어 수 |
| `J4_3rd` | 시행 3 회상 단어 수 |
| `J4_Tot` | 시행 1~3 합 (전체 응답 단어 수) |

### 6. 구성행동(immediate) / 단어목록회상(delayed) / 재인 / 구성회상 — J5~J8 (5 컬럼)

| 컬럼 | 측정 |
|------|------|
| `J5` | 구성행동 immediate (총점) |
| `J6` | 단어목록회상 (delayed, 총점) |
| `J6_storage` | 저장률 (J6 / J4_3rd 등 비율 — `NP memo` 참조) |
| `J7` | 단어목록재인 (총점) |
| `J8` | 구성회상 (총점) |

### 7. Stroop Test — K1 (3 컬럼)

| 컬럼 | 측정 |
|------|------|
| `K1_W` | Word page (단어 페이지) |
| `K1_C` | Color page (색깔 페이지) |
| `K1_CW` | Color-Word page (색깔-단어 페이지) |

### 8. Clox — K3 (2 컬럼)

| 컬럼 | 측정 |
|------|------|
| `K3_1` | CLOX1 (시계 그리기, 자유) |
| `K3_2` | CLOX2 (시계 그리기, 보고 그리기) |

### 9. TMT (Trail Making) — L11 (2 컬럼)

| 컬럼 | 측정 |
|------|------|
| `TMT_A (L11)` | Trail A 소요 시간 (초) |
| `TMT_B (L11)` | Trail B 소요 시간 (초) |

> 컬럼명에 공백 + `(L11)` 포함. pandas access는 `df['TMT_A (L11)']` 형태로.

### 10. Digit Span — L12 (2 컬럼)

| 컬럼 | 측정 |
|------|------|
| `DS_forward (L12)` | Forward Total Score |
| `DS_backward (L12)` | Backward Total Score |

### 11. Total Score — TS (2 컬럼)

| 컬럼 | 측정 |
|------|------|
| `TS1` | Total score 1 (NP1 합산) |
| `TS2` | Total score 2 (NP2 합산) |

> `NP memo`엔 "Total score (이 부분만 NP2에 속한 점수가 아닙니다.)" — TS1은 NP1, TS2는 NP2 종합. 정확한 합산 공식은 `NP memo` 시트 또는 KBASE 운영팀 확인.

### 12. RCFT (Rey Complex Figure Test) — L1/L3/L8/L9 (4 컬럼)

| 컬럼 | 측정 |
|------|------|
| `L1_rcft_copy` | Copy (즉시 따라 그리기) |
| `L3_rcft_3min` | 3-minute Delay |
| `L8_rcft_30min` | 30-Minute Delay |
| `L9_rcft_recog` | Recognition |

### 13. COWAT (음소 유창성) — L2 (4 컬럼)

| 컬럼 | 측정 |
|------|------|
| `L2_1` | ㄱ으로 시작하는 단어 |
| `L2_2` | ㅇ으로 시작하는 단어 |
| `L2_3` | ㅅ으로 시작하는 단어 |
| `L2_Tot` | 총합 |

### 14. WMS-IV-K Logical Memory — L4 (immediate) / L10 (delayed) (7 컬럼)

| 컬럼 | 측정 |
|------|------|
| `L4_A` | Immediate Story A |
| `L4_B` | Immediate Story B |
| `L4_Tot` | Immediate Total |
| `L10_A` | Delay Story A |
| `L10_B` | Delay Story B |
| `L10_Tot` | Delayed Total |
| `L10_recog` | Recognition (A+B) |

### 15. WAIS-IV-K 토막짜기 — L5 (1 컬럼)

| 컬럼 | 측정 |
|------|------|
| `L5` | 토막짜기 총점 |

### 16. FAB (Frontal Assessment Battery) — L7 (5 컬럼)

| 컬럼 | 측정 |
|------|------|
| `L7_1` | 1. 유사성 |
| `L7_3` | 3. 연속 운동 동작 |
| `L7_4` | 4. 상충된 지시 |
| `L7_5` | 5. 진행–멈춤 |
| `L7_6` | 6. 잡기 행동 |

> 2번 항목 (`L7_2`)은 raw 컬럼에 없음 — `NP memo`도 해당 row 비어 있음. FAB 표준 6항목 중 2번 (어휘 유창성, lexical fluency)을 KBASE는 별도 측정 안 한 것으로 추정 (또는 NP1/NP2에 따라 다른 컬럼에 위치).

### 17. Anosognosia + KART — L13, KART (2 컬럼)

| 컬럼 | 측정 |
|------|------|
| `L13` | Anosognosia Rating Scale |
| `KART` | KART (Korean Adult Reading Test, premorbid IQ 추정) |

### 18. Z-scores (17 컬럼)

| 컬럼 | 대응 raw |
|------|---------|
| `J1_Z` | `J1_Tot` 표준화 |
| `J2_Z` | `J2_Tot` |
| `J3_Z` | `J3` (MMSE-KC) |
| `J4_Z` | `J4_Tot` |
| `J5_Z` | `J5` |
| `J6_Z` | `J6` |
| `J7_Z` | `J7` |
| `J8_Z` | `J8` |
| `K1_W_Z` | `K1_W` |
| `K1_C_Z` | `K1_C` |
| `K1_CW_Z` | `K1_CW` |
| `TMT_A_z` | `TMT_A (L11)` |
| `TMT_B_z` | `TMT_B (L11)` |
| `DS_f_z` | `DS_forward (L12)` |
| `DS_b_z` | `DS_backward (L12)` |
| `TS1_Z` | `TS1` |
| `TS2_Z` | `TS2` |

> Z 표기 일관성 quirk: `*_Z` (대문자)와 `*_z` (소문자) 혼재 — `TMT_A_z`/`TMT_B_z`/`DS_f_z`/`DS_b_z`만 소문자, 나머지는 대문자. **분석 코드에선 정확한 컬럼명 필수**.
>
> Z-score 산출 기준 (어떤 normative sample 사용했는지)은 `NP memo` 시트 또는 KBASE 운영팀 확인.

---

## `NP memo` 시트 구조

61 행 × 54 컬럼의 **hierarchical 한국어 codebook**:

- **row 1**: 검사 그룹 헤더 (e.g., `J1. 언어 유창성 검사_동물범주 (1분 간 실시)`, `J2. 보스톤 이름대기 검사`)
- **row 2**: subtest 또는 측정 카테고리 (e.g., `J1. 언어 유창성 검사_동물범주`, `J2. 보스톤 이름대기 검사`)
- **row 3**: 항목 설명 (e.g., `0–15초 동안 대답한 응답수`, `고빈도`)
- 그 외 row: 각 검사의 점수 분포, 한국어 매뉴얼 노트 등 (혼합)

> codebook은 데이터 자체가 아니라 *검사 명칭 사전*. NP 시트의 raw 컬럼 의미를 한국어로 풀어쓰는 용도.

---

## 분석 진입점 권장

```python
import pandas as pd

np_df = pd.read_excel('/Volumes/nfs_storage/KBASE/ORIG/Demo/4_NP.xlsx', sheet_name='NP')

# Z-score 컬럼만 select
z_cols = [c for c in np_df.columns if c.endswith('_Z') or c.endswith('_z')]

# 도메인 평균 (예시)
np_df['memory_z_mean'] = np_df[['J4_Z', 'J6_Z', 'J7_Z']].mean(axis=1)  # word list memory
np_df['executive_z_mean'] = np_df[['K1_CW_Z', 'TMT_B_z', 'DS_b_z']].mean(axis=1)  # executive
```

---

## 알려진 limitations

1. **NP1 vs NP2 가용성** — 한 subject가 두 배터리 모두 받지는 않을 수 있음. NP2 전용 검사(L4/L5/L7/L13/KART 등) NaN이면 NP1만 받은 것. 분석 전 isnull 패턴으로 확인.
2. **Z-score 산출 기준 미문서** — 어떤 normative sample 기준인지 NFS 데이터에서 추론 불가. KBASE 운영팀 확인 필요.
3. **`L7_2` 누락** — FAB 표준 6항목 중 2번이 컬럼에 없음.
4. **컬럼명 괄호 + 공백** — `TMT_A (L11)`, `DS_forward (L12)` 등 — pandas access 시 정확한 문자열 사용. SQL/feather 등 다른 포맷으로 export 시 컬럼명 sanitize 권장.
5. **Z 대소문자 혼재** — `*_Z` (대문자) vs `*_z` (소문자) — 일관 처리 필요. clean-up 시 `df.columns = [c.replace('_Z', '_z') for c in df.columns]` 등.
6. **K3 (Clox) 결측 비율 높을 수 있음** — V0 baseline NP1만 받은 subject에는 K3 없을 수 있음. spot-check 필요.
7. **검사 시행 양식 (NP1 vs NP2)이 visit별로 다를 수 있음** — 한 subject 내 V0=NP1, V2=NP2 가능. longitudinal 비교 시 같은 검사 set으로 align.
