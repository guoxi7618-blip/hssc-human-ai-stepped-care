"""trial analysis

主要分析（ITT）：线性混合模型，结局为 T1、T2 的 PHQ-9，固定效应 = 组别 × 时点 + 基线 PHQ-9 + 基线层级 + 性别，
随机效应 = 辅导员（整群）随机截距 + 学生随机截距（方差成分）。主要估计量：T1 组间调整均值差（95% CI），标准化差以对应时点合并 SD 标准化。
次要：GAD-7、WSAS、ln RMSSD 同模型；风险等级用序数 GEE（累积 logit，辅导员聚类，交换相关）；Holm 校正 T1 次要结局。
敏感性：多重插补（m=20，按组链式回归）、δ 调整模式混合（干预组缺失者 +1、+2 分）、完整病例、去除整群项。
CACE：以随机分组为工具变量的两阶段最小二乘（辅导员聚类稳健 SE）。
反应率：可靠改善（RCI：基线 α=0.87、新乡 SD）、恢复到 PHQ-9 <5；NNT。
亚组（预设，交互检验）：基线层级、亚型（抑郁为主/焦虑为主/混合）、性别。
过程：干预组内练习剂量、辅导员接触与 T1 变化的关联（探索性，非因果）；方案采纳/修改与结局。
输出：results/h3_*.csv
"""
import numpy as np, pandas as pd, json, sys, warnings
import statsmodels.formula.api as smf, statsmodels.api as sm
from statsmodels.genmod.generalized_estimating_equations import OrdinalGEE
from statsmodels.genmod.cov_struct import Exchangeable
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
R = "D:/第五篇/论文_HSSC/results/"
d = pd.read_csv(R + "trial_wide.csv"); pool = pd.read_csv(R + "h0_baseline_pool_xinxiang.csv")
d["elev"] = (d.tier == "elevated").astype(int)
rng = np.random.default_rng(7)


def long_of(df, v):
    L = []
    for t in (1, 2):
        x = df[["sid", "counsellor", "arm", "female", "elev", "tier", "subtype", f"{v}_0"]].copy(); x["y"] = df[f"{v}_{t}"]; x["T2"] = int(t == 2); L.append(x)
    return pd.concat(L, ignore_index=True).rename(columns={f"{v}_0": "base"})


def lmm(df, v, extra=""):
    L = long_of(df, v).dropna(subset=["y", "base"]).reset_index(drop=True)
    f = f"y ~ arm * T2 + base + elev + female{extra}"
    m = smf.mixedlm(f, L, groups="counsellor", re_formula="1", vc_formula={"sid": "0 + C(sid)"}).fit(reml=True, method="lbfgs")
    b = m.params; V = m.cov_params()
    est = {}
    for t, c in ((1, np.array([1, 0])), (2, np.array([1, 1]))):
        names = ["arm", "arm:T2"]; e = float(c @ b[names]); se = float(np.sqrt(c @ V.loc[names, names].values @ c))
        from scipy import stats
        df_ = 20 - 2                                         # 以整群数计算的保守自由度（Kenward–Roger 近似的简化）
        tcrit = stats.t.ppf(.975, df_); p = 2 * stats.t.sf(abs(e / se), df_)
        est[t] = dict(diff=e, lo=e - tcrit * se, hi=e + tcrit * se, p=p, se=se)
    return m, est, L


def cell_means(df, v):
    out = []
    for a in (0, 1):
        for t in (0, 1, 2):
            x = df.loc[df.arm == a, f"{v}_{t}"].dropna(); out.append(dict(outcome=v, arm=a, time=t, n=len(x), mean=x.mean(), sd=x.std()))
    return out


res, means = [], []
for v in ("PHQ9", "GAD7", "WSAS", "lnRMSSD"):
    m, est, L = lmm(d, v)
    for t in (1, 2):
        sd0 = d[f"{v}_{t}"].std()                                   # 以对应时点的合并 SD 标准化（基线受纳入标准截断，会夸大 g）
        e = est[t]; res.append(dict(outcome=v, time=f"T{t}", diff=e["diff"], lo=e["lo"], hi=e["hi"], p=e["p"], g=e["diff"] / sd0, g_lo=e["lo"] / sd0, g_hi=e["hi"] / sd0,
                                    n_obs=int(L[L.T2 == (t - 1)].shape[0])))
    means += cell_means(d, v)
res = pd.DataFrame(res)

# ---------- 风险等级：序数 GEE ----------
for t in (1, 2):
    x = d.dropna(subset=[f"risk_{t}"]).copy(); x["y"] = x[f"risk_{t}"].astype(int)
    mod = OrdinalGEE.from_formula("y ~ 0 + arm + risk_0 + female", groups="counsellor", data=x, cov_struct=Exchangeable())
    f = mod.fit(); b = f.params["arm"]; se = f.bse["arm"]
    res = pd.concat([res, pd.DataFrame([dict(outcome="risk level (OR, higher = worse)", time=f"T{t}", diff=np.exp(b), lo=np.exp(b - 1.96 * se), hi=np.exp(b + 1.96 * se),
                                             p=float(f.pvalues["arm"]), g=np.nan, g_lo=np.nan, g_hi=np.nan, n_obs=len(x))])])
# Holm：T1 次要结局（GAD7, WSAS, lnRMSSD, risk）
sec = (res.time == "T1") & (res.outcome != "PHQ9")
res.loc[sec, "p_holm"] = multipletests(res.loc[sec, "p"], method="holm")[1]
res.to_csv(R + "h3_outcomes.csv", index=False, encoding="utf-8-sig"); pd.DataFrame(means).to_csv(R + "h3_cell_means.csv", index=False, encoding="utf-8-sig")

# ---------- 敏感性分析（主要结局 T1）----------
sens = []
_, e, _ = lmm(d, "PHQ9"); sens.append(dict(analysis="Primary: ITT mixed model (MAR)", diff=e[1]["diff"], lo=e[1]["lo"], hi=e[1]["hi"], p=e[1]["p"]))
cc = d.dropna(subset=["PHQ9_1"]); o = smf.ols("PHQ9_1 ~ arm + PHQ9_0 + elev + female", cc).fit(cov_type="cluster", cov_kwds={"groups": cc.counsellor})
sens.append(dict(analysis="Complete cases, ANCOVA, cluster-robust SE", diff=o.params.arm, lo=o.conf_int().loc["arm", 0], hi=o.conf_int().loc["arm", 1], p=o.pvalues.arm))
o2 = smf.ols("PHQ9_1 ~ arm + PHQ9_0 + elev + female", cc).fit()
sens.append(dict(analysis="Complete cases, ignoring clustering", diff=o2.params.arm, lo=o2.conf_int().loc["arm", 0], hi=o2.conf_int().loc["arm", 1], p=o2.pvalues.arm))


def mi_estimate(delta=0.0, M=20):
    ests, vars_ = [], []
    for mi in range(M):
        x = d.copy()
        for a in (0, 1):
            g = x[x.arm == a]; obs = g.dropna(subset=["PHQ9_1"])
            fit = smf.ols("PHQ9_1 ~ PHQ9_0 + GAD7_0 + WSAS_0 + elev + female", obs).fit()
            beta = rng.multivariate_normal(fit.params, fit.cov_params()); sig = np.sqrt(fit.scale * len(obs) / rng.chisquare(len(obs) - len(beta)))
            mis = g.PHQ9_1.isna(); X = sm.add_constant(g.loc[mis, ["PHQ9_0", "GAD7_0", "WSAS_0", "elev", "female"]])
            imp = X.values @ beta + rng.normal(0, sig, mis.sum()) + (delta if a == 1 else 0)
            x.loc[g.index[mis], "PHQ9_1"] = np.clip(imp, 0, 27)
        f = smf.ols("PHQ9_1 ~ arm + PHQ9_0 + elev + female", x).fit(cov_type="cluster", cov_kwds={"groups": x.counsellor})
        ests.append(f.params.arm); vars_.append(f.bse.arm ** 2)
    q = np.mean(ests); W = np.mean(vars_); B = np.var(ests, ddof=1); T = W + (1 + 1 / M) * B; se = np.sqrt(T)
    from scipy import stats
    return q, q - 1.96 * se, q + 1.96 * se, 2 * stats.norm.sf(abs(q / se))


for delta, lab in ((0, "Multiple imputation (m = 20)"), (1, "Pattern mixture, δ = +1 point (intervention missing)"), (2, "Pattern mixture, δ = +2 points (intervention missing)")):
    q, lo, hi, p = mi_estimate(delta); sens.append(dict(analysis=lab, diff=q, lo=lo, hi=hi, p=p))

# CACE（2SLS，工具变量 = 随机分组）
cc2 = d.dropna(subset=["PHQ9_1"]).copy(); cc2["engaged"] = cc2.comply * cc2.arm
st1 = smf.ols("engaged ~ arm + PHQ9_0 + elev + female", cc2).fit(); cc2["eng_hat"] = st1.fittedvalues
st2 = smf.ols("PHQ9_1 ~ eng_hat + PHQ9_0 + elev + female", cc2).fit(cov_type="cluster", cov_kwds={"groups": cc2.counsellor})
sens.append(dict(analysis="CACE (2SLS, randomisation as instrument)", diff=st2.params.eng_hat, lo=st2.conf_int().loc["eng_hat", 0], hi=st2.conf_int().loc["eng_hat", 1], p=st2.pvalues.eng_hat))
pd.DataFrame(sens).to_csv(R + "h3_sensitivity.csv", index=False, encoding="utf-8-sig")

# ---------- 反应率与 NNT ----------
sd_pool = pool.PHQ9.std(); rci = 1.96 * np.sqrt(2) * sd_pool * np.sqrt(1 - 0.87)
resp = []
for t in (1, 2):
    x = d.dropna(subset=[f"PHQ9_{t}"]); ch = x[f"PHQ9_{t}"] - x.PHQ9_0
    for lab, cond in (("reliable improvement", ch <= -rci), ("PHQ-9 < 5", x[f"PHQ9_{t}"] < 5), ("reliable deterioration", ch >= rci)):
        p1, p0 = cond[x.arm == 1].mean(), cond[x.arm == 0].mean(); rd = p1 - p0
        resp.append(dict(time=f"T{t}", outcome=lab, int_pct=100 * p1, ctrl_pct=100 * p0, risk_diff=100 * rd, NNT=(1 / rd) if rd > 0 and "deterioration" not in lab else np.nan, rci_points=rci))
pd.DataFrame(resp).to_csv(R + "h3_response.csv", index=False, encoding="utf-8-sig")

# ---------- 亚组（交互）----------
sub = []
for var, levels in (("tier", ["moderate", "elevated"]), ("subtype", ["depression-predominant", "mixed", "anxiety-predominant"]), ("female", [0, 1])):
    for lv in levels:
        x = d[(d[var] == lv)].dropna(subset=["PHQ9_1"])
        if x.arm.nunique() < 2 or len(x) < 12: continue
        o = smf.ols("PHQ9_1 ~ arm + PHQ9_0", x).fit(cov_type="cluster", cov_kwds={"groups": x.counsellor})
        sub.append(dict(factor=var, level=str(lv), n=len(x), diff=o.params.arm, lo=o.conf_int().loc["arm", 0], hi=o.conf_int().loc["arm", 1]))
    x = d.dropna(subset=["PHQ9_1"]); f = smf.ols(f"PHQ9_1 ~ arm * C({var}) + PHQ9_0", x).fit(cov_type="cluster", cov_kwds={"groups": x.counsellor})
    terms = [t_ for t_ in f.params.index if t_.startswith("arm:")]
    w = f.wald_test(" , ".join(f"{t_} = 0" for t_ in terms), scalar=True)
    sub.append(dict(factor=var, level="interaction p", n=len(x), diff=np.nan, lo=np.nan, hi=float(w.pvalue)))
pd.DataFrame(sub).to_csv(R + "h3_subgroups.csv", index=False, encoding="utf-8-sig")

# ---------- 过程–结局（干预组，探索性）----------
pl = pd.read_csv(R + "process_plans.csv")
iv = d[d.arm == 1].dropna(subset=["PHQ9_1"]).copy(); iv["chg"] = iv.PHQ9_1 - iv.PHQ9_0
ov = pl.groupby("sid").decision.apply(lambda s: (s != "accepted").mean()).rename("override_share"); iv = iv.join(ov, on="sid")
proc = []
for v, lab in (("practice_per_week", "biofeedback practice (sessions/week)"), ("peer_sessions_attended", "peer sessions attended"), ("counsellor_talks", "counsellor talks"),
               ("override_share", "share of plans modified/rejected")):
    o = smf.ols(f"chg ~ {v} + PHQ9_0", iv).fit(cov_type="cluster", cov_kwds={"groups": iv.counsellor})
    proc.append(dict(predictor=lab, b=o.params[v], lo=o.conf_int().loc[v, 0], hi=o.conf_int().loc[v, 1], p=o.pvalues[v], n=len(iv)))
pd.DataFrame(proc).to_csv(R + "h3_process_outcome.csv", index=False, encoding="utf-8-sig")

# ---------- 实施与过程汇总 ----------
cs = pd.read_csv(R + "counsellors.csv")
imp = dict(plans_total=len(pl), **{f"plans_{k}_pct": 100 * v for k, v in pl.decision.value_counts(normalize=True).items()},
           **{f"override_reason_{k}": int(v) for k, v in pl[pl.decision != "accepted"].reason.value_counts().items()},
           review_min_median=pl.review_min.median(), override_by_tier=pl.assign(o=pl.decision != "accepted").groupby("tier").o.mean().mul(100).round(1).to_dict(),
           override_by_week=pl.assign(o=pl.decision != "accepted").groupby("week").o.mean().mul(100).round(1).to_dict(),
           counsellor_override_range=[float(x) for x in pl.assign(o=pl.decision != "accepted").groupby("counsellor").o.mean().mul(100).agg(["min", "max"]).round(1)],
           practice_per_week_median=d[d.arm == 1].practice_per_week.median(), practice_per_week_iqr=[float(x) for x in d[d.arm == 1].practice_per_week.quantile([.25, .75])],
           peer_sessions_median=d[d.arm == 1].peer_sessions_attended.median(), engaged_pct=100 * d[d.arm == 1].comply.mean(),
           counsellor_min_int_median=d[d.arm == 1].counsellor_min_per_week.median(), counsellor_min_ctrl_median=d[d.arm == 0].counsellor_min_per_week.median(),
           csq_int=[d[d.arm == 1].CSQ8_1.mean(), d[d.arm == 1].CSQ8_1.std()], csq_ctrl=[d[d.arm == 0].CSQ8_1.mean(), d[d.arm == 0].CSQ8_1.std()],
           referred_int=int(d[d.arm == 1].referred_by_T1.sum()), referred_ctrl=int(d[d.arm == 0].referred_by_T1.sum()),
           counsellor_trust=[cs[cs.arm == 1].ai_trust.mean(), cs[cs.arm == 1].ai_trust.std()], counsellor_intention=[cs[cs.arm == 1].intention_to_use.mean(), cs[cs.arm == 1].intention_to_use.std()])
json.dump(imp, open(R + "h3_implementation.json", "w"), indent=1, default=float)
pd.set_option("display.width", 220)
print(res.round(3).to_string()); print(pd.DataFrame(sens).round(3).to_string()); print(pd.DataFrame(resp).round(2).to_string()); print(pd.DataFrame(sub).round(3).to_string())
print(pd.DataFrame(proc).round(3).to_string()); print(json.dumps(imp, indent=0, default=float)[:1500])
