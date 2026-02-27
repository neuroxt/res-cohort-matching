# ADNI4 VISCODE_FIX Error Report

**Date**: 2026-02-14
**Author**: ADNI_match Pipeline Analysis

---

## 1. Summary

ADNI3/4 프로토콜에서 MRI 촬영일(AQUDATE)과 ADNIMERGE 방문일(EXAMDATE) 간 차이가 매칭 threshold(180일)를 초과하여 `VISCODE_FIX = error`로 처리되는 케이스가 발생. ADNI1/GO/2 대비 ADNI3/4에서 이 문제가 유의미하게 증가.

| Protocol | Error Scans | Total Scans | Error Rate | Error PTIDs |
|----------|-------------|-------------|------------|-------------|
| ADNI1    | 2           | 9,115       | 0.02%      | 1           |
| ADNIGO   | 0           | 1,193       | 0.00%      | 0           |
| ADNI2    | 2           | 9,313       | 0.02%      | 1           |
| **ADNI3**| **16**      | **2,650**   | **0.6%**   | **10**      |
| **ADNI4**| **8**       | **1,149**   | **0.7%**   | **8**       |

---

## 2. Root Cause

### 2.1 매칭 메커니즘

`matching.py`의 매칭 로직:

1. MRI 촬영일(AQUDATE) 기준으로 ADNIMERGE의 가장 가까운 방문(EXAMDATE) 탐색
2. `AQUDATE - EXAMDATE_bl`로 DAYSDELTA 계산
3. DAYSDELTA를 가장 가까운 표준 VISCODE (m000, m003, m006, ...) 에 매핑
4. 표준 VISCODE와의 차이가 **threshold(180일)** 초과 시 → `error`

```python
# config.py
MODALITY_CONFIG = {
    'T1': {'threshold': 180, ...},
    ...
}

# matching.py → calc_viscode()
delta = np.abs(MONTH_KEYS - daysdelta)
idx = np.argmin(delta)
if delta[idx] > threshold:
    return 'error'
```

### 2.2 ADNI4 문제 패턴

Error 8건 모두 동일 패턴: **MRI 촬영이 ADNIMERGE 첫 방문보다 6~9개월 전에 수행됨.**

| PTID | AQUDATE_T1 | EXAMDATE m000 | 차이 |
|------|-----------|--------------|------|
| 009_S_10280 | 2024-10-31 | 2025-05-30 | +211일 |
| 022_S_10143 | 2024-07-02 | 2025-03-20 | +261일 |
| 022_S_10256 | 2024-03-14 | 2024-11-22 | +253일 |
| 023_S_10179 | 2024-07-24 | 2025-02-12 | +203일 |
| 037_S_10131 | 2024-08-16 | 2025-02-18 | +186일 |
| 052_S_10246 | 2024-09-25 | 2025-05-07 | +224일 |
| 052_S_10252 | 2024-10-01 | 2025-05-13 | +224일 |
| 073_S_10228 | 2024-09-12 | 2025-05-15 | +245일 |

**원인 추정**:
- Screening MRI가 enrollment 전에 촬영되었으나, ADNIMERGE에는 enrollment 이후 방문만 기록
- 또는 ADNIMERGE 데이터가 아직 업데이트되지 않은 상태 (ADNI4는 진행 중인 study)

### 2.3 ADNI3 동일 패턴

ADNI3에서도 동일 패턴 확인 (16건, 10 PTIDs):

| PTID | AQUDATE | Nearest Visit | 차이 |
|------|---------|---------------|------|
| 037_S_6046 | 2017-07-17 | m000 (2018-03-20) | +246일 |
| 109_S_6220 | 2018-04-11 | m003 (2018-12-17) | +250일 (2건) |
| 109_S_6221 | 2018-07-17 | m003 (2019-01-15) | +182일 (2건) |
| 109_S_6300 | 2018-07-25 | m000 (2019-03-05) | +223일 (2건) |
| 109_S_6405 | 2018-07-27 | m000 (2019-03-28) | +244일 (2건) |
| ... | | | |

Site 109는 특히 집중적으로 문제 발생 (4 PTIDs, 8 scans).

---

## 3. AQUDATE-EXAMDATE Gap 분석 (프로토콜별)

### 3.1 정상 매칭된 스캔의 gap 분포

| Protocol | n | Mean | Median | Max | >90일 | >90일 % |
|----------|---|------|--------|-----|-------|---------|
| ADNI1 | 9,113 | 9일 | 3일 | 181일 | 44 | 0.5% |
| ADNIGO | 1,193 | 11일 | 1일 | 131일 | 8 | 0.7% |
| ADNI2 | 9,311 | 7일 | 0일 | 176일 | 78 | 0.8% |
| **ADNI3** | **2,634** | **19일** | **8일** | **180일** | **113** | **4.3%** |
| **ADNI4** | **1,141** | **30일** | **19일** | **176일** | **94** | **8.2%** |

### 3.2 ADNI4 상세 gap 분포

| Gap | Count | Cumulative % |
|-----|-------|-------------|
| 0일 | 176 | 15.4% |
| ≤7일 | 348 | 30.5% |
| ≤14일 | 481 | 42.2% |
| ≤30일 | 761 | 66.7% |
| ≤60일 | 954 | 83.6% |
| ≤90일 | 1,039 | 91.1% |
| ≤120일 | 1,096 | 96.1% |
| ≤180일 | 1,133 | 99.3% |

### 3.3 Key Observation

- ADNI1/GO/2: 촬영일과 방문일이 거의 일치 (median 0~3일)
- **ADNI3**: median 8일로 증가, >90일 비율 4.3%
- **ADNI4**: median 19일로 더 증가, >90일 비율 **8.2%**
- ADNI4에서는 정상 매칭된 스캔조차 최대 176일 gap (threshold 근접)

이는 ADNI4 운영 방식의 변화를 반영:
- 원격/분산 촬영 증가
- Screening과 enrollment 간 지연 증가
- Multi-site coordination으로 인한 스케줄 변동

---

## 4. 전처리 파이프라인 영향

### 4.1 N4/VA/FastSurfer → ADNI_n4/va/seg 통합 시 영향

`remap_proc_viscode.py`가 T1_all.csv의 VISCODE_FIX를 기준으로 이동하므로,
`VISCODE_FIX = error`인 8건(×3 modality = 24 files)은 이동 불가.

| 항목 | 값 |
|------|---|
| 이동 성공 | 3,279 files (1,093 × 3) |
| 이동 불가 (error) | 24 files (8 × 3) |
| 이동 불가율 | 0.7% |

### 4.2 0_nii_fast_temp Coverage 영향

`0_nii_fast_temp`의 old ADNI4 전처리 결과 대비 ADNI_New coverage:

| Modality | Old (ADNI4) | Covered | Coverage |
|----------|-------------|---------|----------|
| N4 | 1,033 | 857 (PTID,VIS) | 92.1% |
| FastSurfer | 932 | 857 (PTID,VIS) | 92.1% |
| VA | 933 | 857 (PTID,VIS) | 92.1% |

Missing 8 PTIDs = VISCODE_FIX error 8건과 정확히 일치.

---

## 5. 대응 방안

### Option A: Threshold 확대 (권장하지 않음)
- 180일 → 270일로 확대하면 8건 모두 해결 가능
- 그러나 잘못된 방문 매칭 위험 증가 (false positive)

### Option B: Screening visit 별도 처리 (중장기)
- ADNIMERGE 외부 소스(ADSL, registry 등)에서 screening 날짜 확보
- Screening MRI를 별도 VISCODE (예: `scr`) 로 매핑
- 현재는 ADNIMERGE에 enrollment 이후 방문만 포함

### Option C: 수동 매핑 (단기 해결)
- 8건에 대해 m000으로 강제 매핑 (screening MRI → baseline 취급)
- T1_all.csv 수정 또는 remap_proc_viscode.py에 fallback 로직 추가

### Option D: 현상 유지 (현재)
- 8건(0.7%)은 무시하고 진행
- ADNIMERGE 업데이트 시 자동으로 해결될 가능성 있음

---

## 6. Appendix: Error PTID 상세

| PTID | DX_bl | AQUDATE | I_UID | EXAMDATE m000 | Gap |
|------|-------|---------|-------|---------------|-----|
| 009_S_10280 | CN | 2024-10-31 | I11040356 | 2025-05-30 | 211d |
| 022_S_10143 | CN | 2024-07-02 | I10869210 | 2025-03-20 | 261d |
| 022_S_10256 | CN | 2024-03-14 | I11145620 | 2024-11-22 | 253d |
| 023_S_10179 | CN | 2024-07-24 | I10898730 | 2025-02-12 | 203d |
| 037_S_10131 | CN | 2024-08-16 | I11263029 | 2025-02-18 | 186d |
| 052_S_10246 | CN | 2024-09-25 | I10964484 | 2025-05-07 | 224d |
| 052_S_10252 | CN | 2024-10-01 | I10968674 | 2025-05-13 | 224d |
| 073_S_10228 | MCI | 2024-09-12 | I10973554 | 2025-05-15 | 245d |

모두 ADNI4 신규 피험자, 7/8이 CN (정상 대조군).
DCM 데이터는 `DCM/MRI/{PTID}/` 경로에 정상 존재.
