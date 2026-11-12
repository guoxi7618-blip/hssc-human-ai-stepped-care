"""H7：从结果文件生成 LaTeX 表 2（基线）、表 3（结局）与补充表（功效、真实性核验、实施），保证数字与分析一致。"""
import pandas as pd, numpy as np, json, sys
sys.stdout.reconfigure(encoding="utf-8")
R = "D:/第五篇/论文_HSSC/results/"; M = "D:/第五篇/论文_HSSC/manuscript/"
d = pd.read_csv(R + "trial_wide.csv"); res = pd.read_csv(R + "h3_outcomes.csv"); cm = pd.read_csv(R + "h3_cell_means.csv")
f1 = lambda x: f"{x:.1f}"; f2 = lambda x: f"{x:.2f}"
def msd(g, v, k=1): x = g[v].dropna(); return f"{x.mean():.{k}f} ({x.std():.{k}f})"
def npct(g, cond): return f"{int(cond.sum())} ({100 * cond.mean():.1f})"
I, C = d[d.arm == 1], d[d.arm == 0]
rows = [("Age, years, mean (SD)", msd(I, "age"), msd(C, "age")),
        ("Women, n (\\%)", npct(I, I.female == 1), npct(C, C.female == 1)),
        ("Year of study, n (\\%)", "", "")] + \
       [(f"\\quad Year {y}", npct(I, I.year == y), npct(C, C.year == y)) for y in (1, 2, 3)] + \
       [("Rural origin, n (\\%)", npct(I, I.rural == 1), npct(C, C.rural == 1)),
        ("Only child, n (\\%)", npct(I, I.only_child == 1), npct(C, C.only_child == 1)),
        ("Elevated tier at baseline, n (\\%)", npct(I, I.tier == "elevated"), npct(C, C.tier == "elevated")),
        ("Symptom profile, n (\\%)", "", "")] + \
       [(f"\\quad {s.capitalize()}", npct(I, I.subtype == s), npct(C, C.subtype == s)) for s in ("depression-predominant", "mixed", "anxiety-predominant")] + \
       [("PHQ-9, mean (SD)", msd(I, "PHQ9_0", 2), msd(C, "PHQ9_0", 2)), ("GAD-7, mean (SD)", msd(I, "GAD7_0", 2), msd(C, "GAD7_0", 2)),
        ("WSAS, mean (SD)", msd(I, "WSAS_0"), msd(C, "WSAS_0")), ("Resting ln RMSSD, mean (SD)", msd(I, "lnRMSSD_0", 2), msd(C, "lnRMSSD_0", 2)),
        ("Students per counsellor", "9", "9")]
t2 = ["\\begin{table}[p]", "\\caption{Baseline characteristics of students by trial arm}", "\\label{tab:baseline}", "\\centering\\small",
      "\\begin{tabular}{lcc}", "\\toprule", f"Characteristic & Intervention ($n={len(I)}$; 10 clusters) & Enhanced usual care ($n={len(C)}$; 10 clusters) \\\\", "\\midrule"]
t2 += [f"{a} & {b} & {c} \\\\" for a, b, c in rows]
t2 += ["\\bottomrule", "\\end{tabular}", "\\par\\vspace{2pt}{\\footnotesize Values are n (\\%) or mean (SD). In line with CONSORT, baseline differences are not tested for significance. PHQ-9, Patient Health Questionnaire-9; GAD-7, Generalized Anxiety Disorder-7; WSAS, Work and Social Adjustment Scale; RMSSD, root mean square of successive differences. Resting HRV was missing for students whose recording failed quality checks.}", "\\end{table}"]
open(M + "table2_baseline.tex", "w", encoding="utf-8").write("\n".join(t2))

NM = {"PHQ9": "PHQ-9 (0--27)", "GAD7": "GAD-7 (0--21)", "WSAS": "WSAS (0--40)", "lnRMSSD": "ln RMSSD"}
def pf(p): return "$<$0.001" if p < 0.001 else f"{p:.3f}"
t3 = ["\\begin{table}[p]", "\\caption{Primary and secondary outcomes (intention to treat)}", "\\label{tab:outcomes}", "\\centering\\footnotesize",
      "\\begin{tabular}{llcccccc}", "\\toprule",
      "Outcome & Time & \\multicolumn{2}{c}{Intervention} & \\multicolumn{2}{c}{Enhanced usual care} & Adjusted difference [95\\% CI] & $P$ ($P_{\\mathrm{Holm}}$) \\\\",
      "\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}", " & & $n$ & Mean (SD) & $n$ & Mean (SD) & (standardised) & \\\\", "\\midrule"]
for v in ("PHQ9", "GAD7", "WSAS", "lnRMSSD"):
    k = 2 if v == "lnRMSSD" else 1
    for t in (0, 1, 2):
        ci = cm[(cm.outcome == v) & (cm.arm == 1) & (cm.time == t)].iloc[0]; cc = cm[(cm.outcome == v) & (cm.arm == 0) & (cm.time == t)].iloc[0]
        if t == 0: eff = "--"; pp = ""
        else:
            r = res[(res.outcome == v) & (res.time == f"T{t}")].iloc[0]
            eff = f"{r['diff']:.2f} [{r.lo:.2f}, {r.hi:.2f}] ({r.g:.2f})".replace("-", "$-$")
            pp = pf(r.p) + (f" ({pf(r.p_holm)})" if pd.notna(r.get("p_holm", np.nan)) else "")
        lab = NM[v] if t == 0 else ""
        t3.append(f"{lab} & T{t} & {int(ci.n)} & {ci['mean']:.{k}f} ({ci.sd:.{k}f}) & {int(cc.n)} & {cc['mean']:.{k}f} ({cc.sd:.{k}f}) & {eff} & {pp} \\\\")
    t3.append("\\addlinespace")
for _, r in res[res.outcome.str.startswith("risk")].iterrows():
    t3.append(f"Risk level (ordinal) & {r.time} & & & & & OR {r['diff']:.2f} [{r.lo:.2f}, {r.hi:.2f}] & {pf(r.p)}" + (f" ({pf(r.p_holm)})" if pd.notna(r.get("p_holm", np.nan)) else "") + " \\\\")
t3 += ["\\bottomrule", "\\end{tabular}",
       "\\par\\vspace{2pt}{\\footnotesize Means are observed values. Adjusted differences (intervention minus control) come from linear mixed models with fixed effects for arm, time, arm $\\times$ time, baseline score, baseline tier and sex, and random intercepts for counsellor and student; $t$ distribution with 18 degrees of freedom. Standardised differences divide by the pooled SD at the same time point. Risk level: ordinal GEE, odds ratio for a higher risk level (OR $<$ 1 favours the intervention). Holm adjustment across the four secondary outcomes at T1.}",
       "\\end{table}"]
open(M + "table3_outcomes.tex", "w", encoding="utf-8").write("\n".join(t3))
print("tables written")
