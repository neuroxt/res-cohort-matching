# A4 Tau PET SUVR 데이터 소스 비교

A4/LEARN NFS에는 Tau PET SUVR 데이터가 **여러 파일**에 걸쳐 존재한다.
파이프라인 분석과 각 분석 프로젝트에 맞는 소스를 선택할 때 참고.

---

## 파일 요약

| 파일 | 위치 | 형식 | 규모 | 분석 파이프라인 | Reference Region |
|------|------|------|------|----------------|-----------------|
| **TAUSUVR_11Aug2025.csv** | `metadata/A4 Imaging data and docs/` | Wide | 447명 x 274열 | Stanford | 불명 (컬럼명에 미표기) |
| **imaging_Tau_PET_Stanford.csv** | `DEMO/Clinical/External Data/` | Wide | 447명 x 275열 | Stanford | 동일 (VISCODE=2 고정) |
| **imaging_SUVR_tau.csv** | `DEMO/Clinical/External Data/` | **Long** | 296,679행 (454명 x 8 visits x 192 regions) | AAL atlas | cerebellar / persi / crus |
| **TAUSUVR_PETSURFER_11Aug2025.csv** | `metadata/A4 Imaging data and docs/` | Wide | 445명 x 244열 | PetSurfer | 불명 |
| **imaging_Tau_PET_PetSurfer.csv** | `DEMO/Clinical/External Data/` | Wide | 445명 x 245열 | PetSurfer | 동일 |

---

## 상세 비교

### 1. TAUSUVR (Stanford) — 우리 파이프라인이 사용하는 소스

**파이프라인에서 `TAU_*_bl` 컬럼으로 BASELINE.csv/MERGED.csv에 들어가는 데이터.**

- 파일: `TAUSUVR_11Aug2025.csv`
- 형식: Wide (BID당 1행, ROI가 컬럼)
- 피험자: 447명 (V2 시점 단일)
- ROI: 273개 (FreeSurfer atlas 기반)
- 컬럼 예시: `Mean_Left_Hippocampus`, `Volume_mm3_Left_Hippocampus`, `Mean_ctx_lh_superiortemporal`
- SUVR 타입: `Mean_*` (SUVR), `Volume_mm3_*` (volume)
- 파이프라인 처리: `TAU_` prefix + `_bl` suffix → e.g., `TAU_Mean_Left_Hippocampus_bl`

`imaging_Tau_PET_Stanford.csv`는 이 파일과 **동일 데이터**임을 확인 (컬럼명 `.` → `_` 차이, VISCODE=2 컬럼 추가).

### 2. imaging_SUVR_tau.csv — Longitudinal, 다중 reference region

**우리 파이프라인에서 사용하지 않는 별도 파일.**

- 형식: Long (BID + VISCODE + brain_region당 1행)
- 피험자: 454명, **8개 방문** (V4, V6, V24, V27, V48, V66, V84, V999)
- ROI: 192개 (AAL atlas 기반)
- ROI 이름 예시: `Amygdala_L`, `Angular_R`, `Caudate_lh_VOI`, `Temporal_Mid_R`
- **SUVR 3종** (reference region별):
  - `suvr_cer` — cerebellar cortex reference
  - `suvr_persi` — persi (inferior cerebellar) reference
  - `suvr_crus` — cerebellar crus reference
- 코호트: A4 (262,695행), LEARN (32,832행), SF (1,152행)
- Ligand: Flortaucipir

### 3. PetSurfer — FreeSurfer 기반 대안 파이프라인

- 파일: `TAUSUVR_PETSURFER_11Aug2025.csv` 또는 `imaging_Tau_PET_PetSurfer.csv`
- 피험자: 445명
- ROI: 243개 (bilateral FreeSurfer regions)
- 컬럼 예시: `bi_Hippocampus`, `bi_Amygdala`, `bi_Caudate`
- Stanford과 다른 파이프라인으로 처리된 SUVR

---

## 핵심 차이 요약

| 항목 | TAUSUVR (Stanford) | imaging_SUVR_tau |
|------|-------------------|-----------------|
| 형식 | Wide (ROI = 컬럼) | Long (ROI = 행) |
| 시점 | **단일** (baseline만) | **다중** (8 visits) |
| Atlas | FreeSurfer | AAL |
| Reference region | 단일 (미표기) | **3종** (cer/persi/crus) |
| ROI 수 | 273 | 192 |
| ROI 이름 | `Mean_Left_Hippocampus` | `Amygdala_L`, `Temporal_Mid_R` |
| Longitudinal 사용 | 불가 | **가능** |
| 파이프라인 적용 | BASELINE.csv `TAU_*_bl` | 미적용 |

---

## 사용 가이드

### Cross-sectional 분석 (baseline만)

`BASELINE.csv`의 `TAU_*_bl` 컬럼 사용 (Stanford 파이프라인, 447명).

### Longitudinal tau 변화 분석

`imaging_SUVR_tau.csv` 직접 사용. 8개 시점 (V4~V999)의 192 ROI SUVR을 3종 reference region으로 제공.

```python
tau = pd.read_csv('imaging_SUVR_tau.csv')
# 특정 ROI의 longitudinal 변화
hippocampus = tau[tau['brain_region'] == 'Hippocampus_L']
hippocampus.pivot(index='BID', columns='VISCODE', values='suvr_cer')
```

### Reference region 선택

`imaging_SUVR_tau.csv`에서 분석 목적에 따라 선택:
- `suvr_cer` — cerebellar cortex (전통적 reference)
- `suvr_persi` — inferior cerebellar (tau 축적 영향 적음)
- `suvr_crus` — cerebellar crus

### PetSurfer vs Stanford

같은 FTP PET 데이터를 다른 파이프라인으로 처리한 결과. 분석 목적에 따라 선택.
- Stanford: 273 ROI (unilateral, Mean + Volume)
- PetSurfer: 243 ROI (bilateral)

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

## 참고

- Stanford Tau PET 분석 방법은 A4 Study imaging core에서 제공
- AAL atlas 기반 `imaging_SUVR_tau.csv`는 LONI에서 별도 배포
- Flortaucipir (FTP) = AV-1451 = [18F]T807
