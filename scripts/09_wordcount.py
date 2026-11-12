"""H9：统计正文各部分字数（不含摘要、表格、图注、参考文献、声明）。"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
M = "D:/第五篇/论文_HSSC/manuscript/"


def words(t):
    t = re.sub(r"(?<!\\)%.*", "", t)
    t = re.sub(r"\\cite[pt]?\{[^}]*\}", "CIT", t)
    t = re.sub(r"\\(begin|end|label|ref)\{[^}]*\}", " ", t)
    t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", t)
    t = re.sub(r"[{}$~]", " ", t)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9\-\.'’]*", t))


p1 = open(M + "part1_front_intro_methods.tex", encoding="utf-8").read(); p2 = open(M + "part2_results_discussion.tex", encoding="utf-8").read()
cut = lambda s, a, b: s[s.index(a):s.index(b)] if b else s[s.index(a):]
parts = [("Introduction", cut(p1, r"\section*{Introduction}", r"\section*{The intervention model}")),
         ("Intervention model", cut(p1, r"\section*{The intervention model}", r"\section*{Methods}")),
         ("Methods", cut(p1, r"\section*{Methods}", None)),
         ("Results", cut(p2, r"\section*{Results}", r"\section*{Discussion}")),
         ("Discussion", cut(p2, r"\section*{Discussion}", r"\section*{Conclusion")),
         ("Conclusion", cut(p2, r"\section*{Conclusion", r"\section*{Data availability}"))]
tot = 0
for n, t in parts:
    w = words(t); tot += w; print(f"{n:20s}{w:6d}")
print(f"{'Main text total':20s}{tot:6d}")
