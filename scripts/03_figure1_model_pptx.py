"""Fig. 1：人机协同分级干预模式及其与高校四级网络的对接（python-pptx 原生形状，可编辑；PowerPoint 导出矢量 PDF）。
尺寸：双栏 180 mm（7.09 in）。字体 Arial。输出 figures/Fig1_model.pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

OUT = "D:/第五篇/论文_HSSC/analysis/figures/Fig1_model.pptx"
W, H = 7.09, 4.32
prs = Presentation(); prs.slide_width = Inches(W); prs.slide_height = Inches(H)
s = prs.slides.add_slide(prs.slide_layouts[6])
DARK = RGBColor(0x2B, 0x2B, 0x2B); GREY = RGBColor(0x5A, 0x5A, 0x5A)
rgb = RGBColor.from_string
# 角色配色（与四级网络框一致）
ROLE = {"centre": "7B3294", "college": "C2410C", "class": "1F78B4", "dorm": "33A02C", "algo": "4D4D4D"}


def box(x, y, w, h, fill, line="2B2B2B", lw=0.6, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.07):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: sh.adjustments[0] = adj
    if fill is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    sh.line.color.rgb = rgb(line); sh.line.width = Pt(lw); sh.shadow.inherit = False
    return sh


def write(sh, lines, anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT, ml=0.06):
    """lines: list of (text, size, bold, colour_hex or None, italic)"""
    tf = sh.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(ml); tf.margin_top = Inches(0.035); tf.margin_bottom = Inches(0.02)
    for i, ln in enumerate(lines):
        t, size, bold, col, it = (list(ln) + [None, None, None, None])[:5]
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align; p.space_before = Pt(0.6)
        for j, seg in enumerate(t.split("**")):            # **粗体** 片段
            if not seg: continue
            r = p.add_run(); r.text = seg; f = r.font; f.name = "Arial"; f.size = Pt(size or 6.2)
            f.bold = bool(bold) or (j % 2 == 1); f.italic = bool(it); f.color.rgb = rgb(col) if col else DARK
    return sh


def text(x, y, w, h, lines, **kw):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); return write(tb, lines, **kw)


def line(pts, color="2B2B2B", width=0.8, dash=False, head=True, both=False):
    ff = s.shapes.build_freeform(Inches(pts[0][0]), Inches(pts[0][1]), scale=1.0)
    ff.add_line_segments([(Inches(a), Inches(b)) for a, b in pts[1:]], close=False)
    c = ff.convert_to_shape(); c.fill.background(); c.line.color.rgb = rgb(color); c.line.width = Pt(width); c.shadow.inherit = False
    ln = c.line._get_or_add_ln()
    if dash: etree.SubElement(ln, qn("a:prstDash")).set("val", "dash")
    if both: e = etree.SubElement(ln, qn("a:headEnd")); e.set("type", "triangle"); e.set("w", "sm"); e.set("len", "sm")
    if head: e = etree.SubElement(ln, qn("a:tailEnd")); e.set("type", "triangle"); e.set("w", "sm"); e.set("len", "sm")
    return c


def tag(x, y, w, label, role):
    t = box(x, y, w, 0.15, ROLE[role], line=ROLE[role], lw=0.4, adj=0.5)
    write(t, [(label, 5.2, True, "FFFFFF")], anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER, ml=0.02)
    t.text_frame.margin_top = t.text_frame.margin_bottom = 0


# ------------------------- 面板 a：四级网络 -------------------------
text(0.06, 0.04, 1.6, 0.2, [("a  Four-level support network", 7.2, True)])
NX, NW = 0.08, 1.48
net = [("University counselling centre", "professional assessment, counselling, crisis response", "centre", "F3E8F7"),
       ("School (college)", "student affairs counsellors (fudaoyuan): follow-up talks, case ledger", "college", "FDEBDD"),
       ("Class", "class mental-health committee members: peer support, observation", "class", "E1EDF7"),
       ("Dormitory", "dormitory liaisons: early signs, reporting", "dorm", "E2F2DF")]
ny = 0.36; ng = 0.17; nh = (0.36 + 0.86 + 0.16 + 0.14 + 1.06 + 0.2 - ny - 3 * ng) / 4   # 与右侧 FY 底边对齐
for i, (t1, t2, role, fill) in enumerate(net):
    y = ny + i * (nh + ng)
    b = box(NX, y, NW, nh, fill, line=ROLE[role], lw=0.9)
    write(b, [(t1, 6.6, True, ROLE[role]), (t2, 5.6)])
    if i < 3:
        line([(NX + 0.38, y + nh + ng - 0.01), (NX + 0.38, y + nh + 0.01)], color="5A5A5A", width=0.7)           # 上报 ↑
        line([(NX + NW - 0.38, y + nh + 0.01), (NX + NW - 0.38, y + nh + ng - 0.01)], color="5A5A5A", width=0.7)  # 转介/指导 ↓
text(NX, ny + 4 * nh + 3 * ng + 0.03, NW, 0.2, [("↑ reports    ↓ guidance and referral", 5.4, False, "5A5A5A", True)], align=PP_ALIGN.CENTER)

# ------------------------- 面板 b：人机协同闭环 -------------------------
X0 = 1.78
text(X0, 0.04, 5.2, 0.2, [("b  Human–AI collaborative stepped intervention (12 weeks)", 7.2, True)])
TY, TH, TW, TG = 0.36, 0.86, 1.62, 0.17
xs = [X0 + i * (TW + TG) for i in range(3)]
b1 = box(xs[0], TY, TW, TH, "FFFFFF", lw=0.8)
write(b1, [("**1 Data**", 6.6), ("PHQ-9, GAD-7 (online, biweekly)", 5.7), ("resting HRV, 5 min (wearable)", 5.7), ("student goals and context notes", 5.7)])
b2 = box(xs[1], TY, TW, TH, "F2F2F2", lw=0.8)
write(b2, [("**2 Algorithm proposes**", 6.6), ("transparent rules → risk tier", 5.7), ("draft plan: modules, contact frequency", 5.7), ("flags discordant signals", 5.7)])
tag(xs[1] + TW - 0.62, TY + TH - 0.2, 0.56, "rule engine", "algo")
b3 = box(xs[2], TY, TW, TH, "FFF7F0", line=ROLE["college"], lw=1.0)
write(b3, [("**3 Counsellor decides**", 6.6, None, ROLE["college"]), ("reviews before seeing the draft", 5.7), ("accept / modify / reject", 5.7), ("reason logged (override log)", 5.7)])
tag(xs[2] + TW - 0.62, TY + TH - 0.2, 0.56, "fudaoyuan", "college")
for i in range(2): line([(xs[i] + TW + 0.01, TY + TH / 2), (xs[i + 1] - 0.01, TY + TH / 2)], width=0.9)

# 下发总线
BY = TY + TH + 0.16
line([(xs[2] + TW / 2, TY + TH + 0.01), (xs[2] + TW / 2, BY)], width=0.9, head=False)
line([(xs[0] + TW / 2, BY), (xs[2] + TW / 2, BY)], width=0.9, head=False)
text(xs[1] - 0.05, BY - 0.15, TW + 0.1, 0.14, [("4 delivery by tier", 5.6, False, "5A5A5A", True)], align=PP_ALIGN.CENTER)
RY, RH = BY + 0.14, 1.06
tiers = [("Low risk", "E5F5E0", "2E7D32", ["self-guided HRV biofeedback (slow breathing, 2 × 10 min/day)", "psychoeducation micro-lessons", "weekly app check-in"], [("algorithm", "algo")]),
         ("Moderate risk", "FFF4D6", "B26B00", ["peer support group (6 sessions)", "counsellor talks (4 sessions)", "personalised regulation plan incl. biofeedback"], [("class peers", "class"), ("fudaoyuan", "college")]),
         ("High risk", "FDE2E1", "B71C1C", ["same-day professional assessment", "referral to counselling centre", "key-attention ledger; dormitory watch"], [("centre", "centre"), ("dorm", "dorm")])]
for i, (nm, fill, col, items, tags) in enumerate(tiers):
    line([(xs[i] + TW / 2, BY), (xs[i] + TW / 2, RY - 0.01)], width=0.9)
    b = box(xs[i], RY, TW, RH, fill, line=col, lw=1.0)
    write(b, [(nm, 6.8, True, col)] + [("• " + it, 5.7) for it in items])
    tx = xs[i] + 0.06
    for lab, role in tags:
        w_ = 0.12 + 0.052 * len(lab); tag(tx, RY + RH - 0.21, w_, lab, role); tx += w_ + 0.05
# 升降级
for i in range(2):
    xm = xs[i] + TW + TG / 2; yy = RY + RH / 2
    line([(xs[i] + TW + 0.01, yy), (xs[i + 1] - 0.01, yy)], color="7A7A7A", width=0.8, both=True)

# 监测反馈回路（虚线，从三级底部回到 1 Data）
FY = RY + RH + 0.2
for i in range(3): line([(xs[i] + TW / 2, RY + RH + 0.01), (xs[i] + TW / 2, FY)], color="5A5A5A", width=0.8, dash=True, head=False)
line([(xs[2] + TW / 2, FY), (X0 - 0.08, FY), (X0 - 0.08, TY + TH / 2), (xs[0] - 0.01, TY + TH / 2)], color="5A5A5A", width=0.9, dash=True)
text(xs[0] + 0.1, FY + 0.02, 5.0, 0.14, [("5 biweekly monitoring → escalate ⇄ step down (re-tiering); outcomes and override logs refine the rules", 5.6, False, "5A5A5A", True)])

# ------------------------- 面板 c：治理条 -------------------------
GY = FY + 0.26
g = box(0.08, GY, W - 0.16, 0.36, "F7F7F7", line="9E9E9E", lw=0.6)
write(g, [("**c  Safeguards**   separate consent for physiological data · processing on the student's device · role-based access (instructors see no individual data) · "
           "item-9 or high-risk signal → same-day assessment by counselling-centre staff; the algorithm never assigns or lowers a crisis level · "
           "independent safety officer · data deleted at graduation or on request", 5.7)], anchor=MSO_ANCHOR.MIDDLE)
for sh in s.shapes:
    sp = sh._element.find(qn("p:spPr"))
    if sp is not None and sp.find(qn("a:effectLst")) is None: etree.SubElement(sp, qn("a:effectLst"))
prs.slide_height = Inches(GY + 0.42)
prs.save(OUT); print("saved", OUT, "GY", round(GY, 2))
