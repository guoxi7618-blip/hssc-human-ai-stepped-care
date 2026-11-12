"""figure2 consort pptx"""
import json, pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

R = "D:/第五篇/论文_HSSC/results/"; OUT = "D:/第五篇/论文_HSSC/analysis/figures/Fig2_consort.pptx"
f = json.load(open(R + "screening_funnel.json")); d = pd.read_csv(R + "trial_wide.csv")
W, H = 7.09, 5.43
prs = Presentation(); prs.slide_width = Inches(W); prs.slide_height = Inches(H); s = prs.slides.add_slide(prs.slide_layouts[6])
rgb = RGBColor.from_string


def box(x, y, w, h, lines, fill="FFFFFF", line="333333", bold_first=False, align=PP_ALIGN.LEFT, size=6.3):
    b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    b.fill.solid(); b.fill.fore_color.rgb = rgb(fill); b.line.color.rgb = rgb(line); b.line.width = Pt(0.6); b.shadow.inherit = False
    tf = b.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.03)
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        r = p.add_run(); r.text = ln; ft = r.font; ft.name = "Arial"; ft.size = Pt(size); ft.color.rgb = rgb("222222"); ft.bold = bold_first and i == 0
    return b


def arrow(x1, y1, x2, y2):
    ff = s.shapes.build_freeform(Inches(x1), Inches(y1), scale=1.0); ff.add_line_segments([(Inches(x2), Inches(y2))], close=False)
    c = ff.convert_to_shape(); c.fill.background(); c.line.color.rgb = rgb("333333"); c.line.width = Pt(0.7)
    e = etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd")); e.set("type", "triangle"); e.set("w", "sm"); e.set("len", "sm")


def stage(y, h, label):                                           # 左侧阶段标签栏（CONSORT 惯例）
    b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.05), Inches(y), Inches(0.62), Inches(h))
    b.fill.solid(); b.fill.fore_color.rgb = rgb("DCE6F0"); b.line.color.rgb = rgb("8EA9C8"); b.line.width = Pt(0.5); b.shadow.inherit = False
    tf = b.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.margin_left = tf.margin_right = Inches(0.02)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label; r.font.name = "Arial"; r.font.size = Pt(6.4); r.font.bold = True; r.font.color.rgb = rgb("1F3B5A")


ca = f["counsellors_assessed"]; ex_l, ex_d = f["counsellors_excluded_leave"], f["counsellors_excluded_declined"]
box(2.3, 0.08, 2.75, 0.42, [f"Student affairs counsellors assessed", f"for eligibility (n = {ca})"], bold_first=False, align=PP_ALIGN.CENTER)
box(5.3, 0.08, 1.72, 0.42, [f"Excluded (n = {ex_l + ex_d})", f"  planned leave during trial (n = {ex_l})", f"  declined to participate (n = {ex_d})"])
arrow(5.05, 0.29, 5.3, 0.29)
box(2.3, 0.7, 2.75, 0.36, [f"Counsellors (clusters) randomised 1:1 (n = {ca - ex_l - ex_d})", "computer-generated, by independent statistician"], align=PP_ALIGN.CENTER)
arrow(3.67, 0.5, 3.67, 0.7)
XL, XR, BW = 0.78, 3.95, 3.07
arrow(3.1, 1.06, XL + BW / 2, 1.25); arrow(4.25, 1.06, XR + BW / 2, 1.25)
stage(0.08, 0.98, "Enrolment"); stage(1.25, 1.79, "Allocation"); stage(3.17, 1.43, "Follow-up"); stage(4.73, 0.62, "Analysis")
for x, arm, nm in ((XL, 1, "Human–AI collaborative stepped intervention"), (XR, 0, "Enhanced usual care")):
    fa = f["by_arm"][str(arm)]; g = d[d.arm == arm]; nclu = g.counsellor.nunique()
    box(x, 1.25, BW, 1.25, [f"Allocated to {nm}: {nclu} counsellors",
                           f"Students in counsellors' caseloads (n = {fa['caseload']})",
                           f"Completed online screening (n = {fa['screened']})",
                           f"  referred under the safety protocol, not eligible (high risk or item 9 positive; n = {fa['excluded_high_risk']})",
                           f"Eligible moderate-risk subclinical students (n = {fa['eligible']})",
                           f"Approached in random order (n = {fa['approached']}; second recruitment wave n = {fa.get('approached_wave2', 0)})",
                           f"  not reachable (n = {fa['not_reached']}); declined (n = {fa['declined']})",
                           f"Enrolled and assessed at baseline (n = {len(g)}; {len(g) // nclu} per counsellor)"], bold_first=True)
    eng = int(g.comply.sum()) if arm == 1 else None
    box(x, 2.62, BW, 0.42, ([f"Received intervention as allocated (n = {len(g)})", f"  adequate engagement, ≥60% of planned contacts (n = {eng}, {100 * eng / len(g):.0f}%)",
                            f"  escalated and referred during the intervention (n = {int(g.referred_by_T1.sum())})"] if arm == 1 else
                           [f"Received enhanced usual care (n = {len(g)})", "  psychoeducation messages at matched frequency",
                            f"  usual counselling access; referred via usual channels (n = {int(g.referred_by_T1.sum())})"]))
    arrow(x + BW / 2, 2.5, x + BW / 2, 2.62)
    m1 = int(g.missing_T1.sum()); m2 = int(g.missing_T2.sum())
    box(x, 3.17, BW, 0.48, [f"T1, week 12: assessed (n = {len(g) - m1}); lost to follow-up (n = {m1})",
                           "  reasons: coursework or examinations, could not be contacted, no longer interested"])
    arrow(x + BW / 2, 3.04, x + BW / 2, 3.17)
    rs = g[(g.missing_T2 == 1)].withdrew_reason.fillna("").replace("", "did not complete the assessment within the window").value_counts()
    box(x, 3.78, BW, 0.82, [f"T2, 6 months after the intervention: assessed (n = {len(g) - m2}); lost (n = {m2})"] +
        [f"  {k} (n = {v})" for k, v in rs.items()][:5])
    arrow(x + BW / 2, 3.65, x + BW / 2, 3.78)
    any_fu = int(((g.missing_T1 == 0) | (g.missing_T2 == 0)).sum())
    box(x, 4.73, BW, 0.62, [f"Analysed (intention to treat): n = {len(g)} students in {nclu} clusters",
                           f"  contributed ≥1 follow-up to the mixed model (n = {any_fu})",
                           "  missing outcomes handled by likelihood-based estimation (MAR);", "  multiple imputation and δ-adjusted pattern-mixture as sensitivity analyses"])
    arrow(x + BW / 2, 4.6, x + BW / 2, 4.73)
for sh in s.shapes:
    sp = sh._element.find(qn("p:spPr"))
    if sp is not None and sp.find(qn("a:effectLst")) is None: etree.SubElement(sp, qn("a:effectLst"))
prs.save(OUT); print("saved", OUT)
