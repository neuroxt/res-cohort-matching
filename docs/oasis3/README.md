# OASIS3 (Open Access Series of Imaging Studies, Release 3) — 데이터 문서 인덱스

WUSTL Knight ADRC 의 ~30년 retrospective 통합 longitudinal multi-modal 코호트. 1,378 subjects (cognitively normal 755 + cognitive decline 622), 42–95세, MRI + PET + clinical/cognitive 통합 배포. 임상 데이터는 NACC UDS v2/v3 mix 표준이며, 폼 컬럼 정의는 NACC와 공유 (`docs/_shared/nacc_uds_forms.md`). 본 폴더는 OASIS3 cohort-specific quirk (file 이름, OASISID 그래머, days_to_visit anchor, USDa3 typo, c1=`psychometrics` token 등) 에 집중한다.

> **NFS 기준 경로** (macOS 마운트 기준):
> - 임상 / 메타: `/Volumes/nfs_storage/OASIS3/ORIG/DEMO/`
> - PET 정량화: `/Volumes/nfs_storage/OASIS3/ORIG/DEMO/` 안의 PET 관련 CSV
> - 원본 NIfTI: `/Volumes/nfs_storage/OASIS3/ORIG/NII/` (또는 BIDS 변환 경로)
>
> Windows / Linux 는 마운트 root만 본인 환경에 맞게 치환.

---

## 한 눈에 보기

| 항목 | 값 |
|------|---|
| Subject 키 | `OASISID` (`OAS3xxxx`, 1-padded 4 digits, 1378까지) |
| Visit 키 | `(OASISID, days_to_visit)` — **고정 visit code 없음**, 첫 방문 = `d0000` |
| Session label | `OAS3xxxx_<FORM_TOKEN>_d####` (텍스트 단일 키) |
| 진단 그룹 | NACC UDS 표준 (NORMCOG / DEMENTED / IMPNOMCI + MCI 변종 + etiology) |
| Subject 수 | **1,378** (CN 755 + cognitive decline 622) |
| Visit 행수 (UDS b4) | 8,627 (CDR 폼 기준) |
| Visit 행수 (UDS 일반) | 8,500 (대부분 폼) |
| Optional 폼 행수 | 4,090 (a3 가족력, b3 UPDRS) |
| 등록·추적 기간 | ~30년 retrospective (multiple Knight ADRC 연구 통합) |
| 연령 범위 | 42 – 95세 |
| 모달리티 | T1 / T2 / FLAIR / SWI / dMRI / rsfMRI / Amyloid PET (PIB, AV45) / Tau PET (AV1451) / FDG PET |
| UDS 버전 | v2 ↔ v3 mix (FORMVER 컬럼 없음 — 검사 셋 / 시점 추정) |
| Single ADRC | WUSTL Knight ADRC 단일 사이트 |
| 데이터 접근 | DUA 동의 후 [oasis-brains.org](https://sites.wustl.edu/oasisbrains/home/oasis-3/) 다운로드 |
| 공개 publication | LaMontagne et al., medRxiv 2019/2024 (DOI: [10.1101/2019.12.13.19014902](https://doi.org/10.1101/2019.12.13.19014902)) |

---

## 문서 목록

### 시작점

| 문서 | 언제 읽나요? |
|------|-------------|
| [`data_catalog.md`](data_catalog.md) | 24 CSV 마스터 인벤토리 — OASIS3 처음 접할 때 |
| [`protocol.md`](protocol.md) | Knight ADRC 배경, OASIS 시리즈 비교, NACC UDS v2/v3, 모달리티 / PET 트레이서 — 연구 맥락 이해할 때 |
| [`join_relationships.md`](join_relationships.md) | 3-tier 키 계층, 조인 패턴 4종, 카디널리티 — 파이프라인 설계 시 |

### 임상 (UDS) 데이터

| 문서 | 내용 |
|------|------|
| [`uds_forms.md`](uds_forms.md) | OASIS3 overlay — 17 UDS 폼 파일 위치 / 행·열 수 / OASIS3 session token 표 (USDa3 typo, c1=`psychometrics`) |
| [`session_label_reference.md`](session_label_reference.md) | OASIS3 session label 그래머 (`OAS3xxxx_<token>_d####`), `days_to_visit` 의미 / 음수 5건 quirk, 영상-임상 매칭 |
| [`demographics.md`](demographics.md) | `OASIS3_demographics.csv` 19컬럼 1:1 사전 (subject-level baseline) |

### 영상 데이터

| 문서 | 내용 |
|------|------|
| [`pet_imaging.md`](pet_imaging.md) | PET 3 파일 비교, 트레이서 (PIB / AV45 / AV1451 / FDG), Centiloid + PUP 방법론 |
| [`file_index.md`](file_index.md) | NIfTI 파일 인벤토리, BIDS 명명, `*_diff` 부호, oasis_file_list VISIT 분포 |

### `docs/_shared/` (NACC ↔ OASIS3 공통)

| 문서 | 내용 |
|------|------|
| [`docs/_shared/nacc_uds_forms.md`](../_shared/nacc_uds_forms.md) | NACC UDS 17 폼 (A1–D2) 컬럼 정의 / 코딩 / 분석 패턴 — **모든 폼 컬럼 사전은 여기** |
| [`docs/_shared/nacc_session_labels.md`](../_shared/nacc_session_labels.md) | NACC PACKET 그래머 / missing-code 처리 / 영상-임상 시간 매칭 |

---

## 다른 코호트와의 차이

| 항목 | OASIS3 | NACC | ADNI | A4 / LEARN | KBASE |
|------|--------|------|------|-----------|-------|
| 임상 framework | NACC UDS v2/v3 (subset) | NACC UDS v1–v4 | ADNI 자체 (subset of UDS) | A4 자체 (PACC center-stage) | 한국어 자체 CRF |
| Subject ID | `OASISID` (`OAS3xxxx`) | `NACCID` (`NACC` + 6 digits) | `RID` / `PTID` | `BID` | `SU####` / `BR####` |
| Visit 키 | **`(OASISID, days_to_visit)`** | `(NACCID, NACCVNUM, PACKET)` | `VISCODE` (BL/M06/M12/...) | `VISCODE` ↔ `SESSION_CODE` | `K_visit` ∈ {0..4} |
| Session label | **단일 텍스트 키 (`OAS3xxxx_<token>_d####`)** | 합성 필요 (`(NACCID, NACCVNUM, PACKET)` tuple) | 합성 필요 | 합성 필요 | 합성 필요 |
| Sites | 1 (WUSTL Knight ADRC) | 29+ ADRCs | 60+ multi-national | 67 (US/CA/AU/Japan) | 1 (SNUBH/SNU) |
| 데이터 organization | 폼별 별도 CSV (24 파일) | 단일 통합 wide-format (1,936 cols) | 폼별 + 통합 ADNIMERGE | BASELINE + MERGED 통합 | 단일 masterfile |
| 동의 tier | 단일 (open access + DUA) | Commercial vs Investigator | 단일 (LONI DUA) | 단일 (NIA-A4) | 단일 (자체 운영) |
| Freeze 주기 | 비정기 (release 단위) | 분기 (~3개월) | 비정기 (이벤트 기반) | 비정기 (release 단위) | 운영팀 manual |

---

## 알려진 limitations & quirks

문서 작성 시점에 NFS 데이터를 직접 inspect하여 확인된 항목:

1. **고정 visit code 없음.** ADNI 의 `BL`/`M06`/`M12` 같은 fixed visit token이 없다. 모든 시점은 `(OASISID, days_to_visit)` 페어로 표현. 첫 방문 = `d0000`, 후속 visit = `d{N}` (N = 일수). cross-subject 동기화 불가 (subject 마다 d0000 시점이 다름, 절대 날짜 정보 부재).
2. **`d0000` 음수 5건 (UDSb4 폼).** OAS30290 (-2), OAS30330 (-101), OAS30380 (-15), OAS30753 (**-39520, age=-47.25**) ← 명백한 데이터 오류, OAS30851 (-1). 분석 전 `days_to_visit < 0` 필터링 또는 별도 처리.
3. **Session token typo: `USDa3`, `USDb3`.** 파일명은 `UDSa3.csv`, `UDSb3.csv` 인데 session label 토큰은 USD (UDS 글자 순서 뒤바뀜). 정규식 매칭 시 `(UDS[a-d]\d|USDa3|USDb3|psychometrics|...)` 사용.
4. **C1 폼 토큰 = `psychometrics`** (NOT `UDSc1`). OASIS3 만의 처리. 다른 모든 폼은 `UDS<form>` 토큰 사용.
5. **A4 폼 D/G 분리, 같은 토큰.** `OASIS3_UDSa4D_med_codes.csv` (코드) + `OASIS3_UDSa4G_med_names.csv` (이름) 둘 다 session token = `UDSa4`. 파일별로 따로 읽고 (OASISID, days_to_visit) join.
6. **`days_to_visit` 컬럼 dtype 불일치.** 대부분 폼: zero-padded 4-digit string (`'0000'`), b4/c1: integer string (`'0'`). 분석 시 `pd.to_numeric()` 명시적 변환 권장.
7. **PET session token = 트레이서명** (`AV45`, `PIB`, `AV1451`, `FDG`) — 폼 자리에 트레이서가 들어감. UDS label 과 직접 join 불가. ±90일 윈도우 매칭.
8. **42,907 NIfTI 파일 중 5,223 `unmatched`** — 임상 visit과 매칭 실패한 imaging-only scan. 분석 시 처리 결정 필요.
9. **UDS 버전 mix (v2 ↔ v3).** OASIS3는 NACC `FORMVER` 컬럼 없음. 폼 c1 의 MoCA 컬럼 (`mocatots`) 존재 여부로 v3 visit 추정. 같은 변수 명도 v2↔v3 사이에서 정의가 다를 수 있음.
10. **Single ADRC = site effect 통제 불필요.** NACC와 달리 모두 WUSTL 데이터.

---

## 작성 컨벤션

- 한국어 본문 + 영어 기술 용어 (변수명, CRF명, 코드값은 영어 그대로) — 다른 코호트 (`docs/nacc/`, `docs/a4/`, `docs/kbase/`) 컨벤션과 동일.
- 모든 사실은 NFS 원본 inspection 결과 기반. 새 사실 추가 시 inspection 명령과 결과 함께 commit.
- 컬럼명은 백틱 (`OASISID`) 으로 감싸 고정 폭. 한국어 라벨이 있을 땐 슬래시 병기 (`OASISID` / `피험자 ID`).
- **NACC UDS 표준 정의 (폼 컬럼, missing-code 등) 는 본 폴더에 두지 않는다.** `docs/_shared/nacc_uds_forms.md` 에서 공유. 본 폴더에는 OASIS3-specific overlay 만.
- "Known limitations" 섹션은 모든 문서에 포함. quirk 발견 시 즉시 추가.
