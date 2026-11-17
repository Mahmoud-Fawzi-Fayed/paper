
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

**Replacement 7. R1-06 and R2-08: validity, indexing and rounding of the cohort rule**

- Fix: Eq. (15) is written for the completed round and Eq. (16) uses the previous round, so that no future loss is needed. The efficiency is clipped to [0,1], the cohort is an integer obtained by half-up rounding and clamped to [Cmin, Cmax], the history starts at rho^0 = 0 (the first rounds select Cmax), a zero or non-finite previous loss cancels the round, and a candidate whose update is not finite is unavailable. The rule is nonincreasing in the efficiency, and any two rounding conventions differ by at most one client.
- Where: Section 4.2, Eqs. (15)-(16) and the paragraph below Eq. (16).
- Evidence: 13 unit tests pass, among them: the cohort is an integer within its bounds for any rho, the original formula exceeds Cmax for negative rho, and the loss-pair guards hold. No round was cancelled and no update failed in any reproduced run.
- Declaration: The rule returns a valid integer cohort in every round, and the effect of the rounding convention is bounded by one client.

**Replacement 7. R2-09 and R1-18: dynamic range of the cohort and the participation counts**

- Fix: The claim of about 15% fewer clients per round is replaced by the measured saving and its bound, 1 - Cmin/Cmax. The ratio of the loss reduction to the reference rate can replace the absolute reduction, which uses the whole range. Per-round cohort sizes are recorded in every run and are released with the code; the bounds of each configuration are stated; uploads per round and cumulative uploads to a target are reported separately.
- Where: Section 4.2 (paragraph below Eq. (16)); Section 5.1 (ablation text); Section 5.4, Cohort size and Table Z.
- Evidence: Table Z. With the absolute rule the mean cohort is 9.71 [9.68, 9.75] over 45 runs (2.9% fewer uploads than a fixed cohort of ten; the cohort is at its maximum in 75% of the rounds). With the ratio rule the mean cohort is 9.10, the smallest cohort 5, and the uploads fall by 7.5% relative to the absolute rule (9.0% relative to a fixed cohort); accuracy differs by -0.29 [-0.57, +0.05] (best round) and -0.08 [-0.55, +0.41] (last 10 rounds) points.
- Declaration: The cohort rule reduces uploads without a detectable change of accuracy, its saving is stated with its upper bound, and the relative-pace measure uses the full range.

**Replacement 8. R1-03 and R2-07: the implemented aggregation, negative scores and dataset size**

- Fix: Eq. (18) defines one weight family S = (1 - kappa) n_i / sum n_j + kappa q_i, where q is the normalised positive part of the stability score. It is nonnegative, sums to one, and is defined for negative scores, a vanishing denominator (scaled by the largest score; sample-count fallback when all scores are zero) and identical client models. Eq. (4) and Algorithm 2 use these weights. With kappa = 0, used in all reported experiments, the sample size n_i is retained.
- Where: Section 4.2, Eqs. (17)-(18) and the paragraph below them; Section 1 (contributions).
- Evidence: 13 unit tests pass (nonnegative weights summing to one for negative, zero and mixed scores). The smallest weight of a selected client was 2e-3 with sample-count weights and 4e-5 with stability weights. Table W: sample-count weights give a higher last-10-round accuracy in 5 of 9 settings and a lower one in none.
- Declaration: One normalised, nonnegative aggregation rule is specified and evaluated, and its default coincides with the sample-size weighting of the objective.

**Replacement 8. R1-11: the objective and the ranking heuristic**

- Fix: Eq. (1) is stated as the learning objective. The ranking of Eq. (3) decides which clients take part; the aggregation with kappa = 0 weights the selected clients by their sample counts, the weighting of Eq. (1) restricted to the selected clients. The stability weights are an evaluated alternative.
- Where: Section 4.1, last paragraph; Section 4.2, closing paragraph.
- Evidence: Proposition 3 (Section 4.3): the aggregate moves by at most eta K G per round for any selection and any nonnegative weights.
- Declaration: The learning objective, the selection rule and the aggregation weights are separated, and the aggregation is consistent with the population objective.

**Replacement 8. R1-10: selection frequency, waiting time and aggregation influence**

- Fix: The manuscript reports the participation counts, the proportion of never-selected clients, the longest waits, the accuracy of the weakest clients and the cumulative aggregation influence of every client.
- Where: Section 5.4, Participation and aggregation influence; Table Y.
- Evidence: 45 runs: every client selected at least once; Jain index 0.995-0.999; longest wait 10-13 rounds; weakest 10% of clients 63.2% (CIFAR-10) and 76.3% (FMNIST) accuracy; cumulative aggregation influence of the least and most influential client 0.35 and 2.24 times the mean (Gini 0.21), positive for every client.
- Declaration: Participation and influence are measured, and every client contributes to the aggregate.


# 2. Edits: before and after, with locations


::: {custom-style="BA-Sub"}
Replacement 7
:::


::: {custom-style="BA-Edit"}
Replacement 7, edit 1: Section 4.2: cohort size, Eqs. (15)-(16) and the paragraph below them
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2, server side (original line 439)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

On the server-side, it receives fitness scores from all clients for evaluation. The server ranks the clients according to their fitness scores and adaptively determines the cohort size according to the convergence efficiency observed in the previous communication round, [which represents]{custom-style="Del"} the reduction [rate]{custom-style="Del"} of the [global]{custom-style="Del"} loss [value $\rho \in  [0, 1]$]{custom-style="Del"} as shown in Eq. (15). Two predefined bounds, $C_{k_{\min}}$ and [$C_{k_{\max}}$,]{custom-style="Del"} regulate the allowable cohort size range (McMahan et al. 2017; Li et al. 2020), thereby enabling an adaptive number of clients to be selected for aggregation while maintaining communication efficiency and mitigating network congestion, as defined in Eq. (16).

::: {custom-style="DelBlock"}
$$ \rho^{t-1} = \frac{L_{{global}}^{t-2} - L_{{global}}^{t-1}}{L_{{global}}^{t-2}} \qquad (15) $$
:::

::: {custom-style="DelBlock"}
$$ C_k^t = C_{k_{\min}} + \left( (C_{k_{\max}} - C_{k_{\min}})\cdot (1 - \rho^{t-1}) \right) \qquad (16) $$
:::

[When $\rho$ indicates sharp improvement,]{custom-style="Del"} the cohort [size is dynamically decreased reducing communication overhead. In contrast, during stagnation]{custom-style="Del"} and [degradation,]{custom-style="Del"} the [cohort size increases, requesting updates from more informative clients to improve global model]{custom-style="Del"} accuracy [and push it out of]{custom-style="Del"} a [local optimum.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

On the server-side, it receives fitness scores from all clients for evaluation. The server ranks the clients according to their fitness scores and adaptively determines the cohort size [$m_t=|C_k^t|$]{custom-style="Add"} according to the convergence efficiency observed in the previous communication round, [namely]{custom-style="Add"} the [relative]{custom-style="Add"} reduction [$\rho^{t-1}$]{custom-style="Add"} of the [validation]{custom-style="Add"} loss as shown in Eq. (15). Two predefined [integer]{custom-style="Add"} bounds, $C_{k_{\min}}$ and [$C_{k_{\max}}$ (fixed in advance for each configuration),]{custom-style="Add"} regulate the allowable cohort size range (McMahan et al. 2017; Li et al. 2020), thereby enabling an adaptive number of clients to be selected for aggregation while maintaining communication efficiency and mitigating network congestion, as defined in Eq. (16). [Here $L_{global}^{t}$ is the validation loss after round $t$ and $L_{global}^{0}$ that of the initial model. Hence $\rho^{t}\le 1$: it is positive when the loss falls and negative when it rises, and a negative value is kept because it selects the maximum cohort. If the previous loss is zero or non-finite, $\rho^{t}$ is undefined and the round is cancelled with all state unchanged.]{custom-style="Add"}

::: {custom-style="AddBlock"}
$$ \rho^{t} = \frac{L_{{global}}^{t-1} - L_{{global}}^{t}}{L_{{global}}^{t-1}},\qquad L_{{global}}^{t-1}>0 \qquad (15) $$
:::

::: {custom-style="AddBlock"}
$$ m_t = \min\left\{C_{k_{\max}},\ \max\left\{C_{k_{\min}},\ \left\lfloor C_{k_{\min}} + (C_{k_{\max}} - C_{k_{\min}})\big[1-\mathrm{clip}(\rho^{t-1},0,1)\big] + \tfrac{1}{2}\right\rfloor\right\}\right\} \qquad (16) $$
:::

[A large $\rho^{t-1}$ means fast progress, so a smaller cohort suffices and the uploads fall; stagnation or a loss increase ($\rho^{t-1}\le 0$) and the first round select $C_{k_{\max}}$, since averaging more clients reduces the variance of the aggregate. Values in between are interpolated linearly and rounded to the nearest integer. Since $\rho^{t-1}$ alone keeps]{custom-style="Add"} the cohort [near $C_{k_{\max}}$, the ratio $\rho^{t-1}/\Omega^{t}$ can replace it, which spans the full range]{custom-style="Add"} and [lowers]{custom-style="Add"} the [uploads without a detectable change in]{custom-style="Add"} accuracy [(Table Z). Clients with]{custom-style="Add"} a [non-finite update are excluded; if fewer than $m_t$ remain, all are selected.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 7, edit 2: Section 5.1: the claim on fewer clients per round
:::

::: {custom-style="BA-Loc"}
Location: Section 5.1, ablation study (original line 555)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Moreover, [introducing]{custom-style="Del"} dynamic cohort sizing [in FedFACS-A2 leads]{custom-style="Del"} to a [slight change in accuracy due to]{custom-style="Del"} the [adaptive reduction in participating clients, and reduces communication overhead]{custom-style="Del"} by [selecting approximately 15% fewer clients per training round.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Moreover, dynamic cohort sizing [(FedFACS-A2) changes the accuracy only slightly. Relative]{custom-style="Add"} to a [fixed cohort of $C_{k_{\max}}$ clients, it saves]{custom-style="Add"} the [fraction]{custom-style="Add"} by [which the mean cohort size falls below $C_{k_{\max}}$; this fraction cannot exceed $1-C_{k_{\min}}/C_{k_{\max}}$, so it grows with the distance between the two bounds (Table Z).]{custom-style="Add"}


::: {custom-style="BA-Sub"}
Replacement 8
:::


::: {custom-style="BA-Edit"}
Replacement 8, edit 1: Contributions: the aggregation item
:::

::: {custom-style="BA-Loc"}
Location: Section 1, list of contributions (original line 143)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

\item [Stability-weighted]{custom-style="Del"} aggregation [method:]{custom-style="Del"} we present a [stability-weighted aggregation scheme]{custom-style="Del"} that [adaptively adjusts]{custom-style="Del"} the [weight]{custom-style="Del"} of the [selected clients' local models during aggregation by leveraging their]{custom-style="Del"} stability [scores, thereby enhancing]{custom-style="Del"} global [accuracy, training robustness, and convergence speed.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

\item [Normalised]{custom-style="Add"} aggregation [weights:]{custom-style="Add"} we present a [nonnegative weight family $S_i^t=(1-\kappa)\,n_i/\sum_j n_j+\kappa\,q_i^t$]{custom-style="Add"} that [contains]{custom-style="Add"} the [sample-count weighting]{custom-style="Add"} of the [population objective ($\kappa=0$) and the]{custom-style="Add"} stability [weighting ($\kappa=1$) and is defined for negative scores and identical client models; the comparison of the two, reported in Section 5.4, selects $\kappa=0$, which gives the more stable]{custom-style="Add"} global [model at the end of training.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 8, edit 2: Section 4.1: relation between the objective, the selection and the aggregation
:::

::: {custom-style="BA-Loc"}
Location: Section 4.1, last paragraph (original line 216)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

[After selecting]{custom-style="Del"} the [most contributing]{custom-style="Del"} clients [$C_k^t$, weighted]{custom-style="Del"} aggregation [is performed using each client’s stability score ${Stability}_i^t$, incorporating utility and an uncertainty penalty. This amplifies the effectiveness of]{custom-style="Del"} the selected clients to [improve overall performance, as shown in Eq. (4). Subsequently,]{custom-style="Del"} the [resulting aggregated model is used in]{custom-style="Del"} the [next iteration.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

[The next global model is]{custom-style="Add"} the [weighted average of the trained local models $w_i^t$ with nonnegative weights $S_i^t$ that sum to one (Eq. (18)), as shown in Eq. (4). Equation (1) is the learning objective. The ranking of Eq. (3) decides which]{custom-style="Add"} clients [take part in a round, and the]{custom-style="Add"} aggregation [with $\kappa=0$ weights]{custom-style="Add"} the selected clients [by their sample counts, which is the weighting of Eq. (1) restricted]{custom-style="Add"} to the [selected clients;]{custom-style="Add"} the [stability weights ($\kappa>0$) form a variance-aware alternative that Section 5.4 evaluates.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 8, edit 3: Section 4.2: aggregation weights, Eqs. (17)-(18)
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2, after the cohort size (original line 453)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Once the selected clients submit their local updates, [normalization is applied to preserve]{custom-style="Del"} the [exact proportional differences in client quality, as shown in Eq. (18), where *S* represents]{custom-style="Del"} the [normalized]{custom-style="Del"} sum. Following this, the server carries out [a stability-weighted]{custom-style="Del"} aggregation, which is formulated as [follows:]{custom-style="Del"}

$$ w_{{global}}^{t+1} = \sum_{i \in C_k^t} S_i^t \, w_i^t \qquad (17) $$

::: {custom-style="DelBlock"}
$$ S_i^t = \frac{s_i^t}{\sum_{i \in C_k^t} s_i^t} \qquad (18) $$
:::

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Once the selected clients submit their local updates, the [stability scores are converted into aggregation weights. For]{custom-style="Add"} the [selected clients let $s_{i,+}^t=\max(s_i^t,0)$ be the positive part of the raw score and $H^t=\sum_{j\in C_k^t}s_{j,+}^t$ its cohort]{custom-style="Add"} sum. Following this, the server carries out [the]{custom-style="Add"} aggregation, which is formulated as [follows (Eq. (17) restates Eq. (4)):]{custom-style="Add"}

$$ w_{{global}}^{t+1} = \sum_{i \in C_k^t} S_i^t \, w_i^t \qquad (17) $$

::: {custom-style="AddBlock"}
$$ S_i^t = (1-\kappa)\,\dfrac{n_i}{\sum_{j\in C_k^t} n_j} + \kappa\,q_i^t,\qquad q_i^t=\begin{cases}
\dfrac{s_{i,+}^t}{H^t}, & H^t>0,\\
\dfrac{n_i}{\sum_{j\in C_k^t} n_j}, & H^t=0
\end{cases} \qquad (18) $$
:::

[The coefficient $\kappa\in[0,1]$ sets the weighting: $\kappa=0$ gives sample-count weights and $\kappa=1$ gives the stability weights $q_i^t$. FedFACS uses $\kappa=0$ in all reported experiments; Section 5.4 compares the two choices. For numerical stability the first branch of $q_i^t$ is evaluated as $z_i^t/\sum_{j\in C_k^t}z_j^t$ with $z_i^t=s_{i,+}^t/\hat{s}^{\,t}$ and $\hat{s}^{\,t}=\max_{j\in C_k^t}s_{j,+}^t$. All choices of $\kappa$ give $S_i^t\ge 0$ and $\sum_{i\in C_k^t}S_i^t=1$, and they are defined for negative scores and for identical client models (all scores zero). Frozen tensors and nontrainable buffers keep their round-start values. A selected client with $S_i^t=0$ incurs upload cost and resets its idle counter but does not contribute to that round's aggregate.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 8, edit 4: Section 4.2: closing paragraph on the aggregation
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2 (original line 474)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Furthermore, the aggregation [process incorporates stability-based weighting, reflecting the effectiveness]{custom-style="Del"} and [relative contribution across individual]{custom-style="Del"} client [models with respect]{custom-style="Del"} to its stability score. [This approach assigns higher]{custom-style="Del"} aggregation weights [to]{custom-style="Del"} the [informative and stable]{custom-style="Del"} clients. [In addition, it does not compromise fairness but only reduces the implications arising from exploring less utility clients, while assigning lower weights to less informative clients.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Furthermore, the aggregation [weights of Eq. (18) are nonnegative]{custom-style="Add"} and [sum to one for every choice of $\kappa$. With $\kappa=0$ each selected]{custom-style="Add"} client [contributes in proportion]{custom-style="Add"} to its [sample count, so that the aggregate is consistent with the objective of Eq. (1); with $\kappa>0$ the weights shift towards clients with a high]{custom-style="Add"} stability score. [Selection is governed by the fitness of Eq. (14) and the waiting-time guard, and]{custom-style="Add"} aggregation [by the]{custom-style="Add"} weights [of Eq. (18); Section 5.4 reports participation counts, waiting times and]{custom-style="Add"} the [cumulative aggregation influence of the]{custom-style="Add"} clients.


::: {custom-style="BA-Edit"}
Replacement 8, edit 5: Section 5.1: the claim on the full model
:::

::: {custom-style="BA-Loc"}
Location: Section 5.1, ablation study (original line 555)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Furthermore, [incorporating the adaptive stability-weighted aggregation in]{custom-style="Del"} the full FedFACS model [limits]{custom-style="Del"} the [effect]{custom-style="Del"} of [gradient noise from unstable clients]{custom-style="Del"} by [assigning larger aggregation]{custom-style="Del"} weights [to]{custom-style="Del"} stable [and informative client updates. Consequently, the aggregated global model becomes more robust, mitigating the impact of noisy clients and accelerating convergence with fewer training rounds.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Furthermore, the full FedFACS model [replaces]{custom-style="Add"} the [sample-count weights]{custom-style="Add"} of [FedFACS-A2]{custom-style="Add"} by [the stability]{custom-style="Add"} weights [of Eq. (18) with $\kappa=1$. The comparison of the two weightings is repeated in Section 5.4 on nine dataset–partition settings, where the sample-count weighting gives the more]{custom-style="Add"} stable [final model.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 8, edit 6: Abstract: the aggregation sentence
:::

::: {custom-style="BA-Loc"}
Location: Abstract (original line 99)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Furthermore, we propose a [stability-weighted]{custom-style="Del"} aggregation [method that aligns model aggregation]{custom-style="Del"} with the stability [criteria.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Furthermore, we propose a [nonnegative normalised]{custom-style="Add"} aggregation [family whose default, the sample-count weighting, keeps the aggregate consistent]{custom-style="Add"} with the [population objective, and we compare it with]{custom-style="Add"} stability [weighting.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 8, edit 7: Introduction: the stability score and the aggregation
:::

::: {custom-style="BA-Loc"}
Location: Section 1, contributions paragraph (original line 137)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Furthermore, the client contributions are quantified [using]{custom-style="Del"} stability score which is [used to adaptively weight global model aggregation.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Furthermore, the client contributions are quantified [by a]{custom-style="Add"} stability score [that defines an optional weighting of the global aggregation,]{custom-style="Add"} which is [evaluated against sample-count weights.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 8, edit 8: Section 5 discussion: effect of the aggregation
:::

::: {custom-style="BA-Loc"}
Location: Section 5, fairness discussion (original line 1152)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Furthermore, the [stability-weighted]{custom-style="Del"} aggregation [strategy improves accuracy by assigning greater weights to updates from more]{custom-style="Del"} stable [clients.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Furthermore, the [sample-count]{custom-style="Add"} aggregation [keeps the global model]{custom-style="Add"} stable [at the end of training (Section 5.4).]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 8, edit 9: Section 5 discussion: the full model
:::

::: {custom-style="BA-Loc"}
Location: Section 5, closing paragraph of the discussion (original line 1155)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Finally, the full FedFACS model improves accuracy, communication efficiency and, fairness by integrating adaptive client selection, dynamic cohort sizing, and [adaptive stability-weighted]{custom-style="Del"} aggregation.

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Finally, the full FedFACS model improves accuracy, communication efficiency and, fairness by integrating adaptive client selection, dynamic cohort sizing, and [normalised]{custom-style="Add"} aggregation.


::: {custom-style="BA-Edit"}
Replacement 8, edit 10: Section 5: summary of the ablation
:::

::: {custom-style="BA-Loc"}
Location: Section 5, summary paragraph (original line 1076)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

This is achieved through the integration of fitness-based client selection, adaptive cohort sizing, and [stability-weighted aggregation,]{custom-style="Del"} which enhance the effectiveness of federated learning under heterogeneous data distributions, facilitate faster convergence, and enable more efficient utilization of participating clients.

::: {custom-style="BA-Label-After"}
After (put instead)
:::

This is achieved through the integration of fitness-based client selection, adaptive cohort sizing, and [normalised nonnegative aggregation weights,]{custom-style="Add"} which enhance the effectiveness of federated learning under heterogeneous data distributions, facilitate faster convergence, and enable more efficient utilization of participating clients.


::: {custom-style="BA-Edit"}
Replacement 8, edit 11: Conclusion: the aggregation sentence
:::

::: {custom-style="BA-Loc"}
Location: Section 6, Conclusion (original line 1164)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Moreover, [stability-aware]{custom-style="Del"} aggregation [is employed, assigning higher weights to reliable client updates, thereby enhancing]{custom-style="Del"} the [stability and reliability]{custom-style="Del"} of the [resulting global model.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Moreover, [the]{custom-style="Add"} aggregation [uses nonnegative normalised weights, with sample-count weighting as]{custom-style="Add"} the [default, which gives the more stable global model at the end]{custom-style="Add"} of [training in]{custom-style="Add"} the [comparison of Section 5.4.]{custom-style="Add"}


# 3. Evidence (new paragraphs and tables of subsection 5.4)

::: {custom-style="BA-Note"}
Insert the two paragraphs below in subsection 5.4 (Analysis of the selection score), before the paragraph on the uncertainty penalty; Table Z belongs to the first and Table W summarises the paragraph on aggregation weights that is already in 5.4.
:::

**Cohort size.** Eq. (16) with the absolute loss reduction $\rho^{t-1}$ keeps the cohort at $C_{k_{\max}}$ in 75% of the rounds and never below 7 clients in the 45 runs of the reproduction study (mean 9.71 [9.68, 9.75] clients, i.e.\ 2.9% fewer uploads than a fixed cohort of ten). Measuring the efficiency against the reference pace of the run (the ratio $\rho^{t-1}/\Omega^{t}$ in place of $\rho^{t-1}$ in Eq. (16)) uses the whole range from 5 to 10 clients: in Table Z the mean cohort falls from 9.83 to 9.10 clients and the upload volume by 7.5% relative to the absolute rule (9.0% relative to a fixed cohort), with best-round accuracy $-0.29$ [$-0.57$, $+0.05$] and last-10-round accuracy $-0.08$ [$-0.55$, $+0.41$] points, Jain index 0.997 against 0.998 and no unselected client; the longest wait rises from 10.8 to 14.0 rounds, below the threshold $R=20$ of the waiting-time guard. The saving of either rule is bounded by $1-C_{k_{\min}}/C_{k_{\max}}$. The cohort size is the number of uploads per round; the cumulative uploads to a target accuracy are the sum of the cohort sizes over the rounds needed to reach it, so that a reduction of the cumulative count can come from smaller cohorts or from fewer rounds, and the two are reported separately (Section 5.4 and the round-to-target columns of Section 5).


Table Z. Cohort rules (CIFAR-10 and FMNIST, Dirichlet $\alpha=0.5$, sample-count aggregation, bounds 5 and 10; mean of 6 runs). Accuracy columns: paired difference to the fixed cohort of ten with 95% bootstrap interval (percentage points).

| Rule | Mean cohort | Smallest $m_t$ | Uploads (GB) | $\Delta$ best acc. | $\Delta$ last-10 acc. | Max. wait |
|:--|--:|--:|--:|:--|:--|--:|
| Fixed cohort of ten | 10.00 | 10 | 33.6 | – | – | 10.0 |
| Absolute rule, Eq. (16) | 9.83 | 8 | 33.0 | +0.38 [−0.20, +0.96] | +0.47 [−0.10, +1.10] | 10.8 |
| Relative rate | 9.10 | 5 | 30.6 | +0.09 [−0.34, +0.58] | +0.39 [−0.20, +1.14] | 14.0 |


**Participation and aggregation influence.** With the feedback rule and sample-count aggregation (45 runs, nine settings) every client was selected at least once, the Jain index of the selection counts was 0.995–0.999 and the longest wait 10–13 rounds, below the guard threshold; the weakest tenth of the clients reached 63.2% and 76.3% accuracy on CIFAR-10 and FMNIST (Table Y). The cumulative aggregation influence of a client, the sum of its weights $S_i^t$ over the rounds, was positive for every client; on average over the runs the least influential client had 0.35 and the most influential 2.24 times the mean influence (Gini coefficient 0.21). The smallest weight of any selected client in any round was $2\times10^{-3}$ with sample-count weights and $4\times10^{-5}$ with stability weights, so that no weight was zero or negative.

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


# 3a. New section to insert: 4.3

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


# 5. Prepared answers (internal, not for the manuscript)

- **Why does the cohort stay close to its maximum?** Eq. (16) with the absolute loss reduction selects the maximum in 75% of the rounds; the ratio rule uses the whole range and lowers the uploads by 7.5% without a detectable change of accuracy (Table Z).
- **Why is the saving not larger?** It is bounded by 1 − Cmin/Cmax; the reproduction uses bounds of 5 and 10, wider than the 8 and 10 of the original ablation.
- **Where are the per-round cohort logs?** Every run records the cohort size of every round; they are released with the code.
- **Why sample-count weights?** They keep the aggregate consistent with Eq. (1) and give the higher last-10-round accuracy in 5 of 9 settings and a lower one in none (Table W).
