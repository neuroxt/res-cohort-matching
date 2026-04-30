# 진단 + Demographics — `2_Diag_Demo.xlsx`

`/Volumes/nfs_storage/KBASE/ORIG/Demo/2_Diag_Demo.xlsx` (179 KB).

KBASE 임상 데이터의 **중심 파일**. simplified 진단/CDR/age/sex/edu와 더불어 **CRF 전체 codebook (Sheet1)** 을 같이 담고 있다.

---

## 시트 3개

| 시트 | rows | cols | 내용 |
|------|------|------|------|
| `진단명, CDR, age sx edu` | 2,069 | 16 | **simplified 임상 데이터** — 분석 진입점 |
| `Sheet1` | 2 | 302 | **codebook** — 한국어 라벨 ↔ 영어 변수명 매핑 |
| `Sheet2` | 1 | 1 | **빈 시트** (max_row=1, max_col=1) |

> 디렉토리에 같이 있는 `2_Diag_Demo_sheet3_dx_coding.png`는 **별도 시트가 아님**. Sheet1(codebook)의 `y2_diag`/`y2_desc` 셀을 캡처한 이미지로 추정. xlsx의 실제 Sheet2는 비어있음.

---

## simplified 시트 (`진단명, CDR, age sx edu`) — 16 컬럼

| 순서 | 컬럼 | 타입 | 분포 / 의미 |
|------|------|------|------------|
| 1 | `ID` | str | `SU####` 1,850 + `BR####` 219, 630 unique |
| 2 | `K_visit` | int | 0:627 / 1:497 / 2:426 / 3:377 / 4:142 |
| 3 | `a1_sx` | int | **0:1,209 / 1:860** — codebook은 한국어 라벨 `성별`만 명시, 값 인코딩 (M/F) 미명시. 추정 **0=Male, 1=Female** (한국 임상 컨벤션) |
| 4 | `a1_age` | int | 21~93, 평균 70.8 (visit 시점 나이) |
| 5 | `a1_edu` | int | 0~25년, 평균 11.2 |
| 6 | `c9_memory` | float | CDR 박스 (memory) 0/0.5/1/2/3 |
| 7 | `c9_orientation` | float | CDR 박스 (orientation) |
| 8 | `c9_judgment` | float | CDR 박스 (judgment & problem solving) |
| 9 | `c9_social` | float | CDR 박스 (community affairs) |
| 10 | `c9_family` | float | CDR 박스 (home & hobbies) |
| 11 | `c9_personal` | float | CDR 박스 (personal care) |
| 12 | `c9_cdr` | float | **global CDR**. 0:1,173 / 0.5:581 / 1:254 / 2:54 / 3:7 |
| 13 | `c9_sb_total` | float | sum of boxes (0~21) |
| 14 | `y2_diag` | int | 1차 진단 5 코드. → [`codebook_dx.md`](codebook_dx.md) |
| 15 | `y2_desc` | float | 상세 진단 19 코드. → [`codebook_dx.md`](codebook_dx.md) |
| 16 | `y2_desc_details` | str | 자유 텍스트 (대부분 비어 있음) |

---

## Sheet1 codebook — CRF 전체 변수 사전 (302 컬럼)

`Sheet1`은 **데이터가 아니라 사전**. 행 2개:

- **row 1**: 한국어 라벨 (`모집경로`, `성별`, `연령`, `교육연수`, `결혼상태`, ...)
- **row 2**: 대응 영어 변수명 (`a0_ref_source`, `a1_sx`, `a1_age`, `a1_eud` (sic, 'edu' 오타), `a1_marriage`, ...)

302 컬럼 = KBASE CRF의 전체 raw 변수 set. simplified 시트와 master에는 그중 일부 노출. 노출 안 된 변수가 필요하면 KBASE 운영팀에 raw CRF 파일 요청.

### 영역별 변수 그룹 (영어 prefix 기준)

| Prefix | 영역 | 대표 변수 |
|--------|-----|----------|
| `a0_*` | 모집 정보 | `a0_ref_source`, `a0_ref_source_desc` |
| `a1_*` | 인적 사항 + 직업 | `a1_name`, `a1_sx`, `a1_age`, `a1_edu`, `a1_marriage`, `a1_career_*` |
| `b1_*` | 정신·뇌질환·전신질환 (제외 기준) | `b1_mental_illness`, `b1_cere`, `b1_serious_treat`, `b1_mri_contra`, `b1_pre_trial` |
| `c1_*` | 주관적 기억 호소 (SMC) | `c1_memory_current`, `c1_memory_10year`, `c1_memory_friend` (총 13문항) |
| `c1a_*` | 인지기능 감퇴 양상 | `c1a_cognitive_decline`, `c1a_cognitive_decline_start_year`, ... |
| `c2_*` | 노인우울척도 (GDS-30) | 30문항 (`c2_depression_satisfy`, `c2_depression_look`, ..., `c2_depression_mind`) + 총점 `c2_depression_scale` |
| `c3_*` | Faculty 평가 | 7 도메인 (memory, language, character, orientation, ADL, job, judgment) × 2~5 문항 + memo |
| `c4_*` | 인지 증상 양상 | `c4_memory`, `c4_daily`, `c4_appearance`, `c4_progress`, `c4_dementia` |
| `c5_*` | NIMH dAD / DSM-IV 우울 항목 | 11 문항 × 3 (NIMH dAD, daily, DSM-IV) |
| `c6_*` | 일상생활동작 (BDS-ADL) | `c6_homework`, `c6_calculation`, `c6_memory`, `c6_diraction`, `c6_road`, `c6_situation`, `c6_remember`, `c6_past_action`, `c6_eat_habit`, `c6_clothes_habit`, `c6_bathroom_habit` + 원인 코드 + `c6_total` |
| `c7_*` | SBT-K (Short Blessed Test) | year/month/time/number/day/name+addr 오류 카운트 + `c7_total` |
| `c8_*` | 신경학적 검사 | walk, dyskinetic, parkinsonism, hearing, brain, speech, motor, reflex |
| `c9_*` | CDR 6 박스 + 총점 | 위에 simplified 시트 참조 |
| `c10_*` | GDS (Global Deterioration Scale) | `c10_gds` |
| `y1_*` | 차수/사유 | `y1_reason` |
| `y2_*` | 진단 | 위 |

### codebook 일부 영어 변수명 sample (row 2)

```
a0_ref_source / a0_ref_source_desc / a1_name / a1_sx / a1_age / a1_birth_record / a1_birth_date / a1_eud / a1_literacy /
a1_marriage / a1_marriage_etc / a1_resident / a1_resident_etc / a1_resident_num / a1_cg / a1_cg_attend / a1_cg_name / a1_cg_relation /
a1_career / a1_career_title / a1_career_period / a1_career_ksco / a1_career_level / a1_retire / a1_retire_year / a1_retire_age /
a1_career_current / a1_career_title_current / a1_career_period_current / a1_career_ksco_current / a1_career_level_current / a1_career_period_total /
... (이하 b1, c1~c10, y1, y2 prefix)
```

### codebook 일부 한국어 라벨 sample (row 1)

```
모집경로 | 모집경로_기술 | 영문명 | 성별 | 연령 | 주민등록상생일 | 실제생일 | 교육연수 | 문맹상태 |
결혼상태 | 결혼상태_기타기술 | 동거상태 | ... | 정보제공자 유무 | 방문시동반가능여부 | 이니셜 |
... (302 cols)
```

> **Sheet1 변수명 quirk**: `a1_eud` (`a1_edu` 오타), `c4_appearance_etc`, `c4_progress_etc` 등 — 실제 simplified/master 시트의 변수명과 정확히 일치하지 않을 수 있음. simplified 시트에선 `a1_edu`로 정상 표기. cross-reference 시 양쪽 다 검색.

---

## GROUP vs y2_diag mismatch

KBASE의 가장 큰 quirk. `GROUP`은 imaging-time 임상 그룹 라벨, `y2_diag`는 formal CRF 진단 코드. **두 필드는 1:1 대응 아님**.

master 1,292 행 기준 cross-tabulation (GROUP × y2_diag):

| GROUP | y2_diag=1 | y2_diag=2 | y2_diag=3 | y2_diag=4 | y2_diag=9 | NaN |
|-------|-----------|-----------|-----------|-----------|-----------|-----|
| `AD` | 0 | 0 | 0 | 151 | 4 | 23 |
| `MCI` | 0 | 1 | 205 | **38** | 36 | 49 |
| `NC_고령` | 0 | 568 | **8** | 0 | 18 | 81 |
| `NC_청장년` | 97 | 2 | 0 | 0 | 0 | 3 |
| `CIND` | 0 | 0 | 0 | 0 | 0 | 1 |
| `PRD` | 0 | 0 | 0 | 0 | 0 | 2 |
| `QD` | 0 | 0 | 0 | 0 | 0 | 1 |
| `QD_naMCI` | 0 | 0 | 0 | 0 | 0 | 1 |
| `_고령` (typo) | 0 | 1 | 0 | 0 | 0 | 0 |
| `고령` (typo) | 0 | 1 | 0 | 0 | 0 | 0 |
| NaN | 0 | 1 | 0 | 0 | 0 | 0 |

**불일치 사례**:
- `MCI` GROUP인데 `y2_diag=4` (probable AD): 38건
- `MCI` GROUP인데 `y2_diag=2` (elderly NC): 1건
- `NC_고령` GROUP인데 `y2_diag=3` (MCI): 8건
- 다수 그룹의 `y2_diag=NaN`: total 184건

### 해석 가설 (검증 필요)

1. **시점 차이**: `GROUP`이 imaging visit 시점 임상 분류고, `y2_diag`는 별도 시점(예: baseline 또는 마지막 진단 결정)의 formal CRF 진단일 수 있음.
2. **converter case**: MCI → AD 진행 또는 NC → MCI 진행 케이스. visit 진행하며 진단 변경.
3. **정의 차이**: `GROUP=MCI`는 amnestic + non-amnestic 모두 포함, `y2_diag=3`은 amnestic만 (`y2_desc=30/31`). non-amnestic은 `y2_diag=9`로 분류됨 (codebook 참조). 하지만 이 정의로도 38건 MCI×AD 불일치는 설명 안 됨.
4. **NaN 184건**: V0/V2 baseline에서 진단 미결정 또는 데이터 입력 미완료.

→ **분석 시 어느 필드가 ground truth인지 명시 필수**. CRF formal 진단은 `y2_diag`/`y2_desc` 우선.

---

## 알려진 limitations

1. **a1_sx 값 인코딩 codebook 미명시** — 0/1의 M/F 매핑이 어디에도 명시 안 됨. KBASE 운영팀 확인 권장. 현재 추정 (한국 임상 컨벤션 + 분포 0:1209, 1:860) → 0=Male, 1=Female.
2. **`a1_edu` 0년**: 분포에 `0`이 포함됨 — 무학 (illiterate) 표기. `a1_literacy` 컬럼 (Sheet1 codebook의 `문맹상태`) 별도 존재해 cross-check 가능하지만 simplified/master에는 노출 안 됨.
3. **`a1_age` 21**: 청장년 정상인 (`y2_diag=1`) 중에 21세부터 등록. 일반적인 노화 코호트와 다른 점.
4. **GROUP typo** (`_고령`, `고령`, `''`) — V2/master에 3건. clean-up 권장.
5. **Sheet1 codebook은 변수 사전일 뿐 값 인코딩은 별도** — 일부 변수만 inline 값 매핑 포함 (`y2_diag`, `y2_desc`, `c4_appearance`, `c5_*`, `c6_*_cause` 일부). 나머지 변수의 값 의미는 KBASE 운영팀에 확인.
6. **Sheet2 빈 시트 처리** — 자동 파싱 시 `max_row=1, max_col=1` 시트는 skip 권장.
7. **CDR 분포 편향**: 정상(0) 1,173건 vs 치매(2/3) 61건. 표본 imbalance 큼.

---

## 분석 진입점 권장 코드

```python
import pandas as pd

# Simplified 임상 데이터
df = pd.read_excel(
    '/Volumes/nfs_storage/KBASE/ORIG/Demo/2_Diag_Demo.xlsx',
    sheet_name='진단명, CDR, age sx edu',
)

# GROUP typo clean-up (master 사용 시 동일하게 적용)
df['GROUP'] = df['GROUP'].replace({'_고령': 'NC_고령', '고령': 'NC_고령'})

# 진단 라벨 매핑 (codebook_dx.md 참조)
Y2_DIAG_LABEL = {1: 'NC_young', 2: 'NC_elderly', 3: 'MCI', 4: 'AD_probable', 9: 'Other'}
df['dx_label'] = df['y2_diag'].map(Y2_DIAG_LABEL)
```
