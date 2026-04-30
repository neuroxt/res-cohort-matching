# 영상 가용성 인벤토리

`/Volumes/nfs_storage/KBASE/ORIG/Demo/1_KBASE1_nifti_0,2,4.xlsx` (130 KB).

파일명의 `0,2,4` = imaging visit 번호 (V0/V2/V4). V1/V3은 임상 전용이라 이 파일에 행 없음.

---

## 시트 구성

| 시트 | 데이터 행수 | 컬럼수 | 용도 |
|------|------------|--------|------|
| `V0` | 644 | 16 | baseline imaging visit |
| `V2` | 408 | 16 | 2년 추적 imaging visit |
| `V4` | 240 | 16 | 4년 추적 imaging visit |
| `protocol` | 13 | 11 | 모달리티 short-code ↔ scanner protocol string |
| `NOTE` | 9 | 0 | 빈 placeholder |

---

## V0/V2/V4 시트의 16 컬럼

| 순서 | 컬럼 | 타입 | 의미 |
|------|------|------|------|
| 1 | `GROUP` | str | 임상 그룹 (NC_고령 / NC_청장년 / MCI / AD / 기타) |
| 2 | `ID` | str | Subject ID (`SU####` 또는 `BR####`) |
| 3 | `K_visit` | int | 현재 visit (V0=0, V2=2, V4=4) |
| 4 | `PiB-PET` | datetime/str | PiB 촬영일 |
| 5 | `FDG-PET` | datetime/str | FDG 촬영일 |
| 6 | `TAU-PET` | datetime/str/`N` | Tau 촬영일 또는 `N` (촬영 안 됨) |
| 7~15 | 9 모달리티 가용성 | str | `BR####`/`SU####`/`O`/`X`/blank |
| 16 | `비고` | str | 자유 텍스트 메모 (예: `fs error`) |

**9 모달리티 컬럼 순서**: `PIB | T1 | rfMRI | DTI | ASL | FDG | FLAIR | SWI | TAU`

---

## 모달리티 가용성 인코딩

각 모달리티 셀의 값은 다음 중 하나:

| 값 | 의미 |
|----|------|
| `BR####` 또는 `SU####` | **가용 + 파일 식별자**. 셀 값 자체가 영상 파일 검색 키 (즉, NII 디렉토리에서 `{ID}_{modality}_V{visit}.json`/`.nii.gz` 검색) |
| `O` | 가용 (older notation, 주로 V0의 PIB 컬럼에 등장) |
| `X` | 명시적 미촬영 |
| 빈 값 (NaN/`''`) | 프로토콜 미해당 또는 정보 없음 |

**가용성 판정**: `cell_value not in (None, '', 'X')` → 가용.

---

## V별 모달리티 가용 분포 (실측)

### V0 (baseline, 644 rows)

| 모달리티 | avail | X | blank |
|---------|-------|---|-------|
| PIB | 643 | 1 | 0 |
| T1 | 644 | 0 | 0 |
| rfMRI | 644 | 0 | 0 |
| DTI | 642 | 2 | 0 |
| ASL | 643 | 1 | 0 |
| FDG | 640 | 4 | 0 |
| FLAIR | 639 | 5 | 0 |
| SWI | 591 | 53 | 0 |
| TAU | 22 | 622 | 0 |

→ baseline은 PIB/T1/rfMRI/DTI/ASL/FDG/FLAIR ~99% 커버. SWI 91%. **TAU는 V0 시점엔 도입 안 됨** (22 scan만).

### V2 (2년, 408 rows)

| 모달리티 | avail | X | blank |
|---------|-------|---|-------|
| PIB | 383 | 25 | 0 |
| T1 | 385 | 23 | 0 |
| rfMRI | 379 | 29 | 0 |
| DTI | 382 | 26 | 0 |
| ASL | 379 | 29 | 0 |
| FDG | 406 | 2 | 0 |
| FLAIR | 406 | 2 | 0 |
| SWI | 401 | 7 | 0 |
| TAU | 162 | 246 | 0 |

→ V2부터 TAU PET 본격 도입 (162 scan, 40%).

### V4 (4년, 240 rows)

| 모달리티 | avail | X | blank |
|---------|-------|---|-------|
| PIB | 214 | 26 | 0 |
| T1 | 214 | 26 | 0 |
| rfMRI | 214 | 26 | 0 |
| DTI | 214 | 26 | 0 |
| ASL | 212 | 28 | 0 |
| FDG | 215 | 25 | 0 |
| FLAIR | 215 | 25 | 0 |
| SWI | 215 | 25 | 0 |
| TAU | 91 | 149 | 0 |

→ V4 모달리티별 가용률 ~89%. TAU 38%.

**TAU 누적 (V0+V2+V4) = 22 + 162 + 91 = 275 scan**. JSON_Files/TAU 디렉토리의 파일 수와 일치.

---

## GROUP 분포 per visit

| GROUP | V0 | V2 | V4 |
|-------|----|----|----|
| `NC_고령` | 306 | 214 | 155 |
| `MCI` | 164 | 109 | 56 |
| `AD` | 100 | 57 | 21 |
| `NC_청장년` | 74 | 25 | 3 |
| `_고령` (typo) | 0 | 1 | 0 |
| `고령` (typo) | 0 | 1 | 0 |
| `''` (empty) | 0 | 1 | 0 |
| `PRD` | 0 | 0 | 2 |
| `QD` | 0 | 0 | 1 |
| `CIND` | 0 | 0 | 1 |
| `QD_naMCI` | 0 | 0 | 1 |

> **GROUP typo**: V2에서 `_고령`, `고령`, `''` 각 1건. `NC_고령` 의도였던 것으로 보임. V4의 `PRD`/`QD`/`CIND`/`QD_naMCI`는 후기 도입된 atypical 진단 라벨 (5건 합계).
>
> **clean-up 권장**: `df['GROUP'] = df['GROUP'].replace({'_고령': 'NC_고령', '고령': 'NC_고령'})` + 빈 행은 별도 처리.

---

## `protocol` 시트 — scanner protocol string 매핑

13 행 × 11 컬럼. 각 컬럼이 한 모달리티의 *full DICOM SeriesDescription* 같은 문자열을 짧은 코드로 묶음.

| 컬럼 헤더 (row 1, full string) | row 2 (short code) |
|---|---|
| `HEAD C-11 PIB PET BRAIN AC image` | `pib` |
| `HEAD TFL3D SAG 208 SLAB` | `t1` |
| `HEAD rfMRI 116 phase bold moco` | `rfMRI` |
| `TRUE AXL dti 67d TDI B1000 SCH` | `dti` |
| `Head ep2d tra pasl` | `asl` |
| (빈 컬럼) | (빈) |
| `HEAD PET Brain (f-18 FDG) AC image` | `fdg` |
| `Head T2 spc fl sag` | `flair` |
| `SWI image` | `swi` |
| (빈 컬럼) | (빈) |
| `T37 F18 Brain PET` | `TAU` |

→ 원본 DICOM의 `SeriesDescription` 필드와 매칭하여 모달리티 분류할 때 사용. 다른 row는 alternative protocol string (스캐너 변경 시 다른 description으로 잡힐 수 있음). 실측 sample 필요 시 `JSON_Files/{modality}/*.json`의 `SeriesDescription`/`ProtocolName` 확인.

---

## NIfTI / JSON sidecar 매핑

영상 파일은 별도 디렉토리:

- **NII**: `/Volumes/nfs_storage/KBASE/ORIG/NII/` (구조 상세 미조사)
- **JSON sidecar (BIDS 메타)**: `/Volumes/nfs_storage/KBASE/ORIG/Demo/JSON_Files/<modality>/<ID>_<modality>_V<visit>.json`

JSON 파일명 패턴: `{SU|BR}{####}_{T1|PIB|rfMRI|DTI|FDG|T2_FLAIR|TAU}_V{0|2|4}.json`. 예: `SU0055_T1_V0.json`.

JSON 파일 수 (모달리티별):

| 모달리티 | JSON 파일 수 |
|---------|-------------|
| DTI | 1,193 |
| FDG | 1,220 |
| PIB | 1,197 |
| rfMRI | 1,195 |
| T1 | 1,198 |
| T2_FLAIR | 1,219 |
| **TAU** | **275** |
| **합** | **7,497** |

> **`T2_FLAIR` vs `FLAIR`**: JSON 디렉토리는 `T2_FLAIR`라는 이름을 쓰지만 inventory 시트의 컬럼은 `FLAIR`. 같은 모달리티 (T2 FLAIR sequence). 매칭 코드 작성 시 양쪽 알리아스 처리.

JSON 표준 키 (T1 sample 기준): `AcquisitionTime, EchoTime, RepetitionTime, FlipAngle, MagneticFieldStrength, Manufacturer, ManufacturersModelName, InstitutionName, ProtocolName, PulseSequenceDetails, SliceThickness, ImageType, ...` — dcm2niix 표준 출력.

---

## 알려진 limitations

1. **TAU PET은 V0에 22 scan만** — KBASE 도입 시점이 V2/V4임. V0 시점의 tau 분석은 불가능 (sample size 부족).
2. **GROUP typo** (`_고령`, `고령`, `''`) — V2/master에 3건. clean-up script로 표준화 후 사용.
3. **`O` legacy notation** vs **`{ID}` 신규 notation** — 두 가지가 mixed. 가용성 판정은 `not in (None, '', 'X')` 패턴이면 안전.
4. **imaging visit과 임상 visit 정렬 불일치 가능** — V0 PiB 촬영일과 V0 Diag_Demo 평가일이 며칠~몇 주 차이날 수 있음. 정확한 timing이 중요한 분석은 `PiB-PET`/`FDG-PET`/`TAU-PET` 컬럼의 datetime 사용.
5. **NII 디렉토리 구조 미조사** — 이 문서 작성 시점에 `/Volumes/nfs_storage/KBASE/ORIG/NII/` 내부 layout은 inspect하지 않음. 분석 시작 전 직접 확인 필요.
