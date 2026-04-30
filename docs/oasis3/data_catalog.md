# OASIS3 NFS 데이터 파일 카탈로그

NFS에 분산된 OASIS3 CSV 파일의 통합 카탈로그. **현재 OASIS3 전용 파이프라인은 미구현**이므로, 이 문서는 향후 분석/파이프라인 작업 시 참조 인벤토리로 사용된다.

**NFS 기준 경로**: `/Volumes/nfs_storage/OASIS3/ORIG/DEMO/`

> **날짜 컨벤션**: OASIS3 데이터는 모두 de-identified. 모든 시간은 `days_to_visit` (피험자별 첫 방문일 = `d0000` 기준 경과일)로 표현.
>
> **세션 라벨 grammar**: `OAS3{0001-1378}_{FORM}_d{0000-9999}` — 예: `OAS30001_UDSb4_d0339` = subject `OAS30001`, NACC UDS b4(CDR) form, day 339. 자세한 규칙은 [`session_label_reference.md`](session_label_reference.md).
>
> **상위 디렉터리 구성**: `/Volumes/nfs_storage/OASIS3/ORIG/`에는 `DEMO/`(이 문서 대상), `NII/`(영상 NIfTI), `DCM/`(원본 DICOM), `JSON/`(BIDS sidecar)가 있고, `/Volumes/nfs_storage/OASIS3/PROC/`에는 파생 데이터가 있다.

---

## 1. Subject-Level 데이터 (1 file, ~78 KB)

피험자당 1행. APOE/race/education 등 변동되지 않는 정보.

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| OASIS3_demographics.csv | 78K | 1,379 | 19 | **참가자 인구통계 (subject-level)**. OASISID(unique), GENDER(1=Male/2=Female), AgeatEntry/AgeatDeath(de-identified, 90+ ceiling), EDUC(years), SES(Hollingshead), 인종 인코딩 4종(racecode/race/AIAN/NHPI/ASIAN/AA/WHITE flags), ETHNIC(0/1), daddem/momdem(부모 치매), HAND(R/L/B), APOE(2자리: 22/23/24/33/34/44 + 0=결측 + #N/A). 자세한 컬럼 정의는 [`demographics.md`](demographics.md). |

---

## 2. NACC UDS A-forms — 등록·인구통계·약물·건강력 (6 files, ~5.2 MB)

NACC Uniform Data Set의 Initial/Follow-up Visit Packet (IVP/FVP) A 시리즈. 공통 키 `(OASISID, OASIS_session_label, days_to_visit, age at visit)`. 자세한 폼별 컬럼은 [`uds_forms.md`](uds_forms.md).

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| OASIS3_UDSa1_participant_demo.csv | 478K | 8,500 | 14 | **Form A1 — 참가자 인구통계 (visit-level)**. REASON(방문 사유), REFER(의뢰 경로), LIVSIT/LIVSITUA(거주 형태), INDEPEND(독립성), RESIDENC, MARISTAT(결혼). 변동 가능 정보(주거·결혼)를 longitudinal로 추적. |
| OASIS3_UDSa2_cs_demo.csv | 527K | 8,500 | 17 | **Form A2 — Co-participant (정보제공자) demographics**. INSEX, INHISP/INHISPOR, INRACE/INRASEC/INRATER, INEDUC(교육연수), INRELTO(피험자와의 관계), INLIVWTH(동거 여부), INVISITS/INCALLS(접촉 빈도), INRELY(신뢰도). |
| OASIS3_UDSa3.csv | 1.8M | 4,090 | **398** | **Form A3 — Subject family history (가족력)**. 외조부모(GMOM*/GDAD*), 친조부모(미별도), 부모(MOM*/DAD*), 형제자매(SIB1-20*) 각각 ID/YOB/LIV/YOD/DEM(치매)/ONSET(발병연령)/AUTO(부검여부)/SEX. **398 컬럼** 중 대부분은 sibling slot 20개 × 8 fields. A3CHG(변화 여부), TWIN/TWINTYPE(쌍둥이). |
| OASIS3_UDSa4D_med_codes.csv | 957K | 7,617 | 51 | **Form A4 — 처방/OTC 약물 코드**. anymeds(0/1), drug1~drug46(NACC 약물 코드, integer). UDS v3에서 a4가 D(코드)/G(이름)로 분할됨. |
| OASIS3_UDSa4G_med_names.csv | 1.5M | 7,617 | 51 | **Form A4 — 약물명 (text)**. anymeds, meds_1~meds_46(약물명 free text, e.g., `LISINOPR`, `ASA`, `CALCIUM`). a4D와 1:1 페어. |
| OASIS3_UDSa5_health_history.csv | 1.1M | 8,500 | 72 | **Form A5 — 건강력**. 심혈관(CVHATT, CVAFIB, CVANGIO, CVBYPASS, CVPACE, CVCHF, CVOTHR), 뇌혈관(CBSTROKE, CBTIA), 신경(PD, SEIZURES, TBI*), 대사(HYPERTEN, HYPERCHO, DIABETES, B12DEF, THYROID), 정신(DEP2YRS, ALCOHOL, ABUSOTHR, PSYCDIS), 수면(APNEA, RBD, INSOMN), 흡연(TOBAC30/TOBAC100/SMOKYRS/PACKSPER/QUITSMOK). 코딩: 0/1/9(unknown), 88/888(N/A). |

---

## 3. NACC UDS B-forms — 임상 평가 (9 files, ~5.5 MB)

신체검사·인지/정신상태·신경학적 평가. 공통 키 동일.

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| OASIS3_UDSb1_physical_eval.csv | 589K | 8,627 | 15 | **Form B1 — 신체검사**. WEIGHT(lb), HEIGHT(in), BPSYS/BPDIAS, HRATE(bpm), VISION/VISCORR/VISWCORR(시력 코드), HEARING/HEARAID/HEARWAID(청력). 999=missing. |
| OASIS3_UDSb2_his_cvd.csv | 539K | 8,500 | 20 | **Form B2 — Hachinski Ischemic Score (HIS)**. 혈관성 치매 평가: ABRUPT(급성 발병), STEPWISE, SOMATIC, EMOT, HXHYPER/HXSTROKE, FOCLSYM/FOCLSIGN, HACHIN(총점), CVDCOG(CVD-cog), CVDIMAG1-4(영상 소견 카테고리). |
| OASIS3_UDSb3.csv | 307K | 4,090 | 32 | **Form B3 — UPDRS (Unified Parkinson's Disease Rating Scale)**. 운동 평가: SPEECH, FACEXP, TRESTFAC/RHD/LHD/RFT/LFT(휴식 떨림), TRACTRHD/LHD(자세 떨림), RIGD*(경직), TAPSRT/LF(손가락 두드리기), HANDMOVR/L, HANDALTR/L, LEGRT/LF, ARISING, POSTURE, GAIT, POSSTAB, BRADYKIN. PD 의심 시만 시행 — UDS optional module. |
| OASIS3_UDSb4_cdr.csv | 916K | 8,627 | 23 | **Form B4 — CDR (+ MMSE + 진단)**. MMSE(0-30), 6 도메인 CDR: memory, orient, judgment, commun, homehobb, perscare(0/0.5/1/2/3), CDRSUM(합산), CDRTOT(global, 0/0.5/1/2/3), dx1-dx5(코드 + free text label). 임상 진단 매핑 시 핵심. |
| OASIS3_UDSb5_npiq.csv | 677K | 8,500 | 29 | **Form B5 — NPI-Q (Neuropsychiatric Inventory Questionnaire)**. 12 도메인 행동/정신 증상 × {존재(0/1), 심각도(1/2/3)}: DEL(망상)/DELSEV, HALL/HALLSEV, AGIT, DEPD, ANX, ELAT, APA(무관심), DISN(탈억제), IRR(과민), MOT(운동), NITE(야간행동), APP(식욕). NPIQINF=정보제공자 코드. |
| OASIS3_UDSb6_gds.csv | 623K | 8,500 | 21 | **Form B6 — GDS-15 (Geriatric Depression Scale, 15-item)**. NOGDS(시행 여부), 15 항목(SATIS, DROPACT, EMPTY, BORED, SPIRITS, AFRAID, HAPPY, HELPLESS, STAYHOME, MEMPROB, WONDRFUL, WRTHLESS, ENERGY, HOPELESS, BETTER) + GDS(총점). |
| OASIS3_UDSb7_faq_fas.csv | 519K | 8,500 | 14 | **Form B7 — FAQ (Functional Activities Questionnaire)**. 10 ADL/IADL: BILLS(공과금), TAXES(세금), SHOPPING, GAMES, STOVE(가스), MEALPREP, EVENTS, PAYATTN(주의), REMDATES, TRAVEL. 0=normal, 1=dependent, 2=requires assistance, 3=dependent. |
| OASIS3_UDSb8_neuro_exam.csv | 770K | 8,500 | 50 | **Form B8 — 신경학적 검사**. NORMAL/NORMEXAM(전체 정상), FOCLDEF(국소 결손), GAITDIS, EYEMOVE, PARKSIGN(파킨슨 징후 + RESTTRL/R, SLOWING, RIGID, BRADY, PARKGAIT, POSTINST), CVDSIGNS(혈관 징후), CORTDEF(피질 징후), PSPCBS(PSP/CBS 변종), APRAX*, ATAX*, ALIENLM*, DYSTON*, MYOCL*, ALSFIND, GAITNPH(NPH 보행). |
| OASIS3_UDSb9_symptoms.csv | 916K | 8,500 | 58 | **Form B9 — Clinician 판정 증상/임상양상**. DECSUB(주관 보고)/DECIN(정보제공자)/DECCLIN(임상의), COG{MEM, JUDG, ORI, LANG, VIS, ATTN, FLUC}, BE{APATHY, DEP, VHALL, AHALL, DEL, DISIN, IRRIT, AGIT, PERCH, REM, ANX}, MO{GAIT, FALLS, TREM, SLOW}, COURSE(경과), FRSTCHG(첫 변화), LBDEVAL/FTLDEVAL(검사 여부). |

---

## 4. NACC UDS C/D-forms — 인지 검사 + 진단 + 의학 상태 (3 files, ~4.3 MB)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| OASIS3_UDSc1_cognitive_assessments.csv | 1.7M | 7,925 | **107** | **Form C1/C2 — Neuropsychological battery**. UDS v2 (C1) → v3 (C2)에서 검사 일부 변경, 컬럼이 두 버전을 union으로 보유. 주요 검사: MMSE/MoCA, Logical Memory(LOGIMEM/MEMUNITS, lmdelay), Digit Span(DIGIF/DIGIB, digfor/digback), Trail Making A/B(TRAILA/tma/tmb), Category Fluency(ANIMALS/VEG), Boston Naming(bnt), WAIS Digit Symbol(digsym), Craft Story(craftvrs/craftdvr), Number Span, Benson Complex Figure(udsbentc/udsbentd/udsbenrs), Multilingual Naming Test(MINT). |
| OASIS3_UDSd1_diagnoses.csv | 1.9M | 8,500 | **149** | **Form D1 — Clinician diagnosis**. WHODIDDX(평가자), NORMCOG, DEMENTED, MCI 7 변종(MCIAMEM=amnestic single, MCIAPLUS=amnestic multi + LAN/ATT/EX/VIS subtypes, MCINON1/N2 = nonamnestic 1/2 domain + subtypes), IMPNOMCI(impaired but not MCI). 진단 etiology 플래그(각각 *IF=imaging이 진단에 contributory): PROBAD, POSSAD, DLB, VASC/VASCPS, ALCDEM, FTD, PPAPH, PSP, CORT, HUNT, PRION, MEDS, DEP, OTHPSY, DOWNS, PARK, STROKE, HYCEPH, BRNINJ, NEOP. UDS v3 추가: amndem, pca(PCA), ppasyn/ppasynt(PPA 변종), ftdsyn, lbdsyn, bio markers(amylpet, amylcsf, fdgad, hippatr, taupetad, csftau). |
| OASIS3_UDSd2_med_conditions.csv | 690K | 8,500 | 32 | **Form D2 — Clinician 판정 의학 상태**. 암(cancer), 당뇨(diabet), 심근경색(myoinf), 울혈성심부전(conghrt), 심방세동(afibrill), 고혈압(hypert), 협심증(angina), 고지혈증(hypchol), 비타민 B12 결핍(vb12def), 갑상선(thydis), 관절염(arth, artype, artupex/loex/spin/unkn), 요실금(urineinc/bowlinc), 수면 무호흡(sleepap), REM 수면행동장애(remdis), 과수면(hyposom), 혈관시술(angiocp/pci, pacemake, hvalve), antienc(자가면역 뇌염). |

---

## 5. PET & Imaging Metadata (3 files, ~3.8 MB)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| OASIS3_amyloid_centiloid.csv | 139K | 1,894 | 8 | **Amyloid PET Centiloid 정량**. PUP 파이프라인 출력. tracer ∈ {PIB:1178, AV45:715}. Centiloid_fBP_TOT_CORTMEAN(binding potential 기반, PIB만 정상값, AV45는 NaN), Centiloid_fSUVR_TOT_CORTMEAN(SUVR 기반, 두 트레이서 모두), `*_rsf_*`(regional spread function PVC 적용). 자세한 내용은 [`pet_imaging.md`](pet_imaging.md). |
| OASIS3_PET_json.csv | 3.4M | 2,158 | 51 | **PET BIDS JSON sidecar 평탄화**. 스캔별 1행. tracer ∈ {PIB:999, AV45:491, FDG:117, blank:550}. Manufacturer, ManufacturersModelName(예: BioGraph mMR PET), Tracer.Isotope(F18/C11), Tracer.InjectionType(Bolus), Recon.MethodName(OP-OSEM), InjectedRadioactivity, InjectionTime, ScanStartTime, FrameTimes(JSON-encoded list of frame schedules), AttenuationCorrection, ImageDecayCorrected, ConversionSoftware. |
| OASIS3_PET_datasetdescription.csv | 308K | 1,088 | 9 | **PET BIDS dataset_description.json**. OASIS_ID, session_id, Name(`OASIS3`), License(Refer to DUA), HowToAcknowledge, filename, **DatasetDOI(XNAT URL `https://central.xnat.org/data/archive/projects/OASIS3/...`)**, BidsVersion(1.0.1), accesssion(CENTRAL_E*/CENTRAL02_E* 식별자, 컬럼명에 오타 — `accesssion` 3개 's'). |

---

## 6. File Index — 영상 파일/세션 인벤토리 (2 files, ~5.9 MB)

| 파일명 | 크기 | 행 수 | 컬럼 | 설명 |
|--------|------|-------|------|------|
| oasis_file_list.csv | 5.6M | 42,907 | 5 | **NIfTI 파일 인덱스**. COHORT(`OASIS3`), SUB_ID(`OAS3xxxx`), VISIT(`d####`), SEQ(modality token), PATH(Windows mapping `Z:\1_combined\OASIS3\ORIG\NII\oasis_{batch}\...` → macOS는 `/Volumes/nfs_storage/OASIS3/ORIG/NII/...`로 변환). SEQ 분포: bold(5,114), dwi(12,915), T1w(4,116), T2w(4,051), fieldmap(3,819), T2star(2,350), FLAIR(1,381), GRE(1,326), asl(1,337), swi(1,229), minIP(1,231), PIB(1,248), angio(896), AV1451(763), AV45(780), pasl(223), FDG(127). |
| oasis3.csv | 236K | 8,627 | 10 | **Subject × visit modality inventory (collapsed)**. ID, refdate, FDG, FDG_diff, AV45, AV45_diff, MR, MR_diff, PIB, PIB_diff. `*_diff` = days_to_scan minus refdate (음수 = scan이 ref보다 이전). 임상-영상 visit 매칭에 사용. 자세한 내용은 [`file_index.md`](file_index.md). |

---

## 행 수 분포 패턴

UDS 폼들의 행 수가 다른 이유:

| 행 수 | 폼 | 의미 |
|-------|-----|------|
| 8,627 | b1, b4, oasis3.csv | 모든 임상 visit + 시행 횟수 가장 많은 폼 |
| 8,500 | a1, a2, a4(D/G), a5, b2, b5, b6, b7, b8, b9, d1, d2 | 표준 임상 visit 수 (대부분의 longitudinal 폼) |
| 7,925 | c1 | Cognitive battery — 일부 visit에서 누락 |
| 7,617 | a4D, a4G | 약물 정보 — 일부 visit 미수집 |
| 4,090 | a3, b3 | **Optional UDS module** — A3는 baseline 위주 (변경 시만 갱신), B3는 PD 의심 시만 |
| 1,894 | amyloid_centiloid | Amyloid PET 스캔 수 |
| 2,158 | PET_json | 모든 PET 스캔 (FDG 포함) |
| 1,379 | demographics | Subject 수 |
| 1,088 | PET_datasetdescription | PET 세션 수 |
| 42,907 | oasis_file_list | 모든 NIfTI 파일 |

> 1,378 OASIS3 참가자(LaMontagne 2019 발표 기준) vs demographics 1,379행 — 1행 차이는 헤더/추가 등록 가능성. 분석 시 `OASISID.nunique()`로 확인.

---

## 사이드 디렉터리 (이 카탈로그 외 OASIS3 데이터)

`/Volumes/nfs_storage/OASIS3/`:
- `ORIG/DEMO/` — **이 문서 대상** (24 CSV, 임상 메타데이터)
- `ORIG/NII/` — NIfTI 영상 (~42K 파일, `oasis_file_list.csv`로 인덱싱)
- `ORIG/DCM/` — 원본 DICOM
- `ORIG/JSON/` — BIDS JSON sidecar
- `PROC/` — 파생 데이터 (FreeSurfer 등)

---

## 참고 문서

| 문서 | 내용 |
|------|------|
| [`protocol.md`](protocol.md) | 연구 배경, OASIS 시리즈 비교, NACC UDS 버전, de-identification |
| [`session_label_reference.md`](session_label_reference.md) | 세션 라벨 grammar, FORM 토큰, days_to_visit 의미 |
| [`uds_forms.md`](uds_forms.md) | 17개 UDS 폼 컬럼 그룹별 요약 + 핵심 컬럼 정의 |
| [`demographics.md`](demographics.md) | OASIS3_demographics.csv 19컬럼 1:1 사전 |
| [`pet_imaging.md`](pet_imaging.md) | PET 3 파일 비교, 트레이서, Centiloid 방법론 |
| [`file_index.md`](file_index.md) | NIfTI 인벤토리 + 세션 매칭 |
| [`join_relationships.md`](join_relationships.md) | 키 계층, 조인 패턴, 카디널리티 |

## 외부 참조

- **OASIS3 paper**: LaMontagne et al. *OASIS-3: Longitudinal Neuroimaging, Clinical, and Cognitive Dataset for Normal Aging and Alzheimer Disease*. medRxiv 2019. [doi:10.1101/2019.12.13.19014902](https://doi.org/10.1101/2019.12.13.19014902)
- **OASIS 공식 사이트**: [https://sites.wustl.edu/oasisbrains/home/oasis-3/](https://sites.wustl.edu/oasisbrains/home/oasis-3/)
- **NACC UDS-3 Researcher's Data Dictionary**: [https://files.alz.washington.edu/documentation/uds3-rdd.pdf](https://files.alz.washington.edu/documentation/uds3-rdd.pdf)
- **NACC UDS-3 forms 페이지**: [https://naccdata.org/data-collection/forms-documentation/uds-3](https://naccdata.org/data-collection/forms-documentation/uds-3)
