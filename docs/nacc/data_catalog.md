# NACC NFS 파일 카탈로그

`/Volumes/nfs_storage/NACC_NEW/ORIG/` (v71 freeze, 2026-04 기준) 의 마스터 인벤토리. 파일별 크기·행수·컬럼수·content를 정리하며, 어디서 무엇을 읽어야 하는지 결정할 때 시작점이 된다.

> **NFS 마운트 root**: macOS `/Volumes/nfs_storage/NACC_NEW/ORIG/`, Windows `Z:\NACC_NEW\ORIG\`, Linux `/mnt/nfs/NACC_NEW/ORIG/`. 이하 모든 경로는 `ORIG/` 이하 상대.

---

## 1. 최상위 구조

```
NACC_NEW/ORIG/
├── DEMO/                        임상 + 정량화 (CSV / PDF)
│   ├── merged.csv               NeuroXT-built 통합 working file
│   ├── Data_Directory/          NACC RDD PDF (10개)
│   ├── Commercial_Data/         Commercial 동의 tier (좁은 동의)
│   └── Non_Commercial_Data/     Investigator 동의 tier (학술 default)
├── NII_NEW/                     BIDS-style NIfTI (6,481명)
├── DCM/                         원본 DICOM (archive)
└── ZIP/                         압축 백업 (분기 freeze export)
```

---

## 2. `DEMO/` — 임상 + 정량화 데이터

### 2.1 NeuroXT-built working file

| 파일 | 크기 | 행 | 열 | 1줄 설명 |
|------|------|------|------|---------|
| `DEMO/merged.csv` | 96 MB | 205,909 | 390 | UDS 핵심 38 cols + CSF 5 + Amyloid PET 175 + Tau PET 169 + meta — `(NACCID, NACCVNUM)` 단위 inner-join. 자세한 사전: [`merged_csv.md`](merged_csv.md) |

> **`merged.csv`는 NACC 표준 배포가 아닌 NeuroXT-pre-built file**. 원본은 `DEMO/Non_Commercial_Data/investigator_*.csv` 시리즈 + `investigator_scan_pet/*` 시리즈에서 가져옴. NACC 표준 분석 / reproducibility를 추구한다면 `Non_Commercial_Data/investigator_*.csv` 를 직접 사용.

### 2.2 NACC 공식 RDD PDF (`Data_Directory/`)

NACC가 매 freeze에 함께 배포하는 Researcher's Data Dictionary. 컬럼 정의의 권위 source.

| 파일 | 크기 | 내용 |
|------|------|------|
| `DEMO/Data_Directory/uds3-rdd.pdf` | 2.2 MB | **UDS v3 RDD** (1000+ 변수 정의, A1–D2 폼 전체) |
| `DEMO/Data_Directory/rdd-np.pdf` | 449 KB | Neuropathology 폼 RDD |
| `DEMO/Data_Directory/rdd-imaging.pdf` | 263 KB | Imaging metadata 폼 RDD |
| `DEMO/Data_Directory/rdd-genetic-data.pdf` | 123 KB | NACC genetic flag 정의 (APOE 등) |
| `DEMO/Data_Directory/SCAN-MRI-Imaging-RDD.pdf` | 572 KB | NACC SCAN MRI 변수 사전 (mriqc, mrisbm) |
| `DEMO/Data_Directory/ftld3-fvp-ded.pdf` | 325 KB | FTLD3 FVP (Follow-up Visit Packet) DED |
| `DEMO/Data_Directory/ftld3-ivp-ded.pdf` | 324 KB | FTLD3 IVP (Initial Visit Packet) DED |
| `DEMO/Data_Directory/lbd3_1-fvp-ded.pdf` | 360 KB | LBD 모듈 v3.1 FVP DED |
| `DEMO/Data_Directory/lbd3_1-ivp-ded.pdf` | 340 KB | LBD 모듈 v3.1 IVP DED |
| `DEMO/Data_Directory/biomarker-ee2-csf-ded.pdf` | 157 KB | CSF 바이오마커 (EE2 episodic enrichment) DED |

> **DED** = Data Element Definition. Form-by-form spec.
> **IVP / FVP** = Initial Visit Packet / Follow-up Visit Packet. 같은 모듈도 첫 방문과 후속 방문이 양식이 다르다.

### 2.3 `Commercial_Data/` — 산업 / 상업 사용 가능 동의 (좁은 동의)

같은 NACC 데이터의 commercial-tier subset. 컬럼 스키마는 Investigator tier와 동일 (1:1 미러), 행 수만 적다. 자세한 tier 정책: [`data_tier_reference.md`](data_tier_reference.md).

| 파일 | 크기 | 행 | 열 | 1줄 설명 |
|------|------|------|------|---------|
| `DEMO/Commercial_Data/commercial_fcsf_nacc71.csv` | 261 KB | 2,770 | 23 | CSF 바이오마커 (Aβ42, p-tau, t-tau + 채취일/측정일/방법/메타) |
| `DEMO/Commercial_Data/commercial_ftldlbd_nacc71.csv` | 605 MB | 179,753 | **1,936** | **FULL UDS + FTLD3 + LBD3.1 통합** — A1–D2 + bookkeeping + FTLD/LBD 모듈 (옵셔널 visit) 모두. 이 파일이 NACC 임상 데이터의 master |
| `DEMO/Commercial_Data/commercial_mri_nacc71.csv` | 14 MB | 10,520 | 191 | NACC 전통적 MRI metric (volumetry, NACCMRIA/MRFI/MNUM/MRDY 등) — SCAN MRI와 별개 |
| `DEMO/Commercial_Data/commercial_scan_mri_nacc71/` (subdir) | — | — | — | NACC SCAN MRI 정량화 |
| `└── commercial_scan_mriqc_nacc71.csv` | 6.1 MB | 22,855 | 38 | SCAN MRI QC (study/series 단위 protocol/QC flag) |
| `└── commercial_scan_mrisbm_nacc71.csv` | 6.5 MB | 5,330 | 249 | SCAN MRI SBM (Surface-Based Morphometry, FreeSurfer-style cortical thickness/volume) |
| `DEMO/Commercial_Data/commercial_scan_pet_nacc71/` (subdir) | — | — | — | NACC SCAN PET 정량화 |
| `└── commercial_scan_amyloidpetgaain_nacc71.csv` | 486 KB | (≈2,808) | 15 | Amyloid PET GAAIN composite SUVR + Centiloid + AMYLOID_STATUS |
| `└── commercial_scan_amyloidpetnpdka_nacc71.csv` | 2.9 MB | (≈2,808) | 172 | Amyloid PET NPDKA per-region SUVR (FreeSurfer DKT atlas, bilateral + LH + RH) |
| `└── commercial_scan_fdgpetnpdka_nacc71.csv` | 489 KB | (≈485) | 169 | FDG PET NPDKA per-region SUVR |
| `└── commercial_scan_petqc_nacc71.csv` | 281 KB | (≈5,103) | 11 | PET QC (study-level pass/fail) |
| `└── commercial_scan_taupetnpdka_nacc71.csv` | 1.9 MB | (≈1,815) | 171 | Tau PET NPDKA per-region SUVR (entorhinal + meta-temporal 추가) |
| `DEMO/Commercial_Data/ADSP-PHC-122024-commercial/` (subdir) | — | — | — | ADSP-PHC December 2024 commercial release. 8 도메인 + Return-to-Cohort manifest xlsx (자세한 내용은 [`optional_modules.md`](optional_modules.md)) |

### 2.4 `Non_Commercial_Data/` — Investigator (학술 전용, default)

`Commercial_Data/` 와 1:1 미러 구조. 행 수가 더 많음.

| 파일 | 크기 | 행 | 열 | 1줄 설명 |
|------|------|------|------|---------|
| `DEMO/Non_Commercial_Data/investigator_fcsf_nacc71.csv` | 279 KB | 3,052 | 23 | CSF 바이오마커 |
| `DEMO/Non_Commercial_Data/investigator_ftldlbd_nacc71.csv` | 693 MB | **205,909** | **1,936** | **NACC 임상 master 파일.** `merged.csv` 의 행 수와 동일 (NeuroXT가 이 파일에서 38 cols 추출) |
| `DEMO/Non_Commercial_Data/investigator_mri_nacc71.csv` | 16 MB | 12,043 | 191 | 전통적 MRI metric |
| `DEMO/Non_Commercial_Data/investigator_scan_mri_nacc71/` (subdir) | — | — | — | SCAN MRI |
| `└── investigator_scan_mriqc_nacc71.csv` | 6.6 MB | 22,855 | 38 | SCAN MRI QC |
| `└── investigator_scan_mrisbm_nacc71.csv` | 7.2 MB | 5,330 | 249 | SCAN MRI SBM |
| `DEMO/Non_Commercial_Data/investigator_scan_pet_nacc71/` (subdir) | — | — | — | SCAN PET |
| `└── investigator_scan_amyloidpetgaain_nacc71.csv` | 509 KB | 2,808 | 15 | Amyloid PET GAAIN |
| `└── investigator_scan_amyloidpetnpdka_nacc71.csv` | 3.0 MB | 2,808 | 172 | Amyloid PET NPDKA per-region |
| `└── investigator_scan_fdgpetnpdka_nacc71.csv` | 489 KB | 485 | 169 | FDG PET NPDKA |
| `└── investigator_scan_petqc_nacc71.csv` | 290 KB | 5,103 | 11 | PET QC |
| `└── investigator_scan_taupetnpdka_nacc71.csv` | 1.9 MB | 1,815 | 171 | Tau PET NPDKA |
| `DEMO/Non_Commercial_Data/ADSP-PHC-122024-investigator/` (subdir) | — | — | — | ADSP-PHC investigator-tier 8 도메인 |

> **`investigator_*.csv`는 모두 `(NACCID, NACCADC)` 시작.** 단, fcsf만 `(NACCADC, NACCID)` 순서로 시작 — 분석 시 컬럼명으로 join, 위치 의존 금지.

### 2.5 `ADSP-PHC-122024-investigator/` 상세

ADSP-PHC = Alzheimer's Disease Sequencing Project — Phenotype Harmonization Consortium. December 2024 freeze. 한 번 더 nested (`ADSP-PHC-122024-investigator/ADSP-PHC-122024-investigator/`) 인 점 주의.

```
ADSP-PHC-122024-investigator/ADSP-PHC-122024-investigator/
├── NACC_ADSP-PHC_Dec2024_Return-to-Cohort.xlsx     ADSP↔NACC subject manifest
├── Imaging_PET/                                     Amyloid + Tau PET 정량화
│   ├── NACC_ADSP_PHC_Amyloid_Simple_2024.csv        Amyloid SUVR composite
│   ├── NACC_ADSP_PHC_Amyloid_Detailed_2024.csv      Amyloid per-region SUVR
│   ├── NACC_ADSP_PHC_Tau_Simple_2024.csv            Tau composite
│   ├── NACC_ADSP_PHC_Tau_Detailed_2024.csv          Tau per-region
│   ├── NACC_ADSP_PHC_*_DD_2024.xlsx                 (각 CSV별 Data Dictionary)
│   └── NACC_ADSP_PHC_PET_ReadMe_2024.docx           release notes
├── Imaging_T1/
│   ├── NACC_ADSP_PHC_T1_Freesurfer_2024.csv         FreeSurfer (DKT atlas)
│   ├── NACC_ADSP_PHC_T1_MUSE_2024.xlsx              MUSE (region segmentation)
│   ├── NACC_ADSP_PHC_T1_*_DD_2024.xlsx
│   └── NACC_ADSP_PHC_T1_ReadMe_2024.docx
├── Imaging_FLAIR/                                    WMH segmentation
├── Imaging_DTI/                                      DTI metric (FA, MD)
├── Vascular_Risk/
│   ├── NACC_ADSP_PHC_VascularRisk_2024.csv          VRF score
│   ├── NACC_ADSP_PHC_VascularRisk_DD_2024.xlsx
│   └── NACC_ADSP_PHC_VascularRisk_ReadMe_2024.docx
├── Biomarker/
│   ├── NACC_ADSP_PHC_Biomarker_2024.csv             ADSP-PHC harmonized fluid biomarker
│   └── NACC_ADSP_PHC_Biomarker_ReadMe_2024.docx
├── Neuropath/                                        부검 / 신경병리
└── Cognition/                                        ADSP-PHC harmonized cognition score
```

각 도메인은 `*_2024.csv` (data) + `*_DD_2024.xlsx` (data dictionary) + `*_ReadMe_2024.docx` (release notes) 3-tuple 구조.

> Commercial tier (`ADSP-PHC-122024-commercial/ADSP-PHC-122024-commercial/`) 도 같은 구조. 행 수만 다르다.

---

## 3. `NII_NEW/` — BIDS-style NIfTI

```
NII_NEW/
└── NACC{ID}/                     예: NACC252073/
    └── v{N}/                     예: v1, v2, ... (visit number, 1-based)
        └── {MODALITY}/           예: T1/, AV45/, FLAIR/
            └── {protocol}/       acquisition protocol token
                └── {date}/       YYYY-MM-DD
                    └── {imageID}/
                        └── *.nii.gz
```

| 항목 | 값 |
|------|------|
| Imaged subjects | 6,481 |
| Modalities (관찰) | T1, T2w, FLAIR, T2_STAR (GRE), ASL, HighResHippo, dMRI, rsfMRI, AV45, AV1451, FBB, PIB, MK6240, FDG (11+) |
| Subject 1 visit 수 (예) | 1–11 (NACC252073: 11회 방문, 9 모달리티) |

> 자세한 모달리티 분포 / 파일 카운트 / unmatched 처리는 [`imaging_inventory.md`](imaging_inventory.md) 참조.

---

## 4. `DCM/` 와 `ZIP/`

| 디렉토리 | 용도 |
|---------|------|
| `DCM/` | 원본 DICOM. NII_NEW 변환 검증 / archive 용. 분석 파이프라인은 NII_NEW 사용. |
| `ZIP/` | 분기 freeze export 압축 백업. 새 freeze가 들어오면 이전 export가 ZIP/로 이동. v71 이전 freeze 추적용. |

---

## 5. 컬럼 사전 / 분석 가이드 — Cross-link

| 알고 싶은 것 | 어디 보나 |
|-------------|----------|
| `merged.csv` 390 컬럼이 무엇인가 | [`merged_csv.md`](merged_csv.md) |
| UDS 폼 컬럼 정의 (A1, B4, C1, D1, …) | [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) |
| NACC bookkeeping 컬럼 (NACCID/NACCADC/PACKET/FORMVER/NACCVNUM) | [`uds_forms.md`](uds_forms.md) |
| Visit / packet 시맨틱 | [`session_label_reference.md`](session_label_reference.md) + [`docs/_shared/nacc_session_labels.md`](../_shared/nacc_session_labels.md) |
| FTLD3 / LBD3.1 / SCAN PET / SCAN MRI / fcsf / ADSP-PHC | [`optional_modules.md`](optional_modules.md) |
| `(NACCID, NACCVNUM, PACKET)` 조인 키와 카디널리티 | [`join_relationships.md`](join_relationships.md) |
| Commercial vs Investigator 어느 쪽 쓸지 | [`data_tier_reference.md`](data_tier_reference.md) |
| 영상 ↔ 임상 visit 매칭 | [`imaging_inventory.md`](imaging_inventory.md) |

---

## 6. 검증 명령

NFS 마운트 상태에서 본 docs 의 사실을 재검증할 때 사용:

```bash
cd /Volumes/nfs_storage/NACC_NEW/ORIG

# merged.csv 행 / 열 검증
wc -l DEMO/merged.csv
head -1 DEMO/merged.csv | awk -F, '{print NF}'

# Tier 미러링 검증 (Commercial vs Investigator 행 수 차이)
for f in DEMO/Commercial_Data/*.csv; do
    base=$(basename "$f" | sed 's/^commercial_/investigator_/')
    inv="DEMO/Non_Commercial_Data/$base"
    com_n=$(wc -l < "$f")
    inv_n=$(wc -l < "$inv" 2>/dev/null)
    echo "$(basename $f): commercial=$com_n investigator=$inv_n"
done

# RDD PDF 카운트
ls DEMO/Data_Directory/*.pdf | wc -l   # → 10
```

---

## Known limitations & quirks

1. **`merged.csv`는 NACC 표준 아님 (NeuroXT-built).** 본 docs 어디서든 "NACC 표준 분석"을 하고 싶다면 `Non_Commercial_Data/investigator_ftldlbd_nacc71.csv` (또는 commercial 짝) 를 직접 사용.
2. **`merged_CDR.csv`는 v71 freeze에서 사라짐.** 2026-03-13 inventory에 있던 보조 파일이 v71 freeze 시점에는 없음. CDR 컬럼은 모두 `merged.csv` 에 들어있음.
3. **fcsf 컬럼 순서 첫 두 칼이 다른 시리즈와 반대.** `(NACCADC, NACCID)` 순. 컬럼명으로 join 권장.
4. **ADSP-PHC 폴더는 double-nested.** `ADSP-PHC-122024-investigator/ADSP-PHC-122024-investigator/` — release tarball을 그대로 풀어둔 흔적.
5. **`commercial_*` 와 `investigator_*` 동일 컬럼 스키마.** 쓰임은 컨센트 차이만. 행 수 차이 + (자주) NACCID 차이 발생.
6. **SCAN PET 행 수가 모달리티별로 다름.** Amyloid 2,808 (가장 많음) > Tau 1,815 > FDG 485. Tau / FDG 가 적은 이유는 trace 대상자 수가 적은 것.
7. **`commercial_scan_amyloidpetgaain` rows 미확정 (≈2,808 expected).** 본 docs 검증 사이클에서 commercial tier SCAN PET 행 수는 cross-tier 비교로 추정. 별도 검증 권장.
8. **DCM/ 트리는 inspection 비용이 큼.** 직접 listing 시 NFS 응답 지연. NACC 분석은 NII_NEW만 사용 권장.

> 검증일 2026-05-01 (freeze v71)
