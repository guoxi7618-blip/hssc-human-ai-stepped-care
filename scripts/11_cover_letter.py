"""cover letter"""
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
sys.stdout.reconfigure(encoding="utf-8")
OUT = "D:/第五篇/论文_HSSC/submission/07_Cover_Letter/Cover_Letter_HSSC.docx"
import os; os.makedirs(os.path.dirname(OUT), exist_ok=True)
d = Document()
for s in d.sections: s.left_margin = s.right_margin = Cm(2.5); s.top_margin = s.bottom_margin = Cm(2.2)
st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
def P(t, bold=False, italic=False, color=None, after=6):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = bold; r.italic = italic
    if color: r.font.color.rgb = RGBColor.from_string(color)
    p.paragraph_format.space_after = Pt(after); return p
P("12 November 2026")
P("The Editors\nHumanities and Social Sciences Communications")
P("Dear Editors,")
P("We submit the manuscript “Human–AI collaborative stepped care in a Chinese university student support system: a cluster randomised hybrid effectiveness–implementation trial” for consideration as an Article in Humanities and Social Sciences Communications.")
P("Universities increasingly use digital and artificial intelligence (AI) tools to support student mental health, but these tools are usually evaluated on research platforms rather than inside the organisations that actually support students. In China, that organisation is a four-level network in which student affairs counsellors (fudaoyuan), who are educators rather than clinicians, carry first-line responsibility. The manuscript reports a cluster randomised trial in which an algorithm proposed risk tiers and support plans and counsellors accepted, modified or rejected them. Twenty counsellors and 180 students took part.")
P("The main findings are as follows:")
for t in ["The intervention reduced depressive symptoms, anxiety symptoms and the blinded risk level over 12 weeks; the difference in depressive symptoms narrowed and was no longer significant six months later.",
          "Counsellors overrode one-third of algorithmic plans, more often for students at higher risk and as they came to know their students, mainly on the basis of information the algorithm did not hold. Override rates varied widely across counsellors.",
          "Heart rate variability biofeedback was rarely practised and resting heart rate variability did not change, which limits the role of physiological data in this setting.",
          "Counsellor time (about 20 minutes per student per week), rather than technology, was the binding constraint on scaling."]:
    p = d.add_paragraph(t, style="List Bullet"); p.paragraph_format.space_after = Pt(3)
P("We believe the work suits the journal’s readership because its central questions concern the social organisation of care: how decision authority is divided between people and algorithms, how a support system embedded in education distributes responsibility, and what this means for policy on student mental health. The manuscript also addresses ethical questions of labelling, consent and accountability that arise when sensitive data enter an educational hierarchy.")
P("Declarations. The manuscript is original, has not been published and is not under consideration elsewhere. All authors have approved the submission. Before enrolment, the trial was approved by the institutional ethics committee of the university where it was conducted and preregistered on the Open Science Framework. The authors declare no competing interests. Claude (Anthropic) was used to polish the language of the manuscript, as stated in the manuscript.")
P("Thank you for considering our manuscript.")
P("Yours sincerely,\n\nYindong Dong (corresponding author)\nAnhui Agricultural University, Hefei, China\ndongyindong66@163.com\non behalf of all authors")
d.save(OUT); print("saved", OUT)
