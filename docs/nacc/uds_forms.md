# NACC UDS 폼 overlay (NACC-specific)

NACC 임상 데이터는 **NACC UDS 표준** 그 자체이며, 17 UDS 폼 (A1–D2) 의 **컬럼 정의 / 코딩 / 분석 패턴** 은 [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) 에서 다룬다.

본 overlay 는 NACC 데이터 자체에만 존재하는 사실 — bookkeeping 컬럼 (NACCID, NACCADC, PACKET, FORMVER, NACCVNUM 등), UDS 버전 deltas (v1→v2→v3→v4), 폼-form 통합 운영 모델 (1936-col `investigator_ftldlbd_nacc71.csv`) — 을 정리한다.

---

## 1. NACC bookkeeping 컬럼 (모든 UDS 폼 공통)

NACC가 자체적으로 부여하는 visit-level 식별/메타 컬럼. UDS 폼 form-specific 컬럼 위에 붙는다.

| 컬럼 | 의미 | 예시 / 코딩 |
|------|------|---------|
| `NACCID` | NACC subject ID | `NACC` + 6 digits (예: `NACC252073`). `NACCADC` 와 합쳐 ADRC 연동 |
| `NACCADC` | ADRC 코드 | NIA-funded ADRC 식별 (예: `1=Wash U`, `2=Mayo Clinic`, ...). `NACCADC` 외부 표는 NACC-internal |
| `PACKET` | Visit packet 종류 | `I` (Initial), `F` (Follow-up), `T` (Telephone). 자세한 것은 [`session_label_reference.md`](session_label_reference.md) |
| `FORMVER` | Visit이 시행된 UDS 폼 버전 | `1`=v1, `2`=v2, `3`=v3, `4`=v4 |
| `NACCVNUM` | Subject 내부 visit sequence (1-based) | `1`, `2`, ..., `11` |
| `NACCAVST` | 누적 available visit count | |
| `NACCNVST` | Total visit count (누적 + 추정) | |
| `NACCDAYS` | First visit ↔ current visit 일수 | 정수 |
| `NACCFDYS` | First visit ↔ first IVP 일수 | 정수 |
| `NACCCORE` | Core visit 여부 | 0/1 |
| `NACCREAS` | 방문 사유 코드 | NACC 내부 코드 |
| `NACCREFR` | 의뢰 경로 | NACC 내부 코드 |
| `VISITMO` | Visit 시행 월 | 1–12 |
| `VISITDAY` | Visit 시행 일 | 1–31 |
| `VISITYR` | Visit 시행 년 | 4-digit |

> NACC 자체 파이프라인은 `(NACCID, NACCVNUM)` 단위 visit-level 분석을 기본으로 한다. PACKET 은 visit 종류 식별, FORMVER 는 폼 버전 식별, VISITMO/DAY/YR 은 절대 시간 (cross-subject 비교용).

---

## 2. UDS 버전 deltas

| UDS 버전 | 도입 | 본 NACC freeze 에서의 분포 (추정) | 주요 폼 변화 |
|----------|------|--------------------------------|-------------|
| v1 | 2005 | 일부 historical visit | 최초 도입. A1–C1 + D1 + D2. C1는 Boston Naming + Logical Memory + Trail A/B |
| v2 | 2008 | 일부 visit | A3 (가족력) 확장, B3 (UPDRS optional), 약물 폼 분리 (a4D + a4G), A5 항목 추가 |
| **v3** | 2015 | **다수 visit** (NACC 표준) | C1 cognitive battery 대폭 교체 (Boston Naming → MINT, Logical Memory → Craft Story), D1 syndrome flag 추가 (`amndem`, `pca`, `ppasyn`, `ftdsyn`, `lbdsyn`, `namndem`), biomarker contributory flag 추가 (`amylpet`, `amylcsf`, `fdgad`, `hippatr`, `taupetad`, `csftau`, `fdgftld`, `tpetftld`, `mrftld`, `datscan`) |
| v3.1 | 2017 | v3 visit 상당수 | MoCA 추가 (`mocacomp`, `mocatots`, `mocatrai`, ...) |
| **v4** | 2024 (rolling) | **부분 도입** (FORMVER=4 visit 일부) | 인지/기능 평가 일부 modernize. 자세한 deltas 는 NACC v4 RDD 도착 후 본 docs에 추가 예정 |

분석 시:

```python
# 폼 버전별 분포 확인
df['FORMVER'].value_counts()
# 보통 v3 (3) 이 가장 많고, v4 (4) 는 점진 증가
```

> **버전 mix 처리**: 같은 변수명도 버전별로 코딩이 변할 수 있다. 주요 변동 변수 (B4 `dx*`, C1 `mocatots` 등) 의 분포를 폼 버전별로 확인하고 분석 전에 맞춤 처리 권장. C1 cognitive battery v2 ↔ v3 매핑 패턴은 [`docs/_shared/nacc_uds_forms.md` C1 절](../_shared/nacc_uds_forms.md) 참조.

---

## 3. NACC 통합 운영 모델

NACC core 임상 데이터는 **단일 통합 wide-format 파일** 로 배포 (OASIS3가 폼별 별도 CSV 인 것과 다름):

| 파일 | 행 | 열 | 내용 |
|------|------|------|------|
| `Non_Commercial_Data/investigator_ftldlbd_nacc71.csv` | 205,909 | **1,936** | 모든 UDS 폼 (A1–D2) + FTLD3 + LBD3.1 + bookkeeping. 같은 row 에 한 visit 의 모든 폼 변수가 들어있다 |
| `Commercial_Data/commercial_ftldlbd_nacc71.csv` | 179,753 | 1,936 | 동일 스키마, commercial-tier subset |

따라서 NACC 분석은:
- **폼-form join 불필요**. 같은 visit 의 모든 변수가 한 행에 존재.
- **Visit 키**: `(NACCID, NACCVNUM)` (또는 `(NACCID, NACCVNUM, PACKET)`).
- **컬럼 prefix 로 폼 식별**: 컬럼명 자체가 NACC RDD 의 변수명 (예: `MEMORY`, `MOCATOTS`, `PROBAD`, `amylpet`).

---

## 4. NeuroXT-built `merged.csv` 와의 관계

`/Volumes/nfs_storage/NACC_NEW/ORIG/DEMO/merged.csv` 는 NeuroXT 가 NACC 표준 배포 위에 빌드한 working file:

- **Source**: `investigator_ftldlbd_nacc71.csv` (UDS 핵심) + `investigator_fcsf_nacc71.csv` (CSF) + `investigator_scan_pet/amyloidpetnpdka` (Amyloid PET) + `investigator_scan_pet/taupetnpdka` (Tau PET).
- **Visit 단위**: `(NACCID, NACCVNUM)`.
- **390 컬럼 사전**: [`merged_csv.md`](merged_csv.md).

> NACC 표준 분석 / reproducibility 추구 시에는 `investigator_*.csv` 시리즈를 직접 사용. NeuroXT 사내 통합 분석 (UDS + CSF + PET SUVR 즉시 사용) 시에는 `merged.csv` 를 사용.

---

## 5. NACC missing-code 처리 (NACC freeze 한정)

```python
import pandas as pd
import numpy as np

# UDS 변수의 width 별 missing 코드
NACC_MISSING_INTEGER = [88, 99, 888, 999, 9999]
NACC_NA_TEXT = ['.', 'NA', 'unknown']

df = pd.read_csv("investigator_ftldlbd_nacc71.csv")

# integer/numeric: width-aware 변환
df = df.replace(NACC_MISSING_INTEGER, np.nan)

# text: dx1 등 free-text 컬럼
text_cols = df.select_dtypes(include='object').columns
df[text_cols] = df[text_cols].replace(NACC_NA_TEXT, np.nan)
```

> 자세한 width-별 표는 [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) 도입부.

---

## 6. 폼-별 NACC freeze 분포 (사실 검증 필요)

NACC freeze 에서 각 UDS 폼이 채워진 visit 비율은 폼별로 다르다 (optional 모듈 + missing 비율 + 버전 도입 시점). 본 docs 작성 시점에는 정확한 분포 미집계 — 분석 시 직접 `FORMVER` × form-specific 컬럼 non-null 카운트로 확인 권장:

```python
# 예: A3 가족력 폼 채움률
a3_filled = df['SIBS'].notna().sum()    # FAMILYID, MOMDEM 등 채움 비율 cross-check
total = len(df)
print(f"A3 filled: {a3_filled}/{total} = {a3_filled/total*100:.1f}%")
```

---

## Known limitations & quirks

1. **단일 통합 파일이 1,936 cols.** 파이프라인이 무거우면 `usecols=` 로 필요한 컬럼만 부분 로드 권장 (UDS 핵심 변수 ≈ 200 cols, FTLD3 + LBD3.1 + bookkeeping 합 ≈ 1,700+).
2. **FORMVER=4 visit 의 v4-specific 컬럼은 v3 컬럼 set 에 없다.** v4 deltas 는 NACC v4 RDD 도착 후 별도 docs 갱신.
3. **`NACCADC` 외부 표는 미배포.** ADRC 식별이 익명화돼 있어 site-level 분석 시 `NACCADC` 정수만 사용 가능 (어느 ADRC인지 알 수 없음). NACC DUA 제출 시 별도 요청으로 ADRC 매핑 받을 수 있음.
4. **v71 freeze 에 NP (Neuropathology) 컬럼 일부가 통합되었을 수 있음.** `investigator_ftldlbd_nacc71.csv` 의 1,936 cols 에 NP 변수 존재 여부 — column scan 으로 검증 권장.
5. **dx1 free text vs D1 binary flag.** B4 폼의 `dx1` 자유 텍스트는 NACC 표준 카테고리에 1:1 mapping 되지 않음. 일관된 그룹 분류는 D1 binary flag 사용.
6. **Telephone packet (PACKET=T) 은 인지검사 일부만.** B1 (신체검사), B8 (신경학적 검사) 등 대면 필요 폼이 결측.

> 검증일 2026-05-01 (freeze v71)
