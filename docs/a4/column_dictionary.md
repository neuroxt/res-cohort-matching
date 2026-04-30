# A4/LEARN MERGED.csv 출력 컬럼 사전

`build_session_merged()` + `_reorder_columns()`가 생성하는 MERGED.csv의 모든 컬럼.

**참조 코드**: `src/a4/clinical.py`, `src/a4/pipeline.py`

> MERGED.csv는 session-centric (SV.csv 전체 세션 기준).
> 인덱스: (BID, SESSION_CODE). 예상 행 수: ~65K (기존 imaging-only ~11.8K 대비).
> per-modality `*_unique.csv`는 기존과 동일 구조.

---

## 인덱스 컬럼

| 컬럼명 | 소스 | 타입 | 설명 |
|--------|------|------|------|
| **BID** | SV.csv | string | 피험자 ID (`B1xxxxxxx`, 9자리) |
| **SESSION_CODE** | SV.csv VISITCD | string | 3자리 방문코드 (`001`~`999`), VISITCD zero-pad |

---

## 1. Timing

| 컬럼명 | 소스 | 타입 | null 예상 | 설명 |
|--------|------|------|----------|------|
| DAYS_CONSENT | SV.csv SVSTDTC_DAYS_CONSENT | float | ~0% | 동의일 기준 경과일. 음수 가능(-174~3302). |

---

## 2. Demographics (BID 수준, 모든 세션 행에 동일 값 반복)

| 컬럼명 | 소스 | 타입 | null 예상 | 설명 |
|--------|------|------|----------|------|
| PTGENDER | PTDEMOG → `map_ptgender()` | string | <1% | `Male` / `Female` |
| PTAGE | AGEYR + DAYS_CONSENT/365.25 | float | <1% | **세션별 동적 연령** (screening 고정값 아님) |
| PTEDUCAT | PTDEMOG | float | ~1.3% | 교육연수 (0~36, mean=16.4) |
| APOEGN | SUBJINFO → `format_apoe_genotype()` | string | ~21% | `e3/e3`, `e3/e4` 등 (ADNI 호환 소문자) |
| AGEYR | SUBJINFO | float | <1% | 동의 시 연령 (PTAGE 계산 기반) |
| LRNFLGSNM | SUBJINFO | string | 0% | LEARN 참여 플래그 (`Y`/`N`) |
| Research_Group | SUBJINFO + demography | string | <1% | `amyloidE`, `LEARN amyloidNE` (amyloidNE는 기본 제외) |

---

## 3. Amyloid Status (`_bl` suffix, baseline 단일 시점)

| 컬럼명 | 소스 | 타입 | null 예상 | 설명 |
|--------|------|------|----------|------|
| AMY_STATUS_bl | PETVADATA.SCORE | string | ~35% | `positive` / `negative` |
| AMY_SUVR_bl | PETVADATA.PMODSUVR | float | ~35% | PMOD composite SUVR (0.7~1.98) |
| AMY_SUVR_CER_bl | PETSUVR[Composite_Summary].suvr_cer | float | ~35% | cerebellar reference SUVR |
| AMY_CENTILOID_bl | PETSUVR[Composite_Summary].centiloid | float | ~87% | Centiloid 변환값 (-49~205) |

**null 이유**: PETVADATA/PETSUVR = screening PET 참여자만(4,492/6,945 BID).
centiloid는 Composite_Summary 행에만 존재(87.5% null in 원본).

---

## 4. Clinical Baseline (`_bl` suffix)

| 컬럼명 | 소스 | 타입 | null 예상 | 설명 |
|--------|------|------|----------|------|
| MMSE_bl | MMSE(PRV2) MMSCORE, 최초 방문 | float | ~3% | 9~30 (mean=28.6) |
| CDGLOBAL_bl | CDR(PRV2) CDGLOBAL, 최초 방문 | float | ~9% | {0, 0.5, 1} |
| CDRSB_bl | CDR(PRV2) CDSOB → rename | float | ~9% | 0~5 (mean=0.1) |

---

## 5. Clinical Longitudinal (세션별, `_bl` suffix 없음)

| 컬럼명 | 소스 | 타입 | null 예상 | 설명 |
|--------|------|------|----------|------|
| MMSE | mmse.csv(Raw Data) MMSCORE | float | ~80% | 해당 세션에서 측정된 MMSE (3~30). 측정 안 된 세션은 NaN. |
| CDGLOBAL | cdr.csv(Raw Data) CDGLOBAL | float | ~85% | 해당 세션에서 측정된 CDR global. |
| CDRSB | cdr.csv(Raw Data) CDSOB → rename | float | ~85% | 해당 세션에서 측정된 CDR-SB. |

**주의**: `_bl` 컬럼은 BID 수준(모든 행 동일), longitudinal 컬럼은 세션 수준.

---

## 6. pTau217 (방문별 pivot, BID 수준)

### A4 피험자

| 컬럼명 | 소스 VISCODE | 타입 | null 예상 | 설명 |
|--------|-------------|------|----------|------|
| PTAU217_BL | 6 (Baseline) | float | ~75% | pg/mL |
| PTAU217_WK12 | 9 (wk12) | float | ~85% | A4 only |
| PTAU217_WK240 | 66 (wk240) | float | ~90% | End DB |
| PTAU217_OLE | 997 (Final OLE) | float | ~95% | OLE 종료 시 |
| PTAU217_ET | 999 (Early Term) | float | ~95% | 조기종료 시 |

### LEARN 피험자

| 컬럼명 | 소스 VISCODE | 타입 | null 예상 | 설명 |
|--------|-------------|------|----------|------|
| PTAU217_SCR | 1 (Screening) | float | ~95% | |
| PTAU217_WK72 | 24 (wk72) | float | ~95% | |
| PTAU217_WK240 | 66 (wk240) | float | ~98% | A4와 컬럼 공유 |
| PTAU217_ET | 999 (Early Term) | float | ~98% | A4와 컬럼 공유 |

각 값 컬럼마다 `{컬럼명}_LLOQ` boolean 플래그 동반 (ORRES가 `<LLOQ`이면 True).

---

## 7. Modality / Path

| 컬럼명 | 소스 | 타입 | null 예상 | 설명 |
|--------|------|------|----------|------|
| MODALITIES | inventory (computed) | string | ~70% | 해당 세션에 존재하는 모달리티 (comma-sep: `T1,FLAIR,FBP`). 이미징 없는 세션은 NaN. |

### Per-modality NII 경로

| 컬럼명 | 모달리티 | 설명 |
|--------|---------|------|
| T1_NII_PATH | T1 | T1w MRI .nii.gz 절대경로 |
| FLAIR_NII_PATH | FLAIR | FLAIR MRI |
| T2_SE_NII_PATH | T2_SE | T2 Spin Echo |
| T2_STAR_NII_PATH | T2_STAR | T2* GRE |
| FMRI_REST_NII_PATH | FMRI_REST | resting-state fMRI |
| B0CD_NII_PATH | B0CD | b0 field map |
| FBP_NII_PATH | FBP | Florbetapir PET |
| FTP_NII_PATH | FTP | Flortaucipir PET |

---

## 8. MRI Protocol Metadata (per-modality, from JSON sidecar)

각 MRI 모달리티(T1, FLAIR, T2_SE, T2_STAR, FMRI_REST, B0CD)에 대해:

| 컬럼명 패턴 | 소스 JSON key | 타입 | 설명 |
|------------|--------------|------|------|
| protocol/{MOD}/TE | EchoTime | string | Echo Time (ms) |
| protocol/{MOD}/TR | RepetitionTime | string | Repetition Time (ms) |
| protocol/{MOD}/TI | InversionTime | string | Inversion Time (ms) |
| protocol/{MOD}/Flip Angle | FlipAngle | string | Flip Angle (°) |
| protocol/{MOD}/Slice Thickness | SliceThickness | string | Slice Thickness (mm) |
| protocol/{MOD}/Manufacturer | Manufacturer | string | 장비 제조사 |
| protocol/{MOD}/Mfg Model | ManufacturersModelName | string | 장비 모델명 |
| protocol/{MOD}/Field Strength | MagneticFieldStrength | string | 자기장 세기 (T) |
| protocol/{MOD}/description | SeriesDescription | string | 시리즈 설명 |
| protocol/{MOD}/Protocol Name | ProtocolName | string | 프로토콜명 |

총 10 fields × 6 MRI modalities = 최대 60 protocol 컬럼.

---

## 9. PET Protocol Metadata (per-modality, from JSON sidecar)

각 PET 모달리티(FBP, FTP)에 대해:

| 컬럼명 패턴 | 소스 JSON key | 타입 | 설명 |
|------------|--------------|------|------|
| protocol/{MOD}/Tracer | Radiopharmaceutical | string | 추적자명 |
| protocol/{MOD}/Injected Dose | InjectedRadioactivity | string | 주입 방사능량 |
| protocol/{MOD}/Frame Duration | FrameDuration | string | 프레임 시간 |
| protocol/{MOD}/Recon Method | ReconstructionMethod | string | 재구성 방법 |
| protocol/{MOD}/Manufacturer | Manufacturer | string | |
| protocol/{MOD}/Mfg Model | ManufacturersModelName | string | |
| protocol/{MOD}/Slice Thickness | SliceThickness | string | |

총 7 fields × 2 PET modalities = 최대 14 protocol 컬럼.

---

## 10. VMRI (MRI 볼륨, `_bl` suffix, BID 수준)

50개 FreeSurfer ROI 컬럼 + update_stamp (BID/VISCODE 제외 후 51개이나 ROI는 50개). 모두 `VMRI_` 접두사 + `_bl` suffix.

| 컬럼명 패턴 | 원본 컬럼 | 단위 | null 예상 |
|------------|----------|------|----------|
| VMRI_LeftCorticalGrayMatter_bl | LeftCorticalGrayMatter | mL | ~82% |
| VMRI_RightCorticalGrayMatter_bl | RightCorticalGrayMatter | mL | ~82% |
| VMRI_LeftLateralVentricle_bl | LeftLateralVentricle | mL | ~82% |
| VMRI_RightLateralVentricle_bl | RightLateralVentricle | mL | ~82% |
| VMRI_LeftThalamus_bl | LeftThalamus | mL | ~82% |
| VMRI_RightThalamus_bl | RightThalamus | mL | ~82% |
| VMRI_LeftCaudate_bl | LeftCaudate | mL | ~82% |
| VMRI_RightCaudate_bl | RightCaudate | mL | ~82% |
| VMRI_LeftPutamen_bl | LeftPutamen | mL | ~82% |
| VMRI_RightPutamen_bl | RightPutamen | mL | ~82% |
| VMRI_LeftPallidum_bl | LeftPallidum | mL | ~82% |
| VMRI_RightPallidum_bl | RightPallidum | mL | ~82% |
| VMRI_LeftHippocampus_bl | LeftHippocampus | mL | ~82% |
| VMRI_RightHippocampus_bl | RightHippocampus | mL | ~82% |
| VMRI_LeftAmygdala_bl | LeftAmygdala | mL | ~82% |
| VMRI_RightAmygdala_bl | RightAmygdala | mL | ~82% |
| VMRI_LeftVentralDiencephalon_bl | LeftVentralDiencephalon | mL | ~82% |
| VMRI_RightVentralDiencephalon_bl | RightVentralDiencephalon | mL | ~82% |
| VMRI_Left/RightCerebellarWhiteMatter_bl | Cerebellar WM | mL | ~82% |
| VMRI_Left/RightCerebellarGrayMatter_bl | Cerebellar GM | mL | ~82% |
| VMRI_Left/RightWMHypo_bl | WM Hypointensities | mL | ~82% |
| VMRI_Left/RightEntorhinal_bl | Entorhinal cortex | mL | ~82% |
| VMRI_Left/RightFusiform_bl | Fusiform gyrus | mL | ~82% |
| VMRI_Left/RightInferiorparietal_bl | Inferior parietal | mL | ~82% |
| VMRI_Left/RightInferiortemporal_bl | Inferior temporal | mL | ~82% |
| VMRI_Left/RightMiddletemporal_bl | Middle temporal | mL | ~82% |
| VMRI_Left/RightParahippocampal_bl | Parahippocampal | mL | ~82% |
| VMRI_Left/RightSuperiorfrontal_bl | Superior frontal | mL | ~82% |
| VMRI_Left/RightSuperiorparietal_bl | Superior parietal | mL | ~82% |
| VMRI_Left/RightSuperiortemporal_bl | Superior temporal | mL | ~82% |
| VMRI_Left/RightTemporalpole_bl | Temporal pole | mL | ~82% |
| VMRI_Brainstem_bl | Brainstem | mL | ~82% |
| VMRI_ForebrainParenchyma_bl | ForebrainParenchyma | mL | ~82% |
| VMRI_IntraCranialVolume_bl | IntraCranialVolume | mL | ~82% |
| VMRI_HOC_bl | HOC (ratio) | float | ~82% |

**null 이유**: VMRI = 1,271 BID only (전체 6,945의 18.3%). session-centric MERGED에서는 ~82% null.

---

## 11. Tau SUVR (`_bl` suffix, BID 수준)

272개 FreeSurfer ROI 컬럼 + update_stamp (ID 제외 후 273개이나 ROI는 272개). 모두 `TAU_` 접두사 + `_bl` suffix.

| 컬럼 그룹 | 예시 | 컬럼 수 | null 예상 |
|----------|------|---------|----------|
| TAU_Mean_* (subcortical) | TAU_Mean_3rd_Ventricle_bl | ~35 | ~94% |
| TAU_Mean_ctx_lh_* (좌반구 피질) | TAU_Mean_ctx_lh_entorhinal_bl | 34 | ~94% |
| TAU_Mean_ctx_rh_* (우반구 피질) | TAU_Mean_ctx_rh_entorhinal_bl | 34 | ~94% |
| TAU_Volume_mm3_* | TAU_Volume_mm3_Left_Hippocampus_bl | ~103 | ~94% |
| TAU_bi_* (bilateral weighted) | TAU_bi_entorhinal_bl | ~35 | ~94% |
| TAU_bi_totalWM_bl | bilateral total WM | 1 | ~94% |

**null 이유**: TAUSUVR = 447 BID only (전체의 6.4%).

---

## 컬럼 정렬 순서 (`_reorder_columns`)

`pipeline.py`의 `_reorder_columns()`에 의해 다음 순서로 정렬:

1. **Timing**: DAYS_CONSENT
2. **Demographics**: PTGENDER, PTAGE, PTEDUCAT, APOEGN, AGEYR, LRNFLGSNM, Research_Group
3. **Amyloid**: AMY_STATUS_bl, AMY_SUVR_bl, AMY_SUVR_CER_bl, AMY_CENTILOID_bl
4. **Clinical**: MMSE_bl, MMSE, CDGLOBAL_bl, CDGLOBAL, CDRSB_bl, CDRSB
5. **pTau217**: PTAU217_* (모든 visit별 컬럼)
6. **Modality**: MODALITIES, (legacy: MODALITY, NII_PATH)
7. **MRI paths + protocols**: T1_NII_PATH, protocol/T1/*, FLAIR_NII_PATH, ..., B0CD_NII_PATH, protocol/B0CD/*
8. **PET paths + protocols**: FBP_NII_PATH, protocol/FBP/*, FTP_NII_PATH, protocol/FTP/*
9. **VMRI**: VMRI_*_bl (50 ROI + update_stamp)
10. **Tau SUVR**: TAU_*_bl (272 ROI + update_stamp)
11. **Remainder**: 위 그룹에 포함되지 않은 잔여 컬럼

---

## per-modality `*_unique.csv` 컬럼 (참고)

`build_modality_csv()`가 생성하는 per-modality CSV 구조:

| 컬럼명 | 설명 |
|--------|------|
| BID | (인덱스) |
| SESSION_CODE | (인덱스) |
| MODALITY | 모달리티 키 (e.g., `T1`) |
| NII_PATH | .nii.gz 절대경로 |
| protocol/{MOD}/* | JSON sidecar 메타데이터 |
| (clinical cols) | build_clinical_table() 전체 컬럼 |
| PTAGE | 세션별 동적 연령 (session_ages 덮어쓰기) |
| MMSE, CDGLOBAL, CDRSB | longitudinal cognitive (세션 수준) |
