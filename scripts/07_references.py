"""H6：生成 Springer basic（作者–年份）格式参考文献，并用 Crossref 核对 DOI。
1. 从 manuscript/*.tex 收集 \\citep/\\citet 的键；
2. 在三个 bib 库（第五篇旧库、RCT 库、论文_TLT/refs.bib）和本脚本的 EXTRA 中找 DOI；
3. 有 DOI 的从 Crossref 取元数据（缓存于 results/crossref_cache.json），按 Springer basic 格式排版；无 DOI 的用 MANUAL；
4. 输出 manuscript/refs_springer.tex（natbib 兼容的 thebibliography）与 results/h6_reference_check.csv。
"""
import re, json, os, glob, sys, time, urllib.request, urllib.parse, html
sys.stdout.reconfigure(encoding="utf-8")
M = "D:/第五篇/论文_HSSC/manuscript/"; R = "D:/第五篇/论文_HSSC/results/"
BIBS = ["D:/第五篇/参考文献/references.bib", "D:/第五篇/参考文献/人机协同分级干预RCT/references.bib", "D:/第五篇/论文_TLT/refs.bib"]
EXTRA = {"yoo2023hrver": "10.1038/s41597-023-02396-5", "li2024sbs": "10.1038/s41398-024-02812-3", "curran2012hybrid": "10.1097/MLR.0b013e3182408812",
         "campbell2012consort": "10.1136/bmj.e5661", "eysenbach2011consort": "10.2196/jmir.1923", "hoffmann2014tidier": "10.1136/bmj.g1687",
         "mundt2002wsas": "10.1192/bjp.180.5.461", "posner2011cssrs": "10.1176/appi.ajp.2011.10111704", "larsen1979csq": "10.1016/0149-7189(79)90094-6",
         "proctor2011outcomes": "10.1007/s10488-010-0319-7", "angrist1996iv": "10.1080/01621459.1996.10476902", "jacobson1991rci": "10.1037/0022-006X.59.1.12"}
MANUAL = {
    "moe2018guideline": ("Ministry of Education of the People's Republic of China", "2018", "Ministry of Education of the People's Republic of China (2018) Guidelines on mental health education for students in higher education institutions [in Chinese]. Ministry of Education, Beijing"),
    "moe2017counselor": ("Ministry of Education of the People's Republic of China", "2017", "Ministry of Education of the People's Republic of China (2017) Regulations on the development of counsellor teams in regular higher education institutions (Order No. 43) [in Chinese]. Ministry of Education, Beijing"),
    "moe2023action": ("Ministry of Education of the People's Republic of China et al.", "2023", "Ministry of Education of the People's Republic of China et al (2023) Special action plan for comprehensively strengthening and improving student mental health work in the new era (2023--2025) [in Chinese]. Ministry of Education, Beijing"),
    "pipl2021": ("Standing Committee of the National People's Congress", "2021", "Standing Committee of the National People's Congress (2021) Personal Information Protection Law of the People's Republic of China. Beijing"),
}


def parse_bib(path):
    s = open(path, encoding="utf-8").read(); out = {}
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", s, flags=re.S):
        key, body = m.group(1).strip(), m.group(2)
        dm = re.search(r"doi\s*=\s*\{([^}]*)\}", body, flags=re.I)
        out[key] = dm.group(1).strip() if dm else None
    for m in re.finditer(r"@\w+\{([^,]+),[^\n]*doi=\{([^}]*)\}", s):         # 单行条目
        out.setdefault(m.group(1).strip(), m.group(2).strip())
    return out


doimap = {}
for b in BIBS:
    for k, v in parse_bib(b).items(): doimap.setdefault(k, v)
doimap.update(EXTRA)
cited = []
for f in sorted(glob.glob(M + "*.tex")):
    if "refs_springer" in f: continue
    for m in re.finditer(r"\\cite[pt]?\*?(?:\[[^\]]*\])*\{([^}]*)\}", open(f, encoding="utf-8").read()):
        for k in m.group(1).split(","):
            k = k.strip()
            if k and k not in cited: cited.append(k)
cache_f = R + "crossref_cache.json"; cache = json.load(open(cache_f)) if os.path.exists(cache_f) else {}


def crossref(doi):
    if doi in cache: return cache[doi]
    u = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    req = urllib.request.Request(u, headers={"User-Agent": "reference-check/1.0 (academic manuscript preparation)"})
    for i in range(3):
        try:
            j = json.load(urllib.request.urlopen(req, timeout=40))["message"]; cache[doi] = j; json.dump(cache, open(cache_f, "w")); return j
        except urllib.error.HTTPError as e:
            if e.code == 404: cache[doi] = None; return None
            time.sleep(3)
        except Exception: time.sleep(3)
    return None


def initials(given):
    parts = re.split(r"[\s\-]+", given.replace(".", " ").strip())
    return "".join(p[0] for p in parts if p)


def tex_escape(t):
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    for a, b in (("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#")): t = t.replace(a, b)
    for a_, b_ in (("‐", "-"), ("‑", "-"), ("−", "-"), ("’", "'"), ("‘", "`"), ("“", "``"), ("”", "''"), (" ", " ")): t = t.replace(a_, b_)
    return t.replace("–", "--").replace("—", "---")


items, rows = [], []
for k in cited:
    if k in MANUAL:
        au, yr, txt = MANUAL[k]; items.append((au, yr, k, rf"\bibitem[{{{au}}}({yr})]{{{k}}} {txt}")); rows.append(dict(key=k, doi="", status="manual")); continue
    doi = doimap.get(k)
    if not doi: rows.append(dict(key=k, doi="", status="NO_DOI_FOUND")); continue
    j = crossref(doi)
    if not j: rows.append(dict(key=k, doi=doi, status="DOI_NOT_RESOLVED")); continue
    auth = [a for a in j.get("author", []) if "family" in a]
    names = [f"{a['family']} {initials(a.get('given', ''))}".strip() for a in auth]
    if not names and j.get("author"): names = [j["author"][0].get("name", "")]
    if len(names) > 3: au_txt = ", ".join(names[:3]) + " et al"
    else: au_txt = ", ".join(names)
    yr = str((j.get("published-print") or j.get("published-online") or j.get("issued"))["date-parts"][0][0])
    title = tex_escape(j.get("title", [""])[0]); title = title[0] + title[1:] if title else title
    jn = tex_escape((j.get("container-title") or [""])[0]); vol = j.get("volume", ""); iss = j.get("issue", ""); pg = j.get("page", "") or j.get("article-number", "")
    typ = j.get("type", "")
    src = f"{jn} {vol}" + (f"({iss})" if iss else "") + (f":{pg.replace('-', '--')}" if pg else "") if typ.startswith("journal") else (jn or j.get("publisher", ""))
    txt = f"{tex_escape(au_txt)} ({yr}) {title}. {src.strip()}. \\url{{https://doi.org/{doi}}}"
    fam = [a["family"] for a in auth]
    lab = (fam[0] if len(fam) == 1 else f"{fam[0]} and {fam[1]}" if len(fam) == 2 else f"{fam[0]} et~al.") if fam else names[0]
    items.append((fam[0] if fam else names[0], yr, k, rf"\bibitem[{{{tex_escape(lab)}}}({yr})]{{{k}}} {txt}"))
    rows.append(dict(key=k, doi=doi, status="OK", crossref_title=j.get("title", [""])[0][:90], year=yr))
items.sort(key=lambda x: (x[0].lower(), x[1]))
open(M + "refs_springer.tex", "w", encoding="utf-8").write("\\begin{thebibliography}{%d}\n" % len(items) + "\n\n".join(i[3] for i in items) + "\n\\end{thebibliography}\n")
import pandas as pd
pd.DataFrame(rows).to_csv(R + "h6_reference_check.csv", index=False, encoding="utf-8-sig")
print(pd.DataFrame(rows).status.value_counts().to_dict()); print([r for r in rows if r["status"] not in ("OK", "manual")])
