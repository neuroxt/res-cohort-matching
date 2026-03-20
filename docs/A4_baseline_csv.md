# BASELINE.csv 컬럼 사전

A4/LEARN 파이프라인이 생성하는 `BASELINE.csv`의 컬럼 정의.

피험자당 1행. V1~V6의 데이터를 하나의 "Baseline" 시점으로 통합한 CSV입니다.

- **위치**: `A4/ORIG/DEMO/matching/BASELINE.csv`
- **규모**: ~1,890행 x ~369열
- **인덱스**: BID (피험자 ID)
- **생성**: `a4-pipeline` 또는 `a4-pipeline --baseline-only`

---

## Baseline 통합 규칙

A4는 screening(V1~V5) + randomization(V6)에 걸쳐 baseline 데이터가 수집됩니다.
각 데이터 항목이 어떤 방문에서 추출되는지:

```
V1 (screening)     → CDR (CDGLOBAL, CDRSB)
                     혈액 바이오마커 (pTau217, Roche panel)
V2 (PET scan)      → Amyloid PET (AMY_STATUS_bl, AMY_SUVR_bl, AMY_CENTILOID_bl)
                     아밀로이드 적격성 판정
V4 (MRI)           → T1, FLAIR NII paths
                     MRI 볼륨 (VMRI_*_bl, 50 ROI)
                     Tau PET (FTP NII path, TAU_*_bl, 273 ROI, 서브셋 ~447명)
V6 (randomization) → MMSE
                     최종 등록 확정
```

> LEARN은 V4가 아닌 **V6에서 MRI가 촬영**됩니다. 파이프라인이 자동 처리합니다.

---

## 알려진 제한 사항

### PTAGE 159건 누락 (8.4%)

PTAGE는 `AGEYR + DAYS_CONSENT(V6) / 365.25`로 계산하는 V6 기준 나이입니다.
V6 세션이 SV.csv에 없는 159명(early termination 등)은 PTAGE가 NaN입니다.

대안 컬럼 AGEYR(screening 나이)은 100% 채워져 있습니다.
screening~randomization 간격이 수개월이므로 PTAGE와 AGEYR의 차이는 보통 0.1~0.5세입니다.

**분석 시 권장**: PTAGE를 우선 사용하되, NaN인 경우 AGEYR을 fallback으로 사용하세요:
```python
df['age'] = df['PTAGE'].fillna(df['AGEYR'])
```

### CDR은 V1 값

A4 프로토콜에서 CDR은 V1(screening)에서만 측정됩니다.
V6(randomization)에서는 CDR 평가가 없으므로, CDGLOBAL/CDRSB는 V1 값입니다.
A4 등록 기준이 CDR=0이므로 CDGLOBAL은 전원 0.0입니다.

---

## 컬럼 목록

### Demographics (7열)

| 컬럼 | 설명 | 소스 시점 | Fill | 값 / 범위 |
|------|------|-----------|------|-----------|
| PTGENDER | 성별 | screening | 100% | Male / Female |
| PTAGE | V6 기준 나이 | V6 | 91.6% | 65.1 ~ 86.0세 (159건 NaN, 위 참고) |
| PTEDUCAT | 교육 연수 | screening | 99.8% | 7 ~ 30 |
| APOEGN | APOE 유전형 | screening | 99.2% | e3/e3, e3/e4, e4/e4, e2/e3, e2/e4, e2/e2 |
| AGEYR | Screening 나이 | screening | 100% | 65.0 ~ 85.7세 |
| LRNFLGSNM | LEARN 여부 | enrollment | 100% | Y / N |
| Research_Group | 코호트 | enrollment | 100% | amyloidE / LEARN amyloidNE |

### Amyloid PET (4열)

| 컬럼 | 설명 | 소스 시점 | Fill | 값 / 범위 |
|------|------|-----------|------|-----------|
| AMY_STATUS_bl | 아밀로이드 상태 | V2 | 100% | positive / negative |
| AMY_SUVR_bl | Composite SUVR | V2 | 100% | 0.81 ~ 1.98 |
| AMY_SUVR_CER_bl | Cerebellar ref SUVR | V2 | 99.9% | 0.79 ~ 2.09 |
| AMY_CENTILOID_bl | Centiloid 단위 | V2 | 99.9% | -32.6 ~ 205.4 |

### Cognitive (3열)

| 컬럼 | 설명 | 소스 시점 | Fill | 값 / 범위 |
|------|------|-----------|------|-----------|
| MMSE | Mini-Mental State Examination | **V6** | 91.2% | 22 ~ 30 |
| CDGLOBAL | CDR Global Score | **V1** | 100% | 0.0 (전원, 등록 기준) |
| CDRSB | CDR Sum of Boxes | **V1** | 100% | 0.0 ~ 2.0 |

### pTau217 (14열)

방문별 피벗. 값: ORRESRAW (수치). LLOQ 컬럼: `<LLOQ` 여부 (True/False).

| 컬럼 | 설명 | Fill |
|------|------|------|
| PTAU217_BL | Baseline (A4: VISCODE=6) | 57.2% |
| PTAU217_WK12 | Week 12 (A4: VISCODE=9) | 55.7% |
| PTAU217_WK240 | Week 240 (VISCODE=66) | 51.0% |
| PTAU217_OLE | Open-label extension (VISCODE=997) | 9.9% |
| PTAU217_ET | Early termination (VISCODE=999) | 10.0% |
| PTAU217_SCR | Screening (LEARN: VISCODE=1) | 25.4% |
| PTAU217_WK72 | Week 72 (LEARN: VISCODE=24) | 24.3% |
| *_LLOQ | 각 방문별 LLOQ flag | 위와 유사 |

### Roche Plasma Biomarkers (12열)

Screening 시점 혈액. 값: LABRESN (수치). BLQ 컬럼: below limit of quantification 여부.

| 컬럼 | 설명 | Fill |
|------|------|------|
| ROCHE_GFAP_bl | Glial Fibrillary Acidic Protein | 55.6% |
| ROCHE_NFL_bl | Neurofilament Light Chain | 55.5% |
| ROCHE_PTAU181_bl | Phospho-tau 181 | 40.6% |
| ROCHE_AB40_bl | Amyloid-beta 40 | 55.0% |
| ROCHE_AB42_bl | Amyloid-beta 42 | 55.7% |
| ROCHE_APOE4_bl | APOE4 (Roche assay) | 24.2% |
| *_BLQ_bl | 각 마커별 BLQ flag | 위와 유사 |

### NII Paths (4열)

Baseline NII 파일 절대 경로. A4는 V4, LEARN은 V6에서 MRI 추출. FBP는 V2.

| 컬럼 | 설명 | Fill |
|------|------|------|
| T1_NII_PATH | 구조 MRI (T1w) | 93.7% |
| FLAIR_NII_PATH | FLAIR MRI | 92.9% |
| FBP_NII_PATH | Florbetapir amyloid PET | 99.4% |
| FTP_NII_PATH | Flortaucipir tau PET | 23.8% (서브셋만) |

### VMRI — MRI 볼륨 (51열)

NeuroQuant 기반 FreeSurfer 볼륨. V4(MRI) 시점. 전체 66.4% fill (1,255/1,890명).

접두사 `VMRI_`, 접미사 `_bl`. 예: `VMRI_LeftHippocampus_bl`, `VMRI_RightThalamus_bl`.

주요 ROI:
- Hippocampus (Left/Right)
- Amygdala (Left/Right)
- Lateral Ventricle (Left/Right + Inferior)
- Caudate, Putamen, Pallidum (Left/Right)
- Thalamus (Left/Right)
- Cortical Gray/White Matter (Left/Right)
- Total Gray Matter, Supratentorial Volume
- 전체 목록: 51개 ROI

### TAU SUVR — Tau PET 볼륨 (273열)

Flortaucipir (FTP) SUVR. V4 시점. 서브셋 ~447명 (23.7% fill).

접두사 `TAU_Mean_` 또는 `TAU_Volume_mm3_`, 접미사 `_bl`.

FreeSurfer atlas 기반 273개 ROI. 예:
- `TAU_Mean_Left_Hippocampus_bl` (SUVR)
- `TAU_Volume_mm3_Left_Hippocampus_bl` (mm3)
- Cortical regions, subcortical nuclei, white matter, ventricles 등

> 2개 ROI(`TAU_*_non_WM_hypointensities_bl`)는 fill rate 0.5% (9명)로 사실상 비어있습니다.
> FreeSurfer segmentation에서 해당 영역이 거의 검출되지 않기 때문입니다.

---

## 참고 문서

| 문서 | 내용 |
|------|------|
| [`docs/A4_protocol.md`](A4_protocol.md) | V1~V9 방문 체계, 영상 프로토콜, 바이오마커 수집 시점 |
| [`docs/A4_column_dictionary.md`](A4_column_dictionary.md) | MERGED.csv 전체 컬럼 사전 (BASELINE.csv 컬럼도 포함) |
| [`docs/A4_viscode_reference.md`](A4_viscode_reference.md) | VISCODE <-> SESSION_CODE 매핑 |
