"""
AV1451 ↔ T1 matching gap analysis for GitHub Issue #4.

Generates:
  - output/av1451_t1_gap/breakdown.png   — waterfall breakdown
  - output/av1451_t1_gap/heatmap.png     — VISCODE mismatch cross-tab heatmap
  - output/av1451_t1_gap/summary.md      — markdown summary tables
"""

from __future__ import annotations

import pathlib
import textwrap

import matplotlib
import matplotlib.pyplot as plt
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
OUT = ROOT / "output" / "av1451_t1_gap"
OUT.mkdir(parents=True, exist_ok=True)

# ── Load data ────────────────────────────────────────────────────────────────

av = pd.read_csv(DATA / "AV1451_6MM_unique.csv", low_memory=False)
t1 = pd.read_csv(DATA / "T1_unique.csv", low_memory=False)

t1_ptids = set(t1["PTID"])
t1_keys = set(zip(t1["PTID"], t1["VISCODE_FIX"]))
t1_viscode_map = t1.groupby("PTID")["VISCODE_FIX"].apply(sorted).apply(list).to_dict()

# ── Categorize each AV1451 row ───────────────────────────────────────────────

def categorize(row):
    key = (row["PTID"], row["VISCODE_FIX"])
    if key in t1_keys:
        return "matched"
    if row["PTID"] not in t1_ptids:
        return "no_ptid"
    return "viscode_mismatch"

av["_category"] = av.apply(categorize, axis=1)

n_matched = (av["_category"] == "matched").sum()
n_no_ptid = (av["_category"] == "no_ptid").sum()
n_viscode = (av["_category"] == "viscode_mismatch").sum()
n_total = len(av)
n_unmatched = n_no_ptid + n_viscode

assert n_matched + n_no_ptid + n_viscode == n_total, "Count mismatch!"
print(f"Total: {n_total}  Matched: {n_matched}  No-PTID: {n_no_ptid}  VISCODE mismatch: {n_viscode}")

# ── 1. Breakdown chart ────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 5))

categories = ["AV1451\n전체", "T1 매칭\n성공", "PTID\n미존재", "VISCODE\n불일치"]
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
ax.set_title(f"AV1451 ↔ T1 매칭 갭 분석 ({n_total}건)", fontsize=14, fontweight="bold", pad=15)
ax.set_ylim(0, n_total + 80)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="x", labelsize=11)

fig.tight_layout()
fig.savefig(OUT / "breakdown.png", dpi=150, bbox_inches="tight")
print(f"Saved: {OUT / 'breakdown.png'}")
plt.close(fig)

# ── 2. VISCODE mismatch heatmap ──────────────────────────────────────────────

mismatch = av[av["_category"] == "viscode_mismatch"].copy()

# For each mismatch, find the closest T1 VISCODE
def month_num(v: str) -> int:
    return int(v.replace("m", ""))

def closest_t1_viscode(row):
    viscodes = t1_viscode_map.get(row["PTID"], [])
    if not viscodes:
        return "N/A"
    av_m = month_num(row["VISCODE_FIX"])
    return min(viscodes, key=lambda v: abs(month_num(v) - av_m))

mismatch["T1_VISCODE_CLOSEST"] = mismatch.apply(closest_t1_viscode, axis=1)

ct = pd.crosstab(
    mismatch["VISCODE_FIX"].rename("AV1451 VISCODE"),
    mismatch["T1_VISCODE_CLOSEST"].rename("T1 VISCODE (closest)"),
)

# Show top patterns only (limit heatmap to top 10 rows/cols for readability)
row_sums = ct.sum(axis=1).sort_values(ascending=False)
col_sums = ct.sum(axis=0).sort_values(ascending=False)
top_rows = row_sums.head(10).index
top_cols = col_sums.head(10).index
ct_top = ct.loc[ct.index.isin(top_rows), ct.columns.isin(top_cols)]
# Reorder by frequency
ct_top = ct_top.loc[row_sums[row_sums.index.isin(top_rows)].index,
                     col_sums[col_sums.index.isin(top_cols)].index]

fig, ax = plt.subplots(figsize=(max(6, len(ct_top.columns) * 0.9), max(4, len(ct_top) * 0.6)))
im = ax.imshow(ct_top.values, cmap="YlOrRd", aspect="auto")

ax.set_xticks(range(len(ct_top.columns)))
ax.set_xticklabels(ct_top.columns, fontsize=10, rotation=45, ha="right")
ax.set_yticks(range(len(ct_top.index)))
ax.set_yticklabels(ct_top.index, fontsize=10)
ax.set_xlabel("T1 VISCODE (closest)", fontsize=12, labelpad=8)
ax.set_ylabel("AV1451 VISCODE", fontsize=12, labelpad=8)
ax.set_title(f"VISCODE 불일치 패턴 ({n_viscode}건)", fontsize=13, fontweight="bold", pad=12)

# Annotate cells
for i in range(len(ct_top.index)):
    for j in range(len(ct_top.columns)):
        val = ct_top.values[i, j]
        if val == 0:
            continue
        color = "white" if val > ct_top.values.max() * 0.6 else "black"
        ax.text(j, i, str(val), ha="center", va="center",
                fontsize=12, fontweight="bold", color=color)

fig.colorbar(im, ax=ax, label="건수", shrink=0.8)
fig.tight_layout()
fig.savefig(OUT / "heatmap.png", dpi=150, bbox_inches="tight")
print(f"Saved: {OUT / 'heatmap.png'}")
plt.close(fig)

# ── 3. Markdown summary ──────────────────────────────────────────────────────

# Top mismatch patterns
pattern_ct = mismatch.groupby(["VISCODE_FIX", "T1_VISCODE_CLOSEST"]).size().sort_values(ascending=False)
top_patterns = pattern_ct.head(10)

missing_ptid_df = av[av["_category"] == "no_ptid"][["PTID", "VISCODE_FIX"]].reset_index(drop=True)

summary = textwrap.dedent(f"""\
## AV1451 ↔ T1 매칭 갭 분석 (Issue #4)

### 요약

AV1451_6MM_unique.csv {n_total}건 중 {n_matched}건만 T1과 (PTID, VISCODE_FIX) 일치 — **{n_unmatched}건 불일치**.

| 카테고리 | 건수 | 비율 | 설명 |
|---|---|---|---|
| T1 매칭 성공 | {n_matched} | {n_matched/n_total:.1%} | 동일 (PTID, VISCODE_FIX) |
| PTID 미존재 | {n_no_ptid} | {n_no_ptid/n_total:.1%} | T1 데이터 자체 없음 |
| VISCODE 불일치 | {n_viscode} | {n_viscode/n_total:.1%} | 같은 PTID, 다른 방문 시점 |
| **합계** | **{n_total}** | **100%** | |

> **참고**: Issue #4 원문의 354건은 구 MERGED.csv (11,710행) 기준.
> 현재 MERGED.csv (13,112행) 기준으로는 {n_unmatched}건 불일치.

### VISCODE 불일치 상위 패턴 ({n_viscode}건)

| AV1451 VISCODE | T1 closest VISCODE | 건수 | 비율 |
|---|---|---|---|
""")

for (av_v, t1_v), cnt in top_patterns.items():
    summary += f"| {av_v} | {t1_v} | {cnt} | {cnt/n_viscode:.1%} |\n"

summary += f"""
### 근본 원인

- **outer join 설계**: `merge.py`의 outer join on `(PTID, VISCODE_FIX)` — 모달리티별 촬영 시점 차이
- **PET vs MRI 프로토콜 차이**: AV1451 PET과 T1 MRI는 다른 방문에서 촬영되는 경우 빈번
- **VISCODE_FIX 계산**: `round((AQUDATE - EXAMDATE_bl) / 30.44)` → 촬영일 차이가 VISCODE 차이로 이어짐
- **코드 이슈 아님** — 물리적 촬영 스케줄 차이에 의한 예상된 동작

### PTID 미존재 ({n_no_ptid}건)

| PTID | AV1451 VISCODE |
|---|---|
"""

for _, row in missing_ptid_df.iterrows():
    summary += f"| {row['PTID']} | {row['VISCODE_FIX']} |\n"

summary += "\n![매칭 갭 breakdown](breakdown.png)\n"
summary += "\n![VISCODE 불일치 heatmap](heatmap.png)\n"

(OUT / "summary.md").write_text(summary, encoding="utf-8")
print(f"Saved: {OUT / 'summary.md'}")
print("\nDone.")
