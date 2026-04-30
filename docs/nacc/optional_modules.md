# NACC 옵셔널 모듈 통합 사전

NACC core UDS 폼 (A1–D2) 외의 옵셔널 / 보조 모듈을 한 곳에 정리. 모듈별 NFS 파일 위치, 행/열 수, 컬럼 그룹, 권위 RDD PDF 페이지를 cross-link 한다.

대상 모듈:
1. **FTLD3** (Frontotemporal Lobar Degeneration 모듈) — FVP / IVP
2. **LBD3.1** (Lewy Body Dementia 모듈) — FVP / IVP
3. **CSF biomarker** (EE2, episodic enrichment) — fcsf 파일
4. **NACC SCAN MRI** — mriqc / mrisbm
5. **NACC SCAN PET** — Amyloid (GAAIN + NPDKA), Tau, FDG, QC
6. **ADSP-PHC December 2024** — 8 도메인 (PET / T1 / FLAIR / DTI / Vascular / Biomarker / Neuropath / Cognition)
7. **Genetics (APOE)** — `NACCAPOE` 인코딩 표 + workflow

> 각 모듈의 컬럼 정의는 NACC 가 PDF DED (Data Element Definition) 로 배포한다. 본 docs는 모듈 입구를 정리하고, 컬럼 단위 사전은 RDD PDF 를 직접 참조한다.

---

## 1. FTLD3 모듈 (FTD / PPA / CBS 의심 시)

### 1.1 운영 모델

NACC FTLD module v3. Initial Visit Packet (IVP) 와 Follow-up Visit Packet (FVP) 가 양식이 다르다.

| Packet | RDD PDF | 페이지 수 (대략) |
|--------|---------|------|
| IVP (Initial) | `DEMO/Data_Directory/ftld3-ivp-ded.pdf` | 324 KB |
| FVP (Follow-up) | `DEMO/Data_Directory/ftld3-fvp-ded.pdf` | 325 KB |

### 1.2 데이터 위치

FTLD3 변수는 별도 CSV가 아닌 **`investigator_ftldlbd_nacc71.csv`** (1,936 cols) 안에 통합되어 있다. FTD 의심 visit 만 채워지므로 대부분 행은 결측. 분석 시:

```python
# FTLD3 변수가 채워진 visit 만 필터링
ftld_visits = df[df['FTDPPA'].notna() | df['FTDIDIAG'].notna()]
```

### 1.3 컬럼 그룹 (대표)

| 그룹 | 컬럼 prefix / 예시 | RDD 페이지 |
|------|-------------------|----------|
| 임상 표현형 (clinical phenotype) | `FTDIDIAG`, `FTDPPA`, `FTDBVCLIN`, `FTDBVPRIM`, `FTDPPAEEC`, `FTDPPAESM`, `FTDPPAESC` | IVP/FVP 1–4p |
| 행동 변화 (behavioral) | `FTDBA*` (brake, axiocity, ...), `FTDDISIN`, `FTDAPATHY` | IVP/FVP 4–8p |
| 언어 평가 (language) | `FTDLBOSCT`, `FTDSPEECH`, `FTDTLANGCMP`, `FTDLBOST` | IVP/FVP 8–12p |
| 운동 (motor) | `FTDMOTOR`, `FTDPSP*`, `FTDCBS*` | IVP/FVP 12–16p |
| 인지 / cognitive | `FTDCWDLI`, `FTDCWDREP`, `FTDCWDREL` | IVP/FVP 16–20p |
| 가족력 / 유전 | `FTDFAMHX`, `FTDFAMNUM`, `FTDC9ORF`, `FTDMAPT`, `FTDGRN` | IVP only |

> 자세한 컬럼 단위 코딩은 RDD PDF 의 form-by-form 표 참조. FTLD3 변수는 모두 NACC missing-code 컨벤션 (`88`/`888`/`9`/`99` 등) 을 따른다.

---

## 2. LBD3.1 모듈 (DLB / PD-D / RBD 의심 시)

### 2.1 운영 모델

NACC LBD module v3.1. FTLD 와 같은 IVP / FVP 분리.

| Packet | RDD PDF |
|--------|---------|
| IVP | `DEMO/Data_Directory/lbd3_1-ivp-ded.pdf` (340 KB) |
| FVP | `DEMO/Data_Directory/lbd3_1-fvp-ded.pdf` (360 KB) |

### 2.2 데이터 위치

LBD3.1 변수도 `investigator_ftldlbd_nacc71.csv` 안에 통합. DLB / PD-dementia 의심 visit 만 채움.

### 2.3 컬럼 그룹 (대표)

| 그룹 | 컬럼 prefix / 예시 |
|------|-------------------|
| 임상 진단 | `LBDIDIAG`, `LBDPRINS`, `LBDOTHIS`, `LBDFAMHX` |
| 핵심 임상 특징 (4 cardinal) | `LBDFLU` (cognitive fluctuation), `LBDVH` (visual hallucination), `LBDPARK` (parkinsonism), `LBDRBD` (REM sleep behavior disorder) |
| 운동 (parkinsonian motor) | `LBDMOTBR*`, `LBDMOTLT*`, `LBDMOTRS*`, `LBDMOTGT*` (각 motor sign 의 onset/severity) |
| 자율신경 (autonomic) | `LBDAUTOH` (orthostatic), `LBDAUTU` (urinary), `LBDAUTC` (constipation), `LBDAUTSE`, `LBDAUTSF` |
| 정신 증상 | `LBDDEL`, `LBDDEP`, `LBDANX`, `LBDAPA` |
| 영상 / biomarker | `LBDDATSCAN`, `LBDPSGCONF` (polysomnography), `LBDMIBG` (cardiac MIBG scan) |

---

## 3. CSF biomarker (EE2 episodic enrichment)

### 3.1 데이터 위치 + 사이즈

| Tier | 파일 | 행 | 열 |
|------|------|-----|-----|
| Investigator | `DEMO/Non_Commercial_Data/investigator_fcsf_nacc71.csv` | 3,052 | 23 |
| Commercial | `DEMO/Commercial_Data/commercial_fcsf_nacc71.csv` | 2,770 | 23 |

RDD: `DEMO/Data_Directory/biomarker-ee2-csf-ded.pdf` (157 KB).

### 3.2 컬럼 (23개 — 전체)

```
NACCADC, NACCID                                # bookkeeping (fcsf 만 ADC가 먼저)
CSFABETA, CSFPTAU, CSFTTAU                     # 측정값 (pg/mL)
CSFLPMO, CSFLPDY, CSFLPYR                      # 요추천자 (LP) 일자
CSFABMO, CSFABDY, CSFABYR, CSFABMD, CSFABMDX   # Aβ42 측정 일자 + 방법
CSFPTMO, CSFPTDY, CSFPTYR, CSFPTMD, CSFPTMDX   # p-tau 측정 일자 + 방법
CSFTTMO, CSFTTDY, CSFTTYR, CSFTTMD, CSFTTMDX   # t-tau 측정 일자 + 방법
```

| 그룹 | 컬럼 | 의미 |
|------|------|------|
| ID | `NACCADC`, `NACCID` | (fcsf 만 ADC 먼저!) |
| 측정값 | `CSFABETA`, `CSFPTAU`, `CSFTTAU` | Aβ42, p-tau, t-tau (pg/mL) |
| LP 일자 | `CSFLPMO`, `CSFLPDY`, `CSFLPYR` | 요추천자 일 |
| 분석 일자 (각 마커별) | `CSF{AB,PT,TT}{MO,DY,YR}` | 측정 일 |
| 분석 방법 (각 마커별) | `CSF{AB,PT,TT}MD` | 1=ELISA, 2=Luminex, 3=Lumipulse, ... |
| 분석 방법 free text | `CSF{AB,PT,TT}MDX` | 방법 사용자 입력 |

> **fcsf 파일은 컬럼 순서가 `(NACCADC, NACCID)` 로 다른 시리즈와 반대.** 위치 의존 코드 작성 금지 — 컬럼명으로 join.

### 3.3 분석 패턴

```python
csf = pd.read_csv("investigator_fcsf_nacc71.csv")

# Aβ42/p-tau ratio (AD biomarker)
csf['ab_ptau_ratio'] = csf['CSFABETA'] / csf['CSFPTAU']

# AD-positive (NIA-AA criteria, 다양한 cutoff 사용)
# 예: Aβ42 < 600 + p-tau > 60 (Lumipulse Innogenetics 표준)
ad_pos = (csf['CSFABETA'] < 600) & (csf['CSFPTAU'] > 60)
```

> CSF 분석 방법 (`CSF*MD`) 별 cutoff 가 다르다. 연구별 표준 cutoff 적용 시 method 일관성 확인.

---

## 4. NACC SCAN MRI

### 4.1 데이터 위치 (SCAN 파이프라인)

| 파일 | 행 | 열 | 내용 |
|------|------|------|------|
| `investigator_scan_mri_nacc71/investigator_scan_mriqc_nacc71.csv` | 22,855 | 38 | 스캔/시리즈 단위 protocol/QC flag |
| `investigator_scan_mri_nacc71/investigator_scan_mrisbm_nacc71.csv` | 5,330 | 249 | Surface-Based Morphometry (FreeSurfer-style) |

RDD: `DEMO/Data_Directory/SCAN-MRI-Imaging-RDD.pdf` (572 KB).

### 4.2 mriqc 컬럼 그룹

```
NACCID, NACCADC, STUDYDATE, SERIESTIME, STUDYVISITCODE, SERIESNUMBER,
SERIESTYPE, STUDYQC, STUDYQCCOMMENT, MRIPROTOCOLPHASE, STUDYPROTOCOL,
STUDYPROTOCOLCOMMENT, STUDYRESCANREQUESTED, SERIESDESCRIPTION,
SERIESQC, SERIESQCREASONS, SERIESPROTOCOL, SERIESPROTOCOLCOMMENT,
SERIESCHOSEN, SERIALEXAM, ...
```

각 study/series 단위 1행. `STUDYVISITCODE` 로 임상 visit 매칭 (NACC SCAN 자체 코드 — UDS NACCVNUM 과 별개).

### 4.3 mrisbm 컬럼 그룹

249 cols. FreeSurfer DKT atlas 기반 cortical thickness + volume:
- bilateral cortical thickness (35 ROI)
- bilateral cortical volume (35 ROI)
- bilateral subcortical volume (15 ROI)
- LH / RH 분리 컬럼
- volume normalization (eTIV 등)

자세한 컬럼 정의는 `SCAN-MRI-Imaging-RDD.pdf` 참조.

---

## 5. NACC SCAN PET

### 5.1 데이터 위치

| 파일 | 행 | 열 | tracer/모달리티 |
|------|------|------|----------------|
| `investigator_scan_pet_nacc71/investigator_scan_petqc_nacc71.csv` | 5,103 | 11 | PET QC (tracer 무관) |
| `.../investigator_scan_amyloidpetgaain_nacc71.csv` | 2,808 | 15 | Amyloid composite (GAAIN + Centiloid) |
| `.../investigator_scan_amyloidpetnpdka_nacc71.csv` | 2,808 | 172 | Amyloid per-region (NPDKA) |
| `.../investigator_scan_taupetnpdka_nacc71.csv` | 1,815 | 171 | Tau per-region |
| `.../investigator_scan_fdgpetnpdka_nacc71.csv` | 485 | 169 | FDG per-region |

RDD: NPDKA / GAAIN 표준은 NACC SCAN 공식 페이지 (https://scan.naccdata.org/).

### 5.2 amyloidpetgaain 컬럼 (15)

```
NACCID, NACCADC, LONIUID, SCANDATE, PROCESSDATE, TRACER, TRACER_SUVR_WARNING,
ACQUISITION_TIME, AMYLOID_STATUS, CENTILOIDS, GAAIN_SUMMARY_SUVR,
GAAIN_WHOLECEREBELLUM_SUVR, GAAIN_COMPOSITE_REF_SUVR, GAAIN_CEREBELLUM_CORTEX,
NPDKA_ERODED_SUBCORTICALWM_SUVR
```

| 컬럼 | 의미 |
|------|------|
| `LONIUID` | LONI 영상 unique ID (NeuroXT가 LONI 검색에 사용) |
| `SCANDATE` | PET 촬영일 |
| `PROCESSDATE` | 정량화 처리일 |
| `TRACER` | `florbetapir` (AV45), `florbetaben` (FBB), `pittsburgh compound b` (PIB), `flutemetamol` |
| `AMYLOID_STATUS` | NACC SCAN 표준 양성 분류 |
| `CENTILOIDS` | Centiloid 값 (GAAIN 표준 0–100+) |
| `GAAIN_*` | GAAIN composite SUVR (4종 reference region) |

### 5.3 amyloidpetnpdka 컬럼 (172) / taupetnpdka (171) / fdgpetnpdka (169)

DKT atlas 기반 per-region SUVR. 본 docs `merged.csv` 절 ([`merged_csv.md` §2.7](merged_csv.md#27-amyloid-pet-175-cols-46221--investigator_scan_petamyloidpetnpdka--amyloidpetgaain-source)) 의 Amyloid PET 175 cols 와 동일 layout (단 행 수가 적음 — `merged.csv` 가 visit-level inner-join이므로 Amyloid PET 가 측정된 visit 만 175 col 채움).

> NPDKA = NACC PET Data analysis pipeline (GAAIN 외의 reference region 사용). NPDKA `ERODED_SUBCORTICALWM_SUVR` 가 deep WM reference 의 표준.

### 5.4 분석 패턴

```python
amy = pd.read_csv("investigator_scan_amyloidpetnpdka_nacc71.csv")

# DKT atlas 33 cortical SUVR 평균
ctx_cols = [c for c in amy.columns if c.startswith('CTX_') and c.endswith('_SUVR')
            and 'LH_' not in c and 'RH_' not in c]
amy['cortical_mean_suvr'] = amy[ctx_cols].mean(axis=1)
```

---

## 6. ADSP-PHC December 2024

### 6.1 운영 모델

ADSP-PHC = Alzheimer's Disease Sequencing Project — Phenotype Harmonization Consortium. NACC 와 별도 cadence 로 release; December 2024 release 가 v71 freeze 와 함께 사용된다.

| Tier | 폴더 |
|------|------|
| Investigator | `DEMO/Non_Commercial_Data/ADSP-PHC-122024-investigator/ADSP-PHC-122024-investigator/` (double-nested) |
| Commercial | `DEMO/Commercial_Data/ADSP-PHC-122024-commercial/ADSP-PHC-122024-commercial/` |

### 6.2 8 도메인 + Return-to-Cohort manifest

| 도메인 | 폴더 | 핵심 CSV (investigator) | 사전 |
|--------|------|------------------------|------|
| **Imaging_PET** | `Imaging_PET/` | `NACC_ADSP_PHC_Amyloid_Simple_2024.csv`, `NACC_ADSP_PHC_Amyloid_Detailed_2024.csv`, `NACC_ADSP_PHC_Tau_Simple_2024.csv`, `NACC_ADSP_PHC_Tau_Detailed_2024.csv` | `*_DD_2024.xlsx` |
| **Imaging_T1** | `Imaging_T1/` | `NACC_ADSP_PHC_T1_Freesurfer_2024.csv`, `NACC_ADSP_PHC_T1_MUSE_2024.xlsx` | `*_DD_2024.xlsx` |
| **Imaging_FLAIR** | `Imaging_FLAIR/` | WMH segmentation | (디렉토리 inspection 필요) |
| **Imaging_DTI** | `Imaging_DTI/` | DTI metric (FA, MD) | |
| **Vascular_Risk** | `Vascular_Risk/` | `NACC_ADSP_PHC_VascularRisk_2024.csv` | `NACC_ADSP_PHC_VascularRisk_DD_2024.xlsx` |
| **Biomarker** | `Biomarker/` | `NACC_ADSP_PHC_Biomarker_2024.csv` | (DD 미발견, ReadMe 참조) |
| **Neuropath** | `Neuropath/` | 부검 / 신경병리 harmonized | |
| **Cognition** | `Cognition/` | ADSP-PHC harmonized cognition score (PHC-MEM, PHC-EXEC 등) | |
| Manifest | (root) | `NACC_ADSP-PHC_Dec2024_Return-to-Cohort.xlsx` | ADSP↔NACC subject 연동 |

각 도메인별 ReadMe `.docx` 파일이 release notes 역할.

### 6.3 Subject 키

ADSP-PHC 파일들은 NACC 와 동일 `NACCID` 를 키로 사용 (ADSP 내부 ID 와 매핑은 `Return-to-Cohort.xlsx` 에서 처리). 따라서 NACC merged.csv ↔ ADSP-PHC PET 간 join 가능.

```python
adsp_amyloid = pd.read_excel("Return-to-Cohort.xlsx")
phc_amyloid_simple = pd.read_csv("NACC_ADSP_PHC_Amyloid_Simple_2024.csv")

# NACC 와 join
nacc_phc = merged.merge(phc_amyloid_simple, on='NACCID', how='left')
```

> ADSP-PHC 의 PHC- 시작 변수 (예: `PHC_MEM`, `PHC_EXEC`, `PHC_LANG`) 는 **harmonized phenotype** 으로, 다른 코호트 (ADNI, AIBL, HABS-HD, DOD-ADNI 등) 와 **같은 정의** 를 사용. cross-cohort 메타분석 가능.

---

## 7. Genetics (APOE)

NACC core APOE 데이터는 별도 CSV 가 아닌 **`investigator_ftldlbd_nacc71.csv` 에 통합** 되어 있다. NeuroXT-built `merged.csv` 는 ε4 count (`NACCNE4S`) 만 가져왔으므로, 유전자형 pair 가 필요하면 source 파일에서 `NACCAPOE` 컬럼을 추가 join 해야 한다.

### 7.1 데이터 위치

| 컬럼 | 위치 | dtype | 의미 |
|------|------|-------|------|
| `NACCAPOE` | `investigator_ftldlbd_nacc71.csv` col 815 | integer | APOE 유전자형 pair (코드) |
| `NACCNE4S` | `investigator_ftldlbd_nacc71.csv` col 816 + `merged.csv` col 38 | integer | ε4 allele 수 (0/1/2/9) |

RDD: `DEMO/Data_Directory/rdd-genetic-data.pdf` (123 KB) — NACC genetic flag 정의.

### 7.2 `NACCAPOE` 인코딩 (UDS-3 RDD 표준 + 실측 분포)

| Code | 유전자형 | 행 수 (v71 freeze) | 비율 |
|------|---------|-------------------|------|
| `1` | **ε3 / ε3** | 89,208 | ~43% |
| `2` | **ε3 / ε4** | 48,394 | ~24% |
| `3` | **ε3 / ε2** | 16,069 | ~8% |
| `4` | **ε4 / ε4** | 9,591 | ~5% |
| `5` | **ε4 / ε2** | 4,276 | ~2% |
| `6` | **ε2 / ε2** | 693 | ~0.3% |
| `9` | Missing / unknown | 25,642 | ~12% |
| `88` | Not assessed | 6,773 | ~3% |
| `0` | Not done (visit-specific code) | 4,391 | ~2% |
| `NG#####` (예: `NG00067`, `NG00079`, `NG00139`) | 비표준 (study-specific genotyping run code) | <1% 합계 | minor |

> `NACCNE4S` (ε4 count) 와 일관성 검증:
> - APOE=1 (ε3/ε3) → NE4S=0 ✓
> - APOE=2 (ε3/ε4), 5 (ε4/ε2) → NE4S=1 ✓
> - APOE=4 (ε4/ε4) → NE4S=2 ✓
> - APOE=9/88/0 → NE4S 도 9 (missing) 가 일반적

### 7.3 visit-level 데이터 변동 quirk

APOE 는 유전적으로 정적이지만, NACC 데이터에서는 **같은 subject 가 visit 마다 다른 NACCAPOE 값을 가질 수 있다** (실측 예: NACC002909 v1=2, v2=2, v3=88; NACC016631 v1=2, v2=0). 이는 visit 별 데이터 수집 status 차이 — 일부 visit 에서 APOE 가 "not assessed" 처리됨.

분석 권고:
```python
# subject 별 가장 정보량 많은 NACCAPOE 값 (9/88/0 missing 우선 제외)
import pandas as pd
ftldlbd = pd.read_csv("investigator_ftldlbd_nacc71.csv",
                     usecols=['NACCID', 'NACCVNUM', 'NACCAPOE', 'NACCNE4S'])

# APOE 는 정적 → subject 단위 forward-fill
valid = ftldlbd[~ftldlbd['NACCAPOE'].isin([0, 9, 88])].copy()
subject_apoe = valid.groupby('NACCID')['NACCAPOE'].first()
```

### 7.4 ADSP-PHC genetics

ADSP-PHC December 2024 release 의 `Biomarker/NACC_ADSP_PHC_Biomarker_2024.csv` 는 **CSF 바이오마커 (AB42, Tau, pTau, AT_class, PHC_*) 만** 다루며, APOE 유전자형은 포함하지 않는다. 별도의 ADSP-PHC genetic data 파일은 v71 freeze 의 ADSP-PHC December 2024 release 에 미동봉 — APOE 유전자형은 NACC core 의 `NACCAPOE` 가 유일 source.

> ADSP-PHC sequencing data (WGS / GWAS 등) 는 ADSP 별도 portal (NIAGADS) 에서 신청 — 본 NACC freeze 와 별도 access.

### 7.5 Workflow 권장

| 분석 목적 | 사용 데이터 |
|----------|------------|
| ε4 dosage (가장 흔한 분석) | `merged.csv` 의 `NACCNE4S` (이미 join 되어 있음) |
| ε4 carrier vs non-carrier | `NACCNE4S > 0` |
| 유전자형 pair (예: ε3/ε4 vs ε4/ε4 분리) | `investigator_ftldlbd_nacc71.csv` 의 `NACCAPOE` 추가 join |
| ε2 보호 효과 분석 | `NACCAPOE` ∈ {3, 5, 6} (ε2 carrier) |
| Cross-cohort APOE 메타분석 | NACC `NACCAPOE` 정수 → 다른 코호트 인코딩 (KBASE `E3/3`, A4 `e3/e3`, OASIS3 `33`, ADNI `APGEN1+APGEN2`) 매핑 |

```python
# NACCAPOE 정수 → 표준 문자열 변환
NACC_APOE_MAP = {
    1: 'e3/e3', 2: 'e3/e4', 3: 'e2/e3',
    4: 'e4/e4', 5: 'e2/e4', 6: 'e2/e2',
}
df['APOE_pair'] = df['NACCAPOE'].map(NACC_APOE_MAP)  # missing/unknown → NaN
```

---

## 8. 모듈 결측 패턴 (요약)

| 모듈 | 채움 visit 비율 (대략) | 채움 조건 |
|------|----------------------|----------|
| FTLD3 | < 5% | FTD 의심 시만 |
| LBD3.1 | < 5% | DLB 의심 시만 |
| CSF (fcsf) | ~1.5% | LP 시행한 visit |
| SCAN MRI (mriqc) | ~11% | NACC SCAN MRI 제출 visit |
| SCAN MRI (mrisbm) | ~2.6% | mrisbm 정량화 완료 visit |
| SCAN Amyloid PET | ~1.4% | Amyloid PET 제출 visit |
| SCAN Tau PET | ~0.9% | Tau PET 제출 visit |
| SCAN FDG PET | ~0.2% | FDG PET 제출 visit |
| ADSP-PHC | NACC 의 일부 subset | DNA 동의 + 시퀀싱 / harmonization 완료 subject |
| Genetics (NACCAPOE) | ~83% (informative) | DNA 동의 + 유전형 분석 완료 visit. ε3/ε3 가장 흔함 (43%). 정적 변수 → subject-level forward-fill 권장 |

---

## Known limitations & quirks

1. **FTLD3 / LBD3.1 변수는 별도 CSV 가 아닌 `investigator_ftldlbd_nacc71.csv` 안에 통합.** 의외의 위치이므로 grep 으로 변수 위치 확인.
2. **fcsf 파일의 컬럼 순서는 `(NACCADC, NACCID)` 로 반대.** 위치 의존 코드 금지.
3. **SCAN MRI/PET 의 visit 매칭 키는 NACCVNUM 이 아닌 SCANDATE.** 임상 ↔ 영상 매칭은 `(NACCID, SCANDATE ↔ VISITDATE)` ±윈도우.
4. **ADSP-PHC release 는 별도 cadence.** 다음 release 가 NACC freeze 와 시간차로 들어올 수 있음 (12-2024 release 가 v71 = 2026-04 freeze 와 함께 쓰임).
5. **ADSP-PHC 폴더는 double-nested.** `ADSP-PHC-122024-investigator/ADSP-PHC-122024-investigator/...` — release tarball 그대로.
6. **Tier별 SCAN 파일 행 수가 거의 같음** — Commercial 동의자 대부분이 SCAN 참여. tier 차이가 의미 있는 모듈은 fcsf / ftldlbd / mri 정도.
7. **NACC SCAN 변수 정의는 NACC SCAN 공식 페이지 의존.** RDD PDF 외에 https://scan.naccdata.org/ 에서 추가 변수 정의 / 처리 파이프라인 문서 확인.
8. **`NACCAPOE` 가 visit 마다 변동 가능 (data quality artifact).** 같은 subject 의 다른 visit 에서 NACCAPOE=2 → NACCAPOE=88 같은 변동 관찰. APOE 는 정적 → subject-level forward-fill / 정보량 많은 값 우선 권장.
9. **`NACCAPOE` 코드 `0` 과 `NG#####` 는 비표준.** UDS-3 RDD 의 표준 코드는 1–6, 9, 88. `0` 과 `NG`-prefixed 코드는 v71 freeze 에서 관찰되는 study-specific extension — 분석 시 missing 으로 처리 권장.

> 검증일 2026-05-01 (freeze v71)
