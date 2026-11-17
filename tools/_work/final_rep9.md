
::: {custom-style="BA-Title"}
FedFACS: Replacement 9
:::

::: {custom-style="BA-Note"}
Scope. Replacement 9 covers the server-side procedure after the aggregation (validation, staging and commit of the state, Eq. (19)) and Algorithm 2. Locations refer to the original sn-article.tex. Evidence comes from our reproduced runs (ResNet-18 with frozen early layers, 100 clients, 100 rounds, five seeds; 689 runs in total) and the manuscript must say that its numbers come from this implementation. Colours: [red]{custom-style="Del"} = removed, [green]{custom-style="Add"} = added.
:::

::: {custom-style="BA-Note"}
NEW ELEMENTS. Table S (in part 3) and its paragraph are new: the original paper has no Section 5.4. Insert them in Section 5.4, after the paragraph on participation and aggregation influence (Section 5.4 itself is inserted before the Conclusion, see the Replacement 5 file).
:::

# 1. Comment, fix, location, evidence, declaration

**R1-01 and R2-03: when the counters are updated**

- Fix: The server stages the idle counters of Eq. (7) with the model and the feedback state after the aggregation and commits them in one step; a cancelled round leaves them unchanged. The counters are read at selection time from the committed state; Eq. (19) averages them over the N clients.
- Where: Section 4.2, paragraph after the aggregation and Eq. (19); Algorithm 2, lines 9 and 10.
- Evidence: Table S: in all 251 runs the selection counts and the longest wait recomputed from the per-round selections equal the logged values; the 13 unit tests of the equations pass, among them the increment and the reset of the idle counter.
- Declaration: The counters have one update time, and the logs reproduce it.

**R2-08: time indexing and notation**

- Fix: After round t the server computes the loss reduction, the reference rate and the deviation signal for the next round (Eqs. (15), (11), (10)) from completed rounds only. The population size is N throughout (K and C of the original are removed).
- Where: Section 4.2, Eq. (19) and the paragraph above it; Algorithm 2, inputs and lines 9 to 11.
- Evidence: The reference trajectory uses only past rounds (unit test); the cohort size is within its bounds in every logged round (Table S).
- Declaration: Every quantity used in round t comes from an earlier committed round.

**R1-21: one consistent and executable account**

- Fix: Algorithm 2 lists the received information, the cohort size from the previous round, the selection with the waiting-time guard, the aggregation with the weights of Eq. (18), the validation, the update of the control state and the counters, the commit and the broadcast to the N candidates, in the order of the text. Messages with identifiers describe a deployment. The restriction of the privacy and scalability statements is in the paragraph on the operating assumptions of Section 4.3.
- Where: Algorithm 2 and the paragraph that describes it, Section 4.2; Section 4.3.
- Evidence: Table S: the logged cohorts, selection counts, waiting times and uploaded volumes are consistent in all 251 runs; no round was cancelled and no update was non-finite in the 689 runs.
- Declaration: The procedure of the server follows the equations and runs in the stated order.


# 2. Edits: before and after, with locations


::: {custom-style="BA-Edit"}
Edit 1: Section 4.2: state after aggregation, commit and Eq. (19)
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
Edit 2: Section 4.2: description of Algorithm 2
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
Edit 3: Algorithm 2, inputs, outputs and steps
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2, Algorithm 2 (original line 310); changed lines are marked.
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


# 3. New text and table for Section 5.4

**Protocol consistency.** Table S lists the consistency checks applied to the per-round logs. Every check holds in all 251 runs of FedFACS and its variants, and the 13 unit tests of the equations of Section 4 (idle counter, mixing coefficient, aggregation weights, cohort size, reference trajectory) pass.

Table S. Consistency of the logged protocol in the 251 runs of FedFACS and its ablation variants. Across all 689 runs no round was cancelled and no client update was non-finite.

| Check | Runs passing |
|:--|--:|
| Cohort size within $[C_{k_{\min}},C_{k_{\max}}]$ in every round | 251 / 251 |
| Logged cohort size equals the number of selected clients | 251 / 251 |
| Selection counts recomputed from the per-round selections equal the logged counts | 251 / 251 |
| Longest wait recomputed from the per-round selections equals the logged value | 251 / 251 |
| Uploaded volume equals the sum of the cohort sizes times the model size | 251 / 251 |
| Number of logged rounds equals the configured number of rounds | 251 / 251 |


# 4. Notation declared

| Symbol | Declaration |
|:--|:--|
| $N$ | CHANGED: client population; replaces $K$ and $C$ of the original |
| $r_i^{t+1}$, $\overline{r^{t+1}}$ (7), (19) | CHANGED: idle counter and population mean after round $t$, staged after the aggregation and committed with the model |
| $\rho^{t}$, $\Omega^{t+1}$, $\nu^{t+1}$ (15), (11), (10) | previously declared; computed after round $t$ from completed rounds and used from round $t+1$ |


# 5. Notes for the authors (internal, not for the manuscript)

- **Messages with identifiers.** The simulation is synchronous; the sentence on identifiers describes a deployment (introduced with "In a deployment").
- **Reproducibility package.** The runs log the configuration, seeds, per-round selections, cohort sizes, validation loss and accuracy, the mean mixing coefficient and fairness term, the deviation signal and the traffic counters (JSON). The individual fitness scores of every round are not logged. A release statement needs the authors' confirmation.