"""Builds FedFACS_Replacements_5_6.docx (Before/After with locations, declarations, evidence tables, notation).
Sources: paper_overleaf/sn-article.tex (original), paper_overleaf_revised/sn-article.tex (revised),
paper_overleaf_revised/section_5_4_selection_score.tex (new subsection). Native Word equations via pandoc."""
import difflib
import os
import re
import subprocess

import docx
import pypandoc
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

P = r"C:\Users\0xRay\Downloads\paper"
OUT = os.path.join(P, "FedFACS_Replacements_5_6.docx")
WORK = os.path.join(P, "tools", "_work")
os.makedirs(WORK, exist_ok=True)
ORIG = open(os.path.join(P, "paper_overleaf", "sn-article.tex"), encoding="utf8", newline="").read().replace("\r\n", "\n")
REV = open(os.path.join(P, "paper_overleaf_revised", "sn-article.tex"), encoding="utf8", newline="").read().replace("\r\n", "\n")
S54 = open(os.path.join(P, "paper_overleaf_revised", "section_5_4_selection_score.tex"), encoding="utf8", newline="").read().replace("\r\n", "\n")
BS = chr(92)
BSR = re.escape(BS)

# ----------------------------------------------------------------------------- LaTeX -> markdown helpers
MATH = re.compile(r"(\$[^$]+\$)")


def conv_text(s):
    out = []
    for k, part in enumerate(MATH.split(s)):
        if k % 2 == 1:
            out.append(part.replace(BS + BS + "[1.5ex]", BS + BS))
            continue
        t = part
        t = t.replace(BS + "ref{sec:properties}", "4.3").replace(BS + "ref{sec:score_analysis}", "5.4")
        t = t.replace(BS + "ref{tab:cohort}", "Z").replace(BS + "ref{tab:mixing}", "Y").replace(BS + "ref{tab:kl_validity}", "X").replace(BS + "ref{tab:kl_drift}", "X2").replace(BS + "ref{tab:cost}", "V").replace(BS + "ref{tab:fairness}", "U").replace(BS + "ref{tab:cls}", "T").replace(BS + "ref{tab:audit}", "S")
        t = re.sub(BSR + r"ref\{([^}]*)\}", r"\1", t)
        t = t.replace("_", BS + "_")
        t = re.sub(BSR + r"textbf\{([^}]*)\}", r"**\1**", t)
        t = re.sub(BSR + r"textit\{([^}]*)\}", r"*\1*", t)
        t = t.replace(BS + "%", "%").replace("~", " ").replace("--", "\u2013").replace("``", "\u201c").replace("''", "\u201d")
        out.append(t)
    return "".join(out)


TOK = re.compile(r"\$[^$]+\$[^\s$]*|\S+")


def eq_clean(body):
    body = re.sub(BSR + r"label\{[^}]*\}", "", body)
    body = re.sub(BSR + r"tag\{[^}]*\}", "", body)
    body = body.replace(BS + BS + "[1.5ex]", BS + BS)
    return body.strip()


def eq_norm(body):
    return re.sub(r"\s+", "", eq_clean(body))


def parse_block(text, nums):
    nums = list(nums)
    units = []
    pos = 0

    def text_units(t):
        t = "\n".join(l for l in t.split("\n") if not l.lstrip().startswith("%"))
        paras = [p for p in re.split(r"\n\s*\n", t) if p.strip()]
        for i, p in enumerate(paras):
            if i:
                units.append(("P",))
            for tok in TOK.findall(p):
                units.append(("T", tok))

    for m in re.finditer(BSR + r"begin\{equation\}(.*?)" + BSR + r"end\{equation\}", text, re.S):
        text_units(text[pos:m.start()])
        units.append(("E", eq_norm(m.group(1)), eq_clean(m.group(1)), nums.pop(0)))
        pos = m.end()
    text_units(text[pos:])
    assert not nums, nums
    return units


def key(u):
    return u[1] if u[0] == "E" else ("\u00b6" if u[0] == "P" else u[1])


def render(units, marks, style_inline, style_block):
    """markdown for a unit list; marks = set of indexes to highlight."""
    lines, para = [], []
    state = {"run": []}

    def flush_run():
        if state["run"]:
            para.append('[%s]{custom-style="%s"}' % (" ".join(state["run"]), style_inline))
            state["run"] = []

    def flush_para():
        flush_run()
        if para:
            lines.append(" ".join(para))
            lines.append("")
            para.clear()

    for i, u in enumerate(units):
        if u[0] == "P":
            flush_para()
        elif u[0] == "E":
            flush_para()
            md = "$$ %s \\qquad (%s) $$" % (u[2], u[3])
            if i in marks:
                lines.append('::: {custom-style="%s"}' % style_block)
                lines.append(md)
                lines.append(":::")
            else:
                lines.append(md)
            lines.append("")
        else:
            c = conv_text(u[1])
            if i in marks:
                state["run"].append(c)
            else:
                flush_run()
                para.append(c)
    flush_para()
    return "\n".join(lines)


def before_after(orig, rev, onums, rnums):
    a, b = parse_block(orig, onums), parse_block(rev, rnums)
    sm = difflib.SequenceMatcher(None, [key(u) for u in a], [key(u) for u in b], autojunk=False)
    da, db = set(), set()
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ("delete", "replace"):
            da.update(range(i1, i2))
        if op in ("insert", "replace"):
            db.update(range(j1, j2))
    return render(a, da, "Del", "DelBlock"), render(b, db, "Add", "AddBlock")


def line_of(text, sub):
    return text.count("\n", 0, text.index(sub)) + 1


def sentence(text, k):
    i = text.index(k)
    a = max(text.rfind(". ", 0, i) + 2 if text.rfind(". ", 0, i) >= 0 else 0, text.rfind("\n", 0, i) + 1)
    b1 = text.find(". ", i)
    b2 = text.find("\n", i)
    b = min(x for x in (b1 + 1 if b1 >= 0 else len(text), b2 if b2 >= 0 else len(text)))
    return text[a:b]


def span(text, start, end, from_marker=None):
    i = text.index(from_marker or start)
    j = text.index(end, i) + len(end)
    return text[i:j]


# ----------------------------------------------------------------------------- the seven edits
EQ_END = lambda lab: BS + "label{" + lab + "}\n" + BS + "end{equation}"
EDITS = [
    dict(rep=5, title="Abstract: wording of the KL utility", loc="Abstract (original line %d)",
         orig=sentence(ORIG, "multi-objective fitness function combining"), rev=sentence(REV, "multi-objective fitness function combining"),
         onums=[], rnums=[], at=("multi-objective fitness function combining", ORIG)),
    dict(rep=5, title="Introduction: definition of the client utility", loc="Section 1, contributions paragraph (original line %d)",
         orig=sentence(ORIG, "Client utility is quantified by"), rev=sentence(REV, "Client utility is quantified by"),
         onums=[], rnums=[], at=("Client utility is quantified by", ORIG)),
    dict(rep=5, title="Section 4.2: KL score, Eqs. (5a), (5b), (5), and its effect on the priority", loc="Section 4.2, first paragraph and Eq. (5) (original line %d)",
         orig=span(ORIG, EQ_END("eq:kl"), EQ_END("eq:kl"), "Each participating client is denoted by"),
         rev=span(REV, "keeps every client participating.", "keeps every client participating.", "% REVISED (Replacement 5): KL"),
         onums=["5"], rnums=["5a", "5b", "5"], at=("Each participating client is denoted by", ORIG)),
    dict(rep=5, title="Section 4.2: uncertainty penalty, stability score and fitness, Eqs. (12a), (12), (13), (14)", loc="Section 4.2 (original line %d)",
         orig=span(ORIG, EQ_END("eq:fitness"), EQ_END("eq:fitness"), "Client-side uncertainty is introduced into the fitness score"),
         rev=span(REV, EQ_END("eq:fitness"), EQ_END("eq:fitness"), "% REVISED (Replacement 5/6): batch variance"),
         onums=["12", "13", "14"], rnums=["12a", "12", "13", "14"], at=("Client-side uncertainty is introduced into the fitness score", ORIG)),
    dict(rep=6, title="Introduction: wording of the control mechanism", loc="Section 1, contributions paragraph (original line %d)",
         orig=sentence(ORIG, "FedFACS balances utility and fairness using a"), rev=sentence(REV, "FedFACS balances utility and fairness using a"),
         onums=[], rnums=[], at=("FedFACS balances utility and fairness using a", ORIG)),
    dict(rep=6, title="Section 4.2: feedback rule and priority, Eqs. (8) and (9)", loc="Section 4.2 (original line %d)",
         orig=span(ORIG, EQ_END("eq:priority"), EQ_END("eq:priority"), "The proposed control mechanism is inspired by the Lyapunov"),
         rev=span(REV, EQ_END("eq:priority"), EQ_END("eq:priority"), "% REVISED (Replacement 6)"),
         onums=["8", "9"], rnums=["8", "9"], at=("The proposed control mechanism is inspired by the Lyapunov", ORIG)),
]

# ----------------------------------------------------------------------------- narrative blocks
HEAD = r"""
::: {custom-style="BA-Title"}
FedFACS: Replacements 5 and 6 (final text, declarations and evidence)
:::

::: {custom-style="BA-Note"}
Scope. Replacement 5 covers the utility score, the uncertainty penalty and the fitness (Eqs. (5), (12)–(14)); Replacement 6 covers the feedback rule and the priority (Eqs. (8)–(9)). Locations refer to the original sn-article.tex. Evidence comes from our reproduced runs (ResNet-18 with frozen early layers, 100 clients, 100 rounds, cohorts of 5 to 10 clients; 3 seeds for ablations, 5 for the main comparison, 2 for the parameter-drift study; 95% bootstrap intervals); the manuscript must state that its numbers come from this implementation. Colours: [red]{custom-style="Del"} = removed, [green]{custom-style="Add"} = added.
:::

::: {custom-style="BA-Note"}
NEW ELEMENTS. The original paper has no Section 4.3 and no Section 5.4, and none of Tables X, X2, Y, nor Eqs. (5a), (5b), (12a). They are new; their full text is given in parts 3 and 3a of this file and must be inserted: Section 4.3 after Section 4.2; Section 5.4 at the end of Section 5, before the Conclusion.
:::

::: {custom-style="BA-Note"}
Consequence for Replacements 8–9. Eq. (18) is generalised with a coefficient κ: κ = 0 gives sample-count weights and κ = 1 the stability weights. All reported results use κ = 0, because stability weights increased the oscillation of the global model at the end of training (Section 5.4, Aggregation weights). The wording of Replacements 8–9, the abstract and the conclusion must follow this choice.
:::

# 1. What each comment receives: fix, location, evidence, declaration
"""

COMMENTS = [
    ("R1-04 and R2-06: the utility score and its sum over x ∈ X",
     "Eq. (5) is replaced by a three-level definition: per-example divergence over the label set (5a), batch mean (5b) and sample-weighted client score (5). The text states what a large and a small value mean and how the score enters the priority.",
     "Section 4.2, Eqs. (5a), (5b), (5); Abstract and Introduction wording.",
     "New subsection 5.4: rank correlation of the score with the marginal validation-loss gain (Table X), comparison with the global cross-entropy and with the parameter drift (Tables X and X2), behaviour under label noise.",
     "The KL score is a label-free indicator of the benefit of an update; its association with the marginal gain was measured, and unlike a loss-based score it is not misled by corrupted labels."),
    ("R1-05: the uncertainty penalty",
     "Eq. (12) is the sample variance of the batch scores with B ≥ 2 and the batch mean (12a); the fitness (14) is built on the renamed priority Π and the penalty.",
     "Section 4.2, Eqs. (12a), (12), (13), (14).",
     "Section 5.4, Uncertainty penalty: effect of removing the penalty under the final aggregation and its rank AUC for label noise.",
     "The penalty is a stabilising term in the fitness, evaluated by ablation."),
    ("R1-02, R2-04 and R2-20: the control law",
     "Eq. (8) has the positive denominator λF + |ν(ΔKL − F)|, with λ = 1, β = 0.9 and a⁰ = 0.5 stated; clip(x, 0, 1) is defined; the direction of the feedback is derived; the Lyapunov wording is removed from the Abstract, the Introduction and Section 4.2.",
     "Section 4.2, Eq. (8) and the paragraph below it.",
     "In the 96 main runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2% of the 4,316 rounds with ν > 0; Table Y.",
     "The rule is well posed (Proposition 1) and bounded, and its effect follows Eq. (8)."),
    ("R2-05: the scales of F and ΔKL",
     "The priority of Eq. (9) is stated with the quantities that determine it: at the diagnostic rounds the fairness term has a median of 1.88, the utility score 0.73 and the coefficient 0.10, so that the weighted utility term is a median 3% of the weighted fairness term and the priority is rank-correlated with F (Spearman 0.92). Two alternatives with comparable weights were implemented and evaluated.",
     "Section 4.2, paragraph before Eq. (9); Section 5.4.",
     "Table Y: a constant a = 0.5 and a = 1 lower the Jain index to 0.92–0.94 and 0.35–0.56. A rank-normalised priority with the waiting-time guard gave a Jain index of 0.94–0.99, longest waits of 17–20 rounds and no accuracy gain.",
     "The regime in which the priority is determined mainly by the waiting time is the configuration that preserves near-uniform participation at the highest accuracy; the feedback rule reaches it without tuning the coefficient."),
    ("R2-18: theoretical analysis",
     "Section 4.3 adds Propositions 1 to 3 (well-posedness, bounded waiting under the waiting-time guard, bounded movement of the aggregate).",
     "Section 4.3 (see FedFACS_R2-18_Analysis_and_Guarantees.docx).",
     "In all runs of the unmodified rule the longest wait (17 rounds for N = 100) stayed below the guard threshold R = 20, so the reported results are those of the unguarded rule.",
     "FedFACS guarantees a maximum waiting time; convergence is evaluated empirically."),
]

REP6_ONLY = True
HEAD6 = r"""
::: {custom-style="BA-Title"}
FedFACS: Replacement 6 (feedback rule and priority, Eqs. (8) and (9))
:::

::: {custom-style="BA-Note"}
Scope. Everything that belongs to Replacement 6: the sentence of the Introduction and the paragraph of Section 4.2 that define the feedback rule and the priority, the fix and declaration for each comment it answers, the evidence tables, the notation and the prepared answers. Locations refer to the original sn-article.tex. Evidence comes from our reproduced runs (ResNet-18 with frozen early layers, 100 clients, 100 rounds, cohorts of 5 to 10 clients; 3 seeds; 95% bootstrap intervals); the manuscript must state that its numbers come from this implementation. Table Y is measured with sample-count aggregation (kappa = 0 in Eq. (18)). Colours: [red]{custom-style="Del"} = removed, [green]{custom-style="Add"} = added.
:::

::: {custom-style="BA-Note"}
NEW ELEMENTS. The original paper has no Section 4.3, no Section 5.4 and no Table Y. They are new: the full text of Section 4.3 is in part 4a of this file (insert it after Section 4.2); the passage of Section 5.4 and Table Y that belong to this replacement are in part 3 (Section 5.4 is inserted at the end of Section 5, before the Conclusion).
:::

# 1. What each comment receives: fix, location, evidence, declaration
"""

NOTATION6 = r"""
# 4. Notation declared by this replacement

| Symbol | Declaration |
|:--|:--|
| $a_i^t$, $\beta=0.9$, $\lambda=1$, $a_i^0=0.5$ | mixing coefficient, smoothing constant, fairness regularisation (now specified) |
| $\mathrm{clip}(x,0,1)$ | CHANGED: projection onto $[0,1]$, $\min\{1,\max\{0,x\}\}$ (original wrote $\mathrm{clip}(a,1,0)$) |
| $\Pi_i^t$ | CHANGED: priority score of client $i$ at round $t$ (was $P_i^t$, which clashed with the prediction $P(x)$) |
| $\nu^t$ | deviation signal (Replacement 3), the feedback input of Eq. (8) |
| $F_i^t\ge 1$ | fairness term (Replacement 4), larger than $\Delta KL_i^t$ by construction |
| $\Delta KL_i^t$ | utility score (Replacement 5) |
"""

PREP6 = r"""
# 5. Prepared answers (internal, not for the manuscript)

- **Is the utility term small?** The score itself is not (median 0.73, against 1.88 for F); its weighted contribution is, because the feedback rule keeps the coefficient at a median of 0.10: a·ΔKL is a median 3% of (1−a)·F, and the priority is rank-correlated with F (0.92). A comparable weight (a constant of 0.5, or rank normalisation) lowered the Jain index and did not raise accuracy (Table Y).
- **Is the controller necessary?** It reaches the best operating point without tuning: no constant coefficient is significantly more accurate than the rule in any comparison, and the rule is significantly more accurate in some (a = 0.05 on CIFAR-10, a = 0.10 on FMNIST in the last 10 rounds).
- **Is the direction of the feedback correct?** When the deviation signal is positive the mean mixing coefficient decreased in 98.2% of 4,316 rounds (96 main runs), as Eq. (8) predicts.
- **No Lyapunov analysis?** The mechanism is presented as a bounded feedback rule; its properties that can be proved (positive denominator, coefficient in [0,1], bounded waiting under the guard) are in Section 4.3.
"""

PREP = r"""
# 5. Prepared answers (internal, not for the manuscript)

- **Is the utility term small?** Its weighted contribution is (a·ΔKL is a median 3% of (1−a)·F, Section 5.4); the utility term orders clients with similar waiting times, and a comparable weight lowered the Jain index and did not raise accuracy.
- **Why KL and not the loss?** Both predict the gain under label skew; under label noise only KL is not misled (ρ = +0.12 against −0.77). Selecting with a loss-based utility is not detectably different in accuracy.
- **Why sample-count weights?** Stability weights concentrate the weight on few clients and increased the oscillation of the global model; sample-count weights improved the last-10-round accuracy in 5 of 9 settings and decreased it in none.
- **Where are the baselines?** Main comparison tables (Replacement 11) are in section_5_main_tables.tex.
"""

NOTATION = r"""
# 4. Notation declared by these replacements

| Symbol | Declaration |
|:--|:--|
| $\mathrm{KL}(P\Vert Q)$ | NEW: Kullback–Leibler divergence, nonnegative, zero only if $P=Q$, asymmetric |
| $\mathcal{Y}$, $P_i^t(c\mid x)$, $Q^t(c\mid x)$ | NEW: label set; class probabilities of the locally trained model and of the unchanged global model |
| $d_i^t(x)$ (5a), $X_{i,b}^t$, $B\ge 2$, $KL_{i,b}^t$ (5b) | NEW: per-example divergence, scoring batch $b$, number of batches, batch score |
| $\Delta KL_i^t$ (5) | CHANGED: sample-weighted divergence between local and global predictions after local training; $\Delta$ is a label, not a change over rounds |
| $\overline{KL}_i^t$ (12a), $\sigma_i^2$ (12), $\mu\ge 0$ | NEW: batch mean; CHANGED: sample variance of the batch scores; penalty coefficient |
| $s_i^t$ (13), $Fitness_i^t$ (14) | stability score (may be negative); composite fitness built on $\Pi_i^t$ |
| $a_i^t$, $\beta=0.9$, $\lambda=1$, $a_i^0=0.5$ | mixing coefficient, smoothing constant, fairness regularisation (now specified) |
| $\mathrm{clip}(x,0,1)$ | CHANGED: projection onto $[0,1]$ (original wrote $\mathrm{clip}(a,1,0)$) |
| $\Pi_i^t$ | CHANGED: priority score (was $P_i^t$, which clashed with the prediction $P(x)$) |
| $\nu^t$, $F_i^t$ | deviation signal (Replacement 3) and fairness term (Replacement 4) |
| $\kappa\in[0,1]$, $q_i^t$ | NEW (Eq. (18)): weighting coefficient ($\kappa=0$ sample-count weights, used) and stability weights |
| $g_i^t$ | NEW (Section 5.4): marginal gain, the reduction in global validation loss when the update of client $i$ alone is added with weight $1/m_t$ |
"""

# tables of Section 5.4 (values identical to section_5_4_selection_score.tex)
TABLES_MD = r"""
Table X. Spearman correlation between a client indicator and the marginal validation-loss gain of its update, pooled over datasets and seeds ($n$ round-runs; 95% bootstrap intervals in brackets; higher is better).

| Data partition | $n$ | KL score ↑ | Global cross-entropy ↑ |
|:--|--:|:--|:--|
| Dirichlet $\alpha=0.1$ | 90 | 0.50 [0.42, 0.58] | **0.64** [0.59, 0.69] |
| Dirichlet $\alpha=0.5$ | 90 | 0.39 [0.33, 0.45] | **0.50** [0.45, 0.55] |
| Two classes per client | 90 | 0.73 [0.69, 0.77] | **0.75** [0.71, 0.79] |
| Label noise (0–45%) | 18 | **0.12** [−0.09, 0.33] | −0.77 [−0.88, −0.65] |

Table X2. KL score versus parameter drift as predictors of the marginal gain (Spearman $\rho$; 2 seeds, 12 round-runs per row; last column: paired difference and 95% bootstrap interval; higher is better).

| Dataset | Data partition | KL score ↑ | Drift ↑ | KL − drift ↑ |
|:--|:--|--:|--:|:--|
| CIFAR-10 | Dirichlet $\alpha=0.1$ | 0.41 | 0.24 | 0.17 [−0.17, 0.43] |
| | Two classes per client | 0.71 | 0.33 | **0.37** [0.32, 0.43] |
| FMNIST | Dirichlet $\alpha=0.1$ | 0.56 | 0.64 | −0.08 [−0.34, 0.11] |
| | Two classes per client | 0.75 | 0.50 | **0.25** [0.09, 0.46] |

Table Y. Feedback rule versus constant mixing coefficients (Dirichlet $\alpha=0.5$, sample-count aggregation; mean ± standard deviation over 3 seeds). Acc.: test accuracy at the round of best validation accuracy; Last-10: mean test accuracy of the last 10 rounds; $a=1$ removes the fairness term. Bold: best value per dataset and column (ties not marked).

| Dataset | Rule | Acc. (%) ↑ | Last-10 (%) ↑ | JFI ↑ | Never sel. (%) ↓ | Max. wait ↓ | Weakest 10% (%) ↑ |
|:--|:--|--:|--:|--:|--:|--:|--:|
| CIFAR-10 | FedFACS (feedback rule) | **72.13** ± 0.23 | 70.17 ± 0.83 | 0.997 | 0 | 11.0 | 63.2 ± 1.5 |
| | Constant $a=0.05$ | 71.33 ± 0.74 | 70.04 ± 0.78 | **0.999** | 0 | 10.0 | 63.2 ± 1.0 |
| | Constant $a=0.10$ | 72.01 ± 0.36 | **70.46** ± 0.33 | 0.998 | 0 | 10.0 | 60.5 ± 3.2 |
| | Constant $a=0.5$ | 70.88 ± 0.74 | 68.81 ± 0.95 | 0.916 | 0 | 15.7 | 57.3 ± 4.1 |
| | Constant $a=1$ (no fairness) | 69.54 ± 0.35 | 65.58 ± 0.72 | 0.557 | 10.0 | 100 | 55.2 ± 1.3 |
| FMNIST | FedFACS (feedback rule) | **85.54** ± 0.34 | **84.57** ± 0.55 | 0.998 | 0 | 10.7 | 76.3 ± 2.2 |
| | Constant $a=0.05$ | 85.49 ± 0.47 | 84.18 ± 0.66 | 0.998 | 0 | 10.3 | 73.3 ± 1.7 |
| | Constant $a=0.10$ | 85.24 ± 0.39 | 83.67 ± 0.42 | 0.998 | 0 | **10.0** | 73.9 ± 4.0 |
| | Constant $a=0.5$ | 85.32 ± 0.33 | 83.04 ± 1.13 | 0.941 | 0 | 14.3 | **76.6** ± 2.0 |
| | Constant $a=1$ (no fairness) | 83.36 ± 1.09 | 79.00 ± 0.14 | 0.346 | 20.3 | 100 | 68.2 ± 6.3 |
"""


NEW43_NOTE = ('::: {custom-style="BA-Note"}' + chr(10) + 'NEW SECTION: Section 4.3 does not exist in the original paper. Insert it as a new subsection after Section 4.2 and before Section 5 (Experimental Evaluation). '
              'Its full text follows; the replacements refer to it as "Section 4.3".' + chr(10) + ':::' + chr(10))


def section43_md():
    NLC = chr(10)
    i = REV.index(BS + "subsection{Properties of FedFACS}")
    j = REV.index(BS + "section{Experimental Evaluation}")
    t = NLC.join(l for l in REV[i:j].split(NLC) if not l.lstrip().startswith("%"))
    t = re.sub(BSR + r"subsection\{[^}]*\}" + BSR + r"label\{[^}]*\}", "", t)
    t = t.replace(BS + "hfill$" + BS + "square$", "$" + BS + "square$")
    paras = [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]
    out = ['::: {custom-style="BA-Sub"}' + NLC + '4.3 Properties of FedFACS (new subsection)' + NLC + ':::' + NLC]
    for p in paras:
        out.append(conv_text(" ".join(p.split(NLC))) + NLC)
    return NLC.join(out)


def section54_md():
    t = "\n".join(l for l in S54.split("\n") if not l.lstrip().startswith("%"))
    t = re.sub(BSR + r"begin\{table\}.*?" + BSR + r"end\{table\}", "@@TABLE@@", t, flags=re.S)
    t = re.sub(BSR + r"subsection\{[^}]*\}" + BSR + r"label\{[^}]*\}", "", t)
    paras = [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]
    out = []
    tables_done = 0
    for p in paras:
        if p == "@@TABLE@@":
            tables_done += 1
            if tables_done == 1:
                out.append("@@TABLES@@")
            continue
        p = " ".join(p.split("\n"))
        out.append(conv_text(p))
        out.append("")
    return "\n\n".join(out)


def build_md(only6=False):
    md = [HEAD6 if only6 else HEAD]
    for n, (t, fix, where, ev, decl) in enumerate([COMMENTS[i] for i in (2, 3, 4)] if only6 else COMMENTS, 1):
        md.append("**%s**\n" % t)
        md.append("- Fix: %s" % fix)
        md.append("- Where: %s" % where)
        md.append("- Evidence: %s" % ev)
        md.append("- Declaration: %s\n" % decl)
    md.append("\n# 2. Edits: before and after, with locations\n")
    for rep in ((6,) if only6 else (5, 6)):
        md.append('\n::: {custom-style="BA-Sub"}\nReplacement %d\n:::\n' % rep)
        for k, e in enumerate([x for x in EDITS if x["rep"] == rep], 1):
            before, after = before_after(e["orig"], e["rev"], e["onums"], e["rnums"])
            line = line_of(e["at"][1], e["at"][0])
            md.append('\n::: {custom-style="BA-Edit"}\nReplacement %d, edit %d: %s\n:::\n' % (rep, k, e["title"]))
            md.append('::: {custom-style="BA-Loc"}\nLocation: %s\n:::\n' % (e["loc"] % line))
            md.append('::: {custom-style="BA-Label-Before"}\nBefore (remove)\n:::\n')
            md.append(before)
            md.append('::: {custom-style="BA-Label-After"}\nAfter (put instead)\n:::\n')
            md.append(after)
    if only6:
        md.append("\n# 3. Evidence (Section 5.4, paragraph and Table Y)\n")
        md.append('::: {custom-style="BA-Note"}\nThese passages belong to subsection 5.4 (Analysis of the selection score); the full subsection is in the Replacement 5 file.\n:::\n')
        t = "\n".join(l for l in S54.split("\n") if not l.lstrip().startswith("%"))
        t = re.sub(BSR + r"begin\{table\}.*?" + BSR + r"end\{table\}", "@@TABLE@@", t, flags=re.S)
        i0 = t.index(BS + "textbf{Fairness term and mixing coefficient.}")
        i1 = t.index("@@TABLE@@", i0) if "@@TABLE@@" in t[i0:] else len(t)
        para = " ".join(t[i0:i1].split("\n"))
        md.append(conv_text(para.strip()))
        md.append("")
        md.append(TABLES_MD[TABLES_MD.index("Table Y."):])
        md.append(conv_text("In the 96 main runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2" + BS + "% of the 4,316 rounds in which $" + BS + "nu^t>0$, as Eq.~(8) predicts."))
        md.append(chr(10) + "# 4a. New section to insert: 4.3" + chr(10))
        md.append(NEW43_NOTE)
        md.append(section43_md())
        md.append(NOTATION6)
        md.append(PREP6)
        return "\n".join(md)
    md.append("\n# 3. New subsection 5.4 (insert at the end of Section 5, before the Conclusion)\n")
    md.append('::: {custom-style="BA-Note"}\nHeading: 5.4 Analysis of the selection score. The three tables below belong to this subsection (LaTeX source: section_5_4_selection_score.tex).\n:::\n')
    body = section54_md().replace("@@TABLES@@", TABLES_MD)
    md.append(body)
    md.append(chr(10) + "# 3a. New section to insert: 4.3" + chr(10))
    md.append(NEW43_NOTE)
    md.append(section43_md())
    md.append(NOTATION)
    md.append(PREP)
    return "\n".join(md)


# ----------------------------------------------------------------------------- docx styling
def set_style_shading(style, fill):
    pPr = style.element.get_or_add_pPr()
    for e in pPr.findall(qn("w:shd")):
        pPr.remove(e)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def char_style(doc, name, color, fill, strike=False, bold=False):
    st = doc.styles[name]
    st.font.color.rgb = RGBColor.from_string(color)
    st.font.strike = strike
    st.font.bold = bold
    rPr = st.element.get_or_add_rPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    rPr.append(shd)


def para_style(doc, name, size=None, bold=None, italic=None, color=None, fill=None, before=None, after=None):
    st = doc.styles[name]
    if size:
        st.font.size = Pt(size)
    if bold is not None:
        st.font.bold = bold
    if italic is not None:
        st.font.italic = italic
    if color:
        st.font.color.rgb = RGBColor.from_string(color)
    if fill:
        set_style_shading(st, fill)
    if before is not None:
        st.paragraph_format.space_before = Pt(before)
    if after is not None:
        st.paragraph_format.space_after = Pt(after)


def border(cell, **kw):
    tcPr = cell._tc.get_or_add_tcPr()
    b = tcPr.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders")
        tcPr.append(b)
    for edge, val in kw.items():
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), val)
        e.set(qn("w:sz"), "8" if val == "single" else "0")
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), "000000")
        b.append(e)


def style_tables(doc, kinds=(0, 1, 2, 3)):
    allw = [[1.8, 0.45, 2.1, 2.1], [0.9, 2.0, 0.8, 0.8, 1.9], [0.75, 1.6, 0.8, 0.8, 0.55, 0.65, 0.6, 0.8], [2.4, 4.1]]
    allleft = [[0], [0, 1], [0, 1], [0, 1]]
    widths = [allw[k] for k in kinds]
    left = [allleft[k] for k in kinds]
    isy = [k == 2 for k in kinds]
    isx2 = [k == 1 for k in kinds]
    isnot = [k == 3 for k in kinds]
    for ti, t in enumerate(doc.tables[:len(kinds)]):
        t.autofit = False
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        t._tbl.tblPr.append(lay)
        n = len(t.rows)
        for r_i, row in enumerate(t.rows):
            for c_i, cell in enumerate(row.cells):
                cell.width = Inches(widths[ti][c_i])
                border(cell, top="nil", bottom="nil", left="nil", right="nil")
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(1)
                    p.paragraph_format.space_after = Pt(1)
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (c_i in left[ti] or isnot[ti]) else WD_ALIGN_PARAGRAPH.CENTER
                    for run in p.runs:
                        run.font.size = Pt(9)
                        if r_i == 0:
                            run.font.bold = True
        for cell in t.rows[0].cells:
            border(cell, top="single", bottom="single")
        for cell in t.rows[n - 1].cells:
            border(cell, bottom="single")
        if isy[ti]:
            for cell in t.rows[6].cells:
                border(cell, top="single")
        if isx2[ti]:
            for cell in t.rows[3].cells:
                border(cell, top="single")
        for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), widths[ti]):
            gc.set(qn("w:w"), str(int(w * 1440)))


def main(only6=False):
    OUTF = os.path.join(P, "FedFACS_Replacement_6.docx") if only6 else OUT
    md_path = os.path.join(WORK, "final6.md" if only6 else "final56.md")
    open(md_path, "w", encoding="utf8").write(build_md(only6))
    ref = os.path.join(WORK, "ref.docx")
    pandoc = pypandoc.get_pandoc_path()
    subprocess.run([pandoc, "-o", ref, "--print-default-data-file", "reference.docx"], check=True)
    subprocess.run([pandoc, md_path, "-f", "markdown+tex_math_dollars+raw_attribute+fenced_divs+bracketed_spans", "-o", OUTF,
                    "--reference-doc=" + ref, "--columns=300"], check=True)
    d = docx.Document(OUTF)
    for name in ("BA-Title", "BA-Sub", "BA-Note", "BA-Edit", "BA-Loc", "BA-Label-Before", "BA-Label-After", "DelBlock", "AddBlock"):
        if name not in [s.name for s in d.styles]:
            raise SystemExit("style missing: " + name)
    para_style(d, "BA-Title", size=16, bold=True, color="1F3864", after=8)
    para_style(d, "BA-Sub", size=13, bold=True, color="1F3864", before=10, after=4)
    para_style(d, "BA-Note", size=10, italic=True, fill="EEF3F8", before=4, after=6)
    para_style(d, "BA-Edit", size=11, bold=True, color="1F3864", before=10, after=2)
    para_style(d, "BA-Loc", size=9.5, italic=True, color="595959", after=3)
    para_style(d, "BA-Label-Before", size=10, bold=True, color="C00000", before=4, after=1)
    para_style(d, "BA-Label-After", size=10, bold=True, color="00793A", before=4, after=1)
    para_style(d, "DelBlock", fill="F8D7D7")
    para_style(d, "AddBlock", fill="D9F0DF")
    char_style(d, "Del", "C00000", "FBE4E4", strike=True)
    char_style(d, "Add", "00793A", "DDF3E3", bold=True)
    style_tables(d, (2, 3) if only6 else (0, 1, 2, 3))
    d.save(OUTF)
    n_eq = subprocess.run(["python", "-c", "import zipfile;print(zipfile.ZipFile(r'%s').read('word/document.xml').decode('utf8').count('<m:oMath>'))" % OUTF],
                          capture_output=True, text=True).stdout.strip()
    print("saved", OUTF, "| equations:", n_eq)


if __name__ == "__main__":
    import sys
    main(len(sys.argv) > 1 and sys.argv[1] == "6")
