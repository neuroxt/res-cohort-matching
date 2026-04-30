# A4/LEARN VISCODE 전체 매핑

VISCODE(정수) ↔ SESSION_CODE(3자리 문자열) ↔ 방문명 ↔ 방문단계 완전 참조.

**소스**: `DEMO/Clinical/Documents/Data Dictionaries/visits_datadic.csv` (152행)

> **SESSION_CODE 규칙**: VISCODE를 3자리 zero-pad (`6` → `006`).
> 3자리 초과 VISCODE(701~999)는 그대로 유지 (`997` → `997`).

---

## A4 방문 코드 (125개)

### Screening (VISCODE 1–5)

| VISCODE | SESSION_CODE | 방문명 | 속성 | VISITGROUP |
|---------|-------------|--------|------|-----------|
| 1 | 001 | Visit 1 (Screening) | sc1 | Screening |
| 2 | 002 | Visit 2 (Screening PET) | sc2 | Screening |
| 3 | 003 | Visit 3 (Screening Disclosure) | sc3 | Screening |
| 4 | 004 | Visit 4 (Screening MRI) | sc4 | Screening |
| 5 | 005 | Visit 5 (Screening LP) | sc5 | Screening |

### Blinded Treatment (VISCODE 6–66)

| VISCODE | SESSION_CODE | 방문명 | 속성 | 주차 |
|---------|-------------|--------|------|------|
| 6 | 006 | Visit 6 (Baseline) | bl6 | Baseline |
| 7 | 007 | Visit 7 (wk4 Infusion) | infusion | wk4 |
| 8 | 008 | Visit 8 (wk8 Infusion) | infusion | wk8 |
| 9 | 009 | Visit 9 (wk12 Clinic) | w12 | wk12 |
| 10 | 010 | Visit 10 (wk16 Infusion) | infusion | wk16 |
| 11 | 011 | Visit 11 (wk20 Infusion) | infusion | wk20 |
| 12 | 012 | Visit 12 (wk24 Clinic) | w24 | wk24 |
| 13–14 | 013–014 | wk28–32 Infusion | infusion | |
| 15 | 015 | Visit 15 (wk36 Clinic) | w36 | wk36 |
| 16–17 | 016–017 | wk40–44 Infusion | infusion | |
| 18 | 018 | Visit 18 (wk48 Clinic) | w48 | wk48 |
| 19–20 | 019–020 | wk52–56 Infusion | infusion | |
| 21 | 021 | Visit 21 (wk60 Clinic) | w60 | wk60 |
| 22–23 | 022–023 | wk64–68 Infusion | infusion | |
| 24 | 024 | Visit 24 (wk72 Clinic) | w72 | wk72 |
| 25–26 | 025–026 | wk76–80 Infusion | infusion | |
| 27 | 027 | Visit 27 (wk84 Clinic) | w84 | wk84 |
| 28–29 | 028–029 | wk88–92 Infusion | infusion | |
| 30 | 030 | Visit 30 (wk96 Clinic) | w96 | wk96 |
| 31–32 | 031–032 | wk100–104 Infusion | infusion | |
| 33 | 033 | Visit 33 (wk108 Clinic) | w108 | wk108 |
| 34–35 | 034–035 | wk112–116 Infusion | infusion | |
| 36 | 036 | Visit 36 (wk120 Clinic) | w120 | wk120 |
| 37–38 | 037–038 | wk124–128 Infusion | infusion | |
| 39 | 039 | Visit 39 (wk132 Clinic) | w132 | wk132 |
| 40–41 | 040–041 | wk136–140 Infusion | infusion | |
| 42 | 042 | Visit 42 (wk144 Clinic) | w144 | wk144 |
| 43–44 | 043–044 | wk148–152 Infusion | infusion | |
| 45 | 045 | Visit 45 (wk156 Clinic) | w156 | wk156 |
| 46–47 | 046–047 | wk160–164 Infusion | infusion | |
| 48 | 048 | Visit 48 (wk168 Clinic) | w168 | wk168 |
| 49–50 | 049–050 | wk172–176 Infusion | infusion | |
| 51 | 051 | Visit 51 (wk180 Clinic) | w180 | wk180 |
| 52–53 | 052–053 | wk184–188 Infusion | infusion | |
| 54 | 054 | Visit 54 (wk192 Clinic) | w192 | wk192 |
| 55–56 | 055–056 | wk196–200 Infusion | infusion | |
| 57 | 057 | Visit 57 (wk204 Clinic) | w204 | wk204 |
| 58–59 | 058–059 | wk208–212 Infusion | infusion | |
| 60 | 060 | Visit 60 (wk216 Clinic) | w216 | wk216 |
| 61–62 | 061–062 | wk220–224 Infusion | infusion | |
| 63 | 063 | Visit 63 (wk228 Clinic) | w228 | wk228 |
| 64–65 | 064–065 | wk232–236 Infusion | infusion | |
| 66 | 066 | Visit 66 (wk240 End DB/Start OLE) | w240 | wk240 |

**패턴**: Clinic 방문 = 3의 배수(9,12,15,...,66), Infusion 방문 = 나머지.
Clinic 방문 간격 = 12주, 각 Clinic 사이에 Infusion 2회(4주 간격).

### Open-Label Extension (VISCODE 67–117)

| VISCODE | SESSION_CODE | 방문명 | 속성 | 주차 |
|---------|-------------|--------|------|------|
| 67–68 | 067–068 | wk244–248 Infusion OLE | infusionole | |
| 69 | 069 | Visit 69 (wk252 Clinic OLE) | w252 | wk252 |
| 70–71 | 070–071 | wk256–260 Infusion OLE | infusionole | |
| 72 | 072 | Visit 72 (wk264 Clinic OLE) | w264 | wk264 |
| ... | ... | (동일 12주 패턴 반복) | ... | ... |
| 114 | 114 | Visit 114 (wk432 Clinic OLE) | w432 | wk432 |
| 115–116 | 115–116 | wk436–440 Infusion OLE | infusionole | |
| 117 | 117 | Visit 117 (wk444 Clinic OLE) | w444 | wk444 |

### Unscheduled / Termination

| VISCODE | SESSION_CODE | 방문명 | 속성 | VISITGROUP |
|---------|-------------|--------|------|-----------|
| 701 | 701 | Unscheduled Visit 1 | uns | Unscheduled |
| 702 | 702 | Unscheduled Visit 2 | uns | Unscheduled |
| 703 | 703 | Unscheduled Visit 3 | uns | Unscheduled |
| 704 | 704 | Unscheduled Visit 4 | uns | Unscheduled |
| 705 | 705 | Unscheduled Visit 5 | uns | Unscheduled |
| 997 | 997 | Final OLE [ET or Study Close] | et2 | OLE Treatment |
| 998 | 998 | Unscheduled MRI Visits | uv | Unscheduled |
| 999 | 999 | Early Termination [DOUBLE BLIND] | et1 | Blinded Treatment |

---

## LEARN 방문 코드 (21개)

LEARN은 A4의 관찰 연구(observational) 대응. 방문 간격이 더 넓음(24주 간격).

| VISCODE | SESSION_CODE | 방문명 | 속성 | VISITGROUP | A4 대응 |
|---------|-------------|--------|------|-----------|---------|
| 1 | 001 | A4 Visit 1 (Screening) | sc1 | Screening | A4 v1 |
| 2 | 002 | A4 Visit 2 (Screening PET) | sc2 | Screening | A4 v2 |
| 3 | 003 | A4 Visit 3 (Screening Disclosure) | sc3 | Screening | A4 v3 |
| **6** | **006** | **Visit 1 (Baseline: A4 v4-6)** | **bl** | **Blinded Tx equiv** | A4 v4–6 |
| 12 | 012 | Visit 2 (wk24: A4 v12) | w24 | Blinded Tx equiv | A4 v12 |
| 18 | 018 | Visit 3 (wk48: A4 v18) | w48 | Blinded Tx equiv | A4 v18 |
| 24 | 024 | Visit 4 (wk72: A4 v24) | w72 | Blinded Tx equiv | A4 v24 |
| 30 | 030 | Visit 5 (wk96: A4 v30) | w96 | Blinded Tx equiv | A4 v30 |
| 36 | 036 | Visit 6 (wk120: A4 v36) | w120 | Blinded Tx equiv | A4 v36 |
| 42 | 042 | Visit 7 (wk144: A4 v42) | w144 | Blinded Tx equiv | A4 v42 |
| 48 | 048 | Visit 8 (wk168: A4 v48) | w168 | Blinded Tx equiv | A4 v48 |
| 54 | 054 | Visit 9 (wk192: A4 v54) | w192 | Blinded Tx equiv | A4 v54 |
| 60 | 060 | Visit 10 (wk216: A4 v60) | w216 | Blinded Tx equiv | A4 v60 |
| 66 | 066 | Visit 11 (wk240: A4 v66) | w240 | Blinded Tx equiv | A4 v66 |
| 72 | 072 | Visit 12 (wk264: A4 v72) | w264 | OLE equiv | A4 v72 |
| 78 | 078 | Visit 13 (wk288: A4 v78) | w288 | OLE equiv | A4 v78 |
| 84 | 084 | Visit 14 (wk312: A4 v84) | w312 | OLE equiv | A4 v84 |
| 90 | 090 | Visit 15 (wk336: A4 v90) | w336 | OLE equiv | A4 v90 |
| 96 | 096 | Visit 16 (wk360: A4 v96) | w360 | OLE equiv | A4 v96 |
| 102 | 102 | Visit 17 (wk384 EOS: A4 v102/EOS) | w384 | OLE equiv | A4 v102 |
| 999 | 999 | Early Termination (Protocol) | et1 | Unscheduled | — |

**핵심 차이점**: LEARN은 **infusion 방문 없음** — Clinic 방문만 24주 간격.
LEARN baseline = **VISCODE 6** (A4는 screening MRI가 VISCODE 4, baseline이 6).

---

## Screen Fail (SF) 방문 코드 (6개)

| VISCODE | SESSION_CODE | 방문명 | 속성 | VISITGROUP |
|---------|-------------|--------|------|-----------|
| 1 | 001 | A4 Visit 1 (Screening) | sc1 | Screening |
| 2 | 002 | A4 Visit 2 (Screening PET) | sc2 | Screening |
| 3 | 003 | A4 Visit 3 (Screening Disclosure) | sc3 | Screening |
| 4 | 004 | A4 Visit 4 (Screening MRI) | sc4 | Screening |
| 5 | 005 | A4 Visit 5 (Screening LP) | sc5 | Screening |
| 6 | 006 | LEARN Visit 1 (Baseline: A4 v4-6) | bl | Screening |

---

## 주의사항

### 이미징 관련
- **A4 screening MRI** = VISCODE 4 (`004`) — VMRI baseline 데이터
- **A4 screening PET** = VISCODE 2 (`002`) — 단, PETSUVR은 VISCODE=3(SCV2), PETVADATA는 VISCODE 컬럼 없음(BID only)
- **LEARN baseline MRI** = VISCODE 6 (`006`)
- NII 인벤토리의 session code는 이 매핑과 직접 대응

### pTau217 방문코드 (config.py `PTAU217_VISIT_MAP`)
```
A4:    VISCODE 6→PTAU217_BL, 9→PTAU217_WK12, 66→PTAU217_WK240, 997→PTAU217_OLE, 999→PTAU217_ET
LEARN: VISCODE 1→PTAU217_SCR, 24→PTAU217_WK72, 66→PTAU217_WK240, 999→PTAU217_ET
```

### CDR/MMSE longitudinal 방문코드 (SV.csv 실측)
```
MMSE: VISCODE {1, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84, 90, 96, 102, 108, 114, 117, 997, 999}
CDR:  VISCODE {1, 6, 24, 48, 66, 72, 78, 84, 90, 96, 102, 108, 114, 117, 997, 998, 999}
```

### VISCODE ↔ 주차 계산
```
주차 = (VISCODE - 6) * 4    (VISCODE >= 6, Clinic + Infusion 모두 동일)
예: VISCODE 66 → (66-6)*4 = wk240
    VISCODE 7  → (7-6)*4  = wk4  (infusion)
    VISCODE 9  → (9-6)*4  = wk12 (clinic)
```

### SV.csv 특이사항
- SV.csv에서는 `VISITCD` 컬럼 사용 (VISCODE와 동일 값이지만 컬럼명이 다름)
- `SVSTDTC_DAYS_CONSENT`: 동의일 기준 경과일 (음수 가능: 사전 방문)
- `SVTYPE`: Standard / Nonstandard / Not Done
