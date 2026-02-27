# MERGED.csv Matching Validation Report

Generated: 2026-02-14 11:58

---

## Part A: ADNI1/GO/2/3 Comparison

### A1. Overall Summary

| Metric | Ref | New (non-ADNI4) |
|--------|-----|-----------------|
| Rows | 11,710 | 11,744 |
| Columns | 1,035 | 780 |
| Unique PTIDs | 2,631 | 2,632 |

**COLPROT distribution (new):**

- ADNI2: 4,670
- ADNI1: 3,681
- ADNI3: 2,779
- ADNIGO: 591

### A2. Modality Distribution (non-null I_{MOD} counts)

| Modality | Ref | New | Diff |
|----------|-----|-----|------|
| AV1451_6MM | 1,534 | 1,547 | +13 |
| AV1451_8MM | 1,570 | 1,570 | 0 |
| AV45_6MM | 2,860 | 2,876 | +16 |
| AV45_8MM | 3,154 | 3,154 | 0 |
| FBB_6MM | 587 | 598 | +11 |
| FLAIR | 3,373 | 3,389 | +16 |
| MK6240_6MM | 0 | 0 | 0 |
| T1 | 11,040 | 11,046 | +6 |
| T2_3D | 0 | 1 | +1 |
| T2_FSE | 2,094 | 2,097 | +3 |
| T2_STAR | 6,595 | 6,619 | +24 |
| T2_TSE | 1,705 | 1,707 | +2 |

### A3. PTID+VISCODE_FIX Index Comparison

- Common rows (intersection): **11,692**
- Ref-only rows: 18
- New-only rows: 52
- Coverage of ref: 99.8%

### A4. Per-Modality ImageUID Comparison (common rows)

| Modality | Both Have Value | Match | Mismatch | Match Rate |
|----------|-----------------|-------|----------|------------|
| T1 | 11,021 | 11,018 | 3 | 100.0% |
| AV45_8MM | 3,154 | 3,154 | 0 | 100.0% |
| AV45_6MM | 2,860 | 2,860 | 0 | 100.0% |
| AV1451_8MM | 1,570 | 1,570 | 0 | 100.0% |
| AV1451_6MM | 1,532 | 1,532 | 0 | 100.0% |
| FBB_6MM | 586 | 586 | 0 | 100.0% |
| FLAIR | 3,359 | 3,358 | 1 | 100.0% |
| T2_FSE | 2,094 | 2,084 | 10 | 99.5% |
| T2_TSE | 1,705 | 1,703 | 2 | 99.9% |
| T2_STAR | 6,576 | 6,571 | 5 | 99.9% |

### A5. Per-Modality AQUDATE Comparison (common rows)

| Modality | Both Have Value | Match | Match Rate |
|----------|-----------------|-------|------------|
| T1 | 11,021 | 11,021 | 100.0% |
| AV45_8MM | 3,154 | 3,154 | 100.0% |
| AV45_6MM | 2,860 | 2,860 | 100.0% |
| AV1451_8MM | 1,570 | 1,570 | 100.0% |
| AV1451_6MM | 1,532 | 1,532 | 100.0% |
| FBB_6MM | 586 | 586 | 100.0% |
| FLAIR | 3,359 | 3,359 | 100.0% |
| T2_FSE | 2,094 | 2,093 | 100.0% |
| T2_TSE | 1,705 | 1,705 | 100.0% |
| T2_STAR | 6,576 | 6,576 | 100.0% |

### A6. Demographics Comparison (common rows)

| Field | Both Have Value | Match | Match Rate |
|-------|-----------------|-------|------------|
| DX_bl | 11,490 | 10,327 | 89.9% |
| subjectSex | 11,669 | 11,663 | 99.9% |
| Apoe | 10,812 | 10,801 | 99.9% |

### A7. ImageUID Mismatch Samples

**T1** (showing up to 5):

| PTID | VISCODE_FIX | Ref I_{MOD} | New I_{MOD} |
|------|-------------|-------------|-------------|
| 022_S_5004 | m054 | 831854 | 831855 |
| 053_S_5202 | m030 | 515912 | 515913 |
| 127_S_6241 | m012 | 1226896 | 1226899 |

**FLAIR** (showing up to 5):

| PTID | VISCODE_FIX | Ref I_{MOD} | New I_{MOD} |
|------|-------------|-------------|-------------|
| 127_S_4928 | m024 | 444248 | 444258 |

**T2_FSE** (showing up to 5):

| PTID | VISCODE_FIX | Ref I_{MOD} | New I_{MOD} |
|------|-------------|-------------|-------------|
| 002_S_0685 | m000 | 18212 | 18213 |
| 006_S_1130 | m012 | 89143 | 89144 |
| 007_S_1222 | m000 | 37274 | 38487 |
| 021_S_0343 | m012 | 50699 | 50700 |
| 027_S_0850 | m000 | 23847 | 23848 |

**T2_TSE** (showing up to 5):

| PTID | VISCODE_FIX | Ref I_{MOD} | New I_{MOD} |
|------|-------------|-------------|-------------|
| 057_S_1269 | m060 | 297066 | 297068 |
| 941_S_1197 | m018 | 106927 | 106928 |

**T2_STAR** (showing up to 5):

| PTID | VISCODE_FIX | Ref I_{MOD} | New I_{MOD} |
|------|-------------|-------------|-------------|
| 037_S_6083 | m024 | 1268817 | 1268818 |
| 053_S_4813 | m114 | 1509972 | 1509973 |
| 053_S_6598 | m042 | 1592648 | 1592649 |
| 053_S_7109 | m000 | 1626155 | 1626156 |
| 116_S_4209 | m003 | 269322 | 269323 |

---

## Part B: ADNI4 Comparison

### B1. Overall Summary

| Metric | Ref | New (ADNI4 PTIDs) |
|--------|-----|-------------------|
| Rows | 1,711 | 3,725 |
| Columns | 898 | 782 |
| Unique PTIDs | 1,397 | 1,176 |

**New ADNI4 COLPROT distribution (PTID-based filter includes longitudinal):**

- ADNI3: 1,470
- ADNI4: 1,298
- ADNI2: 763
- ADNI1: 128
- ADNIGO: 66

### B2. VISCODE_FIX Format Difference

**VISCODE_FIX 형식이 다르므로 row-level 비교 불가:**

| Ref (top 5) | Count | New (top 5) | Count |
|-------------|-------|-------------|-------|
| 4_sc | 872 | m000 | 1154 |
| 4_init | 525 | m003 | 303 |
| 4_m12 | 304 | m024 | 286 |
| 4_m24 | 10 | m012 | 280 |
|  |  | m048 | 217 |

Ref uses `4_sc/4_init/4_m12` format; New uses `m000/m003/m072` format.

### B3. PTID Overlap

- Common PTIDs: **1,168**
- Ref-only PTIDs: 229
- New-only PTIDs: 8
- Coverage of ref PTIDs: 83.6%

### B4. Modality Distribution

| Modality | Ref | New | Note |
|----------|-----|-----|------|
| AV1451_6MM | 575 | 1,405 |  |
| AV1451_8MM | 0 | 847 |  |
| AV45_6MM | 423 | 1,276 |  |
| AV45_8MM | 0 | 911 |  |
| FBB_6MM | 331 | 672 |  |
| FLAIR | 1,045 | 2,417 |  |
| MK6240 | 130 | 0 | Our name: MK6240_6MM |
| MK6240_6MM | 0 | 108 | Ref name: MK6240 |
| T1 | 1,042 | 3,130 |  |
| T2_3D | 0 | 955 | Ref name: T2w |
| T2_FSE | 0 | 75 |  |
| T2_STAR | 908 | 2,776 |  |
| T2_TSE | 0 | 83 |  |
| T2w | 945 | 0 | Our name: T2_3D |

### B5. Per-Modality ImageUID Set Comparison (ADNI4 phase only)

Ref는 ADNI4 phase 데이터만 포함 → New도 COLPROT='ADNI4' 행만으로 비교:

| Ref Mod | Our Mod | Ref UIDs | New UIDs | Intersection | Jaccard |
|---------|---------|----------|----------|--------------|---------|
| T1 | T1 | 1,042 | 1,012 | 882 | 75.3% |
| T2_STAR | T2_STAR | 908 | 881 | 253 | 16.5% |
| FLAIR | FLAIR | 1,045 | 1,016 | 979 | 90.5% |
| AV45_6MM | AV45_6MM | 423 | 399 | 399 | 94.3% |
| AV1451_6MM | AV1451_6MM | 575 | 549 | 549 | 95.5% |
| FBB_6MM | FBB_6MM | 331 | 306 | 304 | 91.3% |
| MK6240 | MK6240_6MM | 130 | 108 | 108 | 83.1% |
| T2w | T2_3D | 945 | 955 | 891 | 88.3% |

---

## Part C: ADNI4 Matching Issue Analysis

### C1. AQUDATE-Based ImageUID Comparison

VISCODE_FIX가 다르므로 PTID+AQUDATE 기준으로 UID를 비교합니다.

| Ref Mod | Our Mod | Common PTID+AQUDATE | Same UID | Diff UID | Match Rate |
|---------|---------|---------------------|----------|----------|------------|
| T1 | T1 | 944 | 842 | 102 | 89.2% |
| T2_STAR | T2_STAR | 824 | 219 | 605 | 26.6% |
| FLAIR | FLAIR | 949 | 920 | 29 | 96.9% |
| AV45_6MM | AV45_6MM | 398 | 398 | 0 | 100.0% |
| AV1451_6MM | AV1451_6MM | 549 | 549 | 0 | 100.0% |
| FBB_6MM | FBB_6MM | 305 | 304 | 1 | 99.7% |
| MK6240 | MK6240_6MM | 108 | 108 | 0 | 100.0% |
| T2w | T2_3D | 891 | 891 | 0 | 100.0% |

### C2. Ref-only PTID 원인 분석

- Ref PTIDs: 1,397
- New PTIDs: 1,176
- Ref-only PTIDs: 229

**Ref-only 원인 분류:**

| 원인 | 수 | 설명 |
|------|-----|------|
| NFS 전체 DCM 부재 | 224 | ADNI4/ORIG, ADNI_New 양쪽 모두 DCM 파일 없음 |
| 비-T1 모달리티만 존재 | 3 | T1 없어 T1 기반 매칭 불가 |
| T1 존재 (기타) | 2 | DCM+T1 있으나 매칭 안 됨 (추가 조사 필요) |

- Ref(기존 코드)는 XML 메타데이터 기반 → 물리적 DCM 없이도 행 생성 가능
- New(v4 코드)는 DCM 인벤토리 기반 → DCM 없으면 매칭 불가
- **파이프라인 버그 아님** — 데이터 가용성 차이

**비-T1 PTID 상세:**

| PTID | 보유 모달리티 |
|------|---------------|
| 013_S_10689 | NAV4694_6MM |
| 123_S_7125 | DTI |
| 131_S_10369 | FMRI, NAV4694_6MM |

**T1 존재하나 매칭 안 된 PTID (추가 조사 필요):**

| PTID | 보유 모달리티 |
|------|---------------|
| 011_S_7112 | ASL, DTI, DTI_MB, FLAIR, FMRI, T1, T2_3D, T2_STAR |
| 013_S_6970 | DTI, FLAIR, FMRI, T1, T2_STAR |

**T1 기준:**
- Ref T1 PTIDs: 973
- New T1 PTIDs: 1,135 (NEW가 더 많음)
- Ref-only T1 PTIDs: 22

### C3. VISCODE_FIX System Difference Impact

Ref(기존 코드)는 ADNI4 전용 VISCODE(`4_sc`, `4_init`, `4_m12`)를 사용하고,
New(v4 코드)는 표준 month 기반(`m000`, `m003`, `m012`)을 사용합니다.

**영향:**
- Row-level 비교 불가 (PTID+VISCODE_FIX 교집합 = 0)
- 동일 촬영일에도 다른 EXAMDATE 행 매칭 → 다른 UID 선택
- 다중 시리즈 모달리티(T2_STAR: 세션당 최대 10개)에서 영향 극대화
- **이것은 시스템 차이이며 버그가 아님** — 추후 VISCODE 매핑 테이블로 해결 가능

---

## Notes

- **subjectAge**: Empty in new MERGED.csv due to missing `birth_dates.csv`.
- **weightKg / Flip Angle**: Not available from non-XML sources.
- **MK6240 vs MK6240_6MM, T2w vs T2_3D**: Modality name mapping not yet applied. Direct column comparison only works for identically-named modalities.
- **Modalities not compared**: DTI, DTI_MB, FMRI, HIPPO, ASL, NAV4694_6MM, PI2620_6MM (not in ref or not yet run).

