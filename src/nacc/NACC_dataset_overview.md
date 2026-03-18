# NACC (National Alzheimer's Coordinating Center) Dataset Overview

> 조사일: 2026-03-13

## 1. 데이터셋 특성

NACC는 **ongoing (지속적으로 업데이트되는) longitudinal 데이터셋**이다.

| 항목 | 내용 |
|------|------|
| 운영 기관 | National Alzheimer's Coordinating Center (University of Washington) |
| 펀딩 | NIA (National Institute on Aging) |
| 데이터 수집 시작 | 2005년 (UDS v1) |
| 수집 센터 | NIA-funded 29+ ADRCs (Alzheimer's Disease Research Centers) |
| 수집 주기 | 참가자별 **연 1회** 방문 (±6개월 윈도우) |
| 데이터 프리즈 | **약 3개월마다** (분기별) |
| 최근 프리즈 | 2025년 12월 |
| 다음 프리즈 | 2026년 3월 (예정) |
| 현재 UDS 버전 | **UDS v4** (최신) |
| 향후 계획 | 2026년부터 5년 연장 경쟁 신청 제출 완료 |

## 2. 데이터 구조

### UDS (Uniform Data Set)
- 표준화된 연례 임상 평가 데이터
- UDS v1 (2005) → v2 → v3 → **v4** (현재)
- 18개 데이터 수집 양식 (clinician 작성)
- 인지, 행동, 기능, 신경학적 평가 포함

### 주요 데이터 영역
- **Clinical/Cognitive**: 인지기능 평가, 행동 증상, 기능적 상태
- **Neuropathologic**: 부검 데이터
- **Biomarker**: CSF, 혈액 바이오마커
- **Imaging**: MRI, PET (별도 모듈)
- **Genetics**: APOE, GWAS 등

## 3. ADNI와의 비교

| 비교 항목 | ADNI | NACC |
|-----------|------|------|
| 중심 데이터 | **이미징** (MRI, PET) | **임상/인지/신경병리** |
| 수집 방식 | 프로토콜 기반 다기관 연구 | ADRCs 표준화 연례 평가 |
| 펀딩 | NIA + 산업 파트너 | NIA |
| 데이터 프리즈 | 비정기 | **분기별** (~3개월) |
| 참가자 추적 | 프로토콜 종료 시 | 참가자 의사에 따라 지속 |
| 데이터 접근 | LONI 포털 | DUA 서명 후 48시간 이내 |
| 코호트 설계 | CN/MCI/AD 고정 코호트 | 임상 센터 내원 환자 기반 |

## 4. 데이터 접근 방법

1. [naccdata.org](https://naccdata.org/requesting-data/nacc-data/)에서 Quick-Access 요청
2. DUA (Data Use Agreement) 서명 (~15분)
3. 온라인 요청 제출
4. **승인 후 48시간 이내** 데이터 수령
5. 업데이트 필요 시 언제든 온라인 재요청 가능

## 5. NFS 데이터 현황

> 경로: `/Volumes/nfs_storage-1/1_combined/NACC_NEW/ORIG/`

```
NACC_NEW/ORIG/
├── DEMO/
│   ├── merged.csv          (206,768행 × 484열, 55,004명)
│   └── merged_CDR.csv      (206,398행)
├── NII/                     (6,481명)
│   └── NACC{ID}/{v1,v2,...}/{MODALITY}/{protocol}/{date}/{imageID}/*.nii.gz
├── DCM/
└── ZIP/
```

- Subject ID 컬럼: `NACCID` (NACC + 6자리)
- 11+ 모달리티: T1, T2w, FLAIR, T2_STAR(GRE), ASL, HighResHippo, dMRI, rsfMRI, AV45, AV1451, FBB, PIB, MK6240, FDG 등

## 6. 데이터 품질: 이미징-임상 불일치 (Issue #7)

NII 이미징이 있는 6,481명 중 **381명(5.9%)이 merged.csv에 임상 데이터가 전혀 없음**.

| 분류 | 인원 | 비율 |
|------|------|------|
| 이미징 + 임상 모두 있음 | 6,100 | 94.1% |
| **이미징만 있음 (임상 부재)** | **381** | **5.9%** |
| 임상만 있음 (이미징 없음) | 48,904 | — |

### 패턴
- **완전히 이분법적**: 임상 데이터가 있으면 충분(주요 컬럼 100%), 없으면 아예 없음
- `fewer_clinical` (임상이 이미징보다 적은 경우): **0건**
- 381명 중 160명(42%)이 2회 이상 longitudinal 이미징 보유
- 대표: NACC252073 (11회 방문, 9종 모달리티), NACC606503 (10회, 9종)

### 원인
NACC의 임상(UDS)과 이미징(SCAN) 파이프라인이 독립 운영:
- 이미징 제출은 자발적, 기한 없음
- NACCID는 "앞으로 임상 연구에 참여할" 피험자에게 부여 → 미제출 가능성
- 분기별 데이터 업데이트 시 일부 해소될 수 있음

## 7. 후속 조사 필요 사항

- [ ] NACC UDS v4 양식/컬럼 상세 프로파일링
- [ ] NACC-ADNI 공통 subject 연계 가능성 (PTID 매핑)
- [ ] NACC 데이터 다운로드 후 CSV 구조 분석
- [ ] src/nacc 파이프라인 설계 (config, inventory, clinical, pipeline, cli)
- [x] 이미징-임상 불일치 규모 파악 → Issue #7

## Sources

- [NACC Home](https://www.naccdata.org/)
- [About NACC data](https://naccdata.org/requesting-data/nacc-data/)
- [NIA - NACC](https://www.nia.nih.gov/research/dn/national-alzheimers-coordinating-center-nacc)
- [NACC 1999-2025 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12541278/)
- [UDS v4 Updates](https://naccdata.org/nacc-collaborations/uds4-updates)
- [NACC Researcher's Guide](https://www.naccdata.org/the-nacc-researchers-guide)
- [NACC Data File FAQ](https://www.naccdata.org/data-file-faq)
