# OASIS3 연구 프로토콜 & 데이터 참조

## 1. 연구 개요

### OASIS-3 (Open Access Series of Imaging Studies, Release 3)

- **운영기관**: WUSTL Knight ADRC (Knight Alzheimer Disease Research Center, Washington University in St. Louis)
- **공개 형식**: 공개 데이터셋 (Data Use Agreement 동의 후 다운로드, [oasis-brains.org](https://sites.wustl.edu/oasisbrains/home/oasis-3/))
- **수집 기간**: WUSTL Knight ADRC의 다중 진행 연구에서 ~30년에 걸쳐 수집된 데이터를 retrospective 통합
- **참가자**: 1,378명 (cognitively normal 755명 + cognitive decline 622명)
- **연령 범위**: 42 ~ 95세
- **DOI**: [doi:10.1101/2019.12.13.19014902](https://doi.org/10.1101/2019.12.13.19014902) (LaMontagne et al., medRxiv 2019)

### OASIS 시리즈 비교

| 릴리스 | 발표 | 디자인 | N | 모달리티 |
|--------|------|--------|---|----------|
| OASIS-1 | Marcus 2007 | Cross-sectional | 416 | T1 only |
| OASIS-2 | Marcus 2010 | Longitudinal MRI | 150 | T1 only (longitudinal) |
| **OASIS-3** | LaMontagne 2019/2024 | **Longitudinal multi-modal** | **1,378** | **MRI + PET + clinical/cognitive** |
| OASIS-4 | LaMontagne 2024 | Clinical phenotyping | 663 | Clinical assessment 중심 |

---

## 2. 코호트 구조

OASIS3는 RCT가 아니므로 amyloid+/- 같은 무작위 배정 그룹은 없다. 대신 임상 진단(`OASIS3_UDSb4_cdr.csv`의 `dx1` 또는 `OASIS3_UDSd1_diagnoses.csv`의 `NORMCOG`/`DEMENTED`/`MCI*` flags)으로 그룹을 정의한다.

OASIS3_UDSb4_cdr.csv `dx1` 빈도 (실측):

| 진단 | 행 수 | 비고 |
|------|-------|------|
| Cognitively normal | 6,401 | 가장 많음 — longitudinal control |
| AD Dementia | 1,145 | NIA-AA criteria 또는 NINCDS-ADRDA |
| uncertain dementia | 475 | 임상의 미확정 |
| Unc: ques. Impairment | 80 | Questionable impairment |
| AD dem w/depresss | 71 | AD + 우울 동반 |
| DLBD | 49 | Dementia with Lewy Bodies |
| (그 외 free-text 라벨 다수) | — | 자세한 매핑은 [`OASIS3_uds_forms.md`](OASIS3_uds_forms.md) D1/B4 섹션 참조 |

> **분석 권장**: 진단 그룹화는 `dx1`의 free-text 매핑보다 D1 폼의 binary flag 컬럼(`NORMCOG`, `DEMENTED`, `PROBAD`, `MCIAMEM` 등)을 사용하는 편이 안정적이다. UDS v3에서는 `amndem`, `pca`, `lbdsyn`, `ftdsyn` 같은 syndrome flag도 추가됨.

---

## 3. 영상 프로토콜

### MRI (1.5T 및 3T 혼재)

OASIS3는 30년에 걸친 retrospective 통합이므로 스캐너/시퀀스가 단일하지 않다. `OASIS3_PET_json.csv` 또는 BIDS JSON sidecar를 통해 스캔별 파라미터 확인 필수.

| Modality | NII Folder | Description | OASIS_file_list SEQ token |
|----------|-----------|-------------|---------------------------|
| T1w | `T1w/` | MPRAGE 또는 다른 T1 weighted 구조 영상 | `T1w` (4,116 files) |
| T2w | `T2w/` | T2 weighted 구조 영상 | `T2w` (4,051) |
| FLAIR | `FLAIR/` | Fluid-attenuated inversion recovery | `FLAIR` (1,381) |
| ASL | `asl/` 또는 `pasl/` | Arterial Spin Labeling perfusion | `asl` (1,337), `pasl` (223) |
| BOLD | `bold/` | Resting-state functional MRI | `bold` (5,114) |
| DWI | `dwi/` | Diffusion-weighted | `dwi` (12,915) |
| SWI | `swi/` | Susceptibility-weighted (microbleeds) | `swi` (1,229) |
| T2* | `T2star/` | T2* GRE | `T2star` (2,350) |
| GRE | `GRE/` | Gradient echo | `GRE` (1,326) |
| Time-of-Flight Angio | `angio/` | TOF MR Angiography | `angio` (896) |
| Fieldmap | `fieldmap/` | B0 fieldmap (DWI/BOLD distortion correction용) | `fieldmap` (3,819) |
| MIP | `minIP/` | Minimum intensity projection (SWI 후처리) | `minIP` (1,231) |

### PET

| Tracer | Folder | Target | T½ | OASIS_file_list SEQ | OASIS3_amyloid_centiloid 행 수 |
|--------|--------|--------|----|--------------------|---------------------------------|
| **PIB** ([11C]Pittsburgh Compound B) | `PIB/` | Amyloid-β | 20 min | `PIB` (1,248) | 1,178 |
| **AV45** (Florbetapir, [18F]) | `AV45/` | Amyloid-β | 110 min | `AV45` (780) | 715 |
| **AV1451** (Flortaucipir, [18F]T807) | `AV1451/` | Tau (PHF) | 110 min | `AV1451` (763) | — (centiloid는 amyloid only) |
| **FDG** ([18F]Fluorodeoxyglucose) | `FDG/` | Glucose metabolism | 110 min | `FDG` (127) | — |

> AV1451은 OASIS-3 본 데이터셋의 sub-project (OASIS-3_AV1451)으로 별도 공개. NIfTI는 `oasis_file_list.csv`에 포함되지만 centiloid CSV에는 없음 (centiloid는 amyloid 전용).

처리 파이프라인은 **PUP (PET Unified Pipeline, Su et al.)**: scanner resolution harmonization → inter-frame motion correction → PET-MR registration → regional time-activity curves → regional spread function (RSF) 기반 partial volume correction → SUVR/binding potential. 자세한 내용은 [`OASIS3_pet_imaging.md`](OASIS3_pet_imaging.md).

---

## 4. Visit/Session 구조

### `days_to_visit` 시스템

OASIS3는 **고정된 visit code (V1, V2, ...) 가 없다**. 대신 모든 시간을 **피험자별 첫 방문 = `d0000` 기준 경과일**로 표현한다.

- **모든 임상/영상 데이터의 시간축**: `days_to_visit` 정수 (zero-padded 4자리 문자열로 세션 라벨에 등장)
- **음수 가능 여부**: 일반적으로 0 이상. 단, `oasis3.csv`의 `*_diff` 컬럼은 음수 가능 (영상 visit이 임상 ref보다 이전인 경우)
- **De-identification**: 절대 날짜 없음. 90+ 연령은 ceiling 처리되어 `AgeatEntry` 등에서 90으로 표시될 수 있음.

### `OASIS_session_label` Grammar

```
OAS3{0001-1378}_{FORM}_d{0000-9999}
```

예:
- `OAS30001_UDSb4_d0339` — subject 1, B4(CDR) form, day 339
- `OAS30001_AV45_d2430` — subject 1, AV45 amyloid PET scan, day 2430

자세한 grammar(특히 `USDa3`/`USDb3` 오타 등)는 [`OASIS3_session_label_reference.md`](OASIS3_session_label_reference.md).

### Multi-form same-day 묶기

같은 `(OASISID, days_to_visit)`인 폼들은 동일 visit에서 수집된 것으로 간주.

```
OAS30001_UDSa1_d0000  ┐
OAS30001_UDSa5_d0000  ├─ 동일 visit (Initial Visit Packet)
OAS30001_UDSb4_d0000  │
OAS30001_UDSc1_d0000  ┘
```

### 영상 ↔ 임상 visit 매칭

영상은 임상 visit과 같은 날 촬영되지 않을 수 있다 (보통 ±몇 주 ~ 몇 달). `oasis3.csv`의 `*_diff` 컬럼은 **`*_diff = refdate − scan_date`** (실측 검증: refdate=0, MR=129, MR_diff=−129 → −129 = 0 − 129):

```
ID         refdate  FDG  FDG_diff   AV45  AV45_diff  MR    MR_diff   PIB    PIB_diff
OAS30001   0        NA   NA         NA    NA         129   -129      NA     NA
OAS30001   339      NA   NA         NA    NA         NA    NA        423    -84
```

→ 음수 `*_diff` = 영상 스캔이 임상 ref 시점보다 **이후**에 촬영. 위 예에서 subject `OAS30001`은 임상 ref(`d0000`) 이후 129일 뒤(`d129`)에 MR이 있었고, 임상 ref(`d339`) 이후 84일 뒤(`d423`)에 PIB이 있었다.

---

## 5. NACC UDS 버전과 폼 변경

OASIS3 데이터는 ~30년에 걸쳐 수집되었으므로 **NACC UDS v1 → v2 → v3 전환**이 모두 포함되어 있다. 결과적으로 일부 컬럼은 특정 시점 이후에만 채워진다.

| UDS 버전 | 발효 | 주요 변경 |
|---------|------|-----------|
| **v1** | 2005~ | 초기 폼 |
| **v2** | 2008~ | C1 neuropsych battery 표준화 |
| **v3** | 2015~ | A4 form `a4`가 D/G로 분할 (`a4D` = drug codes, `a4G` = drug names), C1 → C2 (Craft Story 추가, MoCA 추가, 일부 검사 교체), D1에 syndrome flags(amndem, pca, lbdsyn, ftdsyn) 및 biomarker flags(amylpet, taupetad 등) 추가 |
| v4 | 2024~ | OASIS3에는 미포함 (수집 시기 외) |

**실용적 함의**:
- `OASIS3_UDSc1_cognitive_assessments.csv`(107 컬럼)는 v2 + v3 컬럼의 **union**. 같은 검사가 다른 컬럼명으로 들어갈 수 있음 (예: 즉시 회상 = `LOGIMEM` v2, `craftvrs` v3 추가).
- D1의 syndrome flags(amndem 등)는 v3 visit에서만 채워짐 → 초기 visit은 NaN.

---

## 6. De-identification 규칙

OASIS3는 HIPAA Safe Harbor에 준한 de-identification:

- **날짜**: 절대 날짜 없음. 모두 `days_to_visit` 정수 offset.
- **연령**: 90세 이상은 ceiling 처리 (관찰 가능한 최대값이 90). `AgeatEntry`/`AgeatDeath`에서 영향.
- **위치**: 사이트 정보 없음 (Knight ADRC 단일 사이트이므로 무의미).
- **Subject ID**: `OAS3{0001-1378}` 임의 일련번호.
- **연구 시작 기준**: 각 subject의 first visit이 `d0000`. **다른 subject의 d0000은 시간적으로 무관**.

---

## 7. 데이터 레이아웃 (NFS)

### NII 구조

```
/Volumes/nfs_storage/OASIS3/ORIG/NII/
    oasis_{batch_id}/                    # 예: oasis_1117
        {SUB_ID}/                        # 예: OAS31039
            d{####}/                     # 예: d1182
                {SEQ}/                   # 예: T1w, AV1451
                    sub_{SUB_ID}_ses_{visit_day}_{seq}_{...}.nii.gz
                    *.json (BIDS sidecar)
```

> `oasis_file_list.csv`의 PATH 컬럼은 **Windows 매핑 경로** (`Z:\1_combined\OASIS3\ORIG\NII\...`). macOS 마운트 시 `/Volumes/nfs_storage/OASIS3/ORIG/NII/...`로 변환 필요. 자세한 내용은 [`OASIS3_file_index.md`](OASIS3_file_index.md).

### 임상 메타데이터

```
/Volumes/nfs_storage/OASIS3/ORIG/DEMO/
    OASIS3_demographics.csv
    OASIS3_amyloid_centiloid.csv
    OASIS3_PET_*.csv
    OASIS3_UDS{a1, a2, a3, a4D, a4G, a5, b1-b9, c1, d1, d2}.csv
    oasis_file_list.csv
    oasis3.csv
```

전체 인벤토리는 [`OASIS3_data_catalog.md`](OASIS3_data_catalog.md).

---

## 8. ADNI / A4 vs OASIS3 주요 차이점

| | ADNI | A4/LEARN | **OASIS3** |
|---|------|----------|------------|
| 디자인 | Multi-cohort observational | RCT (A4) + observational (LEARN) | **Single-site retrospective compilation** |
| 사이트 | Multi-site | Multi-site (67) | **Single (WUSTL Knight ADRC)** |
| Visit 코딩 | bl/m06/m12/.../scmri | VISCODE 1-117, 701-705, 997-999 | **`days_to_visit` 정수 offset (d0000~d9999)** |
| 영상 형식 | DICOM | NIfTI (BIDS-like) | **NIfTI (BIDS)** |
| 임상 데이터 | ADNIMERGE 통합 | 51+ 개별 CSV | **24 CSV (UDS form 단위)** |
| 인지 검사 | 자체 protocol (ADAS-Cog 등) | 자체 protocol (PACC) | **NACC UDS standardized battery** |
| Tracer | FBP/FBB/FTP/FDG | FBP, FTP | **PIB/AV45/AV1451/FDG** |
| Subject ID | PTID (XXX_S_XXXX) | BID (B[1-9][0-9]{7}) | **OAS3{0001-1378}** |
| 진단 코드 | DX (1=CN/2=MCI/3=AD) | CDR=0 only (registration filter) | **D1 binary flag set + B4 dx1 free text** |

---

## 9. 참고 문헌

### 핵심 논문

- LaMontagne PJ, et al. *OASIS-3: Longitudinal Neuroimaging, Clinical, and Cognitive Dataset for Normal Aging and Alzheimer Disease*. medRxiv 2019. [doi:10.1101/2019.12.13.19014902](https://doi.org/10.1101/2019.12.13.19014902)
- Klunk WE, et al. *The Centiloid Project: standardizing quantitative amyloid plaque estimation by PET*. Alzheimers Dement 2015. [doi:10.1016/j.jalz.2014.07.003](https://doi.org/10.1016/j.jalz.2014.07.003)
- Su Y, et al. *Utilizing the Centiloid scale in cross-sectional and longitudinal PiB PET studies*. NeuroImage Clin 2018. [PMC6051499](https://pmc.ncbi.nlm.nih.gov/articles/PMC6051499/)
- Weintraub S, et al. *Version 3 of the National Alzheimer's Coordinating Center's Uniform Data Set*. Alzheimer Dis Assoc Disord 2018. NACC UDS v3 발표 논문.

### 공식 문서

- OASIS-3 공식: [https://sites.wustl.edu/oasisbrains/home/oasis-3/](https://sites.wustl.edu/oasisbrains/home/oasis-3/)
- NACC UDS-3 RDD: [https://files.alz.washington.edu/documentation/uds3-rdd.pdf](https://files.alz.washington.edu/documentation/uds3-rdd.pdf)
- NACC UDS-3 forms: [https://naccdata.org/data-collection/forms-documentation/uds-3](https://naccdata.org/data-collection/forms-documentation/uds-3)
- PUP 코드: [https://github.com/ysu001/PUP](https://github.com/ysu001/PUP)
