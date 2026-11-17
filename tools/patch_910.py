"""Adds the Replacement 9/10 text, Section 5.4 paragraphs and Tables V, U, T, S to the revised manuscript (numbers from tools/_work/ev910.json).
LaTeX in this file uses '@' for the backslash."""
import json
import os
import shutil

import numpy as np

P = r"C:\Users\0xRay\Downloads\paper"
O = json.load(open(os.path.join(P, "tools", "_work", "ev910.json")))
BS = chr(92)


def L(s):
    return s.replace("@", BS)


R, T, A = O["resource"], O["target"], O["audit"]
ff, rd = R["abl_A2"], R["random"]
tf, tr = T["abl_A2"], T["random"]
save_up = 100 * (1 - tf["uploads"] / tr["uploads"])

# ---------------------------------------------------------------- Table V
names = [("random", "Random sampling (FedAvg)"), ("powd", "Power-of-Choice"), ("oort", "Oort"), ("divfl", "DivFL"), ("abl_A2", "FedFACS ($@kappa=0$)")]
rows_v = []
for k, nm in names:
    r, t = R[k], T[k]
    rows_v.append("%s & %.1f & %.2f & %.0f & %.1f & %.1f & %.0f (%d/%d) & %.1f & %.2f \\\\" % (
        nm, r["down"], r["up"], r["steps"], r["fwd_k"], r["total_gb"], t["uploads"], t["reached"], t["n"], t["total_gb"], r["wall"]))
tab_v = """@begin{table}[!htbp]
@centering
@footnotesize
@setlength{@tabcolsep}{2.5pt}
@renewcommand{@arraystretch}{1.08}
@caption{Resources per round and cost to the common target accuracy (45 runs per method: CIFAR-10, FMNIST and MNIST; Dirichlet $@alpha@in@{0.1,0.5@}$ and two-class partitions; five seeds; 100 rounds; $N=100$ clients). Per round: models downloaded, updates uploaded, local SGD steps, scoring or probing forward passes (in thousands). Total GB is the volume of Eq.~(23a) without setup traffic. Cost to target: uploaded updates (runs reaching the target / runs) and total GB, averaged over the runs that reach the target. Time is the simulated elapsed time per round (one GPU, clients trained sequentially).}
@label{tab:cost}
@begin{tabular*}{@journalfloatwidth}{@{@extracolsep{@fill}}lcccccccc@{}}
@toprule
Method & Down & Up & Steps & Scoring (k) & Total GB & Uploads to target & GB to target & s/round \\\\
@midrule
%s
@bottomrule
@end{tabular*}
@end{table}""" % "\n".join(rows_v)

# ---------------------------------------------------------------- Table U
F = O["fair"]
fn = [("random", "Random"), ("powd", "Power-of-Choice"), ("greedy", "Greedy"), ("fairfedcs", "FairFedCS"), ("fedfacs", "FedFACS")]
rows_u = []
for ds, dn in (("cifar10", "CIFAR-10"), ("fmnist", "FMNIST")):
    for k, nm in fn:
        v = F[ds + "|" + k]
        mu_ = lambda x: float(np.mean(v[x]))
        rows_u.append("%s & %s & %.3f & %.3f & %.1f & %.0f & %.1f & %.1f & %.1f \\\\" % (
            dn, nm, mu_("jfi"), mu_("jfi_q"), mu_("never"), mu_("wait"), mu_("pc_mean"), mu_("pc_std"), mu_("pc_p10")))
    if ds == "cifar10":
        rows_u.append("@addlinespace")
tab_u = """@begin{table}[!htbp]
@centering
@footnotesize
@setlength{@tabcolsep}{2.5pt}
@renewcommand{@arraystretch}{1.08}
@caption{Participation and outcome fairness in Scenario 3 (noisy clients, IID; mean of 3 seeds, 100 rounds). JFI is Eq.~(24) with $q_i=1$ (equality of participation) and JFI$_q$ is Eq.~(24) (participation proportional to quality). Client accuracy: mean, standard deviation and 10th percentile (@%) of the global model on the held-out local data of each client. The FedFACS runs use the stability weights ($@kappa=1$); the selection rule is the same for all $@kappa$.}
@label{tab:fairness}
@begin{tabular*}{@journalfloatwidth}{@{@extracolsep{@fill}}llccccccc@{}}
@toprule
Dataset & Method & JFI & JFI$_q$ & Never selected (@%) & Longest wait & Acc. mean & Acc. s.d. & Acc. p10 \\
@midrule
@ROWS@
@bottomrule
@end{tabular*}
@end{table}""".replace("@ROWS@", chr(10).join(rows_u))

# ---------------------------------------------------------------- Table T
C = O["cls"]
rows_t = []
for ds, dn in (("cifar10", "CIFAR-10"), ("fmnist", "FMNIST"), ("mnist", "MNIST")):
    for k, nm in (("random", "Random sampling"), ("abl_A2", "FedFACS ($@kappa=0$)")):
        v = C[ds + "|" + k]
        rows_t.append("%s & %s & %.2f & %.2f & %.2f & %.2f \\\\" % (dn, nm, np.mean(v["acc"]), np.mean(v["rec"]), np.mean(v["prec"]), np.mean(v["f1"])))
tab_t = """@begin{table}[!htbp]
@centering
@footnotesize
@setlength{@tabcolsep}{3pt}
@renewcommand{@arraystretch}{1.08}
@caption{Accuracy and macro-averaged recall, precision and F1 (@%) computed from the confusion matrix of the test set (mean of 15 runs per row: three partitions, five seeds).}
@label{tab:cls}
@begin{tabular*}{@journalfloatwidth}{@{@extracolsep{@fill}}llcccc@{}}
@toprule
Dataset & Method & Accuracy & Recall & Precision & F1 \\
@midrule
@ROWS@
@bottomrule
@end{tabular*}
@end{table}""".replace("@ROWS@", chr(10).join(rows_t))

# ---------------------------------------------------------------- Table S
n = A["ff"]
items = [("Cohort size within $[C_{k_{@min}},C_{k_{@max}}]$ in every round", A["bounds"]),
         ("Logged cohort size equals the number of selected clients", A["cohort_eq"]),
         ("Selection counts recomputed from the per-round selections equal the logged counts", A["selcnt_ok"]),
         ("Longest wait recomputed from the per-round selections equals the logged value", A["wait_ok"]),
         ("Uploaded volume equals the sum of the cohort sizes times the model size", A["up_ok"]),
         ("Number of logged rounds equals the configured number of rounds", A["rounds_ok"])]
rows_s = "\n".join("%s & %d / %d \\\\" % (a, b, n) for a, b in items)
tab_s = """@begin{table}[!htbp]
@centering
@footnotesize
@setlength{@tabcolsep}{3pt}
@renewcommand{@arraystretch}{1.08}
@caption{Consistency of the logged protocol in the %d runs of FedFACS and its ablation variants. Across all %d runs of the reproduction no round was cancelled and no client update was non-finite.}
@label{tab:audit}
@begin{tabular*}{@journalfloatwidth}{@{@extracolsep{@fill}}lc@{}}
@toprule
Check & Runs passing \\\\
@midrule
%s
@bottomrule
@end{tabular*}
@end{table}""" % (n, A["runs"], rows_s)

# ---------------------------------------------------------------- paragraphs
p_cost = ("@textbf{Communication and computation cost.} Table~@ref{tab:cost} counts the resources over 100 rounds. FedFACS sends the model to all $N=100$ candidates and trains all of them, "
          "so that its downloads and local steps are %.1f times those of random sampling, while its uploads are %.2f per round against %.0f. After 100 rounds the volume of Eq.~(23a) is %.1f times that of random sampling (%.1f against %.1f~GB). "
          "To the common target accuracy FedFACS uploads %.0f updates against %.0f for random sampling (%.1f@%% fewer; the target is reached in %d of %d runs against %d of %d), but transmits %.0f against %.0f~GB in total. "
          "FedFACS therefore lowers the uploads and not the total communication or the local computation; Power-of-Choice downloads %.0f and DivFL %.0f models per round for a cohort of ten. "
          "The simulated elapsed time per round is %.1f~s against %.1f~s (clients are trained sequentially on one GPU)." % (
              ff["steps_rel"], ff["up"], rd["up"], ff["total_rel"], ff["total_gb"], rd["total_gb"],
              tf["uploads"], tr["uploads"], save_up, tf["reached"], tf["n"], tr["reached"], tr["n"], tf["total_gb"], tr["total_gb"],
              R["powd"]["down"], R["divfl"]["down"], ff["wall"], rd["wall"]))
fq, fc = F["cifar10|fedfacs"], F["fmnist|fedfacs"]
gr_c, gr_f = F["cifar10|greedy"], F["fmnist|greedy"]
rn_c, rn_f = F["cifar10|random"], F["fmnist|random"]
m = lambda v, k: float(np.mean(v[k]))
p_fair = ("@textbf{Participation fairness.} Table~@ref{tab:fairness} separates three notions. The Jain index of the selection counts (equality of participation) is %.3f and %.3f for FedFACS on CIFAR-10 and FMNIST, against %.3f and %.3f for random sampling; "
          "no client is left unselected and the longest wait is %.0f rounds. The quality-adjusted index of Eq.~(24) is lower (%.3f and %.3f) because FedFACS serves the clients almost uniformly and not in proportion to $q_i$: "
          "the adjusted index equals one only if $p_i$ is proportional to $q_i$, so that two clients with $q_i=10$ and $q_i=5$ selected twice and once give %.1f for the adjusted and %.1f for the raw index. "
          "Greedy selection leaves %.0f@%% and %.0f@%% of the clients unselected. The outcome is described by the client-level accuracy: its 10th percentile is %.1f@%% and %.1f@%% for FedFACS against %.1f@%% and %.1f@%% for random sampling." % (
              m(fq, "jfi"), m(fc, "jfi"), m(rn_c, "jfi"), m(rn_f, "jfi"), max(max(fq["wait"]), max(fc["wait"])),
              m(fq, "jfi_q"), m(fc, "jfi_q"), O["example_quality"]["adj"], O["example_quality"]["raw"],
              m(gr_c, "never"), m(gr_f, "never"), m(fq, "pc_p10"), m(fc, "pc_p10"), m(rn_c, "pc_p10"), m(rn_f, "pc_p10")))
gap = max(abs(np.mean(C[d + "|" + k]["rec"]) - np.mean(C[d + "|" + k]["f1"])) for d in ("cifar10", "fmnist", "mnist") for k in ("random", "abl_A2"))
p_cls = ("@textbf{Classification metrics.} Table~@ref{tab:cls} reports the macro-averaged metrics. On CIFAR-10 and FMNIST, whose test sets have equal class sizes, the macro-recall equals the accuracy in every run; "
         "on MNIST, whose classes are unbalanced, the two differ by at most %.2f points. The macro-F1 differs from the macro-recall by at most %.1f points in every row." % (O["cls_max_gap_acc_recall"], gap))
p_audit = ("@textbf{Protocol consistency.} Table~@ref{tab:audit} lists the consistency checks applied to the per-round logs. Every check holds in all %d runs of FedFACS and its variants, "
           "and the 13 unit tests of the equations of Section~4 (idle counter, mixing coefficient, aggregation weights, cohort size, reference trajectory) pass." % n)
block = "\n\n".join([p_cost, tab_v, p_fair, tab_u, p_cls, tab_t, p_audit, tab_s])
block = L(block)

# ---------------------------------------------------------------- edits
FIX = [
    ("including partial and cancelled ones.", "including partial and cancelled ones. Local training steps, scoring forward passes and elapsed time are counted separately (Table~@ref{tab:cost})."),
    ("Because $q_i$ depends on the noise level, JFI differences may partly reflect selection by data quality.",
     "Because $q_i$ depends on the noise level, JFI differences may partly reflect selection by data quality. Three notions of fairness are therefore distinguished: equality of participation, measured by Eq.~(24) with $q_i=1$; participation proportional to quality, measured by Eq.~(24); and fairness of the outcome, measured by the accuracy of the global model on the held-out local data of each client (mean, standard deviation and 10th percentile). The share of clients that are never selected and the longest waiting time are reported with them (Table~@ref{tab:fairness})."),
    ("respectively. These metrics evaluate the performance",
     "respectively. For ten classes the three quantities are computed per class from the confusion matrix of the test set and averaged with equal class weights (macro-average). These metrics evaluate the performance"),
    ("Messages carry run and round identifiers", "In a deployment, messages carry run and round identifiers"),
    ("@textbf{Aggregate} with stability weights $S^t_i$ from (18):", "@textbf{Aggregate} with the weights $S^t_i$ from (18):"),
    ("with the nonnegative stability weights of Eq.", "with the nonnegative normalised weights of Eq."),
]
for fname in ("sn-article.tex", "section_5_4_selection_score.tex"):
    path = os.path.join(P, "paper_overleaf_revised", fname)
    bak = path.replace(".tex", "_before_910.tex")
    if not os.path.exists(bak):
        shutil.copy(path, bak)
    s = open(path, encoding="utf8", newline="").read()
    crlf = "\r\n" in s
    s = s.replace("\r\n", "\n")
    if fname == "sn-article.tex":
        for a, b in FIX:
            a, b = L(a), L(b)
            assert s.count(a) == 1, (a[:60], s.count(a))
            s = s.replace(a, b)
    i = s.index(BS + "textbf{Participation and aggregation influence.}")
    j = s.index("\n", i)
    assert "Communication and computation cost" not in s
    s = s[:j] + "\n\n" + block + s[j:]
    open(path, "w", encoding="utf8", newline="").write(s.replace("\n", "\r\n") if crlf else s)
    print("patched", fname, "crlf" if crlf else "lf")
