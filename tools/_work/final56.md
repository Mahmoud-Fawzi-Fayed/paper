
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

**R1-04 and R2-06: the utility score and its sum over x ∈ X**

- Fix: Eq. (5) is replaced by a three-level definition: per-example divergence over the label set (5a), batch mean (5b) and sample-weighted client score (5). The text states what a large and a small value mean and how the score enters the priority.
- Where: Section 4.2, Eqs. (5a), (5b), (5); Abstract and Introduction wording.
- Evidence: New subsection 5.4: rank correlation of the score with the marginal validation-loss gain (Table X), comparison with the global cross-entropy and with the parameter drift (Tables X and X2), behaviour under label noise.
- Declaration: The KL score is a label-free indicator of the benefit of an update; its association with the marginal gain was measured, and unlike a loss-based score it is not misled by corrupted labels.

**R1-05: the uncertainty penalty**

- Fix: Eq. (12) is the sample variance of the batch scores with B ≥ 2 and the batch mean (12a); the fitness (14) is built on the renamed priority Π and the penalty.
- Where: Section 4.2, Eqs. (12a), (12), (13), (14).
- Evidence: Section 5.4, Uncertainty penalty: effect of removing the penalty under the final aggregation and its rank AUC for label noise.
- Declaration: The penalty is a stabilising term in the fitness, evaluated by ablation.

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
Replacement 5
:::


::: {custom-style="BA-Edit"}
Replacement 5, edit 1: Abstract: wording of the KL utility
:::

::: {custom-style="BA-Loc"}
Location: Abstract (original line 99)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

FedFACS formulates client selection using a multi-objective fitness function combining the [expected reduction in]{custom-style="Del"} Kullback–Leibler (KL) divergence with a dynamic fairness baseline.

::: {custom-style="BA-Label-After"}
After (put instead)
:::

FedFACS formulates client selection using a multi-objective fitness function combining the Kullback–Leibler (KL) divergence [between local and global predictions]{custom-style="Add"} with a dynamic fairness baseline.


::: {custom-style="BA-Edit"}
Replacement 5, edit 2: Introduction: definition of the client utility
:::

::: {custom-style="BA-Loc"}
Location: Section 1, contributions paragraph (original line 137)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Client utility is quantified by estimating its potential contribution to the global model through the [expected decrease in]{custom-style="Del"} KL divergence [across]{custom-style="Del"} local and global predictive [distributions]{custom-style="Del"} (Kullback and Leibler 1951).

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Client utility is quantified by estimating its potential contribution to the global model through the KL divergence [between]{custom-style="Add"} local and global predictive [distributions, which measures how far the local model has moved from the global model]{custom-style="Add"} (Kullback and Leibler 1951).


::: {custom-style="BA-Edit"}
Replacement 5, edit 3: Section 4.2: KL score, Eqs. (5a), (5b), (5), and its effect on the priority
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2, first paragraph and Eq. (5) (original line 353)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Each [participating]{custom-style="Del"} client is denoted by [$C_i$, where $i \in \{1,\ldots,C\}$.]{custom-style="Del"} At round $t$, the central server sends $w_{\text{global}}^t$ to all [participating clients $C_i$.]{custom-style="Del"} The [KL]{custom-style="Del"} divergence [represents]{custom-style="Del"} the [client utility introduced previously in Eq. (3). Client $i$ produces]{custom-style="Del"} the [predictive distribution $P(x)$, where]{custom-style="Del"} the [corresponding global-model prediction is denoted by $Q(x)$, as defined in Eq. (5)]{custom-style="Del"} (Amini et al. 2025). [Furthermore, KL]{custom-style="Del"} divergence is [used as an indicator of]{custom-style="Del"} the divergence between local and global predictive [distributions, where larger values reflect a greater potential to improve]{custom-style="Del"} the global model with [new information. Therefore, selecting]{custom-style="Del"} clients with [higher]{custom-style="Del"} KL [divergence reduces]{custom-style="Del"} the [inconsistency between local and global predictive outputs, thereby enhancing model stability and generalization.]{custom-style="Del"}

::: {custom-style="DelBlock"}
$$ \Delta KL(P \parallel Q) = \sum_{x \in X} P(x)\log\left(\frac{P(x)}{Q(x)}\right) \qquad (5) $$
:::

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Each [candidate]{custom-style="Add"} client is denoted by [$i \in \mathcal{C}$.]{custom-style="Add"} At round $t$, the central server sends $w_{\text{global}}^t$ to all [candidate clients.]{custom-style="Add"} The [Kullback–Leibler (KL)]{custom-style="Add"} divergence [of a distribution $P$ from a reference distribution $Q$ is $\mathrm{KL}(P \parallel Q)=\sum_{c}P(c)\log\frac{P(c)}{Q(c)}$; it is nonnegative, zero only when $P=Q$, and asymmetric (Kullback and Leibler 1951). For a classification task with label set $\mathcal{Y}$, client $i$ compares]{custom-style="Add"} the [class probabilities $P_i^t(\cdot\mid x)$ of its model after local training with]{custom-style="Add"} the [probabilities $Q^t(\cdot\mid x)$ of]{custom-style="Add"} the [unchanged global model received at round $t$, on the same client-local scoring examples]{custom-style="Add"} (Amini et al. 2025). [The per-example]{custom-style="Add"} divergence is

::: {custom-style="AddBlock"}
$$ d_i^t(x)=\sum_{c\in\mathcal{Y}}P_i^t(c\mid x)\log\frac{P_i^t(c\mid x)}{Q^t(c\mid x)} \qquad (5a) $$
:::

[The scoring examples are divided into $B\ge 2$ nonempty batches $X_{i,b}^t$. The batch score and the client score, which weights every example equally, are]{custom-style="Add"}

::: {custom-style="AddBlock"}
$$ KL_{i,b}^t=\frac{1}{|X_{i,b}^t|}\sum_{x\in X_{i,b}^t}d_i^t(x) \qquad (5b) $$
:::

::: {custom-style="AddBlock"}
$$ \Delta KL_i^t=\frac{\sum_{b=1}^{B}|X_{i,b}^t|\,KL_{i,b}^t}{\sum_{b=1}^{B}|X_{i,b}^t|} \qquad (5) $$
:::

[The client-level KL score $\Delta KL_i^t$ (the symbol $\Delta$ denotes]{custom-style="Add"} the divergence between local and global [predictions) measures how far the]{custom-style="Add"} predictive [distribution of the locally trained model has moved from that of]{custom-style="Add"} the global model [on the client's scoring examples. A large value indicates that local training has altered the client's predictions substantially, so its update carries information not yet absorbed by the global model, and the client receives a higher utility term in the priority of Eq. (9). A small value indicates that the local model reproduces the global predictive distribution, so that its update is expected to change the aggregate little and the utility term is low. The score requires no labels.]{custom-style="Add"}

[In FedFACS the utility term is combined]{custom-style="Add"} with [the waiting-time term $F_i^t\ge 1$ of Eq. (6), which is larger in magnitude and is weighted by $1-a_i^t$, so that the priority is determined mainly by how long clients have waited and the KL score orders the]{custom-style="Add"} clients with [similar waiting times. Among such clients, those whose updates are more informative are therefore preferred, while no client is excluded by a low score. The experiments of Section 5.4 support this use: under label skew the score is positively associated with the reduction in global validation loss obtained by aggregating the update, and more closely so than the magnitude of the parameter change when clients hold few classes. Under label noise a loss-based score would place clients with corrupted labels first among clients with similar waiting times, whereas the]{custom-style="Add"} KL [score does not. The score thus orders clients by a label-free indicator of update benefit that remains reliable under noise, and]{custom-style="Add"} the [waiting-time term keeps every client participating.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 5, edit 4: Section 4.2: uncertainty penalty, stability score and fitness, Eqs. (12a), (12), (13), (14)
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2 (original line 415)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Client-side uncertainty is introduced into the fitness score as a variance based penalty term. It quantifies KL [estimate]{custom-style="Del"} across several small batches of local [client’s]{custom-style="Del"} dataset. [This term penalizes the clients whose]{custom-style="Del"} data [is highly unstable]{custom-style="Del"} or [non-representative data (i.e., high variance), even having a high utility as its variability between samples indicates that the data might be noisy or contain extreme outliers. While the clients with low uncertainty score reflect their stability that enhances robustness and stability under heterogeneous scenarios.]{custom-style="Del"} The uncertainty penalty term for client *i* is defined [as:]{custom-style="Del"}

::: {custom-style="DelBlock"}
$$ \sigma_i^2 = \frac{1}{B-1} \sum_{b=1}^{B} \left( KL_i^b - \overline{KL}_i \right)^2 \qquad (12) $$
:::

Where [$B$]{custom-style="Del"} indicates the total count of [mini batches, $\overline{KL_i}$]{custom-style="Del"} represents the average [KL-divergence]{custom-style="Del"} over batches for client $i$, and [$KL_i^b$]{custom-style="Del"} is the [KL-divergence]{custom-style="Del"} of batch [$b$.]{custom-style="Del"}

The stability score is derived from Eqs. (5) and (12). [This score is]{custom-style="Del"} used [for weighting]{custom-style="Del"} the local model updates in aggregation [step. It prioritizes]{custom-style="Del"} the [informative]{custom-style="Del"} and [stable clients over less informative ones to stabilize and accelerate the convergence]{custom-style="Del"} in [heterogeneous data environments without affecting fairness.]{custom-style="Del"} The formula of stability score is defined as follows:

$$ s_i^t = \Delta KL_i^t - \mu \sigma_i^2 \qquad (13) $$

The following equation summarizes the calculation formula of the composite fitness score:

::: {custom-style="DelBlock"}
$$ Fitness_i^t = P_i^t - \mu \sigma_i^2 \qquad (14) $$
:::

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Client-side uncertainty is introduced into the fitness score as a variance based penalty term. It quantifies [the dispersion of the]{custom-style="Add"} KL [score]{custom-style="Add"} across several small batches of [the]{custom-style="Add"} local [client's]{custom-style="Add"} dataset. [It measures differences between scoring batches; it does not by itself separate noisy]{custom-style="Add"} data [from legitimate heterogeneity]{custom-style="Add"} or [rare classes.]{custom-style="Add"} The uncertainty penalty term for client *i* is defined [from the batch mean (12a) and the sample variance (12):]{custom-style="Add"}

::: {custom-style="AddBlock"}
$$ \overline{KL}_i^t = \frac{1}{B}\sum_{b=1}^{B} KL_{i,b}^t \qquad (12a) $$
:::

::: {custom-style="AddBlock"}
$$ \sigma_i^2 = \frac{1}{B-1} \sum_{b=1}^{B} \left( KL_{i,b}^t - \overline{KL}_i^t \right)^2 \qquad (12) $$
:::

Where [$B\ge 2$]{custom-style="Add"} indicates the total count of [scoring batches (the sample variance is undefined for fewer batches), $\overline{KL}_i^t$]{custom-style="Add"} represents the average [KL score]{custom-style="Add"} over batches for client $i$, and [$KL_{i,b}^t$]{custom-style="Add"} is the [KL score]{custom-style="Add"} of batch [$b$ (Eq. (5b)).]{custom-style="Add"}

The stability score is derived from Eqs. (5) and (12). [It expresses the utility of a client's update net of its uncertainty and can be]{custom-style="Add"} used [to weight]{custom-style="Add"} the local model updates in [the]{custom-style="Add"} aggregation [step (Eq. (18));]{custom-style="Add"} the [weighting that is used is stated below]{custom-style="Add"} and [compared]{custom-style="Add"} in [Section 5.4.]{custom-style="Add"} The formula of [the]{custom-style="Add"} stability score is defined as follows:

$$ s_i^t = \Delta KL_i^t - \mu \sigma_i^2 \qquad (13) $$

[The raw score may be negative; it is converted to nonnegative aggregation weights in Eq. (18).]{custom-style="Add"} The following equation summarizes the calculation formula of the composite fitness score:

::: {custom-style="AddBlock"}
$$ Fitness_i^t = \Pi_i^t - \mu \sigma_i^2 \qquad (14) $$
:::


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


# 3. New subsection 5.4 (insert at the end of Section 5, before the Conclusion)

::: {custom-style="BA-Note"}
Heading: 5.4 Analysis of the selection score. The three tables below belong to this subsection (LaTeX source: section_5_4_selection_score.tex).
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


**Fairness term and mixing coefficient.** At the diagnostic rounds 5 to 100 the fairness term has a median of 1.88 and the utility score $\Delta KL_i^t$ a median of 0.73, and the coefficients have a median of 0.10 (below). The weighted utility term $a_i^t\Delta KL_i^t$ is therefore a median 3% of $(1-a_i^t)F_i^t$, the priority of Eq. (9) is rank-correlated with $F_i^t$ (Spearman 0.92 against 0.27 for $\Delta KL_i^t$), and 98.9% of the selected clients have a fairness term above the median: the priority is determined mainly by the waiting time, and the utility term orders the clients with similar waiting times. Table Y shows that this regime is the one that works. Without the fairness term ($a=1$) the Jain index falls to 0.56 and 0.35, 10.0% and 20.3% of the clients are never selected, and accuracy decreases by 2.6 and 2.2 points. A balanced constant $a=0.5$ lowers the Jain index to 0.92 and 0.94, lengthens the longest wait to 14–16 rounds, and lowers accuracy (best round, CIFAR-10: $-1.25$ [$-1.90$, $-0.73$]; last 10 rounds, FMNIST: $-1.53$ [$-3.42$, $-0.29$]). Rank-normalising both terms so that they carry equal weight, together with the waiting-time guard and with $a\in\{0.25,0.5\}$, gave the same outcome: the Jain index fell to 0.94–0.99, the longest wait rose to 17–20 rounds, and accuracy did not improve ($-0.5$ to $-0.8$ points). At the diagnostic rounds 5 to 100 the coefficients of the clients have a median of 0.10 (mean 0.14; 5th–95th percentile 0.001–0.33). In accuracy, no constant is significantly better than the feedback rule in any comparison, and the rule is significantly better in some ($a=0.05$ on CIFAR-10, best round: $-0.80$ [$-1.91$, $-0.10$] for the constant; $a=0.10$ on FMNIST, last 10 rounds: $-0.90$ [$-1.33$, $-0.30$]); the constants $a=0.05$ and $a=0.10$ differ from it by at most one round in the longest wait and by at most 0.002 in the Jain index. The rule thus provides this operating point without requiring the coefficient to be tuned.



**Aggregation weights.** Replacing the stability weights ($\kappa=1$ in Eq. (18)) by sample-count weights ($\kappa=0$), with the selection unchanged, leaves participation unchanged (Jain index 0.995–0.999, longest wait 10–13 rounds, no unselected client in all nine settings) and removes most of the oscillation of the global model at the end of training: in the five of nine dataset–partition settings with a detectable difference the last-10-round accuracy increases (by up to 9.6 [7.4, 12.9] points on MNIST with $\alpha=0.5$), in none does it decrease, and the round-to-round fluctuation of the test accuracy falls from 5.0 to 1.5 points on CIFAR-10 and from 3.9 to 1.0 points on FMNIST ($\alpha=0.5$). The best-round accuracy is higher in four settings, not distinguishable in four, and lower in one (CIFAR-10, $\alpha=0.1$). FedFACS therefore uses $\kappa=0$.



**Cohort size.** Eq. (16) with the absolute loss reduction $\rho^{t-1}$ keeps the cohort at $C_{k_{\max}}$ in 75% of the rounds and never below 7 clients in the 45 runs of the reproduction study (mean 9.71 [9.68, 9.75] clients, i.e.\ 2.9% fewer uploads than a fixed cohort of ten). Measuring the efficiency against the reference pace of the run (the ratio $\rho^{t-1}/\Omega^{t}$ in place of $\rho^{t-1}$ in Eq. (16)) uses the whole range from 5 to 10 clients: in Table Z the mean cohort falls from 9.83 to 9.10 clients and the upload volume by 7.5% relative to the absolute rule (9.0% relative to a fixed cohort), with best-round accuracy $-0.29$ [$-0.57$, $+0.05$] and last-10-round accuracy $-0.08$ [$-0.55$, $+0.41$] points, Jain index 0.997 against 0.998 and no unselected client; the longest wait rises from 10.8 to 14.0 rounds, below the threshold $R=20$ of the waiting-time guard. The saving of either rule is bounded by $1-C_{k_{\min}}/C_{k_{\max}}$. The cohort size is the number of uploads per round; the cumulative uploads to a target accuracy are the sum of the cohort sizes over the rounds needed to reach it, so that a reduction of the cumulative count can come from smaller cohorts or from fewer rounds, and the two are reported separately (Section 5.4 and the round-to-target columns of Section 5).



**Participation and aggregation influence.** With the feedback rule and sample-count aggregation (45 runs, nine settings) every client was selected at least once, the Jain index of the selection counts was 0.995–0.999 and the longest wait 10–13 rounds, below the guard threshold; the weakest tenth of the clients reached 63.2% and 76.3% accuracy on CIFAR-10 and FMNIST (Table Y). The cumulative aggregation influence of a client, the sum of its weights $S_i^t$ over the rounds, was positive for every client; on average over the runs the least influential client had 0.35 and the most influential 2.24 times the mean influence (Gini coefficient 0.21). The smallest weight of any selected client in any round was $2\times10^{-3}$ with sample-count weights and $4\times10^{-5}$ with stability weights, so that no weight was zero or negative.



**Uncertainty penalty.** The batch variance does not separate noisy from clean clients (rank AUC 0.45 [0.39, 0.52]), so it acts as a stabilising term in the fitness of Eq. (14) and not as a noise detector. With sample-count aggregation, removing it changes the best-round accuracy by $-0.04$ [$-0.22$, $+0.12$] points on CIFAR-10 and $-0.14$ [$-0.35$, $+0.27$] on FMNIST and lowers the last-10-round accuracy by 0.39 [0.14, 0.77] points on FMNIST, so the penalty improves the stability of the final model on FMNIST and is neutral on CIFAR-10. In the 96 main runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2% of the 4,316 rounds in which $\nu^t>0$, as Eq. (8) predicts.



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


# 5. Prepared answers (internal, not for the manuscript)

- **Is the utility term small?** Its weighted contribution is (a·ΔKL is a median 3% of (1−a)·F, Section 5.4); the utility term orders clients with similar waiting times, and a comparable weight lowered the Jain index and did not raise accuracy.
- **Why KL and not the loss?** Both predict the gain under label skew; under label noise only KL is not misled (ρ = +0.12 against −0.77). Selecting with a loss-based utility is not detectably different in accuracy.
- **Why sample-count weights?** Stability weights concentrate the weight on few clients and increased the oscillation of the global model; sample-count weights improved the last-10-round accuracy in 5 of 9 settings and decreased it in none.
- **Where are the baselines?** Main comparison tables (Replacement 11) are in section_5_main_tables.tex.
