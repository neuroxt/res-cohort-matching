# A4/LEARN 파일 간 조인 관계

CSV A를 CSV B에 조인할 때 사용하는 키, 카디널리티(1:1 / 1:N), 파이프라인 내 사용 맥락.

**참조 코드**: `src/a4/clinical.py`, `src/a4/pipeline.py`, `src/a4/config.py`

---

## 조인 키 유형 요약

| 키 유형 | 파일 | 카디널리티 | 설명 |
|---------|------|-----------|------|
| BID only | PTDEMOG, SUBJINFO, demography, PETVADATA | 1:1 per BID | 피험자 수준 |
| BID + VISCODE | MMSE, CDR, REGISTRY, SPPACC, PETSUVR, VMRI | 1:1 per visit | 방문 수준 |
| BID + VISITCD | SV.csv | 1:1 per visit | VISITCD = VISCODE (컬럼명만 다름) |
| ID = BID (compound) | TAUSUVR | 1:1 per BID | ID 컬럼이 BID 역할 |
| BID + VISCODE + SUBSTUDY | pTau217, Plasma_Roche, AB_Test | 1:1 per visit+substudy | SUBSTUDY 필터 필수 |
| BID + VISCODE + PACCQSNUM | SPPACC | 1:N (5 per visit) | 검사항목별 반복 |
| BID + VISCODE + brain_region | PETSUVR | 1:N (8 per visit) | 뇌영역별 반복 |

---

## 파이프라인 조인 흐름

### Phase 1: `build_clinical_table()` — BID 수준 통합

```
_build_demographics():
    PTDEMOG ──[BID, VISCODE=1]──→ dedup(BID) → demo
    SUBJINFO ──[BID]──→ dedup(BID) → subj
    demo.join(subj, how='outer')
    ↓
_build_amyloid_status():
    PETVADATA ──[BID]──→ dedup(BID) → {AMY_STATUS_bl, AMY_SUVR_bl}
    demo.join(amy, how='left')
    ↓
_build_pet_suvr():
    PETSUVR ──[brain_region='Composite_Summary']──→ dedup(BID)
    → {AMY_SUVR_CER_bl, AMY_CENTILOID_bl}
    demo.join(pet_suvr, how='left')
    ↓
_build_cognitive():
    MMSE(PRV2) ──sort(VISCODE)──→ dedup(BID) → {MMSE_bl}
    CDR(PRV2) ──sort(VISCODE)──→ dedup(BID) → {CDGLOBAL_bl, CDRSB_bl}
    demo.join(cognitive, how='left')
    ↓
_build_vmri():
    VMRI ──[VISCODE=4]──→ dedup(BID) → {VMRI_*_bl × 50 ROI}
    demo.join(vmri, how='left')
    ↓
_build_tau_suvr():
    TAUSUVR ──[ID→BID]──→ dedup(BID) → {TAU_*_bl × 272 ROI}
    demo.join(tau, how='left')
    ↓
_build_ptau217():
    pTau217 ──[SUBSTUDY×VISCODE pivot]──→ dedup(BID)
    → {PTAU217_BL, PTAU217_WK12, ..., PTAU217_ET, *_LLOQ}
    demo.join(ptau217, how='left')
    ↓
_build_demography_groups():
    demography ──[Subject ID→BID]──→ Research_Group 보충
    demo.join(demog, how='outer')
    ↓
= clinical_table (BID 인덱스, ~340+ cols)
```

**조인 방법**: 모든 서브 테이블은 BID 인덱스로 정렬한 후 `DataFrame.join(how='left/outer')`.

---

### Phase 2: `build_session_index()` — (BID, SESSION_CODE) 인덱스

```
SV.csv ──[BID, VISITCD]──→ dropna(SVSTDTC_DAYS_CONSENT)
    VISITCD → SESSION_CODE (3자리 zero-pad)
    rename: SVSTDTC_DAYS_CONSENT → DAYS_CONSENT
    ↓
SUBJINFO ──[BID, AGEYR]──→ dedup(BID)
    ↓
sv.merge(ageyr, on='BID', how='inner')
    PTAGE = AGEYR + DAYS_CONSENT / 365.25
    ↓
= session_index (BID+SESSION_CODE 인덱스, cols: DAYS_CONSENT, PTAGE)
```

---

### Phase 3: `build_longitudinal_cognitive()` — (BID, SESSION_CODE) 인지 평가

```
mmse.csv(Raw Data) ──[BID, VISCODE, MMSCORE]──→ dropna
    VISCODE → SESSION_CODE
    dedup(BID+SESSION_CODE) → {MMSE}
    ↓
cdr.csv(Raw Data) ──[BID, VISCODE, CDGLOBAL, CDSOB]──→ dropna
    VISCODE → SESSION_CODE
    dedup(BID+SESSION_CODE) → {CDGLOBAL, CDRSB}
    ↓
mmse.join(cdr, how='outer')
= long_cognitive (BID+SESSION_CODE 인덱스)
```

---

### Phase 4: `build_session_merged()` — MERGED.csv 생성

```
session_index ──────────────────── base (BID+SESSION_CODE)
    │
    ├── clinical_table.join(on='BID', how='left')
    │   → BID-level cols (PTGENDER, APOEGN, AMY_*, VMRI_*, TAU_*, PTAU217_*)
    │   → PTAGE 제외 (session_index의 동적 PTAGE 우선)
    │
    ├── long_cognitive.join(how='left')
    │   → session-level cols (MMSE, CDGLOBAL, CDRSB)
    │
    └── inventory (by_modality)
        for each modality (T1, FLAIR, FBP, ...):
            mod_df ──[BID, SESSION_CODE]──→ dedup
            base.join(mod_df, how='left')
            → {MOD_NII_PATH, protocol/MOD/*}
        ↓
        MODALITIES 컬럼 생성 (comma-sep: "T1,FLAIR,FBP")
    ↓
= MERGED.csv (BID+SESSION_CODE 인덱스)
```

---

## 조인 다이어그램

```
                    ┌─ PTDEMOG (BID)
                    ├─ SUBJINFO (BID)
                    ├─ demography (Subject ID = BID)
                    ├─ PETVADATA (BID)
                    ├─ PETSUVR (BID, brain_region filter)
                    ├─ MMSE PRV2 (BID, VISCODE=1)
    BID 수준 ──────├─ CDR PRV2 (BID, VISCODE=1)
                    ├─ VMRI (BID, VISCODE=4)
                    ├─ TAUSUVR (ID → BID)
                    └─ pTau217 (BID, VISCODE pivot, SUBSTUDY filter)
                            │
                            ▼
                    clinical_table (BID index)
                            │
                            │ .join(on='BID', how='left')
                            ▼
    SV.csv ──────→ session_index ────────────────┐
    (BID+VISITCD)  (BID+SESSION_CODE)            │
                   cols: DAYS_CONSENT, PTAGE     │
                                                 │
    mmse.csv ─────→ long_cognitive ──────────────┤
    cdr.csv        (BID+SESSION_CODE)            │ .join(how='left')
                   cols: MMSE, CDGLOBAL, CDRSB   │
                                                 │
    NII scan ─────→ inventory ──────────────────┤
    (BID/session/  (by_modality dict)            │ per-modality join
     modality)                                   │
                                                 ▼
                                          MERGED.csv
                                    (BID + SESSION_CODE index)
```

---

## 주의사항

### SUBSTUDY 필터 필요 파일
- `pTau217`, `Plasma_Roche`, `AB_Test`, `SV.csv`, `mmse.csv(long)`, `cdr.csv(long)`
- 이들은 A4 + LEARN + SF(Screen Fail) 데이터가 혼재
- 파이프라인에서는 SUBSTUDY 필터 없이 전체 BID에 대해 처리 (clinical_table에서 amyloidNE 제외로 처리)

### VISCODE vs VISITCD
- 대부분 CSV: `VISCODE` 컬럼
- SV.csv만: `VISITCD` 컬럼 (동일 값이지만 컬럼명이 다름)
- 파이프라인에서 `VISITCD` → `SESSION_CODE` 변환 시 `%03d` zero-pad

### TAUSUVR ID 파싱
- TAUSUVR의 `ID` 컬럼은 순수 BID (BID_VISCODE가 아닌 BID만)
- 현재 파이프라인에서는 `ID` → `BID`로 단순 rename 후 dedup

### Long-format → Wide-format 변환
- **PETSUVR**: brain_region 기준 long-format → Composite_Summary 행만 필터
- **pTau217**: SUBSTUDY × VISCODE 기준 long-format → wide-format 피벗 (PTAU217_BL, _WK12, ...)
- **Plasma_Roche**: LBTESTCD 기준 long-format (현재 파이프라인 미사용)
- **AB_Test**: LBTESTCD 기준 long-format (현재 파이프라인 미사용)

### Outer vs Left Join
- `_build_demographics()`: PTDEMOG.join(SUBJINFO, how='**outer**') — SUBJINFO에만 있는 BID 포함
- `_build_demography_groups()`: demo.join(demog, how='**outer**') — amyloidNE 추가
- 나머지 모든 join: **left** join (clinical_table 기준)
- `build_session_merged()`: session_index 기준 left join (세션이 있는데 clinical이 없으면 NaN)
