"""H12：生成 Word 版稿件（英文、中文）。引用由 pandoc citeproc 按 Springer basic 作者–年份格式生成。
1. 由 Crossref 缓存与手工条目生成 CSL-JSON；
2. 展开 \\input，去掉 thebibliography，换成 pandoc 的参考文献占位；
3. pandoc --citeproc --csl springer-basic-author-date.csl → docx。
"""
import json, re, os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
B = "D:/第五篇/论文_HSSC/"; M = B + "manuscript/"; R = B + "results/"; CSL = B + "analysis/csl/springer-basic-author-date.csl"
OUT = B + "submission/"
sys.path.insert(0, B + "analysis/scripts")
cache = json.load(open(R + "crossref_cache.json"))
chk = __import__("pandas").read_csv(R + "h6_reference_check.csv")
items = []
for r in chk.itertuples():
    if r.status == "OK":
        c = cache[r.doi]; first = lambda v: (v[0] if isinstance(v, list) and v else v) or ""
        TYPE = {"journal-article": "article-journal", "proceedings-article": "paper-conference", "posted-content": "article", "book-chapter": "chapter", "dataset": "dataset"}
        dp = (c.get("published-print") or c.get("published-online") or c.get("issued"))["date-parts"]
        j = {"id": r.key, "type": TYPE.get(c.get("type", ""), "article-journal"), "title": first(c.get("title")), "container-title": first(c.get("container-title")),
             "volume": c.get("volume", ""), "issue": c.get("issue", ""), "page": c.get("page", "") or c.get("article-number", ""), "DOI": r.doi,
             "publisher": c.get("publisher", ""), "issued": {"date-parts": [dp[0][:1]]},
             "author": [{"family": a["family"], "given": a.get("given", "")} if "family" in a else {"literal": a.get("name", "")} for a in c.get("author", [])]}
        items.append({k: v for k, v in j.items() if v not in ("", [], None)})
MAN = {"moe2018guideline": ("Ministry of Education of the People's Republic of China", 2018, "Guidelines on mental health education for students in higher education institutions [in Chinese]"),
       "moe2017counselor": ("Ministry of Education of the People's Republic of China", 2017, "Regulations on the development of counsellor teams in regular higher education institutions (Order No. 43) [in Chinese]"),
       "moe2023action": ("Ministry of Education of the People's Republic of China et al.", 2023, "Special action plan for comprehensively strengthening and improving student mental health work in the new era (2023–2025) [in Chinese]"),
       "pipl2021": ("Standing Committee of the National People's Congress", 2021, "Personal Information Protection Law of the People's Republic of China")}
for k, (au, yr, ti) in MAN.items():
    items.append({"id": k, "type": "document", "author": [{"literal": au}], "issued": {"date-parts": [[yr]]}, "title": ti, "publisher": "Beijing"})
json.dump(items, open(R + "refs_csl.json", "w", encoding="utf-8"), ensure_ascii=False)


def flatten(main, tables_zh=False):
    s = open(M + main, encoding="utf-8").read()
    def inc(m):
        f = m.group(1); f = f if f.endswith(".tex") else f + ".tex"
        if "refs_springer" in f: return "\n\\section*{" + ("参考文献" if tables_zh else "References") + "}\n::REFS::\n"
        return open(M + f, encoding="utf-8").read()
    s = re.sub(r"\{\\linespread\{1.0\}\\small\s*\\input\{([^}]*)\}\s*\}", inc, s)
    s = re.sub(r"\{\\singlespacing\\small\s*\\input\{([^}]*)\}\s*\}", inc, s)
    s = re.sub(r"\\input\{([^}]*)\}", inc, s)
    s = s.replace("\\linenumbers", "").replace("\\doublespacing", "")
    s = s.replace("::REFS::", "\\hypertarget{refs}{}")
    return s


for main, out, zh in (("main_hssc.tex", "01_Manuscript/Manuscript_HSSC.docx", False), ("main_zh_hssc.tex", "04_中文版/论文_中文版.docx", True)):
    tmp = M + "_flat_" + main
    open(tmp, "w", encoding="utf-8").write(flatten(main, zh))
    cmd = ["pandoc", tmp, "-f", "latex", "-t", "docx", "--citeproc", "--csl", CSL, "--bibliography", R + "refs_csl.json", "-M", "link-citations=false", "-o", OUT + out]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=M)
    print(out, "exit", r.returncode, r.stderr[-600:])
