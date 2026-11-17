"""Builds FedFACS_Replacements_7_8.docx (cohort size; aggregation weights): Before/After with locations, declarations, evidence."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docx
import pypandoc
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

import build_final56 as B

P, WORK, BS = B.P, B.WORK, B.BS
OUTF = os.path.join(P, "FedFACS_Replacements_7_8.docx")
ORIG, REV = B.ORIG, B.REV


def to_eol(text, start):
    i = text.index(start)
    j = text.find("\n", i)
    return text[i:j if j >= 0 else len(text)]


def seg(text, start, end):
    i = text.index(start)
    j = text.index(end, i) + len(end)
    return text[i:j]


def upto_eol(text, start, last):
    i = text.index(start)
    k = text.index(last, i)
    j = text.find(chr(10), k)
    return text[i:j if j >= 0 else len(text)]


EQ = lambda lab: BS + "label{" + lab + "}\n" + BS + "end{equation}"
EDITS = [
    dict(rep=7, title="Section 4.2: cohort size, Eqs. (15)-(16) and the paragraph below them", loc="Section 4.2, server side (original line %d)",
         orig=upto_eol(ORIG, "On the server-side, it receives fitness scores", "When $" + BS + "rho$ indicates sharp improvement"),
         rev=upto_eol(REV, "On the server-side, it receives fitness scores", "A large $" + BS + "rho^{t-1}$ means fast progress"),
         onums=["15", "16"], rnums=["15", "16"], at=("On the server-side, it receives fitness scores", ORIG)),
    dict(rep=7, title="Section 5.1: the claim on fewer clients per round", loc="Section 5.1, ablation study (original line %d)",
         orig=seg(ORIG, "Moreover, introducing dynamic cohort sizing", "per training round."),
         rev=seg(REV, "Moreover, dynamic cohort sizing (FedFACS-A2)", "distance between the two bounds (Table~" + BS + "ref{tab:cohort})."),
         onums=[], rnums=[], at=("Moreover, introducing dynamic cohort sizing", ORIG)),
    dict(rep=8, title="Contributions: the aggregation item", loc="Section 1, list of contributions (original line %d)",
         orig=to_eol(ORIG, BS + "item Stability-weighted aggregation method"), rev=to_eol(REV, BS + "item Normalised aggregation weights"),
         onums=[], rnums=[], at=(BS + "item Stability-weighted aggregation method", ORIG)),
    dict(rep=8, title="Section 4.1: relation between the objective, the selection and the aggregation", loc="Section 4.1, last paragraph (original line %d)",
         orig=to_eol(ORIG, "After selecting the most contributing clients"), rev=to_eol(REV, "The next global model is the weighted average"),
         onums=[], rnums=[], at=("After selecting the most contributing clients", ORIG)),
    dict(rep=8, title="Section 4.2: aggregation weights, Eqs. (17)-(18)", loc="Section 4.2, after the cohort size (original line %d)",
         orig=seg(ORIG, "Once the selected clients submit their local updates", EQ("eq:stability_norm")),
         rev=seg(REV, "Once the selected clients submit their local updates", "does not contribute to that round's aggregate."),
         onums=["17", "18"], rnums=["17", "18"], at=("Once the selected clients submit their local updates", ORIG)),
    dict(rep=8, title="Section 4.2: closing paragraph on the aggregation", loc="Section 4.2 (original line %d)",
         orig=to_eol(ORIG, "Furthermore, the aggregation process incorporates"), rev=to_eol(REV, "Furthermore, the aggregation weights of Eq."),
         onums=[], rnums=[], at=("Furthermore, the aggregation process incorporates", ORIG)),
    dict(rep=8, title="Section 5.1: the claim on the full model", loc="Section 5.1, ablation study (original line %d)",
         orig=seg(ORIG, "Furthermore, incorporating the adaptive stability-weighted aggregation", "fewer training rounds."),
         rev=seg(REV, "Furthermore, the full FedFACS model replaces", "more stable final model."),
         onums=[], rnums=[], at=("Furthermore, incorporating the adaptive stability-weighted aggregation", ORIG)),
]

for _title, _loc, _ko, _kr in [
    ("Abstract: the aggregation sentence", "Abstract (original line %d)", "we propose a stability-weighted aggregation method", "we propose a nonnegative normalised aggregation family"),
    ("Introduction: the stability score and the aggregation", "Section 1, contributions paragraph (original line %d)", "the client contributions are quantified using stability score", "the client contributions are quantified by a stability score"),
    ("Section 5 discussion: effect of the aggregation", "Section 5, fairness discussion (original line %d)", "the stability-weighted aggregation strategy improves accuracy", "the sample-count aggregation keeps the global model stable"),
    ("Section 5 discussion: the full model", "Section 5, closing paragraph of the discussion (original line %d)", "and adaptive stability-weighted aggregation", "and normalised aggregation"),
    ("Section 5: summary of the ablation", "Section 5, summary paragraph (original line %d)", "adaptive cohort sizing, and stability-weighted aggregation", "normalised nonnegative aggregation weights"),
    ("Conclusion: the aggregation sentence", "Section 6, Conclusion (original line %d)", "Moreover, stability-aware aggregation is employed", "Moreover, the aggregation uses nonnegative normalised weights"),
]:
    EDITS.append(dict(rep=8, title=_title, loc=_loc, orig=B.sentence(ORIG, _ko), rev=B.sentence(REV, _kr), onums=[], rnums=[], at=(_ko, ORIG)))

HEAD = r"""
::: {custom-style="BA-Title"}
FedFACS: Replacements 7 and 8 (cohort size; aggregation weights)
:::

::: {custom-style="BA-Note"}
Scope. Replacement 7 covers the cohort-size rule (Eqs. (15)-(16)), its bounds and the claim on fewer clients per round; Replacement 8 covers the aggregation weights (Eqs. (4), (17)-(18)), their relation to the objective of Eq. (1) and the reporting of participation and influence. Locations refer to the original sn-article.tex. Evidence comes from our reproduced runs (ResNet-18 with frozen early layers, 100 clients, 100 rounds, cohorts of 5 to 10 clients; 95% bootstrap intervals); the manuscript must state that its numbers come from this implementation. Colours: [red]{custom-style="Del"} = removed, [green]{custom-style="Add"} = added.
:::

::: {custom-style="BA-Note"}
NEW ELEMENTS. The original paper has no Section 4.3, no Section 5.4, no Tables Y, Z, W and no Eq. (18) with the coefficient kappa. They are new: the full text of Section 4.3 is in part 3a of this file (insert it after Section 4.2); the new paragraphs of Section 5.4 and Tables Z and W are in part 3 (Section 5.4 is inserted at the end of Section 5, before the Conclusion; its remaining paragraphs and Tables X, X2, Y are in the Replacement 5 file).
:::

# 1. What each comment receives: fix, location, evidence, declaration
"""

COMMENTS = [
    ("Replacement 7. R1-06 and R2-08: validity, indexing and rounding of the cohort rule",
     "Eq. (15) is written for the completed round and Eq. (16) uses the previous round, so that no future loss is needed. The efficiency is clipped to [0,1], the cohort is an integer obtained by half-up rounding and clamped to [Cmin, Cmax], the history starts at rho^0 = 0 (the first rounds select Cmax), a zero or non-finite previous loss cancels the round, and a candidate whose update is not finite is unavailable. The rule is nonincreasing in the efficiency, and any two rounding conventions differ by at most one client.",
     "Section 4.2, Eqs. (15)-(16) and the paragraph below Eq. (16).",
     "13 unit tests pass, among them: the cohort is an integer within its bounds for any rho, the original formula exceeds Cmax for negative rho, and the loss-pair guards hold. No round was cancelled and no update failed in any reproduced run.",
     "The rule returns a valid integer cohort in every round, and the effect of the rounding convention is bounded by one client."),
    ("Replacement 7. R2-09 and R1-18: dynamic range of the cohort and the participation counts",
     "The claim of about 15% fewer clients per round is replaced by the measured saving and its bound, 1 - Cmin/Cmax. The ratio of the loss reduction to the reference rate can replace the absolute reduction, which uses the whole range. Per-round cohort sizes are recorded in every run and are released with the code; the bounds of each configuration are stated; uploads per round and cumulative uploads to a target are reported separately.",
     "Section 4.2 (paragraph below Eq. (16)); Section 5.1 (ablation text); Section 5.4, Cohort size and Table Z.",
     "Table Z. With the absolute rule the mean cohort is 9.71 [9.68, 9.75] over 45 runs (2.9% fewer uploads than a fixed cohort of ten; the cohort is at its maximum in 75% of the rounds). With the ratio rule the mean cohort is 9.10, the smallest cohort 5, and the uploads fall by 7.5% relative to the absolute rule (9.0% relative to a fixed cohort); accuracy differs by -0.29 [-0.57, +0.05] (best round) and -0.08 [-0.55, +0.41] (last 10 rounds) points.",
     "The cohort rule reduces uploads without a detectable change of accuracy, its saving is stated with its upper bound, and the relative-pace measure uses the full range."),
    ("Replacement 8. R1-03 and R2-07: the implemented aggregation, negative scores and dataset size",
     "Eq. (18) defines one weight family S = (1 - kappa) n_i / sum n_j + kappa q_i, where q is the normalised positive part of the stability score. It is nonnegative, sums to one, and is defined for negative scores, a vanishing denominator (scaled by the largest score; sample-count fallback when all scores are zero) and identical client models. Eq. (4) and Algorithm 2 use these weights. With kappa = 0, used in all reported experiments, the sample size n_i is retained.",
     "Section 4.2, Eqs. (17)-(18) and the paragraph below them; Section 1 (contributions).",
     "13 unit tests pass (nonnegative weights summing to one for negative, zero and mixed scores). The smallest weight of a selected client was 2e-3 with sample-count weights and 4e-5 with stability weights. Table W: sample-count weights give a higher last-10-round accuracy in 5 of 9 settings and a lower one in none.",
     "One normalised, nonnegative aggregation rule is specified and evaluated, and its default coincides with the sample-size weighting of the objective."),
    ("Replacement 8. R1-11: the objective and the ranking heuristic",
     "Eq. (1) is stated as the learning objective. The ranking of Eq. (3) decides which clients take part; the aggregation with kappa = 0 weights the selected clients by their sample counts, the weighting of Eq. (1) restricted to the selected clients. The stability weights are an evaluated alternative.",
     "Section 4.1, last paragraph; Section 4.2, closing paragraph.",
     "Proposition 3 (Section 4.3): the aggregate moves by at most eta K G per round for any selection and any nonnegative weights.",
     "The learning objective, the selection rule and the aggregation weights are separated, and the aggregation is consistent with the population objective."),
    ("Replacement 8. R1-10: selection frequency, waiting time and aggregation influence",
     "The manuscript reports the participation counts, the proportion of never-selected clients, the longest waits, the accuracy of the weakest clients and the cumulative aggregation influence of every client.",
     "Section 5.4, Participation and aggregation influence; Table Y.",
     "45 runs: every client selected at least once; Jain index 0.995-0.999; longest wait 10-13 rounds; weakest 10% of clients 63.2% (CIFAR-10) and 76.3% (FMNIST) accuracy; cumulative aggregation influence of the least and most influential client 0.35 and 2.24 times the mean (Gini 0.21), positive for every client.",
     "Participation and influence are measured, and every client contributes to the aggregate."),
]

TABLES_MD = r"""
Table Z. Cohort rules (CIFAR-10 and FMNIST, Dirichlet $\alpha=0.5$, sample-count aggregation, bounds 5 and 10; mean of 6 runs). Accuracy columns: paired difference to the fixed cohort of ten with 95% bootstrap interval (percentage points).

| Rule | Mean cohort | Smallest $m_t$ | Uploads (GB) | $\Delta$ best acc. | $\Delta$ last-10 acc. | Max. wait |
|:--|--:|--:|--:|:--|:--|--:|
| Fixed cohort of ten | 10.00 | 10 | 33.6 | – | – | 10.0 |
| Absolute rule, Eq. (16) | 9.83 | 8 | 33.0 | +0.38 [−0.20, +0.96] | +0.47 [−0.10, +1.10] | 10.8 |
| Relative rate | 9.10 | 5 | 30.6 | +0.09 [−0.34, +0.58] | +0.39 [−0.20, +1.14] | 14.0 |

Table W. Sample-count weights ($\kappa=0$, FedFACS-A2) minus stability weights ($\kappa=1$, FedFACS), selection unchanged; paired difference over 3 seeds (percentage points, 95% bootstrap interval).

| Dataset | Partition | $\Delta$ best acc. | $\Delta$ last-10 acc. |
|:--|:--|:--|:--|
| CIFAR-10 | Dir. 0.1 | −1.72 [−2.15, −1.04] | +0.56 [−0.50, +1.62] |
| | Dir. 0.5 | +0.70 [+0.39, +1.17] | **+3.61** [+0.18, +8.40] |
| | Two classes | +1.41 [+1.03, +1.80] | +0.59 [−0.66, +1.83] |
| FMNIST | Dir. 0.1 | −0.08 [−1.07, +0.70] | +0.45 [−0.09, +1.00] |
| | Dir. 0.5 | +0.46 [−0.06, +0.97] | **+2.58** [+1.48, +3.96] |
| | Two classes | −0.67 [−1.33, +0.05] | +1.65 [−0.92, +4.02] |
| MNIST | Dir. 0.1 | +0.45 [−0.05, +0.96] | **+4.35** [+1.93, +6.54] |
| | Dir. 0.5 | +0.58 [+0.30, +0.92] | **+9.60** [+7.40, +12.91] |
| | Two classes | +0.24 [+0.01, +0.43] | **+3.86** [+1.27, +6.21] |
"""

NOTATION = r"""
# 4. Notation declared by these replacements

| Symbol | Declaration |
|:--|:--|
| $m_t=\lvert C_k^t\rvert$, $C_{k_{\min}}\le m_t\le C_{k_{\max}}$ | NEW/CHANGED: integer cohort size and its integer bounds, fixed in advance for each configuration |
| $\rho^{t}$ (15) | CHANGED: relative reduction of the validation loss of the completed round $t$; selection in round $t$ uses $\rho^{t-1}$ |
| $\Omega^{t}$ | reference convergence rate (Eq. (11)); the ratio rule uses the ratio $\rho^{t-1}/\Omega^{t}$ in Eq. (16), taken as zero when $\Omega^{t}\le 0$ |
| $\kappa\in[0,1]$, $S_i^t$ (18) | NEW/CHANGED: weighting coefficient and aggregation weights; $\kappa=0$ gives sample-count weights (used) |
| $s_{i,+}^t=\max(s_i^t,0)$, $H^t=\sum_{j\in C_k^t}s_{j,+}^t$ | NEW: positive part of the stability score and its cohort sum |
| $q_i^t$, $\hat s^{\,t}$ | NEW: stability weights; largest positive score (numerical scaling) |
| $N$, $C_k^t$, $m_t$ | the population size, the cohort and its size (the unused symbol $K$ of the original is removed) |
"""

PREP = r"""
# 5. Prepared answers (internal, not for the manuscript)

- **Why does the cohort stay close to its maximum?** Eq. (16) with the absolute loss reduction selects the maximum in 75% of the rounds; the ratio rule uses the whole range and lowers the uploads by 7.5% without a detectable change of accuracy (Table Z).
- **Why is the saving not larger?** It is bounded by 1 − Cmin/Cmax; the reproduction uses bounds of 5 and 10, wider than the 8 and 10 of the original ablation.
- **Where are the per-round cohort logs?** Every run records the cohort size of every round; they are released with the code.
- **Why sample-count weights?** They keep the aggregate consistent with Eq. (1) and give the higher last-10-round accuracy in 5 of 9 settings and a lower one in none (Table W).
"""


def build_md():
    md = [HEAD]
    for t, fix, where, ev, decl in COMMENTS:
        md.append("**%s**\n" % t)
        md.append("- Fix: %s" % fix)
        md.append("- Where: %s" % where)
        md.append("- Evidence: %s" % ev)
        md.append("- Declaration: %s\n" % decl)
    md.append("\n# 2. Edits: before and after, with locations\n")
    for rep in (7, 8):
        md.append('\n::: {custom-style="BA-Sub"}\nReplacement %d\n:::\n' % rep)
        for k, e in enumerate([x for x in EDITS if x["rep"] == rep], 1):
            before, after = B.before_after(e["orig"], e["rev"], e["onums"], e["rnums"])
            line = B.line_of(e["at"][1], e["at"][0])
            md.append('\n::: {custom-style="BA-Edit"}\nReplacement %d, edit %d: %s\n:::\n' % (rep, k, e["title"]))
            md.append('::: {custom-style="BA-Loc"}\nLocation: %s\n:::\n' % (e["loc"] % line))
            md.append('::: {custom-style="BA-Label-Before"}\nBefore (remove)\n:::\n')
            md.append(before)
            md.append('::: {custom-style="BA-Label-After"}\nAfter (put instead)\n:::\n')
            md.append(after)
    md.append("\n# 3. Evidence (new paragraphs and tables of subsection 5.4)\n")
    md.append('::: {custom-style="BA-Note"}\nInsert the two paragraphs below in subsection 5.4 (Analysis of the selection score), before the paragraph on the uncertainty penalty; Table Z belongs to the first and Table W summarises the paragraph on aggregation weights that is already in 5.4.\n:::\n')
    s = B.S54
    a = s.index(BS + "textbf{Cohort size.}")
    b = s.index(BS + "textbf{Uncertainty penalty.}")
    block = s[a:b]
    block = B.re.sub(B.BSR + r"begin\{table\}.*?" + B.BSR + r"end\{table\}", "@@T@@", block, flags=B.re.S)
    parts = [p.strip() for p in B.re.split(r"\n\s*\n", block) if p.strip()]
    for p in parts:
        if p == "@@T@@":
            md.append(TABLES_MD.split("Table W.")[0])
        else:
            md.append(B.conv_text(" ".join(p.split("\n"))) + "\n")
    md.append("Table W." + TABLES_MD.split("Table W.")[1])
    md.append(chr(10) + "# 3a. New section to insert: 4.3" + chr(10))
    md.append(B.NEW43_NOTE)
    md.append(B.section43_md())
    md.append(NOTATION)
    md.append(PREP)
    return "\n".join(md)


def style_generic(doc):
    spec = [([0.55, 1.5, 0.7, 0.7, 1.3, 1.3, 0.5], 1), ([0.6, 0.9, 2.5, 2.5], 1)]
    # Table Z is the first table, Table W the second, then the notation table
    widths = [[1.7, 0.7, 0.8, 0.8, 1.4, 1.4, 0.6], [0.8, 0.9, 2.3, 2.3], [2.4, 4.1]]
    for ti, t in enumerate(doc.tables[:3]):
        t.autofit = False
        lay = B.OxmlElement("w:tblLayout")
        lay.set(B.qn("w:type"), "fixed")
        t._tbl.tblPr.append(lay)
        n = len(t.rows)
        for r_i, row in enumerate(t.rows):
            for c_i, cell in enumerate(row.cells):
                cell.width = Inches(widths[ti][c_i])
                B.border(cell, top="nil", bottom="nil", left="nil", right="nil")
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(1)
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (c_i == 0 or ti == 2 or (ti == 1 and c_i == 1)) else WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.size = Pt(9)
                        if r_i == 0:
                            run.font.bold = True
        for cell in t.rows[0].cells:
            B.border(cell, top="single", bottom="single")
        for cell in t.rows[n - 1].cells:
            B.border(cell, bottom="single")
        if ti == 1:
            for r_i in (4, 7):
                for cell in t.rows[r_i].cells:
                    B.border(cell, top="single")
        for gc, w in zip(t._tbl.tblGrid.findall(B.qn("w:gridCol")), widths[ti]):
            gc.set(B.qn("w:w"), str(int(w * 1440)))


def main():
    md_path = os.path.join(WORK, "final78.md")
    open(md_path, "w", encoding="utf8").write(build_md())
    ref = os.path.join(WORK, "ref.docx")
    pandoc = pypandoc.get_pandoc_path()
    subprocess.run([pandoc, "-o", ref, "--print-default-data-file", "reference.docx"], check=True)
    subprocess.run([pandoc, md_path, "-f", "markdown+tex_math_dollars+raw_attribute+fenced_divs+bracketed_spans", "-o", OUTF,
                    "--reference-doc=" + ref, "--columns=300"], check=True)
    d = docx.Document(OUTF)
    B.para_style(d, "BA-Title", size=16, bold=True, color="1F3864", after=8)
    B.para_style(d, "BA-Sub", size=13, bold=True, color="1F3864", before=10, after=4)
    B.para_style(d, "BA-Note", size=10, italic=True, fill="EEF3F8", before=4, after=6)
    B.para_style(d, "BA-Edit", size=11, bold=True, color="1F3864", before=10, after=2)
    B.para_style(d, "BA-Loc", size=9.5, italic=True, color="595959", after=3)
    B.para_style(d, "BA-Label-Before", size=10, bold=True, color="C00000", before=4, after=1)
    B.para_style(d, "BA-Label-After", size=10, bold=True, color="00793A", before=4, after=1)
    B.para_style(d, "DelBlock", fill="F8D7D7")
    B.para_style(d, "AddBlock", fill="D9F0DF")
    B.char_style(d, "Del", "C00000", "FBE4E4", strike=True)
    B.char_style(d, "Add", "00793A", "DDF3E3", bold=True)
    style_generic(d)
    d.save(OUTF)
    z = subprocess.run(["python", "-c", "import zipfile;x=zipfile.ZipFile(r'%s').read('word/document.xml').decode('utf8');print(x.count('<m:oMath>'),x.count(chr(92)))" % OUTF], capture_output=True, text=True).stdout.strip()
    print("saved", OUTF, "| equations, backslashes:", z, "| tables:", len(d.tables))


if __name__ == "__main__":
    main()
