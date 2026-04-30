# 진단 코드북 — `y2_diag` & `y2_desc`

KBASE의 formal 진단 인코딩. 출처는 `2_Diag_Demo.xlsx`의 Sheet1 codebook (302-col 통합 사전) 안의 `y2_diag` / `y2_desc` cell value. 디렉토리에 같이 있는 `2_Diag_Demo_sheet3_dx_coding.png`가 같은 내용을 캡처한 이미지.

> **별도 시트 아님**: 파일명이 "sheet3"이지만 xlsx의 실제 Sheet2는 `max_row=1, max_col=1`로 빈 시트. 매핑은 codebook(Sheet1) 안에서만 확인 가능.

---

## `y2_diag` (1차 진단, 5 코드)

| 코드 | 한국어 라벨 | 영어 | 실측 행수 (Diag_Demo) |
|------|-----------|------|----------------------|
| `1` | 청장년 정상인 | Young adult normal control | 97 |
| `2` | 고령 정상인 | Elderly normal control | 1,073 |
| `3` | 경도인지장애 [기억상실성] | MCI (amnestic) | 369 |
| `4` | NIA-AA 유력 알츠하이머병 치매 | NIA-AA probable AD | 383 |
| `9` | 기타 | Other | 147 |

---

## `y2_desc` (상세 진단, 19 코드)

`y2_desc`는 `y2_diag`를 더 세분화한 진단 분류. 정수 또는 NaN.

| 코드 | 한국어 라벨 | 영어 약어 | 부모 `y2_diag` | 실측 행수 |
|------|-----------|----------|---------------|-----------|
| `10` | 청장년 정상인 | Young adult NC | 1 | 23 |
| `20` | 고령 정상인 | Elderly NC | 2 | 776 |
| `30` | 기억성 단일영역 경도인지장애 | aMCI-S (amnestic single-domain) | 3 | 65 |
| `31` | 기억성 다중영역 경도인지장애 | aMCI-M (amnestic multi-domain) | 3 | 150 |
| `32` | 비기억성 단일영역 경도인지장애 | naMCI-S (non-amnestic single) | 9 (계열상 MCI) | 40 |
| `33` | 비기억성 다중영역 경도인지장애 | naMCI-M (non-amnestic multi) | 9 (계열상 MCI) | 33 |
| `34` | 경도인지장애가 아닌 비치매 인지장애 | CIND (non-MCI cognitive impairment) | 9 | 59 |
| `40` | NIA-AA 유력 알츠하이머병 치매 | NIA-AA probable AD | 4 | 281 |
| `41` | NIA-AA 가능 알츠하이머병 | NIA-AA possible AD | 9 | 8 |
| `50` | 유력 혈관성 치매 | probable VD (vascular dementia) | 9 | (실측 0) |
| `51` | 가능 혈관성 치매 | possible VD | 9 | (실측 0) |
| `60` | 유력 루이체 치매 | probable DLB | 9 | (실측 0) |
| `61` | 가능 루이체 치매 | possible DLB | 9 | (실측 0) |
| `62` | 유력 파킨슨병 치매 | probable PDD | 9 | (실측 0) |
| `63` | 가능 파킨슨병 치매 | possible PDD | 9 | (실측 0) |
| `70` | 전측두엽 치매 | FTD | 9 | (실측 0) |
| `71` | 진행성 비유창성 실어증 | PNA (progressive non-fluent aphasia) | 9 | (실측 0) |
| `72` | 의미 치매 | SD (semantic dementia) | 9 | (실측 0) |
| `99` | 기타 (상세 기술) | Other (free-text in `y2_desc_details`) | 9 | 7 |
| (NaN) | (미진단 또는 baseline 미실시) | — | — | 627 |

**관찰**:
- 50/51/60/61/62/63/70/71/72 — 다른 치매 변형 코드는 codebook에 정의돼 있지만 실제 데이터에서 0건. KBASE는 사실상 NC + MCI + AD 3 큰 그룹 + 소수 atypical cases로 구성.
- y2_desc=NaN 627건은 V0 baseline 미할당 추정 — Diag_Demo simplified 시트에서 K_visit별 분포 확인 권장.

---

## `y2_desc_details`

자유 텍스트 컬럼. y2_desc=99 (기타) 또는 추가 메모가 필요한 경우 사용. 대부분의 행에서 빈 값.

---

## 코드 → Python dict (분석용)

```python
Y2_DIAG_LABEL = {
    1: 'NC_young',
    2: 'NC_elderly',
    3: 'MCI',
    4: 'AD_probable',
    9: 'Other',
}

Y2_DESC_LABEL = {
    10: 'NC_young',
    20: 'NC_elderly',
    30: 'aMCI-S',
    31: 'aMCI-M',
    32: 'naMCI-S',
    33: 'naMCI-M',
    34: 'CIND',
    40: 'AD_probable',
    41: 'AD_possible',
    50: 'VD_probable',
    51: 'VD_possible',
    60: 'DLB_probable',
    61: 'DLB_possible',
    62: 'PDD_probable',
    63: 'PDD_possible',
    70: 'FTD',
    71: 'PNA',
    72: 'SD',
    99: 'Other',
}

# y2_desc → y2_diag inverse mapping (검증용)
Y2_DESC_TO_DIAG = {
    10: 1, 20: 2,
    30: 3, 31: 3,
    32: 9, 33: 9, 34: 9,  # naMCI/CIND은 y2_diag=3 아닌 9 (기타)로 분류됨에 주의
    40: 4,
    41: 9, 50: 9, 51: 9, 60: 9, 61: 9, 62: 9, 63: 9, 70: 9, 71: 9, 72: 9, 99: 9,
}
```

> **주의**: codebook 텍스트 그대로의 분류상 naMCI/CIND/possible AD 등이 y2_diag=9(기타)로 들어감. **y2_diag=3 (MCI [기억상실성])은 amnestic MCI만 포함**. 비기억성 MCI를 분석 대상에 포함하려면 y2_desc=30/31/32/33/34 필터 권장.

---

## GROUP 라벨과의 관계

`GROUP` (imaging inventory + master 컬럼)은 y2_diag와 별개의 임상 그룹 라벨. **1:1 대응 아님**.

매핑 가이드 (master 실측 기반):

| GROUP | 가장 흔한 y2_diag | y2_diag NaN 비율 |
|-------|------------------|---------------------|
| `NC_청장년` | 1 (97/102) | 3/102 |
| `NC_고령` | 2 (568/675) | 81/675 |
| `MCI` | 3 (205/329) | 49/329 |
| `AD` | 4 (151/178) | 23/178 |

**불일치 사례** (master 실측):
- `MCI` GROUP인데 `y2_diag=4` (probable AD): **38건**
- `MCI` GROUP인데 `y2_diag=2` (elderly NC): 1건
- `NC_고령` GROUP인데 `y2_diag=3` (MCI): 8건
- `NC_고령` GROUP인데 `y2_diag=9` (기타): 18건

→ 분석 시 어느 필드를 ground truth로 쓸지 명시. CRF formal 진단을 우선하려면 `y2_diag`/`y2_desc`, imaging-time 임상 그룹 라벨이 필요하면 `GROUP`. 자세한 진단 quirk는 [`diagnosis_demographics.md`](diagnosis_demographics.md#group-vs-y2_diag-mismatch).

---

## ADNI / OASIS3 / A4 진단과의 매핑 가이드

cross-cohort 분석 시 표준화 권장:

| 표준 그룹 | KBASE | ADNI (`DX`) | OASIS3 | A4 / LEARN |
|-----------|-------|------------|--------|-----------|
| Cognitively Normal | y2_diag=1 또는 2, 또는 GROUP=NC_* | `CN` | `RACCDIAG=Cognitively Normal` | `Research_Group=LEARN amyloidNE` |
| MCI | y2_diag=3 (또는 y2_desc=30/31/32/33/34) | `MCI`/`LMCI`/`EMCI` | `RACCDIAG=Mild Cognitive Impairment` | (A4는 amyloid+ asymptomatic 위주) |
| Probable AD | y2_diag=4 (y2_desc=40) | `AD`/`Dementia` | `RACCDIAG=Alzheimer Disease Dementia` | (A4는 비치매) |
| Atypical / Other | y2_diag=9 | `MCIAD` 등 | `NACCETPR` (etiology) | — |

→ 한국 코호트 특성상 `청장년` (young NC, age 21~) 그룹이 따로 있음. ADNI/OASIS3에는 거의 없는 카테고리.
