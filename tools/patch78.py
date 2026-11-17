"""Patch the revised manuscript for Replacements 7 (cohort) and 8 (aggregation). Idempotent: aborts if already applied."""
import os
import shutil

P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
TEX = os.path.join(P, "sn-article.tex")
S54 = os.path.join(P, "section_5_4_selection_score.tex")
src = open(TEX, encoding="utf8", newline="").read()
assert "tab:cohort" not in src, "already patched"
shutil.copy(TEX, os.path.join(P, "sn-article_before_78.tex"))
shutil.copy(S54, os.path.join(P, "section_5_4_before_78.tex"))
NL = "\r\n" if "\r\n" in src else "\n"
src = src.replace("\r\n", "\n")


def replace_line(text, start, new):
    i = text.index(start)
    j = text.find("\n", i)
    j = len(text) if j < 0 else j
    return text[:i] + new + text[j:]


# ---- Replacement 7: cohort paragraph below Eq. (16)
src = replace_line(src, r"When $\rho^{t-1}$ indicates sharp improvement, the cohort size is dynamically decreased",
    r"When $\rho^{t-1}$ indicates sharp improvement, the cohort size is dynamically decreased, reducing communication overhead. "
    r"In contrast, during stagnation and degradation (including a loss increase), the cohort size increases to $C_{k_{\max}}$, requesting updates from more informative clients "
    r"to improve global model accuracy and push it out of a local optimum; initialisation ($\rho^0=0$) also selects $C_{k_{\max}}$. "
    r"Eq.~(16) is nonincreasing in $\rho^{t-1}$, and any two rounding conventions change a cohort by at most one client. "
    r"The efficiency of Eq.~(15) can also be measured against the reference pace of the run: with $e^{t-1}=\rho^{t-1}/\Omega^{t}$ for $\Omega^{t}>0$ and $e^{t-1}=0$ otherwise, "
    r"Eq.~(16) is evaluated with $e^{t-1}$ in place of $\rho^{t-1}$ (FedFACS-R). A round that progresses at least at the reference pace then selects $C_{k_{\min}}$ clients, "
    r"so that the cohort uses its full range whatever the absolute scale of the loss; Section~\ref{sec:score_analysis} (Table~\ref{tab:cohort}) evaluates both measures. "
    r"A candidate whose update is not finite is reported as unavailable and cannot be selected; if fewer than $m_t$ candidates are available, all of them are selected.")

# ---- Replacement 8
src = replace_line(src, r"The next global model is the stability-weighted average of the trained local models",
    r"The next global model is the weighted average of the trained local models $w_i^t$ with nonnegative weights $S_i^t$ that sum to one (Eq.~(18)), as shown in Eq.~(4). "
    r"Equation (1) is the learning objective. The ranking of Eq.~(3) decides which clients take part in a round, and the aggregation with $\kappa=0$ weights the selected clients "
    r"by their sample counts, which is the weighting of Eq.~(1) restricted to the selected clients; the stability weights ($\kappa>0$) form a variance-aware alternative that "
    r"Section~\ref{sec:score_analysis} evaluates.")
src = replace_line(src, r"Furthermore, the aggregation process incorporates stability-based weighting",
    r"Furthermore, the aggregation weights of Eq.~(18) are nonnegative and sum to one for every choice of $\kappa$. With $\kappa=0$ each selected client contributes in proportion "
    r"to its sample count, so that the aggregate is consistent with the objective of Eq.~(1); with $\kappa>0$ the weights shift towards clients with a high stability score. "
    r"Selection is governed by the fitness of Eq.~(14) and the waiting-time guard, and aggregation by the weights of Eq.~(18); Section~\ref{sec:score_analysis} reports "
    r"participation counts, waiting times and the cumulative aggregation influence of the clients.")
src = replace_line(src, r"\item Stability-weighted aggregation method:",
    r"\item Normalised aggregation weights: we present a nonnegative weight family $S_i^t=(1-\kappa)\,n_i/\sum_j n_j+\kappa\,q_i^t$ that contains the sample-count weighting of the "
    r"population objective ($\kappa=0$) and the stability weighting ($\kappa=1$) and is defined for negative scores and identical client models; the comparison of the two, "
    r"reported in Section 5.4, selects $\kappa=0$, which gives the more stable global model at the end of training.")
i = src.index("Moreover, introducing dynamic cohort sizing in FedFACS-A2")
j = src.index("\n", i)
src = src[:i] + (r"Moreover, introducing dynamic cohort sizing in FedFACS-A2 leads to a slight change in accuracy and reduces the upload volume; the saving equals the reduction of the "
    r"mean cohort below the fixed size (1.7\% in the reproduction study with cohort bounds of 5 and 10, Table~\ref{tab:cohort}) and is bounded by $1-C_{k_{\min}}/C_{k_{\max}}$ for any configuration. "
    r"Furthermore, the full FedFACS model replaces the sample-count weights of FedFACS-A2 by the stability weights of Eq.~(18) with $\kappa=1$. The comparison of the two weightings "
    r"is repeated in Section~\ref{sec:score_analysis} on nine dataset--partition settings, where the sample-count weighting gives the more stable final model.") + src[j:]
open(TEX, "w", encoding="utf8", newline="").write(src.replace("\n", NL))

# ---- Section 5.4 additions
s = open(S54, encoding="utf8", newline="").read()
NL2 = "\r\n" if "\r\n" in s else "\n"
s = s.replace("\r\n", "\n")
new = r"""\textbf{Cohort size.} Eq.~(16) with the absolute loss reduction $\rho^{t-1}$ keeps the cohort at $C_{k_{\max}}$ in 75\% of the rounds and never below 7 clients in the 45 runs of the reproduction study (mean 9.71 [9.68, 9.75] clients, i.e.\ 2.9\% fewer uploads than a fixed cohort of ten). Measuring the efficiency against the reference pace of the run ($e^{t-1}=\rho^{t-1}/\Omega^{t}$, FedFACS-R) uses the whole range from 5 to 10 clients: in Table~\ref{tab:cohort} the mean cohort falls from 9.83 to 9.10 clients and the upload volume by 7.5\% relative to the absolute rule (9.0\% relative to a fixed cohort), with best-round accuracy $-0.30$ [$-0.57$, $+0.05$] and last-10-round accuracy $-0.08$ [$-0.56$, $+0.41$] points, Jain index 0.997 against 0.998 and no unselected client; the longest wait rises from 10.8 to 14.0 rounds, below the threshold $R=20$ of the waiting-time guard. The saving of either rule is bounded by $1-C_{k_{\min}}/C_{k_{\max}}$.

\begin{table}[!htbp]
\centering
\footnotesize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.08}
\caption{Cohort rules (CIFAR-10 and FMNIST, Dirichlet $\alpha=0.5$, sample-count aggregation, bounds 5 and 10; mean of 6 runs). Accuracy columns: paired difference to the fixed cohort of ten with 95\% bootstrap interval (best-round and last-10-round test accuracy, percentage points).}
\label{tab:cohort}
\begin{tabular*}{\journalfloatwidth}{@{\extracolsep{\fill}}lcccccc@{}}
\toprule
Rule & Mean cohort & Smallest $m_t$ & Uploads (GB) & $\Delta$ best acc. & $\Delta$ last-10 acc. & Max. wait \\
\midrule
Fixed cohort of ten & 10.00 & 10 & 33.6 & --- & --- & 10.0 \\
Absolute rule, Eq.~(16) & 9.83 & 8 & 33.0 & $+0.38$ [$-0.20$, $+0.96$] & $+0.47$ [$-0.10$, $+1.10$] & 10.8 \\
Relative pace (FedFACS-R) & 9.10 & 5 & 30.6 & $+0.09$ [$-0.34$, $+0.58$] & $+0.39$ [$-0.20$, $+1.14$] & 14.0 \\
\bottomrule
\end{tabular*}
\end{table}

\textbf{Participation and aggregation influence.} With the feedback rule and sample-count aggregation (45 runs, nine settings) every client was selected at least once, the Jain index of the selection counts was 0.995--0.998 and the longest wait 10--13 rounds, below the guard threshold; the weakest tenth of the clients reached 63.2\% and 76.3\% accuracy on CIFAR-10 and FMNIST (Table~\ref{tab:mixing}). The cumulative aggregation influence of a client, the sum of its weights $S_i^t$ over the rounds, was positive for every client; on average over the runs the least influential client had 0.35 and the most influential 2.24 times the mean influence (Gini coefficient 0.21). The smallest weight of any selected client in any round was $2\times10^{-3}$ with sample-count weights and $4\times10^{-5}$ with stability weights, so that no weight was zero or negative.

"""
k = s.index(r"\textbf{Uncertainty penalty.}")
s = s[:k] + new + s[k:]
open(S54, "w", encoding="utf8", newline="").write(s.replace("\n", NL2))
print("patched")
