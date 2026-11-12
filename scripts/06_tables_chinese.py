"""H11：由英文表格生成中文表题、表头和注释（表内数字不变）。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
M = "D:/第五篇/论文_HSSC/manuscript/"
REP = {
 "table1_model.tex": [
  ("Tiering rules, content and division of labour in the human--AI collaborative stepped intervention (TIDieR summary)", "人机协同分级干预的分层规则、内容与分工（TIDieR 摘要）"),
  ("Tier & Entry criterion & Content and dose (12 weeks) & Proposed by & Decided and delivered by", "层级 & 进入标准 & 内容与剂量（12 周） & 由谁提出 & 由谁决定与实施"),
  ("Moderate &", "中度 &"), ("Elevated &", "较高 &"), ("High &", "高 &"), ("Monitoring &", "监测 &"), ("Plan review &", "方案审核 &"),
  ("HRV, heart rate variability; RMSSD, root mean square of successive differences. Control clusters (enhanced usual care) receive the same assessments and psychoeducation messages at matched frequency, retain access to the counselling centre and follow the same safety protocol.",
   "HRV：心率变异性；RMSSD：相邻 RR 间期差值的均方根。对照组（强化常规照护）完成相同评估，以相同频率收到心理健康科普信息，可正常使用心理咨询中心，并遵循相同的安全规程。表内条目保留英文原文。")],
 "table2_baseline.tex": [
  ("Baseline characteristics of students by trial arm", "两组学生的基线特征"), ("Characteristic &", "特征 &"),
  ("Intervention ($n=90$; 10 clusters)", "干预组（$n=90$；10 个整群）"), ("Enhanced usual care ($n=90$; 10 clusters)", "强化常规照护组（$n=90$；10 个整群）"),
  ("Age, years, mean (SD)", "年龄（岁），均值（SD）"), ("Women, n (\\%)", "女性，n（\\%）"), ("Year of study, n (\\%)", "年级，n（\\%）"),
  ("\\quad Year 1", "\\quad 大一"), ("\\quad Year 2", "\\quad 大二"), ("\\quad Year 3", "\\quad 大三"), ("Rural origin, n (\\%)", "农村生源，n（\\%）"),
  ("Only child, n (\\%)", "独生子女，n（\\%）"), ("Elevated tier at baseline, n (\\%)", "基线为较高层级，n（\\%）"), ("Symptom profile, n (\\%)", "症状类型，n（\\%）"),
  ("\\quad Depression-predominant", "\\quad 抑郁为主型"), ("\\quad Mixed", "\\quad 混合型"), ("\\quad Anxiety-predominant", "\\quad 焦虑为主型"),
  ("PHQ-9, mean (SD)", "PHQ-9，均值（SD）"), ("GAD-7, mean (SD)", "GAD-7，均值（SD）"), ("WSAS, mean (SD)", "WSAS，均值（SD）"),
  ("Resting ln RMSSD, mean (SD)", "静息 ln RMSSD，均值（SD）"), ("Students per counsellor", "每名辅导员的学生数"),
  ("Values are n (\\%) or mean (SD). In line with CONSORT, baseline differences are not tested for significance. PHQ-9, Patient Health Questionnaire-9; GAD-7, Generalized Anxiety Disorder-7; WSAS, Work and Social Adjustment Scale; RMSSD, root mean square of successive differences. Resting HRV was missing for students whose recording failed quality checks.",
   "数值为 n（\\%）或均值（SD）。按 CONSORT 要求，不对基线差异做显著性检验。HRV 记录未通过质量检查的学生缺失静息 HRV。")],
 "table3_outcomes.tex": [
  ("Primary and secondary outcomes (intention to treat)", "主要与次要结局（意向性分析）"),
  ("Outcome & Time & \\multicolumn{2}{c}{Intervention} & \\multicolumn{2}{c}{Enhanced usual care} & Adjusted difference [95\\% CI] & $P$ ($P_{\\mathrm{Holm}}$)",
   "结局 & 时点 & \\multicolumn{2}{c}{干预组} & \\multicolumn{2}{c}{强化常规照护组} & 调整差 [95\\% CI] & $P$（$P_{\\mathrm{Holm}}$）"),
  (" & & $n$ & Mean (SD) & $n$ & Mean (SD) & (standardised) & ", " & & $n$ & 均值（SD） & $n$ & 均值（SD） & （标准化差） & "),
  ("Risk level (ordinal)", "风险等级（有序）"),
  ("Means are observed values. Adjusted differences (intervention minus control) come from linear mixed models with fixed effects for arm, time, arm $\\times$ time, baseline score, baseline tier and sex, and random intercepts for counsellor and student; $t$ distribution with 18 degrees of freedom. Standardised differences divide by the pooled SD at the same time point. Risk level: ordinal GEE, odds ratio for a higher risk level (OR $<$ 1 favours the intervention). Holm adjustment across the four secondary outcomes at T1.",
   "均值为观测值。调整差（干预减对照）来自线性混合模型：固定效应为组别、时间、组别 $\\times$ 时间、基线得分、基线层级和性别，随机效应为辅导员和学生随机截距；推断使用自由度 18 的 $t$ 分布。标准化差以同一时点合并 SD 标准化。风险等级：有序 GEE，风险等级更高的比值比（OR $<$ 1 有利于干预）。Holm 校正针对 T1 的四个次要结局。")],
}
for f, reps in REP.items():
    s = open(M + f, encoding="utf-8").read()
    for a, b in reps:
        if a not in s: print("MISSING in", f, ":", a[:50])
        s = s.replace(a, b)
    open(M + f.replace(".tex", "_zh.tex"), "w", encoding="utf-8").write(s)
print("zh tables written")
