# OASIS3 PET imaging 데이터 참조

OASIS3에는 PET 데이터가 **3개 메타데이터 CSV** + **NIfTI raw scan** 형태로 존재한다. 이 문서는 세 CSV의 역할 비교, 트레이서별 컬럼 채워짐 패턴, Centiloid 변환 방법론, PUP 파이프라인 원리를 정리한다.

---

## 1. 파일 요약

| 파일 | 위치 | 행 수 × 컬럼 | 역할 |
|------|------|--------------|------|
| **OASIS3_amyloid_centiloid.csv** | `DEMO/` | 1,894 × 8 | **PUP 출력 + Centiloid 변환**. Amyloid PET (PIB, AV45)에 대한 정량 결과. |
| **OASIS3_PET_json.csv** | `DEMO/` | 2,158 × 51 | **BIDS JSON sidecar 평탄화**. 모든 PET 스캔(amyloid + tau + FDG)의 acquisition 파라미터. |
| **OASIS3_PET_datasetdescription.csv** | `DEMO/` | 1,088 × 9 | **BIDS dataset_description.json**. XNAT URL, accession 식별자. 데이터 출처 추적용. |

---

## 2. OASIS3_amyloid_centiloid.csv

### 컬럼

| 컬럼 | 설명 |
|------|------|
| subject_id | OASISID (e.g., `OAS30001`) |
| oasis_session_id | PET session label (`OAS30001_AV45_d2430` 형식) |
| accession_number | XNAT accession (`CENTRAL_E*` 또는 `CENTRAL_S*`) |
| tracer | `PIB` 또는 `AV45` |
| Centiloid_fBP_TOT_CORTMEAN | Binding potential 기반 Centiloid (kinetic modeling 필요) |
| Centiloid_fSUVR_TOT_CORTMEAN | SUVR 기반 Centiloid (single-frame 가능) |
| Centiloid_fBP_rsf_TOT_CORTMEAN | fBP + Regional Spread Function PVC |
| Centiloid_fSUVR_rsf_TOT_CORTMEAN | fSUVR + RSF PVC |

### Tracer × 컬럼 채워짐 패턴 (실측)

| tracer | 행 수 | fBP | fSUVR | fBP_rsf | fSUVR_rsf |
|--------|-------|-----|-------|---------|-----------|
| **PIB** | 1,178 | 1,141 (97%) | 1,178 (100%) | 1,141 (97%) | 1,178 (100%) |
| **AV45** | 715 | **0 (NaN)** | 715 (100%) | **0 (NaN)** | 715 (100%) |

> **중요한 패턴**: AV45는 `fBP` 컬럼이 전부 NaN. **AV45 분석에는 `Centiloid_fSUVR_*` 컬럼을 사용해야 한다**.
>
> 이유: fBP (binding potential, BPND)는 dynamic PET acquisition (multi-frame, 60+분)이 필요한 kinetic modeling 결과. PIB 데이터는 dynamic으로 수집되어 Logan plot으로 BPND 산출 가능, **AV45는 static acquisition (post-injection ~50분 단일 frame)** 만 있어 kinetic modeling 불가 — SUVR만 산출.

### Centiloid 값 범위 (실측)

| | min | max |
|---|---|---|
| Centiloid_fSUVR | −39.7 | +203.9 |

해석 (Klunk 2015 권장 임계값):
- **< 12 Centiloid**: amyloid negative
- **12 ~ 25 Centiloid**: 경계
- **> 25 Centiloid**: amyloid positive
- **~100 Centiloid**: 전형적 AD 환자 평균

---

## 3. OASIS3_PET_json.csv

### 컬럼 그룹별 요약 (51 cols)

| 그룹 | 컬럼 (대표) | 설명 |
|------|------------|------|
| 식별자 | subject_id, session_id, filename | NIfTI 매칭 키 |
| 스캐너 | Modality, Manufacturer, ManufacturersModelName, DeviceSerialNumber | `Modality=PT`, `Manufacturer ∈ {Siemens, SIEMENS}` (대소문자 혼재), `BioGraph mMR PET` 등 |
| 트레이서 식별 | Tracer.Name, TracerName, Tracer.Isotope, TracerRadionuclide, Tracer.InjectionType, ModeOfAdministration | `Tracer.Name ∈ {PIB, AV45, AV1451, FDG}`. Isotope: `C11`(PIB) 또는 `F18`(AV45/AV1451/FDG). InjectionType: `Bolus`. |
| 재구성 | Recon.MethodName, ReconMethodName, ReconMethodParameterLabels/Unit/Values, ReconFilterType, ReconFilterSize | `Recon.MethodName ∈ {Back projection reconstruction, DIFT, OP-OSEM, OSEM2D 4i16s}`. |
| 주입량 | Dosage, DosageUnits, InjectedRadioactivity, InjectedRadioactivityUnit, InjectedMass, InjectedMassUnits, SpecificRadioactivity, SpecificRadioactivityUnit | `mCi`/`MBq` 단위 혼재 가능. |
| 시간 | InjectionTime, InjectionStart, InjectionStartUnit, ScanStartTime, ScanStart, ScanStartUnit, TimeZero, TimeZeroUnit, Time, Unit | `hh:mm:ss` 또는 epoch seconds. |
| 프레임 | FrameTimes (JSON-encoded list) | Dynamic 스캔의 frame schedule (`{Labels, Units, Values}` 구조) |
| 정량 | AcquisitionMode, AttenuationCorrection, Data.DecayCorrectionTime, ImageDecayCorrected, ImageDecayCorrectionTime | Decay correction 기준점 (TimeZero 또는 ScanStart) |
| 처리 | ConversionSoftware | DICOM → NIfTI 변환 도구 (예: `dcm2niix`) |

### 트레이서 분포 (실측)

```
PIB:    999  (PET_json, dynamic)
AV45:   491  (PET_json, static)
FDG:    117  (PET_json, dynamic)
blank:  550  (TracerName 누락 — JSON sidecar에 명시 안 된 케이스)
```

> 550건의 blank tracer는 BIDS sidecar에 `TracerName` 필드가 없어서. JSON 파일 자체를 다시 파싱하거나 `oasis_file_list.csv`의 SEQ 컬럼으로 fallback.

### 활용 예: AV45 vs PIB protocol 비교

```python
import pandas as pd
df = pd.read_csv("OASIS3_PET_json.csv")

# tracer별 평균 주입량
df.groupby('TracerName')[['InjectedRadioactivity', 'Dosage']].mean()
# AV45 평균 주입량은 ~10 mCi (370 MBq) 표준
# PIB은 ~15 mCi (555 MBq), 단 더 짧은 T½(20분)이라 빠른 촬영 필요
```

---

## 4. OASIS3_PET_datasetdescription.csv

### 컬럼

| 컬럼 | 설명 |
|------|------|
| OASIS_ID | OASISID |
| session_id | PET session label |
| Name | 항상 `OASIS3` |
| License | DUA 안내 텍스트 |
| HowToAcknowledge | 인용 안내 |
| filename | 항상 `dataset_description.json` |
| **DatasetDOI** | XNAT 데이터 archive URL (`https://central.xnat.org/data/archive/projects/OASIS3/subjects/CENTRAL_S*/experiments/CENTRAL_E*` 또는 `CENTRAL02_E*`) |
| BidsVersion | `1.0.1` (BIDS 1.0.1 표준) |
| **accesssion** | XNAT accession 식별자 (**컬럼명 오타 — 's' 3개**). `CENTRAL_E*` 또는 `CENTRAL02_E*` |

> 컬럼명 `accesssion`은 OASIS3 원본 데이터의 오타이므로 분석 코드에서 그대로 사용. `df['accesssion']`. 만약 정상 철자(`accession`)로 컬럼이 변경된 케이스를 발견하면 데이터 갱신 검토 필요.

---

## 5. PET 트레이서 상세

| Tracer | 정식명 | 표적 | T½ | Acquisition | Centiloid 가능? | 비고 |
|--------|--------|------|----|--------------------|-----------------|------|
| **PIB** | [11C]Pittsburgh Compound B | Amyloid-β plaque | 20 min | **Dynamic** (60-90분, multi-frame) | ✓ (fBP + fSUVR) | C11 표지로 sub-cyclotron 시설 필요. Knight ADRC PIB 스캔은 60분에 종료. Klunk 2004. |
| **AV45** | Florbetapir, [18F]Avid AV-45 | Amyloid-β plaque | 110 min | **Static** (주입 후 ~50분 단일 frame) | ✓ (fSUVR only) | F18로 운반 용이. FDA 승인 (Amyvid). |
| **AV1451** | Flortaucipir, [18F]T807 | Tau (PHF) | 110 min | Static (주입 후 ~80-100분) | ✗ (centiloid는 amyloid 전용) | FDA 승인 (Tauvid). off-target binding 주의 (choroid plexus, basal ganglia). Wang 2016. |
| **FDG** | [18F]Fluorodeoxyglucose | Glucose metabolism | 110 min | Dynamic (~30-60분) | ✗ (cerebral metabolism, amyloid와 무관) | AD-typical 패턴: parietotemporal hypometabolism. |

---

## 6. PUP (PET Unified Pipeline) 처리 단계

OASIS3 amyloid centiloid 값은 **Knight ADRC의 PUP 파이프라인** 출력. Su et al. NeuroImage Clin 2018에 상세 기술되어 있으며, 코드는 [GitHub: ysu001/PUP](https://github.com/ysu001/PUP)에 공개.

### 처리 흐름

```
1. Scanner resolution harmonization
   └─ 다른 스캐너 간 PSF (point spread function) 차이 보정. 각 스캔을 표준 8mm FWHM로 smoothing.

2. Inter-frame motion correction
   └─ Dynamic 스캔의 frame 간 head motion 보정 (frame-to-reference rigid registration).

3. Sum/mean image 생성 (SUVR용) 또는 frame-by-frame TAC (BPND용)

4. PET-MR registration
   └─ Subject별 T1 MRI에 PET을 rigid-body로 등록. FreeSurfer aparc+aseg를 PET space로 이동.

5. Regional time-activity curves (TAC) extraction (dynamic only)
   └─ Frame별 region mean activity → time series.

6. Partial Volume Correction (PVC) — 옵션
   └─ Regional Spread Function (RSF) 방법 (Rousset, Maroy, Bullich): 작은 ROI의 PVE 보정.
   └─ `*_rsf_*` 컬럼이 PVC 적용 결과.

7. SUVR 산출
   └─ Reference region (cerebellar GM 또는 cerebellum whole) 기준 normalize.

8. Binding Potential (BPND) 산출 — dynamic only
   └─ Logan graphical analysis (45-90분 frame).

9. Centiloid 변환
   └─ GAAIN 표준 anchor 데이터셋 (Klunk 2015) 기반 linear scale 변환.
   └─ AV45 → Centiloid: tracer-specific calibration constants 사용.
   └─ PIB → Centiloid: 직접 변환.

10. Mean cortical SUVR/BPND → TOT_CORTMEAN composite
    └─ frontal, temporal, parietal, posterior cingulate cortex의 평균.
```

---

## 7. Centiloid 방법론

### Klunk 2015 정의

Centiloid scale은 amyloid PET 결과를 **트레이서/파이프라인 독립적인 단일 척도**로 표준화한다.

```
Centiloid = 100 × (target_SUVR − YC_mean) / (AD100_mean − YC_mean)
```

- **YC_mean**: GAAIN Young Control (인지정상 30-49세) 35명의 평균 SUVR. 정의에 의해 0 Centiloid.
- **AD100_mean**: GAAIN Typical AD 45명의 평균 SUVR. 정의에 의해 100 Centiloid.

### Tracer 간 호환성

각 트레이서별로 **YC_mean과 AD100_mean이 다르므로** linear regression으로 상호 변환한다 (Klunk 2015 Table 4):

```
PIB SUVR → Centiloid:    Centiloid = (PIB_SUVR − 1.009) × 100 / 0.940
AV45 SUVR → Centiloid:   Centiloid = (AV45_SUVR − 1.009) × 100 / 1.067 × scale_factor
                          (각 사이트의 calibration anchor 필요)
```

> OASIS3는 Knight ADRC의 자체 calibration을 사용 — 다른 데이터셋(ADNI 등)의 centiloid와 직접 비교 시 cross-calibration 검증 권장.

### 임계값

| Centiloid | 해석 | 활용 |
|-----------|------|------|
| < 12 | Negative | A4 trial cut-off는 AV45 SUVR 1.15 ≈ 14-25 Centiloid |
| 12-25 | Borderline / equivocal | |
| 25-50 | Positive (mild) | Preclinical AD에 자주 등장 |
| 50-100 | Positive (moderate) | MCI/early AD |
| > 100 | Positive (severe) | Typical AD dementia |

---

## 8. 활용 예

### 예 1: Amyloid 양성 subject 선정

```python
import pandas as pd

centiloid = pd.read_csv("OASIS3_amyloid_centiloid.csv")

# Subject별 baseline (가장 작은 days_to_visit) AV45 또는 PIB Centiloid
centiloid['day'] = centiloid['oasis_session_id'].str.extract(r'_d(\d+)$')[0].astype(int)
baseline = (centiloid
            .sort_values('day')
            .drop_duplicates('subject_id', keep='first'))

# AV45는 fSUVR 사용, PIB도 fSUVR 사용 (호환성)
baseline['centiloid'] = baseline['Centiloid_fSUVR_TOT_CORTMEAN']
baseline['amyloid_positive'] = baseline['centiloid'] >= 25
```

### 예 2: Tracer 혼합 longitudinal

같은 subject가 여러 시점에 다른 트레이서로 측정된 경우:

```python
longi = (centiloid
         .sort_values(['subject_id', 'day'])
         .assign(centiloid=lambda d: d['Centiloid_fSUVR_TOT_CORTMEAN']))
# tracer 컬럼 보존하여 trajectory 시각화 시 색깔 구분 가능
```

> Knight ADRC는 PIB → AV45 전환 시기에 일부 subject가 **두 트레이서 모두**로 측정되었다. Cross-validation에 활용 가능.

### 예 3: PUP raw data 조회

PET NIfTI 원본은 `oasis_file_list.csv`의 SEQ ∈ {AV45, PIB, AV1451, FDG} 행에서 PATH 컬럼으로 조회 가능. 자세한 내용은 [`file_index.md`](file_index.md).

---

## 9. 알려진 한계

1. **AV45 fBP NaN**: Static acquisition이므로 dynamic 분석 불가. fSUVR만 사용.
2. **PET_json blank tracer 550행 (25%)**: BIDS sidecar에서 TracerName 누락. `oasis_file_list.csv`의 SEQ로 fallback.
3. **Manufacturer 대소문자 혼재** (`Siemens` vs `SIEMENS`): 분석 시 `.str.upper()`.
4. **`accesssion` 컬럼명 오타**: 's' 3개. 정상 철자로 변경 시 코드 호환성 깨짐 주의.
5. **Knight ADRC calibration 의존**: ADNI 등 외부 데이터셋의 centiloid와 직접 비교 시 cross-calibration 검증 필요.
6. **AV1451 centiloid 없음**: tau는 centiloid 정의 없음. AV1451 정량은 NIfTI를 별도 파이프라인(예: FreeSurfer + 자체 SUVR)으로 처리.

---

## 참고 문헌

- **OASIS-3 paper**: LaMontagne PJ, et al. *OASIS-3: Longitudinal Neuroimaging, Clinical, and Cognitive Dataset for Normal Aging and Alzheimer Disease*. medRxiv 2019. [doi:10.1101/2019.12.13.19014902](https://doi.org/10.1101/2019.12.13.19014902)
- **Centiloid 표준**: Klunk WE, et al. *The Centiloid Project: standardizing quantitative amyloid plaque estimation by PET*. Alzheimers Dement 2015;11(1):1-15. [doi:10.1016/j.jalz.2014.07.003](https://doi.org/10.1016/j.jalz.2014.07.003)
- **PUP**: Su Y, et al. *Utilizing the Centiloid scale in cross-sectional and longitudinal PiB PET studies*. NeuroImage Clin 2018;19:406-416. [PMC6051499](https://pmc.ncbi.nlm.nih.gov/articles/PMC6051499/) | 코드: [github.com/ysu001/PUP](https://github.com/ysu001/PUP)
- **PIB**: Klunk WE, et al. *Imaging brain amyloid in Alzheimer's disease with Pittsburgh Compound-B*. Ann Neurol 2004;55(3):306-319.
- **AV45 (Florbetapir)**: Wong DF, et al. *In vivo imaging of amyloid deposition in Alzheimer disease using the radioligand 18F-AV-45 (florbetapir)*. J Nucl Med 2010;51(6):913-920.
- **AV1451 (Flortaucipir)**: Wang L, et al. *Evaluation of Tau Imaging in Staging Alzheimer Disease and Revealing Interactions Between β-Amyloid and Tauopathy*. JAMA Neurol 2016;73(9):1070-1077.

## 참고 문서

| 문서 | 내용 |
|------|------|
| [`data_catalog.md`](data_catalog.md) | 24 CSV 마스터 인벤토리 |
| [`protocol.md`](protocol.md) | 연구 배경, 트레이서 사용 방침 |
| [`file_index.md`](file_index.md) | NIfTI 경로, BIDS 명명 규칙 |
| [`join_relationships.md`](join_relationships.md) | PET-clinical 조인 패턴 |
