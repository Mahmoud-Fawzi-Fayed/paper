
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


# 3. New Section 4.3 (insert after Section 4.2, before Section 5)

::: {custom-style="BA-Sub"}
4.3 Properties of FedFACS (new subsection)
:::

This subsection states what the design guarantees. Throughout, $m_t=|C_k^t|$ is the cohort size of Eq. (16) with $C_{k_{\min}}\le m_t\le C_{k_{\max}}$, $\mathcal{C}$ is the set of $N$ clients and $r_i^t$ is the idle counter of Eq. (7).

**Waiting-time guard.** To make participation fairness a guarantee rather than only a tendency of the fairness term, selection uses an age guard with threshold $R=\lceil N/C_{k_{\min}}\rceil$. Let $U^t=\{i\in\mathcal{C}: r_i^t\ge R\}$ be the overdue clients, ordered by decreasing $r_i^t$ and, for equal counters, by ascending identifier. If $|U^t|\ge m_t$, the cohort consists of the first $m_t$ clients of $U^t$; otherwise it consists of $U^t$ and of the $m_t-|U^t|$ clients of $\mathcal{C}\setminus U^t$ with the highest fitness (Eq. (14)). When no client is overdue the rule is exactly Eq. (3).

**Proposition 1 (well-posedness).** In every round: (i) the denominator of Eq. (8) is at least $\lambda>0$ and $a_i^t\in[0,1]$; (ii) $1\le F_i^t<N+1$; (iii) $m_t$ is an integer with $C_{k_{\min}}\le m_t\le C_{k_{\max}}$; (iv) the weights satisfy $S_i^t\ge 0$ and $\sum_{i\in C_k^t}S_i^t=1$.

*Proof.* (i) $F_i^t\ge 1$ gives $\lambda F_i^t\ge\lambda$, and the clip in Eq. (8) bounds $a_i^t$. (ii) $r_i^t\le\sum_j r_j^t=N\,\overline{r^t}$, hence $F_i^t=1+r_i^t/(1+\overline{r^t})<1+N$. (iii) and (iv) follow from the clamping and rounding of Eq. (16) and from the two branches of Eq. (18). $\square$

**Proposition 2 (bounded waiting).** Assume $m_t\ge C_{k_{\min}}$ in every committed round. With the guard, every client is selected within $W=R+\lceil N/C_{k_{\min}}\rceil$ consecutive committed rounds, i.e. $r_i^t\le W-1$ for all $i$ and $t$.

*Proof.* Let client $i$ first reach $r_i^{t_0}=R$; from $t_0$ on it is overdue until it is selected. Let $A^t$ be the number of overdue clients ranked ahead of $i$, so $A^{t_0}\le N-1$. A client that becomes overdue after $t_0$ has a smaller counter than $i$ and ranks behind it, and clients ahead of $i$ that are not selected keep their order because all counters grow by one. In a round in which $i$ is not selected, all $m_t\ge C_{k_{\min}}$ selected clients are ahead of $i$, so $A^t$ falls by at least $C_{k_{\min}}$; once $A^t+1\le m_t$ the client is selected. Hence $i$ is selected at a round $t_0+k$ with $k\le\lceil N/C_{k_{\min}}\rceil-1$, when its counter is $R+k\le W-1$. $\square$

For $N=100$ and $C_{k_{\min}}=5$ the threshold is $R=20$ and no client waits more than 39 rounds, whatever the scores are. The longest waiting times observed were 6, 17, 22 and 43 rounds for $N=50,100,200,400$ (thresholds $R=10,20,40,80$), so the guard was never active in the 84 FedFACS runs (nor in the 45 runs of its A2 variant) of Section 5, and the reported results are those of the unguarded rule. The guarantee concerns participation, not influence: a selected client with $S_i^t=0$ does not change the aggregate.

**Proposition 3 (bounded round-to-round movement).** Let local training clip the gradient norm at $G$, use learning rate $\eta$ and at most $K$ local steps per round. Then $\|w_i^t-w_{\text{global}}^t\|\le\eta KG$ for every client, and, for any selection and any weights with $S_i^t\ge 0$ and $\sum_i S_i^t=1$, $\|w_{\text{global}}^{t+1}-w_{\text{global}}^t\|\le\eta KG$.

*Proof.* Each clipped step moves the parameters by at most $\eta G$, so $K$ steps move them by at most $\eta KG$; the aggregate is a convex combination of the local models, and the norm is convex. $\square$

The aggregate therefore cannot move by more than $\eta KG$ in one round, whichever clients are selected or how they are weighted; clients whose update is not finite are excluded, and a round is committed only if all checks pass (Section 4.1).


# 4. New Section 5.4 with its tables (insert at the end of Section 5, before the Conclusion)

::: {custom-style="BA-Sub"}
5.4 Analysis of the selection score (new subsection)
:::

This subsection examines the components of the selection score of Eqs. (5)–(14). It uses a ResNet-18 with frozen early layers, 100 clients, 100 rounds and cohorts of 5 to 10 clients, with 3 seeds for the ablations (5 for the utility analysis) and 95% bootstrap intervals. The absolute accuracies therefore differ from those of Tables 1 and 2. All variants in Table Y use sample-count aggregation and differ from FedFACS only in the mixing coefficient $a$.

**Utility of the KL score.** For every candidate client, in rounds 1, 5, 10, 25, 50 and 100, we computed the marginal gain, i.e. the reduction in global validation loss obtained when that client's update alone is added to the global model with weight $1/m_t$, and its Spearman rank correlation $\rho$ with the client indicators of Table X. The KL score is positively associated with the gain under every label-skew partition ($\rho=0.39$ to $0.73$). The global cross-entropy of the client's examples is the stronger predictor under label skew but reverses its sign under label noise ($\rho=-0.77$), because clients with corrupted labels have a high loss and degrade the aggregate; the KL score shows no such reversal ($\rho=0.12$, not significant). Selecting with a loss-based utility instead of KL changes accuracy by $+0.57$ [$-0.33$, $+1.64$] points on CIFAR-10 and $+0.25$ [$-0.08$, $+0.48$] on FMNIST, i.e. not detectably. The KL score is therefore a valid, label-free and noise-robust utility indicator. Compared with the raw parameter drift $\lVert w_i^t-w_{\mathrm{global}}^t\rVert$ (Table X2), it is the better predictor under the two-class partition on both datasets and is not distinguishable from it under Dirichlet $\alpha=0.1$.

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

**Fairness term and mixing coefficient.** At the diagnostic rounds 5 to 100 the fairness term has a median of 1.88 and the utility score $\Delta KL_i^t$ a median of 0.73, and the coefficients have a median of 0.10 (below). The weighted utility term $a_i^t\Delta KL_i^t$ is therefore a median 3% of $(1-a_i^t)F_i^t$, the priority of Eq. (9) is rank-correlated with $F_i^t$ (Spearman 0.92 against 0.27 for $\Delta KL_i^t$), and 98.9% of the selected clients have a fairness term above the median: the priority is determined mainly by the waiting time, and the utility term orders the clients with similar waiting times. Table Y shows that this regime is the one that works. Without the fairness term ($a=1$) the Jain index falls to 0.56 and 0.35, 10.0% and 20.3% of the clients are never selected, and accuracy decreases by 2.6 and 2.2 points. A balanced constant $a=0.5$ lowers the Jain index to 0.92 and 0.94, lengthens the longest wait to 14–16 rounds, and lowers accuracy (best round, CIFAR-10: $-1.25$ [$-1.90$, $-0.73$]; last 10 rounds, FMNIST: $-1.53$ [$-3.42$, $-0.29$]). Rank-normalising both terms so that they carry equal weight, together with the waiting-time guard and with $a\in\{0.25,0.5\}$, gave the same outcome: the Jain index fell to 0.94–0.99, the longest wait rose to 17–20 rounds, and accuracy did not improve ($-0.5$ to $-0.8$ points). At the diagnostic rounds 5 to 100 the coefficients of the clients have a median of 0.10 (mean 0.14; 5th–95th percentile 0.001–0.33). In accuracy, no constant is significantly better than the feedback rule in any comparison, and the rule is significantly better in some ($a=0.05$ on CIFAR-10, best round: $-0.80$ [$-1.91$, $-0.10$] for the constant; $a=0.10$ on FMNIST, last 10 rounds: $-0.90$ [$-1.33$, $-0.30$]); the constants $a=0.05$ and $a=0.10$ differ from it by at most one round in the longest wait and by at most 0.002 in the Jain index. The rule thus provides this operating point without requiring the coefficient to be tuned.

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

**Aggregation weights.** Replacing the stability weights ($\kappa=1$ in Eq. (18)) by sample-count weights ($\kappa=0$), with the selection unchanged, leaves participation unchanged (Jain index 0.995–0.999, longest wait 10–13 rounds, no unselected client in all nine settings) and removes most of the oscillation of the global model at the end of training: in the five of nine dataset–partition settings with a detectable difference the last-10-round accuracy increases (by up to 9.6 [7.4, 12.9] points on MNIST with $\alpha=0.5$), in none does it decrease, and the round-to-round fluctuation of the test accuracy falls from 5.0 to 1.5 points on CIFAR-10 and from 3.9 to 1.0 points on FMNIST ($\alpha=0.5$). The best-round accuracy is higher in four settings, not distinguishable in four, and lower in one (CIFAR-10, $\alpha=0.1$). FedFACS therefore uses $\kappa=0$.

**Cohort size.** Eq. (16) with the absolute loss reduction $\rho^{t-1}$ keeps the cohort at $C_{k_{\max}}$ in 75% of the rounds and never below 7 clients in the 45 runs of the reproduction study (mean 9.71 [9.68, 9.75] clients, i.e.\ 2.9% fewer uploads than a fixed cohort of ten). Measuring the efficiency against the reference pace of the run (the ratio $\rho^{t-1}/\Omega^{t}$ in place of $\rho^{t-1}$ in Eq. (16)) uses the whole range from 5 to 10 clients: in Table Z the mean cohort falls from 9.83 to 9.10 clients and the upload volume by 7.5% relative to the absolute rule (9.0% relative to a fixed cohort), with best-round accuracy $-0.29$ [$-0.57$, $+0.05$] and last-10-round accuracy $-0.08$ [$-0.55$, $+0.41$] points, Jain index 0.997 against 0.998 and no unselected client; the longest wait rises from 10.8 to 14.0 rounds, below the threshold $R=20$ of the waiting-time guard. The saving of either rule is bounded by $1-C_{k_{\min}}/C_{k_{\max}}$. The cohort size is the number of uploads per round; the cumulative uploads to a target accuracy are the sum of the cohort sizes over the rounds needed to reach it, so that a reduction of the cumulative count can come from smaller cohorts or from fewer rounds, and the two are reported separately (Section 5.4 and the round-to-target columns of Section 5).

Table Z. Cohort rules (CIFAR-10 and FMNIST, Dirichlet $\alpha=0.5$, sample-count aggregation, bounds 5 and 10; mean of 6 runs). Accuracy columns: paired difference to the fixed cohort of ten with 95% bootstrap interval (percentage points).

| Rule | Mean cohort | Smallest $m_t$ | Uploads (GB) | $\Delta$ best acc. | $\Delta$ last-10 acc. | Max. wait |
|:--|--:|--:|--:|:--|:--|--:|
| Fixed cohort of ten | 10.00 | 10 | 33.6 | – | – | 10.0 |
| Absolute rule, Eq. (16) | 9.83 | 8 | 33.0 | +0.38 [−0.20, +0.96] | +0.47 [−0.10, +1.10] | 10.8 |
| Relative rate | 9.10 | 5 | 30.6 | +0.09 [−0.34, +0.58] | +0.39 [−0.20, +1.14] | 14.0 |

**Participation and aggregation influence.** With the feedback rule and sample-count aggregation (45 runs, nine settings) every client was selected at least once, the Jain index of the selection counts was 0.995–0.999 and the longest wait 10–13 rounds, below the guard threshold; the weakest tenth of the clients reached 63.2% and 76.3% accuracy on CIFAR-10 and FMNIST (Table Y). The cumulative aggregation influence of a client, the sum of its weights $S_i^t$ over the rounds, was positive for every client; on average over the runs the least influential client had 0.35 and the most influential 2.24 times the mean influence (Gini coefficient 0.21). The smallest weight of any selected client in any round was $2\times10^{-3}$ with sample-count weights and $4\times10^{-5}$ with stability weights, so that no weight was zero or negative.

**Uncertainty penalty.** The batch variance does not separate noisy from clean clients (rank AUC 0.45 [0.39, 0.52]), so it acts as a stabilising term in the fitness of Eq. (14) and not as a noise detector. With sample-count aggregation, removing it changes the best-round accuracy by $-0.04$ [$-0.22$, $+0.12$] points on CIFAR-10 and $-0.14$ [$-0.35$, $+0.27$] on FMNIST and lowers the last-10-round accuracy by 0.39 [0.14, 0.77] points on FMNIST, so the penalty improves the stability of the final model on FMNIST and is neutral on CIFAR-10. In the 96 main runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2% of the 4,316 rounds in which $\nu^t>0$, as Eq. (8) predicts.

Table W (supporting evidence for the paragraph on aggregation weights; not a table of the manuscript).


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

# 5. New and changed equations

::: {custom-style="BA-Note"}
New or changed equations of Section 4.2 that the text above relies on. The numbers are those of the revised manuscript.
:::

$$ d_i^t(x)=\sum_{c\in\mathcal{Y}}P_i^t(c\mid x)\log\frac{P_i^t(c\mid x)}{Q^t(c\mid x)} \qquad (5a) $$

$$ KL_{i,b}^t=\frac{1}{|X_{i,b}^t|}\sum_{x\in X_{i,b}^t}d_i^t(x) \qquad (5b) $$

$$ \overline{KL}_i^t = \frac{1}{B}\sum_{b=1}^{B} KL_{i,b}^t \qquad (12a) $$

$$ m_t = \min\left\{C_{k_{\max}},\ \max\left\{C_{k_{\min}},\ \left\lfloor C_{k_{\min}} + (C_{k_{\max}} - C_{k_{\min}})\big[1-\mathrm{clip}(\rho^{t-1},0,1)\big] + \tfrac{1}{2}\right\rfloor\right\}\right\} \qquad (16) $$

$$ S_i^t = (1-\kappa)\,\dfrac{n_i}{\sum_{j\in C_k^t} n_j} + \kappa\,q_i^t,\qquad q_i^t=\begin{cases}
\dfrac{s_{i,+}^t}{H^t}, & H^t>0,\\
\dfrac{n_i}{\sum_{j\in C_k^t} n_j}, & H^t=0
\end{cases} \qquad (18) $$


# 6. Ledger: every number of the new text, recomputed from the raw run files

::: {custom-style="BA-Note"}
Method. `tools/verify_claims.py` reads the 683 result files in `fedfacs_repro/results/` and recomputes each value stated in Sections 4.3 and 5.4 and in the replacement files: means, paired differences with 95% bootstrap intervals (10,000 resamples), Spearman correlations, rank AUC, waiting times, cohort sizes, aggregation weights and influence; the properties of Section 4.3 are executed on random inputs and by simulation. Result: 56 of 56 values agree with the text. Rerun: `python tools/verify_claims.py`.
:::

| ID | Where | Claim | In the paper | Recomputed from the raw runs | Source |
|:--|:--|:--|:--|:--|:--|
| Y-cif-abl_A2 | Table Y | cifar10 abl_A2: acc, last-10, JFI, never, max wait, weakest 10% | 72.13 70.17 0.997 0 11.0 63.2 | 72.13 70.17 0.997 0 11.0 63.2 | results/*_abl_A2_s{0,1,2}.json |
| Y-cif-a2_fix05 | Table Y | cifar10 a2_fix05: acc, last-10, JFI, never, max wait, weakest 10% | 71.33 70.04 0.999 0 10.0 63.2 | 71.33 70.04 0.999 0 10.0 63.2 | results/*_a2_fix05_s{0,1,2}.json |
| Y-cif-a2_fix10 | Table Y | cifar10 a2_fix10: acc, last-10, JFI, never, max wait, weakest 10% | 72.01 70.46 0.998 0 10.0 60.5 | 72.01 70.46 0.998 0 10.0 60.5 | results/*_a2_fix10_s{0,1,2}.json |
| Y-cif-a2_fix50 | Table Y | cifar10 a2_fix50: acc, last-10, JFI, never, max wait, weakest 10% | 70.88 68.81 0.916 0 15.7 57.3 | 70.88 68.81 0.916 0 15.7 57.3 | results/*_a2_fix50_s{0,1,2}.json |
| Y-cif-a2_nofair | Table Y | cifar10 a2_nofair: acc, last-10, JFI, never, max wait, weakest 10% | 69.54 65.58 0.557 10.0 100 55.2 | 69.54 65.58 0.557 10.0 100 55.2 | results/*_a2_nofair_s{0,1,2}.json |
| Y-fmn-abl_A2 | Table Y | fmnist abl_A2: acc, last-10, JFI, never, max wait, weakest 10% | 85.54 84.57 0.998 0 10.7 76.3 | 85.54 84.57 0.998 0 10.7 76.3 | results/*_abl_A2_s{0,1,2}.json |
| Y-fmn-a2_fix05 | Table Y | fmnist a2_fix05: acc, last-10, JFI, never, max wait, weakest 10% | 85.49 84.18 0.998 0 10.3 73.3 | 85.49 84.18 0.998 0 10.3 73.3 | results/*_a2_fix05_s{0,1,2}.json |
| Y-fmn-a2_fix10 | Table Y | fmnist a2_fix10: acc, last-10, JFI, never, max wait, weakest 10% | 85.24 83.67 0.998 0 10.0 73.9 | 85.24 83.67 0.998 0 10.0 73.9 | results/*_a2_fix10_s{0,1,2}.json |
| Y-fmn-a2_fix50 | Table Y | fmnist a2_fix50: acc, last-10, JFI, never, max wait, weakest 10% | 85.32 83.04 0.941 0 14.3 76.6 | 85.32 83.04 0.941 0 14.3 76.6 | results/*_a2_fix50_s{0,1,2}.json |
| Y-fmn-a2_nofair | Table Y | fmnist a2_nofair: acc, last-10, JFI, never, max wait, weakest 10% | 83.36 79.00 0.346 20.3 100 68.2 | 83.36 79.00 0.346 20.3 100 68.2 | results/*_a2_nofair_s{0,1,2}.json |
| X2-cif0.1 | Table X2 | cifar10 s1_0.1: KL, drift, KL-drift (n=12) | 0.41/0.24/0.17 [-0.17, 0.43] | 0.41/0.24/0.17 [-0.17, 0.43] | results/*_fedfacs_s{0,1}_dist.json (diag records) |
| X2-cifs2 | Table X2 | cifar10 s2: KL, drift, KL-drift (n=12) | 0.71/0.33/0.37 [0.32, 0.43] | 0.71/0.33/0.37 [0.32, 0.43] | results/*_fedfacs_s{0,1}_dist.json (diag records) |
| X2-fmn0.1 | Table X2 | fmnist s1_0.1: KL, drift, KL-drift (n=12) | 0.56/0.64/-0.08 [-0.34, 0.11] | 0.56/0.64/-0.08 [-0.34, 0.11] | results/*_fedfacs_s{0,1}_dist.json (diag records) |
| X2-fmns2 | Table X2 | fmnist s2: KL, drift, KL-drift (n=12) | 0.75/0.50/0.25 [0.09, 0.46] | 0.75/0.50/0.25 [0.09, 0.46] | results/*_fedfacs_s{0,1}_dist.json (diag records) |
| X-s1_0.1 | Table X | s1_0.1: KL, global CE (n=90) | 0.50 [0.42, 0.58] / 0.64 [0.59, 0.69] / 90 | 0.50 [0.42, 0.58] / 0.64 [0.59, 0.69] / 90 | results/*_fedfacs_s*.json (diag records); analysis/utility_validity.md |
| X-s1_0.5 | Table X | s1_0.5: KL, global CE (n=90) | 0.39 [0.33, 0.45] / 0.50 [0.45, 0.55] / 90 | 0.39 [0.33, 0.45] / 0.50 [0.45, 0.55] / 90 | results/*_fedfacs_s*.json (diag records); analysis/utility_validity.md |
| X-s2 | Table X | s2: KL, global CE (n=90) | 0.73 [0.69, 0.77] / 0.75 [0.71, 0.79] / 90 | 0.73 [0.69, 0.77] / 0.75 [0.71, 0.79] / 90 | results/*_fedfacs_s*.json (diag records); analysis/utility_validity.md |
| X-s3 | Table X | s3: KL, global CE (n=18) | 0.12 [-0.09, 0.33] / -0.77 [-0.88, -0.65] / 18 | 0.12 [-0.09, 0.33] / -0.77 [-0.88, -0.65] / 18 | results/*_fedfacs_s*.json (diag records); analysis/utility_validity.md |
| D1 | 5.4 Aggregation | last-10 accuracy A2 minus stability: wins/ties/losses over 9 settings | 5/4/0 | 5/4/0 | analysis/a2_vs_all.md; results/* |
| D2 | 5.4 Aggregation | best-round accuracy: wins/ties/losses | 4/4/1 | 4/4/1 | analysis/a2_vs_all.md; results/* |
| D3 | 5.4 Aggregation | MNIST alpha=0.5 last-10 gain | 9.6 [7.4, 12.9] | 9.6 [7.4, 12.9] | results/* |
| D4 | 5.4 Aggregation | A2 Jain index range / longest wait range / unselected clients (45 runs) | 0.995-0.999 / 10-13 / 0 | 0.995-0.999 / 10-13 / 0 | results/*_abl_A2_s*.json |
| D5-cif | 5.4 Aggregation | round-to-round fluctuation, cifar10 alpha=0.5 (stability -> sample count) | 5.0 -> 1.5 | 5.0 -> 1.5 | results/*; mean /diff/ of test accuracy, last 30 rounds |
| D5-fmn | 5.4 Aggregation | round-to-round fluctuation, fmnist alpha=0.5 (stability -> sample count) | 3.9 -> 1.0 | 3.9 -> 1.0 | results/*; mean /diff/ of test accuracy, last 30 rounds |
| E1 | 5.4 Uncertainty / 4.2 | rounds with nu>0 in which the mean mixing coefficient decreased (base runs of FedFACS and FedFACS-A2) | 98.2% of 4,316 (96 runs) | 98.2% of 4316 (96 runs) | results/*_fedfacs_s*.json, *_abl_A2_s*.json (log nu, a_mean) |
| E2 | 5.4 Mixing | per-client mixing coefficient at the diagnostic rounds 5-100 (FedFACS base runs) | median 0.10 mean 0.14 p5-p95 0.001-0.33 | median 0.10 mean 0.14 p5-p95 0.001-0.33 (n=24300) | results/*_fedfacs_s*.json (diag records) |
| F1 | 4.3 | longest waits for N=50,100,200,400 (fedfacs) | 6, 17, 22, 43 | 6, 17, 22, 43 | results/*_fedfacs_*.json (max_wait) |
| F2 | 4.3 | number of FedFACS runs behind F1 (text: 84) | 84 | 84 | results/* |
| F3 | 4.3 | no wait reached the guard threshold R=ceil(N/5) | never active | all below R | results/*; R=10,20,40,80 |
| G1 | 5.4 Cohort | A2 mean cohort (45 runs) | 9.71 [9.68, 9.75] | 9.71 [9.68, 9.75] | results/*_abl_A2_*.json (log cohort) |
| G2 | 5.4 Cohort | rounds at Cmax / smallest cohort | 75% / 7 | 75% / 7 | results/*_abl_A2_*.json |
| G3 | 5.4 Cohort | saving versus a fixed cohort of ten | 2.9% | 2.9% | results/* |
| G4 | 5.4 Participation | influence: least/most influential client over the mean; Gini; clients with zero influence | 0.35 / 2.24 / 0.21 / 0 | 0.35 / 2.24 / 0.21 / 0 | results/*_abl_A2_*.json (selected, n) |
| G5 | 5.4 Participation | smallest weight of any selected client (sample-count / stability) | 2e-3 / 4e-5 | 2.4e-03 / 4.4e-05 | results/* (log weights_min) |
| Z-abl_A1 | Table Z | abl_A1: mean cohort / smallest / uploads GB (n=6) | 10.00 / 10 / 33.6 | 10.00 / 10 / 33.6 | results/*; tools/ev78c.py, ev78d.py |
| Z-abl_A2 | Table Z | abl_A2: mean cohort / smallest / uploads GB (n=6) | 9.83 / 8 / 33.0 | 9.83 / 8 / 33.0 | results/*; tools/ev78c.py, ev78d.py |
| Z-a2_relcoh | Table Z | a2_relcoh: mean cohort / smallest / uploads GB (n=6) | 9.10 / 5 / 30.6 | 9.10 / 5 / 30.6 | results/*; tools/ev78c.py, ev78d.py |
| I1-cif | 5.4 Utility | loss-based utility minus KL utility, best-round accuracy (n=3 seeds) | +0.57 [-0.33, +1.64] | +0.57 [-0.33, +1.64] | results/*_abl_loss_*, *_fedfacs_* |
| I1-fmn | 5.4 Utility | loss-based utility minus KL utility, best-round accuracy (n=3 seeds) | +0.25 [-0.08, +0.48] | +0.25 [-0.08, +0.48] | results/*_abl_loss_*, *_fedfacs_* |
| I2-cif | 5.4 Uncertainty | no penalty minus penalty, best-round accuracy (n=3 seeds) | -0.04 [-0.22, +0.12] | -0.04 [-0.22, +0.12] | results/*_a2_nopen_*, *_abl_A2_* |
| I2-fmn | 5.4 Uncertainty | no penalty minus penalty, best-round accuracy (n=3 seeds) | -0.14 [-0.35, +0.27] | -0.14 [-0.35, +0.27] | results/*_a2_nopen_*, *_abl_A2_* |
| I3-fmn | 5.4 Uncertainty | no penalty minus penalty, last-10 accuracy | -0.39 [-0.77, -0.14] | -0.39 [-0.77, -0.14] | results/* |
| I5 | 5.4 Mixing | rank-normalised priority (a=0.25, 0.5): Jain range / longest wait range / mean accuracy change (12 runs) | 0.94-0.99 / 17-20 / -0.5 to -0.8 | 0.944-0.993 / 17-20 / -0.67 | results/*_norm_a25_*, *_norm_a50_* |
| J-best | 5.4 Cohort | FedFACS-R minus absolute rule, best accuracy (6 runs) | -0.29 [-0.57, +0.05] | -0.29 [-0.57, +0.05] | results/*_a2_relcoh_*, *_abl_A2_* |
| J-last-10 | 5.4 Cohort | FedFACS-R minus absolute rule, last-10 accuracy (6 runs) | -0.08 [-0.55, +0.41] | -0.08 [-0.55, +0.41] | results/*_a2_relcoh_*, *_abl_A2_* |
| J-up | 5.4 Cohort | upload reduction of FedFACS-R relative to the absolute rule | 7.5% | 7.5% | results/* |
| J-wait | 5.4 Cohort | longest wait: absolute rule -> FedFACS-R | 10.8 -> 14.0 | 10.8 -> 14.0 | results/* |
| K1 | 5.4 Mixing | median fairness term / median utility score / median coefficient at rounds 5-100 (FedFACS main runs) | 1.88 / 0.73 / 0.10 | 1.88 / 0.73 / 0.10 | results/*_fedfacs_s*.json (diag records, 51 runs) |
| K3 | 5.4 Mixing | Spearman of the priority with F / with the utility score; selected clients above median F; median a*KL/((1-a)*F) | 0.92 / 0.27 / 98.9% / 3% | 0.92 / 0.27 / 98.9% / 3% | results/*_fedfacs_s*.json (diag records, log selected) |
| K4 | 4.2 / Lemma A | share of client-rounds with the utility score below the fairness term (rounds 5-100) | 82.7% | 82.7% | results/*_fedfacs_s*.json (diag records) |
| K2 | 5.4 Uncertainty | rank AUC of the batch variance for label noise | 0.45 [0.39, 0.52] (analysis/noise_discrimination.md) | 0.45 [0.38, 0.52] (n=18 round-runs, noisy = noise level above 0.2) | results/*_s3_fedfacs_s*.json (diag records); analysis/noise_discrimination.md |
| H1 | 4.3 Prop. 2 | simulated longest wait with the guard (N=50,100,200; adversarial / random scores) against W-1 | <= 19, 39, 79 | adv 15,31,65 / rand 11,23,45 | tools/verify_claims.py (3000 rounds each, cohort 5-10) |
| H2 | 4.3 Prop. 1(ii) | fairness term range over 2000 random counter vectors | 1 <= F < N+1 | min 1.000 max 3.3 | spec.fairness |
| H3 | 4.3 Prop. 1(i) | mixing coefficient over 20000 random inputs lies in [0,1] | [0, 1] | [0.000, 0.955] | spec.mix_coeff |
| H4 | 4.3 Prop. 1(iii) | cohort size over 20000 random efficiencies (incl. negative) | integer in [5,10] | [5, 10] | spec.cohort_size |
| H5 | 4.3 Prop. 1(iv) | aggregation weights over 20000 random score vectors (negative, zero, tiny) | w >= 0, sum = 1 | min 0.0e+00, max /sum-1/ 2.2e-16 | spec.stability_weights |

**Values corrected by this verification (internal, not for the manuscript).** The text of the earlier drafts contained the following values, which the raw runs did not reproduce; each was replaced by the recomputed value and the sentence was rewritten around it.

| Earlier statement | Recomputed | Change made |
|:--|:--|:--|
| the mean mixing coefficient decreased in 96.7% of 1,827 rounds with $\nu>0$ | 98.2% of 4,316 rounds (96 main runs); the earlier alignment of $\nu$ with the round was off by one | value and alignment replaced |
| the coefficient settles at a median of 0.04 (mean 0.10) | median 0.10, mean 0.14 over the diagnostic rounds 5 to 100 | value replaced |
| $\Delta KL$ is typically much smaller than one; clients are grouped by waiting time | $\Delta KL$ has a median of 0.73 (F: 1.88); the weighted utility term is a median 3% of the weighted fairness term; the priority is rank-correlated with F (0.92) | the sentence now states the measured dominance of the waiting time, not a grouping |
| Jain index 0.995 to 0.998 for the sample-count aggregation | 0.995 to 0.999 | range corrected |
| rank-normalised priority: Jain 0.95 to 0.99, longest wait 18 to 20 | 0.94 to 0.99, 17 to 20 | ranges corrected |
| the ratio rule accuracy difference −0.30 [−0.57, +0.05] and −0.08 [−0.56, +0.41] | −0.29 [−0.57, +0.05] and −0.08 [−0.55, +0.41] | rounding corrected |
