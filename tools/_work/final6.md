
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

**R1-02, R2-04 and R2-20: the control law**

- Fix: Eq. (8) has the positive denominator λF + |ν(ΔKL − F)|, with λ = 1, β = 0.9 and a⁰ = 0.5 stated; clip(x, 0, 1) is defined; the direction of the feedback is derived; the Lyapunov wording is removed from the Abstract, the Introduction and Section 4.2.
- Where: Section 4.2, Eq. (8) and the paragraph below it.
- Evidence: In the 96 main runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2% of the 4,316 rounds with ν > 0; Table Y.
- Declaration: The rule is well posed (Proposition 1) and bounded, and its effect follows Eq. (8).

**R2-05: the scales of F and ΔKL**

- Fix: The priority of Eq. (9) is stated with the quantities that determine it: at the diagnostic rounds the fairness term has a median of 1.88, the utility score 0.73 and the coefficient 0.10, so that the weighted utility term is a median 3% of the weighted fairness term and the priority is rank-correlated with F (Spearman 0.92). Two alternatives with comparable weights were implemented and evaluated.
- Where: Section 4.2, paragraph before Eq. (9); Section 5.4.
- Evidence: Table Y: a constant a = 0.5 and a = 1 lower the Jain index to 0.92–0.94 and 0.35–0.56. A rank-normalised priority with the waiting-time guard gave a Jain index of 0.94–0.99, longest waits of 17–20 rounds and no accuracy gain.
- Declaration: The regime in which the priority is determined mainly by the waiting time is the configuration that preserves near-uniform participation at the highest accuracy; the feedback rule reaches it without tuning the coefficient.

**R2-18: theoretical analysis**

- Fix: Section 4.3 adds Propositions 1 to 3 (well-posedness, bounded waiting under the waiting-time guard, bounded movement of the aggregate).
- Where: Section 4.3 (see FedFACS_R2-18_Analysis_and_Guarantees.docx).
- Evidence: In all runs of the unmodified rule the longest wait (17 rounds for N = 100) stayed below the guard threshold R = 20, so the reported results are those of the unguarded rule.
- Declaration: FedFACS guarantees a maximum waiting time; convergence is evaluated empirically.


# 2. Edits: before and after, with locations


::: {custom-style="BA-Sub"}
Replacement 6
:::


::: {custom-style="BA-Edit"}
Replacement 6, edit 1: Introduction: wording of the control mechanism
:::

::: {custom-style="BA-Loc"}
Location: Section 1, contributions paragraph (original line 137)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Moreover, FedFACS balances utility and fairness using a control [mechanism inspired by the Lyapunov control law (Chaudhari et al.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Moreover, FedFACS balances utility and fairness using a [bounded feedback]{custom-style="Add"} control [mechanism.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 6, edit 2: Section 4.2: feedback rule and priority, Eqs. (8) and (9)
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2 (original line 376)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

The proposed control mechanism is [inspired]{custom-style="Del"} by the [Lyapunov stability principle, where the feedback signal guides the system in determining whether to shift toward informativeness or fairness. At]{custom-style="Del"} the same [time, the use of bounded and normalized updates helps ensure stable behavior during training.]{custom-style="Del"} The [control mechanism]{custom-style="Del"} is defined as follows:

::: {custom-style="DelBlock"}
$$ a_i^t = clip(a,1,0) = \prod_{[0,1]}
\left(
\beta \cdot a_i^{t-1} + (1-\beta)
\frac{
\nu^t \cdot (\Delta KL_i^t - F_i^t)
}{
\lambda \cdot F + \nu^t \cdot (\Delta KL_i^t - F_i^t)
}
\right) \qquad (8) $$
:::

The term $\Delta KL_i^t - F_i^t$ provides a directional signal for decision-making, [while incorporating the fairness term in the denominator helps stabilize]{custom-style="Del"} the update and [avoids rapid shifts caused by under-served clients. This leads]{custom-style="Del"} to [a smooth and balanced control mechanism. The parameter $\beta \in [0,1]$ is an exponential moving average smoothing parameter, $\lambda$ is a fairness regularization coefficient, and $\prod_{[0,1]}(\cdot)$ represents the Euclidean projection to ensure that the parameter remains within the bounded interval.]{custom-style="Del"}

The fairness [value increases when]{custom-style="Del"} a client remains unselected, [forcing other metrics]{custom-style="Del"} in the priority [score to encourage its selection as in]{custom-style="Del"} Eq. (9), where the [contribution]{custom-style="Del"} of client $i$ [during communication]{custom-style="Del"} round $t$ is [represented]{custom-style="Del"} by the [priority score $p_i^t$. This score combines]{custom-style="Del"} two [main factors such as: fairness]{custom-style="Del"} and [utility while weighting them through a control mechanism by tuning]{custom-style="Del"} the [control parameter $a$, allowing]{custom-style="Del"} the [framework to prioritize fairness or utility depending on the global model’s needs for either exploitation or exploration.]{custom-style="Del"}

::: {custom-style="DelBlock"}
$$ P_i^t = a \cdot \Delta KL_i^t + (1 - a)\, F_i^t \qquad (9) $$
:::

::: {custom-style="BA-Label-After"}
After (put instead)
:::

The proposed control mechanism is [a bounded feedback rule that adapts the balance between informativeness and fairness to the observed training progress. It is well posed (Proposition 1 of Section 4.3): the denominator below is positive and the mixing coefficient stays in $[0,1]$; participation fairness is additionally guaranteed]{custom-style="Add"} by the [waiting-time guard of]{custom-style="Add"} the same [section.]{custom-style="Add"} The [mixing coefficient $a_i^t \in [0,1]$, with $a_i^0=0.5$,]{custom-style="Add"} is defined as follows:

::: {custom-style="AddBlock"}
$$ a_i^t = \mathrm{clip}\left(
\beta \cdot a_i^{t-1} + (1-\beta)
\frac{
\nu^t \cdot (\Delta KL_i^t - F_i^t)
}{
\lambda \cdot F_i^t + \left|\nu^t \cdot (\Delta KL_i^t - F_i^t)\right|
},\ 0,\ 1\right) \qquad (8) $$
:::

[Here $\mathrm{clip}(x,0,1)=\min\{1,\max\{0,x\}\}$, $\beta=0.9$ is an exponential moving average smoothing parameter and $\lambda=1$ is a fairness regularization coefficient. Since $F_i^t \ge 1$ and $\lambda>0$, the denominator is positive.]{custom-style="Add"} The term $\Delta KL_i^t - F_i^t$ provides a directional signal for decision-making, [and]{custom-style="Add"} the update [smooths toward a signed feedback target in $[-1,1]$ before clipping to $[0,1]$. Because $F_i^t$ usually exceeds $\Delta KL_i^t$, a positive $\nu^t$ tends to lower $a_i^t$]{custom-style="Add"} and [a negative $\nu^t$ tends]{custom-style="Add"} to [raise it.]{custom-style="Add"}

The fairness [term grows while]{custom-style="Add"} a client remains unselected, [so that long-waiting clients rise]{custom-style="Add"} in the priority [of]{custom-style="Add"} Eq. (9), where [$\Pi_i^t$ is]{custom-style="Add"} the [priority score]{custom-style="Add"} of client $i$ [at]{custom-style="Add"} round $t$ [and $a_i^t$ weights utility against fairness. Since $F_i^t \ge 1$ and the feedback rule keeps the mixing coefficient small, the priority]{custom-style="Add"} is [determined mainly]{custom-style="Add"} by the [fairness term: the utility term orders the clients with similar waiting times, so that no client is excluded by a low utility. Section 5.4 shows that this is the regime in which FedFACS reaches its highest accuracy at near-uniform participation: weighting the]{custom-style="Add"} two [terms comparably, either with a constant coefficient of 0.5 or by rank normalisation, lowers the Jain index]{custom-style="Add"} and [does not raise accuracy, and no constant coefficient tested is significantly more accurate than]{custom-style="Add"} the [feedback rule, which sets]{custom-style="Add"} the [coefficient without tuning.]{custom-style="Add"}

::: {custom-style="AddBlock"}
$$ \Pi_i^t = a_i^t \cdot \Delta KL_i^t + (1 - a_i^t)\, F_i^t \qquad (9) $$
:::


# 3. Evidence (Section 5.4, paragraph and Table Y)

::: {custom-style="BA-Note"}
These passages belong to subsection 5.4 (Analysis of the selection score); the full subsection is in the Replacement 5 file.
:::

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

In the 96 main runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2% of the 4,316 rounds in which $\nu^t>0$, as Eq. (8) predicts.

# 4a. New section to insert: 4.3

::: {custom-style="BA-Note"}
NEW SECTION: Section 4.3 does not exist in the original paper. Insert it as a new subsection after Section 4.2 and before Section 5 (Experimental Evaluation). Its full text follows; the replacements refer to it as "Section 4.3".
:::

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


# 4. Notation declared by this replacement

| Symbol | Declaration |
|:--|:--|
| $a_i^t$, $\beta=0.9$, $\lambda=1$, $a_i^0=0.5$ | mixing coefficient, smoothing constant, fairness regularisation (now specified) |
| $\mathrm{clip}(x,0,1)$ | CHANGED: projection onto $[0,1]$, $\min\{1,\max\{0,x\}\}$ (original wrote $\mathrm{clip}(a,1,0)$) |
| $\Pi_i^t$ | CHANGED: priority score of client $i$ at round $t$ (was $P_i^t$, which clashed with the prediction $P(x)$) |
| $\nu^t$ | deviation signal (Replacement 3), the feedback input of Eq. (8) |
| $F_i^t\ge 1$ | fairness term (Replacement 4), larger than $\Delta KL_i^t$ by construction |
| $\Delta KL_i^t$ | utility score (Replacement 5) |


# 5. Prepared answers (internal, not for the manuscript)

- **Is the utility term small?** The score itself is not (median 0.73, against 1.88 for F); its weighted contribution is, because the feedback rule keeps the coefficient at a median of 0.10: a·ΔKL is a median 3% of (1−a)·F, and the priority is rank-correlated with F (0.92). A comparable weight (a constant of 0.5, or rank normalisation) lowered the Jain index and did not raise accuracy (Table Y).
- **Is the controller necessary?** It reaches the best operating point without tuning: no constant coefficient is significantly more accurate than the rule in any comparison, and the rule is significantly more accurate in some (a = 0.05 on CIFAR-10, a = 0.10 on FMNIST in the last 10 rounds).
- **Is the direction of the feedback correct?** When the deviation signal is positive the mean mixing coefficient decreased in 98.2% of 4,316 rounds (96 main runs), as Eq. (8) predicts.
- **No Lyapunov analysis?** The mechanism is presented as a bounded feedback rule; its properties that can be proved (positive denominator, coefficient in [0,1], bounded waiting under the guard) are in Section 4.3.
