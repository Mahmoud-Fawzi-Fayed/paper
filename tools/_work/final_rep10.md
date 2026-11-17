
::: {custom-style="BA-Title"}
FedFACS: Replacement 10
:::

::: {custom-style="BA-Note"}
Scope. Replacement 10 covers the metric definitions that concern communication and fairness (Eqs. (23), (23a), (24)) and one new table with the cost and the participation of the methods. Locations refer to the original sn-article.tex. Evidence comes from our reproduced runs (ResNet-18 with frozen early layers, 100 clients, 100 rounds, five seeds; 689 runs in total) and the manuscript must say that its numbers come from this implementation. Colours: [red]{custom-style="Del"} = removed, [green]{custom-style="Add"} = added.
:::

::: {custom-style="BA-Note"}
NEW ELEMENTS. Eq. (23a), Table V and its paragraph are new: the original paper has no Section 5.4. Insert them in Section 5.4, after the paragraph on participation and aggregation influence (Section 5.4 itself is inserted before the Conclusion, see the Replacement 5 file). Table 4 of the original paper is not changed here; Replacement 11 treats it.
:::

# 1. Comment, fix, location, evidence, declaration

**R1-08 and R2-01: the communication model and the hidden costs**

- Fix: Eq. (23) counts the uploaded updates. Eq. (23a) adds the downloads and the control messages, so that the total communication of every method is counted under one model. Table V reports the models sent, the updates uploaded, the local steps and the volume to the target for all methods, run in the same simulation.
- Where: Section 5.1, Eqs. (23), (23a); Section 5.4, paragraph and Table V.
- Evidence: Table V (45 runs per method): FedFACS sends the model to all 100 candidates and trains them, 10.0 times the local steps of random sampling; its uploads to the target are 6.2% fewer (520 against 555) and its total volume to the target is 198 against 37 GB.
- Declaration: Uploads, downloads and local computation are measured for every method, and the saving of FedFACS is stated for the uploaded updates.

**R1-09 and R2-15: what the Jain index measures**

- Fix: Eq. (24) is read as the equality of the quality-adjusted participation, and with q equal to one as the equality of participation. The interpretation of 0.5 as a boundary is replaced by the minimum 1/N and an example. The percentage of never-selected clients is reported next to the index.
- Where: Section 5.1, Eqs. (24)-(25); Section 5.4, Table V (columns JFI and Never).
- Evidence: Table V: JFI with q equal to one is 0.997 for FedFACS and 0.920 for random sampling; no FedFACS client is left unselected, while DivFL leaves 47.4% unselected. Example: 90 of 100 clients served uniformly give 0.9.
- Declaration: The index is interpreted correctly, and its value is accompanied by the share of clients that are never served.


# 2. Edits: before and after, with locations


::: {custom-style="BA-Edit"}
Edit 1: Performance metrics: round-to-target
:::

::: {custom-style="BA-Loc"}
Location: Section 5.1, performance metrics (original line 504)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

*Round-to-accuracy*: defines the [training iteration count required to]{custom-style="Del"} reach [a specified accuracy. This metric provides an assessment of the convergence efficiency of the client selection strategy and the communication cost associated with achieving the desired performance, where fewer communication]{custom-style="Del"} rounds indicate faster [convergence and lower communication requirements.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

*Round-to-accuracy*: defines the [first completed round at which the validation accuracy reaches the target; a run that does not]{custom-style="Add"} reach [it is recorded as not reached. Fewer]{custom-style="Add"} rounds indicate faster [convergence.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Edit 2: Performance metrics: uploads and total communication, Eqs. (23) and (23a)
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

[The total communication in bytes is]{custom-style="Add"}

::: {custom-style="AddBlock"}
$$ \mathrm{Comm}_{\mathrm{total}}(T)=\sum_{t=1}^{T}\left(\mathrm{Comm}^t_{\mathrm{down}}+\mathrm{Comm}^t_{\mathrm{up}}+\mathrm{Comm}^t_{\mathrm{aux}}\right) \qquad (23a) $$
:::

[where $\mathrm{Comm}^t_{\mathrm{down}}$, $\mathrm{Comm}^t_{\mathrm{up}}$ and $\mathrm{Comm}^t_{\mathrm{aux}}$ are]{custom-style="Add"} the [bytes of]{custom-style="Add"} the [models sent, the updates uploaded and the control messages in round $t$.]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Edit 3: Performance metrics: reading of Jain's index, Eqs. (24)-(25)
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

For client $i$, $p_i$ reflects its rate of participation in model aggregation, while [$n$]{custom-style="Del"} denotes the overall client population, and $q_i$ represents the quality of its locally stored dataset (Shi et al. 2023). [When $JFI = 1$, it refers]{custom-style="Del"} to equal participation for [all clients, when]{custom-style="Del"} the [values in]{custom-style="Del"} the [range $0.5 \leq JFI < 1$ indicate that all clients participates with different times, and values below $0.5$ represent the unfair participation.]{custom-style="Del"}

::: {custom-style="BA-Label-After"}
After (put instead)
:::

*Jain’s Fairness Index (JFI)*: quantifies [the]{custom-style="Add"} fairness [of participation on]{custom-style="Add"} the [quality-adjusted participation $p_i/q_i$]{custom-style="Add"} (Shi et al. 2024; Cho et al. 2020).

::: {custom-style="AddBlock"}
$$ JFI = \frac{\left(\sum_{i=1}^{N} \frac{p_i}{q_i}\right)^2}
{N \cdot \sum_{i=1}^{N} \left(\frac{p_i}{q_i}\right)^2} \qquad (24) $$
:::

$$ q_i = (\text{number of labels}) \times (1 - \text{percentage of noisy data}) \qquad (25) $$

For client $i$, $p_i$ reflects its rate of participation in model aggregation, while [$N$]{custom-style="Add"} denotes the overall client population, and $q_i$ represents the quality of its locally stored dataset (Shi et al. 2023). [Therefore $JFI = 1$ means participation proportional]{custom-style="Add"} to [quality, and]{custom-style="Add"} equal participation for [$q_i=1$;]{custom-style="Add"} the [minimum value is $1/N$. The percentage of clients that are never selected is reported with]{custom-style="Add"} the [index (Table V).]{custom-style="Add"}


::: {custom-style="BA-Edit"}
Edit 4: range of the fairness term of Eq. (6)
:::

::: {custom-style="BA-Loc"}
Location: Section 4.2, directly after Eq. (6) (original line 365)
:::

::: {custom-style="BA-Label-Before"}
Before (remove)
:::

No statement of the range of $F_i^t$.

::: {custom-style="BA-Label-After"}
After (put instead)
:::

[Since $0\le r_i^t\le N\,\overline{r^t}$, the fairness term satisfies $1\le F_i^t < N+1$.]{custom-style="Add"}

::: {custom-style="BA-Note"}
Declaration: no new symbol. The bound follows from $\sum_j r_j^t=N\,\overline{r^t}$ and $F_i^t=1+r_i^t/(1+\overline{r^t})$; it is Proposition 1 (ii) of Section 4.3, with its proof, and a unit test checks it.
:::


# 3. New text and table for Section 5.4

**Communication and participation.** Table V gives the terms of Eq. (23a): Down and Up are the models sent and the updates uploaded per round (times the model size of 33.6 MB), and Total GB is their sum over 100 rounds. FedFACS sends the model to all $N=100$ candidates and uploads 520 updates to the target against 555 for random sampling (6.2% fewer), at 198 against 37 GB.

Table V. Methods under one communication model (45 runs each; 100 rounds; $N=100$). Steps: local SGD steps per round. Scoring: forward passes per round (thousands) that give $\Delta KL_i^t$ and $\sigma_i^2$ of the fitness score, Eq. (14) (Eqs. (5) and (12)); for Power-of-Choice and DivFL, the forward passes of their selection. To target: $C_{\mathrm{total}}$ and $\mathrm{Comm}_{\mathrm{total}}$ at the first round that reaches the common target accuracy. JFI: Eq. (24) with $q_i=1$. Never: percentage of clients with $p_i=0$.

| Method | Down | Up | Steps | Scoring | Total GB | Uploads to target | GB to target | JFI | Never (%) |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Random sampling (FedAvg) | 10.0 | 10.00 | 268 | 0.0 | 67.2 | 555 | 37.3 | 0.920 | 0.0 |
| Power-of-Choice | 20.0 | 10.00 | 313 | 5.1 | 100.8 | 528 | 53.2 | 0.727 | 4.4 |
| Oort | 10.0 | 10.00 | 291 | 0.0 | 67.2 | 488 | 32.8 | 0.493 | 0.0 |
| DivFL | 100.0 | 10.00 | 285 | 25.6 | 369.8 | 668 | 247.1 | 0.203 | 47.4 |
| FedFACS ($\kappa=0$) | 100.0 | 9.71 | 2680 | 51.2 | 368.6 | 520 | 198.3 | 0.997 | 0.0 |


# 3a. How each number of Table V follows from Eq. (23a)

Reading guide (explanatory, not for the manuscript). Model size: 33.6 MB (trainable weights). Down, Up and the volumes are averages over the 45 runs of each method; the values of each row follow from the previous rows up to the averaging over runs.

| Quantity | Equation term | Column of Table V | FedFACS | Random sampling |
|:--|--:|--:|--:|--:|
| Models sent per round | $\mathrm{Comm}^t_{\mathrm{down}}$ divided by the model size | Down | 100.0 | 10.0 |
| Updates uploaded per round | $\mathrm{Comm}^t_{\mathrm{up}}$ divided by the model size | Up | 9.71 | 10.00 |
| Volume per round (GB) | $\mathrm{Comm}^t_{\mathrm{down}}+\mathrm{Comm}^t_{\mathrm{up}}$ (the term $\mathrm{Comm}^t_{\mathrm{aux}}$ is below 0.1% of it) | none | 3.69 | 0.67 |
| Volume after 100 rounds (GB) | $\mathrm{Comm}_{\mathrm{total}}(100)$, sum over $t=1,\dots,100$ | Total GB | 368.6 | 67.2 |
| Uploads to the target | $C_{\mathrm{total}}$ of Eq. (23) at the first round that reaches the target | Uploads to target | 520 | 555 |
| Volume to the target (GB) | $\mathrm{Comm}_{\mathrm{total}}$ of Eq. (23a) at that round | GB to target | 198.3 | 37.3 |
| Saving in uploads | $1-C_{\mathrm{total}}^{\mathrm{FedFACS}}/C_{\mathrm{total}}^{\mathrm{random}}$ | none | 6.2% | none |


# 4. Notation declared

| Symbol | Declaration |
|:--|:--|
| $\mathrm{Comm}_{\mathrm{total}}(T)$ (23a) | NEW: total communication in bytes over the first $T$ rounds |
| $\mathrm{Comm}^t_{\mathrm{down}}$ (23a) | NEW: volume in bytes of the models sent to the clients in round $t$ |
| $\mathrm{Comm}^t_{\mathrm{up}}$ (23a) | NEW: volume in bytes of the updates uploaded by the selected clients in round $t$ |
| $\mathrm{Comm}^t_{\mathrm{aux}}$ (23a) | NEW: volume in bytes of the scores and control messages in round $t$ |
| $C_{\mathrm{total}}$ (23) | CHANGED: sum of the cohort sizes $\lvert C_k^t\rvert$ over the first $T$ rounds (uploaded updates) |
| $N$ | CHANGED: client population; replaces $n$ of the original |
| $p_i$, $q_i$ (24), (25) | previously declared: participation rate and data quality of client $i$; $q_i=1$ gives the equality of participation |


# 5. Notes for the authors (internal, not for the manuscript)

- **Model size.** The volumes count the trainable weights of the model (33.6 MB per model); the frozen layers are assumed present at the clients. The ratios between the methods do not depend on this size. The authors confirm whether the frozen weights count.
- **Baselines.** Power-of-Choice, Oort and DivFL are our implementations of the published descriptions, run in the same simulation; the Methods section must say so.
- **Wording.** "Communication-efficient" in the title and the abstract refers to the uploaded updates (Replacement 11).
- **Scenario 4.** The reproduction contains Scenarios 1 to 3 only.