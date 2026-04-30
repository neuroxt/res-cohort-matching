# NACC (National Alzheimer's Coordinating Center) — 데이터 문서 인덱스

NACC는 NIA가 자금을 대고 University of Washington이 운영하는 **AD Research Center 네트워크 (29+ ADRCs) 표준화 데이터 통합** 프로젝트로, 2005년부터 매년 1회 (±6개월) UDS (Uniform Data Set) 양식으로 임상·인지·기능·신경학적 평가를 수집한다. 분기별로 freeze가 만들어지고 (~3개월 주기), 영상 (NIfTI/DICOM)·신경병리·바이오마커 (CSF, ADSP-PHC 유전체)·SCAN PET/MRI 정량화 데이터가 함께 배포된다.

본 repo는 v71 freeze (2025-10/2026-04) 시점의 NACC NFS export를 기준으로 한다. 임상 데이터는 OASIS3와 동일한 **NACC UDS 표준**을 따르므로, **UDS 폼별 컬럼 정의는 [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md)** 한 곳에 두고 NACC와 OASIS3가 함께 참조한다. NACC 폴더는 NACC 자체의 ADRC 설계, 동의 tier 분리 (Commercial vs Investigator), 옵셔널 모듈 (FTLD3 / LBD3.1 / ADSP-PHC), SCAN PET/MRI 정량화 산출물에 집중한다.

> **NFS 기준 경로** (macOS 마운트 기준):
> - 임상/메타/PET 통합: `/Volumes/nfs_storage/NACC_NEW/ORIG/DEMO/`
> - 원본 NIfTI: `/Volumes/nfs_storage/NACC_NEW/ORIG/NII_NEW/`
> - 원본 DICOM: `/Volumes/nfs_storage/NACC_NEW/ORIG/DCM/`
> - 압축 export 백업: `/Volumes/nfs_storage/NACC_NEW/ORIG/ZIP/`
>
> Windows/Linux는 마운트 root만 본인 환경에 맞게 치환 (예: `Z:\NACC_NEW\...`, `/mnt/nfs/NACC_NEW/...`).

---

## 한 눈에 보기

| 항목 | 값 |
|------|---|
| Subject 키 | `NACCID` (`NACC` + 6 digits, 예: `NACC252073`) |
| Visit 키 | `NACCVNUM` (visit number, 1-based) + `PACKET` (I=Initial / F=Follow-up / T=Telephone) |
| Form 버전 | `FORMVER` (UDS v1=1, v2=2, v3=3, v4=4) — v71 freeze는 v3가 다수, v4 점진 도입 |
| 진단 그룹 | UDS 표준 (NORMCOG / IMPNOMCI / DEMENTED + MCI 변종 + etiology 23+) — [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) D1 폼 참조 |
| 등록·추적 기간 | 2005-09 ~ 진행중 (분기 freeze 갱신) |
| Subject 수 | 55,004 unique NACCID (clinical), 6,481 imaged |
| Visit 행수 (clinical) | 205,909 행 (`investigator_ftldlbd_nacc71.csv`) |
| Working file | `merged.csv` 205,909 × 390 (NeuroXT-built UDS subset + CSF + Amyloid/Tau PET SUVR pre-merged) |
| Modalities | T1, T2w, FLAIR, T2_STAR(GRE), ASL, dMRI, rsfMRI, AV45, AV1451, FBB, PIB, MK6240, FDG, HighResHippo (11+) |
| 동의 tier | **Commercial** (산업/상업 사용 가능, 좁은 동의 → 행 수 적음) vs **Non_Commercial = Investigator** (학술 전용, **넓은 동의 → 기본 사용 권장**) |
| 옵셔널 모듈 | FTLD3 (FVP/IVP), LBD3.1 (FVP/IVP), CSF biomarker (EE2), ADSP-PHC 122024 (PET/T1/FLAIR/DTI/Vascular/Cognition/Neuropath/Biomarker) |
| 데이터 freeze 주기 | 분기 (≈3개월), v71 freeze 기준 본 docs 작성 |
| 데이터 접근 | DUA 서명 후 48시간 이내 ([naccdata.org](https://naccdata.org/requesting-data/nacc-data/)) |

---

## 문서 목록

### 시작점

| 문서 | 언제 읽나요? |
|------|-------------|
| [`data_catalog.md`](data_catalog.md) | NFS 파일 인벤토리 — DEMO/NII_NEW/DCM/ZIP, Commercial/Non_Commercial tier 파일 페어, 10개 RDD PDF — NACC 처음 접할 때 |
| [`protocol.md`](protocol.md) | NACC 배경 (29+ ADRCs, NIA, 2005~), UDS v1→v4 evolution, 분기 freeze 체계, 데이터 접근 |
| [`data_tier_reference.md`](data_tier_reference.md) | Commercial vs Non_Commercial(Investigator) 컨센트 분리의 의미와 사용 가이드 — 어느 파일 쓸지 결정할 때 |
| [`join_relationships.md`](join_relationships.md) | `(NACCID, NACCVNUM, PACKET)` 조인 키, `merged.csv` ↔ FTLD/LBD/SCAN 카디널리티, 5.9% 영상-임상 미스매치 처리 |

### 데이터 종류별

| 문서 | 내용 |
|------|------|
| [`merged_csv.md`](merged_csv.md) | `merged.csv` 390-col 사전 (UDS bookkeeping 8 + UDS clinical 30 + CSF 5 + Amyloid PET 175 + Tau PET 169) — NeuroXT 통합 분석 시작점 |
| [`uds_forms.md`](uds_forms.md) | NACC bookkeeping 컬럼 (NACCID/NACCADC/PACKET/FORMVER/NACCVNUM/VISITDATE), missing-code 컨벤션, UDS v3↔v4 deltas — 폼-level 사전은 [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) |
| [`session_label_reference.md`](session_label_reference.md) | NACC visit/packet 시맨틱 (PACKET=I/F/T, NACCVNUM 의미, longitudinal 조인 키) — UDS packet 그래머는 [`docs/_shared/nacc_session_labels.md`](../_shared/nacc_session_labels.md) |
| [`optional_modules.md`](optional_modules.md) | FTLD3 (FVP/IVP), LBD3.1 (FVP/IVP), CSF biomarker (EE2), ADSP-PHC 122024 (8 도메인), SCAN MRI (mriqc/mrisbm), SCAN PET (amyloid GAAIN/NPDKA, tau, FDG) — 모듈별 컬럼 그룹 + RDD PDF 포인터 |
| [`imaging_inventory.md`](imaging_inventory.md) | `NII_NEW/` 트리 (`NACC{ID}/{v1,v2,...}/{MOD}/{protocol}/{date}/{imageID}/*.nii.gz`), 11+ 모달리티 분포, 6,481 imaged subjects, 임상-영상 5.9% 미스매치 |

### `docs/_shared/` (NACC↔OASIS3 공통)

| 문서 | 내용 |
|------|------|
| [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) | 17 UDS 폼 (A1–D2) 컬럼 정의, NACC missing-code 표 (88/888/999/9999), 분석 권장 사항 |
| [`docs/_shared/nacc_session_labels.md`](../_shared/nacc_session_labels.md) | UDS packet 그래머, FORM 토큰 표, NACC missing-code 처리 패턴 |

---

## 다른 코호트와의 차이

| 항목 | NACC | OASIS3 | ADNI | A4 / LEARN | KBASE |
|------|------|--------|------|-----------|-------|
| 임상 framework | NACC UDS v1–v4 | NACC UDS v2–v3 (subset) | ADNI 자체 (subset of NACC) | A4 자체 (PACC center-stage) | 한국어 자체 CRF |
| Subject ID | `NACCID` (NACC + 6 digits) | `OASISID` (`OAS3xxxx`) | `RID` / `PTID` | `BID` | `SU####` / `BR####` |
| Visit 키 | `(NACCVNUM, PACKET)` | `(OASISID, days_to_visit)` | `VISCODE` (BL/M06/M12/...) | `VISCODE` ↔ `SESSION_CODE` | `K_visit` ∈ {0..4} |
| 통합 working file | `merged.csv` (390 col, NeuroXT-built) | per-form CSVs | `ADNIMERGE.csv` (132 col) | `BASELINE.csv` (369 col) | `masterfile.csv` (150 col) |
| 동의 tier 분리 | **있음** (Commercial vs Investigator) | 없음 (open access 후 DUA) | 없음 (개별 DUA) | 없음 (NIA-A4 단일 access) | 없음 (자체 운영) |
| Site / center 수 | 29+ ADRCs | 1 (WUSTL Knight ADRC) | 60+ (다국가) | 70+ (US/CA) | 1 (SNUBH/SNU) |
| Freeze 주기 | 분기 (~3개월) | 비정기 (release 단위) | 비정기 (이벤트 기반) | 비정기 (release 단위) | 운영팀 manual |
| 영상 정량화 | NACC SCAN (MRI SBM, Amyloid/Tau/FDG NPDKA + GAAIN) | OASIS3 PUP | UCBERKELEY (per-tracer) | A4 표준 SUVR pipeline | KBASE 자체 + 외부 |
| 옵셔널 모듈 | FTLD3 / LBD3.1 / ADSP-PHC genetics | (없음, UDS 핵심만) | (없음, ADNI-specific 모듈) | (없음, A4 baseline 단일) | (없음) |

---

## 알려진 limitations & quirks (요약)

문서 작성 시점 (v71 freeze, 2026-05-01)에 NFS 데이터를 직접 inspect하여 확인된 항목:

1. **`merged.csv`는 NACC 표준 배포가 아님 — NeuroXT-built 파일.** 205,909행 × 390열로, `investigator_ftldlbd_nacc71.csv` (205,909 × 1,936)에서 UDS 핵심 컬럼 ~38개를 추출한 뒤 `investigator_fcsf_nacc71.csv` (CSF 5컬럼) + `investigator_scan_pet/amyloidpetnpdka` (175 SUVR) + `investigator_scan_pet/taupetnpdka` (169 SUVR) 를 `(NACCID, NACCVNUM)` 단위로 inner-join한 것으로 확인. 어느 컬럼이 어디서 왔는지는 [`merged_csv.md`](merged_csv.md) 참조.
2. **Commercial vs Investigator는 동의 tier — 같은 데이터의 다른 subset.** 컬럼 스키마 동일 (1,936 cols), 행 수가 다름 (commercial 179,753 < investigator 205,909). 학술 연구는 **Investigator (Non_Commercial)** 를 default로 사용 권장. 상세는 [`data_tier_reference.md`](data_tier_reference.md).
3. **UDS 버전 mix.** v71 freeze에는 UDS v1/v2/v3가 혼재하며 (v4 일부 도입). 분석 시 `FORMVER` 필드로 visit별 폼 버전을 확인. 같은 변수명도 v2↔v3 사이에서 정의가 변할 수 있다 (예: c1 cognitive battery는 v2 → v3 전환에서 검사 자체 교체). 자세한 기준은 [`uds_forms.md`](uds_forms.md).
4. **영상-임상 미스매치 5.9% (Issue #7).** 영상이 있는 6,481명 중 381명 (5.9%) 이 `merged.csv` 에 임상 데이터가 *전혀* 없음. 기존 inventory 시점(2026-03-13) 기준이며, v71 freeze에서 일부 해소되었을 수 있음 — 분석 사용 전 재집계 권장. 패턴 / 처리 방법은 [`join_relationships.md`](join_relationships.md).
5. **`merged_CDR.csv`는 v71 freeze에서 사라짐.** 2026-03-13 시점에 존재하던 보조 파일이 v71 freeze (2025-10 / 2026-04) 에서는 보이지 않음. CDR 컬럼은 `merged.csv` (`MEMORY`, `ORIENT`, `JUDGMENT`, `COMMUN`, `HOMEHOBB`, `PERSCARE`, `CDRSUM`, `CDRGLOB`, `COMPORT`, `CDRLANG`) 에 모두 들어있음.
6. **PACKET 인코딩**: `I` = Initial Visit Packet, `F` = Follow-up Visit Packet, `T` = Telephone Follow-up. 분기 freeze 도중 같은 `(NACCID, NACCVNUM)` 행이 `I` → `F` → `F` 순으로 누적된다.
7. **`AMY/CTX_*_SUVR` 컬럼은 FreeSurfer DKT atlas 기반.** Amyloid PET 175 컬럼 = bilateral 합 (35) + LH (35) + RH (35) + bilateral subcortical (35 → 일부) + cerebellar reference (5) + GAAIN summary (5) + NPDKA composite (5) + global metrics. 같은 layout이 Tau PET 169 컬럼에도 적용 (단 entorhinal-meta-temporal 추가). 정량화 방법은 [`optional_modules.md`](optional_modules.md) GAAIN/NPDKA 절.
8. **ADSP-PHC는 별도 release line.** ADSP-PHC December 2024 freeze는 NACC core freeze와 별도 cadence로 배포되며, 12월 release를 v71 (10월 freeze) 와 함께 사용. PHC = Phenotype Harmonization Consortium — Amyloid/Tau/T1/FLAIR/DTI/Vascular/Biomarker/Neuropath/Cognition 9 도메인에 걸쳐 ADNI/AIBL/HABS-HD/DOD-ADNI 등 연구와 동일한 phenotype 정의를 사용한다.
9. **NACC missing-code 표준**: `0`=No / `1`=Yes / `8`=N/A / `9`=Unknown / `88`/`888`/`999`/`9999` (자릿수 매칭) = missing. 분석 시 일괄 NaN 변환 권장. 코드 표 전체는 [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) 도입부.
10. **DCM/ vs NII_NEW/ 동시 존재.** DCM은 원본 DICOM, NII_NEW는 BIDS-style NIfTI 변환. 분석 파이프라인은 NII_NEW 사용. DCM은 archive/검증 용도.

---

## 작성 컨벤션

- 한국어 본문 + 영어 기술 용어 (변수명, 폼명, 코드값은 영어 그대로) — 다른 코호트(`docs/oasis3/`, `docs/a4/`, `docs/kbase/`) 컨벤션과 동일.
- 모든 사실은 NFS 원본 inspection 결과 기반. 새 사실 추가 시 inspection 명령과 결과 함께 commit.
- 컬럼명은 백틱(`NACCID`)으로 감싸 고정 폭. 한국어 라벨이 있을 땐 슬래시로 병기 (`NACCID` / `피험자 ID`).
- "Known limitations" 섹션은 모든 문서에 포함. quirk를 발견하면 즉시 추가.
- v71 freeze 기준 사실은 `> 검증일 2026-05-XX (freeze v71)` 푸터로 표시. 다음 freeze 이후 갱신 트래커 역할.
