"""Builds FedFACS_Missing_Sections_5-8.docx: every new element of Replacements 5-8 that does not exist in the original paper,
with the proofs and a ledger that ties every number to the raw runs (tools/verify_claims.py)."""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docx
import pypandoc
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

import build_78 as N
import build_final56 as B

P, WORK, BS, BSR = B.P, B.WORK, B.BS, B.BSR
OUTF = os.path.join(P, "FedFACS_Missing_Sections_5-8.docx")
NL = chr(10)
CLAIMS = json.load(open(os.path.join(WORK, "claims.json"), encoding="utf8"))

# ----------------------------------------------------------------------------- tables as markdown
XP, X2P, YP = [s.strip() for s in re.split(r"(?=Table X2\.|Table Y\.)", B.TABLES_MD.strip())]
ZP, WP = [s.strip() for s in re.split(r"(?=Table W\.)", N.TABLES_MD.strip())]
TABLE_MD = {"tab:kl_validity": XP, "tab:kl_drift": X2P, "tab:mixing": YP, "tab:cohort": ZP}

HEAD = r"""
::: {custom-style="BA-Title"}
FedFACS: the new sections, with their proofs and the evidence for every number (Replacements 5 to 8)
:::

::: {custom-style="BA-Note"}
Purpose. The original paper has no Section 4.3, no Section 5.4, no Tables X, X2, Y, Z, no Eqs. (5a), (5b), (12a) and no coefficient kappa in Eq. (18). Replacements 5 to 8 refer to them. This file contains all of them in one place: where each is inserted (part 1), the proofs of the statements that the new text makes (part 2), the full text of the two new sections with their tables (parts 3 and 4), the new equations (part 5), and a ledger that recomputes every number of the new text from the raw run files (part 6). Evidence comes from our reproduced runs (ResNet-18 with frozen early layers, 100 clients, 100 rounds, cohorts of 5 to 10 clients); the manuscript must state that its numbers come from this implementation.
:::

# 1. What is new and where it is inserted

| New element | Insert at | Used by | Reviewer comments |
|:--|:--|:--|:--|
| Section 4.3 Properties of FedFACS (Propositions 1 to 3, waiting-time guard) | after Section 4.2, before Section 5 | Replacements 6, 7, 8 | R1-02, R1-10, R2-04, R2-18 |
| Section 5.4 Analysis of the selection score | end of Section 5, before the Conclusion | Replacements 5, 6, 7, 8 | R1-04, R1-05, R1-06, R1-10, R1-11, R1-18, R2-04, R2-05, R2-06, R2-07, R2-09 |
| Tables X, X2 (utility validity and drift), Y (mixing coefficient), Z (cohort rules) | inside Section 5.4 | Replacements 5, 6, 7 | as above |
| Eqs. (5a), (5b), (12a); Eq. (16) with the relative-pace option; Eq. (18) with kappa | Section 4.2 | Replacements 5, 7, 8 | R1-03, R1-04, R1-05, R1-06, R2-06, R2-07 |
| the aggregation family S = (1 - kappa) n_i / sum n_j + kappa q_i and its default kappa = 0 | Section 4.2, Eq. (18) | Replacement 8 | R1-03, R1-11, R2-07 |

Tables X, X2, Y and Z are numbered by LaTeX in the manuscript; the letters are used here only to name them.
"""

LEMMAS = r"""
# 2. Proofs of the statements made by the new text

**Lemma A (direction of the feedback, Eq. (8); R1-02, R2-04).** Let $g_i^t=\dfrac{\nu^t(\Delta KL_i^t-F_i^t)}{\lambda F_i^t+\lvert\nu^t(\Delta KL_i^t-F_i^t)\rvert}$, so that $a_i^t=\mathrm{clip}\big(\beta a_i^{t-1}+(1-\beta)g_i^t,0,1\big)$ with $a_i^{t-1}\in[0,1]$.

(i) $\lvert g_i^t\rvert<1$ and $\operatorname{sign} g_i^t=\operatorname{sign}\big(\nu^t(\Delta KL_i^t-F_i^t)\big)$, because $\lambda F_i^t\ge\lambda>0$.

(ii) If $\nu^t>0$ and $\Delta KL_i^t<F_i^t$, then $g_i^t<0$, hence $\beta a_i^{t-1}+(1-\beta)g_i^t<\beta a_i^{t-1}\le a_i^{t-1}$ and, since $a_i^{t-1}\ge 0$, the clip gives $a_i^t\le a_i^{t-1}$, with strict inequality unless $a_i^{t-1}=0$.

(iii) If $\nu^t>0$ and $\Delta KL_i^t>F_i^t$, then $g_i^t>0$ and $a_i^t>a_i^{t-1}$ if and only if $g_i^t>a_i^{t-1}$.

So a positive deviation signal lowers the utility weight exactly when the utility score is below the fairness term, and can raise it otherwise. In the reproduced runs the utility score was below $F_i^t$ in 82.7% of the client-rounds, and the mean coefficient decreased in 98.2% of the 4,316 rounds with $\nu^t>0$ (ledger K4, E1). $\square$

**Lemma B (cohort rule, Eq. (16); R1-06, R2-08, R2-09).** Let $m(x)=\min\{C_{k_{\max}},\max\{C_{k_{\min}},\lfloor C_{k_{\min}}+(C_{k_{\max}}-C_{k_{\min}})(1-\mathrm{clip}(x,0,1))+\tfrac12\rfloor\}\}$.

(i) $m(x)$ is an integer with $C_{k_{\min}}\le m(x)\le C_{k_{\max}}$ for every real $x$, because of the clamp.

(ii) $m$ is nonincreasing in $x$, because $\mathrm{clip}$ is nondecreasing and the other maps are nonincreasing.

(iii) The floor, the nearest-integer and the ceiling conventions differ by at most one client, because $\lceil x\rceil-\lfloor x\rfloor\le 1$.

(iv) The original unrounded formula $C_{k_{\min}}+(C_{k_{\max}}-C_{k_{\min}})(1-\rho)$ exceeds $C_{k_{\max}}$ if and only if $\rho<0$.

(v) Since $m_t\ge C_{k_{\min}}$, the uploads over $T$ rounds are at least $T\,C_{k_{\min}}$, so the saving relative to a fixed cohort of $C_{k_{\max}}$ is at most $1-C_{k_{\min}}/C_{k_{\max}}$: 50% for bounds of 5 and 10, and 20% for bounds of 8 and 10. $\square$

**Lemma C (aggregation weights, Eq. (18); R1-03, R1-11, R2-07).** Let $q_i^t=s_{i,+}^t/H^t$ if $H^t>0$ and $q_i^t=n_i/\sum_{j}n_j$ otherwise, and $S_i^t=(1-\kappa)n_i/\sum_j n_j+\kappa q_i^t$ with $\kappa\in[0,1]$.

(i) $S_i^t\ge 0$ and $\sum_{i\in C_k^t}S_i^t=1$, since $S^t$ is a convex combination of two points of the simplex.

(ii) For $\kappa=0$, $w_{\mathrm{global}}^{t+1}=\sum_i n_iw_i^t/\sum_i n_i$; when the cohort is the whole population these are the weights $n_i/n$ of Eq. (1).

(iii) Negative scores: only the positive part enters. If no score is positive, or all scores are zero (identical client models give $\Delta KL=0$ and $\sigma^2=0$), then $H^t=0$ and the sample-count fallback applies, so no division by a vanishing quantity occurs.

(iv) For $H^t>0$ the scaled form $z_i/\sum_j z_j$ with $z_i=s_{i,+}^t/\hat s^{\,t}$ equals $s_{i,+}^t/H^t$, because $\hat s^{\,t}>0$ cancels. $\square$

**Proposition 2 (bounded waiting) and Propositions 1 and 3** are proved in Section 4.3 (part 3). They are also executed in part 6: the guard was simulated for 3,000 rounds with adversarial and random scores (rows H1) and the quantities of Proposition 1 were evaluated on random inputs (rows H2 to H5); 13 unit tests pass (`fedfacs_repro/test_spec.py`).
"""

EQ_NOTE = '::: {custom-style="BA-Note"}' + NL + "New or changed equations of Section 4.2 that the text above relies on. The numbers are those of the revised manuscript." + NL + ":::" + NL


def new_equations_md():
    t = B.REV
    out = [EQ_NOTE]
    want = [("tag{5a}", "5a"), ("tag{5b}", "5b"), ("tag{12a}", "12a"), ("label{eq:ck_selection}", "16"), ("label{eq:stability_norm}", "18")]
    for m in re.finditer(BSR + r"begin\{equation\}(.*?)" + BSR + r"end\{equation\}", t, re.S):
        body = m.group(1)
        for key, num in want:
            if BS + key in body:
                out.append("$$ %s \\qquad (%s) $$" % (B.eq_clean(body), num))
                out.append("")
    return NL.join(out)


def sec54_md():
    s = NL.join(l for l in B.S54.split(NL) if not l.lstrip().startswith("%"))
    s = re.sub(BSR + r"subsection\{[^}]*\}" + BSR + r"label\{[^}]*\}", "", s)
    out = ['::: {custom-style="BA-Sub"}' + NL + "5.4 Analysis of the selection score (new subsection)" + NL + ":::" + NL]
    pos = 0
    for m in re.finditer(BSR + r"begin\{table\}.*?" + BSR + r"end\{table\}", s, re.S):
        for p in [x.strip() for x in re.split(r"\n\s*\n", s[pos:m.start()]) if x.strip()]:
            out.append(B.conv_text(" ".join(p.split(NL))) + NL)
        lab = re.search(r"label\{([^}]*)\}", m.group(0)).group(1)
        out.append(TABLE_MD[lab] + NL)
        pos = m.end()
    for p in [x.strip() for x in re.split(r"\n\s*\n", s[pos:]) if x.strip()]:
        out.append(B.conv_text(" ".join(p.split(NL))) + NL)
    return NL.join(out)


def ledger_md():
    rows = ["| ID | Where | Claim | In the paper | Recomputed from the raw runs | Source |", "|:--|:--|:--|:--|:--|:--|"]
    esc = lambda x: str(x).replace("|", "/")
    for c in CLAIMS:
        rows.append("| %s | %s | %s | %s | %s | %s |" % (esc(c["id"]), esc(c["where"]), esc(c["claim"]), esc(c["text"]), esc(c["got"]), esc(c["source"])))
    n_ok = sum(1 for c in CLAIMS if c["ok"])
    head = (NL + "# 6. Ledger: every number of the new text, recomputed from the raw run files" + NL + NL +
            '::: {custom-style="BA-Note"}' + NL +
            "Method. `tools/verify_claims.py` reads the 683 result files in `fedfacs_repro/results/` and recomputes each value stated in Sections 4.3 and 5.4 and in the replacement files: means, paired differences with 95% bootstrap intervals (10,000 resamples), Spearman correlations, rank AUC, waiting times, cohort sizes, aggregation weights and influence; the properties of Section 4.3 are executed on random inputs and by simulation. "
            "Result: @OK@ of @N@ values agree with the text. Rerun: `python tools/verify_claims.py`.".replace("@OK@", str(n_ok)).replace("@N@", str(len(CLAIMS))) + NL + ":::" + NL + NL)
    corr = r"""
**Values corrected by this verification (internal, not for the manuscript).** The text of the earlier drafts contained the following values, which the raw runs did not reproduce; each was replaced by the recomputed value and the sentence was rewritten around it.

| Earlier statement | Recomputed | Change made |
|:--|:--|:--|
| the mean mixing coefficient decreased in 96.7% of 1,827 rounds with $\nu>0$ | 98.2% of 4,316 rounds (96 main runs); the earlier alignment of $\nu$ with the round was off by one | value and alignment replaced |
| the coefficient settles at a median of 0.04 (mean 0.10) | median 0.10, mean 0.14 over the diagnostic rounds 5 to 100 | value replaced |
| $\Delta KL$ is typically much smaller than one; clients are grouped by waiting time | $\Delta KL$ has a median of 0.73 (F: 1.88); the weighted utility term is a median 3% of the weighted fairness term; the priority is rank-correlated with F (0.92) | the sentence now states the measured dominance of the waiting time, not a grouping |
| Jain index 0.995 to 0.998 for the sample-count aggregation | 0.995 to 0.999 | range corrected |
| rank-normalised priority: Jain 0.95 to 0.99, longest wait 18 to 20 | 0.94 to 0.99, 17 to 20 | ranges corrected |
| the ratio rule accuracy difference −0.30 [−0.57, +0.05] and −0.08 [−0.56, +0.41] | −0.29 [−0.57, +0.05] and −0.08 [−0.55, +0.41] | rounding corrected |
"""
    return head + NL.join(rows) + NL + corr


def build_md():
    md = [HEAD, LEMMAS]
    md.append(NL + "# 3. New Section 4.3 (insert after Section 4.2, before Section 5)" + NL)
    md.append(B.section43_md())
    md.append(NL + "# 4. New Section 5.4 with its tables (insert at the end of Section 5, before the Conclusion)" + NL)
    md.append(sec54_md())
    md.append("Table W (supporting evidence for the paragraph on aggregation weights; not a table of the manuscript)." + NL + NL + WP.split("Table W.", 1)[1].split(NL, 1)[1])
    md.append(NL + "# 5. New and changed equations" + NL)
    md.append(new_equations_md())
    md.append(ledger_md())
    return NL.join(md)


# ----------------------------------------------------------------------------- docx styling
def style_all(doc):
    widths = [[2.4, 1.6, 1.0, 1.5],                         # insert map
              [1.8, 0.45, 2.1, 2.1],                         # X
              [0.9, 2.0, 0.8, 0.8, 1.9],                     # X2
              [0.75, 1.6, 0.8, 0.8, 0.55, 0.65, 0.6, 0.8],   # Y
              [1.7, 0.7, 0.8, 0.8, 1.4, 1.4, 0.6],           # Z
              [0.8, 0.9, 2.3, 2.3],                          # W
              [0.5, 0.8, 1.9, 1.15, 1.35, 1.1],              # ledger
              [2.6, 2.0, 1.9]]                               # corrections
    left = [[0, 1, 2, 3], [0], [0, 1], [0, 1], [0], [0, 1], [0, 1, 2, 3, 4, 5], [0, 1, 2]]
    fsz = [9, 9, 9, 9, 9, 9, 7.5, 8.5]
    for ti, t in enumerate(doc.tables[:len(widths)]):
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
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_i in left[ti] else WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.size = Pt(fsz[ti])
                        if r_i == 0:
                            run.font.bold = True
        for cell in t.rows[0].cells:
            B.border(cell, top="single", bottom="single")
        for cell in t.rows[n - 1].cells:
            B.border(cell, bottom="single")
        if ti == 3:
            for cell in t.rows[6].cells:
                B.border(cell, top="single")
        if ti == 2:
            for cell in t.rows[3].cells:
                B.border(cell, top="single")
        if ti == 5:
            for r_i in (4, 7):
                for cell in t.rows[r_i].cells:
                    B.border(cell, top="single")
        for gc, w in zip(t._tbl.tblGrid.findall(B.qn("w:gridCol")), widths[ti]):
            gc.set(B.qn("w:w"), str(int(w * 1440)))


def main():
    md_path = os.path.join(WORK, "missing.md")
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
    style_all(d)
    d.save(OUTF)
    x = subprocess.run(["python", "-c", "import zipfile;x=zipfile.ZipFile(r'%s').read('word/document.xml').decode('utf8');print(x.count('<m:oMath>'))" % OUTF], capture_output=True, text=True).stdout.strip()
    print("saved", OUTF, "| equations:", x, "| tables:", len(d.tables))


if __name__ == "__main__":
    main()
