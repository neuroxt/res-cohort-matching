# OASIS3 NACC UDS 폼 컬럼 참조

OASIS3에 포함된 17개 NACC UDS 폼의 컬럼 그룹별 요약 + 핵심 컬럼 정의. 폼 단위로 1섹션 = 1폼.

> **공통 prefix 4 컬럼** (모든 UDS 폼에 동일하게 존재):
> - `OASISID` — 피험자 ID (`OAS3xxxx`)
> - `OASIS_session_label` — 세션 라벨 (form-specific 토큰. [`OASIS3_session_label_reference.md`](OASIS3_session_label_reference.md))
> - `days_to_visit` — 첫 방문 기준 경과일 (정수, 음수 가능 5건)
> - `age at visit` — 해당 visit 시점 나이 (소수점 둘째자리)
>
> 본 문서의 컬럼 표는 위 4개를 제외한 form-specific 컬럼만 다룬다.

> **NACC 공통 코딩 규칙**:
> - `0 = No`, `1 = Yes`, `9 = Unknown`
> - `8 = N/A` (해당 없음 — 예: 남성에게 출산 관련 질문)
> - `88 / 888 / 999 / 9999` = NACC missing-code (자릿수에 맞춰 사용)
> - 정확한 코딩 표는 [NACC UDS-3 RDD](https://files.alz.washington.edu/documentation/uds3-rdd.pdf) 참조 (1,000+ 변수의 완전한 정의)

---

## A1 — 참가자 인구통계 (visit-level)

`OASIS3_UDSa1_participant_demo.csv` · 8,500행 × 14컬럼 · session token: `UDSa1`

방문마다 **변동 가능**한 인구통계 정보 (cross-sectional `OASIS3_demographics.csv`와 보완 관계).

### 컬럼 정의 (10 form-specific)

| 컬럼 | 설명 | 코딩 |
|------|------|------|
| REASON | 방문 사유 | 1=Initial, 2=Follow-up, 3=Telephone, ... |
| REFER | 의뢰 경로 | 1=Self/Family, 2=Clinic referral, 4=ADC solicitation, ... |
| LEARNED | 연구 인지 경로 | 의뢰자 친구·가족·미디어 등 |
| PRESTAT | 등록 상태 | |
| PRESPART | 참가 상태 | |
| LIVSIT | 거주 상황 (간단) | 1=Lives alone, 2=Lives with someone |
| LIVSITUA | 거주 상황 (상세) | NACC 다단계 코드 |
| INDEPEND | 독립성 등급 | 1=Independent, ..., 4=Dependent |
| RESIDENC | 주거 type | 1=Own home, 2=Senior, 3=Nursing home, ... |
| MARISTAT | 결혼 상태 | 1=Married, 2=Widowed, 3=Divorced, 4=Separated, 5=Never married, 6=Living as married |

> **활용 팁**: `nursing home 입소 시점`을 추적하려면 `RESIDENC` 변화 detect.

---

## A2 — Co-participant (정보제공자) 인구통계

`OASIS3_UDSa2_cs_demo.csv` · 8,500행 × 17컬럼 · session token: `UDSa2`

CDR/NPI 등 정보제공자 기반 평가의 신뢰성을 위해 정보제공자 자체 인구통계를 수집.

### 컬럼 그룹

| 그룹 | 컬럼 | 설명 |
|------|------|------|
| 정보제공자 인구통계 | INSEX, INHISP, INHISPOR, INRACE, INRASEC, INRATER, INEDUC | 성별, Hispanic 여부, 인종 (3중 표기 race+secondary+tertiary) |
| 관계 | INRELTO | 관계 코드 (1=Spouse, 2=Adult child, 3=Other relative, 4=Friend/neighbor, ...) |
| 접촉 | INLIVWTH (동거 여부 0/1), INVISITS (방문 빈도), INCALLS (전화 빈도) | 정보 접근성 |
| 신뢰도 | INRELY (신뢰할 만한가? 0/1), NEWINF (이번 방문 새 정보제공자 여부) | |

> 한 subject의 정보제공자가 longitudinal로 바뀔 수 있다 (배우자 → 자녀). `NEWINF=1`인 시점부터는 history 보고가 일관되지 않을 수 있음.

---

## A3 — Subject family history (가족력) — Optional

`OASIS3_UDSa3.csv` · **4,090행** × **398컬럼** · session token: `USDa3` (UDS 오타)

**가장 컬럼 수가 많은 폼**. 가족 구성원별 dementia history를 매트릭스 형태로 수집. Optional module이므로 일부 visit에만 존재.

### 컬럼 그룹 (398 → 그룹별 정리)

#### 변경 추적 (5 컬럼)

| 컬럼 | 설명 |
|------|------|
| A3CHG | A3 변경 여부 (0=No change, 1=Updated) |
| PARCHG | Parent 정보 변경 |
| SIBCHG | Sibling 정보 변경 |
| KIDCHG | Children 정보 변경 |
| RELCHG | Other relative 정보 변경 |

#### 가족 식별자

| 컬럼 | 설명 |
|------|------|
| FAMILYID | NACC family ID (cross-subject family linkage) |
| TWIN | 쌍둥이 여부 (0/1/9) |
| TWINTYPE | 일란성/이란성 (1=Identical, 2=Fraternal, 9=Unknown) |
| SIBS | 형제자매 수 |
| KIDS | 자녀 수 |

#### 가족 구성원별 매트릭스

각 구성원에 대해 **표준 8-9 fields** 패턴이 반복된다:

| Field 접미사 | 설명 |
|--------------|------|
| `*ID` | 가족 구성원 ID (NACC internal) |
| `*YOB` | Year of Birth (de-identified, 4자리) |
| `*LIV` | Living status (0=Deceased, 1=Living, 9=Unknown) |
| `*YOD` | Year of Death (사망 시) |
| `*DEM` | Dementia 여부 (0/1/9) |
| `*ONSET` 또는 `*ONS` | Dementia 발병 연령 |
| `*AUTO` | 부검 여부 (0/1/9) |
| `*SEX` | 성별 (sibling/kids만) |

#### 구성원 그룹

| Prefix | 구성원 | 슬롯 수 |
|--------|--------|---------|
| `GMOM` | 외할머니 | 1 |
| `GDAD` | 외할아버지 | 1 |
| `MOM` | 어머니 | 1 |
| `DAD` | 아버지 | 1 |
| `SIB1`-`SIB20` | 형제자매 (최대 20명) | **20 슬롯** × 8 = 160 cols |
| `KID1`-`KID*` | 자녀 (가변 슬롯) | ~10-15 슬롯 |
| `REL1`-`REL15` | 기타 친족 (15 슬롯, 5 fields each) | 75 cols |
| `RELSDEM` | 친족 중 치매 사례 수 요약 | |

> **친조부모(paternal grandparents)는 별도 컬럼이 없다** — UDS v3 폼이 외조부모만 추적. 친조부모 정보는 부모(`DAD*`)의 가족력으로 추적할 수 있지만 별도 데이터로는 부재.
>
> 친조부모 컬럼을 따로 만든 NACC v3.1+ 폼이 있지만 OASIS3 데이터에는 미포함.

### 활용 예: dementia 가족력 binary flag

```python
import pandas as pd
a3 = pd.read_csv("OASIS3_UDSa3.csv")

# 1차 친족(부모/형제자매) 중 dementia 양성이 있는가?
parent_dem = (a3[['MOMDEM', 'DADDEM']] == 1).any(axis=1)
sib_cols = [f'SIB{i}DEM' for i in range(1, 21)]
sib_dem = (a3[sib_cols] == 1).any(axis=1)

a3['family_history_dementia'] = (parent_dem | sib_dem).astype(int)
```

---

## A4 — 약물 (Drug Code + Drug Name 페어)

UDS v3에서 폼 a4가 **D(코드)** + **G(이름)** 둘로 분할됨. 두 파일은 같은 인덱스 위치에 같은 약물의 코드와 이름을 담음 → 1:1 매칭 가능.

### A4-D — 약물 코드

`OASIS3_UDSa4D_med_codes.csv` · 7,617행 × 51컬럼 · session token: `UDSa4`

| 컬럼 | 설명 |
|------|------|
| anymeds | 어떤 약이라도 복용 중인가 (0=No, 1=Yes) |
| drug1 ~ drug46 | NACC 약물 코드 (integer, 최대 46개 슬롯) |

### A4-G — 약물명

`OASIS3_UDSa4G_med_names.csv` · 7,617행 × 51컬럼 · session token: `UDSa4` (D와 동일 토큰)

| 컬럼 | 설명 |
|------|------|
| anymeds | 동일 |
| meds_1 ~ meds_46 | 약물명 free text (예: `LISINOPR`, `ASA`, `CALCIUM`, `MVI`, `INNER BA`) |

> **주의**: 두 파일은 session label로 구별 불가 (둘 다 `UDSa4`). 분석 시 파일별로 따로 읽고 KEY로 join.

---

## A5 — 건강력

`OASIS3_UDSa5_health_history.csv` · 8,500행 × 72컬럼 · session token: `UDSa5`

### 컬럼 그룹

| 그룹 | 컬럼 (대표) | 설명 |
|------|------------|------|
| 심혈관 | CVHATT, CVAFIB, CVANGIO, CVBYPASS, CVPACE, CVCHF, CVOTHR, CVANGINA, CVHVALVE, CVPACDEF, HATTMULT | 심근경색, 심방세동, 혈관조영, 우회로, 페이스메이커, 울혈성심부전 등 |
| 뇌혈관 | CBSTROKE, STROKMUL, CBTIA, TIAMULT, CBOTHR | 뇌졸중 (다회 여부), TIA |
| 신경 | PD, PDOTHR, SEIZURES, TBI, TBIBRIEF, TBIEXTEN, TBIWOLOS, TRAUMBRF, TRAUMEXT, TRAUMCHR, NCOTHR | 파킨슨병, 발작, TBI (brief/extensive/with or without LOC) |
| 대사·내분비 | HYPERTEN, HYPERCHO, DIABETES, DIABTYPE, B12DEF, THYROID | 고혈압, 고지혈증, 당뇨 (type), B12 결핍, 갑상선 |
| 비뇨·기능 | INCONTU (urinary), INCONTF (fecal) | 요실금, 변실금 |
| 정신 | DEP2YRS, DEPOTHR, ALCOHOL, ALCFREQ, ALCOCCAS, ABUSOTHR, PSYCDIS, PTSD, BIPOLAR, SCHIZ, ANXIETY, OCD, NPSYDEV | 우울 (2년 내), 알코올 빈도/사용, 약물 남용, 양극성, 조현병, 불안, OCD, 발달장애 |
| 흡연 | TOBAC30 (30일 내 흡연), TOBAC100 (100개 평생), SMOKYRS, PACKSPER, QUITSMOK | 흡연 history |
| 근골격 | ARTHRIT, ARTHTYPE, ARTHUPEX, ARTHLOEX, ARTHSPIN, ARTHUNK | 관절염 종류 + 부위 |
| 수면 | APNEA, RBD (REM behavior disorder), INSOMN, OTHSLEEP | 수면무호흡, RBD, 불면증 |
| 요약 플래그 | stroke_tia, hbp, seiz, headinj | 카테고리 통합 binary flag (legacy) |

### 핵심 컬럼

```python
# 임상 위험 요인 4종 baseline
risks = a5[['HYPERTEN', 'DIABETES', 'CBSTROKE', 'PD']]
# 각 컬럼: 0=No, 1=Recent/Active, 2=Remote/Inactive, 3=Both, 9=Unknown
```

---

## B1 — 신체검사

`OASIS3_UDSb1_physical_eval.csv` · 8,627행 × 15컬럼 · session token: `UDSb1`

| 컬럼 | 설명 | 단위/코딩 |
|------|------|-----------|
| WEIGHT | 체중 | lb (999=missing) |
| HEIGHT | 신장 | inch (999=missing) |
| BPSYS | 수축기 혈압 | mmHg |
| BPDIAS | 이완기 혈압 | mmHg |
| HRATE | 맥박 | bpm |
| VISION | 시각 결손 | 0=Normal, 1=Impaired (corrected w/ glasses) |
| VISCORR | 시각 교정 사용 | 0/1 |
| VISWCORR | 시각 교정 후 결손 여부 | |
| HEARING | 청각 결손 | 0/1 |
| HEARAID | 보청기 사용 | 0/1 |
| HEARWAID | 보청기 사용 후 결손 | |

### BMI 계산 예

```python
import pandas as pd
b1 = pd.read_csv("OASIS3_UDSb1_physical_eval.csv")
b1.replace(999, pd.NA, inplace=True)
# lb → kg, inch → m
b1['BMI'] = (b1['WEIGHT'] * 0.4536) / (b1['HEIGHT'] * 0.0254) ** 2
```

---

## B2 — Hachinski Ischemic Score (HIS)

`OASIS3_UDSb2_his_cvd.csv` · 8,500행 × 20컬럼 · session token: `UDSb2`

혈관성 치매 vs 알츠하이머 감별 진단 척도 (Hachinski 1975).

| 컬럼 그룹 | 컬럼 | 비고 |
|-----------|------|------|
| HIS 항목 | ABRUPT (급성 발병), STEPWISE (단계적 악화), SOMATIC, EMOT, HXHYPER, HXSTROKE, FOCLSYM, FOCLSIGN | 0=No, 1=Yes, 각 항목 가중치 1-2점 |
| HIS 총점 | HACHIN | ≥4 = 혈관성 치매 시사 |
| 임상의 판정 | CVDCOG (혈관 → 인지 contributory 여부) | |
| 영상 소견 | CVDIMAG, CVDIMAG1, CVDIMAG2, CVDIMAG3, CVDIMAG4 | 영상 카테고리 (cortical infarct, lacune, WMH 등) |
| 추가 | STROKCOG | 뇌졸중 → 인지 contributory 여부 |

---

## B3 — UPDRS — Optional (PD module)

`OASIS3_UDSb3.csv` · **4,090행** × 32컬럼 · session token: `USDb3` (UDS 오타)

Unified Parkinson's Disease Rating Scale Motor section. PD 의심 시에만 시행.

### 컬럼 그룹

| 그룹 | 컬럼 |
|------|------|
| 일반 | PDNORMAL (전체 정상), SPEECH, FACEXP (얼굴 표정) |
| 휴식 떨림 | TRESTFAC (얼굴), TRESTRHD/LHD (오/왼손), TRESTRFT/LFT (오/왼발) |
| 자세 떨림 | TRACTRHD/LHD |
| 경직 | RIGDNECK, RIGDUPRT/UPLF (상지 오/왼), RIGDLORT/LOLF (하지 오/왼) |
| 운동완서 | TAPSRT/LF (손가락 두드리기), HANDMOVR/L (손 회전), HANDALTR/L (alternating) |
| 다리 운동 | LEGRT, LEGLF |
| 자세 / 보행 | ARISING, POSTURE, GAIT, POSSTAB (postural stability) |
| 운동완서 종합 | BRADYKIN (전체적 운동완서) |

각 항목: 0 (정상) ~ 4 (severe).

> **분석 시 주의**: UDS v2와 v3에서 일부 항목 코딩 변경 가능. 시점별 visit type 확인 필수.

---

## B4 — CDR + MMSE + 1차 진단

`OASIS3_UDSb4_cdr.csv` · **8,627행** × 23컬럼 · session token: `UDSb4`

OASIS3에서 가장 핵심적인 임상 폼. CDR + MMSE + 임상의 1차 진단(`dx1-dx5`)을 묶어서 제공.

### 컬럼

| 그룹 | 컬럼 | 값/범위 |
|------|------|---------|
| 인지 점수 | MMSE | 0-30 (Mini-Mental State Exam, 30점 만점) |
| CDR 도메인 (6) | memory, orient, judgment, commun, homehobb, perscare | 0 / 0.5 / 1 / 2 / 3 (각 도메인 등급) |
| CDR 합산 | CDRSUM | 6 도메인 합산 (0-18) |
| CDR Global | CDRTOT | 0 / 0.5 / 1 / 2 / 3 (Hughes 1982 알고리즘) |
| 진단 코드 | dx1_code, dx2_code, dx3_code, dx4_code, dx5_code | NACC integer 코드 |
| 진단 라벨 (free text) | dx1, dx2, dx3, dx4, dx5 | 예: `Cognitively normal`, `AD Dementia`, `MCI`, ... |

### dx1 분포 (실측 — 8,627행 기준 상위)

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

### CDR 활용

```python
# CDR severity로 그룹 분류
cdr_group = (b4['CDRTOT']
             .map({0.0: 'CN', 0.5: 'Very mild', 1.0: 'Mild',
                   2.0: 'Moderate', 3.0: 'Severe'}))
```

> **D1 폼과의 관계**: dx1은 임상의 1차 판정. **D1 폼은 더 상세한 etiology breakdown** (PROBAD, POSSAD, MCI 변종 등)을 제공. 일관된 분석을 위해서는 D1 폼이 권장.

---

## B5 — NPI-Q (Neuropsychiatric Inventory Questionnaire)

`OASIS3_UDSb5_npiq.csv` · 8,500행 × 29컬럼 · session token: `UDSb5`

12 도메인 행동/정신 증상 × {존재(0/1), 심각도(1/2/3)}. 정보제공자 보고 기반.

### 컬럼

| 도메인 | 존재 | 심각도 | 설명 |
|--------|------|--------|------|
| 망상 | DEL | DELSEV | 망상 |
| 환각 | HALL | HALLSEV | |
| 흥분 | AGIT | AGITSEV | Agitation |
| 우울 | DEPD | DEPDSEV | |
| 불안 | ANX | ANXSEV | |
| 환희 | ELAT | ELATSEV | Elation/Euphoria |
| 무관심 | APA | APASEV | Apathy |
| 탈억제 | DISN | DISNSEV | Disinhibition |
| 과민 | IRR | IRRSEV | Irritability |
| 운동행동 | MOT | MOTSEV | Motor behaviors (배회 등) |
| 야간행동 | NITE | NITESEV | |
| 식욕 | APP | APPSEV | Appetite changes |
| 정보제공자 | NPIQINF | — | 정보제공자 코드 (1=Spouse, 2=Adult child, ...) |

존재(0/1) 컬럼이 0이면 심각도 컬럼은 missing. 1이면 1(mild)/2(moderate)/3(severe).

### NPI-Q total score 계산

```python
domains = ['DEL', 'HALL', 'AGIT', 'DEPD', 'ANX', 'ELAT',
           'APA', 'DISN', 'IRR', 'MOT', 'NITE', 'APP']
sevs = [d + 'SEV' for d in domains]
# 존재하는 도메인의 심각도만 합산
b5['NPIQ_total'] = b5[sevs].fillna(0).sum(axis=1)  # 0-36
```

---

## B6 — GDS-15 (Geriatric Depression Scale, 15-item)

`OASIS3_UDSb6_gds.csv` · 8,500행 × 21컬럼 · session token: `UDSb6`

자가보고 우울 척도. 15개 yes/no 문항 + 시행 여부 flag + 총점.

### 컬럼

| 컬럼 | 의미 (요지) | 채점 방향 |
|------|-------------|-----------|
| NOGDS | GDS 시행 여부 (0=Done, 1=Not done) | — |
| SATIS | "Are you basically satisfied with your life?" | No=1점 |
| DROPACT | "Have you dropped many of your activities and interests?" | Yes=1점 |
| EMPTY | "Do you feel that your life is empty?" | Yes=1점 |
| BORED | "Do you often get bored?" | Yes=1점 |
| SPIRITS | "Are you in good spirits most of the time?" | No=1점 |
| AFRAID | "Are you afraid that something bad is going to happen to you?" | Yes=1점 |
| HAPPY | "Do you feel happy most of the time?" | No=1점 |
| HELPLESS | "Do you often feel helpless?" | Yes=1점 |
| STAYHOME | "Do you prefer to stay at home, rather than going out?" | Yes=1점 |
| MEMPROB | "Do you feel you have more problems with memory than most?" | Yes=1점 |
| WONDRFUL | "Do you think it is wonderful to be alive?" | No=1점 |
| WRTHLESS | "Do you feel pretty worthless the way you are now?" | Yes=1점 |
| ENERGY | "Do you feel full of energy?" | No=1점 |
| HOPELESS | "Do you feel that your situation is hopeless?" | Yes=1점 |
| BETTER | "Do you think most people are better off than you are?" | Yes=1점 |
| GDS | 총점 (0-15) | ≥5 = 우울 가능, ≥10 = 중증 |

---

## B7 — FAQ (Functional Activities Questionnaire)

`OASIS3_UDSb7_faq_fas.csv` · 8,500행 × 14컬럼 · session token: `UDSb7`

10개 IADL 항목. 정보제공자 평가.

### 컬럼

각 항목: 0 = Normal / 1 = Has difficulty but does by self / 2 = Requires assistance / 3 = Dependent / 8 = Never did, would have difficulty / 9 = N/A or unknown.

| 컬럼 | 활동 |
|------|------|
| BILLS | Writing checks, paying bills, balancing checkbook |
| TAXES | Assembling tax records, business affairs, papers |
| SHOPPING | Shopping alone for clothes, household necessities, groceries |
| GAMES | Playing a game of skill (chess, bridge), working on a hobby |
| STOVE | Heating water, making coffee, turning off stove |
| MEALPREP | Preparing balanced meals |
| EVENTS | Keeping track of current events |
| PAYATTN | Paying attention to and understanding TV/book/magazine |
| REMDATES | Remembering appointments, family occasions, holidays, medications |
| TRAVEL | Traveling out of neighborhood (driving, public transport) |

### FAQ total score

```python
faq_items = ['BILLS', 'TAXES', 'SHOPPING', 'GAMES', 'STOVE',
             'MEALPREP', 'EVENTS', 'PAYATTN', 'REMDATES', 'TRAVEL']
# 8/9 → 0 처리 (NACC 표준 권장)
b7_clean = b7[faq_items].replace({8: 0, 9: pd.NA})
b7['FAQ_total'] = b7_clean.sum(axis=1)  # 0-30
```

---

## B8 — 신경학적 검사

`OASIS3_UDSb8_neuro_exam.csv` · 8,500행 × 50컬럼 · session token: `UDSb8`

50 컬럼 — 임상의가 시행한 신경학적 검사 결과.

### 컬럼 그룹

| 그룹 | 컬럼 |
|------|------|
| 전반 | NORMAL (전체 정상), NORMEXAM, FOCLDEF (국소 결손), GAITDIS (보행 이상), EYEMOVE (안구 운동 이상) |
| 파킨슨 | PARKSIGN, RESTTRL/R (휴식 떨림), SLOWINGL/R (운동 완서), RIGIDL/R (경직), BRADY (운동완서), PARKGAIT (파킨슨 보행), POSTINST (postural instability) |
| 혈관 | CVDSIGNS, CVDMOTL/R, CORTVISL/R (피질 시각), SOMATL/R |
| 피질 | CORTDEF, SIVDFIND, POSTCORT |
| PSP/CBS | PSPCBS, EYEPSP, DYSPSP, AXIALPSP, GAITPSP |
| 실행증 | APRAXSP, APRAXL/R |
| 감각 | CORTSENL/R |
| 소뇌·실조 | ATAXL/R |
| 외계인손 | ALIENLML/R |
| 이상운동 | DYSTONL/R, MYOCLLT/RT (myoclonus) |
| ALS | ALSFIND |
| NPH | GAITNPH (정상압 수두증 보행) |
| 기타 | OTHNEUR |

각 항목: 0 = Absent / 1 = Present / 9 = Unknown.

### Parkinsonism flag 통합 예

```python
park_signs = ['RESTTRL', 'RESTTRR', 'SLOWINGL', 'SLOWINGR',
              'RIGIDL', 'RIGIDR', 'BRADY', 'PARKGAIT', 'POSTINST']
b8['parkinsonism_present'] = (b8[park_signs] == 1).any(axis=1).astype(int)
```

---

## B9 — Clinician 판정 증상/임상양상

`OASIS3_UDSb9_symptoms.csv` · 8,500행 × 58컬럼 · session token: `UDSb9`

임상의가 정보제공자/환자 보고 + 검사 결과를 종합해 인지·행동·운동 변화를 정리.

### 컬럼 그룹

| 그룹 | 컬럼 (대표) | 설명 |
|------|------------|------|
| 변화 인식 | DECSUB (자가 인식), DECIN (정보제공자 인식), DECCLIN (임상의 판정), DECCLCOG (인지 변화), DECCLBE (행동 변화), DECCLMOT (운동 변화) | |
| 인지 도메인 변화 | COGMEM (기억), COGJUDG (판단), COGORI (지남력), COGLANG (언어), COGVIS (시공간), COGATTN (주의), COGFLUC (변동성), COGFLAGO (변동 시작 시기), COGOTHR | |
| 인지 변화 시작 | COGFRST (어떤 도메인 첫 변화), COGFPRED (predominant), COGMODE (서서히/급성/단계적) | |
| 행동 변화 | BEAPATHY, BEDEP, BEVHALL (visual hall), BEAHALL (auditory hall), BEDEL, BEDISIN, BEIRRIT, BEAGIT, BEPERCH, BEREM (RBD), BEANX, BEOTHR | |
| 행동 시작 | BEFRST, BEFPRED, BEAGE, BEMODE | |
| 운동 변화 | MOGAIT (보행), MOFALLS (낙상), MOTREM (떨림), MOSLOW (운동완서), MOFRST, MOMODE, MOMOPARK (파킨슨 양상 운동), PARKAGE, MOMOALS (ALS 양상), ALSAGE, MOAGE | |
| 종합 | COURSE (gradual/stepwise/static/improving), FRSTCHG (전체 첫 변화 도메인) | |
| 평가 의뢰 | LBDEVAL (LBD 평가 의뢰됨), FTLDEVAL (FTLD 평가 의뢰됨) | |

> **분석 시**: B9는 D1 폼의 임상 진단을 보완. PROBAD 판정의 근거를 더 추적할 때 유용.

---

## C1 — Neuropsychological battery (UDS v2 + v3 union)

`OASIS3_UDSc1_cognitive_assessments.csv` · 7,925행 × **107컬럼** · session token: **`psychometrics`** (UDS 다른 폼과 다른 토큰)

UDS v2 → v3 전환에서 검사 일부가 변경되어 **두 버전의 컬럼이 union**으로 들어 있음. v2-only와 v3-only가 혼재.

### 컬럼 그룹 (107 cols)

#### UDS v2 (legacy, 일부 v3에서 제거됨)

| 검사 | v2 컬럼 |
|------|---------|
| Boston Naming (30-item) | bnt |
| WMS-R Logical Memory | LOGIMEM (immediate), MEMUNITS (delayed), LOGI* |
| Digit Span (WMS-R) | digfor (forward), digback (backward), DIGIF (forward subset), DIGIB (backward subset) |
| Digit Symbol | digsym |
| Trail Making A | tma, TRAILA |
| Trail Making B | tmb |
| Category Fluency | ANIMALS, VEG, mentcont |
| Selective Reminding Test | srtfree, srttotal |
| Other v2 검사 | PSY019, PSY021, PSY003, SIM, simon, simonnumber, switchCV, switchmixed, switch, lettnum (Letter-Number Sequencing), inform, logmem, pairs, block, lmdelay, line, slosson, asscmem, place_r, numsym |

#### UDS v3 추가 검사

| 검사 | v3 컬럼 |
|------|---------|
| Craft Story (대체용) | craftvrs (immediate verbatim), crafturs (immediate units), craftdvr (delayed verbatim), craftdre (delayed units), craftdti (delayed time), craftcue (cued recall) |
| Multilingual Naming Test (MINT) | minttots (total spontaneous), minttotw (with semantic cue), mintscng/mintscnc (semantic cues given/correct), mintpcng/mintpcnc (phonemic cues given/correct) |
| Number Span | digforct/sl, digbacct/ls (count and longest span) |
| Trail Making B (v3) | trailb |
| Benson Complex Figure | udsbentc (copy), udsbentd (delayed), udsbenrs (recognition score) |
| Verbal Fluency (UDS v3) | udsverfc (F + L correct), udsverfn (F + L errors), udsvernf, udsverlc/lr/ln/tn/te/ti |
| Trigram | trigram |
| Spatial recall | spatial |
| Selective Reminding (v3) | srt1f/c, srt2f/c, srt3f/c (3 trials, free/cued) |

#### MoCA (Montreal Cognitive Assessment) — UDS v3.1 추가

```
mocacomp, mocareas (시행/미시행 reasons), mocaloc, mocalan, mocalanx,
mocavis, mocahear, mocatots (총점),
mocatrai (Trail B), mocacube (cube), mocacloc/clon/cloh (clock contour/numbers/hands),
mocanami (naming), mocaregi (registration), mocadigi (digit span), mocalett (letter A),
mocaser7 (serial 7), mocarepe (sentence repetition), mocaflue (verbal fluency),
mocaabst (abstraction), mocarecn/recc/recr (delayed recall: no cue/category cue/recognition),
mocaordt/ormo/oryr/ordy/orpl/orct (orientation: date/month/year/day/place/city)
```

### 분석 권장 사항

```python
import pandas as pd
c1 = pd.read_csv("OASIS3_UDSc1_cognitive_assessments.csv")

# v2 vs v3 visit 구분 — MoCA가 NaN이면 v2 시점, 아니면 v3
c1['uds_version'] = c1['mocatots'].notna().map({True: 'v3', False: 'v2'})

# v2/v3 공통 검사로 longitudinal trajectory 만들기
# Trail B: tmb (v2) vs trailb (v3) 또는 mocatrai (MoCA)
c1['trail_b'] = c1['trailb'].fillna(c1['tmb'])
```

> v2 → v3 전환 시점에서 같은 subject가 두 버전 모두 거쳤을 수 있음. trajectory 분석 시 검사 매핑 주의.

---

## D1 — Clinician diagnosis

`OASIS3_UDSd1_diagnoses.csv` · 8,500행 × **149컬럼** · session token: `UDSd1`

OASIS3에서 **가장 풍부한 진단 정보**를 담는 폼. 임상 진단 + etiology breakdown + (v3) syndrome flags + biomarker contributory flags.

### 컬럼 그룹 (149 cols)

#### 평가자 / 일반 (3)

| 컬럼 | 설명 |
|------|------|
| WHODIDDX | 진단 평가자 (1=Single clinician, 2=Consensus) |
| dxmethod | UDS v3 추가 — 진단 방법 |
| hiv | HIV 감염 여부 |

#### Top-level 인지 상태 (3)

| 컬럼 | 설명 |
|------|------|
| NORMCOG | Cognitively normal (0/1) |
| DEMENTED | Demented (0/1) |
| IMPNOMCI | Impaired but not MCI (0/1) |

> 위 3개는 **mutually exclusive** (같은 visit에 1개만 1).

#### MCI 변종 (7) — UDS v2/v3

| 컬럼 | 설명 |
|------|------|
| MCIAMEM | Amnestic MCI, single domain (memory only) |
| MCIAPLUS | Amnestic MCI, multi-domain |
| MCIAPLAN | Amnestic+ Language affected |
| MCIAPATT | Amnestic+ Attention affected |
| MCIAPEX | Amnestic+ Executive affected |
| MCIAPVIS | Amnestic+ Visuospatial affected |
| MCINON1 | Non-amnestic MCI, single domain |
| MCIN1LAN/ATT/EX/VIS | Non-amnestic single, which domain |
| MCINON2 | Non-amnestic MCI, multi-domain |
| MCIN2LAN/ATT/EX/VIS | Non-amnestic multi, which domains |

#### Etiology pairs (각 etiology + `*IF` "imaging contributory")

| Etiology | 진단 flag | Imaging contributory flag |
|----------|-----------|--------------------------|
| Probable AD | PROBAD | PROBADIF |
| Possible AD | POSSAD | POSSADIF |
| DLB (Lewy body) | DLB | DLBIF |
| Vascular dementia | VASC | VASCIF |
| Vascular cognitive impairment (subcortical) | VASCPS | VASCPSIF |
| Alcohol-related dementia | ALCDEM | ALCDEMIF |
| Dementia, undetermined | DEMUN | DEMUNIF |
| FTD (frontotemporal) | FTD | FTDIF |
| Primary progressive aphasia | PPAPH | PPAPHIF |
| PPA non-fluent | PNAPH | — |
| Semantic dementia | SEMDEMAN, SEMDEMAG | — |
| PPA, other variant | PPAOTHR | — |
| PSP (progressive supranuclear palsy) | PSP | PSPIF |
| CBS (corticobasal syndrome) | CORT | CORTIF |
| Huntington | HUNT | HUNTIF |
| Prion disease | PRION | PRIONIF |
| Medication-related cognitive impairment | MEDS | MEDSIF |
| Systemic illness-related | DYSILL | DYSILLIF |
| Depression-related | DEP | DEPIF |
| Other psychiatric | OTHPSY | OTHPSYIF |
| Down syndrome | DOWNS | DOWNSIF |
| Parkinson disease | PARK | — |
| Stroke | STROKE | STROKIF |
| Hydrocephalus | HYCEPH | HYCEPHIF |
| Brain injury | BRNINJ | BRNINJIF |
| Neoplasm | NEOP | NEOPIF |
| Cognitive impairment, other 1/2/3 | COGOTH/COGOTHIF, COGOTH2/COGOTH2F, COGOTH3/COGOTH3F | |

#### UDS v3 syndrome flags (v3 visit에서만 채워짐)

| 컬럼 | 설명 |
|------|------|
| amndem | Amnestic syndrome (clinical phenotype) |
| pca | Posterior cortical atrophy syndrome |
| ppasyn | PPA syndrome present |
| ppasynt | PPA subtype (1=nonfluent, 2=semantic, 3=logopenic) |
| ftdsyn | FTD behavioral syndrome |
| lbdsyn | LBD syndrome (parkinsonism + RBD + visual hall + cog fluc) |
| namndem | Non-amnestic dementia |

#### UDS v3 biomarker contributory flags

| 컬럼 | 설명 |
|------|------|
| amylpet | Amyloid PET positive (contributory to dx) |
| amylcsf | CSF amyloid positive (contributory) |
| fdgad | FDG PET shows AD pattern (contributory) |
| hippatr | Hippocampal atrophy on MRI (contributory) |
| taupetad | Tau PET positive AD pattern (contributory) |
| csftau | CSF tau elevated (contributory) |
| fdgftld | FDG PET shows FTLD pattern |
| tpetftld | Tau PET shows FTLD pattern |
| mrftld | MRI shows FTLD pattern (frontal/temporal atrophy) |
| datscan | DaT scan abnormal (Parkinson) |
| othbiom | Other biomarker |

#### 영상 소견 (vascular)

| 컬럼 | 설명 |
|------|------|
| imaglinf | Imaging shows large infarct |
| imaglac | Imaging shows lacune |
| imagmach | Imaging shows macrohemorrhage |
| imagmich | Imaging shows microhemorrhage |
| imagmwmh | Imaging shows moderate WMH |
| imagewmh | Imaging shows extensive WMH |

#### 기타 (v3)

| 컬럼 | 설명 |
|------|------|
| admut | AD-related mutation (PSEN1, PSEN2, APP) |
| ftldmut | FTLD-related mutation (MAPT, GRN, C9ORF72) |
| othmut | Other mutation |
| alzdis, alzdisif | Alzheimer disease (combined flag) |
| lbdis, lbdif | Lewy body disease (combined flag) |
| msa, msaif | MSA (multiple system atrophy) |
| ftldmo, ftldmoif | FTLD with motor disorder (FTD-MND) |
| ftldnos, ftldnoif | FTLD NOS |
| ftldsubt | FTLD subtype |
| cvd, cvdif | Cerebrovascular disease (combined) |
| prevstk | Previous stroke contributory |
| strokdec | Stroke decline contributory |
| stkimag | Stroke imaging confirmed |
| infnetw | Network infarction |
| infwmh | Infarct + WMH |
| esstrem, esstreif | Essential tremor |
| brnincte | Brain infarct, chronic |
| epilep, epilepif | Epilepsy |
| neopstat | Neoplasm status |
| hivif | HIV contributory |
| othcog, othcogif | Other cognitive |
| deptreat | Depression treatment status |
| bipoldx, bipoldif | Bipolar |
| schizop, schizoif | Schizophrenia |
| anxiet, anxietif | Anxiety |
| delir, delirif | Delirium |
| ptsddx, ptsddxif | PTSD |
| alcabuse | Alcohol abuse |
| impsub, impsubif | Impairment due to substance |

### 분석 활용 예

#### Subject별 final diagnosis 추출

```python
import pandas as pd
d1 = pd.read_csv("OASIS3_UDSd1_diagnoses.csv")

# 가장 최근 visit (가장 큰 days_to_visit)
final_dx = (d1.sort_values('days_to_visit')
              .drop_duplicates('OASISID', keep='last'))

# 진단 카테고리 정리
def classify(row):
    if row['NORMCOG'] == 1: return 'CN'
    if row['DEMENTED'] == 1:
        if row['PROBAD'] == 1: return 'AD'
        if row['DLB'] == 1: return 'DLB'
        if row['VASC'] == 1: return 'VaD'
        if row['FTD'] == 1: return 'FTD'
        return 'Other dementia'
    if any(row[c] == 1 for c in ['MCIAMEM', 'MCIAPLUS']): return 'aMCI'
    if any(row[c] == 1 for c in ['MCINON1', 'MCINON2']): return 'naMCI'
    if row['IMPNOMCI'] == 1: return 'IMPNOMCI'
    return 'Unknown'

final_dx['dx_group'] = final_dx.apply(classify, axis=1)
```

> **D1과 B4 dx1의 관계**: B4 `dx1`은 free text 1차 진단. D1은 binary flag로 더 정밀한 etiology 분류. 일관된 그룹 분류는 D1 사용 권장.

---

## D2 — Clinician 판정 의학 상태

`OASIS3_UDSd2_med_conditions.csv` · 8,500행 × 32컬럼 · session token: `UDSd2`

A5(self-reported health history)와 비슷하지만 **임상의가 활성/비활성 여부를 판정**.

### 컬럼

| 컬럼 | 설명 | 코딩 |
|------|------|------|
| cancer | 암 | 0=No, 1=Active/Recent, 2=Remote/Inactive |
| diabet | 당뇨 | |
| myoinf | 심근경색 | |
| conghrt | 울혈성심부전 | |
| afibrill | 심방세동 | |
| hypert | 고혈압 | |
| angina | 협심증 | |
| hypchol | 고지혈증 | |
| vb12def | 비타민 B12 결핍 | |
| thydis | 갑상선 질환 | |
| arth, artype, artupex, artloex, artspin, artunkn | 관절염 + 부위 | |
| urineinc, bowlinc | 요/변실금 | |
| sleepap | 수면 무호흡 | |
| remdis | RBD | |
| hyposom | 과수면 | |
| sleepoth | 기타 수면 장애 | |
| angiocp | 혈관성형술 (CABG) | |
| angiopci | 혈관성형술 (PCI) | |
| pacemake | 페이스메이커 | |
| hvalve | 심장판막 시술 | |
| antienc | 자가면역 뇌염 (autoimmune encephalitis) | |
| othcond | 기타 | |

> A5 vs D2: A5는 환자/정보제공자 보고. D2는 임상의 판정. 불일치 시 D2가 더 신뢰할 만.

---

## NACC RDD 외부 참조

각 폼의 정확한 코딩값과 history는 NACC Researcher's Data Dictionary 참조:

- **공식 RDD-UDS-3 PDF**: [https://files.alz.washington.edu/documentation/uds3-rdd.pdf](https://files.alz.washington.edu/documentation/uds3-rdd.pdf)
- **NACC Forms documentation**: [https://naccdata.org/data-collection/forms-documentation/uds-3](https://naccdata.org/data-collection/forms-documentation/uds-3)
- **UDS v3 Forms 공식 페이지** (form-by-form PDF): [https://www.alz.washington.edu/WEB/forms_uds.html](https://www.alz.washington.edu/WEB/forms_uds.html)
- **UDS v3 발표 논문**: Weintraub S, et al. *Version 3 of the National Alzheimer's Coordinating Center's Uniform Data Set*. Alzheimer Dis Assoc Disord 2018;32(1):10-17.

---

## 분석 시 일반 권장 사항

### 1. NACC missing-code 처리

```python
import pandas as pd
import numpy as np

# 모든 UDS 폼 공통: 88, 99, 888, 999, 9999는 NACC missing
NACC_MISSING = [88, 99, 888, 999, 9999]
df = df.replace(NACC_MISSING, np.nan)
```

### 2. UDS 버전 시점 확인

```python
# c1 폼: MoCA 컬럼이 있으면 v3, 없으면 v2
# d1 폼: amndem 등 syndrome flag가 있으면 v3
```

### 3. Form-form join 시 outer join

A3, B3는 optional이라 일부 visit 누락 → outer join으로 모든 visit 보존.

### 4. dx1 free text vs D1 binary flag

진단 그룹 분류는 **D1 binary flag** 사용 (free text dx1은 NACC 표준 카테고리에 매핑되지 않음).

---

## 참고 문서

| 문서 | 내용 |
|------|------|
| [`OASIS3_data_catalog.md`](OASIS3_data_catalog.md) | 24 CSV 마스터 인벤토리 |
| [`OASIS3_session_label_reference.md`](OASIS3_session_label_reference.md) | 세션 라벨 grammar (`UDSx{N}`, `USDa3`, `psychometrics` 토큰) |
| [`OASIS3_protocol.md`](OASIS3_protocol.md) | UDS v2/v3 전환, 코호트 구조 |
| [`OASIS3_join_relationships.md`](OASIS3_join_relationships.md) | Form-form join, A4 D/G 페어링 |
