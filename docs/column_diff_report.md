# Ref vs New MERGED.csv Column Difference Report

Generated: 2026-02-14

## Overview

| Metric | Ref MERGED.csv | New MERGED.csv |
|--------|---------------|----------------|
| Rows | 11,710 | 13,042 |
| Columns | 1,037 | 782 |
| Unique PTIDs | 2,631 | 3,278 |
| Common rows (PTID+VISCODE_FIX) | 11,692 | 11,692 |
| Common columns | 362 | 362 |

### Column Distribution

| Category | Count |
|----------|-------|
| Ref-only columns | 673 (UCBERKELEY_AMY/* 338, UCBERKELEY_TAU/* 333, FS_path, IMAGEUID_bl) |
| New-only columns | 418 (ADNI4 modalities, plasma biomarkers, new protocol metadata) |
| Common columns | 362 |

---

## Common Column Comparison (362 cols, 11,692 common rows)

### Summary

| Match Rate | Columns | % |
|------------|---------|---|
| 100% | 49 | 13.5% |
| 99-100% | 29 | 8.0% |
| 95-99% | 10 | 2.8% |
| 50-95% | 33 | 9.1% |
| 1-50% | 10 | 2.8% |
| 0% | 31 | 8.6% |
| No overlap (column exists but 0 shared non-null rows) | 200 | 55.2% |

---

## Category (A): 100% or Near-100% Match (78 cols)

**핵심 임상 변수 — 동일 소스, 동일 로직**

| Column | Both Non-Null | Match Rate | Note |
|--------|--------------|------------|------|
| RID, SITE, ORIGPROT, PTEDUCAT, PTETHCAT | 11,502 | **100%** | 인구통계 |
| PTMARRY, RAVLT_immediate/learning/learning_bl | 11,476-11,502 | **100%** | |
| CDRSB, DIGITSCOR, TRABSCOR_bl, FLDSTRENG_bl | 3,613-11,502 | **100%** | |
| EXAMDATE_bl | 11,502 | **~100%** | 1건 차이 |
| CDRSB_bl, Years_bl, DAYSDELTA | 11,502 | **99.9%** | |
| DX (방문별 진단) | 10,536 | **99.9%** | sc→bl 병합 순서 차이 |
| RAVLT_forgetting, Apoe, APOE4 | 10,389-11,181 | **99.9%** | 데이터 업데이트 |
| COLPROT, PTGENDER, subjectSex | 11,502-11,669 | **~100%** | |
| protocol/T1/TE, TR, TI, FlipAngle | 9,344-10,846 | **100%** | DCM 직접 추출 |
| protocol/FLAIR, T2_FSE, T2_STAR, T2_TSE (TE/TR/TI/FlipAngle) | 56-6,400 | **100%** | DCM 직접 추출 |

**결론**: 인구통계, 진단, 인지검사 핵심 변수는 모두 **99.9%+ 일치**.

---

## Category (B): Data Source Change (0-24%)

**ADNIMERGE2 설계에 따른 소스 테이블 변경 — `adnimerge_py/README.md` 섹션 (C) 참조**

### MRI Volumes (0%)

| Column | Both Non-Null | Match Rate | Ref Source | New Source |
|--------|--------------|------------|-----------|-----------|
| Entorhinal | 3,490 | **0%** | UCSFFSX (FS 4.x) | UCSFFSX51 (FS 5.1) |
| Entorhinal_bl | 4,521 | **0%** | " | " |
| Fusiform / _bl | 3,490 / 4,521 | **0%** | " | " |
| MidTemp / _bl | 3,490 / 4,521 | **0%** | " | " |
| WholeBrain / _bl | 3,984 / 4,952 | **0%** | " | " |
| Ventricles / _bl | 3,038 / 4,274 | **0%** | UCSFFSX | UCSDVOL |
| Hippocampus_bl | 4,611 | **83.1%** | " | UCSFFSX51 |
| ICV_bl | 5,050 | **84.0%** | " | UCSFFSX51 |
| Hippocampus | 3,907 | **93.5%** | " | UCSFFSX51 |
| ICV | 4,248 | **93.6%** | " | UCSFFSX51 |

**원인**: FreeSurfer 버전(4.x→5.1) atlas 차이 + ROI 정의 변경.
WholeBrain/Entorhinal 등은 r=0.5-0.7 상관 있으나 절대값 상이.
Hippocampus/ICV는 r≈0.998로 거의 동일 측정 (UCSFFSX51 primary로 전환하여 93%+ 달성).

### CSF Biomarkers (5-10%)

| Column | Both Non-Null | Match Rate | Ref Source | New Source |
|--------|--------------|------------|-----------|-----------|
| ABETA | 2,329 | **5.7%** | UPENNBIOMK (Luminex) | MASTER + ROCHE_ELECSYS |
| TAU | 2,329 | **10.4%** | " | " |
| PTAU | 2,328 | **9.6%** | " | " |
| ABETA_bl | 7,043 | **0%** | " | " |
| TAU_bl | 7,043 | **1.1%** | " | " |
| PTAU_bl | 7,043 | **0%** | " | " |

**원인**: Ref는 Luminex 단독. New는 `UPENNBIOMK_MASTER` (Luminex+Elecsys 혼합) + `ROCHE_ELECSYS` 병합.
ADNI3+ Elecsys 전환으로 Luminex 단독 사용 시 최신 데이터 누락.
ABETA ratio≈0.22는 Elecsys의 알려진 변환계수.
([Shaw et al. 2019](https://www.nature.com/articles/s41598-019-54204-z))

### PET Composites (0-0.1%)

| Column | Both Non-Null | Match Rate | Ref Source | New Source |
|--------|--------------|------------|-----------|-----------|
| FDG | 3,677 | **0%** | UCBERKELEYFDG (구) | UCBERKELEYFDG_8mm MetaROI |
| FDG_bl | 7,975 | **0%** | " | " |
| AV45 | 3,201 | **0.1%** | AV45 SUVR (8mm) | AMY_6MM SUMMARY_SUVR |
| AV45_bl | 5,678 | **0%** | " | " |

**원인**: FDG 파이프라인 세대교체 (r=0.847), AV45 해상도 8mm→6mm + reference region 업데이트 (r=0.998).

---

## Category (C): Data Update (.rda 2024→2026)

### Ecog Series (28 cols, 43-98%)

| Column Group | Range | Match Rate | Note |
|-------------|-------|------------|------|
| EcogSPTotal / _bl | 6,675-6,766 | **43-46%** | .rda 업데이트 + VISSPAT 버그 수정 |
| EcogPtTotal / _bl | 6,700-6,800 | **47-52%** | " |
| EcogSPOrgan / _bl | 6,381-6,500 | **82-83%** | " |
| EcogPtOrgan / _bl | 6,568-6,656 | **89-90%** | " |
| EcogSP/PtMem / _bl | 6,673-6,804 | **94-96%** | " |
| EcogPtDivatt / _bl | 6,664-6,754 | **97-99%** | " |

**원인**: 빌드 과정에서 발견한 VISSPAT 항목 누락 + mean-of-means 계산 오류 수정 (`docs/ADNIMERGE_reproducibility_audit.md` 참조).
또한 .rda 소스 2024→2026 버전 업데이트.

### Cognitive Tests

| Column | Both Non-Null | Match Rate | Note |
|--------|--------------|------------|------|
| ADAS11 / ADAS13 | 10,434-10,521 | **~70%** | 소수점 정밀도 차이 (r=0.999), round() 적용 시 99.7% |
| AGE | 11,492 | **59.5%** | 소수점 반올림 차이 (평균 0.04세, r≈1.000) |
| ADAS11_bl / ADAS13_bl | 11,416-11,471 | **~70%** | " |
| MMSE | 10,554 | **98.4%** | .rda 업데이트 |
| MMSE_bl | 11,501 | **99.4%** | " |
| MOCA | 2,458 | **89.7%** | .rda 업데이트 |
| MOCA_bl | 1,565 | **90.2%** | " |

### mPACC (0%)

| Column | Both Non-Null | Match Rate | Note |
|--------|--------------|------------|------|
| mPACCdigit_bl | 4,770 | **0%** | ADNIMERGE2 새 계산 로직 |
| mPACCtrailsB_bl | 11,500 | **0%** | " |

**원인**: mPACC 합성 점수의 계산 수식이 ADNIMERGE2 패키지에서 변경됨.

---

## Category (D): System/Definition Differences

| Column | Both Non-Null | Match Rate | Note |
|--------|--------------|------------|------|
| Month_bl | 11,502 | **22.3%** | Ref: screening 기준 (소수), New: enrollment=0 |
| Month / M | 11,443 | **72%** | Month_bl 연쇄 차이 |
| researchGroup | 10,724 | **52.1%** | Ref: enrollment group (고정), New: DX (방문별) |
| MODALITY | 11,692 | **95.4%** | 다중 모달리티 행의 MODALITY 선택 차이 |
| RAVLT_perc_forgetting_bl | 11,461 | **50.2%** | 계산 수식 차이 |
| DX_bl | 11,490 | **89.9%** | ARM.rda 연동 (91.3%, ADNI3 ARM 부재 8.7%) |

---

## Category (E): Format/Path Differences (0%)

| Column | Both Non-Null | Match Rate | Note |
|--------|--------------|------------|------|
| T1_image_path | 11,021 | **0%** | NFS 경로 포맷 차이 |
| AV45_8MM/6MM_image_path | 2,860-3,154 | **0%** | " |
| AV1451_8MM/6MM_image_path | 1,532-1,570 | **0%** | " |
| FBB_6MM_image_path | 586 | **0%** | " |
| FLAIR_image_path | 3,359 | **0%** | " |
| T2_FSE/TSE/STAR_image_path | 1,705-6,576 | **0%** | " |
| FSVERSION / _bl | 3,957-4,764 | **0%** | FreeSurfer 버전 문자열 |
| LONIUID | 923 | **0%** | LONI 식별자 형식 |
| update_stamp | 11,443 | **0%** | 빌드 타임스탬프 |

---

## No-Overlap Columns (200 cols)

양쪽 모두 컬럼이 존재하지만, 공통 행에서 한쪽만 non-null인 경우.

| Category | Count | Note |
|----------|-------|------|
| protocol/*/Manufacturer, Matrix, Pixel Spacing 등 | 150+ | XML 메타데이터 (v4는 DCM에서 TE/TR/TI/FlipAngle만 추출) |
| S_* (SeriesUID) | 6 | Ref는 S_{MOD}, New는 다른 이름 |
| visitIdentifier_* | 10 | XML에만 존재 |
| subjectAge | 1 | birth_dates.csv 미제공 |
| weightKg | 1 | DCM에서 추출 불가 |
| ADASQ4 / _bl | 2 | Ref ADNIMERGE에만 존재 |
| mPACCdigit/mPACCtrailsB (visit) | 2 | New에서 visit-level 미생성 |
| FBB/PIB + _bl | 4 | New ADNIMERGE에 placeholder NA |
| IMAGEUID | 1 | Ref에만 존재 |

---

## UCBERKELEY Column Issue

### Ref-only: 671 UCBERKELEY columns

Ref에만 존재하는 671개 컬럼 중 338개는 `UCBERKELEY_AMY/*`, 333개는 `UCBERKELEY_TAU/*`.
이는 PET 이미지의 뇌 영역별 SUVR/Volume 정량화 데이터 (UC Berkeley Lab).

### New의 상태: 프리픽스 누락 (Bug)

New MERGED.csv에도 UCBerkeley 데이터가 존재하지만 **프리픽스 없이** 저장됨:
- Ref: `UCBERKELEY_AMY/ACCUMBENS_AREA_SUVR`, `UCBERKELEY_TAU/ACCUMBENS_AREA_SUVR`
- New: `ACCUMBENS_AREA_SUVR` (AMY인지 TAU인지 구분 불가)

**329개 AMY/TAU 컬럼명 충돌** → merge.py에서 먼저 병합된 CSV(AMY) 우선, TAU 값 소실.

**수정**: `config.py`에 `column_prefix` 추가 → 재실행 필요.

---

## References

- [adnimerge_py/README.md](../adnimerge_py/README.md) — ADNIMERGE 빌드 검증 상세
- [docs/ADNIMERGE_reproducibility_audit.md](./ADNIMERGE_reproducibility_audit.md) — Ecog, RAVLT 버그 수정 이력
- [Shaw et al. 2019](https://www.nature.com/articles/s41598-019-54204-z) — CSF Luminex→Elecsys 변환
