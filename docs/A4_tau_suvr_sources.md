# A4 Tau PET SUVR 데이터 소스 비교

A4/LEARN NFS에는 Tau PET SUVR 데이터가 **3개의 서로 다른 파이프라인**에서 생성된
5개 파일에 걸쳐 존재한다. 파이프라인마다 atlas, reference region, PVC 적용 여부가 다르므로
분석 목적에 맞는 소스를 선택해야 한다.

- Ligand: **Flortaucipir** (FTP, = AV-1451, = [18F]T807)
- 촬영 시점: SCV4 (MRI와 동일 방문), 80-110분 post-injection, 6 x 5분 frames

---

## 파일 요약

| 파일 | 위치 | 형식 | 규모 | 파이프라인 | Reference Region |
|------|------|------|------|-----------|-----------------|
| **TAUSUVR_11Aug2025.csv** | `metadata/A4 Imaging data and docs/` | Wide | 447명 x 274열 | Stanford | Cerebellar cortex GM |
| **imaging_Tau_PET_Stanford.csv** | `DEMO/Clinical/External Data/` | Wide | 447명 x 275열 | Stanford | 동일 (VISCODE=2 추가) |
| **imaging_SUVR_tau.csv** | `DEMO/Clinical/External Data/` | **Long** | 296,679행 (454명 x 8 visits x 192 regions) | Avid/Clark | Whole cerebellum (GM+WM) |
| **TAUSUVR_PETSURFER_11Aug2025.csv** | `metadata/A4 Imaging data and docs/` | Wide | 445명 x 244열 | PetSurfer (PVC) | Cerebellar cortex GM |
| **imaging_Tau_PET_PetSurfer.csv** | `DEMO/Clinical/External Data/` | Wide | 445명 x 245열 | PetSurfer (PVC) | 동일 |

> `TAUSUVR_11Aug2025.csv`와 `imaging_Tau_PET_Stanford.csv`는 **동일 데이터**임을 확인.
> 컬럼명 `.` → `_` 차이 + VISCODE 컬럼 추가만 다름.

---

## 3대 파이프라인 비교

| 항목 | Avid/Clark (SUVR) | Stanford (no PVC) | PetSurfer (PVC) |
|------|-------------------|-------------------|-----------------|
| **출력 파일** | `imaging_SUVR_tau.csv` | `imaging_Tau_PET_Stanford.csv` | `imaging_Tau_PET_PetSurfer.csv` |
| **Atlas** | AAL (template-based) | FreeSurfer aparc+aseg (native) | FreeSurfer gtmseg (native) |
| **처리 공간** | MNI template space | PET native space | PET native space |
| **Reference region** | **Whole cerebellum (GM+WM)** | **Cerebellar cortex GM only** | **Cerebellar cortex GM only** |
| **Target ROI 수** | 6 + composite | All aparc+aseg (~273) | All aparc+aseg (~243) |
| **PVC** | No | No | **Yes** (Muller-Gartner, PSF=6mm) |
| **Smoothing** | None | 4mm FWHM (111 subjects, 1 site) | None |
| **Bilateral 방법** | N/A | Volume-weighted avg | Voxel-weighted avg |
| **Longitudinal** | **Yes** (8 visits) | No (baseline만) | No (baseline만) |
| **파이프라인 적용** | 미적용 | **BASELINE.csv `TAU_*_bl`** | 미적용 |

---

## 파이프라인 상세

### 1. Stanford Pipeline (no PVC) — 우리 파이프라인이 사용하는 소스

Published in [Young et al., JAMA Neurology, 2022](https://jamanetwork.com/journals/jamaneurology/fullarticle/2790807).

**처리 단계:**
1. FreeSurfer `recon-all` (v5.3) → `nu.mgz`, `aparc+aseg.mgz`
2. PET 5분 frames realignment → sum/mean into single 3D volume
3. 111명 (1개 사이트): 4mm FWHM smoothing (FSL) — noisy data 보정
4. SPM으로 PET-to-MRI coregistration → aparc+aseg를 PET space로 이동
5. 모든 aparc+aseg region에서 mean SUVR 추출 (Desikan-Killiany atlas)
6. Bilateral regions: **volume-weighted averaging** (`bi_*` 컬럼)
7. Reference: **bilateral cerebellar cortex GM** (Left/Right-Cerebellum-Cortex, `bi_Cerebellum.Cortex` = 1.0)

**컬럼 구조:**
- `Mean_*` — SUVR (e.g., `Mean_Left_Hippocampus`)
- `Volume_mm3_*` — volume (e.g., `Volume_mm3_Left_Hippocampus`)
- `bi_*` — bilateral volume-weighted average

**참고:** Subject B34660963는 뇌 외부 off-target binding으로 frontal lobe SUVR이 부풀려져 있음 — 분석 시 제외 고려.

### 2. Avid/Clark Pipeline — Longitudinal, 다중 reference region

[Clark et al., Lancet Neurol 2012](https://doi.org/10.1016/S1474-4422(11)70314-4);
[Joshi et al., J Nucl Med 2015](https://doi.org/10.2967/jnumed.114.148981).

**처리 단계:**
1. PET을 MNI template space로 linear normalization (SPM)
2. AAL atlas 기반 ROI에서 SUVR 추출
3. Amyloid PET과 동일한 방법으로 처리 (`imaging_SUVR_amyloid.csv`와 같은 파이프라인)

**Target ROI (6 + 1 composite):**

| 컬럼명 | 영역 |
|--------|------|
| `xlaal_frontal_med_orb` | Frontal cortex |
| `new_temporal_2` | Temporal cortex |
| `lprecuneus_gm` | Precuneus |
| `lnew_parietal` | Parietal cortex |
| `llposterior_cingulate_2` | Posterior cingulate |
| `lanterior_cingulate_2` | Anterior cingulate |
| `blcere_all` | Whole cerebellum (reference) |
| `Composite_Summary` | Composite summary |

**SUVR 3종 (reference region별):**
- `suvr_cer` — cerebellar cortex reference
- `suvr_persi` — inferior cerebellar gray matter reference (SUIT template indices 6, 8-28, 33, 34)
- `suvr_crus` — cerebellar crus reference

**Longitudinal 데이터:**
- 454명, 8개 방문 (V4, V6, V24, V27, V48, V66, V84, V999)
- 코호트: A4 (262,695행), LEARN (32,832행), SF (1,152행)

### 3. PetSurfer Pipeline (PVC) — Partial Volume Corrected

FreeSurfer 6.0+ 내장 도구. [Baker et al., NeuroImage 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5671473/).

**처리 단계:**
1. `recon-all` → standard FreeSurfer processing
2. `gtmseg` → geometric transfer matrix segmentation
3. `lta_convert` → identity transform (PET-to-anatomical)
4. `mri_gtmpvc` with parameters:
   - `--psf 6` (6mm FWHM point spread function)
   - `--mgx 0.01` (Muller-Gartner analysis, GM threshold 0.01)
   - `--rescale 8 47` (normalize to bilateral cerebellar cortex)
   - `--default-seg-merge`, `--no-reduce-fov`

**Stanford vs PetSurfer 비교 (Young et al. Figure 1):**
- PVC 값이 non-PVC보다 **체계적으로 높음** (위축 증폭 효과)
- Entorhinal: y = -1.2 + 2.3x, R² = 0.89
- Inferior temporal: y = -0.96 + 2.0x, R² = 0.93
- PetSurfer noPVC vs Stanford: R² = 0.99-1.0 (거의 동일)

---

## Reference Region 선택 가이드

| Reference Region | 장점 | 단점 | 추천 용도 |
|------------------|------|------|-----------|
| **Inferior cerebellar GM** (persi) | 그룹 간 분리력 최고, tau 병리 적음 | Longitudinal 변화 감지에 약함 | **Cross-sectional** |
| **Cerebellar cortex GM** | Stanford/PetSurfer 기본, 널리 사용 | Superior cerebellum off-target binding 포함 가능 | Cross-sectional (A4 기본) |
| **Whole cerebellum** (GM+WM) | 안정적, 임상시험 표준 | WM 포함으로 signal 희석 | Amyloid PET 비교 |
| **Eroded subcortical WM** | **Longitudinal 변화** 감지에 최적 | Cross-sectional 그룹 분리 약함 | **Longitudinal** |
| **Cerebellar crus** | Cross-tracer 비교 (FTP vs MK-6240) | 작은 영역 | Harmonization |

> **Cross-sectional 분석**: inferior cerebellar GM 또는 cerebellar cortex GM 사용.
> **Longitudinal 분석**: eroded subcortical WM 사용 권장 (cerebellar reference는 변화 감지에 약함).

참고: [Schwarz et al., EJNMMI 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC8785682/)

---

## 사용 가이드

### Cross-sectional 분석 (baseline만)

`BASELINE.csv`의 `TAU_*_bl` 컬럼 사용 (Stanford pipeline, 447명, cerebellar cortex GM reference).

### Longitudinal tau 변화 분석

`imaging_SUVR_tau.csv` 직접 사용. 8개 시점, 192 ROI, 3종 reference region.

```python
import pandas as pd
tau = pd.read_csv('imaging_SUVR_tau.csv')
# 특정 ROI의 longitudinal 변화 (inferior cerebellar reference)
hippocampus = tau[tau['brain_region'] == 'Hippocampus_L']
hippocampus.pivot(index='BID', columns='VISCODE', values='suvr_persi')
```

### PVC가 필요한 분석

`imaging_Tau_PET_PetSurfer.csv` 사용. 위축이 심한 피험자군에서 SUVR 과소추정을 보정.
PVC 값은 non-PVC보다 체계적으로 높으므로 **PVC/non-PVC를 혼용하지 말 것**.

### Stanford vs PetSurfer vs Avid/Clark 중 선택

| 분석 목적 | 추천 소스 |
|-----------|----------|
| Baseline cross-sectional (ROI 다수) | Stanford (`TAU_*_bl` in BASELINE.csv) |
| Baseline cross-sectional (composite) | Avid/Clark (`imaging_SUVR_tau.csv`, V4) |
| Longitudinal 변화 | Avid/Clark (`imaging_SUVR_tau.csv`, 전 시점) |
| 위축 보정 필요 | PetSurfer (`imaging_Tau_PET_PetSurfer.csv`) |
| 다른 코호트와 비교 | Avid/Clark (표준 방법) |

---

## 파이프라인 코드 참조

```python
# src/a4/config.py
IMAGING_CSV_FILES = {
    'tausuvr': 'TAUSUVR_11Aug2025.csv',  # ← Stanford, baseline only
}

# src/a4/clinical.py _build_tau_suvr()
# ID 기준 drop_duplicates → TAU_ prefix + _bl suffix
```

---

## 참고 문헌

| 주제 | 참조 |
|------|------|
| Stanford pipeline | [Young et al., JAMA Neurology 2022](https://jamanetwork.com/journals/jamaneurology/fullarticle/2790807) |
| Avid/Clark method | [Clark et al., Lancet Neurol 2012](https://doi.org/10.1016/S1474-4422(11)70314-4) |
| Avid/Clark ROI | [Joshi et al., J Nucl Med 2015](https://doi.org/10.2967/jnumed.114.148981) |
| PetSurfer | [FreeSurfer Wiki: PetSurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/PetSurfer) |
| PVC for AV-1451 | [Baker et al., NeuroImage 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5671473/) |
| Reference region 비교 | [Schwarz et al., EJNMMI 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC8785682/) |
| Atlas 비교 | [Rolls et al., Sci Rep 2020](https://www.nature.com/articles/s41598-020-57951-6) |
| A4 imaging data guide | `Quick_Guide_to_A4_imaging_data_v1.1.pdf` (NFS) |
| A4 tau methods | `imaging_Tau_PET_methods.pdf` (NFS, Christina Young & Elizabeth Mormino) |
| A4 SUVR methods | `imaging_SUVR_methods.pdf` (NFS) |
| A4 MRI methods | `A4_VMRI_Volumetric_MRI_Methods.pdf` (NFS, James Brewer, UCSD) |
