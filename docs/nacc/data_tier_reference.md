# NACC 동의 Tier 참조: Commercial vs Investigator (Non_Commercial)

NACC는 같은 임상/영상/유전 데이터를 **두 가지 동의 tier** 로 배포한다. 어느 쪽을 써야 하는지를 결정하는 한 페이지짜리 가이드.

---

## 1. 두 tier의 의미

| Tier | NFS 폴더 | 동의 범위 | 사용 권장 |
|------|---------|----------|----------|
| **Commercial** | `DEMO/Commercial_Data/commercial_*.csv` | Subject가 **산업 / 상업 사용에도 동의** (예: 제약 회사, 의료기기 업체와의 협업) | 산업 협업, IND/IDE 제출, 상용 알고리즘 학습 등 명시적 commercial 목적 |
| **Non_Commercial = Investigator** | `DEMO/Non_Commercial_Data/investigator_*.csv` | **학술/연구 전용** 동의 (broader 모집단, default consent) | **학술 연구 default — 본 NeuroXT 분석은 Investigator 사용** |

> **핵심**: 두 tier는 *컬럼 스키마가 100% 동일*하다. 차이는 **포함된 subject/visit 의 동의 범위**뿐이다.

---

## 2. 행 수 (v71 freeze, 2026-04 기준)

| 파일 페어 | Commercial 행 | Investigator 행 | 차이 (학술 추가 인원) |
|----------|----------|--------------|----------|
| `*_ftldlbd_nacc71.csv` | 179,753 | **205,909** | +26,156 (visit) |
| `*_mri_nacc71.csv` | 10,520 | **12,043** | +1,523 |
| `*_fcsf_nacc71.csv` | 2,770 | **3,052** | +282 |
| `*_scan_mriqc_nacc71.csv` | 22,855 | 22,855 | 0 (동일) |
| `*_scan_mrisbm_nacc71.csv` | 5,330 | 5,330 | 0 |
| `*_scan_amyloidpetgaain_nacc71.csv` | (≈2,808) | 2,808 | 0 (추정) |
| `*_scan_amyloidpetnpdka_nacc71.csv` | (≈2,808) | 2,808 | 0 |
| `*_scan_taupetnpdka_nacc71.csv` | (≈1,815) | 1,815 | 0 |
| `*_scan_fdgpetnpdka_nacc71.csv` | (≈485) | 485 | 0 |
| `*_scan_petqc_nacc71.csv` | (≈5,103) | 5,103 | 0 |

**관찰**:
- **Clinical UDS (`ftldlbd`, `mri`, `fcsf`)**: Investigator > Commercial — 학술 동의가 더 넓다.
- **SCAN imaging quantification**: 두 tier가 **거의 동일** — SCAN 참여자 대부분이 Commercial 동의도 같이 한 것으로 보임.

> 실제 commercial SCAN 행 수가 살짝 적을 수 있으므로 분석 시 직접 `wc -l` 로 검증 권장.

---

## 3. 어느 쪽을 써야 하는가

### 학술 연구 (논문, 학회 발표, 그랜트)
**→ Investigator (Non_Commercial)** 를 default. 가장 넓은 모집단을 보장하며 학술 사용에 명시적으로 허용된 데이터.

### 산업 / 상업 협업
**→ Commercial**. 협업 계약 / IND / 상용 SaaS 학습 등 commercial 사용 명시 시 반드시 Commercial tier를 사용. Investigator tier 데이터를 commercial 목적으로 쓰면 DUA 위반.

### 두 tier를 같이 쓰고 싶다 (예: 학술 분석 후 follow-up 산업 협업)
**→ DUA 검토 필요**. NACC DUA에 두 가지 사용을 모두 명시해야 한다. 단순히 두 파일을 union 한다고 commercial 권리가 자동으로 부여되지 않는다.

---

## 4. 코드에서 tier 선택하는 패턴

```python
import os
import pandas as pd

NACC_ROOT = "/Volumes/nfs_storage/NACC_NEW/ORIG/DEMO"

def load_nacc(filename: str, tier: str = "investigator") -> pd.DataFrame:
    """NACC tier-aware 파일 로더.
    
    tier='investigator' (default, 학술용) 또는 'commercial'.
    """
    if tier == "investigator":
        prefix = "Non_Commercial_Data/investigator_"
    elif tier == "commercial":
        prefix = "Commercial_Data/commercial_"
    else:
        raise ValueError(f"Unknown tier: {tier}")
    
    path = os.path.join(NACC_ROOT, prefix + filename)
    return pd.read_csv(path)

# 사용 예
clinical = load_nacc("ftldlbd_nacc71.csv")           # default investigator
amyloid_pet = load_nacc("scan_pet_nacc71/scan_amyloidpetnpdka_nacc71.csv")
csf = load_nacc("fcsf_nacc71.csv")
```

---

## 5. ADSP-PHC tier 분리

ADSP-PHC December 2024 release도 같은 tier 분리:

| Tier | 경로 |
|------|------|
| Commercial | `DEMO/Commercial_Data/ADSP-PHC-122024-commercial/ADSP-PHC-122024-commercial/` |
| Investigator | `DEMO/Non_Commercial_Data/ADSP-PHC-122024-investigator/ADSP-PHC-122024-investigator/` |

자세한 ADSP-PHC 8 도메인 구조: [`data_catalog.md` §2.5](data_catalog.md) 참조.

> ADSP-PHC 폴더는 **double-nested** (`ADSP-PHC-122024-investigator/ADSP-PHC-122024-investigator/...`). NACC release tarball 구조가 그대로 풀려있는 흔적.

---

## 6. NeuroXT-built `merged.csv` 의 tier

`DEMO/merged.csv` (205,909 × 390) 는 **Investigator (Non_Commercial) tier 데이터로 빌드됨**. 행 수가 `investigator_ftldlbd_nacc71.csv` 와 일치 (205,909) 하는 것으로 확인. 따라서 `merged.csv` 는 **학술 연구용** 이며 commercial 협업에는 사용 불가.

> Commercial 협업이 필요하면 `commercial_ftldlbd_nacc71.csv` (179,753) 부터 새 working file 빌드 필요.

---

## 7. tier 변경 시 데이터 차이 분석 패턴

```python
import pandas as pd

inv = pd.read_csv("Non_Commercial_Data/investigator_ftldlbd_nacc71.csv",
                  usecols=["NACCID", "NACCVNUM"])
com = pd.read_csv("Commercial_Data/commercial_ftldlbd_nacc71.csv",
                  usecols=["NACCID", "NACCVNUM"])

inv_keys = set(zip(inv.NACCID, inv.NACCVNUM))
com_keys = set(zip(com.NACCID, com.NACCVNUM))

print("Investigator only:", len(inv_keys - com_keys))   # 학술 동의에만 포함
print("Commercial only:",   len(com_keys - inv_keys))   # 0이거나 매우 적음 expected
print("Both:",              len(inv_keys & com_keys))   # 산업+학술 동의 동시
```

`Commercial only` 는 0이거나 매우 적을 것 expected (commercial 동의는 항상 학술 동의를 포함하는 superset 구조).

---

## Known limitations & quirks

1. **컬럼 스키마는 100% 동일.** Tier는 동의 범위만 다르다. 따라서 분석 코드는 tier-agnostic하게 작성 가능 (위 §4 패턴).
2. **`merged.csv` 는 Investigator tier 한정 working file.** Commercial 협업에 사용 불가.
3. **SCAN 파일은 두 tier 행 수가 거의 같음.** SCAN 참여자 대부분이 commercial 동의도 한 듯. 학술 분석에서 tier별 차이가 거의 없음.
4. **`NACCID` 자체는 두 tier 사이에서 이식 가능.** 같은 NACCID가 두 tier 모두에 존재 가능 (commercial 동의 = investigator superset). 분석 시 동일 NACCID를 다른 tier에서 cross-link 가능 (단, 사용 권한은 분석 목적에 맞춰).
5. **DUA 위반 위험**: Investigator tier 데이터를 산업 협업 / 상용 알고리즘 학습에 쓰면 DUA 위반. 협업 시작 전 tier 확인 필수.

> 검증일 2026-05-01 (freeze v71)
