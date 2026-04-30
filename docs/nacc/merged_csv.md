# `merged.csv` 컬럼 사전 (NeuroXT-built working file)

`/Volumes/nfs_storage/NACC_NEW/ORIG/DEMO/merged.csv` 의 390 컬럼 사전. 

> **`merged.csv` 는 NACC 표준 배포가 아닌 NeuroXT-pre-built file** 이다. 205,909 행 × 390 열로, NACC v71 freeze 의 `Non_Commercial_Data/investigator_*.csv` 시리즈를 `(NACCID, NACCVNUM)` 단위로 inner-join 한 결과. 학술 연구 default 로 사용.

NACC 표준 분석 (reproducibility 추구) 시에는 `Non_Commercial_Data/investigator_ftldlbd_nacc71.csv` (1,936 cols) 를 직접 사용 권장.

---

## 1. 한 눈에 보기

| 항목 | 값 |
|------|---|
| 파일 경로 | `/Volumes/nfs_storage/NACC_NEW/ORIG/DEMO/merged.csv` |
| 크기 | 96 MB |
| 행 | 205,909 (visit-level, `(NACCID, NACCVNUM)` 단위) |
| 컬럼 | 390 |
| Source | `investigator_ftldlbd_nacc71.csv` (38) + `investigator_fcsf_nacc71.csv` (5) + `investigator_scan_pet/amyloidpetnpdka` (175) + `investigator_scan_pet/taupetnpdka` (169) + meta (3) |
| Subject 수 | 55,004 unique NACCID (추정, freeze 시점 차이로 변동 가능) |
| 동의 tier | **Investigator (Non_Commercial)** — 학술 전용. Commercial 협업에는 사용 불가 |

---

## 2. 컬럼 그룹 (390 cols)

### 2.1 NACC bookkeeping (8 cols, 1–8)

| # | 컬럼 | 의미 |
|---|------|------|
| 1 | `NACCID` | Subject ID (`NACC` + 6 digits) |
| 2 | `NACCADC` | ADRC 코드 |
| 3 | `PACKET` | Visit packet (`I`/`F`/`T`) |
| 4 | `FORMVER` | UDS 폼 버전 (1/2/3/4) |
| 5 | `VISITMO` | Visit 월 |
| 6 | `VISITDAY` | Visit 일 |
| 7 | `VISITYR` | Visit 년 |
| 8 | `NACCVNUM` | Visit sequence (1-based) |

### 2.2 인구통계 (6 cols, 9–14) — A1 폼 subset

| # | 컬럼 | 의미 |
|---|------|------|
| 9 | `BIRTHMO` | 출생 월 |
| 10 | `BIRTHYR` | 출생 년 |
| 11 | `SEX` | 성별 (1=Male, 2=Female) |
| 12 | `RACE` | 인종 (NACC 코드) |
| 13 | `EDUC` | 교육 연수 |
| 14 | `MARISTAT` | 결혼 상태 |

### 2.3 CDR (10 cols, 15–24) — B4 폼

| # | 컬럼 | 의미 |
|---|------|------|
| 15 | `MEMORY` | CDR 도메인 — 기억 (0/0.5/1/2/3) |
| 16 | `ORIENT` | CDR 도메인 — 지남력 |
| 17 | `JUDGMENT` | CDR 도메인 — 판단 |
| 18 | `COMMUN` | CDR 도메인 — Community Affairs |
| 19 | `HOMEHOBB` | CDR 도메인 — Home and Hobbies |
| 20 | `PERSCARE` | CDR 도메인 — Personal Care |
| 21 | `CDRSUM` | CDR Sum of Boxes (0–18) |
| 22 | `CDRGLOB` | CDR Global (0/0.5/1/2/3) |
| 23 | `COMPORT` | CDR 추가 도메인 — Behavior, Comportment, and Personality (UDS v3) |
| 24 | `CDRLANG` | CDR 추가 도메인 — Language (UDS v3) |

### 2.4 인지검사 / 진단 derived (14 cols, 25–38) — C1 + D1 derived

| # | 컬럼 | 의미 |
|---|------|------|
| 25 | `NACCMMSE` | NACC 표준화 MMSE |
| 26 | `MOCATOTS` | MoCA 총점 (UDS v3.1+) |
| 27 | `NACCMOCA` | NACC 표준화 MoCA |
| 28 | `NACCTMCI` | MCI 지표 (NACC derived flag) |
| 29 | `NACCALZD` | AD dementia 지표 (NACC derived) |
| 30 | `NACCAGEB` | Birth age (derived) |
| 31 | `NACCAGE` | Visit-time age |
| 32 | `NACCUDSD` | UDS dementia stage (derived) |
| 33 | `NACCACSF` | CSF Aβ derived flag |
| 34 | `NACCPCSF` | CSF p-tau derived flag |
| 35 | `NACCTCSF` | CSF t-tau derived flag |
| 36 | `NACCNMRI` | MRI 가용 여부 |
| 37 | `NACCNAPA` | Neuropath 자료 여부 |
| 38 | `NACCNE4S` | APOE ε4 allele 수 (derived) |

### 2.5 Visit date + DX (2 cols, 39 + 45)

| # | 컬럼 | 의미 |
|---|------|------|
| 39 | `VISITDATE` | YYYY-MM-DD 합성 (`VISITYR/MO/DAY` 통합) |
| 45 | `DX` | 통합 진단 라벨 (NeuroXT-derived) |

### 2.6 CSF 바이오마커 (5 cols, 40–44) — `investigator_fcsf_nacc71.csv` source

| # | 컬럼 | 의미 |
|---|------|------|
| 40 | `CSFABETA` | CSF Aβ42 (pg/mL) |
| 41 | `CSFPTAU` | CSF p-tau (pg/mL) |
| 42 | `CSFTTAU` | CSF t-tau (pg/mL) |
| 43 | `CSFDATE_MATCH` | CSF 채취일 (visit 매칭 후) |
| 44 | `CSFDATEDIFF` | CSF 채취일 − VISITDATE 차이 (일) |

### 2.7 Amyloid PET (175 cols, 46–221) — `investigator_scan_pet/amyloidpetnpdka` + `amyloidpetgaain` source

`AMY/...` prefix. Amyloid PET 정량화 풀세트.

| # 범위 | 그룹 | 컬럼 패턴 | 비고 |
|--------|------|----------|------|
| 46 | `AMYDATEDIFF` | scan ↔ visit 일수 차이 | |
| 47–52 | `AMY/SCANDATE`, `AMY/PROCESSDATE`, `AMY/TRACER`, `AMY/TRACER_SUVR_WARNING`, `AMY/ACQUISITION_TIME`, `AMY/AMYLOID_STATUS` | scan 메타 + amyloid 양성 status | |
| 53 | `AMY/CENTILOIDS` | Centiloid 값 | GAAIN 표준 |
| 54–62 | GAAIN composite SUVR (5) + NPDKA composite SUVR (4) | `AMY/GAAIN_SUMMARY_SUVR`, `AMY/GAAIN_WHOLECEREBELLUM_SUVR`, `AMY/GAAIN_COMPOSITE_REF_SUVR`, `AMY/GAAIN_CEREBELLUM_CORTEX`, `AMY/NPDKA_SUMMARY_SUVR`, `AMY/NPDKA_WHOLECEREBELLUM_SUVR`, `AMY/NPDKA_COMPOSITE_REF_SUVR`, `AMY/NPDKA_CEREBELLUM_CORTEX_SUVR`, `AMY/NPDKA_ERODED_SUBCORTICALWM_SUVR` | composite 통합 SUVR |
| 63–74 | bilateral subcortical + ventricle (12) | `AMY/BRAINSTEM_SUVR`, `AMY/CC_*` (corpus callosum 5분할), `AMY/CSF_SUVR`, `AMY/VENTRICLE_3RD_SUVR`, `AMY/VENTRICLE_4TH_SUVR`, `AMY/VENTRICLE_5TH_SUVR`, `AMY/WM_HYPOINTENSITIES_SUVR`, `AMY/NON_WM_HYPOINTENSITIES_SUVR` | |
| 75–108 | bilateral cortical 35 ROI | `AMY/CTX_<region>_SUVR` (banksstris, caudalanteriorcingulate, ..., transversetemporal — DKT atlas 35 region) | |
| 109–123 | bilateral subcortical 14 ROI + vessel + chiasm | `AMY/ACCUMBENS_AREA_SUVR`, `AMY/AMYGDALA_SUVR`, `AMY/CAUDATE_SUVR`, `AMY/CEREBELLUM_*`, `AMY/CHOROID_PLEXUS_SUVR`, `AMY/HIPPOCAMPUS_SUVR`, `AMY/OPTIC_CHIASM_SUVR`, `AMY/INF_LAT_VENT_SUVR`, `AMY/LATERAL_VENTRICLE_SUVR`, `AMY/PALLIDUM_SUVR`, `AMY/PUTAMEN_SUVR`, `AMY/THALAMUS_PROPER_SUVR`, `AMY/VENTRALDC_SUVR`, `AMY/VESSEL_SUVR` | |
| 124–157 | LH cortical 35 ROI | `AMY/CTX_LH_<region>_SUVR` | |
| 158–191 | RH cortical 35 ROI | `AMY/CTX_RH_<region>_SUVR` | |
| 192–206 | LH subcortical 15 | `AMY/LEFT_<region>_SUVR` | |
| 207–221 | RH subcortical 15 | `AMY/RIGHT_<region>_SUVR` | |

> Amyloid PET 의 reference region 은 GAAIN composite (cerebellum/whole/composite) 또는 NPDKA (eroded subcortical white matter). Centiloid 변환은 GAAIN 기반이 표준.

### 2.8 Tau PET (169 cols, 222–390) — `investigator_scan_pet/taupetnpdka` source

`TAU/...` prefix. Tau PET 정량화. Amyloid 와 같은 DKT atlas + 일부 다른 ROI (entorhinal, meta-temporal, infcerebellum 추가).

| # 범위 | 그룹 | 컬럼 패턴 |
|--------|------|----------|
| 222 | `TAUDATEDIFF` | scan ↔ visit 일수 차이 |
| 223–228 | scan 메타 + tau 정량 | `TAU/SCANDATE`, `TAU/PROCESSDATE`, `TAU/TRACER`, `TAU/TRACER_SUVR_WARNING`, `TAU/ACQUISITION_TIME`, `TAU/META_TEMPORAL_SUVR` |
| 229–231 | reference + meta region | `TAU/CTX_ENTORHINAL_SUVR`, `TAU/INFERIORCEREBELLUM_SUVR`, `TAU/ERODED_SUBCORTICALWM_SUVR` |
| 232–243 | bilateral subcortical + ventricle (12) | `TAU/BRAINSTEM_SUVR`, `TAU/CC_*`, `TAU/CSF_SUVR`, `TAU/VENTRICLE_*`, `TAU/WM_HYPOINTENSITIES_SUVR`, `TAU/NON_WM_HYPOINTENSITIES_SUVR` |
| 244–276 | bilateral cortical 33 ROI | `TAU/CTX_<region>_SUVR` (DKT atlas, frontalpole 제외 → 33) |
| 277–292 | bilateral subcortical 16 ROI | `TAU/ACCUMBENS_AREA_SUVR`, ..., `TAU/VESSEL_SUVR` |
| 293–326 | LH cortical 34 ROI | `TAU/CTX_LH_<region>_SUVR` |
| 327–360 | RH cortical 34 ROI | `TAU/CTX_RH_<region>_SUVR` |
| 361–375 | LH subcortical 15 | `TAU/LEFT_<region>_SUVR` |
| 376–390 | RH subcortical 15 | `TAU/RIGHT_<region>_SUVR` |

> Tau PET 의 META_TEMPORAL = Braak stage III/IV 평균 (entorhinal + amygdala + parahippocampal + fusiform + inferior/middle temporal). 임상 분석에서 가장 자주 보고됨.

---

## 3. 분석 패턴

### 3.1 baseline + amyloid 양성 분류

```python
import pandas as pd

df = pd.read_csv("/Volumes/nfs_storage/NACC_NEW/ORIG/DEMO/merged.csv")
df = df.replace([88, 99, 888, 999, 9999], pd.NA)

baseline = df[df['NACCVNUM'] == 1]

# Amyloid 양성 분류 (CL ≥ 24 표준)
baseline['amyloid_positive'] = baseline['AMY/CENTILOIDS'] >= 24

# CDR 그룹
baseline['CDR_group'] = baseline['CDRGLOB'].map(
    {0.0: 'CN', 0.5: 'Very mild', 1.0: 'Mild', 2.0: 'Moderate', 3.0: 'Severe'})
```

### 3.2 PACKET 별 분석

```python
# Telephone visit 제외 (B1, B8 등 결측)
clinic = df[df['PACKET'].isin(['I', 'F'])]
```

### 3.3 PET ROI 평균 계산 예 (Amyloid Frontal cortex)

```python
frontal_rois = [
    'AMY/CTX_FRONTALPOLE_SUVR',
    'AMY/CTX_LATERALORBITOFRONTAL_SUVR',
    'AMY/CTX_MEDIALORBITOFRONTAL_SUVR',
    'AMY/CTX_PARSOPERCULARIS_SUVR',
    'AMY/CTX_PARSORBITALIS_SUVR',
    'AMY/CTX_PARSTRIANGULARIS_SUVR',
    'AMY/CTX_ROSTRALMIDDLEFRONTAL_SUVR',
    'AMY/CTX_SUPERIORFRONTAL_SUVR',
    'AMY/CTX_CAUDALMIDDLEFRONTAL_SUVR',
]
df['amy_frontal_mean'] = df[frontal_rois].mean(axis=1)
```

---

## 4. Source-별 매핑 검증

`merged.csv` 컬럼이 어느 NACC 표준 파일에서 왔는지:

| `merged.csv` 컬럼 | Source 파일 | Source 컬럼명 |
|------------------|------------|--------------|
| `NACCID`, `NACCADC`, `PACKET`, `FORMVER`, `VISITMO/DAY/YR`, `NACCVNUM`, `BIRTHMO/YR`, `SEX`, `RACE`, `EDUC`, `MARISTAT`, `MEMORY`, ..., `CDRLANG`, `NACCMMSE`, `MOCATOTS`, ..., `NACCNE4S` | `investigator_ftldlbd_nacc71.csv` | 동일 컬럼명 |
| `VISITDATE`, `DX` | (NeuroXT derived) | `VISITDATE` = `YYYY-MM-DD` 합성, `DX` = NeuroXT 통합 진단 라벨 |
| `CSFABETA`, `CSFPTAU`, `CSFTTAU` | `investigator_fcsf_nacc71.csv` | 동일 |
| `CSFDATE_MATCH`, `CSFDATEDIFF` | (NeuroXT derived) | nearest match 결과 |
| `AMY/...` (175) | `investigator_scan_pet/investigator_scan_amyloidpetnpdka_nacc71.csv` (172) + `investigator_scan_amyloidpetgaain_nacc71.csv` (15) | `*_SUVR`, `CENTILOIDS`, `AMYLOID_STATUS` |
| `TAU/...` (169) | `investigator_scan_pet/investigator_scan_taupetnpdka_nacc71.csv` (171) | `*_SUVR`, `META_TEMPORAL_SUVR` 등 |

> NPDKA = New Progress for Discovering Aging (NACC SCAN 정량화 파이프라인 명).
> GAAIN = Global Alzheimer's Association Interactive Network (centiloid 표준 정의).

---

## Known limitations & quirks

1. **`merged.csv` 는 NACC 표준 아님 — NeuroXT-pre-built file.** Reproducibility 가 중요한 분석은 source `investigator_*.csv` 사용.
2. **390 cols 중 일부는 visit 마다 결측 가능.** PACKET=T (telephone) 에서 B1/B8 폼 결측, A3/B3 optional 폼은 일부 visit에만 채움. CSF/PET SUVR은 측정한 visit에서만 채움. 분석 시 컬럼별 missingness 확인 필수.
3. **`CSFDATEDIFF` / `AMYDATEDIFF` / `TAUDATEDIFF` 의 부호 컨벤션.** scan/CSF 일자 − visit 일자 (양수 = scan 이 visit 이후, 음수 = scan 이 visit 이전). join 시 윈도우는 절댓값 기준.
4. **Tau PET ROI 이 Amyloid 보다 적음 (169 < 175).** Tau 는 DKT atlas 의 33 cortical ROI (frontalpole 제외) + 16 subcortical 만. Amyloid 는 35 cortical + 14 subcortical + chiasm + vessel. 같은 region 이름이라도 두 PET 에서 ROI 정의가 살짝 다를 수 있다 — 분석 시 주의.
5. **`NACCNE4S` (APOE ε4 allele 수)** 는 NACC derived flag. APOE 유전자형 (E2/E3/E4) 자체는 별도 컬럼 (genetic data RDD 참조).
6. **`merged_CDR.csv`는 v71 freeze에서 사라짐.** 2026-03-13 inventory에서는 보였으나 현재 freeze에는 없음. CDR 컬럼은 모두 `merged.csv` 안에 있음.

> 검증일 2026-05-01 (freeze v71)
