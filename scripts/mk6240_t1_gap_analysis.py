"""
MK6240 ↔ T1 matching gap analysis for GitHub Issue #5.

Generates:
  - output/mk6240_t1_gap/breakdown.png   — waterfall breakdown (108 → 72 matched)
  - output/mk6240_t1_gap/heatmap.png     — VISCODE mismatch cross-tab heatmap
  - output/mk6240_t1_gap/summary.md      — markdown summary tables
"""

from __future__ import annotations

import pathlib
import textwrap

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# Use AppleGothic on macOS for Korean glyphs; fall back to sans-serif
for _font in ("AppleGothic", "NanumGothic", "Malgun Gothic"):
    if _font in {f.name for f in matplotlib.font_manager.fontManager.ttflist}:
        matplotlib.rcParams["font.family"] = _font
        break
matplotlib.rcParams["axes.unicode_minus"] = False

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "output" / "ADNI_matching_v4"
OUT = ROOT / "output" / "mk6240_t1_gap"
OUT.mkdir(parents=True, exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────────

mk = pd.read_csv(DATA / "MK6240_6MM_unique.csv")
t1 = pd.read_csv(DATA / "T1_unique.csv")

t1_ptids = set(t1["PTID"])
t1_keys = set(zip(t1["PTID"], t1["VISCODE_FIX"]))
t1_viscode_map = t1.groupby("PTID")["VISCODE_FIX"].apply(sorted).apply(list).to_dict()

# ── Categorize each MK6240 row ──────────────────────────────────────────────

def categorize(row):
    key = (row["PTID"], row["VISCODE_FIX"])
    if key in t1_keys:
        return "matched"
    if row["PTID"] not in t1_ptids:
        return "no_ptid"
    return "viscode_mismatch"

mk["_category"] = mk.apply(categorize, axis=1)

n_matched = (mk["_category"] == "matched").sum()
n_no_ptid = (mk["_category"] == "no_ptid").sum()
n_viscode = (mk["_category"] == "viscode_mismatch").sum()
n_total = len(mk)

assert n_matched + n_no_ptid + n_viscode == n_total, "Count mismatch!"
print(f"Total: {n_total}  Matched: {n_matched}  No-PTID: {n_no_ptid}  VISCODE mismatch: {n_viscode}")

# ── 1. Breakdown chart ──────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 5))

categories = ["MK6240\n전체", "T1 매칭\n성공", "PTID\n미존재", "VISCODE\n불일치"]
values = [n_total, n_matched, n_no_ptid, n_viscode]
colors = ["#4A90D9", "#27AE60", "#E74C3C", "#F39C12"]

bars = ax.bar(categories, values, color=colors, width=0.55, edgecolor="white", linewidth=1.5)

for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2,
            str(val), ha="center", va="bottom", fontsize=16, fontweight="bold")

# Annotating flow arrows
ax.annotate("", xy=(1, n_matched + 3), xytext=(0, n_total - 3),
            arrowprops=dict(arrowstyle="->", color="#27AE60", lw=2))
ax.annotate("", xy=(2, n_no_ptid + 3), xytext=(0, n_total - 8),
            arrowprops=dict(arrowstyle="->", color="#E74C3C", lw=1.5, ls="--"))
ax.annotate("", xy=(3, n_viscode + 3), xytext=(0, n_total - 13),
            arrowprops=dict(arrowstyle="->", color="#F39C12", lw=1.5, ls="--"))

# Percentage labels
ax.text(1, n_matched / 2, f"{n_matched/n_total:.1%}", ha="center", va="center",
        fontsize=11, color="white", fontweight="bold")
ax.text(2, max(n_no_ptid / 2, 2), f"{n_no_ptid/n_total:.1%}", ha="center", va="center",
        fontsize=10, color="white", fontweight="bold")
ax.text(3, n_viscode / 2, f"{n_viscode/n_total:.1%}", ha="center", va="center",
        fontsize=11, color="white", fontweight="bold")

ax.set_ylabel("건수", fontsize=12)
ax.set_title("MK6240 ↔ T1 매칭 갭 분석 (108건)", fontsize=14, fontweight="bold", pad=15)
ax.set_ylim(0, n_total + 12)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="x", labelsize=11)

fig.tight_layout()
fig.savefig(OUT / "breakdown.png", dpi=150, bbox_inches="tight")
print(f"Saved: {OUT / 'breakdown.png'}")
plt.close(fig)

# ── 2. VISCODE mismatch heatmap ─────────────────────────────────────────────

mismatch = mk[mk["_category"] == "viscode_mismatch"].copy()

# For each mismatch, find the closest T1 VISCODE
def month_num(v: str) -> int:
    return int(v.replace("m", ""))

def closest_t1_viscode(row):
    viscodes = t1_viscode_map.get(row["PTID"], [])
    if not viscodes:
        return "N/A"
    mk_m = month_num(row["VISCODE_FIX"])
    return min(viscodes, key=lambda v: abs(month_num(v) - mk_m))

mismatch["T1_VISCODE_CLOSEST"] = mismatch.apply(closest_t1_viscode, axis=1)

ct = pd.crosstab(
    mismatch["VISCODE_FIX"].rename("MK6240 VISCODE"),
    mismatch["T1_VISCODE_CLOSEST"].rename("T1 VISCODE (closest)"),
)

fig, ax = plt.subplots(figsize=(6, 4))
im = ax.imshow(ct.values, cmap="YlOrRd", aspect="auto")

ax.set_xticks(range(len(ct.columns)))
ax.set_xticklabels(ct.columns, fontsize=12)
ax.set_yticks(range(len(ct.index)))
ax.set_yticklabels(ct.index, fontsize=12)
ax.set_xlabel("T1 VISCODE (closest)", fontsize=12, labelpad=8)
ax.set_ylabel("MK6240 VISCODE", fontsize=12, labelpad=8)
ax.set_title("VISCODE 불일치 패턴 (30건)", fontsize=13, fontweight="bold", pad=12)

# Annotate cells
for i in range(len(ct.index)):
    for j in range(len(ct.columns)):
        val = ct.values[i, j]
        color = "white" if val > ct.values.max() * 0.6 else "black"
        ax.text(j, i, str(val), ha="center", va="center",
                fontsize=16, fontweight="bold", color=color)

# Dominant pattern annotation
ax.annotate(
    "90% — m003↔m000\n(ADNI4 프로토콜 차이)",
    xy=(0, 0),
    xytext=(1.8, -0.6),
    fontsize=9,
    ha="center",
    arrowprops=dict(arrowstyle="->", color="#333", lw=1.2),
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF3CD", edgecolor="#F39C12"),
)

fig.colorbar(im, ax=ax, label="건수", shrink=0.8)
fig.tight_layout()
fig.savefig(OUT / "heatmap.png", dpi=150, bbox_inches="tight")
print(f"Saved: {OUT / 'heatmap.png'}")
plt.close(fig)

# ── 3. Markdown summary ─────────────────────────────────────────────────────

missing_ptid_df = mk[mk["_category"] == "no_ptid"][["PTID", "VISCODE_FIX"]].reset_index(drop=True)
mismatch_detail = mismatch[["PTID", "VISCODE_FIX"]].copy()
mismatch_detail["T1_VISCODES"] = mismatch_detail["PTID"].map(
    lambda p: ", ".join(t1_viscode_map.get(p, []))
)
mismatch_detail = mismatch_detail.rename(columns={
    "VISCODE_FIX": "MK6240_VISCODE",
}).reset_index(drop=True)

summary = textwrap.dedent(f"""\
### 5. T1+MK6240 매칭 감소 분석 (108 → 72)

#### 요약
108 MK6240 중 72건만 T1과 (PTID, VISCODE_FIX) 일치 — **36건 불일치**.

| 카테고리 | 건수 | 비율 | 설명 |
|---|---|---|---|
| T1 매칭 성공 | {n_matched} | {n_matched/n_total:.1%} | 동일 (PTID, VISCODE_FIX) |
| PTID 미존재 | {n_no_ptid} | {n_no_ptid/n_total:.1%} | T1 데이터 자체 없음 (ADNI4 신규) |
| VISCODE 불일치 | {n_viscode} | {n_viscode/n_total:.1%} | 같은 PTID, 다른 방문 시점 |
| **합계** | **{n_total}** | **100%** | |

#### VISCODE 불일치 패턴 ({n_viscode}건)

![VISCODE 불일치 heatmap](output/mk6240_t1_gap/heatmap.png)

![매칭 갭 breakdown](output/mk6240_t1_gap/breakdown.png)

- **27건 (90%)**: MK6240=m003, T1=m000 — ADNI4에서 MK6240 PET은 3개월차, T1 MRI는 screening
- **2건**: MK6240=m006, T1=m000
- **1건**: MK6240=m000, T1=m012

#### 근본 원인
- ADNI4 프로토콜: MK6240 PET → m003 방문, T1 MRI → m000 (screening)
- VISCODE_FIX = round((AQUDATE − EXAMDATE_bl) / 30.44) → 촬영일 차이가 VISCODE 차이로 이어짐
- **코드 이슈 아님** — 물리적 촬영 스케줄 차이

#### PTID 미존재 목록 ({n_no_ptid}건)

| PTID | MK6240_VISCODE |
|---|---|
""")

for _, row in missing_ptid_df.iterrows():
    summary += f"| {row['PTID']} | {row['VISCODE_FIX']} |\n"

summary += f"\n#### VISCODE 불일치 상세 ({n_viscode}건)\n\n"
summary += "| PTID | MK6240_VISCODE | T1_VISCODES |\n"
summary += "|---|---|---|\n"
for _, row in mismatch_detail.iterrows():
    summary += f"| {row['PTID']} | {row['MK6240_VISCODE']} | {row['T1_VISCODES']} |\n"

(OUT / "summary.md").write_text(summary, encoding="utf-8")
print(f"Saved: {OUT / 'summary.md'}")
print("\nDone.")
