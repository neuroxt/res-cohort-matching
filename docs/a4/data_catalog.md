# A4/LEARN NFS 데이터 파일 카탈로그

NFS에 분산된 A4/LEARN CSV/PDF 파일의 통합 카탈로그.
파이프라인에서 사용하는 파일은 **[pipeline]** 표시.

**NFS 기준 경로**: `/Volumes/nfs_storage/1_combined/A4/ORIG/`

> **날짜 컨벤션**: A4/LEARN 데이터는 de-identified. 모든 날짜는 `_DAYS_CONSENT` (동의일 기준 경과일)
> 또는 `_DAYS_T0` (연구 시작일 기준: A4=무작위배정일, LEARN=baseline registry 검사일)로 변환됨.

---

## 1. metadata/ — Core Assessment CSVs (31 files, ~288 MB)

PRV2 릴리스 (11Aug2025) 기본 평가 데이터. **대부분 BID + VISCODE 키**.
PRV2는 screening/baseline 위주의 부분 릴리스로, 전체 longitudinal은 `Raw Data/` 참조.

### 인구통계 & 등록

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| A4_PTDEMOG_PRV2_11Aug2025.csv **[pipeline]** | 602K | 6,945 | 14 | **참가자 인구통계**. 성별(PTGENDER: 1=Male, 2=Female), 연령(PTAGE), 교육연수(PTEDUCAT), 인종(PTRACE), 민족(PTETHNIC), 결혼상태(PTMARRY), 모국어(PTLANG/PTPLANG). 파이프라인에서 PTGENDER→M/F 변환에 사용. |
| A4_SUBJINFO_PRV2_11Aug2025.csv **[pipeline]** | 402K | 6,945 | 6 | **피험자 기본정보**. 동의 시 연령(AGEYR), APOE 유전형(APOEGN: E3/E4 형식), APOE 결과 표시 동의(APOEGNPRSNFLGSNM), LEARN 참여 플래그(LRNFLGSNM). 파이프라인에서 APOEGN→e3/e4 변환, AGEYR→세션별 PTAGE 계산에 사용. |
| A4_REGISTRY_PRV2_11Aug2025.csv **[pipeline]** | 1.1M | 18,443 | 8 | **방문 등록부**. 각 방문의 유형(VISTYPE), 검사일(EXAMDAY), 미완료 사유(NDREASON), 재스크리닝 여부(RESCRN), 이전 BID(PREBID). 방문당 1행, 행 수가 피험자 수보다 큼(다회 방문). |
| A4_demography.csv **[pipeline]** | 1.9M | 14,333 | 11 | **LONI 형식 인구통계**. Subject ID, Project(A4/LEARN), Sex, Research Group(amyloid+/amyloidNE/TRT-PBO), Visit, Study Date, Age, Description, Type, Modality. **amyloidNE 스크리닝 탈락자 포함** — PTDEMOG에는 없는 그룹. 파이프라인에서 Research Group 매핑에 사용. |
| A4_PUBLICITY_PRV2_11Aug2025.csv | 392K | 6,945 | 7 | **참여 경로 추적**. 연구를 알게 된 경로(PUBTRACK), 미디어 경로(PUBMEDIA). |

### 인지검사

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| A4_MMSE_PRV2_11Aug2025.csv **[pipeline]** | 1.2M | 6,774 | 39 | **간이정신상태검사 (MMSE)**. 지남력(MMDATE~MMCITY), 기억등록, 주의집중(MMSERIAL), 기억회상, 언어(MMNAME~MMCOPY) 등 30점 만점. 총점=MMSCORE. 검사장소(MMSELOC), 단어목록 버전(WORDLIST). 파이프라인에서 baseline MMSCORE 추출. |
| A4_CDR_PRV2_11Aug2025.csv **[pipeline]** | 582K | 6,322 | 16 | **임상치매척도 (CDR)**. 6개 영역: 기억력(MEMORY), 지남력(ORIENT), 판단력(JUDGE), 사회활동(COMMUN), 가정생활(HOME), 자기관리(CARE). CDR-SB 합산점수(CDSOB). 정보제공자 유형(CDPTSRCE/CDSPSRCE), CDR 버전(CDSPVERS). 파이프라인에서 baseline CDGLOBAL/CDSOB 추출. |
| A4_COGDIGIT_PRV2_11Aug2025.csv | 385K | 6,779 | 7 | **숫자부호치환검사 (DSST)**. 처리속도 측정. 버전(VERSION), 총점(DIGITTOTAL). PACC 구성요소. |
| A4_COGFCSR16_PRV2_11Aug2025.csv | 721K | 6,778 | 18 | **자유·단서 선택적 회상검사 (FCSRT-16)**. 시각적 기억. 자유회상 3회(FCFREET1~3), 단서회상 3회(FCCUEDT1~3), 대체값 플래그(FCCUEDT*_IMPFL). 총점(FCTOTAL96, 96점 만점). PACC 구성요소. |
| A4_COGLOGIC_PRV2_11Aug2025.csv | 415K | 6,796 | 8 | **논리적 기억검사 (Logical Memory)**. 이야기 회상. 즉시회상(LIMMTOTAL), 지연회상(LDELTOTAL), 이야기 버전(LMSTORY). PACC 구성요소. |
| A4_SPPACC_PRV2_11Aug2025.csv **[pipeline]** | 5.8M | 34,010 | 16 | **PACC 서브점수 (Study Partner)**. 평가일(PACCASMDY), 시퀀스(PACCSEQID), 항목번호(PACCQSNUM), 점수(PACCD), 검사명(PACCNAME), 수행자명(PACCPERFSNM). 34K행 = 피험자 × 검사항목 × 방문. |

### Cogstate 전산화 인지검사

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| A4_C3COMP_PRV2_11Aug2025.csv | 22M | 97,362 | 32 | **Cogstate C3 Composite**. 전산화 인지검사 배터리 원시 데이터. 손잡이(Hand), 성별(Sex), 테스트시간(TTime), 테스트코드(TCode), GML인덱스(GMLidx), 초당 움직임(mps), 반응시간(dur), 오류수(ter/ler/rer). 97K행 = 피험자 × 시행 × 방문. |
| A4_CPATH_PRV2_11Aug2025.csv | 69M | 278,973 | 11 | **Cogstate C-Path ADL (일상생활활동)**. 279K행, **대용량 주의**. 세션/시간/질문번호/질문텍스트/답변텍스트/점수(Score)/LMN(Log10 반응시간) 항목 수준 데이터. 복합일상생활활동(CADL) 및 대인기능(IF) 도메인 점수 포함. |
| A4_MACQ_PRV2_11Aug2025.csv | 12M | 67,068 | 10 | **Cogstate 기억불만 설문 (MCQ)**. 67K행. Session/Question/Answer/Answer_Text/Score/LMN. MCQ 총점(MCQT Total) 포함. |

### 주관적 인지·심리 평가

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| A4_CFI_PRV2_11Aug2025.csv | 713K | 6,159 | 22 | **인지기능지표 (CFI) - 참가자**. 기억력(MEMORY), 반복(REPEAT), 분실(MISPLA), 기록(WRITTN), 도움필요(HELP), 회상(RECALL), 운전(DRIVE), 금전관리(MONEY), 사회활동(SOCIAL) 등 주관적 인지변화 자가보고. |
| A4_CFISP_PRV2_11Aug2025.csv | 760K | 6,350 | 23 | **인지기능지표 (CFI) - 연구파트너**. 위와 동일 항목을 연구파트너가 평가 (SP* 접두어). |
| A4_CONCERNS_PRV2_11Aug2025.csv | 776K | 10,302 | 12 | **알츠하이머병 우려**. AD 발생 우려(CADDVLP/CADDVLP5), AD 인지(CADKNOW), AD 신념(CADBLIEV), 최악의 경우(CADWRST), 전반적 우려(CADCNCRN). 10K행 (일부 다회 방문). |
| A4_PSYCHWELL_PRV2_11Aug2025.csv | 832K | 5,827 | 29 | **심리적 안녕감 (GDS 포함)**. 생활만족(GDSATIS), 활동포기(GDDROP), 공허함(GDEMPTY), 지루함(GDBORED), 활력(GDSPIRIT), 두려움(GDAFRAID), 행복(GDHAPPY) 등 GDS 항목 + 안녕감 척도. |
| A4_IES_PRV2_11Aug2025.csv | 508K | 4,385 | 22 | **사건영향척도 (IES)**. 아밀로이드 PET 결과 공개 후 심리적 영향 측정. 생각떠오름(IETHINK), 회피(IEAVOID), 수면장애(IESLEEP), 감정파도(IEWAVES), 꿈(IEDREAMS) 등. |
| A4_FTPSCALE_PRV2_11Aug2025.csv | 937K | 10,296 | 16 | **미래시간전망 척도 (FTP)**. 기회인식(FTOPPS), 목표(FTGOAL), 가능성(FTPOSSBL), 삶의 전망(FTLIFE), 무한함(FTINFINIT), 새로운 것(FTNEW), 시간소진(FTRUNOUT), 한계(FTLIMIT). |

### 기능·신체·생활습관 평가

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| A4_ADLPQ_PRV2_11Aug2025.csv | 1.3M | 6,137 | 45 | **ADL-방지 설문 - 참가자**. ADCS 일상생활활동 예방 버전. 45개 항목: 요리(ASCBOOK), 여행(ASTRAVL), 가전사용(ASAPPLI), 세탁(ASLAUN), 지불(ASPAY) 등. |
| A4_ADLPQSP_PRV2_11Aug2025.csv | 2.6M | 6,331 | 88 | **ADL-방지 설문 - 연구파트너**. 위와 동일 항목을 연구파트너가 평가. 88컬럼(각 항목에 하위문항 A/B/C 포함). |
| A4_PHYNEURO_PRV2_11Aug2025.csv | 667K | 5,695 | 22 | **신체·신경학적 검사**. 두경부/안과(PXHEADEY), 심혈관(PXCARD), 호흡기(PXPULM), 복부(PXABDOM), 근골격(PXMUSCUL), 부종(PXEDEMA), 피부(PXSKIN). 신경학적: 보행(NXGAIT), 진전(NXTREMOR), 감각(NXSENSOR). |
| A4_VITALS_PRV2_11Aug2025.csv | 710K | 5,733 | 19 | **활력징후**. 체중(VSWEIGHT, 단위 VSWTUNIT→표준화 STDWT), 신장(VSHEIGHT→STDHT), 수축기(VSBPSYS)/이완기(VSBPDIA) 혈압, 맥박(VSPULSE), 호흡수(VSRESP), 체온(VSTEMP). |
| A4_HABITS_PRV2_11Aug2025.csv | 476K | 5,893 | 13 | **생활습관**. 흡연(SMOKE), 음주(ALCOHOL), 카페인(CAFFEINE), 약물사용(SUBUSE), 유산소운동(AEROBIC), 걷기(WALKING), 수면시간(SLEEP/SLEEPDAY). |
| A4_INITHEALTH_PRV2_11Aug2025.csv | 5.6M | 66,069 | 13 | **초기 건강력**. 66K행 = 피험자 × 건강상태 항목(반복 레코드). 수술력(IHSURG), 수술일(IHSURGDAY), 현재여부(IHPRESENT), 만성여부(IHCHRON), 심각도(IHSEVER), 발생일(IHDTONSET), 현재상태(IHCUR). |

### 가족력·자살위험·기타

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| A4_FAMHXPAR_PRV2_11Aug2025.csv | 443K | 5,907 | 11 | **가족력 - 부모**. 모친: 치매여부(MOTHER), 발병연령(MOTHAGE), 진단명(MOTHDIAG), 부검여부(MOTHAUT). 부친: 동일 구조(FATHER~FATHAUT). |
| A4_FAMHXSIB_PRV2_11Aug2025.csv | 1.0M | 14,600 | 10 | **가족력 - 형제자매 로그**. 14.6K행 = 피험자 × 형제자매(반복 레코드). 출생연도(SIBYOB), 모친(SIBMOTHER)/부친(SIBFATHER) 공유 여부, 치매여부(SIBDEMENT), 발병연령(SIBAGE), 진단명(SIBDIAG). |
| A4_CSSRS_PRV2_11Aug2025.csv | 990K | 5,660 | 34 | **C-SSRS (Columbia 자살심각성 평가) - 기저/스크리닝**. 자살사고: 죽고싶음(WISHLIFE), 자살생각(ACTLIFE). 자살행동: 방법(METHOD), 의도(INTENT), 계획(PLAN). 3개월(3) 및 생애(무접미) 시점. |
| A4_SPINFO_PRV2_11Aug2025.csv | 522K | 6,824 | 12 | **연구파트너 정보**. 관계(INFRELAT), 성별(INFGENDER), 연령(INFAGE), 동거여부(INFLIVE), 주당 접촉시간(INFHRS). |

### 영상 파라미터 (non-PRV2)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| A4_DWI_PARAMS_with_volumes.csv | 609K | 2,327 | 33 | **DWI 파라미터 + 볼륨**. 시리즈별(series_id) 변환소프트웨어(ConversionSoftware), 시퀀스명(SeriesDescription), 확산 gradient 방향(DiffusionGradientOrientation), TotalReadoutTime, 볼륨 수. |

---

## 2. metadata/A4 Imaging data and docs/ — Imaging CSVs (8) + PDFs (7) + Rmd (1)

영상 정량 데이터 및 방법론 문서. ~10 MB.

### CSVs

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| A4_PETSUVR_PRV2_11Aug2025.csv **[pipeline]** | 3.7M | 35,936 | 12 | **Amyloid PET SUVR 정량분석**. 프로토콜(protocol), 스캔번호(scan_number), 리간드(ligand), 분석여부(scan_analyzed), 뇌영역(brain_region) × 3종 reference: 소뇌(suvr_cer), 백질(suvr_wc). 36K행 = 피험자 × 뇌영역 × 스캔. 파이프라인에서 AMY_SUVR/AMY_CENTILOID 산출에 사용. |
| A4_PETVADATA_PRV2_11Aug2025.csv **[pipeline]** | 415K | 4,492 | 9 | **Amyloid PET 시각평가 (적합성 판정)**. PMOD SUVR composite(PMODSUVR), 판독자1(ELIGVI1)/판독자2(ELIGVI2) 적합성 점수, 합의결과(CONSENSUS), 전체점수(SCORE). 아밀로이드 양성/음성 판정 기준. 파이프라인에서 AMY_STATUS 결정에 사용. |
| A4_VMRI_PRV2_11Aug2025.csv **[pipeline]** | 575K | 1,271 | 53 | **구조적 MRI 볼륨 (FreeSurfer)**. 53개 ROI: 좌우 피질회백질, 측뇌실, 시상, 미상핵, 피각, 담창구, 해마, 편도체, 뇌간, 소뇌 등. 파이프라인에서 VMRI_* (50개 ROI 컬럼 + update_stamp) baseline 값 추출. |
| TAUSUVR_11Aug2025.csv **[pipeline]** | 1.7M | 447 | 274 | **Tau PET SUVR - Stanford 파이프라인**. 274개 FreeSurfer ROI의 Mean intensity (Mean_3rd_Ventricle ~ Mean_Left/Right_*). ID 키 = 순수 BID (underscore 없음, BID_VISCODE 아님). 파이프라인에서 TAU_* (272개 ROI + update_stamp) baseline 값 추출. |
| TAUSUVR_PETSURFER_11Aug2025.csv | 1.0M | 445 | 244 | **Tau PET SUVR - PetSurfer 파이프라인**. 244개 FreeSurfer ROI의 volume-weighted bilateral SUVR (bi_Accumbens_area ~ bi_*). 대안 분석용. |
| A4_DATADIC_PRV2_11Aug2025.csv | 229K | 1,193 | 10 | **PRV2 데이터 사전**. metadata/ PRV2 CSV들의 필드 정의. FLDNAME(필드명), TBLNAME(테이블명), CRFNAME(CRF명), TEXT(설명), CODE(코딩). |
| A4_DWI_PARAMS_PRV2_11Aug2025.csv | 533K | 1,815 | 27 | **DWI 스캔 파라미터**. 시리즈별(series_id) BIDS JSON sidecar 정보: ConversionSoftware, SeriesDescription, DiffusionGradientOrientation, TotalReadoutTime, EchoTime, RepetitionTime 등 27개 파라미터. |
| A4_FMRI_PARAMS_PRV2_11Aug2025.csv | 791K | 1,687 | 27 | **fMRI 스캔 파라미터**. DWI와 유사한 구조. TotalReadoutTime, SliceTiming, EchoTime, RepetitionTime, PhaseEncodingDirection 등 resting-state fMRI 시퀀스 메타데이터. |

### PDFs — 영상 방법론

| 파일명 | 크기 | 설명 |
|--------|------|------|
| A4_PET_Processing_Details_20221019.pdf | 205K | PET 데이터 수집·처리·QC 파이프라인 상세 (motion correction, co-registration, SUVR 계산 절차). |
| A4_PETSUVR_Amyloid_PET_Quantitative_Methods.pdf | 153K | Amyloid PET SUVR 정량 방법론: reference region 정의(whole cerebellum, persi white matter, cerebellar crus), ROI 정의, centiloid 변환. |
| A4_PETVADATA_Amyloid_PET_Eligibility_Methods.pdf | 100K | Amyloid PET 적합성 시각평가 방법론: 2명 독립 판독, 불일치 시 합의 프로세스, 양성/음성 판정 기준. |
| A4_VMRI_Volumetric_MRI_Methods.pdf | 114K | FreeSurfer 기반 구조적 MRI 볼륨 분석: T1w 영상 전처리, 분할(segmentation), ROI 볼륨 추출 프로토콜. |
| A4_Pre-Rand_Data_FAQ.pdf | 136K | Pre-randomization 데이터 FAQ: 데이터 구조, 변수 설명, 자주 묻는 질문. |
| A4_Pre-rand_Data_Primer.pdf | 234K | Pre-randomization 데이터 입문서: 데이터셋 개요, 분석 사례, 코드 예시. |
| Quick_Guide_to_A4_imaging_data_v1.1.pdf | 111K | 영상 데이터 퀵 가이드: 파일 구조, 다운로드 방법, 영상 유형별 설명. |

### Other

| 파일명 | 크기 | 설명 |
|--------|------|------|
| a4_pre_rand_data_primer.Rmd | 6.5K | Pre-randomization 데이터 입문서의 R Markdown 원본 (재현 가능한 분석 예시). |

---

## 3. DEMO/Clinical/Raw Data/ — Longitudinal Assessments (27 CSVs, ~70 MB)

모든 방문에 걸친 **raw longitudinal 데이터**. metadata/ PRV2 파일의 전체 버전.

> **metadata/ vs Raw Data/**:
> - **metadata/ (PRV2)**: 부분 릴리스 (~6K행, screening/baseline 위주). CRF 구조 그대로.
> - **Raw Data/**: 전체 longitudinal (~6K–27K행, 모든 방문 포함). 일부 추가 컬럼 있음.
> - 파이프라인에서 MMSE/CDR longitudinal 분석 시에는 **Raw Data 사용**.

### 인지검사 (longitudinal)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| mmse.csv **[pipeline]** | 8.7M | 26,765 | 41 | **MMSE — 전체 longitudinal**. PRV2(6.8K) 대비 4배 행 수. 모든 방문의 MMSE 점수 포함. 파이프라인에서 longitudinal MMSCORE 추출(LONG_MMSE_* 컬럼 생성). |
| cdr.csv **[pipeline]** | 2.4M | 15,511 | 25 | **CDR — 전체 longitudinal**. PRV2(6.3K) 대비 2.5배. 모든 방문의 CDR 영역점수 + CDR-SB. 25컬럼(PRV2 16컬럼 대비 추가 필드). 파이프라인에서 longitudinal CDGLOBAL/CDSOB 추출. |
| cogdigit.csv | 1.6M | 26,770 | 7 | **DSST — 전체 longitudinal**. 처리속도(DIGITTOTAL). PRV2(6.8K) 대비 4배. |
| cogfcsr16.csv | 2.2M | 26,769 | 19 | **FCSRT-16 — 전체 longitudinal**. 자유/단서 회상(FCFREET1~3, FCCUEDT1~3), 총점(FCTOTAL96). |
| coglogic.csv | 1.7M | 26,788 | 8 | **Logical Memory — 전체 longitudinal**. 즉시(LIMMTOTAL)/지연(LDELTOTAL) 회상. |

### 기능·생활·심리 평가 (longitudinal)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| adlpq.csv | 12M | 15,335 | 45 | ADL-방지 설문 - 참가자. 일상생활활동 45개 항목 전체 방문. |
| adlpqsp.csv | 14M | 15,524 | 88 | ADL-방지 설문 - 연구파트너. 88개 항목(하위문항 포함). |
| cfi.csv | 2.0M | 15,355 | 22 | 인지기능지표(CFI) - 참가자. 주관적 인지변화 자가보고. |
| cfisp.csv | 2.1M | 15,540 | 23 | 인지기능지표(CFI) - 연구파트너. |
| concerns.csv | 639K | 15,472 | 12 | 알츠하이머병 우려도. |
| psychwell.csv | 1.6M | 21,778 | 29 | 심리적 안녕감(GDS 포함). |
| ftpscale.csv | 875K | 17,665 | 16 | 미래시간전망 척도(FTP). |
| views.csv | 516K | 10,297 | 16 | 아밀로이드 영상 관련 견해/인식. |
| ies.csv | 289K | 4,392 | 23 | 사건영향척도(IES). 아밀로이드 결과 공개 후 심리적 영향. |
| rss.csv | 392K | 7,431 | 17 | **연구만족도 조사**. 완료(RSSCOMP), 질(RSSQUAL), 기대(RSSEXPECT), 추천(RSSRECOM), 재참여(RSSREDO), 최선/최악 경험, 의약품/검사/방문 관련 항목. |

### 약물·안전·신체 (longitudinal)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| dose.csv | 12M | 75,242 | 16 | **약물투여 기록**. 75K행 = 매 투여 시점. 투여장소(LOCATION), 투여량(VOLUME), 시작/종료일(STARTDATE/ENDDATE_DAYS_CONSENT/_T0), 완료여부(COMPLETE), 시도횟수(ATTEMPTNUM), 투여레벨(DOSELEVEL), 맹검투여(BLINDDOSE). |
| cssrs.csv | 898K | 5,661 | 55 | C-SSRS 기저/스크리닝. 55컬럼(PRV2 34컬럼 대비 추가 세부항목). |
| cssrslv.csv | 1.7M | 18,852 | 30 | **C-SSRS — 마지막 방문 이후**. 방문간 자살사고/행동 변화 추적. 사고(WISHLV), 행동(ACTLV), 방법(METHODLV), 의도(INTENTLV), 빈도(FREQLV), 기간(DURATLV), 통제(CONTROLLV). |
| vitals.csv | 1.6M | 21,828 | 19 | 활력징후. 체중/신장/혈압/맥박/호흡/체온 전체 방문. |
| phyneuro.csv | 727K | 11,480 | 22 | 신체·신경학적 검사 전체 방문. |
| habits.csv | 647K | 14,307 | 13 | 생활습관(흡연/음주/운동/수면). |

### 기타 (longitudinal)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| ptdemog.csv | 375K | 6,946 | 15 | 인구통계(거의 baseline 1회 ≈ PRV2와 동일). |
| famhxpar.csv | 254K | 5,908 | 11 | 가족력-부모(baseline 1회). |
| famhxsib.csv | 646K | 14,601 | 11 | 가족력-형제자매(반복 레코드). |
| spinfo.csv | 327K | 7,647 | 12 | 연구파트너 정보. |
| ruib.csv | 522K | 9,149 | 18 | **자원이용 인벤토리 - 간략형**. 입원(BRADMIT), 진료(BREXAM), 도움필요(BRHELP/BRUPHELP), 봉사(VOLUNTEER/VOLHRS), 고용상태(EMPLOY/EMPHRS), 상실(LOST). |
| ruib1.csv | 35K | 1,107 | 6 | 자원이용 인벤토리 - 입원 로그. 입원일수(BR1NIGHT), 유형(BR1TYPE). |

---

## 4. DEMO/Clinical/Derived Data/ — Derived Measures (6 CSVs, ~152 MB)

가공된 파생 데이터. **SV.csv가 session-centric MERGED.csv의 기반**.

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| SV.csv **[pipeline]** | 7.8M | 103,351 | 9 | **방문 스케줄 마스터**. session-centric MERGED.csv의 인덱스 기반. BID + VISITCD(방문코드). 방문시작일(SVSTDTC_DAYS_CONSENT/_T0), 방문종료일(SVUSEDTC_DAYS_CONSENT/_T0), 방문유형(SVTYPE: Standard/Nonstandard/Not Done). 103K행 = 전체 피험자 × 전체 방문. 파이프라인의 `build_session_index()`에서 DAYS_CONSENT + PTAGE 계산에 사용. |
| SUBJINFO.csv | 1.9M | 6,946 | 62 | **[Derived] 피험자 종합정보**. 치료배정(TX), 동의시 연령(AGEYR), 결혼상태(MARITAL), 성별(SEX), 인종(RACE), 교육연수(EDCCNTU), 거주형태(RESIDENCE), 은퇴상태(WRKRET), 검사언어(TESTLNG), 중단일(DISCDTC_DAYS_CONSENT) 등 **62개 파생 변수**. metadata/SUBJINFO(6컬럼)의 확장 버전. |
| PACC.csv | 7.9M | 26,781 | 31 | **[Derived] PACC 복합점수**. 원점수(PACC.raw), 기저대비 변화량(PACC), 대체값 플래그(PACCIMPFLG). 구성요소: FCSRT 총점(FCTOTAL96), 논리기억(LDELTOTAL), DSST(DIGITTOTAL), MMSE(MMSCORE). 각각 기저값(*_bl), 기저 평균(*_blmean), 기저 SD(*_blsd) 포함. |
| DS.csv | 1.2M | 16,263 | 9 | **[Derived] 연구참여 경과 (Disposition)**. mITT 플래그(DSDECOD: 기저+사후 관찰 있는 무작위배정 피험자=1), 범주(DSCAT: 프로토콜 마일스톤 vs 경과 사건), EPOCH(연구 시기), 경과일(DSSTDTC_DAYS_CONSENT/_T0, DSSTDY). |
| COGSTATE_COMPUTERIZED.csv | 27M | 315,597 | 14 | **[Derived] Cogstate 전산화 검사**. 검사코드(TESTCD), 점수(VALUE), 시행횟수(TRIAL), 기저값(BASELINE.VALUE/TRIAL), 기저대비 변화(VALUE.DIF), 연구주차(ADURW). 315K행 = 피험자 × 검사 × 방문. |
| ADQS.csv | 107M | 247,290 | 81 | **[Derived] 설문 분석 점수 — 대용량(107MB)**. 모든 설문(QSCAT: ADAS-COG, MDS-UPDRS 등)의 항목별(QSTESTCD/QSTEST) 표준화 점수(QSSTRESN), 기저값(QSBLRES), 변화량(QSCHANGE), 기저 SD(QSBLSD), 기저 플래그(QSBLFL), 검사일(QSDTC_DAYS_CONSENT). |

---

## 5. DEMO/Clinical/External Data/ — Biomarkers + External Imaging (17 CSVs, ~533 MB)

외부 분석 기관(중앙연구소, Cogstate, UCSF 등) 데이터.

### 혈액 바이오마커

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| biomarker_pTau217.csv **[pipeline]** | 2.0M | 4,538 | 18 | **pTau-217 디지털 면역분석**. ALZpath pTau-217 검사. 검체(SPEC), 검사명(TESTCD/TEST), 결과값(ORRES), 단위(ORRESU), 완료상태(STAT), 미완료 사유(REASND), 검사기관(NAM), 채혈일(COLLECTION_DATE_DAYS_CONSENT/_T0). 파이프라인에서 방문별 wide-format (PTAU217_BL, _WK12, _WK240 등) 변환. |
| biomarker_Plasma_Roche_Results.csv **[pipeline]** | 2.2M | 13,418 | 14 | **Roche 혈장 분석**. Roche Elecsys 플랫폼. 검사기관(LABNAM), 채혈일(LABD_DAYS_CONSENT/_T0), 검체(LBSPEC), 검사법(LBMETHOD), 검사코드(LBTESTCD), 검사명(LBMTDL), 결과(LABRESN), 단위(LABORESU). Aβ42, Aβ40, pTau181, GFAP, NfL 등 다중 마커. |
| biomarker_AB_Test.csv **[pipeline]** | 3.8M | 31,480 | 12 | **Amyloid-β 검사**. 다양한 아밀로이드 관련 혈액검사. 검체유형(LBSPEC), 범주(LBCAT), 검사코드(LBTESTCD), 결과(LBORRES), 단위(LBORRESU), 검사법(LBMETHOD). 31K행 = 피험자 × 검사항목 × 시점. |

### 외부 영상 정량분석

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| imaging_SUVR_amyloid.csv | 3.7M | 45,968 | 12 | **Amyloid PET SUVR (외부)**. metadata/PETSUVR의 확장 버전. 스캔번호(scan_number), 날짜(scan_date_DAYS_CONSENT/_T0), 리간드(ligand), 분석여부(scan_analyzed), 뇌영역(brain_region) × 3종 reference region (suvr_cer, suvr_persi, suvr_crus). |
| imaging_SUVR_tau.csv | 25M | 296,680 | 12 | **Tau PET SUVR (외부)**. 296K행, 위와 동일 구조. Flortaucipir(FTP) 리간드 기반 tau 축적량. 뇌영역별 SUVR × 3종 reference region. |
| imaging_Tau_PET_Stanford.csv | 1.5M | 448 | 275 | **Tau PET - Stanford 파이프라인**. 275개 FreeSurfer ROI의 Mean intensity. Wide format (1행 = 1스캔). metadata/TAUSUVR와 유사하나 외부 경로 배포본. |
| imaging_Tau_PET_PetSurfer.csv | 804K | 446 | 245 | **Tau PET - PetSurfer 파이프라인**. 245개 ROI의 volume-weighted bilateral SUVR. |
| imaging_volumetric_mri.csv | 1.0M | 2,952 | 58 | **구조적 MRI 볼륨 (외부)**. 검사일(Date_DAYS_CONSENT/_T0) + 58개 ROI: 좌우 피질회백질, 측뇌실, 시상, 미상핵, 피각, 담창구, 해마, 편도체 등. metadata/VMRI의 확장 버전(날짜 포함). |
| imaging_PET_VA.csv | 359K | 4,493 | 12 | **Amyloid PET 시각평가 (외부)**. 스캔번호, 날짜, 리간드, PMOD SUVR composite(pmod_suvr), 판독자1/2 점수(elig_vi_1/2), 합의(consensus), 전체 양/음 판정(overall_score). |
| imaging_FLAIR_WMH_QC.csv | 645K | 6,794 | 9 | **FLAIR MRI 백질고강도신호(WMH) QC**. 폴더명(foldername), QC 통과여부(QC), QC 메모(QCNotes), WMH 볼륨(WMHvol_masked, mm³), 두개내 총 부피(ICV, mm³), 분석용 보정값(WMH_corrected = WMHvol_masked/ICV × 1300). |
| imaging_MRI_reads.csv | 60K | 1,798 | 9 | **MRI 판독 결과**. 확실한 미세출혈(Definite.MCH), 엽(Lobar)/심부(Deep) 미세출혈, 확실한 표면 시데로시스(Definite.SS). ARIA 모니터링용. |
| imaging_retinal.csv | 30K | 499 | 10 | **망막 영상**. 검사일, 눈(Eye), 위치(Field), 총 영상 수(NumberOfImages), 통과 영상 수(NumberPassingImages), 제외여부(Exclude), RAI 모델 점수(RAIModelScore: PET 아밀로이드 상태 기반 판별 점수). |

### Cogstate (외부 배포)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| cogstate_cpath.csv | 159M | 801,135 | 12 | **Cogstate C-Path ADL — 대용량(159MB)**. 항목 수준(item-level) 데이터. 날짜(Date_DAYS_CONSENT/_T0), 세션(Session_ID), 지시문(Instructions), 질문번호/텍스트, 답변텍스트, 점수(Score), LMN(Log10 반응시간). CADL(복합일상활동) + IF(대인기능) 도메인 점수 및 총점 포함. |
| cogstate_battery.csv | 51M | 278,213 | 40 | **Cogstate 전산화 배터리 (외부)**. 손잡이(Hand), 검사일(TDate_DAYS_*), 세션(Session_ID), 테스트코드(TCode), GML인덱스, mps(초당 움직임), dur(검사시간 ms), ter(총오류), ler(합법오류), rer(규칙위반오류). |
| cogstate_macq.csv | 25M | 192,098 | 11 | **Cogstate 기억불만설문 (MCQ, 외부)**. 질문(Question), 답변(Answer/Answer Text), 점수(Score), LMN. MCQ 총점 포함. |

### 대규모 모니터링 (CLRM)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| clrm_lab.csv | 160M | 607,614 | 44 | **중앙검사실 — 혈액/소변 검사 — 대용량(160MB)**. 방문유형(VISITTYP/VISITMOD), 검사기관(LBNAM), 채혈일(LBDTM_DAYS_*), 수신일(RCVDTM_DAYS_*), 검체(LBSPEC), 공복여부(FASTSTAT), 배터리ID(BATTRID), 검사항목(LBTESTCD) × 결과값. 607K행 = 피험자 × 검사항목 × 방문. |
| clrm_ecg.csv | 98M | 377,440 | 44 | **중앙검사실 — 심전도(ECG) — 대용량(98MB)**. 위와 동일 구조. 377K행. HR, PR interval, QRS, QT/QTc 등 ECG 파라미터. |

---

## 6. DEMO/Clinical/Documents/ — Data Dictionaries (4 CSVs) + Methods PDFs (10) + Guides (5)

### Data Dictionaries

| 파일명 | 크기 | 행 수 | 설명 |
|--------|------|-------|------|
| clinical_datadic.csv | 88K | 620 | **임상 CRF 데이터 사전**. 27개 CRF에 대한 필드 정의: CRF_NAME, CRF_LABEL, FIELD_NAME, TEXT(설명), FIELD_FORMAT, FIELD_CODE(코딩값). Raw Data/ CSV 필드 이해에 필수. |
| derived_datadic.csv | 29K | 207 | **파생 데이터 사전**. 6개 파생 CSV(ADQS, COGSTATE, DS, PACC, SUBJINFO, SV)의 필드 정의: FILE_NAME, FILE_LABEL, FIELD_NAME, FIELD_DESC. |
| external_datadic.csv | 129K | 836 | **외부 데이터 사전**. 17개 외부 CSV의 필드 정의. 바이오마커, 영상, Cogstate, CLRM 필드 설명 포함. |
| visits_datadic.csv | 16K | 153 | **방문 코드 사전**. A4/LEARN 각 VISCODE의 방문명(VISNAME), 순서(VISORDER), 속성(ATTRIBS: sc1, sc2, bl, w012 등), 방문그룹(VISITGROUP: Screening, Treatment, Follow-Up). |

### Methods PDFs — 외부 데이터 방법론

| 파일명 | 크기 | 설명 |
|--------|------|------|
| biomarker_assay_methods.pdf | 316K | 혈액 바이오마커 분석법: pTau-217, Roche Elecsys 패널(Aβ42/40, pTau181, GFAP, NfL), AB_Test 분석 조건 및 정도관리. |
| clrm_methods.pdf | 315K | CLRM 중앙검사실 방법론: 혈액/소변 검체 처리, ECG 기록 및 판독, 정상범위 정의, 이상치 플래깅. |
| cogstate_methods.pdf | 311K | Cogstate 전산화 인지검사 방법론: 배터리 구성, C-Path ADL, MCQ 채점 규칙, LMN 계산, 품질관리. |
| imaging_FLAIR_WMH_QC_methods.pdf | 305K | FLAIR WMH QC 방법론: 자동 분할, FreeSurfer 마스킹, ICV 보정, QC 기준(통과/실패/수정). |
| imaging_MRI_reads_methods.pdf | 311K | MRI 판독 방법론: 미세출혈(MCH) 판독 기준, 표면 시데로시스(SS) 분류, ARIA 모니터링 프로토콜. |
| imaging_PET_VA_methods.pdf | 318K | Amyloid PET 시각평가 방법론: 2인 독립 판독, 5점 척도, 양성/음성 합의, SUVR 보조 기준. |
| imaging_retinal_methods.pdf | 301K | 망막 영상 방법론: OCT/안저촬영 프로토콜, 영상 품질 기준, RAI 모델 아밀로이드 판별 알고리즘. |
| imaging_SUVR_methods.pdf | 320K | PET SUVR 정량 방법론: Amyloid/Tau 공통 — FreeSurfer 분할, reference region 정의(cerebellum, persi WM, crus), centiloid 변환, 종단 분석 방법. |
| imaging_Tau_PET_methods.pdf | 412K | Tau PET 방법론: Stanford 파이프라인(Mean intensity per ROI) vs PetSurfer 파이프라인(volume-weighted bilateral SUVR). ROI 정의, 전처리 차이, 파이프라인 비교. |
| imaging_volumetric_MRI_methods.pdf | 311K | Volumetric MRI 방법론: FreeSurfer cross-sectional 분석, ROI 정의, 볼륨 추출, QC, 종단 변화 분석. |

### FAQ + Guides

| 파일명 | 크기 | 설명 |
|--------|------|------|
| a4_learn_data_faq.pdf | 314K | A4/LEARN 데이터 FAQ: 데이터 접근 방법, DAYS_CONSENT/DAYS_T0 차이, SUBSTUDY 코드, BID/VISCODE 규칙, 자주 발생하는 질문과 해결법. |
| a4_learn_data_primer.pdf | 417K | A4/LEARN 데이터 입문서: 연구 설계 개요, 데이터 구조, 주요 변수 설명, R 코드 예시, 분석 팁. |
| a4_learn_data_primer.Rmd | 9.0K | 데이터 입문서 R Markdown 원본 (재현 가능한 분석). |
| Intro-to-A4-data.pdf | 468K | A4 데이터 소개: 연구 배경, 코호트 구성, 데이터 타입 분류, 다운로드 절차. |
| Intro-to-A4-data.Rmd | 12K | A4 데이터 소개 R Markdown 원본. |

---

## Summary Table

| 디렉토리 | CSVs | PDFs | Rmd | 총 크기 |
|----------|------|------|-----|---------|
| metadata/ (root) | 31 | — | — | ~130 MB |
| metadata/A4 Imaging data and docs/ | 8 | 7 | 1 | ~10 MB |
| DEMO/Clinical/Raw Data/ | 27 | — | — | ~70 MB |
| DEMO/Clinical/Derived Data/ | 6 | — | — | ~152 MB |
| DEMO/Clinical/External Data/ | 17 | — | — | ~533 MB |
| DEMO/Clinical/Documents/ | 4 | 13 | 2 | ~5 MB |
| **합계** | **93** | **20** | **3** | **~900 MB** |

---

## 주요 참고사항

### Primary Key 규칙
- **대부분의 CSV**: `BID` + `VISCODE` (방문코드)
- **TAUSUVR / TAUSUVR_PETSURFER**: `ID` (= 순수 BID, underscore 없음)
- **SV.csv**: `BID` + `VISITCD` (VISCODE와 유사하나 별도 체계, 주의)
- **반복 레코드 CSV** (INITHEALTH, FAMHXSIB, RUIB1): `BID` + `VISCODE` + `RECNO`
- **Cogstate 외부**: `BID` + `VISCODE` + `Session_ID`

### metadata/ vs Raw Data/ vs Derived Data/ 관계
```
metadata/ (PRV2)          → screening/baseline 부분 릴리스 (~6K행)
                               ↓ 전체 버전
Raw Data/ (longitudinal)  → 모든 방문 포함 raw CRF 데이터 (~6K–27K행)
                               ↓ 가공
Derived Data/             → 표준화 · 점수 계산 · wide format 파생 데이터
```

### 대용량 파일 주의 (로딩 시 메모리/시간 고려)
| 파일 | 행 수 | 크기 | 내용 |
|------|-------|------|------|
| cogstate_cpath.csv | 801K | 159M | C-Path ADL item-level 응답 |
| clrm_lab.csv | 608K | 160M | 중앙검사실 혈액/소변 검사 항목별 결과 |
| clrm_ecg.csv | 377K | 98M | 중앙검사실 ECG 파라미터 |
| ADQS.csv | 247K | 107M | 전 설문 항목별 표준화 점수 |
| cogstate_battery.csv | 278K | 51M | 전산화 인지검사 배터리 원시 |
| A4_CPATH_PRV2_11Aug2025.csv | 279K | 69M | C-Path ADL item-level (PRV2) |

### config.py 매핑 → 파이프라인 사용 파일

```
CLINICAL_CSV_FILES (metadata/):
  ptdemog    → 인구통계 (PTGENDER, PTAGE, PTEDUCAT)
  subjinfo   → AGEYR, APOEGN
  registry   → 방문 등록 (VISTYPE, EXAMDAY)
  mmse       → MMSE 기저 점수 (MMSCORE)
  cdr        → CDR 기저 점수 (CDGLOBAL, CDSOB)
  pacc       → PACC 서브점수 (SPPACC)
  demography → Research Group 매핑 (amyloidNE 포함)

IMAGING_CSV_FILES (metadata/A4 Imaging data and docs/):
  petsuvr    → Amyloid PET SUVR (AMY_SUVR, AMY_CENTILOID)
  petvadata  → Amyloid PET 시각평가 (AMY_STATUS)
  vmri       → FreeSurfer ROI 볼륨 (VMRI_* 50 ROI)
  tausuvr    → Tau PET ROI (TAU_* 272 ROI)

BIOMARKER_CSV_FILES (External Data/):
  ptau217      → pTau-217 wide-format (PTAU217_BL 등)
  roche_plasma → Roche Elecsys 혈장 패널
  ab_test      → Amyloid-β 혈액검사

LONGITUDINAL_CSV_FILES (Raw Data/ + Derived Data/):
  sv   → SV.csv — 세션 인덱스 기반 (DAYS_CONSENT, PTAGE 계산)
  mmse → mmse.csv — longitudinal MMSE (LONG_MMSE_*)
  cdr  → cdr.csv — longitudinal CDR (LONG_CDR_*)
```
