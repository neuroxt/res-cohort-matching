# NACC NII_NEW 영상 인벤토리

`/Volumes/nfs_storage/NACC_NEW/ORIG/NII_NEW/` BIDS-style NIfTI 트리 구조, 모달리티 분포, 임상-영상 매칭 패턴.

NACC SCAN 정량화 (Amyloid/Tau/FDG/MRI SBM) 표준 산출물은 [`optional_modules.md`](optional_modules.md) 에서 다룬다 — 본 docs 는 **원본 NIfTI 파일 자체** 의 인벤토리.

---

## 1. 디렉토리 트리

```
NII_NEW/
└── NACC{ID}/                      예: NACC000133/
    └── v{N}/                      예: v1, v2, ..., (visit number, 1-based)
        └── {MODALITY}/            예: T1/, FLAIR/, AV45/, AV1451/, ...
            └── {protocol}/        acquisition protocol token (예: MPRAGE, Sagittal_3D_FLAIR)
                └── {date}/        YYYY-MM-DD_HH_MM_SS.0
                    └── {imageID}/
                        └── *.nii.gz  (+ *.json BIDS sidecar)
```

### Sample subject

```
NII_NEW/NACC000133/
├── v1/
│   ├── FLAIR/
│   │   └── Sagittal_3D_FLAIR/
│   │       └── 2024-10-31_10_29_53.0/
│   │           └── ...nii.gz
│   ├── T1/
│   │   └── MPRAGE/
│   │       └── 2024-10-31_10_24_18.0/
│   │           └── ...nii.gz
│   └── Other/
│       └── [BR-DY_CTAC_JP]_UH_CADRC_BRAIN/
│           └── 2024-09-17_12_50_37.0/
│               └── ...nii.gz
```

---

## 2. 핵심 통계

| 항목 | 값 (v71 freeze 기준) |
|------|---------------------|
| Unique imaged subjects | **6,548** (`ls NII_NEW/ | sort -u | wc -l`) |
| 디렉토리 엔트리 (총) | 6,548 (unique 와 동일 — 중복 없음) |
| 모달리티 종류 (관찰됨) | T1, T2w, FLAIR, T2_STAR (GRE), HighResHippo, ASL, dMRI, rsfMRI, AV45, AV1451, FBB, PIB, MK6240, FDG, Other |
| 평균 visit 수 / subject | ~1–11 (subject 별 차이 큼; 4–5 visit subjects 가 다수) |

> 이전 inventory (2026-03-13) 시점에서 6,481 명 → v71 freeze (2026-04) 에서 6,548 명. 신규 imaging-submitting subject 가 2 분기 동안 추가됨.

---

## 3. 모달리티 표 (예상 / 검증 필요)

각 모달리티가 디렉토리 단위에 등장한 빈도 (sample of 10 subjects 기준):

| Modality 디렉토리명 | 기능 | 일반 protocol token |
|------|------|---------------------|
| `T1` | 구조 MRI (1mm isotropic) | `MPRAGE`, `MPRAGE_GRAPPA2`, `T1_MPR` |
| `T2w` | T2-weighted | `T2W_FLAIR`, `T2_TSE` |
| `FLAIR` | Fluid-attenuated IR (WMH 측정) | `Sagittal_3D_FLAIR`, `Axial_FLAIR` |
| `T2_STAR(GRE)` | Gradient Echo (microbleed 측정) | `T2STAR`, `GRE`, `SWI` |
| `HighResHippo` | High-resolution hippocampus 코로넬 | `T2_HippoCoronal` |
| `ASL` | Arterial Spin Labeling (CBF) | `pCASL`, `pcasl_2d_22sl` |
| `dMRI` | Diffusion Tensor / Spectrum | `DTI`, `dwi`, `dki` |
| `rsfMRI` | Resting-state fMRI | `rs_fMRI`, `rest_fMRI` |
| `AV45` | Amyloid PET (florbetapir) | tracer-named |
| `AV1451` | Tau PET (flortaucipir) | tracer-named |
| `FBB` | Amyloid PET (florbetaben) | tracer-named |
| `PIB` | Amyloid PET (Pittsburgh Compound B) | tracer-named |
| `MK6240` | Tau PET (MK-6240) | tracer-named |
| `FDG` | Glucose metabolism PET | tracer-named |
| `Other` | 미분류 / vendor-specific 시퀀스 | (예: `[BR-DY_CTAC_JP]_UH_CADRC_BRAIN` — CT attenuation correction) |

> 표는 sample 기반 추정. v71 freeze 의 정확한 modality × subject 분포는 다음 NACC SCAN 정량화 (mriqc/petqc) 파일과 cross-check:
> - `investigator_scan_mriqc_nacc71.csv` (22,855 series-level rows × 38 cols)
> - `investigator_scan_petqc_nacc71.csv` (5,103 study-level rows × 11 cols)
>
> 자세한 모달리티 × subject × visit 분포는 (TODO) 별도 inventory script 로 집계.

---

## 4. NIfTI 파일 구조 (BIDS-style)

각 modality / protocol / date 디렉토리에 들어가는 파일 패턴:

```
{protocol}/{date}/{imageID}/
├── *.nii.gz       NIfTI 영상 본체 (gzip 압축)
└── *.json         BIDS sidecar (acquisition parameters)
```

JSON sidecar 의 핵심 필드 (예시):

```json
{
  "Modality": "MR" or "PT",
  "Manufacturer": "Siemens" / "GE" / "Philips" / "Canon",
  "ManufacturersModelName": "Skyra" / "Prisma" / ...,
  "MagneticFieldStrength": 3.0,
  "RepetitionTime": 2.4,
  "EchoTime": 0.003,
  "FlipAngle": 8,
  "RadionuclideDose": ...,            # PET only
  "Tracer": "florbetapir",            # PET only
  "AcquisitionTime": "10:24:18.000"
}
```

각 modality 별 BIDS conventions 는 NACC SCAN documentation 참조.

---

## 5. 임상 ↔ 영상 매칭 패턴

### 5.1 NII_NEW 디렉토리에서 visit 추출

```python
import re
import pandas as pd
from pathlib import Path

ROOT = Path("/Volumes/nfs_storage/NACC_NEW/ORIG/NII_NEW")

def parse_nii_path(p: Path):
    """파일 경로에서 (NACCID, visit_num, modality, scan_date) 추출."""
    parts = p.parts
    # parts: [..., 'NII_NEW', NACCID, vN, MOD, protocol, date, imageID, file]
    nacc_idx = parts.index('NII_NEW')
    return {
        'NACCID': parts[nacc_idx + 1],
        'visit_num': int(re.match(r'v(\d+)', parts[nacc_idx + 2]).group(1)),
        'modality': parts[nacc_idx + 3],
        'scan_date': pd.to_datetime(parts[nacc_idx + 5][:10]),  # YYYY-MM-DD
    }

# 모든 NIfTI 파일 인덱스 빌드
records = [parse_nii_path(p) for p in ROOT.rglob('*.nii.gz')]
nii_index = pd.DataFrame(records)
```

### 5.2 임상 ↔ 영상 nearest match

```python
import pandas as pd

merged = pd.read_csv("/Volumes/nfs_storage/NACC_NEW/ORIG/DEMO/merged.csv",
                     usecols=['NACCID', 'NACCVNUM', 'VISITDATE'])
merged['VISITDATE'] = pd.to_datetime(merged['VISITDATE'])

# nii_index = above 결과
joined = pd.merge_asof(
    nii_index.sort_values('scan_date'),
    merged.sort_values('VISITDATE').rename(columns={'VISITDATE': 'scan_date'}),
    on='scan_date', by='NACCID',
    direction='nearest', tolerance=pd.Timedelta('90D'))

# joined 의 NACCVNUM 가 NaN 인 행 = 임상 visit 매칭 실패
unmatched = joined[joined['NACCVNUM'].isna()]
```

> ±90일 윈도우는 일반 default. 영상 visit 가 임상 visit 보다 자주 일어나는 (CSF 자주 채취, scan 가끔) 케이스에서는 윈도우를 ±180일 로 넓히면 매칭률 ↑.

---

## 6. 5.9% 영상-only / 임상 부재 처리

NII_NEW 에 영상은 있지만 `merged.csv` 에 임상 데이터가 부재한 381명 (5.9% of 6,481, 2026-03-13 기준):

| 처리 옵션 | 설명 |
|----------|------|
| 1. 자동 제외 | `merged.csv` join 시 left-join 으로 처리 → 임상 부재 영상은 자연 결측 |
| 2. Imaging-only cohort 별도 분석 | 영상 quality control / longitudinal scan 추적 등 임상 비의존적 분석에 사용 |
| 3. NACC freeze 갱신 대기 | 분기 freeze 갱신 시 누락 임상 데이터 일부 도착 |

```python
# 영상 있는데 임상 없는 NACCID 식별
imaged_ids = set(nii_index['NACCID'])
clinical_ids = set(merged['NACCID'])
imaging_only = sorted(imaged_ids - clinical_ids)

print(f"Imaging-only (no clinical): {len(imaging_only)} subjects")
# v71 freeze 기준 재집계 권장 (이전 inventory의 381 → freeze 갱신 후 변동)
```

---

## 7. DCM/ 와의 관계

`/Volumes/nfs_storage/NACC_NEW/ORIG/DCM/` 에는 원본 DICOM 시리즈가 저장된다. NII_NEW 는 DCM 을 dcm2niix 로 변환한 BIDS-style export. 분석은 NII_NEW 사용 권장 (DCM 은 archive).

> DCM 디렉토리는 listing 비용이 크므로 분석 시 직접 inspect 금지. 필요 시 NACC SCAN QC 파일 (`*_scan_petqc_*.csv`, `*_scan_mriqc_*.csv`) 로 series-level metadata 확인.

---

## 8. 모달리티 별 NACC SCAN 정량화 매핑

NII_NEW 의 raw 영상 ↔ NACC SCAN 정량화 산출물 매핑:

| NII_NEW modality | NACC SCAN 정량화 파일 | 컬럼 |
|------------------|----------------------|------|
| `T1` | `investigator_scan_mri_*/investigator_scan_mrisbm_nacc71.csv` (5,330 × 249) | FreeSurfer cortical thickness/volume (DKT atlas) |
| `T1` (QC 메타) | `investigator_scan_mriqc_nacc71.csv` (22,855 × 38) | series-level QC flag |
| `AV45` / `FBB` / `PIB` (Amyloid) | `investigator_scan_amyloidpet*` (composite + per-region) | GAAIN composite, NPDKA per-region SUVR |
| `AV1451` / `MK6240` (Tau) | `investigator_scan_taupetnpdka_nacc71.csv` (1,815 × 171) | per-region SUVR + meta-temporal |
| `FDG` (Metabolism) | `investigator_scan_fdgpetnpdka_nacc71.csv` (485 × 169) | per-region SUVR |
| `FLAIR` | (NACC SCAN 자체 미정량화) | ADSP-PHC FLAIR 폴더 (WMH segmentation) 별도 |
| `dMRI` | (NACC SCAN 자체 미정량화) | ADSP-PHC DTI 폴더 별도 |
| `rsfMRI` | (정량화 없음 — raw 만) | — |
| `T2_STAR (GRE)` | (정량화 없음) | — |

> NACC SCAN 은 T1/Amyloid PET/Tau PET/FDG PET 4종만 자체 정량화 수행. FLAIR/DTI/rsfMRI 등은 ADSP-PHC release 또는 외부 파이프라인 활용.

---

## 9. 검증 명령

```bash
cd /Volumes/nfs_storage/NACC_NEW/ORIG

# unique subject count
ls NII_NEW/ | sort -u | wc -l   # → 6,548

# 모달리티 분포 (NACC SCAN 정량화 기반 - 더 빠름)
head -2 DEMO/Non_Commercial_Data/investigator_scan_mri_nacc71/investigator_scan_mriqc_nacc71.csv | head -1 | awk -F, '{print $14}'  # SERIESDESCRIPTION
awk -F',' 'NR>1 {print $14}' DEMO/Non_Commercial_Data/investigator_scan_mri_nacc71/investigator_scan_mriqc_nacc71.csv | sort | uniq -c | sort -rn | head -20

# 한 subject 의 modality 트리
ls NII_NEW/NACC000133/v1/   # → FLAIR, T1, Other
```

---

## Known limitations & quirks

1. **NII_NEW 디렉토리 listing 의 일부 도구가 중복 리포트.** `ls -la` 하면 같은 NACCID 가 여러 번 나오는 경우 발생 (NFS attribute caching). 정확한 unique count 는 `ls | sort -u | wc -l` 또는 `find . -maxdepth 1 -type d | wc -l`.
2. **`Other/` 디렉토리는 vendor-specific / non-BIDS 시퀀스.** 분석 시 일반적으로 제외. 예: `[BR-DY_CTAC_JP]_UH_CADRC_BRAIN` (CT attenuation correction).
3. **모달리티 디렉토리명에 NACC 표준 / vendor 명 혼재.** `T2_STAR(GRE)` 같이 괄호 포함, `HighResHippo` 등. 정규식 매칭 시 lowercase 처리 + alias 표 필요.
4. **Visit 번호 = `vN` 디렉토리** 가 NACC `NACCVNUM` 과 일치하지 않을 수 있다. NACC 의 `NACCVNUM` 은 *임상* visit sequence — 영상은 그 사이/이후에 들어올 수 있다. 따라서 v1 (영상) ≠ NACCVNUM=1 (임상) 가능. join 키는 `(NACCID, scan_date)` ↔ `(NACCID, VISITDATE)` 의 시간 매칭이 정석.
5. **NIfTI ↔ NACC SCAN 정량화 사이 mismatch 가능.** SCAN 정량화 (mriqc/petqc) 에 들어있는 series 와 NII_NEW 의 *.nii.gz 가 1:1 매칭 안 될 수 있음 (변환 누락 / QC 탈락 등). 분석 시 둘 다 cross-check 권장.
6. **6,548 vs 이전 inventory 6,481** — 약 67명 증가. 분기 freeze 사이에 신규 영상 제출 subject 추가.
7. **DCM/ 트리 inspection 비용 큼.** NFS 응답 지연. 분석 파이프라인은 NII_NEW만 사용.

> 검증일 2026-05-01 (freeze v71)
