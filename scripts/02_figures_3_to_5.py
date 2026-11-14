"""figures 3 to 5
Fig. 3 结局轨迹；Fig. 4 效应森林图；Fig. 5 人机协作过程与实施结局。CONSORT（Fig. 2）由 h_fig2_consort_pptx.py 生成。
"""
import numpy as np, pandas as pd, json, sys
import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
sys.stdout.reconfigure(encoding="utf-8")
R = "D:/第五篇/论文_HSSC/results/"; F = "D:/第五篇/论文_HSSC/analysis/figures/"
mpl.rcParams.update({"font.family": "Arial", "font.size": 6.5, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                     "xtick.major.size": 2.5, "ytick.major.size": 2.5, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "pdf.fonttype": 42, "axes.titlesize": 7, "axes.labelsize": 6.8, "savefig.dpi": 600})
CI, CC = "#C2410C", "#2F5D8A"            # 干预 / 对照
d = pd.read_csv(R + "trial_wide.csv"); res = pd.read_csv(R + "h3_outcomes.csv"); sens = pd.read_csv(R + "h3_sensitivity.csv")
sub = pd.read_csv(R + "h3_subgroups.csv"); resp = pd.read_csv(R + "h3_response.csv"); plans = pd.read_csv(R + "process_plans.csv")
imp = json.load(open(R + "h3_implementation.json")); proc = pd.read_csv(R + "h3_process_outcome.csv")


def plab(ax, s, x=-0.18, y=1.06): ax.text(x, y, s, transform=ax.transAxes, fontsize=8.5, fontweight="bold", va="bottom")
def save(fig, name): fig.savefig(F + name + ".pdf", bbox_inches="tight"); fig.savefig(F + name + ".png", bbox_inches="tight", dpi=600); plt.close(fig)


# ============================ Fig. 3 轨迹 ============================
fig = plt.figure(figsize=(7.09, 3.55)); gs = fig.add_gridspec(2, 4, height_ratios=[1, 0.82], hspace=0.62, wspace=0.55)
OUT = [("PHQ9", "PHQ-9 (depressive symptoms)", "a"), ("GAD7", "GAD-7 (anxiety symptoms)", "b"), ("WSAS", "WSAS (functional impairment)", "c"), ("lnRMSSD", "Resting ln RMSSD", "d")]
tx = np.array([0, 12, 38])                                               # 周：T0、T1（12 周）、T2（干预结束后 6 个月 ≈ 第 38 周）
for j, (v, lab, L) in enumerate(OUT):
    ax = fig.add_subplot(gs[0, j])
    for a, col, off, mk in ((0, CC, -0.9, "s"), (1, CI, 0.9, "o")):
        g = d[d.arm == a]
        # 个体轨迹（随机抽 25 人，细灰线）
        smp = g.sample(25, random_state=3 + a)
        for _, r in smp.iterrows():
            ax.plot(tx + off, [r[f"{v}_0"], r[f"{v}_1"], r[f"{v}_2"]], color=col, lw=0.25, alpha=0.18, zorder=1)
        m = [g[f"{v}_{t}"].mean() for t in (0, 1, 2)]; se = [g[f"{v}_{t}"].std() / np.sqrt(g[f"{v}_{t}"].notna().sum()) for t in (0, 1, 2)]
        ax.errorbar(tx + off, m, yerr=1.96 * np.array(se), color=col, lw=1.1, marker=mk, ms=3.2, capsize=1.6, zorder=3, mfc="white" if a == 0 else col, mew=0.9)
    for t, T in ((1, "T1"), (2, "T2")):
        rr = res[(res.outcome == v) & (res.time == T)].iloc[0]
        ytop = ax.get_ylim()[1]
        star = "*" if rr.p < 0.05 else "ns"
        ax.text(tx[t], ytop, f"Δ {rr['diff']:+.2f}".replace("-", "−") + f"\n{star}", ha="center", va="bottom", fontsize=5.4, color="#333333")
    ax.set_xticks(tx); ax.set_xticklabels(["T0", "T1\n12 wk", "T2\n+6 mo"]); ax.set_title(lab, fontsize=6.6, pad=13)
    if v == "lnRMSSD": ax.set_ylabel("ln RMSSD");
    else: ax.set_ylabel("Score")
    plab(ax, L, x=-0.32, y=1.12)
h_ = [Line2D([], [], color=CI, marker="o", lw=1.1, ms=3.2, label="Human–AI stepped intervention (10 clusters, n = 90)"),
      Line2D([], [], color=CC, marker="s", mfc="white", lw=1.1, ms=3.2, label="Enhanced usual care (10 clusters, n = 90)")]
fig.legend(handles=h_, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.03), fontsize=6.2)
# e: 风险等级构成（堆叠条）
ax = fig.add_subplot(gs[1, 0:2])
cols = ["#D9EAD3", "#FFE599", "#F6B26B", "#CC0000"]; labs = ["low", "moderate", "elevated", "high"]
ypos = []; yl = []
k = 0
for t in (0, 1, 2):
    for a, nm in ((1, "Intervention"), (0, "Control")):
        x = d.loc[d.arm == a, f"risk_{t}"].dropna(); pr = [100 * (x == c).mean() for c in range(4)]
        left = 0
        for c in range(4):
            ax.barh(k, pr[c], left=left, color=cols[c], height=0.72, edgecolor="white", lw=0.4)
            if pr[c] >= 7: ax.text(left + pr[c] / 2, k, f"{pr[c]:.0f}", ha="center", va="center", fontsize=5.2)
            left += pr[c]
        ypos.append(k); yl.append(f"T{t}  {nm} (n = {len(x)})"); k += 1
    k += 0.5
ax.set_yticks(ypos); ax.set_yticklabels(yl, fontsize=5.6); ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xlabel("Blinded risk level (% of assessed students)")
ax.legend(handles=[Patch(color=c, label=l) for c, l in zip(cols, labs)], ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=5.6, handlelength=1)
plab(ax, "e", x=-0.2, y=1.1)
# f: 可靠改善 / 恢复 / 可靠恶化（按时点分组）
ax = fig.add_subplot(gs[1, 2:4])
SHORT = {"reliable improvement": "Reliable\nimprov.", "PHQ-9 < 5": "PHQ-9\n< 5", "reliable deterioration": "Reliable\ndeterior."}
xpos, xl = [], []
for gi, T in enumerate(("T1", "T2")):
    for jj, oc in enumerate(["reliable improvement", "PHQ-9 < 5", "reliable deterioration"]):
        r = resp[(resp.time == T) & (resp.outcome == oc)].iloc[0]; x0 = gi * 3.6 + jj
        ax.bar(x0 - 0.18, r.int_pct, 0.34, color=CI); ax.bar(x0 + 0.18, r.ctrl_pct, 0.34, color="white", edgecolor=CC, hatch="////", lw=0.7)
        lab = f"NNT {r.NNT:.0f}" if pd.notna(r.NNT) and r.NNT < 60 else f"Δ {r.risk_diff:+.0f} pp".replace("-", "−")
        ax.text(x0, max(r.int_pct, r.ctrl_pct) + 2, lab, ha="center", fontsize=5.2)
        xpos.append(x0); xl.append(SHORT[oc])
    ax.text(gi * 3.6 + 1, -30, T + (" (12 weeks)" if T == "T1" else " (+6 months)"), ha="center", fontsize=6, fontweight="bold")
ax.set_xticks(xpos); ax.set_xticklabels(xl, fontsize=5.2); ax.set_ylabel("% of students"); ax.set_ylim(0, 95)
ax.legend(handles=[Patch(color=CI, label="Intervention"), Patch(facecolor="white", edgecolor=CC, hatch="////", label="Control")], loc="upper center", ncol=2, fontsize=5.6, bbox_to_anchor=(0.5, 1.13))
plab(ax, "f", x=-0.12, y=1.1)
save(fig, "Fig3_outcomes")

# ============================ Fig. 4 森林图（手动排版：森林图 + 数值列，互不重叠）============================
def fp(v): return "<0.001" if v < 0.001 else f"{v:.3f}"
fig = plt.figure(figsize=(7.09, 4.2))
axA = fig.add_axes([0.13, 0.13, 0.25, 0.80]); axAt = fig.add_axes([0.385, 0.13, 0.15, 0.80]); axAt.axis("off")
axB = fig.add_axes([0.79, 0.13, 0.19, 0.80]); axBl = fig.add_axes([0.60, 0.13, 0.19, 0.80]); axBl.axis("off")
NAMES = {"PHQ9": "PHQ-9 (primary)", "GAD7": "GAD-7", "WSAS": "WSAS", "lnRMSSD": "ln RMSSD"}
y = 0; yt, ylab, bold = [], [], []
for v in ("PHQ9", "GAD7", "WSAS", "lnRMSSD"):
    yt.append(y); ylab.append(NAMES[v]); bold.append(True); y += 1
    for T in ("T1", "T2"):
        r = res[(res.outcome == v) & (res.time == T)].iloc[0]
        col = CI if r.p < 0.05 else "#7F7F7F"
        axA.plot([r.g_lo, r.g_hi], [y, y], color=col, lw=0.9); axA.plot(r.g, y, "s" if T == "T1" else "D", color=col, ms=3.4 if T == "T1" else 2.8)
        axAt.text(0.0, y, f"{r['diff']:+.2f} [{r.lo:+.2f}, {r.hi:+.2f}]".replace("-", "−"), fontsize=5.4, va="center", transform=axAt.get_yaxis_transform())
        ph = r.get("p_holm", np.nan)
        axAt.text(0.74, y, fp(r.p) + (f" ({fp(ph)})" if pd.notna(ph) else ""), fontsize=5.4, va="center", transform=axAt.get_yaxis_transform())
        yt.append(y); ylab.append(f"  {T}"); bold.append(False); y += 1
ro = res[res.outcome.str.startswith("risk")]
y += 0.4; yt.append(y); ylab.append("Risk level (OR)"); bold.append(True); y += 1
for _, r in ro.iterrows():
    axA.text(0.0, y, "", fontsize=1)
    axAt.text(0.0, y, f"OR {r['diff']:.2f} [{r.lo:.2f}, {r.hi:.2f}]", fontsize=5.4, va="center", transform=axAt.get_yaxis_transform())
    axAt.text(0.74, y, fp(r.p) + (f" ({fp(r.p_holm)})" if pd.notna(r.get("p_holm", np.nan)) else ""), fontsize=5.4, va="center", transform=axAt.get_yaxis_transform())
    yt.append(y); ylab.append(f"  {r.time}"); bold.append(False); y += 1
for ax_ in (axA, axAt): ax_.set_ylim(y - 0.3, -1.2)
axA.axvline(0, color="#999999", lw=0.6, ls="--"); axA.set_yticks(yt); axA.set_yticklabels(ylab, fontsize=6)
for t_, b_ in zip(axA.get_yticklabels(), bold): t_.set_fontweight("bold" if b_ else "normal")
axA.set_xlabel("Standardised difference (pooled SD)\n← favours intervention", fontsize=6)
axAt.text(0.0, -0.9, "Difference [95% CI]", fontsize=5.6, fontweight="bold", transform=axAt.get_yaxis_transform())
axAt.text(0.74, -0.9, "P (Holm)", fontsize=5.6, fontweight="bold", transform=axAt.get_yaxis_transform())
axA.text(-0.62, 1.01, "a", transform=axA.transAxes, fontsize=8.5, fontweight="bold")
# b：敏感性 + 亚组
y = 0; rowsB = [("Sensitivity analyses (PHQ-9, T1)", None, True)]
SH = {"Primary: ITT mixed model (MAR)": "Primary: ITT mixed model", "Complete cases, ANCOVA, cluster-robust SE": "Complete cases, cluster-robust",
      "Complete cases, ignoring clustering": "Complete cases, no clustering", "Multiple imputation (m = 20)": "Multiple imputation (m = 20)",
      "Pattern mixture, δ = +1 point (intervention missing)": "Pattern mixture, δ = +1", "Pattern mixture, δ = +2 points (intervention missing)": "Pattern mixture, δ = +2",
      "CACE (2SLS, randomisation as instrument)": "CACE (2SLS)"}
for _, r in sens.iterrows(): rowsB.append((SH.get(r.analysis, r.analysis), r, False))
rowsB.append(("Prespecified subgroups", None, True))
FN = {"tier": "Baseline tier", "subtype": "Symptom profile", "female": "Sex"}; LV = {"0": "men", "1": "women"}
for fac in ("tier", "subtype", "female"):
    g = sub[sub.factor == fac]; pint = g[g.level == "interaction p"].hi.iloc[0]
    rowsB.append((f"{FN[fac]} (P interaction = {pint:.2f})", None, False))
    for _, r in g[g.level != "interaction p"].iterrows(): rowsB.append((f"    {LV.get(r.level, r.level)} (n = {int(r.n)})", r, False))
XL = (-8.5, 2.0)
for k, (lab, r, b_) in enumerate(rowsB):
    axBl.text(1.0, k, lab, ha="right", va="center", fontsize=5.6, fontweight="bold" if b_ else "normal", transform=axBl.get_yaxis_transform())
    if r is None: continue
    col = CI if "Primary" in lab else ("#5B3A8C" if "CACE" in lab else "#333333")
    lo_, hi_ = max(r.lo, XL[0]), min(r.hi, XL[1])
    axB.plot([lo_, hi_], [k, k], color=col, lw=0.9); axB.plot(r["diff"], k, "s" if "analysis" in r.index else "o", color=col, ms=3, mfc=col if "analysis" in r.index else "white")
    if r.lo < XL[0]: axB.annotate("", xy=(XL[0], k), xytext=(XL[0] + 0.6, k), arrowprops=dict(arrowstyle="->", lw=0.6, color=col))
for ax_ in (axB, axBl): ax_.set_ylim(len(rowsB) - 0.4, -0.8)
axB.set_xlim(*XL); axB.axvline(0, color="#999999", lw=0.6, ls="--"); axB.set_yticks([])
axB.set_xlabel("PHQ-9 difference at T1\n(points, 95% CI)", fontsize=6)
axBl.text(-0.05, 1.01, "b", transform=axBl.transAxes, fontsize=8.5, fontweight="bold")
save(fig, "Fig4_effects")

# ============================ Fig. 5 过程与实施 ============================
fig = plt.figure(figsize=(7.09, 3.7)); gs = fig.add_gridspec(2, 3, hspace=0.75, wspace=0.62)
# a: 采纳/修改/否决（按层级 × 周）
ax = fig.add_subplot(gs[0, 0]); cat = ["accepted", "modified", "rejected"]; cc = ["#BFBFBF", "#E69F00", "#B00020"]
k = 0; xt, xl = [], []
for tier in ("moderate", "elevated"):
    for wk in (0, 4, 8):
        g = plans[(plans.tier == tier) & (plans.week == wk)]; b = 0
        for c, col in zip(cat, cc):
            v = 100 * (g.decision == c).mean(); ax.bar(k, v, bottom=b, color=col, width=0.75, edgecolor="white", lw=0.3); b += v
        ax.text(k, 101, f"{len(g)}", ha="center", fontsize=4.8, color="#555555"); xt.append(k); xl.append(f"w{wk}"); k += 1
    k += 0.6
ax.set_xticks(xt); ax.set_xticklabels(xl, fontsize=5.4); ax.set_ylabel("% of algorithm plans"); ax.set_ylim(0, 108)
ax.text(1, -24, "moderate tier", ha="center", fontsize=5.6, transform=ax.transData); ax.text(4.6, -24, "elevated tier", ha="center", fontsize=5.6)
ax.legend(handles=[Patch(color=c, label=l) for c, l in zip(cc, cat)], ncol=3, loc="lower left", bbox_to_anchor=(-0.05, 1.08), fontsize=5.2, handlelength=0.8, columnspacing=0.5)
plab(ax, "a", x=-0.3, y=1.12)
# b: 修改理由
ax = fig.add_subplot(gs[0, 1]); rs = plans[plans.decision != "accepted"].reason.value_counts()
lab_ = {"contextual information not available to the algorithm": "context unavailable\nto algorithm", "student preference": "student preference",
        "risk judgement": "risk judgement", "feasibility/workload": "feasibility / workload"}
ax.barh(range(len(rs)), rs.values, color="#E69F00", height=0.6); ax.set_yticks(range(len(rs))); ax.set_yticklabels([lab_[i] for i in rs.index], fontsize=5.6); ax.invert_yaxis()
for i, v in enumerate(rs.values): ax.text(v + 0.8, i, f"{v} ({100 * v / rs.sum():.0f}%)", va="center", fontsize=5.3)
ax.set_xlabel("Overridden plans (n)"); ax.set_xlim(0, rs.max() * 1.45); plab(ax, "b", x=-0.62, y=1.12)
# c: 辅导员间推翻率差异
ax = fig.add_subplot(gs[0, 2]); o = plans.assign(o=plans.decision != "accepted").groupby("counsellor").o.agg(["mean", "size"]).sort_values("mean")
lo_ = o["mean"] - 1.96 * np.sqrt(o["mean"] * (1 - o["mean"]) / o["size"]); hi_ = o["mean"] + 1.96 * np.sqrt(o["mean"] * (1 - o["mean"]) / o["size"])
ax.errorbar(100 * o["mean"], range(len(o)), xerr=[100 * (o["mean"] - lo_.clip(0)), 100 * (hi_.clip(upper=1) - o["mean"])], fmt="o", color="#333333", ms=2.6, lw=0.6, capsize=1)
ax.axvline(100 * (plans.decision != "accepted").mean(), color="#E69F00", lw=0.8, ls="--")
ax.set_yticks(range(len(o))); ax.set_yticklabels([f"C{c:02d}" for c in o.index], fontsize=5); ax.set_xlabel("Plans overridden (%; 95% CI)"); ax.set_xlim(0, 80)
plab(ax, "c", x=-0.3, y=1.12)
# d: 生理反馈练习分布
ax = fig.add_subplot(gs[1, 0]); iv = d[d.arm == 1]
ax.hist(iv.practice_per_week, bins=np.arange(0, 17, 1.0), color="#2E7D32", alpha=0.85, edgecolor="white", lw=0.3)
ax.axvline(iv.practice_per_week.median(), color="k", lw=0.7, ls="--"); ax.text(iv.practice_per_week.median(), ax.get_ylim()[1] * 0.92, f" median {iv.practice_per_week.median():.1f}", fontsize=5.3)
ax.set_xlabel("Biofeedback sessions per week"); ax.set_ylabel("Students (n)"); plab(ax, "d", x=-0.3, y=1.08)
# e: 辅导员投入
ax = fig.add_subplot(gs[1, 1])
parts = ax.violinplot([d[d.arm == 0].counsellor_min_per_week, d[(d.arm == 1) & (d.tier == "moderate")].counsellor_min_per_week, d[(d.arm == 1) & (d.tier == "elevated")].counsellor_min_per_week],
                      showmedians=True, widths=0.7)
for pc, col in zip(parts["bodies"], [CC, "#E69F00", CI]): pc.set_facecolor(col); pc.set_alpha(0.55); pc.set_edgecolor("none")
for k_ in ("cbars", "cmins", "cmaxes", "cmedians"): parts[k_].set_color("#333333"); parts[k_].set_linewidth(0.6)
ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["control", "interv.\nmoderate", "interv.\nelevated"], fontsize=5.5); ax.set_ylabel("Counsellor min / student / week")
plab(ax, "e", x=-0.42, y=1.08)
# f: 过程–结局（探索性）
ax = fig.add_subplot(gs[1, 2])
for i, (_, r) in enumerate(proc.iterrows()):
    ax.plot([r.lo, r.hi], [i, i], color="#333333", lw=0.8); ax.plot(r.b, i, "o", color="#333333", ms=2.8)
ax.axvline(0, color="#999999", lw=0.6, ls="--"); ax.set_yticks(range(len(proc)))
ax.set_yticklabels([p.replace(" (sessions/week)", "\n(per session/week)").replace("share of plans modified/rejected", "share of plans\noverridden") for p in proc.predictor], fontsize=5.3)
ax.invert_yaxis(); ax.set_xlabel("ΔPHQ-9 at T1 per unit\n(intervention arm, exploratory)", fontsize=6); plab(ax, "f", x=-0.75, y=1.08)
save(fig, "Fig5_process")
print("figures saved")
