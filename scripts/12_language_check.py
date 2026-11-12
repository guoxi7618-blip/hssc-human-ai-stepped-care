"""H14：英文稿术语一致性与重复表述核查。"""
import re, collections, sys
sys.stdout.reconfigure(encoding="utf-8")
M = "D:/第五篇/论文_HSSC/manuscript/"
s = open(M + "part1_front_intro_methods.tex", encoding="utf-8").read() + open(M + "part2_results_discussion.tex", encoding="utf-8").read()
b = s[s.index(r"\section*{Introduction}"):s.index(r"\section*{Data availability}")]
t = re.sub(r"\\cite[pt]?\{[^}]*\}", "", b); t = re.sub(r"\$[^$]*\$", "", t); t = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", "", t); t = re.sub(r"[{}~]", " ", t)
w = re.findall(r"[A-Za-z][A-Za-z\-']+", t.lower())
for word in ["whereas", "however", "therefore", "also", "only", "rather than", "may", "might", "which", "this", "these", "suggests", "indicate", "clearly", "important", "notably"]:
    print(word, len(re.findall(r"\b" + word + r"\b", t.lower())), end="; ")
print()
STOP = {"the", "of", "and", "in", "to", "a", "for", "with", "on", "at", "by", "from", "that", "as", "or", "was", "were", "is", "are", "be", "it"}
for n in (3, 4):
    c = collections.Counter(tuple(w[i:i + n]) for i in range(len(w) - n))
    print(n, [(" ".join(k), v) for k, v in c.most_common(300) if v >= 4 and not set(k) <= STOP][:22])
for pat in [r"counselor", r"program\b", r"randomized", r"behavior\b", r"crisis level", r"risk level", r"control group", r"control arm", r"intervention arm",
            r"\bAI\b", r"artificial intelligence", r"heart rate variability", r"\bHRV\b", r"psychological education", r"four-level network", r"override", r"overrid"]:
    print(f"{pat}: {len(re.findall(pat, b))}", end=" | ")
print()
sents = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", t)); st = collections.Counter(" ".join(x.split()[:2]).lower() for x in sents if len(x.split()) > 3)
print("sentence starts:", [(k, v) for k, v in st.most_common(12) if v >= 3])
for m in re.finditer(r"[^.]{0,80}\b(rather than|whereas|only)\b[^.]{0,60}", t): print("  ·", m.group(0).strip()[:150])
