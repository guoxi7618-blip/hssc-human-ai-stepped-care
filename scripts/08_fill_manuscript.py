"""H8：把结果文件中的数值填入稿件占位符（{{...}}），并报告剩余占位符与摘要字数。"""
import re, json, sys, pandas as pd, numpy as np
sys.stdout.reconfigure(encoding="utf-8")
R = "D:/第五篇/论文_HSSC/results/"; M = "D:/第五篇/论文_HSSC/manuscript/"
pw = pd.read_csv(R + "h5_power.csv").set_index("scenario")
pool = pd.read_csv(R + "h0_baseline_pool_xinxiang.csv"); rci = 1.96 * np.sqrt(2) * pool.PHQ9.std() * np.sqrt(1 - 0.87)
pct = lambda v: f"{100 * v:.0f}\\%"
base = pw.loc[[i for i in pw.index if i.startswith("Base")][0]]
V = {"POWER_T1": pct(base.power_T1), "POWER_T2": pct(base.power_T2), "POWER_ICC06": pct(pw.loc["ICC 0.06"].power_T1),
     "POWER_SMALL": pct(pw.loc[[i for i in pw.index if i.startswith("Smaller")][0]].power_T1), "RCI": f"{rci:.1f}"}
ab = open(M + "abstract.txt", encoding="utf-8").read().strip()
V["ABSTRACT"] = ab.replace("%", "\\%").replace("–", "--").replace("−", "$-$")
print("abstract words:", len(re.findall(r"[A-Za-z0-9][A-Za-z0-9\-\.%]*", ab.split("[This version")[0])))
for f in ("part1_front_intro_methods.tex",):
    src = open(M + f.replace(".tex", "_template.tex") if False else M + f, encoding="utf-8").read()
    tpl = M + f.replace(".tex", ".template")
    import os
    if not os.path.exists(tpl): open(tpl, "w", encoding="utf-8").write(src)
    out = open(tpl, encoding="utf-8").read()
    for k, v in V.items(): out = out.replace("{{" + k + "}}", v)
    open(M + f, "w", encoding="utf-8").write(out)
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", out); print(f, "remaining placeholders:", left)
json.dump(V, open(R + "h8_filled_values.json", "w"), indent=1, ensure_ascii=False)
print(V)
