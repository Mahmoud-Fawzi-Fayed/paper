"""Builds FedFACS_Replacement_9.docx or FedFACS_Replacement_10.docx (usage: python build_rep.py 9|10)."""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docx
import numpy as np
import pypandoc
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

import build_final56 as B

P, WORK, BS = B.P, B.WORK, B.BS
ORIG, REV = B.ORIG, B.REV
REP = int(sys.argv[1]) if len(sys.argv) > 1 else 10
OUTF = os.path.join(P, "FedFACS_Replacement_%d.docx" % REP)
O = json.load(open(os.path.join(WORK, "ev910.json")))
R, T, A, PT = O["resource"], O["target"], O["audit"], O["part"]


def to_eol(text, start):
    i = text.index(start)
    j = text.find("\n", i)
    return text[i:j if j >= 0 else len(text)]


def seg(text, start, end):
    i = text.index(start)
    return text[i:text.index(end, i) + len(end)]


def upto_eol(text, start, last):
    i = text.index(start)
    k = text.index(last, i)
    j = text.find("\n", k)
    return text[i:j if j >= 0 else len(text)]


EQ = lambda lab: BS + "label{" + lab + "}\n" + BS + "end{equation}"
CT = "(Table~" + BS + "ref{tab:cost})."
SP = chr(0xE000)


def fix_titles(t):
    bs = re.escape(BS)
    t = re.sub(bs + r"textit\{Cumulative number of selected clients until convergence\s+\(\$C_\{total\}\$\)\}",
               "*Cumulative" + SP + "number" + SP + "of" + SP + "selected" + SP + "clients" + SP + "until" + SP + "convergence" + SP + "($C_{total}$)*", t)
    t = re.sub(bs + r"textit\{Jain.s Fairness Index \(JFI\)\}", "*Jain\u2019s" + SP + "Fairness" + SP + "Index" + SP + "(JFI)*", t)
    return t


# ---------------------------------------------------------------- Algorithm 2 listing (Replacement 9)
ROW = re.compile(r"^(\d+)\.\s*&\s*(.*?)\s*(?:\\\\)?\s*$")


def alg_lines(text):
    i = text.index("Algorithm 2} Server-side")
    blk = text[i:text.index("\\end{tabular}", i)]
    inp = re.search(r"\\textbf\{Input:\}(.*?)\\vspace", blk, re.S).group(1)
    out = re.search(r"\\textbf\{Output:\}(.*?)\\vspace", blk, re.S).group(1)
    lines = ["**Input:** " + " ".join(inp.split()), "**Output:** " + " ".join(out.split())]
    for ln in blk.split("\n"):
        m = ROW.match(ln.strip())
        if m:
            t = re.sub(r"\\hspace\{[^}]*\}", "", m.group(2)).rstrip("\\ ").strip()
            lines.append("%s. %s" % (m.group(1), t))
    return lines


def alg_md(lines, other, style):
    out, keys = [], {re.sub(r"^\d+\.\s*", "", x) for x in other}
    for x in lines:
        c = B.conv_text(x)
        if re.sub(r"^\d+\.\s*", "", x) not in keys:
            lead = re.match(r"^(\d+\.\s*|\*\*\w+:\*\*\s*)", c)
            lead = lead.group(1) if lead else ""
            c = lead + '[%s]{custom-style="%s"}' % (c[len(lead):], style)
        out += [c, ""]
    return "\n".join(out)


EDITS = {
    9: [dict(title="Section 4.2: state after aggregation, commit and Eq. (19)", loc="Section 4.2, end of the model description (original line %d)",
             orig=seg(ORIG, "One more step, the resulting model", EQ("eq:avg_idle_correct")), rev=seg(REV, "After aggregation, the server evaluates", EQ("eq:avg_idle_correct")),
             onums=["19"], rnums=["19"], at="One more step, the resulting model"),
        dict(title="Section 4.2: description of Algorithm 2", loc="Section 4.2, paragraph after Algorithm 1 (original line %d)",
             orig=to_eol(ORIG, "Furthermore, algorithm 2 outlines"), rev=to_eol(REV, "Furthermore, algorithm 2 outlines"), onums=[], rnums=[], at="Furthermore, algorithm 2 outlines")],
    10: [dict(title="Performance metrics: round-to-target", loc="Section 5.1, performance metrics (original line %d)",
              orig=to_eol(ORIG, BS + "textit{Round-to-accuracy}"), rev=to_eol(REV, BS + "textit{Round-to-accuracy}"), onums=[], rnums=[], at=BS + "textit{Round-to-accuracy}"),
         dict(title="Performance metrics: uploads and total communication, Eqs. (23) and (23a)", loc="Section 5.1, performance metrics (original line %d)",
              orig=seg(ORIG, BS + "textit{Cumulative number of selected", EQ("eq:communication")), rev=upto_eol(REV, BS + "textit{Cumulative number of selected", "control messages in round $t$."),
              onums=["23"], rnums=["23", "23a"], at=BS + "textit{Cumulative number of selected"),
         dict(title="Performance metrics: reading of Jain's index, Eqs. (24)-(25)", loc="Section 5.1, performance metrics (original line %d)",
              orig=upto_eol(ORIG, BS + "textit{Jain", "represent the unfair participation."), rev=upto_eol(REV, BS + "textit{Jain's Fairness Index", CT),
              onums=["24", "25"], rnums=["24", "25"], at=BS + "textit{Jain")],
}

SCOPE = {
    9: "Replacement 9 covers the server-side procedure after the aggregation (validation, staging and commit of the state, Eq. (19)) and Algorithm 2.",
    10: "Replacement 10 covers the metric definitions that concern communication and fairness (Eqs. (23), (23a), (24)) and one new table with the cost and the participation of the methods.",
}
NEWNOTE = {
    9: "Table S (in part 3) and its paragraph are new: the original paper has no Section 5.4. Insert them in Section 5.4, after the paragraph on participation and aggregation influence (Section 5.4 itself is inserted before the Conclusion, see the Replacement 5 file).",
    10: "Eq. (23a), Table V and its paragraph are new: the original paper has no Section 5.4. Insert them in Section 5.4, after the paragraph on participation and aggregation influence (Section 5.4 itself is inserted before the Conclusion, see the Replacement 5 file). Table 4 of the original paper is not changed here; Replacement 11 treats it.",
}

COMMENTS = {
    9: [("R1-01 and R2-03: when the counters are updated",
         "The server stages the idle counters of Eq. (7) with the model and the feedback state after the aggregation and commits them in one step; a cancelled round leaves them unchanged. The counters are read at selection time from the committed state; Eq. (19) averages them over the N clients.",
         "Section 4.2, paragraph after the aggregation and Eq. (19); Algorithm 2, lines 9 and 10.",
         "Table S: in all 251 runs the selection counts and the longest wait recomputed from the per-round selections equal the logged values; the 13 unit tests of the equations pass, among them the increment and the reset of the idle counter.",
         "The counters have one update time, and the logs reproduce it."),
        ("R2-08: time indexing and notation",
         "After round t the server computes the loss reduction, the reference rate and the deviation signal for the next round (Eqs. (15), (11), (10)) from completed rounds only. The population size is N throughout (K and C of the original are removed).",
         "Section 4.2, Eq. (19) and the paragraph above it; Algorithm 2, inputs and lines 9 to 11.",
         "The reference trajectory uses only past rounds (unit test); the cohort size is within its bounds in every logged round (Table S).",
         "Every quantity used in round t comes from an earlier committed round."),
        ("R1-21: one consistent and executable account",
         "Algorithm 2 lists the received information, the cohort size from the previous round, the selection with the waiting-time guard, the aggregation with the weights of Eq. (18), the validation, the update of the control state and the counters, the commit and the broadcast to the N candidates, in the order of the text. Messages with identifiers describe a deployment. The restriction of the privacy and scalability statements is in the paragraph on the operating assumptions of Section 4.3.",
         "Algorithm 2 and the paragraph that describes it, Section 4.2; Section 4.3.",
         "Table S: the logged cohorts, selection counts, waiting times and uploaded volumes are consistent in all 251 runs; no round was cancelled and no update was non-finite in the 689 runs.",
         "The procedure of the server follows the equations and runs in the stated order.")],
    10: [("R1-08 and R2-01: the communication model and the hidden costs",
          "Eq. (23) counts the uploaded updates. Eq. (23a) adds the downloads and the control messages, so that the total communication of every method is counted under one model. Table V reports the models sent, the updates uploaded, the local steps and the volume to the target for all methods, run in the same simulation.",
          "Section 5.1, Eqs. (23), (23a); Section 5.4, paragraph and Table V.",
          "Table V (45 runs per method): FedFACS sends the model to all 100 candidates and trains them, 10.0 times the local steps of random sampling; its uploads to the target are 6.2% fewer (520 against 555) and its total volume to the target is 198 against 37 GB.",
          "Uploads, downloads and local computation are measured for every method, and the saving of FedFACS is stated for the uploaded updates."),
         ("R1-09 and R2-15: what the Jain index measures",
          "Eq. (24) is read as the equality of the quality-adjusted participation, and with q equal to one as the equality of participation. The interpretation of 0.5 as a boundary is replaced by the minimum 1/N and an example. The percentage of never-selected clients is reported next to the index.",
          "Section 5.1, Eqs. (24)-(25); Section 5.4, Table V (columns JFI and Never).",
          "Table V: JFI with q equal to one is 0.997 for FedFACS and 0.920 for random sampling; no FedFACS client is left unselected, while DivFL leaves 47.4% unselected. Example: 90 of 100 clients served uniformly give 0.9.",
          "The index is interpreted correctly, and its value is accompanied by the share of clients that are never served.")],
}


def tbl(header, rows, caption):
    return "%s\n\n| %s |\n|%s|\n%s\n" % (caption, " | ".join(header), "|".join([":--"] + ["--:"] * (len(header) - 1)), "\n".join("| " + " | ".join(r) + " |" for r in rows))


def table_v():
    names = [("random", "Random sampling (FedAvg)"), ("powd", "Power-of-Choice"), ("oort", "Oort"), ("divfl", "DivFL"), ("abl_A2", r"FedFACS ($\kappa=0$)")]
    rows = []
    for k, nm in names:
        r, t, p = R[k], T[k], PT[k]
        rows.append([nm, "%.1f" % r["down"], "%.2f" % r["up"], "%.0f" % r["steps"], "%.1f" % r["fwd_k"], "%.1f" % r["total_gb"], "%.0f" % t["uploads"], "%.1f" % t["total_gb"], "%.3f" % p["jfi"], "%.1f" % p["never"]])
    cap = (r"Table V. Methods under one communication model (45 runs each; 100 rounds; $N=100$). Steps: local SGD steps per round. Scoring: forward passes per round (thousands) that give $\Delta KL_i^t$ and $\sigma_i^2$ of the fitness score, Eq. (14) (Eqs. (5) and (12)); for Power-of-Choice and DivFL, the forward passes of their selection. To target: $C_{\mathrm{total}}$ and $\mathrm{Comm}_{\mathrm{total}}$ at the first round that reaches the common target accuracy. "
           r"JFI: Eq. (24) with $q_i=1$. Never: percentage of clients with $p_i=0$.")
    return tbl(["Method", "Down", "Up", "Steps", "Scoring", "Total GB", "Uploads to target", "GB to target", "JFI", "Never (%)"], rows, cap)


def table_s():
    n = A["ff"]
    items = [(r"Cohort size within $[C_{k_{\min}},C_{k_{\max}}]$ in every round", A["bounds"]),
             ("Logged cohort size equals the number of selected clients", A["cohort_eq"]),
             ("Selection counts recomputed from the per-round selections equal the logged counts", A["selcnt_ok"]),
             ("Longest wait recomputed from the per-round selections equals the logged value", A["wait_ok"]),
             ("Uploaded volume equals the sum of the cohort sizes times the model size", A["up_ok"]),
             ("Number of logged rounds equals the configured number of rounds", A["rounds_ok"])]
    cap = "Table S. Consistency of the logged protocol in the %d runs of FedFACS and its ablation variants. Across all %d runs no round was cancelled and no client update was non-finite." % (n, A["runs"])
    return tbl(["Check", "Runs passing"], [[a, "%d / %d" % (b, n)] for a, b in items], cap)


def mapping_md():
    f, r, tf, tr = R["abl_A2"], R["random"], T["abl_A2"], T["random"]
    gb = lambda x: x["total_gb"]
    per = lambda x: (x["down"] + x["up"]) * 33.595432 / 1000.0
    rows = [
        ["Models sent per round", r"$\mathrm{Comm}^t_{\mathrm{down}}$ divided by the model size", "Down", "%.1f" % f["down"], "%.1f" % r["down"]],
        ["Updates uploaded per round", r"$\mathrm{Comm}^t_{\mathrm{up}}$ divided by the model size", "Up", "%.2f" % f["up"], "%.2f" % r["up"]],
        ["Volume per round (GB)", r"$\mathrm{Comm}^t_{\mathrm{down}}+\mathrm{Comm}^t_{\mathrm{up}}$ (the term $\mathrm{Comm}^t_{\mathrm{aux}}$ is below 0.1% of it)", "none", "%.2f" % per(f), "%.2f" % per(r)],
        ["Volume after 100 rounds (GB)", r"$\mathrm{Comm}_{\mathrm{total}}(100)$, sum over $t=1,\dots,100$", "Total GB", "%.1f" % gb(f), "%.1f" % gb(r)],
        ["Uploads to the target", r"$C_{\mathrm{total}}$ of Eq. (23) at the first round that reaches the target", "Uploads to target", "%.0f" % tf["uploads"], "%.0f" % tr["uploads"]],
        ["Volume to the target (GB)", r"$\mathrm{Comm}_{\mathrm{total}}$ of Eq. (23a) at that round", "GB to target", "%.1f" % tf["total_gb"], "%.1f" % tr["total_gb"]],
        ["Saving in uploads", r"$1-C_{\mathrm{total}}^{\mathrm{FedFACS}}/C_{\mathrm{total}}^{\mathrm{random}}$", "none", "%.1f%%" % (100 * (1 - tf["uploads"] / tr["uploads"])), "none"],
    ]
    cap = ("Reading guide (explanatory, not for the manuscript). Model size: 33.6 MB (trainable weights). Down, Up and the volumes are averages over the 45 runs of each method; "
           "the values of each row follow from the previous rows up to the averaging over runs.")
    return tbl(["Quantity", "Equation term", "Column of Table V", "FedFACS", "Random sampling"], rows, cap)


def section3_md():
    s = open(os.path.join(P, "paper_overleaf_revised", "sn-article.tex"), encoding="utf8", newline="").read().replace("\r\n", "\n")
    if REP == 10:
        a, b = s.index(BS + "textbf{Communication and participation.}"), s.index(BS + "textbf{Protocol consistency.}")
        tab = table_v()
    else:
        a, b = s.index(BS + "textbf{Protocol consistency.}"), s.index(BS + "textbf{Uncertainty penalty.}")
        tab = table_s()
    blk = re.sub(re.escape(BS) + r"begin\{table\}.*?" + re.escape(BS) + r"end\{table\}", "@@T@@", s[a:b], flags=re.S)
    parts = [p.strip() for p in re.split(r"\n\s*\n", blk) if p.strip()]
    return "\n".join(tab if p == "@@T@@" else B.conv_text(" ".join(p.split("\n"))) + "\n" for p in parts)


NOTATION = {
    9: r"""
| Symbol | Declaration |
|:--|:--|
| $N$ | CHANGED: client population; replaces $K$ and $C$ of the original |
| $r_i^{t+1}$, $\overline{r^{t+1}}$ (7), (19) | CHANGED: idle counter and population mean after round $t$, staged after the aggregation and committed with the model |
| $\rho^{t}$, $\Omega^{t+1}$, $\nu^{t+1}$ (15), (11), (10) | previously declared; computed after round $t$ from completed rounds and used from round $t+1$ |
""",
    10: r"""
| Symbol | Declaration |
|:--|:--|
| $\mathrm{Comm}_{\mathrm{total}}(T)$ (23a) | NEW: total communication in bytes over the first $T$ rounds |
| $\mathrm{Comm}^t_{\mathrm{down}}$ (23a) | NEW: volume in bytes of the models sent to the clients in round $t$ |
| $\mathrm{Comm}^t_{\mathrm{up}}$ (23a) | NEW: volume in bytes of the updates uploaded by the selected clients in round $t$ |
| $\mathrm{Comm}^t_{\mathrm{aux}}$ (23a) | NEW: volume in bytes of the scores and control messages in round $t$ |
| $C_{\mathrm{total}}$ (23) | CHANGED: sum of the cohort sizes $\lvert C_k^t\rvert$ over the first $T$ rounds (uploaded updates) |
| $N$ | CHANGED: client population; replaces $n$ of the original |
| $p_i$, $q_i$ (24), (25) | previously declared: participation rate and data quality of client $i$; $q_i=1$ gives the equality of participation |
""",
}
PREP = {
    9: """- **Messages with identifiers.** The simulation is synchronous; the sentence on identifiers describes a deployment (introduced with "In a deployment").
- **Reproducibility package.** The runs log the configuration, seeds, per-round selections, cohort sizes, validation loss and accuracy, the mean mixing coefficient and fairness term, the deviation signal and the traffic counters (JSON). The individual fitness scores of every round are not logged. A release statement needs the authors' confirmation.""",
    10: """- **Model size.** The volumes count the trainable weights of the model (33.6 MB per model); the frozen layers are assumed present at the clients. The ratios between the methods do not depend on this size. The authors confirm whether the frozen weights count.
- **Baselines.** Power-of-Choice, Oort and DivFL are our implementations of the published descriptions, run in the same simulation; the Methods section must say so.
- **Wording.** "Communication-efficient" in the title and the abstract refers to the uploaded updates (Replacement 11).
- **Scenario 4.** The reproduction contains Scenarios 1 to 3 only.""",
}


def build_md():
    md = ['\n::: {custom-style="BA-Title"}\nFedFACS: Replacement %d\n:::\n' % REP,
          '::: {custom-style="BA-Note"}\nScope. %s Locations refer to the original sn-article.tex. Evidence comes from our reproduced runs (ResNet-18 with frozen early layers, 100 clients, 100 rounds, five seeds; 689 runs in total) and the manuscript must say that its numbers come from this implementation. Colours: [red]{custom-style="Del"} = removed, [green]{custom-style="Add"} = added.\n:::\n' % SCOPE[REP],
          '::: {custom-style="BA-Note"}\nNEW ELEMENTS. %s\n:::\n' % NEWNOTE[REP], "# 1. Comment, fix, location, evidence, declaration\n"]
    for t, fix, where, ev, decl in COMMENTS[REP]:
        md += ["**%s**\n" % t, "- Fix: %s" % fix, "- Where: %s" % where, "- Evidence: %s" % ev, "- Declaration: %s\n" % decl]
    md.append("\n# 2. Edits: before and after, with locations\n")
    k = 0
    for e in EDITS[REP]:
        k += 1
        before, after = B.before_after(fix_titles(e["orig"]), fix_titles(e["rev"]), e["onums"], e["rnums"])
        md.append('\n::: {custom-style="BA-Edit"}\nEdit %d: %s\n:::\n' % (k, e["title"]))
        md.append('::: {custom-style="BA-Loc"}\nLocation: %s\n:::\n' % (e["loc"] % B.line_of(ORIG, e["at"])))
        md += ['::: {custom-style="BA-Label-Before"}\nBefore (remove)\n:::\n', before, '::: {custom-style="BA-Label-After"}\nAfter (put instead)\n:::\n', after]
    if REP == 10:
        md.append('\n::: {custom-style="BA-Edit"}\nEdit 4: range of the fairness term of Eq. (6)\n:::\n')
        md.append('::: {custom-style="BA-Loc"}\nLocation: Section 4.2, directly after Eq. (6) (original line %d)\n:::\n' % B.line_of(ORIG, "The counter of idle rounds $r_i^t$"))
        md.append('::: {custom-style="BA-Label-Before"}\nBefore (remove)\n:::\n')
        md.append("No statement of the range of $F_i^t$.\n")
        md.append('::: {custom-style="BA-Label-After"}\nAfter (put instead)\n:::\n')
        md.append('[Since $0\\le r_i^t\\le N\\,\\overline{r^t}$, the fairness term satisfies $1\\le F_i^t < N+1$.]{custom-style="Add"}\n')
        md.append('::: {custom-style="BA-Note"}\nDeclaration: no new symbol. The bound follows from $\\sum_j r_j^t=N\\,\\overline{r^t}$ and $F_i^t=1+r_i^t/(1+\\overline{r^t})$; it is Proposition 1 (ii) of Section 4.3, with its proof, and a unit test checks it.\n:::\n')
    if REP == 9:
        lo, lr = alg_lines(ORIG), alg_lines(REV)
        md.append('\n::: {custom-style="BA-Edit"}\nEdit %d: Algorithm 2, inputs, outputs and steps\n:::\n' % (k + 1))
        md.append('::: {custom-style="BA-Loc"}\nLocation: Section 4.2, Algorithm 2 (original line %d); changed lines are marked.\n:::\n' % B.line_of(ORIG, "Algorithm 2} Server-side"))
        md += ['::: {custom-style="BA-Label-Before"}\nBefore (remove)\n:::\n', alg_md(lo, lr, "Del"), '::: {custom-style="BA-Label-After"}\nAfter (put instead)\n:::\n', alg_md(lr, lo, "Add")]
    md.append("\n# 3. New text and table for Section 5.4\n")
    md.append(section3_md())
    if REP == 10:
        md.append("\n# 3a. How each number of Table V follows from Eq. (23a)\n")
        md.append(mapping_md())
    md.append("\n# 4. Notation declared\n" + NOTATION[REP])
    md.append("\n# 5. Notes for the authors (internal, not for the manuscript)\n\n" + PREP[REP])
    return "\n".join(md).replace(SP, " ")


def style_tables(doc):
    widths = {10: [[1.5, 0.45, 0.4, 0.5, 0.55, 0.5, 0.7, 0.6, 0.45, 0.5], [1.4, 2.3, 1.0, 0.8, 1.0], [2.4, 4.1]], 9: [[5.2, 1.2], [2.4, 4.1]]}[REP]
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
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (c_i == 0 or len(widths[ti]) == 2 or (REP == 10 and ti == 1 and c_i == 1)) else WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.size = Pt(8.5 if len(widths[ti]) > 2 else 9)
                        run.font.bold = (r_i == 0) or run.font.bold
        for cell in t.rows[0].cells:
            B.border(cell, top="single", bottom="single")
        for cell in t.rows[n - 1].cells:
            B.border(cell, bottom="single")
        for gc, w in zip(t._tbl.tblGrid.findall(B.qn("w:gridCol")), widths[ti]):
            gc.set(B.qn("w:w"), str(int(w * 1440)))


def main():
    md_path = os.path.join(WORK, "final_rep%d.md" % REP)
    open(md_path, "w", encoding="utf8").write(build_md())
    ref = os.path.join(WORK, "ref.docx")
    pandoc = pypandoc.get_pandoc_path()
    subprocess.run([pandoc, "-o", ref, "--print-default-data-file", "reference.docx"], check=True)
    subprocess.run([pandoc, md_path, "-f", "markdown+tex_math_dollars+raw_attribute+fenced_divs+bracketed_spans+pipe_tables", "-o", OUTF, "--reference-doc=" + ref, "--columns=300"], check=True)
    d = docx.Document(OUTF)
    B.para_style(d, "BA-Title", size=16, bold=True, color="1F3864", after=8)
    B.para_style(d, "BA-Note", size=10, italic=True, fill="EEF3F8", before=4, after=6)
    B.para_style(d, "BA-Edit", size=11, bold=True, color="1F3864", before=10, after=2)
    B.para_style(d, "BA-Loc", size=9.5, italic=True, color="595959", after=3)
    B.para_style(d, "BA-Label-Before", size=10, bold=True, color="C00000", before=4, after=1)
    B.para_style(d, "BA-Label-After", size=10, bold=True, color="00793A", before=4, after=1)
    B.para_style(d, "DelBlock", fill="F8D7D7")
    B.para_style(d, "AddBlock", fill="D9F0DF")
    B.char_style(d, "Del", "C00000", "FBE4E4", strike=True)
    B.char_style(d, "Add", "00793A", "DDF3E3", bold=True)
    style_tables(d)
    d.save(OUTF)
    print("saved", OUTF, "| tables:", len(d.tables))


if __name__ == "__main__":
    main()
