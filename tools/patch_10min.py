"""Replacement 10, condensed: one table (Table V) with the cost and the participation, short metric definitions. Numbers from ev910.json.
LaTeX in this file uses '@' for the backslash; the genuine tabular preamble characters are restored below."""
import json
import os
import shutil

P = r"C:\Users\0xRay\Downloads\paper"
BS = chr(92)
O = json.load(open(os.path.join(P, "tools", "_work", "ev910.json")))
R, T, PT = O["resource"], O["target"], O["part"]
ff, rd, tf, tr = R["abl_A2"], R["random"], T["abl_A2"], T["random"]


def L(s):
    return s.replace("@", BS)


names = [("random", "Random sampling (FedAvg)"), ("powd", "Power-of-Choice"), ("oort", "Oort"), ("divfl", "DivFL"), ("abl_A2", "FedFACS ($@kappa=0$)")]
rows = []
for k, nm in names:
    r, t, p = R[k], T[k], PT[k]
    rows.append("%s & %.1f & %.2f & %.0f & %.1f & %.0f & %.1f & %.3f & %.1f \\\\" % (nm, r["down"], r["up"], r["steps"], r["total_gb"], t["uploads"], t["total_gb"], p["jfi"], p["never"]))

TABLE = (BS + "begin{table}[!htbp]\n" + BS + "centering\n" + BS + "footnotesize\n" + BS + "setlength{" + BS + "tabcolsep}{2.5pt}\n" + BS + "renewcommand{" + BS + "arraystretch}{1.08}\n"
         + L("@caption{Communication, computation and participation of the methods (45 runs per method: CIFAR-10, FMNIST and MNIST; Dirichlet $@alpha@in@{0.1,0.5@}$ and two-class partitions; five seeds; 100 rounds; $N=100$ clients). "
             "Down and Up: models sent to the clients and updates uploaded per round. Steps: local SGD steps per round. Total GB: $@mathrm{Comm}_{@mathrm{total}}(100)$ of Eq.~(23a). "
             "Uploads and GB to target: $C_{@mathrm{total}}$ of Eq.~(23) and $@mathrm{Comm}_{@mathrm{total}}$ at the first round that reaches the common target accuracy, averaged over the runs that reach it. "
             "JFI: Eq.~(24) with $q_i=1$ on the selection counts. Never: percentage of clients with $p_i=0$.}\n@label{tab:cost}\n")
         + BS + "begin{tabular*}{" + BS + "journalfloatwidth}{@{" + BS + "extracolsep{" + BS + "fill}}lcccccccc@{}}\n"
         + L("@toprule\nMethod & Down & Up & Steps & Total GB & Uploads to target & GB to target & JFI & Never (\\%) \\\\\n@midrule\n") + "\n".join(rows) + "\n"
         + L("@bottomrule\n@end{tabular*}\n@end{table}"))

SAVE = 100 * (1 - tf["uploads"] / tr["uploads"])
PARA = L("@textbf{Communication, computation and participation.} Table~@ref{tab:cost} compares the methods under one communication model. FedFACS sends the model to all $N=100$ candidates and trains all of them, "
         "so that its downloads and local steps per round are %.1f times those of random sampling, while its uploads are %.2f per round against %.0f. "
         "To the common target accuracy it uploads %.0f updates against %.0f (%.1f@%% fewer) and $@mathrm{Comm}_{@mathrm{total}}$ is %.0f against %.0f~GB, since every candidate receives and trains the model; the saving of FedFACS is in the uploaded updates. "
         "Its JFI with $q_i=1$ is %.3f against %.3f for random sampling, and every client is selected at least once." % (
             ff["steps_rel"], ff["up"], rd["up"], tf["uploads"], tr["uploads"], SAVE, tf["total_gb"], tr["total_gb"], PT["abl_A2"]["jfi"], PT["random"]["jfi"]))

NEW_EQ = L("""The total communication in bytes over the first $T$ rounds is
@begin{equation}
@mathrm{Comm}_{@mathrm{total}}(T)=@sum_{t=1}^{T}@left(@mathrm{Comm}^t_{@mathrm{down}}+@mathrm{Comm}^t_{@mathrm{up}}+@mathrm{Comm}^t_{@mathrm{aux}}@right)
@tag{23a}
@end{equation}
where $@mathrm{Comm}^t_{@mathrm{down}}$ is the volume of the models sent to the clients in round $t$, $@mathrm{Comm}^t_{@mathrm{up}}$ that of the updates uploaded by the selected clients and $@mathrm{Comm}^t_{@mathrm{aux}}$ that of the scores and control messages. Local training steps and scoring forward passes are counted separately (Table~@ref{tab:cost}).""")

NEW_JFI = L("""Therefore $JFI = 1$ means participation proportional to quality, which equals equal participation only when all $q_i$ are equal; equality of participation is measured by Eq.~(24) with $q_i=1$. The minimum value is $1/N$, and a value between $0.5$ and $1$ can also arise when some clients are never served (serving 90 of 100 equal-quality clients uniformly gives $0.9$). Because $q_i$ depends on the noise level, JFI differences may partly reflect selection by data quality. The percentage of clients that are never selected is reported with the index (Table~@ref{tab:cost}).""")


def cut(s, a, b, new, inclusive_b=True):
    i = s.index(a)
    j = s.index(b, i) + (len(b) if inclusive_b else 0)
    return s[:i] + new + s[j:]


for fname in ("sn-article.tex", "section_5_4_selection_score.tex"):
    path = os.path.join(P, "paper_overleaf_revised", fname)
    bak = path.replace(".tex", "_before_10min.tex")
    if not os.path.exists(bak):
        shutil.copy(path, bak)
    s = open(path, encoding="utf8", newline="").read()
    crlf = "\r\n" in s
    s = s.replace("\r\n", "\n")
    if fname == "sn-article.tex":
        s = cut(s, "The total communication $" + BS + "mathrm{Comm}_{" + BS + "mathrm{total}}(T)$", "(Table~" + BS + "ref{tab:cost}).", NEW_EQ)
        s = cut(s, "Therefore $JFI = 1$ means", "(Table~" + BS + "ref{tab:fairness}).", NEW_JFI)
        mac = " For ten classes the three quantities are computed per class from the confusion matrix of the test set and averaged with equal class weights (macro-average)."
        assert s.count(mac) == 1
        s = s.replace(mac, "")
    s = cut(s, BS + "textbf{Communication and computation cost.}", BS + "textbf{Protocol consistency.}", PARA + "\n\n" + TABLE + "\n\n", inclusive_b=False)
    open(path, "w", encoding="utf8", newline="").write(s.replace("\n", "\r\n") if crlf else s)
    print("patched", fname)
