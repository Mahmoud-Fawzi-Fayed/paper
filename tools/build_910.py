"""Builds FedFACS_Replacements_9_10.docx (server procedure, commit; resource, fairness and classification metrics)."""
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
from build_78 import EQ, seg, to_eol, upto_eol

P, WORK, BS = B.P, B.WORK, B.BS
OUTF = os.path.join(P, "FedFACS_Replacements_9_10.docx")
ORIG, REV = B.ORIG, B.REV
O = json.load(open(os.path.join(WORK, "ev910.json")))
R, T, A, F, C = O["resource"], O["target"], O["audit"], O["fair"], O["cls"]

# ---------------------------------------------------------------- Algorithm 2 listing, before and after
ROW = re.compile(r"^(\d+)\.\s*&\s*(.*?)\s*(?:\\\\)?\s*$")


def alg_lines(text):
    i = text.index("Algorithm 2} Server-side")
    j = text.index("\\end{tabular}", i)
    blk = text[i:j]
    lines = []
    inp = re.search(r"\\textbf\{Input:\}(.*?)\\vspace", blk, re.S).group(1)
    out = re.search(r"\\textbf\{Output:\}(.*?)\\vspace", blk, re.S).group(1)
    lines.append("**Input:** " + " ".join(inp.split()))
    lines.append("**Output:** " + " ".join(out.split()))
    for ln in blk.split("\n"):
        m = ROW.match(ln.strip().replace("\\\\", "\\\\"))
        if m:
            t = m.group(2)
            t = re.sub(r"\\hspace\{[^}]*\}", "", t).rstrip("\\ ").strip()
            lines.append("%s. %s" % (m.group(1), t))
    return lines


def alg_md(lines, other, style_inline):
    out = []
    keys = {re.sub(r"^\d+\.\s*", "", x) for x in other}
    for x in lines:
        c = B.conv_text(x)
        k = re.sub(r"^\d+\.\s*", "", x)
        if k not in keys:
            lead = re.match(r"^(\d+\.\s*|\*\*\w+:\*\*\s*)", c)
            lead = lead.group(1) if lead else ""
            out.append(lead + '[%s]{custom-style="%s"}' % (c[len(lead):], style_inline))
        else:
            out.append(c)
        out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------- edits
EDITS = [
    dict(rep=9, title="Section 4.2: state after aggregation, commit and Eq. (19)", loc="Section 4.2, end of the model description (original line %d)",
         orig=seg(ORIG, "One more step, the resulting model", EQ("eq:avg_idle_correct")),
         rev=seg(REV, "After aggregation, the server evaluates", EQ("eq:avg_idle_correct")),
         onums=["19"], rnums=["19"], at=("One more step, the resulting model", ORIG)),
    dict(rep=9, title="Section 4.2: description of Algorithm 2", loc="Section 4.2, paragraph after Algorithm 1 (original line %d)",
         orig=to_eol(ORIG, "Furthermore, algorithm 2 outlines"), rev=to_eol(REV, "Furthermore, algorithm 2 outlines"),
         onums=[], rnums=[], at=("Furthermore, algorithm 2 outlines", ORIG)),
    dict(rep=10, title="Section 5, metrics: round-to-target", loc="Section 5.1, performance metrics (original line %d)",
         orig=to_eol(ORIG, BS + "textit{Round-to-accuracy}"), rev=to_eol(REV, BS + "textit{Round-to-accuracy}"),
         onums=[], rnums=[], at=(BS + "textit{Round-to-accuracy}", ORIG)),
    dict(rep=10, title="Section 5, metrics: macro-averaging of recall, precision and F1", loc="Section 5.1, performance metrics, after Eq. (22) (original line %d)",
         orig=to_eol(ORIG, "In the formulation, $TP$"), rev=to_eol(REV, "In the formulation, $TP$"),
         onums=[], rnums=[], at=("In the formulation, $TP$", ORIG)),
    dict(rep=10, title="Section 5, metrics: cumulative uploads and the total communication, Eqs. (23) and (23a)", loc="Section 5.1, performance metrics (original line %d)",
         orig=seg(ORIG, BS + "textit{Cumulative number of selected", EQ("eq:communication")),
         rev=upto_eol(REV, BS + "textit{Cumulative number of selected", "(Table~" + BS + "ref{tab:cost})."),
         onums=["23"], rnums=["23", "23a"], at=(BS + "textit{Cumulative number of selected", ORIG)),
    dict(rep=10, title="Section 5, metrics: Jain's index, quality and the reading of the index, Eqs. (24)-(25)", loc="Section 5.1, performance metrics (original line %d)",
         orig=upto_eol(ORIG, BS + "textit{Jain", "represent the unfair participation."),
         rev=upto_eol(REV, BS + "textit{Jain's Fairness Index", "(Table~" + BS + "ref{tab:fairness})."),
         onums=["24", "25"], rnums=["24", "25"], at=(BS + "textit{Jain", ORIG)),
]


SP = chr(0xE000)


def fix_titles(t):
    bs = re.escape(chr(92))
    t = re.sub(bs + r"textit\{Cumulative number of selected clients until convergence\s+\(\$C_\{total\}\$\)\}",
               "*Cumulative" + SP + "number" + SP + "of" + SP + "selected" + SP + "clients" + SP + "until" + SP + "convergence" + SP + "($C_{total}$)*", t)
    t = re.sub(bs + r"textit\{Jain.s Fairness Index \(JFI\)\}", "*Jain’s" + SP + "Fairness" + SP + "Index" + SP + "(JFI)*", t)
    return t


for _e in EDITS:
    _e["orig"], _e["rev"] = fix_titles(_e["orig"]), fix_titles(_e["rev"])

HEAD = r"""
::: {custom-style="BA-Title"}
FedFACS: Replacements 9 and 10 (server procedure and commit; resource, fairness and classification metrics)
:::

::: {custom-style="BA-Note"}
Scope. Replacement 9 covers the server-side procedure after aggregation (validation, staging and commit of the state, Eq. (19)) and Algorithm 2; Replacement 10 covers the metric definitions (Eqs. (20)-(25)), the communication accounting (new Eq. (23a)) and the reading of the fairness index. Locations refer to the original sn-article.tex. Evidence comes from our reproduced runs (ResNet-18 with frozen early layers, 100 clients, 100 rounds, five seeds; 689 runs in total); the manuscript must state that its numbers come from this implementation. Colours: [red]{custom-style="Del"} = removed, [green]{custom-style="Add"} = added.
:::

::: {custom-style="BA-Note"}
NEW ELEMENTS. The original paper has no Eq. (23a), no Section 5.4 and no Tables V, U, T and S. They are new: the paragraphs and tables are in part 3 of this file (insert them in Section 5.4, after the paragraph on participation and aggregation influence; Section 5.4 itself is inserted at the end of Section 5, before the Conclusion, as described in the Replacement 5 file). Table 4 of the original paper is not changed here: its recall and F1 values are reconciled in Replacement 11.
:::

# 1. What each comment receives: fix, location, evidence, declaration
"""

COMMENTS = [
    ("Replacement 9. R1-01 and R2-03: when the counters are updated",
     "The server stages the idle counters of Eq. (7) together with the model and the feedback state after the aggregation and commits them in one step; a cancelled round leaves the counters unchanged. The counter is read at selection time from the committed state, so that its initialisation, update timing and population mean (Eq. (19), with the population size N) are fixed.",
     "Section 4.2, paragraph after the aggregation and Eq. (19); Algorithm 2, lines 9 and 10.",
     "Table S: in all 251 runs of FedFACS and its variants the selection counts and the longest wait, recomputed from the per-round selections, equal the logged values; the 13 unit tests of the equations pass, among them the increment and the reset of the idle counter.",
     "The counter has one specified update time and the logs reproduce it."),
    ("Replacement 9. R2-08: time indexing and notation",
     "After round t the server computes the reduction of the validation loss, the reference rate and the deviation signal for the next round (Eqs. (15), (11), (10)) from completed rounds only; the next selection uses the committed values. The population size is N throughout (the symbols K and C of the original are removed) and Eq. (19) averages the counters of round t+1 over N clients.",
     "Section 4.2, Eq. (19) and the paragraph above it; Algorithm 2, inputs and lines 9 to 11.",
     "The reference trajectory uses only past rounds (unit test); the cohort size is within its bounds in every logged round of the 251 runs (Table S).",
     "Every quantity used in round t is computed in an earlier committed round."),
    ("Replacement 9. R1-21: one consistent and executable account",
     "Algorithm 2 lists the received information (scores, models, stability scores, sample counts), the cohort size from the previous round, the selection with the waiting-time guard, the aggregation with the weights of Eq. (18), the validation, the update of the control state and the counters, the commit and the broadcast to the N candidates, in the order of the text. In a deployment, messages carry run and round identifiers and duplicates or stale messages are rejected. The restriction of the privacy and scalability statements is in the paragraph on the operating assumptions of Section 4.3.",
     "Algorithm 2 (inputs, outputs, lines 1 to 11) and the paragraph that describes it, Section 4.2; Section 4.3, operating assumptions.",
     "Table S: the logged cohorts, selection counts, waiting times and uploaded volumes are consistent in all 251 runs; no round was cancelled and no update was non-finite in the 689 runs. The messages with identifiers describe a deployment; the simulation is synchronous and does not exercise them.",
     "The procedure of the server follows the equations and can be executed in the stated order."),
    ("Replacement 10. R1-08 and R2-01: the communication model and the hidden costs",
     "Eq. (23) counts the uploaded updates over the first T rounds. Eq. (23a) adds the downloads, the auxiliary traffic and the setup, calibration and final-model traffic, over all attempted rounds. Local training steps, scoring forward passes and elapsed time are reported separately. The text states that the saving of FedFACS is in the uploaded updates, while every candidate receives and trains the model.",
     "Section 5.1, performance metrics (Eqs. (23), (23a)); Section 5.4, Communication and computation cost and Table V.",
     "Table V (45 runs per method): FedFACS downloads to and trains all 100 candidates, 10.0 times the local steps of random sampling; its uploads are 9.71 per round against 10; to the common target it uploads 6.2% fewer updates than random sampling but transmits 198 against 37 GB in total.",
     "The total communication, the local computation and the uploads are measured under one explicit model, and the claim is limited to the uploads."),
    ("Replacement 10. R1-09 and R2-15: what the Jain index measures",
     "The index of Eq. (24) is read as the equality of the quality-adjusted participation; with q equal to one it is the equality of participation. Three notions are distinguished: equality of participation, participation proportional to quality, and fairness of the outcome (client-level accuracy). The interpretation of 0.5 as a boundary is removed; the minimum is 1/N and a value between 0.5 and 1 does not imply that every client participates. The never-selected share, the longest wait and the client-level accuracy are reported.",
     "Section 5.1, performance metrics (Eqs. (24)-(25)); Section 5.4, Participation fairness and Table U.",
     "Table U (Scenario 3, 3 seeds): the raw index of FedFACS is 0.999 and 0.997 against 0.919 for random sampling; the quality-adjusted index is 0.973 and 0.963, lower because the selection is nearly uniform; Greedy leaves 72% and 66% of the clients unselected. Example: two clients with q of 10 and 5 selected twice and once give 1.0 for the adjusted and 0.9 for the raw index; 90 of 100 clients served uniformly give 0.9.",
     "The index is interpreted correctly, and participation, quality-proportional participation and outcome are measured separately."),
    ("Replacement 10. recall, precision and F1 (supports the reconciliation of Table 4 in Replacement 11)",
     "The text states that the three quantities are computed per class from the confusion matrix of the test set and averaged with equal class weights.",
     "Section 5.1, after Eq. (22); Section 5.4, Classification metrics and Table T.",
     "Table T (15 runs per row): on CIFAR-10 and FMNIST the macro-recall equals the accuracy in every run; on MNIST the two differ by at most 0.92 points; the macro-F1 differs from the macro-recall by at most 0.7 points. In the original Table 4 the F1 exceeded the recall by 4 to 10 points, which is not possible for macro-averages on these test sets.",
     "The averaging is stated, and the reproduced values follow it."),
]


def tbl(header, rows, caption):
    return "%s\n\n| %s |\n|%s|\n%s\n" % (caption, " | ".join(header), "|".join([":--"] + ["--:"] * (len(header) - 1)), "\n".join("| " + " | ".join(r) + " |" for r in rows))


def table_v():
    names = [("random", "Random sampling (FedAvg)"), ("powd", "Power-of-Choice"), ("oort", "Oort"), ("divfl", "DivFL"), ("abl_A2", r"FedFACS ($\kappa=0$)")]
    rows = []
    for k, nm in names:
        r, t = R[k], T[k]
        rows.append([nm, "%.1f" % r["down"], "%.2f" % r["up"], "%.0f" % r["steps"], "%.1f" % r["fwd_k"], "%.1f" % r["total_gb"],
                     "%.0f (%d/%d)" % (t["uploads"], t["reached"], t["n"]), "%.1f" % t["total_gb"], "%.2f" % r["wall"]])
    cap = (r"Table V. Resources per round and cost to the common target accuracy (45 runs per method: CIFAR-10, FMNIST and MNIST; Dirichlet $\alpha\in\{0.1,0.5\}$ and two-class partitions; five seeds; 100 rounds; $N=100$ clients). "
           "Per round: models downloaded, updates uploaded, local SGD steps, scoring or probing forward passes (thousands). Total GB is the volume of Eq. (23a) without setup traffic. "
           "Cost to target: uploaded updates (runs reaching the target / runs) and total GB, averaged over the runs that reach the target. Time is the simulated elapsed time per round.")
    return tbl(["Method", "Down", "Up", "Steps", "Scoring (k)", "Total GB", "Uploads to target", "GB to target", "s/round"], rows, cap)


def table_u():
    fn = [("random", "Random"), ("powd", "Power-of-Choice"), ("greedy", "Greedy"), ("fairfedcs", "FairFedCS"), ("fedfacs", "FedFACS")]
    rows = []
    for ds, dn in (("cifar10", "CIFAR-10"), ("fmnist", "FMNIST")):
        for k, nm in fn:
            v = F[ds + "|" + k]
            mu = lambda x: float(np.mean(v[x]))
            rows.append([dn, nm, "%.3f" % mu("jfi"), "%.3f" % mu("jfi_q"), "%.1f" % mu("never"), "%.0f" % mu("wait"), "%.1f" % mu("pc_mean"), "%.1f" % mu("pc_std"), "%.1f" % mu("pc_p10")])
    cap = (r"Table U. Participation and outcome fairness in Scenario 3 (noisy clients, IID; mean of 3 seeds, 100 rounds). JFI is Eq. (24) with $q_i=1$ and JFI$_q$ is Eq. (24). "
           r"Client accuracy: mean, standard deviation and 10th percentile (%) of the global model on the held-out local data of each client. The FedFACS runs use the stability weights ($\kappa=1$); the selection rule is the same for all $\kappa$.")
    return tbl(["Dataset", "Method", "JFI", "JFI$_q$", "Never selected (%)", "Longest wait", "Acc. mean", "Acc. s.d.", "Acc. p10"], rows, cap)


def table_t():
    rows = []
    for ds, dn in (("cifar10", "CIFAR-10"), ("fmnist", "FMNIST"), ("mnist", "MNIST")):
        for k, nm in (("random", "Random sampling"), ("abl_A2", r"FedFACS ($\kappa=0$)")):
            v = C[ds + "|" + k]
            rows.append([dn, nm] + ["%.2f" % np.mean(v[x]) for x in ("acc", "rec", "prec", "f1")])
    cap = "Table T. Accuracy and macro-averaged recall, precision and F1 (%) computed from the confusion matrix of the test set (mean of 15 runs per row: three partitions, five seeds)."
    return tbl(["Dataset", "Method", "Accuracy", "Recall", "Precision", "F1"], rows, cap)


def table_s():
    n = A["ff"]
    items = [(r"Cohort size within $[C_{k_{\min}},C_{k_{\max}}]$ in every round", A["bounds"]),
             ("Logged cohort size equals the number of selected clients", A["cohort_eq"]),
             ("Selection counts recomputed from the per-round selections equal the logged counts", A["selcnt_ok"]),
             ("Longest wait recomputed from the per-round selections equals the logged value", A["wait_ok"]),
             ("Uploaded volume equals the sum of the cohort sizes times the model size", A["up_ok"]),
             ("Number of logged rounds equals the configured number of rounds", A["rounds_ok"])]
    rows = [[a, "%d / %d" % (b, n)] for a, b in items]
    cap = "Table S. Consistency of the logged protocol in the %d runs of FedFACS and its ablation variants. Across all %d runs of the reproduction no round was cancelled and no client update was non-finite." % (n, A["runs"])
    return tbl(["Check", "Runs passing"], rows, cap)


def paragraphs_md():
    s = open(os.path.join(P, "paper_overleaf_revised", "sn-article.tex"), encoding="utf8", newline="").read().replace("\r\n", "\n")
    a = s.index(BS + "textbf{Communication and computation cost.}")
    b = s.index(BS + "textbf{Uncertainty penalty.}")
    blk = re.sub(re.escape(BS) + r"begin\{table\}.*?" + re.escape(BS) + r"end\{table\}", "@@T@@", s[a:b], flags=re.S)
    parts = [p.strip() for p in re.split(r"\n\s*\n", blk) if p.strip()]
    tabs = iter([table_v(), table_u(), table_t(), table_s()])
    out = []
    for p in parts:
        out.append(next(tabs) if p == "@@T@@" else B.conv_text(" ".join(p.split("\n"))) + "\n")
    return "\n".join(out)


NOTATION = r"""
# 4. Notation declared by these replacements

| Symbol | Declaration |
|:--|:--|
| $\mathrm{Comm}^t_{\mathrm{down}}$, $\mathrm{Comm}^t_{\mathrm{up}}$, $\mathrm{Comm}^t_{\mathrm{aux}}$ (23a) | NEW: model-download, update-upload and auxiliary traffic of round $t$, in bytes |
| $\mathrm{Comm}_{\mathrm{setup}}$, $\mathrm{Comm}_{\mathrm{cal}}$, $\mathrm{Comm}_{\mathrm{final}}$ (23a) | NEW: setup, calibration (zero for FedFACS) and final-model traffic, in bytes |
| $\mathcal{R}(T)$ (23a) | NEW: set of attempted rounds among the first $T$, including partial and cancelled rounds |
| $\mathrm{Comm}_{\mathrm{total}}(T)$ (23a) | NEW: total communication in bytes over the first $T$ rounds |
| $C_{\mathrm{total}}$ (23) | CHANGED: sum of the cohort sizes $\lvert C_k^t\rvert$ over the first $T$ rounds (uploaded updates) |
| JFI, JFI$_q$ (Table U) | JFI$_q$ is Eq. (24); JFI is Eq. (24) with $q_i=1$. Labels used in Table U only |
| $N$ | CHANGED: client population; replaces the symbols $K$, $n$ and $C$ of the original |
| $r_i^{t+1}$, $\overline{r^{t+1}}$ (7), (19) | CHANGED: idle counter and population mean after round $t$, staged after aggregation and committed with the model |
"""

PREP = r"""
# 5. Prepared answers and open points (internal, not for the manuscript)

- **Does FedFACS reduce communication?** It reduces the uploads (6.2% fewer than random sampling to the common target); the total volume to the target is 5.3 times that of random sampling (198 against 37 GB) and the local computation is 10 times. The wording of the title and the abstract ("communication-efficient") has to be limited to the uploads; this is handled in Replacement 11.
- **Is there a configuration where the total volume is lower?** Not in the reproduction: all candidates download the model and train. A saving in the total volume would need a lighter scoring pass or a subset of candidates; this is outside the present method.
- **Why is the quality-adjusted index below the raw index?** FedFACS serves the clients almost uniformly (raw index 0.999), while the adjusted index is one only for participation proportional to quality.
- **Scenario 4.** The reproduction contains Scenario 3 only; Table U has no Scenario 4 rows.
- **Messages with identifiers.** The simulation is synchronous and single-process; the sentence on identifiers describes a deployment and is introduced with "In a deployment".
- **Reproducibility package.** The runs log the configuration, seeds, per-round selections, cohort sizes, validation loss and accuracy, the mean mixing coefficient and fairness term, the deviation signal and the traffic counters (JSON); the individual fitness scores of every round are not logged, so a package that includes them needs a rerun; a release statement needs the authors' confirmation.
- **Original Table 4.** Its recall and F1 values are not reproduced by Table T (macro-recall equals accuracy on balanced test sets); they are recomputed or removed in Replacement 11.
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
    for rep in (9, 10):
        md.append('\n::: {custom-style="BA-Sub"}\nReplacement %d\n:::\n' % rep)
        k = 0
        for e in [x for x in EDITS if x["rep"] == rep]:
            k += 1
            before, after = B.before_after(e["orig"], e["rev"], e["onums"], e["rnums"])
            line = B.line_of(e["at"][1], e["at"][0])
            md.append('\n::: {custom-style="BA-Edit"}\nReplacement %d, edit %d: %s\n:::\n' % (rep, k, e["title"]))
            md.append('::: {custom-style="BA-Loc"}\nLocation: %s\n:::\n' % (e["loc"] % line))
            md.append('::: {custom-style="BA-Label-Before"}\nBefore (remove)\n:::\n')
            md.append(before)
            md.append('::: {custom-style="BA-Label-After"}\nAfter (put instead)\n:::\n')
            md.append(after)
        if rep == 9:
            lo, lr = alg_lines(ORIG), alg_lines(REV)
            line = B.line_of(ORIG, "Algorithm 2} Server-side")
            md.append('\n::: {custom-style="BA-Edit"}\nReplacement 9, edit %d: Algorithm 2, inputs, outputs and steps\n:::\n' % (k + 1))
            md.append('::: {custom-style="BA-Loc"}\nLocation: Section 4.2, Algorithm 2 (original line %d); changed lines are marked, unchanged lines are shown in plain text.\n:::\n' % line)
            md.append('::: {custom-style="BA-Label-Before"}\nBefore (remove)\n:::\n')
            md.append(alg_md(lo, lr, "Del"))
            md.append('::: {custom-style="BA-Label-After"}\nAfter (put instead)\n:::\n')
            md.append(alg_md(lr, lo, "Add"))
    md.append("\n# 3. New text and tables for Section 5.4 (do not exist in the original paper)\n")
    md.append('::: {custom-style="BA-Note"}\nInsert the four paragraphs and Tables V, U, T and S below in Section 5.4, after the paragraph on participation and aggregation influence. Every number is recomputed from the run logs by tools/ev910.py.\n:::\n')
    md.append(paragraphs_md())
    md.append(NOTATION)
    md.append(PREP)
    return "\n".join(md)


def style_tables(doc):
    widths = [[1.5, 0.45, 0.4, 0.5, 0.6, 0.6, 0.9, 0.6, 0.5], [0.7, 0.9, 0.45, 0.5, 0.6, 0.6, 0.55, 0.55, 0.55], [0.8, 1.6, 0.9, 0.9, 0.9, 0.9], [5.2, 1.2], [2.4, 4.1]]
    for ti, t in enumerate(doc.tables[:5]):
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
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (c_i == 0 or ti in (3, 4) or (ti == 0 and c_i == 0)) else WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.size = Pt(8.5 if ti < 2 else 9)
                        if r_i == 0:
                            run.font.bold = True
        for cell in t.rows[0].cells:
            B.border(cell, top="single", bottom="single")
        for cell in t.rows[n - 1].cells:
            B.border(cell, bottom="single")
        if ti == 1:
            for cell in t.rows[5].cells:
                B.border(cell, bottom="single")
        for gc, w in zip(t._tbl.tblGrid.findall(B.qn("w:gridCol")), widths[ti]):
            gc.set(B.qn("w:w"), str(int(w * 1440)))


def main():
    md_path = os.path.join(WORK, "final910.md")
    open(md_path, "w", encoding="utf8").write(build_md().replace(SP, " "))
    ref = os.path.join(WORK, "ref.docx")
    pandoc = pypandoc.get_pandoc_path()
    subprocess.run([pandoc, "-o", ref, "--print-default-data-file", "reference.docx"], check=True)
    subprocess.run([pandoc, md_path, "-f", "markdown+tex_math_dollars+raw_attribute+fenced_divs+bracketed_spans+pipe_tables", "-o", OUTF,
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
    style_tables(d)
    d.save(OUTF)
    z = subprocess.run(["python", "-c", "import zipfile;x=zipfile.ZipFile(r'%s').read('word/document.xml').decode('utf8');print(x.count('<m:oMath>'),x.count(chr(92)))" % OUTF], capture_output=True, text=True).stdout.strip()
    print("saved", OUTF, "| equations, backslashes:", z, "| tables:", len(d.tables))


if __name__ == "__main__":
    main()
