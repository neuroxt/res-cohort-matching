#!/usr/bin/env python3
"""
a4_screening_handoff.py — A4/LEARN screening 데이터 인계용 CSV 추출

출력 3개:
  1. screening_biomarkers.csv — BID별 TAU(272), Centiloid, AMY_SUVR_CER, VA(95)
  2. mmse_longitudinal.csv   — 전체 방문 MMSE
  3. cdr_longitudinal.csv    — 전체 방문 CDR
"""

import argparse
import logging
from pathlib import Path

import pandas as pd

LOG_FMT = "%(asctime)s | %(levelname)-5s | %(message)s"
logging.basicConfig(format=LOG_FMT, level=logging.INFO)
log = logging.getLogger(__name__)

DEFAULT_NFS = "/Volumes/nfs_storage-1/1_combined/A4"
DEFAULT_OUT = "output/a4/handoff"

# Cohort filter: amyloidNE (screen-fail) 제외
COHORT_KEEP = {"amyloidE", "LEARN amyloidNE"}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _viscode_to_session_code(viscode) -> str:
    """VISCODE(int) → SESSION_CODE (3-digit zero-pad, 701+ as-is)."""
    try:
        v = int(viscode)
    except (ValueError, TypeError):
        return ""
    return str(v).zfill(3) if v < 100 else str(v)


def _load_cohort_map(nfs: Path) -> pd.DataFrame:
    """A4_demography.csv → BID-unique COHORT mapping (amyloidE / LEARN amyloidNE only)."""
    path = nfs / "ORIG/metadata/A4_demography.csv"
    df = pd.read_csv(path, usecols=["Subject ID", "Research Group"])
    df = df.rename(columns={"Subject ID": "BID", "Research Group": "COHORT"})
    df = df[df["COHORT"].isin(COHORT_KEEP)]
    df = df.drop_duplicates(subset="BID").reset_index(drop=True)
    log.info("Cohort map: %d BIDs (%s)", len(df), df["COHORT"].value_counts().to_dict())
    return df


# ---------------------------------------------------------------------------
# screening_biomarkers builders
# ---------------------------------------------------------------------------

def _build_tau(nfs: Path, valid_bids: set) -> pd.DataFrame:
    """TAUSUVR → TAU_* prefix, BID 필터."""
    path = nfs / "ORIG/metadata/A4 Imaging data and docs/TAUSUVR_11Aug2025.csv"
    df = pd.read_csv(path)
    df = df.rename(columns={"ID": "BID"})
    df = df.drop(columns=["update_stamp"], errors="ignore")
    # TAU_ prefix
    roi_cols = [c for c in df.columns if c != "BID"]
    rename = {c: f"TAU_{c}" for c in roi_cols}
    df = df.rename(columns=rename)
    df = df[df["BID"].isin(valid_bids)].reset_index(drop=True)
    log.info("TAU: %d BIDs, %d ROI cols", len(df), len(roi_cols))
    return df


def _build_centiloid(nfs: Path, valid_bids: set) -> pd.DataFrame:
    """A4_PETSUVR → Composite_Summary → AMY_CENTILOID + AMY_SUVR_CER."""
    path = nfs / "ORIG/metadata/A4 Imaging data and docs/A4_PETSUVR_PRV2_11Aug2025.csv"
    df = pd.read_csv(path)
    df = df[df["brain_region"] == "Composite_Summary"].copy()
    df = df[["BID", "centiloid", "suvr_cer"]].rename(columns={
        "centiloid": "AMY_CENTILOID",
        "suvr_cer": "AMY_SUVR_CER",
    })
    # BID당 중복 시 첫 번째 유지
    df = df.drop_duplicates(subset="BID").reset_index(drop=True)
    df = df[df["BID"].isin(valid_bids)].reset_index(drop=True)
    log.info("Centiloid: %d BIDs", len(df))
    return df


def _build_va(nfs: Path, valid_bids: set) -> pd.DataFrame:
    """va_all.csv → A4 screening (004) + LEARN baseline (006) → VA_* prefix."""
    path = nfs / "PROC/T1/VA/va_all.csv"
    df = pd.read_csv(path)
    # parse SUBJECT: A4_MR_T1_{BID}_{VISCODE}
    parts = df["SUBJECT"].str.split("_", expand=True)
    df["BID"] = parts[3]
    df["VISCODE"] = parts[4]
    # A4 screening=004, LEARN baseline=006
    df = df[df["VISCODE"].isin(["004", "006"])].copy()
    df = df.drop(columns=["SUBJECT", "VISCODE"])
    # rename VA/2 → VA_2
    roi_cols = [c for c in df.columns if c.startswith("VA/")]
    rename = {c: c.replace("/", "_") for c in roi_cols}
    df = df.rename(columns=rename)
    # BID 중복 시 첫 번째 유지
    df = df.drop_duplicates(subset="BID").reset_index(drop=True)
    df = df[df["BID"].isin(valid_bids)].reset_index(drop=True)
    log.info("VA: %d BIDs, %d ROI cols", len(df), len(roi_cols))
    return df


def build_screening_biomarkers(nfs: Path, cohort: pd.DataFrame) -> pd.DataFrame:
    """BID + COHORT + TAU + Centiloid + VA → screening_biomarkers.csv."""
    valid_bids = set(cohort["BID"])
    tau = _build_tau(nfs, valid_bids)
    cen = _build_centiloid(nfs, valid_bids)
    va = _build_va(nfs, valid_bids)

    out = cohort.copy()
    for part in [tau, cen, va]:
        out = out.merge(part, on="BID", how="left")

    out = out.sort_values("BID").reset_index(drop=True)
    log.info("screening_biomarkers: %d rows × %d cols", *out.shape)
    return out


# ---------------------------------------------------------------------------
# longitudinal builders
# ---------------------------------------------------------------------------

def build_mmse(nfs: Path, cohort: pd.DataFrame) -> pd.DataFrame:
    """mmse.csv → BID, COHORT, VISCODE, SESSION_CODE, MMSCORE."""
    path = nfs / "ORIG/DEMO/Clinical/Raw Data/mmse.csv"
    df = pd.read_csv(path, usecols=["BID", "VISCODE", "MMSCORE"])
    df = df[df["BID"].isin(set(cohort["BID"]))].copy()
    df = df.merge(cohort[["BID", "COHORT"]], on="BID", how="left")
    df["SESSION_CODE"] = df["VISCODE"].apply(_viscode_to_session_code)
    df = df[["BID", "COHORT", "VISCODE", "SESSION_CODE", "MMSCORE"]]
    df = df.sort_values(["BID", "VISCODE"]).reset_index(drop=True)
    log.info("MMSE longitudinal: %d rows", len(df))
    return df


def build_cdr(nfs: Path, cohort: pd.DataFrame) -> pd.DataFrame:
    """cdr.csv → BID, COHORT, VISCODE, SESSION_CODE, CDGLOBAL, CDSOB."""
    path = nfs / "ORIG/DEMO/Clinical/Raw Data/cdr.csv"
    df = pd.read_csv(path, usecols=["BID", "VISCODE", "CDGLOBAL", "CDSOB"])
    df = df[df["BID"].isin(set(cohort["BID"]))].copy()
    df = df.merge(cohort[["BID", "COHORT"]], on="BID", how="left")
    df["SESSION_CODE"] = df["VISCODE"].apply(_viscode_to_session_code)
    df = df[["BID", "COHORT", "VISCODE", "SESSION_CODE", "CDGLOBAL", "CDSOB"]]
    df = df.sort_values(["BID", "VISCODE"]).reset_index(drop=True)
    log.info("CDR longitudinal: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="A4/LEARN screening data handoff")
    ap.add_argument("--nfs-root", default=DEFAULT_NFS, help="NFS A4 root")
    ap.add_argument("--output-dir", default=DEFAULT_OUT, help="Output directory")
    args = ap.parse_args()

    nfs = Path(args.nfs_root)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cohort = _load_cohort_map(nfs)

    # 1. screening biomarkers
    bio = build_screening_biomarkers(nfs, cohort)
    bio.to_csv(out_dir / "screening_biomarkers.csv", index=False)

    # 2. MMSE longitudinal
    mmse = build_mmse(nfs, cohort)
    mmse.to_csv(out_dir / "mmse_longitudinal.csv", index=False)

    # 3. CDR longitudinal
    cdr = build_cdr(nfs, cohort)
    cdr.to_csv(out_dir / "cdr_longitudinal.csv", index=False)

    log.info("Done — outputs in %s", out_dir)


if __name__ == "__main__":
    main()
