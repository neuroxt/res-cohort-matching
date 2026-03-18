# A4/LEARN CSV 컬럼 프로파일

파이프라인 사용 CSV 17개의 컬럼별 타입·null률·유니크·값 범위.

**프로파일링 기준**: NFS 원본 CSV 전체 로드 (2026-03-09 기준).

---

## 1. metadata/ — Core Assessment CSVs

### PTDEMOG (`A4_PTDEMOG_PRV2_11Aug2025.csv`)
행: 6,945 | 컬럼: 14 | 키: BID+VISCODE | BID 유니크: 6,945

| 컬럼명 | dtype | null% | unique | 값 범위 / 상위값 |
|--------|-------|-------|--------|-----------------|
| BID | object | 0.0% | 6,945 | B1xxxxxxx 형식 |
| VISCODE | int64 | 0.0% | 1 | {1} (screening only) |
| EXAMDAY | float64 | 0.3% | 56 | -81~203 (mean=0.4) |
| PTGENDER | int64 | 0.0% | 2 | {1=Male, 2=Female} |
| PTAGE | float64 | 0.0% | 1,750 | 59.75~92.0 (mean=71.6) |
| PTETHNIC | int64 | 0.0% | 3 | {1, 2, 3} |
| PTRACE | object | 0.0% | 13 | 5(6,176), 4(339), 2(291) |
| PTLANG | int64 | 0.0% | 3 | {1, 2, 3} |
| PTPLANG | int64 | 0.0% | 2 | {0, 1} |
| PTEDUCAT | float64 | 1.3% | 32 | 0~36 (mean=16.4) |
| PTMARRY | float64 | 0.5% | 5 | {1, 2, 3, 4, 5} |
| PTNOTRT | float64 | 0.9% | 3 | {0, 1, 2} |
| PTHOME | float64 | 0.8% | 5 | {1, 2, 3, 4, 6} |
| update_stamp | object | 0.0% | 5 | timestamp |

---

### SUBJINFO (`A4_SUBJINFO_PRV2_11Aug2025.csv`)
행: 6,945 | 컬럼: 6 | 키: BID | BID 유니크: 6,945

| 컬럼명 | dtype | null% | unique | 값 범위 / 상위값 |
|--------|-------|-------|--------|-----------------|
| BID | object | 0.0% | 6,945 | B1xxxxxxx |
| AGEYR | float64 | 0.0% | 1,750 | 59.75~92.0 (mean=71.6) |
| APOEGN | object | **21.1%** | 6 | {E2/E2, E2/E3, E2/E4, E3/E3, E3/E4, E4/E4} |
| APOEGNPRSNFLGSNM | object | 21.1% | 2 | {N, Y} |
| LRNFLGSNM | object | 0.0% | 2 | {N, Y} — LEARN 참여 플래그 |
| update_stamp | object | 0.0% | 10 | timestamp |

---

### REGISTRY (`A4_REGISTRY_PRV2_11Aug2025.csv`)
행: 18,443 | 컬럼: 8 | 키: BID+VISCODE | BID 유니크: 6,945

| 컬럼명 | dtype | null% | unique | 값 범위 / 상위값 |
|--------|-------|-------|--------|-----------------|
| BID | object | 0.0% | 6,945 | 다회 방문 (BID당 최대 5행) |
| VISCODE | int64 | 0.0% | 5 | {1, 2, 3, 4, 5} |
| VISTYPE | int64 | 0.0% | 3 | {0, 1, 2} |
| EXAMDAY | float64 | 5.2% | 207 | 0~525 (mean=30.0) |
| NDREASON | float64 | **94.9%** | 5 | {2, 3, 7, 8, 9} |
| RESCRN | float64 | 62.3% | 2 | {0, 1} |
| PREBID | object | **99.0%** | 178 | 재스크리닝 이전 BID |
| update_stamp | object | 0.0% | 13 | timestamp |

---

### demography (`A4_demography.csv`)
행: 14,333 | 컬럼: 11 | 키: Subject ID+Visit | Subject ID 유니크: 4,486

| 컬럼명 | dtype | null% | unique | 값 범위 / 상위값 |
|--------|-------|-------|--------|-----------------|
| Subject ID | object | 0.0% | 4,486 | = BID |
| Project | object | 0.0% | 1 | {A4} |
| Sex | object | 0.0% | 3 | {F, M, X} |
| Research Group | object | 0.0% | 3 | {LEARN amyloidNE, amyloidE, amyloidNE} |
| Visit | object | 0.0% | 2 | {SCV2 (Screening PET), SCV4 (Screening MRI)} |
| Study Date | object | 0.0% | 5 | de-identified (1970-01-01 등) |
| Archive Date | object | 0.0% | 35 | 실제 아카이브 날짜 |
| Age | float64 | 0.0% | 220 | 0~116 (mean=68.6) — **de-identified, 신뢰 불가** |
| Description | object | 0.0% | 453 | Florbetapir <- PET Scan 등 |
| Type | object | 0.0% | 1 | {Processed} |
| Imaging Protocol | float64 | **100%** | 0 | 전체 null |

---

### MMSE (`A4_MMSE_PRV2_11Aug2025.csv`)
행: 6,774 | 컬럼: 39 | 키: BID+VISCODE | BID 유니크: 6,774

| 컬럼명 | dtype | null% | unique | 설명 |
|--------|-------|-------|--------|------|
| BID | object | 0.0% | 6,774 | |
| VISCODE | int64 | 0.0% | 1 | {1} — screening only |
| DONE | int64 | 0.0% | 2 | {0, 1} |
| WORDLIST | float64 | 0.3% | 5 | {1, 2, 3, 6, 9} |
| MMDATE~MMSTATE | float64 | 0.3% | 2 | {1=Correct, 2=Incorrect} — 지남력 10항목 |
| MMBALL~MMTREE | float64 | 0.3% | 2 | 기억등록 3항목 |
| MMTRIALS | float64 | 0.3% | 6 | 1~6 |
| MMDLTR~MMWLTR | object | ~0.3% | ~10 | WORLD 역순 글자 |
| MMWORLD | float64 | 0.4% | 6 | 0~5 |
| MMBALLDL~MMTREEDL | float64 | 0.3% | 2 | 기억회상 |
| MMWATCH~MMDRAW | float64 | 0.3% | 2 | 언어·구성 |
| **MMSCORE** | **float64** | **0.5%** | **15** | **9~30 (mean=28.6)** — 파이프라인 핵심 |
| update_stamp | object | 0.0% | 8 | |

---

### CDR (`A4_CDR_PRV2_11Aug2025.csv`)
행: 6,322 | 컬럼: 16 | 키: BID+VISCODE | BID 유니크: 6,322

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| BID | object | 0.0% | 6,322 | |
| VISCODE | int64 | 0.0% | 1 | {1} |
| DONE | int64 | 0.0% | 2 | {0, 1} |
| CDSPVERS | float64 | 1.5% | 2 | {1, 2} |
| MEMORY | float64 | 1.8% | 3 | {0, 0.5, 1} |
| ORIENT | float64 | 1.8% | 3 | {0, 0.5, 1} |
| JUDGE | float64 | 1.8% | 4 | {0, 0.5, 1, 2} |
| COMMUN | float64 | 1.7% | 3 | {0, 0.5, 1} |
| HOME | float64 | 1.7% | 3 | {0, 0.5, 1} |
| CARE | float64 | 1.7% | 2 | {0, 1} |
| **CDSOB** | **float64** | **1.8%** | **10** | **0~5 (mean=0.1)** |
| **CDGLOBAL** | **float64** | **1.8%** | **3** | **{0, 0.5, 1}** |
| update_stamp | object | 0.0% | 6 | |

---

### SPPACC (`A4_SPPACC_PRV2_11Aug2025.csv`)
행: 34,010 | 컬럼: 16 | 키: BID+VISCODE+PACCQSNUM | BID 유니크: 6,802

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| BID | object | 0.0% | 6,802 | BID당 5행(검사항목) |
| VISCODE | int64 | 0.0% | 1 | {1} |
| PACCQSNUM | object | 0.0% | 5 | {PACCRES1~4, PACCTS} |
| PACCD | object | 0.0% | 5 | COGDIGIT/COGLOGIC/FCSRT/MMSE Total Score |
| PACCRN | float64 | 0.7% | 6,355 | -23.2~8.6 (mean=-0.2) |
| PACCRN_RW | float64 | 20.5% | 98 | 0~95 (mean=39.5) |

---

## 2. metadata/A4 Imaging data and docs/ — Imaging CSVs

### PETSUVR (`A4_PETSUVR_PRV2_11Aug2025.csv`)
행: 35,936 | 컬럼: 12 | 키: BID+brain_region | BID 유니크: 4,492

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| BID | object | 0.0% | 4,492 | BID당 8행(8 brain regions) |
| VISCODE | int64 | 0.0% | 1 | {3} — Visit 3 (Screening Disclosure) |
| protocol | object | 0.0% | 1 | {A4} |
| scan_number | int64 | 0.0% | 1 | {1} |
| ligand | object | 0.0% | 1 | {Florbetapir} |
| scan_analyzed | object | 0.0% | 1 | {Yes} |
| **brain_region** | **object** | **0.0%** | **8** | **Composite_Summary, blcere_all, lanterior_cingulate, lfrontal, lparietal, ltemporal, rparietal, rtemporal** |
| **suvr_cer** | **float64** | **0.0%** | **178** | **0.45~2.58 (mean=1.1)** |
| **centiloid** | **float64** | **87.5%** | **116** | **-49.1~205.4 (mean=23.0)** — Composite_Summary 행에만 |
| update_stamp | object | 0.0% | 2 | |

---

### PETVADATA (`A4_PETVADATA_PRV2_11Aug2025.csv`)
행: 4,492 | 컬럼: 9 | 키: BID | BID 유니크: 4,492

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| BID | object | 0.0% | 4,492 | 1:1 (피험자당 1행) |
| PROTOCOL | object | 0.0% | 1 | {A4} |
| LIGAND | object | 0.0% | 1 | {Florbetapir} |
| **PMODSUVR** | **float64** | **0.0%** | **108** | **0.7~1.98 (mean=1.1)** |
| ELIGVI1 | object | 0.0% | 2 | {negative, positive} |
| ELIGVI2 | object | 90.7% | 2 | 2차 판독 (대부분 1차로 확정) |
| CONSENSUS | object | 99.6% | 3 | {negative, no agreement, positive} |
| **SCORE** | **object** | **0.0%** | **2** | **{negative, positive}** |

---

### VMRI (`A4_VMRI_PRV2_11Aug2025.csv`)
행: 1,271 | 컬럼: 53 | 키: BID+VISCODE | BID 유니크: 1,271

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| BID | object | 0.0% | 1,271 | |
| VISCODE | int64 | 0.0% | 1 | {4} — Screening MRI |
| LeftCorticalGrayMatter | float64 | 0.0% | 935 | 1.6~5.5 (mean=3.2) |
| RightCorticalGrayMatter | float64 | 0.0% | 825 | 1.4~4.4 (mean=2.8) |
| Left/RightLateralVentricle | float64 | 0.0% | ~1,240 | 4.2~73.6 |
| Left/RightThalamus | float64 | 0.0% | ~1,050 | 4.9~10.7 |
| Left/RightCaudate | float64 | 0.0% | ~906 | 1.0~8.1 |
| Left/RightPutamen | float64 | 0.0% | ~940 | 3.2~7.3 |
| Left/RightHippocampus | float64 | 0.0% | ~877 | 2.0~5.1 |
| Left/RightAmygdala | float64 | 0.0% | ~646 | 0.8~2.3 |
| Left/RightEntorhinal | float64 | 0.0% | ~945 | 1.3~5.9 |
| Left/RightFusiform | float64 | 0.0% | ~1,113 | 6.5~19.1 |
| Left/RightInferiorparietal | float64 | 0.0% | ~1,147 | 7.3~24.1 |
| Left/RightMiddletemporal | float64 | 0.0% | ~1,150 | 7.8~21.2 |
| Left/RightSuperiorfrontal | float64 | 0.0% | ~1,197 | 16.1~36.2 |
| ForebrainParenchyma | float64 | 0.0% | 1,263 | 688.8~1354.0 (mean=948.3) |
| IntraCranialVolume | float64 | 0.0% | 1,264 | 1189.2~2108.3 (mean=1526.3) |
| HOC | float64 | 0.0% | 1,266 | 0.31~0.87 (mean=0.7) |

**총 50개 ROI 컬럼 + update_stamp** (BID, VISCODE 제외 시 51개이나 update_stamp 포함). 모든 ROI null=0%.
단위: mL (cm³). 좌우 구분.

---

### TAUSUVR (`TAUSUVR_11Aug2025.csv`)
행: 447 | 컬럼: 274 | 키: ID (=BID) | ID 유니크: 447

| 컬럼 그룹 | 컬럼 수 | dtype | null% | 값 범위 |
|----------|---------|-------|-------|---------|
| ID | 1 | object | 0.0% | B1xxxxxxx (VISCODE 없음, BID만) |
| Mean_* (subcortical) | ~35 | float64 | 0–36.7% | SUVR 0.04~2.5 |
| Mean_ctx_lh_* (좌반구 피질) | 34 | float64 | 0.0% | SUVR 0.65~2.28 |
| Mean_ctx_rh_* (우반구 피질) | 34 | float64 | 0.0% | SUVR 0.69~2.47 |
| Volume_mm3_* (subcortical) | ~35 | float64 | 0–98% | 볼륨 mm³ |
| Volume_mm3_ctx_* (피질) | 68 | float64 | 0.0% | 볼륨 mm³ |
| bi_* (bilateral weighted) | 35 | float64 | 0–47.9% | SUVR (양측 가중평균) |
| bi_totalWM | 1 | float64 | 0.0% | 0.90~1.43 |

**주의**: `Mean_Left_vessel`/`Mean_Right_vessel` null 23.7%/36.7%, `bi_vessel` null 47.9%.

---

## 3. External Data/ — 혈액 바이오마커

### pTau217 (`biomarker_pTau217.csv`)
행: 4,538 | 컬럼: 18 | 키: BID+VISCODE+SUBSTUDY | BID 유니크: 1,653

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| SUBSTUDY | object | 0.0% | 3 | {A4, LEARN, SF} |
| BID | object | 0.0% | 1,653 | BID당 최대 4–5행(방문별) |
| **VISCODE** | **int64** | **0.0%** | **7** | **{1, 6, 9, 24, 66, 997, 999}** |
| TESTCD | object | 0.0% | 1 | {PTAU217} |
| ORRES | object | 2.7% | 591 | 수치 또는 `<LLOQ` (657건) |
| **ORRESRAW** | **float64** | **2.7%** | **658** | **0.072~2.74 (mean=0.3)** pg/mL |
| STAT | object | 97.3% | 2 | {NOT DONE, Not Done} |
| COLLECTION_DATE_DAYS_CONSENT | float64 | 0.1% | 1,088 | 0~3262 |
| COMMENT2 | object | 85.1% | 2 | ULOQ 초과 데이터 관련 |

---

### Plasma_Roche (`biomarker_Plasma_Roche_Results.csv`)
행: 13,418 | 컬럼: 14 | 키: BID+LBTESTCD+SUBSTUDY | BID 유니크: 2,345

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| SUBSTUDY | object | 0.0% | 3 | {A4, LEARN, SF} |
| BID | object | 0.0% | 2,345 | BID당 6행(6 검사항목) |
| VISCODE | int64 | 0.0% | 1 | {1} — screening only |
| **LBTESTCD** | **object** | **0.0%** | **6** | **{AMYLB40, AMYLB42, APOE4, GFAP, NF-L, TPP181}** |
| LABRESN | object | 11.7% | 2,970 | 수치 (BLQ 시 null) |
| LABORESU | object | 0.0% | 3 | {NG/ML, PG/ML, UG/ML} |
| LABRESC | object | 88.3% | 1 | {BLQ} — 정량한계 이하 플래그 |

---

### AB_Test (`biomarker_AB_Test.csv`)
행: 31,480 | 컬럼: 12 | 키: BID+LBTESTCD+SUBSTUDY | BID 유니크: 3,141

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| SUBSTUDY | object | 0.0% | 3 | {A4, LEARN, SF} |
| BID | object | 0.0% | 3,141 | BID당 최대 20행 |
| VISCODE | int64 | 0.0% | 1 | {3} |
| **LBTESTCD** | **object** | **0.0%** | **10** | **TP42/TP40, FP42/TP42 등 ratio 포함** |
| LBORRES | object | 0.0% | 10,711 | 수치, NOR, BLQ 혼재 |
| LBORRESU | object | **40.0%** | 1 | {pg/mL} — ratio 항목은 단위 없음 |

---

## 4. Derived Data/ — 세션 인덱스

### SV (`SV.csv`)
행: 103,351 | 컬럼: 9 | 키: BID+VISITCD | BID 유니크: 6,945

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| SUBSTUDY | object | 0.0% | 3 | {A4, LEARN, SF} |
| BID | object | 0.0% | 6,945 | BID당 최대 120행 |
| **VISITCD** | **int64** | **0.0%** | **125** | **1~999** — ≈VISCODE |
| VISIT | object | 0.0% | 143 | 방문명 문자열 |
| **SVSTDTC_DAYS_CONSENT** | **float64** | **3.4%** | **3,144** | **-174~3302 (mean=1001.3)** |
| SVSTDTC_DAYS_T0 | float64 | 14.0% | 3,277 | -406~3256 |
| **SVTYPE** | **object** | **0.0%** | **3** | **{Standard, Nonstandard, Not Done}** |
| SVUSEDTC_DAYS_CONSENT | int64 | 0.0% | 3,146 | -38~3316 |
| SVUSEDTC_DAYS_T0 | float64 | 10.7% | 3,300 | -406~3257 |

---

## 5. Raw Data/ — Longitudinal

### mmse_long (`mmse.csv`)
행: 26,765 | 컬럼: 41 | 키: BID+VISCODE | BID 유니크: 6,774

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| SUBSTUDY | object | 0.0% | 3 | {A4, LEARN, SF} |
| BID | object | 0.0% | 6,774 | BID당 최대 21행 |
| **VISCODE** | **int64** | **0.0%** | **23** | **1~999** (23개 unique 방문) |
| DONE | object | 0.0% | 2 | {No, Yes} |
| **MMSCORE** | **float64** | **1.1%** | **27** | **3~30 (mean=28.7)** |
| MMSELOC | object | 76.2% | 2 | {In clinic, Other Location} |
| MMSE (QC) | object | 74.0% | 3 | {Valid, Questionable, Not reviewed} |

PRV2 대비 컬럼 값이 object 타입(Correct/Incorrect vs 1/2). 파이프라인에서는 MMSCORE만 사용.

---

### cdr_long (`cdr.csv`)
행: 15,511 | 컬럼: 25 | 키: BID+VISCODE | BID 유니크: 6,322

| 컬럼명 | dtype | null% | unique | 값 범위 |
|--------|-------|-------|--------|---------|
| SUBSTUDY | object | 0.0% | 3 | {A4, LEARN, SF} |
| BID | object | 0.0% | 6,322 | BID당 최대 12행 |
| **VISCODE** | **int64** | **0.0%** | **17** | **1~999** (17개 unique 방문) |
| **CDGLOBAL** | **float64** | **2.5%** | **4** | **{0, 0.5, 1, 2}** |
| **CDSOB** | **float64** | **2.5%** | **24** | **0~14 (mean=0.3)** |
| **CDRSB** | **float64** | **2.5%** | **24** | **0~14 (mean=0.3)** — CDSOB 동일값 |
| MEMORY~CARE | float64 | 2.5% | 3–5 | CDR 6개 영역 |
| EPOCH | object | 2.5% | 5 | 연구 시기 구분 |
| CDADTC_DAYS_CONSENT | float64 | 2.5% | 2,188 | -14~3302 |
