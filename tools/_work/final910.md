
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

**Replacement 9. R1-01 and R2-03: when the counters are updated**

- Fix: The server stages the idle counters of Eq. (7) together with the model and the feedback state after the aggregation and commits them in one step; a cancelled round leaves the counters unchanged. The counter is read at selection time from the committed state, so that its initialisation, update timing and population mean (Eq. (19), with the population size N) are fixed.
- Where: Section 4.2, paragraph after the aggregation and Eq. (19); Algorithm 2, lines 9 and 10.
- Evidence: Table S: in all 251 runs of FedFACS and its variants the selection counts and the longest wait, recomputed from the per-round selections, equal the logged values; the 13 unit tests of the equations pass, among them the increment and the reset of the idle counter.
- Declaration: The counter has one specified update time and the logs reproduce it.

**Replacement 9. R2-08: time indexing and notation**

- Fix: After round t the server computes the reduction of the validation loss, the reference rate and the deviation signal for the next round (Eqs. (15), (11), (10)) from completed rounds only; the next selection uses the committed values. The population size is N throughout (the symbols K and C of the original are removed) and Eq. (19) averages the counters of round t+1 over N clients.
- Where: Section 4.2, Eq. (19) and the paragraph above it; Algorithm 2, inputs and lines 9 to 11.
- Evidence: The reference trajectory uses only past rounds (unit test); the cohort size is within its bounds in every logged round of the 251 runs (Table S).
- Declaration: Every quantity used in round t is computed in an earlier committed round.

**Replacement 9. R1-21: one consistent and executable account**

- Fix: Algorithm 2 lists the received information (scores, models, stability scores, sample counts), the cohort size from the previous round, the selection with the waiting-time guard, the aggregation with the weights of Eq. (18), the validation, the update of the control state and the counters, the commit and the broadcast to the N candidates, in the order of the text. In a deployment, messages carry run and round identifiers and duplicates or stale messages are rejected. The restriction of the privacy and scalability statements is in the paragraph on the operating assumptions of Section 4.3.
- Where: Algorithm 2 (inputs, outputs, lines 1 to 11) and the paragraph that describes it, Section 4.2; Section 4.3, operating assumptions.
- Evidence: Table S: the logged cohorts, selection counts, waiting times and uploaded volumes are consistent in all 251 runs; no round was cancelled and no update was non-finite in the 689 runs. The messages with identifiers describe a deployment; the simulation is synchronous and does not exercise them.
- Declaration: The procedure of the server follows the equations and can be executed in the stated order.

**Replacement 10. R1-08 and R2-01: the communication model and the hidden costs**

- Fix: Eq. (23) counts the uploaded updates over the first T rounds. Eq. (23a) adds the downloads, the auxiliary traffic and the setup, calibration and final-model traffic, over all attempted rounds. Local training steps, scoring forward passes and elapsed time are reported separately. The text states that the saving of FedFACS is in the uploaded updates, while every candidate receives and trains the model.
- Where: Section 5.1, performance metrics (Eqs. (23), (23a)); Section 5.4, Communication and computation cost and Table V.
- Evidence: Table V (45 runs per method): FedFACS downloads to and trains all 100 candidates, 10.0 times the local steps of random sampling; its uploads are 9.71 per round against 10; to the common target it uploads 6.2% fewer updates than random sampling but transmits 198 against 37 GB in total.
- Declaration: The total communication, the local computation and the uploads are measured under one explicit model, and the claim is limited to the uploads.

**Replacement 10. R1-09 and R2-15: what the Jain index measures**

- Fix: The index of Eq. (24) is read as the equality of the quality-adjusted participation; with q equal to one it is the equality of participation. Three notions are distinguished: equality of participation, participation proportional to quality, and fairness of the outcome (client-level accuracy). The interpretation of 0.5 as a boundary is removed; the minimum is 1/N and a value between 0.5 and 1 does not imply that every client participates. The never-selected share, the longest wait and the client-level accuracy are reported.
- Where: Section 5.1, performance metrics (Eqs. (24)-(25)); Section 5.4, Participation fairness and Table U.
- Evidence: Table U (Scenario 3, 3 seeds): the raw index of FedFACS is 0.999 and 0.997 against 0.919 for random sampling; the quality-adjusted index is 0.973 and 0.963, lower because the selection is nearly uniform; Greedy leaves 72% and 66% of the clients unselected. Example: two clients with q of 10 and 5 selected twice and once give 1.0 for the adjusted and 0.9 for the raw index; 90 of 100 clients served uniformly give 0.9.
- Declaration: The index is interpreted correctly, and participation, quality-proportional participation and outcome are measured separately.

**Replacement 10. recall, precision and F1 (supports the reconciliation of Table 4 in Replacement 11)**

- Fix: The text states that the three quantities are computed per class from the confusion matrix of the test set and averaged with equal class weights.
- Where: Section 5.1, after Eq. (22); Section 5.4, Classification metrics and Table T.
- Evidence: Table T (15 runs per row): on CIFAR-10 and FMNIST the macro-recall equals the accuracy in every run; on MNIST the two differ by at most 0.92 points; the macro-F1 differs from the macro-recall by at most 0.7 points. In the original Table 4 the F1 exceeded the recall by 4 to 10 points, which is not possible for macro-averages on these test sets.
- Declaration: The averaging is stated, and the reproduced values follow it.


# 2. Edits: before and after, with locations


::: {custom-style="BA-Sub"}
Replacement 9
:::


::: {custom-style="BA-Edit"}
Replacement 9, edit 1: Section 4.2: state after aggregation, commit and Eq. (19)
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2, end of the model description (original line 465)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

[One more step,]{custom-style="Del"} the [resulting]{custom-style="Del"} model [is assessed]{custom-style="Del"} on a separate validation [set, then]{custom-style="Del"} the [centralized server updates its deviation control signal]{custom-style="Del"} and [global fairness baseline as defined in Eq. (19). As]{custom-style="Del"} the [final step,]{custom-style="Del"} the [resulting]{custom-style="Del"} global model parameters $w_{{global}}^{t+1}$, $\overline{r^{t+1}}$, and $\nu^{t+1}$ are broadcast to [the entire set of $C$]{custom-style="Del"} clients for the following training round.

::: {custom-style="DelBlock"}
$$ \overline{r^{t+1}} = \frac{1}{K} \sum_{i=1}^{K} r_i^t \qquad (19) $$
:::

::: {custom-style="BA-Label-After"}
After (put instead)
:::

[After aggregation,]{custom-style="Add"} the [server evaluates the candidate]{custom-style="Add"} model on a separate validation [set and stages $\rho^t$, $\Omega^{t+1}$, $\nu^{t+1}$, $r_i^{t+1}$ and $\overline{r^{t+1}}$ (Eq. (19)). The model,]{custom-style="Add"} the [feedback state]{custom-style="Add"} and the [counters are committed together only if all numerical and protocol checks pass; otherwise]{custom-style="Add"} the [staged state is discarded and the consumed resources are still recorded. In a deployment, messages carry run and round identifiers, and duplicate or stale messages are rejected. The committed]{custom-style="Add"} global model parameters $w_{{global}}^{t+1}$, $\overline{r^{t+1}}$, and $\nu^{t+1}$ are [then]{custom-style="Add"} broadcast to [all $N$ candidate]{custom-style="Add"} clients for the following training round.

::: {custom-style="AddBlock"}
$$ \overline{r^{t+1}} = \frac{1}{N} \sum_{i=1}^{N} r_i^{t+1} \qquad (19) $$
:::


::: {custom-style="BA-Edit"}
Replacement 9, edit 2: Section 4.2: description of Algorithm 2
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2, paragraph after Algorithm 1 (original line 347)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

Furthermore, algorithm 2 outlines the overall procedure of server-side client selection and model aggregation. Clients are ranked according to their fitness scores. In addition, the cohort size is dynamically defined [to select]{custom-style="Del"} the [top $C^t_k$ clients based on]{custom-style="Del"} global convergence efficiency [$\rho$]{custom-style="Del"} (Lines [3-7).]{custom-style="Del"} The centralized server [combines]{custom-style="Del"} the [locally]{custom-style="Del"} trained [models received from]{custom-style="Del"} the selected clients [using a stability-aware weighting strategy]{custom-style="Del"} to construct an aggregated global model for the subsequent training (Lines [8).]{custom-style="Del"} Furthermore, the resulting [global]{custom-style="Del"} model is [then]{custom-style="Del"} validated using the validation [dataset. (Lines]{custom-style="Del"} 9). [Every]{custom-style="Del"} participating client is supplied with the latest global model, accompanied by the fairness baseline and the deviation control signal (Lines [10-13).]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

Furthermore, algorithm 2 outlines the overall procedure of server-side client selection and model aggregation. Clients are ranked according to their fitness scores. In addition, the cohort size [$m_t$]{custom-style="Add"} is dynamically defined [from]{custom-style="Add"} the global convergence efficiency [of the previous round, and the cohort of $m_t$ clients is selected, overdue clients first and then those of highest fitness]{custom-style="Add"} (Lines [3-6).]{custom-style="Add"} The centralized server [receives]{custom-style="Add"} the trained [models, stability scores and sample counts of]{custom-style="Add"} the selected clients [and combines them with the nonnegative normalised weights of Eq. (18)]{custom-style="Add"} to construct an aggregated global model for the subsequent training (Lines [7-8).]{custom-style="Add"} Furthermore, the resulting [candidate]{custom-style="Add"} model is validated using the validation [dataset (Line]{custom-style="Add"} 9). [The model, the feedback state and the idle counters are then committed together, and every]{custom-style="Add"} participating client is supplied with the latest global model, accompanied by the fairness baseline and the deviation control signal (Lines [10-11).]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 9, edit 3: Algorithm 2, inputs, outputs and steps
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2, Algorithm 2 (original line 310); changed lines are marked, unchanged lines are shown in plain text.
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

**Input:** [$T$: communication rounds, $\{D_i\}_{i=1,\ldots,N}$: local datasets of clients, $C$: total number of clients, $\Omega^t$ reference convergence rate, $r^{t+1}_i$: number on idle consecutive rounds, $w^t_i$: local model for client $i$, $Fitness^t_i$: fitness score, $s^t_i$: stability score.]{custom-style="Del"}

**Output:** $w^{t+1}_{global}$: Global model, $\overline{r^{t+1}}$: Average fairness baseline, $\nu^{t+1}$: Deviation control signal.

1. [**Initialize the global model parameters**]{custom-style="Del"}

2. **For each communication round** $t \in \{1,\ldots,T\}$ **do**

3. Receive from clients: $\{Fitness^t_i\}$

4. [**Sort** clients according to their fitness scores in descending order]{custom-style="Del"}

5. [Compute global convergence efficiency $(\rho)$ using (15)]{custom-style="Del"}

6. [Estimate number of top $C^t_k$ to select using (16)]{custom-style="Del"}

7. [**Select** $C^t_k$ clients with highest fitness scores]{custom-style="Del"}

8. [**Aggregate** selected clients' updates with stability weights:]{custom-style="Del"}

9. [**Evaluate** updated global model on validation data]{custom-style="Del"}

10. [**Update** $\overline{r^{t+1}}$ using (19)]{custom-style="Del"}

11. [Compute $\nu^{t+1}$: $\nu^{t+1}=\Omega^{t+1}-\rho^{t+1}$]{custom-style="Del"}

12. [Broadcast to all $C$ clients: $\{w^{t+1}_{global}, \nu^{t+1}, \overline{r^{t+1}}\}$]{custom-style="Del"}

13. **End for**

::: {custom-style="BA-Label-After"}
After (put instead)
:::

**Input:** [$T$: communication rounds, $\{D_i\}_{i=1,\ldots,N}$: local datasets of clients, $N$: total number of clients, $\Omega^t$ reference convergence rate, $r^{t+1}_i$: number on idle consecutive rounds, $w^t_i$: local model for client $i$, $Fitness^t_i$: fitness score, $s^t_i$: stability score, $n_i$: sample count, $R=\lceil N/C_{k_{\min}}\rceil$: waiting-time threshold.]{custom-style="Add"}

**Output:** $w^{t+1}_{global}$: Global model, $\overline{r^{t+1}}$: Average fairness baseline, $\nu^{t+1}$: Deviation control signal.

1. [**Initialize** the global model parameters, $r^1_i = 0$, $\overline{r^1}=0$, $\rho^0=0$, $\nu^1=0$, $\Omega^2=0$]{custom-style="Add"}

2. **For each communication round** $t \in \{1,\ldots,T\}$ **do**

3. Receive from clients: $\{Fitness^t_i\}$

4. [**Sort** clients according to their fitness scores in descending order (ties by ascending identifier)]{custom-style="Add"}

5. [Compute the cohort size $m_t$ using (16) from $\rho^{t-1}$]{custom-style="Add"}

6. [**Select** the $m_t$ clients $C^t_k$: overdue clients first (largest $r^t_i$ first, ties by identifier), then those of highest fitness (Eq. (3), Section 4.3)]{custom-style="Add"}

7. [**Receive** $w^t_i, s^t_i, n_i$ from the selected clients]{custom-style="Add"}

8. [**Aggregate** with the weights $S^t_i$ from (18):]{custom-style="Add"}

9. [**Evaluate** the candidate model on validation data; compute $\rho^t$ using (15), $\Omega^{t+1}$ using (11) and $\nu^{t+1}$ using (10)]{custom-style="Add"}

10. [**Update** $r^{t+1}_i$ using (7) and $\overline{r^{t+1}}$ using (19); **commit** model, feedback state and counters together]{custom-style="Add"}

11. [Broadcast to all $N$ clients: $\{w^{t+1}_{global}, \nu^{t+1}, \overline{r^{t+1}}\}$]{custom-style="Add"}

12. **End for**


::: {custom-style="BA-Sub"}
Replacement 10
:::


::: {custom-style="BA-Edit"}
Replacement 10, edit 1: Section 5, metrics: round-to-target
:::

::: {custom-style="BA-Loc"}
Location: Section 5.1, performance metrics (original line 504)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

*Round-to-accuracy*: defines the training [iteration count required to reach]{custom-style="Del"} a specified [accuracy.]{custom-style="Del"} This metric provides an assessment of the convergence efficiency of the client selection [strategy and the communication cost associated with achieving the desired performance,]{custom-style="Del"} where fewer communication rounds indicate faster [convergence and lower communication requirements.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

*Round-to-accuracy*: defines the [first completed]{custom-style="Add"} training [round at which the accuracy reaches]{custom-style="Add"} a specified [target on the validation data; a run that does not reach the target within its budget is recorded as not reached.]{custom-style="Add"} This metric provides an assessment of the convergence efficiency of the client selection [strategy,]{custom-style="Add"} where fewer communication rounds indicate faster [convergence.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 10, edit 2: Section 5, metrics: macro-averaging of recall, precision and F1
:::

::: {custom-style="BA-Loc"}
Location: Section 5.1, performance metrics, after Eq. (22) (original line 525)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

In the formulation, $TP$, $FP$, and $FN$ indicate correctly detected, incorrectly predicted, and missed positive instances, respectively. These metrics evaluate the performance, stability, and generalization ability of FedFACS under non-IID conditions.

::: {custom-style="BA-Label-After"}
After (put instead)
:::

In the formulation, $TP$, $FP$, and $FN$ indicate correctly detected, incorrectly predicted, and missed positive instances, respectively. [For ten classes the three quantities are computed per class from the confusion matrix of the test set and averaged with equal class weights (macro-average).]{custom-style="Add"} These metrics evaluate the performance, stability, and generalization ability of FedFACS under non-IID conditions.


::: {custom-style="BA-Edit"}
Replacement 10, edit 3: Section 5, metrics: cumulative uploads and the total communication, Eqs. (23) and (23a)
:::

::: {custom-style="BA-Loc"}
Location: Section 5.1, performance metrics (original line 528)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

*Cumulative number of selected clients until convergence ($C_{total}$)*: indicates the overall number of [clients selected]{custom-style="Del"} for aggregation across [all]{custom-style="Del"} training [rounds before]{custom-style="Del"} the [global model reaches]{custom-style="Del"} the [target accuracy.]{custom-style="Del"}

::: {custom-style="DelBlock"}
$$ C_{\text{total}} = \sum_{t=1}^{T} C_k^t \qquad (23) $$
:::

::: {custom-style="BA-Label-After"}
After (put instead)
:::

*Cumulative number of selected clients until convergence ($C_{total}$)*: indicates the overall number of [client updates uploaded]{custom-style="Add"} for aggregation across [the first $T$]{custom-style="Add"} training [rounds:]{custom-style="Add"}

::: {custom-style="AddBlock"}
$$ C_{\text{total}} = \sum_{t=1}^{T} \left|C_k^t\right| \qquad (23) $$
:::

[The total communication $\mathrm{Comm}_{\mathrm{total}}(T)$, in bytes over]{custom-style="Add"} the [first $T$ rounds, also includes downloads, auxiliary traffic and any setup or calibration traffic:]{custom-style="Add"}

::: {custom-style="AddBlock"}
$$ \mathrm{Comm}_{\mathrm{total}}(T)=\mathrm{Comm}_{\mathrm{setup}}+\mathrm{Comm}_{\mathrm{cal}}+\mathrm{Comm}_{\mathrm{final}}+\sum_{t\in\mathcal{R}(T)}\left(\mathrm{Comm}^t_{\mathrm{down}}+\mathrm{Comm}^t_{\mathrm{up}}+\mathrm{Comm}^t_{\mathrm{aux}}\right) \qquad (23a) $$
:::

[where $\mathrm{Comm}^t_{\mathrm{down}}$, $\mathrm{Comm}^t_{\mathrm{up}}$ and $\mathrm{Comm}^t_{\mathrm{aux}}$ are]{custom-style="Add"} the [model-download, update-upload and auxiliary traffic of round $t$ (in bytes), $\mathrm{Comm}_{\mathrm{setup}}$, $\mathrm{Comm}_{\mathrm{cal}}$ and $\mathrm{Comm}_{\mathrm{final}}$ are the setup, calibration (zero for FedFACS) and final-model traffic, and $\mathcal{R}(T)$ is the set of attempted rounds, including partial and cancelled ones. Local training steps, scoring forward passes and elapsed time are counted separately (Table V).]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Replacement 10, edit 4: Section 5, metrics: Jain's index, quality and the reading of the index, Eqs. (24)-(25)
:::

::: {custom-style="BA-Loc"}
Location: Section 5.1, performance metrics (original line 535)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

*Jain’s Fairness Index (JFI)*: quantifies [client-selection]{custom-style="Del"} fairness [using]{custom-style="Del"} the [number of times each client is selected throughout training]{custom-style="Del"} (Shi et al. 2024; Cho et al. 2020).

::: {custom-style="DelBlock"}
$$ JFI = \frac{\left(\sum_{i=1}^{n} \frac{p_i}{q_i}\right)^2}
{n \cdot \sum_{i=1}^{n} \left(\frac{p_i}{q_i}\right)^2} \qquad (24) $$
:::

$$ q_i = (\text{number of labels}) \times (1 - \text{percentage of noisy data}) \qquad (25) $$

For client $i$, $p_i$ reflects its rate of participation in model aggregation, while [$n$]{custom-style="Del"} denotes the overall client population, and $q_i$ represents the quality of its locally stored dataset (Shi et al. 2023). [When $JFI = 1$, it refers]{custom-style="Del"} to equal participation [for]{custom-style="Del"} all [clients,]{custom-style="Del"} when the [values in]{custom-style="Del"} the [range $0.5 \leq JFI < 1$ indicate]{custom-style="Del"} that [all clients participates]{custom-style="Del"} with [different times, and values below $0.5$ represent the unfair participation.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

*Jain’s Fairness Index (JFI)*: quantifies [the]{custom-style="Add"} fairness [of participation on]{custom-style="Add"} the [quality-adjusted participation $p_i/q_i$]{custom-style="Add"} (Shi et al. 2024; Cho et al. 2020).

::: {custom-style="AddBlock"}
$$ JFI = \frac{\left(\sum_{i=1}^{N} \frac{p_i}{q_i}\right)^2}
{N \cdot \sum_{i=1}^{N} \left(\frac{p_i}{q_i}\right)^2} \qquad (24) $$
:::

$$ q_i = (\text{number of labels}) \times (1 - \text{percentage of noisy data}) \qquad (25) $$

For client $i$, $p_i$ reflects its rate of participation in model aggregation, while [$N$]{custom-style="Add"} denotes the overall client population, and $q_i$ represents the quality of its locally stored dataset (Shi et al. 2023). [Therefore $JFI = 1$ means participation proportional]{custom-style="Add"} to [quality, which equals]{custom-style="Add"} equal participation [only when]{custom-style="Add"} all [$q_i$ are equal. The minimum value is $1/N$, and a value between $0.5$ and $1$ can also arise]{custom-style="Add"} when [some clients are never served (serving 90 of 100 equal-quality clients uniformly gives $0.9$). Because $q_i$ depends on]{custom-style="Add"} the [noise level, JFI differences may partly reflect selection by data quality. Three notions of fairness are therefore distinguished: equality of participation, measured by Eq. (24) with $q_i=1$; participation proportional to quality, measured by Eq. (24); and fairness of]{custom-style="Add"} the [outcome, measured by the accuracy of the global model on the held-out local data of each client (mean, standard deviation and 10th percentile). The share of clients]{custom-style="Add"} that [are never selected and the longest waiting time are reported]{custom-style="Add"} with [them (Table U).]{custom-style="Add"}


# 3. New text and tables for Section 5.4 (do not exist in the original paper)

::: {custom-style="BA-Note"}
Insert the four paragraphs and Tables V, U, T and S below in Section 5.4, after the paragraph on participation and aggregation influence. Every number is recomputed from the run logs by tools/ev910.py.
:::

**Communication and computation cost.** Table V counts the resources over 100 rounds. FedFACS sends the model to all $N=100$ candidates and trains all of them, so that its downloads and local steps are 10.0 times those of random sampling, while its uploads are 9.71 per round against 10. After 100 rounds the volume of Eq. (23a) is 5.5 times that of random sampling (368.6 against 67.2 GB). To the common target accuracy FedFACS uploads 520 updates against 555 for random sampling (6.2% fewer) and transmits 198 against 37 GB in total, since every candidate receives and trains the model. The saving of FedFACS is therefore in the uploaded updates; Power-of-Choice downloads 20 and DivFL 100 models per round for a cohort of ten. The simulated elapsed time per round is 3.4 s against 0.3 s (clients are trained sequentially on one GPU).

Table V. Resources per round and cost to the common target accuracy (45 runs per method: CIFAR-10, FMNIST and MNIST; Dirichlet $\alpha\in\{0.1,0.5\}$ and two-class partitions; five seeds; 100 rounds; $N=100$ clients). Per round: models downloaded, updates uploaded, local SGD steps, scoring or probing forward passes (thousands). Total GB is the volume of Eq. (23a) without setup traffic. Cost to target: uploaded updates (runs reaching the target / runs) and total GB, averaged over the runs that reach the target. Time is the simulated elapsed time per round.

| Method | Down | Up | Steps | Scoring (k) | Total GB | Uploads to target | GB to target | s/round |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| Random sampling (FedAvg) | 10.0 | 10.00 | 268 | 0.0 | 67.2 | 555 (45/45) | 37.3 | 0.30 |
| Power-of-Choice | 20.0 | 10.00 | 313 | 5.1 | 100.8 | 528 (44/45) | 53.2 | 0.38 |
| Oort | 10.0 | 10.00 | 291 | 0.0 | 67.2 | 488 (44/45) | 32.8 | 0.31 |
| DivFL | 100.0 | 10.00 | 285 | 25.6 | 369.8 | 668 (25/45) | 247.1 | 0.57 |
| FedFACS ($\kappa=0$) | 100.0 | 9.71 | 2680 | 51.2 | 368.6 | 520 (44/45) | 198.3 | 3.42 |

**Participation fairness.** Table U separates three notions. The Jain index of the selection counts (equality of participation) is 0.999 and 0.997 for FedFACS on CIFAR-10 and FMNIST, against 0.919 and 0.919 for random sampling; no client is left unselected and the longest wait is 10 rounds. The quality-adjusted index of Eq. (24) is 0.973 and 0.963; it equals one when $p_i$ is proportional to $q_i$, whereas FedFACS serves the clients almost uniformly, so that two clients with $q_i=10$ and $q_i=5$ selected twice and once give 1.0 for the adjusted and 0.9 for the raw index. Greedy selection leaves 72% and 66% of the clients unselected. The outcome is described by the client-level accuracy: its 10th percentile is 64.0% and 81.8% for FedFACS against 64.4% and 82.4% for random sampling.

Table U. Participation and outcome fairness in Scenario 3 (noisy clients, IID; mean of 3 seeds, 100 rounds). JFI is Eq. (24) with $q_i=1$ and JFI$_q$ is Eq. (24). Client accuracy: mean, standard deviation and 10th percentile (%) of the global model on the held-out local data of each client. The FedFACS runs use the stability weights ($\kappa=1$); the selection rule is the same for all $\kappa$.

| Dataset | Method | JFI | JFI$_q$ | Never selected (%) | Longest wait | Acc. mean | Acc. s.d. | Acc. p10 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| CIFAR-10 | Random | 0.919 | 0.899 | 0.0 | 57 | 70.7 | 4.9 | 64.4 |
| CIFAR-10 | Power-of-Choice | 0.751 | 0.683 | 1.0 | 98 | 69.0 | 5.0 | 62.2 |
| CIFAR-10 | Greedy | 0.119 | 0.120 | 72.3 | 100 | 62.8 | 5.0 | 56.3 |
| CIFAR-10 | FairFedCS | 0.905 | 0.878 | 0.0 | 40 | 71.1 | 4.9 | 65.1 |
| CIFAR-10 | FedFACS | 0.999 | 0.973 | 0.0 | 10 | 70.2 | 5.0 | 64.0 |
| FMNIST | Random | 0.919 | 0.894 | 0.0 | 57 | 86.2 | 3.3 | 82.4 |
| FMNIST | Power-of-Choice | 0.539 | 0.514 | 27.3 | 100 | 85.1 | 3.5 | 80.6 |
| FMNIST | Greedy | 0.119 | 0.118 | 65.7 | 100 | 82.6 | 3.9 | 77.8 |
| FMNIST | FairFedCS | 0.877 | 0.839 | 0.0 | 38 | 86.2 | 3.4 | 81.8 |
| FMNIST | FedFACS | 0.997 | 0.963 | 0.0 | 10 | 86.2 | 3.3 | 81.8 |

**Classification metrics.** Table T reports the macro-averaged metrics. On CIFAR-10 and FMNIST, whose test sets have equal class sizes, the macro-recall equals the accuracy in every run; on MNIST, whose classes are unbalanced, the two differ by at most 0.92 points. The macro-F1 differs from the macro-recall by at most 0.7 points in every row.

Table T. Accuracy and macro-averaged recall, precision and F1 (%) computed from the confusion matrix of the test set (mean of 15 runs per row: three partitions, five seeds).

| Dataset | Method | Accuracy | Recall | Precision | F1 |
|:--|--:|--:|--:|--:|--:|
| CIFAR-10 | Random sampling | 66.38 | 66.38 | 70.26 | 65.96 |
| CIFAR-10 | FedFACS ($\kappa=0$) | 65.60 | 65.60 | 70.62 | 65.30 |
| FMNIST | Random sampling | 79.93 | 79.93 | 82.33 | 79.23 |
| FMNIST | FedFACS ($\kappa=0$) | 79.37 | 79.37 | 82.26 | 78.79 |
| MNIST | Random sampling | 93.65 | 93.51 | 94.04 | 93.55 |
| MNIST | FedFACS ($\kappa=0$) | 93.72 | 93.57 | 94.14 | 93.62 |

**Protocol consistency.** Table S lists the consistency checks applied to the per-round logs. Every check holds in all 251 runs of FedFACS and its variants, and the 13 unit tests of the equations of Section 4 (idle counter, mixing coefficient, aggregation weights, cohort size, reference trajectory) pass.

Table S. Consistency of the logged protocol in the 251 runs of FedFACS and its ablation variants. Across all 689 runs of the reproduction no round was cancelled and no client update was non-finite.

| Check | Runs passing |
|:--|--:|
| Cohort size within $[C_{k_{\min}},C_{k_{\max}}]$ in every round | 251 / 251 |
| Logged cohort size equals the number of selected clients | 251 / 251 |
| Selection counts recomputed from the per-round selections equal the logged counts | 251 / 251 |
| Longest wait recomputed from the per-round selections equals the logged value | 251 / 251 |
| Uploaded volume equals the sum of the cohort sizes times the model size | 251 / 251 |
| Number of logged rounds equals the configured number of rounds | 251 / 251 |


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


# 5. Prepared answers and open points (internal, not for the manuscript)

- **Does FedFACS reduce communication?** It reduces the uploads (6.2% fewer than random sampling to the common target); the total volume to the target is 5.3 times that of random sampling (198 against 37 GB) and the local computation is 10 times. The wording of the title and the abstract ("communication-efficient") has to be limited to the uploads; this is handled in Replacement 11.
- **Is there a configuration where the total volume is lower?** Not in the reproduction: all candidates download the model and train. A saving in the total volume would need a lighter scoring pass or a subset of candidates; this is outside the present method.
- **Why is the quality-adjusted index below the raw index?** FedFACS serves the clients almost uniformly (raw index 0.999), while the adjusted index is one only for participation proportional to quality.
- **Scenario 4.** The reproduction contains Scenario 3 only; Table U has no Scenario 4 rows.
- **Messages with identifiers.** The simulation is synchronous and single-process; the sentence on identifiers describes a deployment and is introduced with "In a deployment".
- **Reproducibility package.** The runs log the configuration, seeds, per-round selections, cohort sizes, validation loss and accuracy, the mean mixing coefficient and fairness term, the deviation signal and the traffic counters (JSON); the individual fitness scores of every round are not logged, so a package that includes them needs a rerun; a release statement needs the authors' confirmation.
- **Original Table 4.** Its recall and F1 values are not reproduced by Table T (macro-recall equals accuracy on balanced test sets); they are recomputed or removed in Replacement 11.
