::: {custom-style="R-Title"}
FedFACS: Experimental Results Report (all stages, all seeds)
:::

::: {custom-style="R-Sub"}
Every number below is computed from the saved run files; no experiment is run while this report is built.
:::

# 1. Headline findings

Totals: **621 completed runs** (5 seeds for the main comparison). Paired comparisons use the same seed, partition and initialisation; intervals are 95% bootstrap intervals over paired runs.

1. **Participation fairness is the clear strength.** FedFACS Jain index 0.995 against 0.920 (FedAvg), 0.727 (Pow-D), 0.493 (Oort-style) and 0.203 (DivFL-style). Maximum wait 12.1 rounds against 60.6 (FedAvg) and 100.0 (DivFL-style). Clients never selected: FedFACS 0.0%, DivFL-style 47.4%, Pow-D 4.4%.
2. **Checkpoint accuracy:** FedFACS is not different from FedAvg: -0.16 [-0.42, +0.11] points (n=45).
3. **Last-10-round accuracy:** FedFACS is below FedAvg: -3.14 [-4.27, -2.11] points; late-round swing 5.64 against 2.00 points.
4. **Worst-10% client accuracy:** FedFACS is below FedAvg: -4.36 [-7.97, -1.05] points.
5. **Cost.** FedFACS downloads 336.0 GB per run against 33.6 GB for FedAvg and performs 0.27 M training steps against 0.03 M (every candidate trains every round).
6. **Sample-weighted variant (A2), held-out runs (n=39):** A2 minus full FedFACS: checkpoint accuracy +0.08 [-0.27, +0.41], last-10-round accuracy +2.99 [+1.88, +4.20], late-round swing -3.54 [-5.01, -2.20] points (a negative swing means steadier). A2 is above full FedFACS on last-10-round accuracy. Details in Section 6.

# 2. Experimental procedure (steps)

1. **Data.** MNIST, Fashion-MNIST and CIFAR-10 (public). COVID-19 Radiography was not included (it requires a Kaggle login). Native resolution, grayscale replicated to 3 channels, ImageNet mean/std normalisation.
2. **Model.** ImageNet-pretrained ResNet-18. Convolution 1 and layers 1-3 are frozen and run once in evaluation mode, so their 256x2x2 output is cached; layer 4 and a new 10-way fully connected layer are trained. BatchNorm statistics are frozen (evaluation mode). Layer 4 is computed by an exactly equivalent matrix-multiply form (outputs agree with torchvision to 3e-6, gradients to 1e-6; tested).
3. **Splits.** 5,000 training images form a server validation set; the rest are partitioned over N = 100 clients; each client keeps 20% as a held-out local test set (used only for client-level accuracy). The official test set is used only for reporting.
4. **Partitions.** Dirichlet label skew with alpha = 0.1 and 0.5 (minimum 30 samples per client), two classes per client, and for the noise test an IID split with per-client label noise drawn from U(0, 0.45).
5. **Local training.** 100 rounds, 2 local epochs, batch size 32, plain SGD (learning rate 0.05 for CIFAR-10, 0.01 for MNIST/FMNIST), gradient-norm clipping at 50 (applied to every method; it acts on about 0.09% of steps and was added after one client diverged to NaN at the CIFAR-10 learning rate). A non-finite client update is excluded as a failed upload and a non-finite round is cancelled without committing; no run needed either.
6. **Baselines (ten clients per round).** FedAvg (uniform sampling, sample-count weights); FedProx (mu = 0.1); FedNova (normalised averaging); a q-FFL-style loss-weighted average (q = 1; a simplified form, not the original q-FFL); Pow-D (d = 20, highest local loss); a DivFL-style selector (greedy facility location over last-layer gradients of all clients; not the original implementation); an Oort-style selector (statistical utility with exploration, no system-speed term); FairFedCS (Shi et al., ICME 2023: Beta reputation, virtual queues, CSI = 0.6 r + Q; leave-one-out contributions replace GTG-Shapley); Greedy (highest reputation). Zhai et al. and AHIBCS were not reproduced (full texts not accessible).
7. **FedFACS (corrected specification).** All 100 candidates download and train each round; fitness = a*DeltaKL + (1-a)*F - mu*variance with a updated by the bounded feedback rule (beta = 0.9, lambda = 1, a0 = 0.5, mu = 1), F = 1 + r/(1 + mean r), four scoring batches over up to 256 local examples, cohort size from the previous validation-loss reduction within [5, 10], causal reference (beta_ref = 0.9), nonnegative stability weights with a sample-count fallback.
8. **Ablations (FMNIST and CIFAR-10, Dirichlet 0.5, 3 seeds).** A1, A2, fixed mixing, no fairness term, no variance penalty, loss as utility, random scores, rescaled utility.
9. **Diagnostics.** At rounds 1, 5, 10, 25, 50 and 100 (rounds 5, 25, 50 in the noise test) each candidate's update is added alone with weight 1/m to the global model and the change in validation loss is recorded (the marginal gain); the Spearman correlation between each score and this gain is computed per round and run. In the noise test, detection AUC uses clients with more than 22.5% label noise as the positive class.
10. **Sensitivity and scale.** One-factor changes of B, mu, beta, lambda and C_min on FMNIST (3 seeds); N = 50, 100, 200, 400 clients with FedFACS and FedAvg (3 seeds).
11. **Endpoints.** Accuracy at the round of best validation accuracy (checkpoint endpoint) and mean test accuracy over the last 10 rounds. Round-to-target is the first round whose validation accuracy reaches 97% of the mean best validation accuracy of FedAvg in the same dataset and partition (a common target; runs that never reach it are reported as not reached).
12. **Fairness measures.** Jain index of raw selection counts (no injected noise, so quality adjustment is neutral except in the noise test), share of clients never selected, maximum number of consecutive rounds any client waited, and client-level accuracy (mean, standard deviation, 10th percentile of the final global model on each client's held-out data).
13. **Cost accounting.** Every download, upload and auxiliary message is counted in bytes (model size 33.6 MB), plus training steps.
14. **Statistics.** Mean and standard deviation over seeds; paired differences with 95% bootstrap intervals (10,000 resamples) over paired runs; Spearman correlations and rank-based AUC for the diagnostics.
15. **Hardware and deviations from the original paper.** One NVIDIA RTX 5060 Ti shared with desktop applications; CUDA-graph training steps. Compared with the original paper: 2 local epochs instead of 10, 100 rounds instead of 200, features cached, no COVID-19, different baseline implementations, and a corrected FedFACS specification, so these results are not a replication of the original tables.

# 3. Main comparison (mean ± std over seeds)

Columns: checkpoint accuracy (%), accuracy averaged over the last 10 rounds (%), rounds to target (runs reaching it), Jain index, clients never selected (%), maximum wait (rounds), download (GB), training steps (millions), worst-10% client accuracy (%), macro-F1 (%).

## 3.1 FMNIST

| Partition          | Method                      |   Seeds | Acc ckpt     | Acc last10   | Rounds to target   | Jain          | Never %     | Max wait   | Down GB     | Steps M     | Worst-10% client   | Macro-F1      |
|:-------------------|:----------------------------|--------:|:-------------|:-------------|:-------------------|:--------------|:------------|:-----------|:------------|:------------|:-------------------|:--------------|
| Dirichlet 0.1      | FedAvg (random)             |       5 | 81.38 ± 0.70 | 77.79 ± 1.23 | 59 ± 8 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 57.22 ± 5.73       | 77.61 ± 2.63  |
| Dirichlet 0.1      | FedProx                     |       5 | 81.34 ± 0.61 | 77.87 ± 1.18 | 60 ± 6 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 57.26 ± 5.73       | 77.64 ± 2.58  |
| Dirichlet 0.1      | FedNova                     |       5 | 82.06 ± 0.65 | 79.28 ± 0.56 | 49 ± 5 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 59.17 ± 7.82       | 79.13 ± 3.11  |
| Dirichlet 0.1      | q-FFL-style                 |       5 | 82.18 ± 0.99 | 79.33 ± 0.60 | 42 ± 7 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 60.98 ± 3.54       | 79.89 ± 2.56  |
| Dirichlet 0.1      | Pow-D                       |       5 | 81.26 ± 0.70 | 77.01 ± 1.19 | 53 ± 8 (5/5)       | 0.592 ± 0.037 | 8.0 ± 2.6   | 100 ± 0    | 67.2 ± 0.0  | 0.04 ± 0.00 | 51.05 ± 5.81       | 77.25 ± 0.78  |
| Dirichlet 0.1      | Oort-style                  |       5 | 82.55 ± 0.87 | 78.58 ± 2.44 | 45 ± 10 (5/5)      | 0.284 ± 0.017 | 0.2 ± 0.4   | 96 ± 3     | 33.6 ± 0.0  | 0.03 ± 0.00 | 60.12 ± 6.29       | 78.87 ± 3.22  |
| Dirichlet 0.1      | DivFL-style                 |       5 | 79.07 ± 0.47 | 77.30 ± 0.70 | 83 ± 11 (4/5)      | 0.203 ± 0.056 | 48.6 ± 8.2  | 100 ± 0    | 336.0 ± 0.0 | 0.03 ± 0.00 | 55.33 ± 8.08       | 75.87 ± 2.41  |
| Dirichlet 0.1      | FairFedCS                   |       5 | 81.67 ± 0.77 | 78.46 ± 1.65 | 52 ± 6 (5/5)       | 0.876 ± 0.026 | 0.0 ± 0.0   | 40 ± 2     | 33.6 ± 0.0  | 0.03 ± 0.00 | 56.63 ± 6.43       | 77.68 ± 2.49  |
| Dirichlet 0.1      | Greedy (reputation)         |       5 | 76.04 ± 7.25 | 75.27 ± 7.07 | 63 ± 31 (3/5)      | 0.117 ± 0.009 | 66.4 ± 11.5 | 100 ± 0    | 33.6 ± 0.0  | 0.03 ± 0.01 | 51.53 ± 17.15      | 73.06 ± 10.70 |
| Dirichlet 0.1      | FedFACS (full)              |       5 | 81.04 ± 0.60 | 76.89 ± 0.29 | 61 ± 5 (5/5)       | 0.996 ± 0.001 | 0.0 ± 0.0   | 12 ± 0     | 336.0 ± 0.0 | 0.28 ± 0.00 | 49.05 ± 11.41      | 74.69 ± 4.26  |
| Dirichlet 0.1      | FedFACS-A2 (sample weights) |       5 | 80.96 ± 1.11 | 77.34 ± 0.43 | 58 ± 12 (5/5)      | 0.995 ± 0.000 | 0.0 ± 0.0   | 13 ± 1     | 336.0 ± 0.0 | 0.28 ± 0.00 | 54.68 ± 11.14      | 77.76 ± 3.02  |
| Dirichlet 0.5      | FedAvg (random)             |       5 | 85.33 ± 0.18 | 84.20 ± 0.51 | 45 ± 5 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 74.64 ± 3.03       | 83.91 ± 0.82  |
| Dirichlet 0.5      | FedProx                     |       5 | 85.27 ± 0.20 | 84.19 ± 0.50 | 45 ± 5 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 74.64 ± 2.88       | 83.88 ± 0.81  |
| Dirichlet 0.5      | FedNova                     |       5 | 85.47 ± 0.30 | 84.38 ± 0.53 | 45 ± 7 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 75.44 ± 2.37       | 84.14 ± 0.78  |
| Dirichlet 0.5      | q-FFL-style                 |       5 | 85.69 ± 0.21 | 84.56 ± 0.50 | 41 ± 5 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 76.42 ± 2.10       | 84.49 ± 0.98  |
| Dirichlet 0.5      | Pow-D                       |       5 | 85.37 ± 0.62 | 83.79 ± 0.77 | 44 ± 5 (5/5)       | 0.659 ± 0.016 | 7.4 ± 2.1   | 100 ± 0    | 67.2 ± 0.0  | 0.03 ± 0.00 | 72.87 ± 2.71       | 82.68 ± 1.29  |
| Dirichlet 0.5      | Oort-style                  |       5 | 85.54 ± 0.27 | 84.39 ± 0.48 | 48 ± 8 (5/5)       | 0.371 ± 0.026 | 0.0 ± 0.0   | 87 ± 6     | 33.6 ± 0.0  | 0.03 ± 0.00 | 75.96 ± 4.41       | 84.32 ± 2.59  |
| Dirichlet 0.5      | DivFL-style                 |       5 | 84.37 ± 0.30 | 83.84 ± 0.53 | 56 ± 13 (5/5)      | 0.198 ± 0.032 | 46.2 ± 6.8  | 100 ± 0    | 336.0 ± 0.0 | 0.03 ± 0.00 | 74.73 ± 0.87       | 83.76 ± 0.25  |
| Dirichlet 0.5      | FairFedCS                   |       5 | 85.42 ± 0.31 | 84.59 ± 0.34 | 40 ± 2 (5/5)       | 0.856 ± 0.022 | 0.0 ± 0.0   | 40 ± 1     | 33.6 ± 0.0  | 0.03 ± 0.00 | 76.65 ± 0.95       | 84.83 ± 0.45  |
| Dirichlet 0.5      | Greedy (reputation)         |       5 | 82.49 ± 0.84 | 82.41 ± 0.88 | 57 ± 13 (3/5)      | 0.113 ± 0.004 | 70.8 ± 9.4  | 100 ± 0    | 33.6 ± 0.0  | 0.03 ± 0.00 | 73.65 ± 1.92       | 82.38 ± 0.84  |
| Dirichlet 0.5      | FedFACS (full)              |       5 | 84.93 ± 0.34 | 81.87 ± 1.72 | 56 ± 13 (5/5)      | 0.996 ± 0.002 | 0.0 ± 0.0   | 11 ± 1     | 336.0 ± 0.0 | 0.28 ± 0.00 | 74.49 ± 1.21       | 83.61 ± 0.83  |
| Dirichlet 0.5      | FedFACS-A2 (sample weights) |       5 | 85.38 ± 0.48 | 84.46 ± 0.42 | 46 ± 5 (5/5)       | 0.998 ± 0.001 | 0.0 ± 0.0   | 11 ± 1     | 336.0 ± 0.0 | 0.28 ± 0.00 | 77.44 ± 2.19       | 84.60 ± 1.23  |
| Two classes/client | FedAvg (random)             |       5 | 81.04 ± 0.67 | 77.65 ± 0.85 | 63 ± 11 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 58.16 ± 12.77      | 76.15 ± 5.70  |
| Two classes/client | FedProx                     |       5 | 81.01 ± 0.63 | 77.66 ± 0.83 | 63 ± 11 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 58.41 ± 12.61      | 76.23 ± 5.62  |
| Two classes/client | FedNova                     |       5 | 81.02 ± 0.63 | 77.31 ± 0.54 | 60 ± 7 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 59.31 ± 12.02      | 76.46 ± 5.36  |
| Two classes/client | q-FFL-style                 |       5 | 81.84 ± 0.46 | 76.33 ± 1.50 | 60 ± 7 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 54.60 ± 12.64      | 74.98 ± 5.90  |
| Two classes/client | Pow-D                       |       5 | 80.85 ± 0.72 | 77.71 ± 1.69 | 62 ± 14 (5/5)      | 0.765 ± 0.025 | 1.4 ± 1.1   | 99 ± 2     | 67.2 ± 0.0  | 0.03 ± 0.00 | 63.04 ± 7.63       | 78.73 ± 2.64  |
| Two classes/client | Oort-style                  |       5 | 79.87 ± 1.61 | 74.80 ± 2.52 | 64 ± 4 (4/5)       | 0.290 ± 0.024 | 0.0 ± 0.0   | 91 ± 5     | 33.6 ± 0.0  | 0.03 ± 0.00 | 61.71 ± 6.86       | 76.97 ± 3.86  |
| Two classes/client | DivFL-style                 |       5 | 77.27 ± 1.35 | 75.98 ± 1.25 | 100 ± 1 (2/5)      | 0.206 ± 0.035 | 51.6 ± 6.9  | 100 ± 0    | 336.0 ± 0.0 | 0.03 ± 0.00 | 62.33 ± 3.83       | 76.49 ± 1.97  |
| Two classes/client | FairFedCS                   |       5 | 80.81 ± 0.70 | 78.24 ± 0.60 | 54 ± 11 (5/5)      | 0.854 ± 0.018 | 0.0 ± 0.0   | 39 ± 1     | 33.6 ± 0.0  | 0.03 ± 0.00 | 62.87 ± 1.02       | 78.62 ± 1.81  |
| Two classes/client | Greedy (reputation)         |       5 | 75.19 ± 4.27 | 73.64 ± 4.25 | 46 (1/5)           | 0.115 ± 0.011 | 62.0 ± 19.0 | 100 ± 0    | 33.6 ± 0.0  | 0.03 ± 0.00 | 48.69 ± 12.64      | 72.50 ± 5.07  |
| Two classes/client | FedFACS (full)              |       5 | 81.36 ± 0.49 | 75.16 ± 2.86 | 52 ± 8 (5/5)       | 0.997 ± 0.000 | 0.0 ± 0.0   | 11 ± 1     | 336.0 ± 0.0 | 0.29 ± 0.00 | 56.63 ± 10.60      | 75.61 ± 4.84  |
| Two classes/client | FedFACS-A2 (sample weights) |       5 | 80.69 ± 0.55 | 76.80 ± 1.06 | 54 ± 7 (5/5)       | 0.997 ± 0.001 | 0.0 ± 0.0   | 12 ± 1     | 336.0 ± 0.0 | 0.29 ± 0.00 | 52.19 ± 12.87      | 74.02 ± 5.24  |

## 3.2 MNIST

| Partition          | Method                      |   Seeds | Acc ckpt     | Acc last10   | Rounds to target   | Jain          | Never %    | Max wait   | Down GB     | Steps M     | Worst-10% client   | Macro-F1      |
|:-------------------|:----------------------------|--------:|:-------------|:-------------|:-------------------|:--------------|:-----------|:-----------|:------------|:------------|:-------------------|:--------------|
| Dirichlet 0.1      | FedAvg (random)             |       5 | 93.97 ± 0.65 | 92.11 ± 0.39 | 55 ± 7 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 82.57 ± 1.53       | 91.95 ± 0.57  |
| Dirichlet 0.1      | FedProx                     |       5 | 93.98 ± 0.61 | 92.14 ± 0.38 | 55 ± 7 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 82.91 ± 1.73       | 91.91 ± 0.60  |
| Dirichlet 0.1      | FedNova                     |       5 | 94.94 ± 0.26 | 92.91 ± 0.74 | 48 ± 5 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 85.61 ± 2.20       | 93.04 ± 0.62  |
| Dirichlet 0.1      | q-FFL-style                 |       5 | 94.76 ± 0.48 | 92.99 ± 0.57 | 38 ± 2 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 86.74 ± 1.97       | 93.31 ± 1.28  |
| Dirichlet 0.1      | Pow-D                       |       5 | 94.70 ± 0.36 | 93.19 ± 0.81 | 44 ± 8 (5/5)       | 0.584 ± 0.035 | 10.6 ± 3.4 | 100 ± 0    | 67.2 ± 0.0  | 0.04 ± 0.00 | 79.56 ± 16.99      | 91.69 ± 5.73  |
| Dirichlet 0.1      | Oort-style                  |       5 | 95.19 ± 0.22 | 94.37 ± 0.36 | 39 ± 4 (5/5)       | 0.418 ± 0.035 | 0.0 ± 0.0  | 85 ± 4     | 33.6 ± 0.0  | 0.03 ± 0.00 | 88.46 ± 2.22       | 94.49 ± 0.55  |
| Dirichlet 0.1      | DivFL-style                 |       5 | 92.61 ± 0.74 | 91.94 ± 0.74 | 70 ± 14 (5/5)      | 0.219 ± 0.025 | 43.0 ± 7.8 | 100 ± 0    | 336.0 ± 0.0 | 0.04 ± 0.00 | 81.78 ± 4.77       | 91.61 ± 1.03  |
| Dirichlet 0.1      | FairFedCS                   |       5 | 94.37 ± 0.49 | 92.75 ± 0.53 | 52 ± 11 (5/5)      | 0.885 ± 0.015 | 0.0 ± 0.0  | 41 ± 3     | 33.6 ± 0.0  | 0.03 ± 0.00 | 84.01 ± 3.42       | 93.00 ± 0.56  |
| Dirichlet 0.1      | Greedy (reputation)         |       5 | 91.29 ± 1.59 | 90.81 ± 1.63 | 64 ± 5 (2/5)       | 0.115 ± 0.009 | 68.0 ± 7.7 | 100 ± 0    | 33.6 ± 0.0  | 0.03 ± 0.01 | 81.37 ± 4.87       | 90.94 ± 1.83  |
| Dirichlet 0.1      | FedFACS (full)              |       5 | 93.70 ± 0.76 | 87.91 ± 2.80 | 67 ± 10 (5/5)      | 0.995 ± 0.002 | 0.0 ± 0.0  | 13 ± 2     | 336.0 ± 0.0 | 0.29 ± 0.00 | 76.41 ± 13.05      | 89.85 ± 4.18  |
| Dirichlet 0.1      | FedFACS-A2 (sample weights) |       5 | 94.15 ± 0.19 | 92.25 ± 0.54 | 58 ± 3 (5/5)       | 0.997 ± 0.000 | 0.0 ± 0.0  | 12 ± 1     | 336.0 ± 0.0 | 0.29 ± 0.00 | 82.21 ± 2.25       | 91.86 ± 0.74  |
| Dirichlet 0.5      | FedAvg (random)             |       5 | 96.26 ± 0.19 | 95.95 ± 0.16 | 30 ± 3 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 92.71 ± 1.13       | 96.06 ± 0.22  |
| Dirichlet 0.5      | FedProx                     |       5 | 96.15 ± 0.16 | 95.93 ± 0.17 | 29 ± 4 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 92.62 ± 1.16       | 96.08 ± 0.27  |
| Dirichlet 0.5      | FedNova                     |       5 | 96.30 ± 0.24 | 96.05 ± 0.16 | 29 ± 2 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 93.00 ± 1.11       | 96.17 ± 0.29  |
| Dirichlet 0.5      | q-FFL-style                 |       5 | 96.39 ± 0.20 | 96.02 ± 0.24 | 28 ± 4 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 92.18 ± 1.81       | 95.71 ± 1.14  |
| Dirichlet 0.5      | Pow-D                       |       5 | 96.49 ± 0.07 | 96.22 ± 0.14 | 28 ± 3 (5/5)       | 0.697 ± 0.028 | 6.8 ± 3.3  | 100 ± 0    | 67.2 ± 0.0  | 0.03 ± 0.00 | 93.70 ± 0.71       | 96.42 ± 0.12  |
| Dirichlet 0.5      | Oort-style                  |       5 | 96.65 ± 0.09 | 96.39 ± 0.12 | 29 ± 2 (5/5)       | 0.580 ± 0.047 | 0.0 ± 0.0  | 78 ± 6     | 33.6 ± 0.0  | 0.03 ± 0.00 | 93.50 ± 0.34       | 96.44 ± 0.17  |
| Dirichlet 0.5      | DivFL-style                 |       5 | 95.73 ± 0.21 | 95.48 ± 0.28 | 36 ± 8 (5/5)       | 0.242 ± 0.035 | 37.2 ± 7.9 | 100 ± 0    | 336.0 ± 0.0 | 0.03 ± 0.00 | 92.53 ± 0.86       | 95.63 ± 0.32  |
| Dirichlet 0.5      | FairFedCS                   |       5 | 96.43 ± 0.22 | 96.02 ± 0.20 | 29 ± 6 (5/5)       | 0.868 ± 0.012 | 0.0 ± 0.0  | 40 ± 1     | 33.6 ± 0.0  | 0.03 ± 0.00 | 91.51 ± 3.20       | 95.50 ± 1.51  |
| Dirichlet 0.5      | Greedy (reputation)         |       5 | 95.38 ± 0.33 | 95.35 ± 0.29 | 33 ± 9 (5/5)       | 0.112 ± 0.009 | 75.6 ± 7.8 | 100 ± 0    | 33.6 ± 0.0  | 0.03 ± 0.00 | 92.13 ± 0.43       | 95.28 ± 0.29  |
| Dirichlet 0.5      | FedFACS (full)              |       5 | 95.68 ± 0.21 | 86.37 ± 3.75 | 38 ± 7 (5/5)       | 0.986 ± 0.010 | 0.0 ± 0.0  | 16 ± 1     | 336.0 ± 0.0 | 0.28 ± 0.00 | 82.72 ± 16.15      | 90.19 ± 9.76  |
| Dirichlet 0.5      | FedFACS-A2 (sample weights) |       5 | 96.26 ± 0.23 | 95.97 ± 0.06 | 31 ± 3 (5/5)       | 0.997 ± 0.000 | 0.0 ± 0.0  | 11 ± 0     | 336.0 ± 0.0 | 0.28 ± 0.00 | 93.18 ± 0.56       | 96.18 ± 0.25  |
| Two classes/client | FedAvg (random)             |       5 | 93.75 ± 0.17 | 92.51 ± 0.52 | 56 ± 7 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 84.36 ± 3.13       | 92.65 ± 0.71  |
| Two classes/client | FedProx                     |       5 | 93.83 ± 0.25 | 92.52 ± 0.53 | 58 ± 6 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 84.49 ± 3.28       | 92.63 ± 0.72  |
| Two classes/client | FedNova                     |       5 | 93.84 ± 0.26 | 92.46 ± 0.47 | 58 ± 6 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 84.36 ± 3.60       | 92.62 ± 0.98  |
| Two classes/client | q-FFL-style                 |       5 | 94.26 ± 0.34 | 92.02 ± 1.60 | 46 ± 3 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0  | 61 ± 12    | 33.6 ± 0.0  | 0.03 ± 0.00 | 81.25 ± 10.93      | 91.52 ± 2.89  |
| Two classes/client | Pow-D                       |       5 | 94.18 ± 0.31 | 93.18 ± 0.37 | 45 ± 6 (5/5)       | 0.802 ± 0.030 | 1.8 ± 2.2  | 99 ± 1     | 67.2 ± 0.0  | 0.03 ± 0.00 | 85.19 ± 6.62       | 92.91 ± 1.79  |
| Two classes/client | Oort-style                  |       5 | 94.66 ± 0.25 | 93.37 ± 1.11 | 39 ± 5 (5/5)       | 0.438 ± 0.066 | 0.0 ± 0.0  | 81 ± 6     | 33.6 ± 0.0  | 0.03 ± 0.00 | 87.06 ± 4.80       | 93.25 ± 2.04  |
| Two classes/client | DivFL-style                 |       5 | 91.38 ± 1.63 | 90.56 ± 1.85 | 77 ± 6 (3/5)       | 0.214 ± 0.009 | 43.6 ± 2.6 | 100 ± 0    | 336.0 ± 0.0 | 0.03 ± 0.00 | 82.84 ± 3.92       | 90.56 ± 2.06  |
| Two classes/client | FairFedCS                   |       5 | 94.18 ± 0.40 | 92.87 ± 0.75 | 54 ± 6 (5/5)       | 0.857 ± 0.013 | 0.0 ± 0.0  | 38 ± 1     | 33.6 ± 0.0  | 0.03 ± 0.00 | 86.06 ± 2.14       | 92.76 ± 0.77  |
| Two classes/client | Greedy (reputation)         |       5 | 87.83 ± 7.14 | 87.36 ± 7.22 | 85 ± 11 (3/5)      | 0.117 ± 0.003 | 62.2 ± 6.6 | 100 ± 0    | 33.6 ± 0.0  | 0.03 ± 0.00 | 72.59 ± 21.68      | 86.16 ± 10.40 |
| Two classes/client | FedFACS (full)              |       5 | 93.59 ± 0.31 | 88.68 ± 3.22 | 59 ± 10 (5/5)      | 0.997 ± 0.000 | 0.0 ± 0.0  | 12 ± 1     | 336.0 ± 0.0 | 0.28 ± 0.00 | 81.35 ± 6.03       | 91.01 ± 2.60  |
| Two classes/client | FedFACS-A2 (sample weights) |       5 | 93.83 ± 0.25 | 92.54 ± 0.73 | 51 ± 3 (5/5)       | 0.997 ± 0.000 | 0.0 ± 0.0  | 11 ± 0     | 336.0 ± 0.0 | 0.28 ± 0.00 | 84.27 ± 1.47       | 92.81 ± 0.56  |

## 3.3 CIFAR-10

| Partition          | Method                      |   Seeds | Acc ckpt     | Acc last10   | Rounds to target   | Jain          | Never %     | Max wait   | Down GB     | Steps M     | Worst-10% client   | Macro-F1      |
|:-------------------|:----------------------------|--------:|:-------------|:-------------|:-------------------|:--------------|:------------|:-----------|:------------|:------------|:-------------------|:--------------|
| Dirichlet 0.1      | FedAvg (random)             |       5 | 66.31 ± 1.07 | 62.03 ± 1.08 | 63 ± 5 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 43.64 ± 8.57       | 61.90 ± 4.06  |
| Dirichlet 0.1      | FedProx                     |       5 | 66.81 ± 0.88 | 62.87 ± 1.23 | 64 ± 4 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 44.35 ± 6.57       | 62.52 ± 2.81  |
| Dirichlet 0.1      | FedNova                     |       5 | 67.27 ± 0.76 | 63.25 ± 0.61 | 55 ± 19 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 41.80 ± 10.51      | 61.56 ± 4.68  |
| Dirichlet 0.1      | q-FFL-style                 |       5 | 67.50 ± 0.33 | 62.92 ± 1.89 | 55 ± 4 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 46.03 ± 6.87       | 63.22 ± 3.15  |
| Dirichlet 0.1      | Pow-D                       |       5 | 65.93 ± 1.27 | 61.63 ± 1.98 | 62 ± 20 (4/5)      | 0.669 ± 0.054 | 3.8 ± 3.0   | 99 ± 2     | 67.2 ± 0.0  | 0.03 ± 0.00 | 42.52 ± 4.60       | 62.09 ± 2.03  |
| Dirichlet 0.1      | Oort-style                  |       5 | 67.37 ± 0.70 | 63.61 ± 0.51 | 53 ± 12 (5/5)      | 0.642 ± 0.043 | 0.0 ± 0.0   | 91 ± 3     | 33.6 ± 0.0  | 0.03 ± 0.00 | 48.10 ± 9.25       | 64.38 ± 3.36  |
| Dirichlet 0.1      | DivFL-style                 |       5 | 62.62 ± 1.36 | 60.47 ± 1.41 | 99 (1/5)           | 0.163 ± 0.018 | 58.2 ± 6.8  | 100 ± 0    | 336.0 ± 0.0 | 0.03 ± 0.01 | 39.66 ± 6.76       | 59.11 ± 4.09  |
| Dirichlet 0.1      | FairFedCS                   |       5 | 67.24 ± 1.15 | 63.95 ± 1.20 | 57 ± 10 (5/5)      | 0.886 ± 0.021 | 0.0 ± 0.0   | 41 ± 2     | 33.6 ± 0.0  | 0.02 ± 0.00 | 41.41 ± 5.42       | 62.60 ± 2.25  |
| Dirichlet 0.1      | Greedy (reputation)         |       5 | 59.72 ± 3.43 | 58.23 ± 4.28 | not reached (0/5)  | 0.113 ± 0.010 | 74.8 ± 7.7  | 100 ± 0    | 33.6 ± 0.0  | 0.02 ± 0.00 | 36.00 ± 8.71       | 56.95 ± 5.38  |
| Dirichlet 0.1      | FedFACS (full)              |       5 | 67.74 ± 0.42 | 61.45 ± 2.22 | 64 ± 5 (5/5)       | 0.996 ± 0.001 | 0.0 ± 0.0   | 11 ± 1     | 336.0 ± 0.0 | 0.23 ± 0.00 | 35.65 ± 15.31      | 57.99 ± 11.67 |
| Dirichlet 0.1      | FedFACS-A2 (sample weights) |       5 | 66.02 ± 0.84 | 62.01 ± 1.46 | 70 ± 14 (4/5)      | 0.996 ± 0.001 | 0.0 ± 0.0   | 11 ± 1     | 336.0 ± 0.0 | 0.23 ± 0.00 | 39.60 ± 7.19       | 61.00 ± 4.32  |
| Dirichlet 0.5      | FedAvg (random)             |       5 | 71.97 ± 0.30 | 70.30 ± 0.69 | 54 ± 11 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 62.41 ± 1.03       | 71.03 ± 0.60  |
| Dirichlet 0.5      | FedProx                     |       5 | 72.07 ± 0.36 | 70.46 ± 0.57 | 59 ± 14 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 61.93 ± 1.69       | 71.03 ± 1.09  |
| Dirichlet 0.5      | FedNova                     |       5 | 72.19 ± 0.53 | 70.65 ± 0.43 | 55 ± 15 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 62.71 ± 1.17       | 71.00 ± 0.81  |
| Dirichlet 0.5      | q-FFL-style                 |       5 | 72.07 ± 0.27 | 70.02 ± 0.95 | 59 ± 15 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 62.05 ± 2.11       | 70.67 ± 0.93  |
| Dirichlet 0.5      | Pow-D                       |       5 | 71.52 ± 0.45 | 68.35 ± 0.40 | 57 ± 11 (5/5)      | 0.867 ± 0.024 | 0.0 ± 0.0   | 70 ± 11    | 67.2 ± 0.0  | 0.02 ± 0.00 | 60.17 ± 1.60       | 69.20 ± 1.49  |
| Dirichlet 0.5      | Oort-style                  |       5 | 71.74 ± 0.42 | 70.23 ± 0.44 | 54 ± 10 (5/5)      | 0.814 ± 0.013 | 0.0 ± 0.0   | 74 ± 8     | 33.6 ± 0.0  | 0.03 ± 0.00 | 61.07 ± 2.25       | 70.60 ± 1.41  |
| Dirichlet 0.5      | DivFL-style                 |       5 | 68.80 ± 0.67 | 68.05 ± 0.56 | not reached (0/5)  | 0.192 ± 0.019 | 51.0 ± 3.5  | 100 ± 0    | 336.0 ± 0.0 | 0.02 ± 0.00 | 59.43 ± 1.93       | 68.23 ± 0.99  |
| Dirichlet 0.5      | FairFedCS                   |       5 | 72.24 ± 0.41 | 71.33 ± 0.20 | 46 ± 6 (5/5)       | 0.841 ± 0.016 | 0.0 ± 0.0   | 41 ± 1     | 33.6 ± 0.0  | 0.02 ± 0.00 | 62.53 ± 1.02       | 71.00 ± 0.80  |
| Dirichlet 0.5      | Greedy (reputation)         |       5 | 65.76 ± 1.41 | 65.25 ± 1.52 | not reached (0/5)  | 0.109 ± 0.006 | 66.0 ± 19.2 | 100 ± 0    | 33.6 ± 0.0  | 0.02 ± 0.00 | 56.09 ± 2.58       | 65.10 ± 1.75  |
| Dirichlet 0.5      | FedFACS (full)              |       5 | 71.50 ± 0.69 | 66.90 ± 5.39 | 61 ± 4 (5/5)       | 0.997 ± 0.000 | 0.0 ± 0.0   | 11 ± 0     | 336.0 ± 0.0 | 0.23 ± 0.00 | 63.05 ± 0.85       | 70.55 ± 0.63  |
| Dirichlet 0.5      | FedFACS-A2 (sample weights) |       5 | 72.21 ± 0.20 | 70.51 ± 0.76 | 53 ± 10 (5/5)      | 0.997 ± 0.001 | 0.0 ± 0.0   | 11 ± 0     | 336.0 ± 0.0 | 0.23 ± 0.00 | 62.93 ± 1.26       | 71.08 ± 0.50  |
| Two classes/client | FedAvg (random)             |       5 | 67.10 ± 0.30 | 64.00 ± 0.61 | 74 ± 6 (5/5)       | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 48.08 ± 6.03       | 64.93 ± 2.72  |
| Two classes/client | FedProx                     |       5 | 66.98 ± 0.50 | 64.03 ± 0.56 | 79 ± 12 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 48.36 ± 6.00       | 65.21 ± 2.55  |
| Two classes/client | FedNova                     |       5 | 66.77 ± 1.19 | 63.82 ± 0.87 | 79 ± 15 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 45.81 ± 5.75       | 63.82 ± 3.85  |
| Two classes/client | q-FFL-style                 |       5 | 66.69 ± 0.91 | 63.58 ± 1.11 | 84 ± 14 (5/5)      | 0.920 ± 0.005 | 0.0 ± 0.0   | 61 ± 12    | 33.6 ± 0.0  | 0.02 ± 0.00 | 48.38 ± 6.28       | 64.58 ± 2.07  |
| Two classes/client | Pow-D                       |       5 | 67.18 ± 0.61 | 62.67 ± 1.20 | 81 ± 7 (5/5)       | 0.908 ± 0.010 | 0.0 ± 0.0   | 64 ± 13    | 67.2 ± 0.0  | 0.02 ± 0.00 | 45.14 ± 6.29       | 62.08 ± 2.25  |
| Two classes/client | Oort-style                  |       5 | 66.95 ± 0.97 | 63.44 ± 1.04 | 71 ± 15 (5/5)      | 0.602 ± 0.024 | 0.0 ± 0.0   | 90 ± 5     | 33.6 ± 0.0  | 0.02 ± 0.00 | 43.88 ± 6.29       | 62.12 ± 2.59  |
| Two classes/client | DivFL-style                 |       5 | 63.85 ± 1.24 | 62.19 ± 0.76 | not reached (0/5)  | 0.192 ± 0.031 | 47.6 ± 5.5  | 100 ± 0    | 336.0 ± 0.0 | 0.02 ± 0.00 | 47.67 ± 3.67       | 61.97 ± 1.33  |
| Two classes/client | FairFedCS                   |       5 | 67.36 ± 1.15 | 64.22 ± 0.65 | 65 ± 14 (5/5)      | 0.860 ± 0.009 | 0.0 ± 0.0   | 39 ± 0     | 33.6 ± 0.0  | 0.02 ± 0.00 | 45.09 ± 6.11       | 63.79 ± 2.71  |
| Two classes/client | Greedy (reputation)         |       5 | 58.11 ± 3.77 | 56.30 ± 4.52 | not reached (0/5)  | 0.113 ± 0.007 | 65.0 ± 19.2 | 100 ± 0    | 33.6 ± 0.0  | 0.02 ± 0.00 | 33.66 ± 12.86      | 53.03 ± 6.97  |
| Two classes/client | FedFACS (full)              |       5 | 66.15 ± 1.37 | 63.05 ± 1.46 | 73 ± 12 (4/5)      | 0.998 ± 0.000 | 0.0 ± 0.0   | 11 ± 0     | 336.0 ± 0.0 | 0.23 ± 0.00 | 45.19 ± 6.29       | 62.18 ± 3.59  |
| Two classes/client | FedFACS-A2 (sample weights) |       5 | 67.57 ± 1.17 | 63.63 ± 0.87 | 66 ± 6 (5/5)       | 0.998 ± 0.000 | 0.0 ± 0.0   | 10 ± 1     | 336.0 ± 0.0 | 0.23 ± 0.00 | 47.39 ± 4.25       | 63.82 ± 1.76  |

# 4. Pooled paired differences (all datasets and partitions)

Each cell is the mean paired difference in percentage points with its 95% interval; n is the number of paired runs. Positive means the first method is better.

## 4.1 FedFACS (full) minus each method

| Compared with               |   n | Acc ckpt             | Acc last10           | Worst-10% client      | Macro-F1             | Late-round swing     |
|:----------------------------|----:|:---------------------|:---------------------|:----------------------|:---------------------|:---------------------|
| FedAvg (random)             |  45 | -0.16 [-0.42, +0.12] | -3.14 [-4.28, -2.11] | -4.36 [-7.91, -1.05]  | -2.28 [-4.17, -0.66] | +3.65 [+2.47, +4.94] |
| FedProx                     |  45 | -0.19 [-0.44, +0.06] | -3.27 [-4.39, -2.25] | -4.49 [-8.00, -1.26]  | -2.38 [-4.23, -0.80] | +3.77 [+2.61, +5.06] |
| FedNova                     |  45 | -0.46 [-0.76, -0.17] | -3.54 [-4.67, -2.55] | -4.74 [-8.44, -1.32]  | -2.47 [-4.51, -0.77] | +3.57 [+2.39, +4.88] |
| q-FFL-style                 |  45 | -0.63 [-0.87, -0.39] | -3.28 [-4.37, -2.28] | -4.90 [-8.65, -1.30]  | -2.52 [-4.49, -0.85] | +3.17 [+1.99, +4.47] |
| Pow-D                       |  45 | -0.20 [-0.53, +0.14] | -2.83 [-4.08, -1.69] | -3.19 [-6.76, +0.14]  | -1.93 [-3.81, -0.26] | +3.28 [+2.04, +4.59] |
| Oort-style                  |  45 | -0.54 [-0.88, -0.17] | -3.43 [-4.68, -2.26] | -6.15 [-10.05, -2.60] | -2.86 [-4.97, -1.06] | +4.11 [+2.94, +5.37] |
| DivFL-style                 |  45 | +2.22 [+1.69, +2.77] | -1.95 [-3.16, -0.85] | -3.53 [-6.36, -1.00]  | -0.84 [-2.38, +0.51] | +4.60 [+3.50, +5.80] |
| FairFedCS                   |  45 | -0.45 [-0.76, -0.15] | -3.80 [-4.89, -2.80] | -4.69 [-7.95, -1.75]  | -2.68 [-4.44, -1.18] | +3.93 [+2.79, +5.16] |
| Greedy (reputation)         |  45 | +4.88 [+3.67, +6.23] | +0.40 [-1.47, +2.26] | +2.09 [-2.28, +6.29]  | +2.25 [-0.14, +4.72] | +4.94 [+3.87, +6.11] |
| FedFACS-A2 (sample weights) |  45 | -0.15 [-0.45, +0.16] | -3.03 [-4.20, -1.98] | -3.26 [-6.21, -0.62]  | -1.94 [-3.56, -0.48] | +3.47 [+2.28, +4.81] |

## 4.2 FedFACS-A2 (sample weights) minus each method

| Compared with       |   n | Acc ckpt             | Acc last10           | Worst-10% client     | Macro-F1             | Late-round swing     |
|:--------------------|----:|:---------------------|:---------------------|:---------------------|:---------------------|:---------------------|
| FedAvg (random)     |  45 | -0.00 [-0.25, +0.25] | -0.11 [-0.39, +0.16] | -1.10 [-3.62, +1.32] | -0.34 [-1.37, +0.60] | +0.17 [-0.03, +0.39] |
| FedProx             |  45 | -0.04 [-0.30, +0.23] | -0.24 [-0.52, +0.03] | -1.23 [-3.76, +1.20] | -0.45 [-1.46, +0.47] | +0.30 [+0.08, +0.52] |
| FedNova             |  45 | -0.31 [-0.61, +0.01] | -0.51 [-0.82, -0.22] | -1.48 [-4.14, +1.14] | -0.54 [-1.69, +0.60] | +0.09 [-0.15, +0.32] |
| q-FFL-style         |  45 | -0.48 [-0.74, -0.20] | -0.25 [-0.63, +0.13] | -1.64 [-4.25, +1.00] | -0.58 [-1.61, +0.39] | -0.30 [-0.57, -0.04] |
| Pow-D               |  45 | -0.05 [-0.26, +0.19] | +0.20 [-0.22, +0.63] | +0.07 [-3.02, +3.13] | +0.01 [-1.12, +1.10] | -0.19 [-0.44, +0.05] |
| Oort-style          |  45 | -0.39 [-0.73, -0.02] | -0.41 [-0.93, +0.13] | -2.88 [-5.96, -0.02] | -0.92 [-2.20, +0.27] | +0.63 [+0.38, +0.89] |
| DivFL-style         |  45 | +2.37 [+1.95, +2.81] | +1.08 [+0.69, +1.50] | -0.27 [-2.63, +1.83] | +1.10 [+0.25, +1.90] | +1.12 [+0.79, +1.46] |
| FairFedCS           |  45 | -0.29 [-0.56, -0.02] | -0.77 [-1.09, -0.47] | -1.43 [-3.76, +0.68] | -0.74 [-1.67, +0.10] | +0.45 [+0.24, +0.68] |
| Greedy (reputation) |  45 | +5.03 [+3.77, +6.40] | +3.43 [+2.25, +4.78] | +5.35 [+1.80, +9.35] | +4.19 [+2.36, +6.29] | +1.46 [+1.15, +1.79] |
| FedFACS (full)      |  45 | +0.15 [-0.16, +0.45] | +3.03 [+1.96, +4.18] | +3.26 [+0.58, +6.22] | +1.94 [+0.46, +3.56] | -3.47 [-4.77, -2.29] |

## 4.3 Participation and cost, pooled over all runs

| Method                      |   Runs |   Jain |   Never selected % |   Max wait |   Down GB |   Up GB |   Steps M |   Acc ckpt |   Acc last10 |   Late-round swing |   Worst-10% client |
|:----------------------------|-------:|-------:|-------------------:|-----------:|----------:|--------:|----------:|-----------:|-------------:|-------------------:|-------------------:|
| FedAvg (random)             |     45 |  0.92  |                0   |       60.6 |      33.6 |    33.6 |      0.03 |      81.9  |        79.62 |               2    |              67.09 |
| FedProx                     |     45 |  0.92  |                0   |       60.6 |      33.6 |    33.6 |      0.03 |      81.94 |        79.74 |               1.87 |              67.22 |
| FedNova                     |     45 |  0.92  |                0   |       60.6 |      33.6 |    33.6 |      0.03 |      82.21 |        80.01 |               2.08 |              67.47 |
| q-FFL-style                 |     45 |  0.92  |                0   |       60.6 |      33.6 |    33.6 |      0.03 |      82.38 |        79.75 |               2.47 |              67.62 |
| Pow-D                       |     45 |  0.727 |                4.4 |       92.4 |      67.2 |    33.6 |      0.03 |      81.94 |        79.31 |               2.36 |              65.92 |
| Oort-style                  |     45 |  0.493 |                0   |       85.8 |      33.6 |    33.6 |      0.03 |      82.28 |        79.91 |               1.54 |              68.87 |
| DivFL-style                 |     45 |  0.203 |               47.4 |      100   |     336   |    33.6 |      0.03 |      79.52 |        78.42 |               1.05 |              66.26 |
| FairFedCS                   |     45 |  0.865 |                0   |       40   |      33.6 |    33.6 |      0.03 |      82.19 |        80.27 |               1.72 |              67.42 |
| Greedy (reputation)         |     45 |  0.114 |               67.9 |      100   |      33.6 |    33.6 |      0.03 |      76.87 |        76.07 |               0.71 |              60.63 |
| FedFACS (full)              |     45 |  0.995 |                0   |       12.1 |     336   |    31.9 |      0.27 |      81.74 |        76.47 |               5.64 |              62.73 |
| FedFACS-A2 (sample weights) |     45 |  0.997 |                0   |       11.3 |     336   |    32.6 |      0.27 |      81.9  |        79.5  |               2.17 |              65.99 |

## 4.4 FedFACS minus FedAvg in every dataset and partition (paired, mean over seeds)

| Dataset   | Partition          |   n | Acc ckpt diff        | Acc last10 diff       | Worst-10% client diff   |
|:----------|:-------------------|----:|:---------------------|:----------------------|:------------------------|
| FMNIST    | Dirichlet 0.1      |   5 | -0.33 [-0.81, +0.34] | -0.90 [-1.90, +0.14]  | -8.16 [-20.17, +3.67]   |
| FMNIST    | Dirichlet 0.5      |   5 | -0.40 [-0.71, -0.07] | -2.33 [-3.60, -1.47]  | -0.14 [-2.74, +1.97]    |
| FMNIST    | Two classes/client |   5 | +0.32 [+0.01, +0.76] | -2.49 [-4.66, -0.15]  | -1.54 [-12.88, +11.75]  |
| MNIST     | Dirichlet 0.1      |   5 | -0.27 [-0.86, +0.21] | -4.20 [-6.50, -1.91]  | -6.16 [-18.16, +3.49]   |
| MNIST     | Dirichlet 0.5      |   5 | -0.58 [-0.82, -0.36] | -9.58 [-12.93, -7.20] | -9.99 [-24.25, -0.77]   |
| MNIST     | Two classes/client |   5 | -0.16 [-0.35, +0.05] | -3.84 [-6.28, -1.22]  | -3.02 [-7.34, +1.24]    |
| CIFAR-10  | Dirichlet 0.1      |   5 | +1.43 [+0.70, +2.30] | -0.58 [-1.97, +1.23]  | -7.99 [-25.30, +4.21]   |
| CIFAR-10  | Dirichlet 0.5      |   5 | -0.47 [-0.85, -0.09] | -3.40 [-8.20, -0.43]  | +0.64 [-0.49, +2.06]    |
| CIFAR-10  | Two classes/client |   5 | -0.95 [-2.05, +0.18] | -0.95 [-2.23, +0.39]  | -2.89 [-8.89, +2.61]    |

# 5. Ablation study (Dirichlet 0.5, 3 seeds)

## 5.1 FMNIST

| Variant                             |   Seeds | Acc ckpt     | Acc last10   | Rounds to target   | Jain          | Never %    | Mean cohort   | Worst-10% client   | Late-round swing   | Ckpt acc minus full   | Last10 minus full    |
|:------------------------------------|--------:|:-------------|:-------------|:-------------------|:--------------|:-----------|:--------------|:-------------------|:-------------------|:----------------------|:---------------------|
| Full FedFACS                        |       3 | 85.07 ± 0.37 | 82.56 ± 0.94 | 52 ± 9             | 0.997 ± 0.001 | 0.0 ± 0.0  | 9.63 ± 0.04   | 74.93 ± 1.05       | 2.59 ± 0.90        | nan                   | nan                  |
| A1: fixed cohort, sample weights    |       3 | 84.98 ± 0.66 | 83.56 ± 1.23 | 51 ± 13            | 0.999 ± 0.001 | 0.0 ± 0.0  | 10.00 ± 0.00  | 71.17 ± 2.47       | 1.83 ± 0.63        | -0.09 [-0.65, +0.26]  | +1.00 [-0.30, +2.42] |
| A2: adaptive cohort, sample weights |       3 | 85.54 ± 0.34 | 84.57 ± 0.55 | 48 ± 6             | 0.998 ± 0.001 | 0.0 ± 0.0  | 9.83 ± 0.06   | 76.30 ± 2.18       | 0.93 ± 0.23        | +0.47 [-0.34, +0.98]  | +2.01 [+0.74, +2.72] |
| Fixed mixing a=0.5 (no controller)  |       3 | 83.82 ± 0.26 | 77.96 ± 0.25 | 68 ± 5             | 0.934 ± 0.008 | 0.0 ± 0.0  | 9.31 ± 0.13   | 71.78 ± 6.89       | 6.23 ± 2.04        | -1.25 [-1.41, -1.13]  | -4.59 [-5.38, -3.60] |
| No fairness term (a=1)              |       3 | 83.05 ± 0.75 | 77.67 ± 0.44 | 64 ± 11            | 0.353 ± 0.026 | 18.7 ± 3.2 | 9.54 ± 0.06   | 68.33 ± 5.75       | 4.43 ± 1.28        | -2.02 [-2.59, -1.59]  | -4.89 [-5.42, -4.42] |
| No variance penalty (mu=0)          |       3 | 84.39 ± 0.19 | 80.90 ± 1.89 | 55 ± 7             | 0.996 ± 0.001 | 0.0 ± 0.0  | 9.50 ± 0.05   | 70.01 ± 5.59       | 4.81 ± 2.72        | -0.68 [-0.93, -0.50]  | -1.66 [-2.94, -0.48] |
| Loss as utility                     |       3 | 85.32 ± 0.17 | 84.18 ± 0.28 | 41 ± 8             | 0.998 ± 0.000 | 0.0 ± 0.0  | 9.78 ± 0.01   | 76.61 ± 2.43       | 1.27 ± 0.42        | +0.25 [-0.08, +0.48]  | +1.62 [+0.72, +2.21] |
| Random scores                       |       3 | 85.22 ± 0.11 | 84.31 ± 0.55 | 42 ± 8             | 0.916 ± 0.022 | 0.0 ± 0.0  | 9.83 ± 0.04   | 72.88 ± 1.65       | 1.12 ± 0.16        | +0.15 [-0.39, +0.51]  | +1.75 [+0.84, +3.18] |
| Rescaled utility                    |       3 | 85.03 ± 0.17 | 82.87 ± 1.68 | 55 ± 6             | 0.995 ± 0.002 | 0.0 ± 0.0  | 9.64 ± 0.05   | 74.06 ± 3.40       | 3.74 ± 2.89        | -0.04 [-0.44, +0.24]  | +0.31 [-2.58, +2.40] |

## 5.2 CIFAR-10

| Variant                             |   Seeds | Acc ckpt     | Acc last10   | Rounds to target   | Jain          | Never %    | Mean cohort   | Worst-10% client   | Late-round swing   | Ckpt acc minus full   | Last10 minus full     |
|:------------------------------------|--------:|:-------------|:-------------|:-------------------|:--------------|:-----------|:--------------|:-------------------|:-------------------|:----------------------|:----------------------|
| Full FedFACS                        |       3 | 71.31 ± 0.90 | 65.57 ± 6.98 | 59 ± 4             | 0.996 ± 0.000 | 0.0 ± 0.0  | 9.66 ± 0.06   | 62.81 ± 0.37       | 6.18 ± 3.85        | nan                   | nan                   |
| A1: fixed cohort, sample weights    |       3 | 71.93 ± 0.77 | 70.23 ± 0.25 | 63 ± 8             | 0.998 ± 0.000 | 0.0 ± 0.0  | 10.00 ± 0.00  | 62.62 ± 4.30       | 2.05 ± 0.31        | +0.62 [-0.45, +2.08]  | +4.65 [+0.05, +12.74] |
| A2: adaptive cohort, sample weights |       3 | 72.13 ± 0.23 | 70.17 ± 0.83 | 47 ± 4             | 0.997 ± 0.000 | 0.0 ± 0.0  | 9.84 ± 0.02   | 63.25 ± 1.52       | 1.69 ± 0.10        | +0.82 [+0.28, +1.59]  | +4.59 [-0.69, +12.93] |
| Fixed mixing a=0.5 (no controller)  |       3 | 69.69 ± 0.46 | 63.77 ± 0.67 | 90 ± 6             | 0.934 ± 0.011 | 0.0 ± 0.0  | 9.53 ± 0.05   | 43.25 ± 3.32       | 5.69 ± 0.82        | -1.62 [-2.33, -1.13]  | -1.81 [-5.91, +5.49]  |
| No fairness term (a=1)              |       3 | 69.11 ± 0.53 | 63.39 ± 1.06 | n/a                | 0.566 ± 0.020 | 10.0 ± 2.6 | 9.64 ± 0.03   | 50.89 ± 7.56       | 4.72 ± 0.89        | -2.20 [-2.69, -1.53]  | -2.19 [-6.20, +4.99]  |
| No variance penalty (mu=0)          |       3 | 70.77 ± 0.73 | 66.08 ± 3.67 | 67 ± 20            | 0.996 ± 0.000 | 0.0 ± 0.0  | 9.60 ± 0.13   | 47.53 ± 16.56      | 4.80 ± 2.60        | -0.54 [-0.80, -0.40]  | +0.51 [-8.00, +11.30] |
| Loss as utility                     |       3 | 71.88 ± 0.10 | 70.32 ± 0.46 | 52 ± 6             | 0.999 ± 0.000 | 0.0 ± 0.0  | 9.85 ± 0.03   | 61.44 ± 2.44       | 1.67 ± 0.30        | +0.57 [-0.33, +1.64]  | +4.75 [+0.13, +13.33] |
| Random scores                       |       3 | 72.02 ± 0.34 | 70.32 ± 0.75 | 49 ± 8             | 0.916 ± 0.023 | 0.0 ± 0.0  | 9.89 ± 0.04   | 61.95 ± 3.70       | 1.49 ± 0.07        | +0.71 [-0.02, +2.00]  | +4.74 [-0.47, +13.33] |
| Rescaled utility                    |       3 | 71.51 ± 0.07 | 68.43 ± 0.87 | 52 ± 7             | 0.997 ± 0.001 | 0.0 ± 0.0  | 9.74 ± 0.04   | 50.38 ± 15.92      | 2.88 ± 0.57        | +0.20 [-0.51, +1.14]  | +2.86 [-1.46, +10.53] |

# 6. Confirmation of the sample-weighted variant (A2)

A2 (FedFACS selection and adaptive cohort, sample-count aggregation weights) was singled out after seeing the ablations on FMNIST and CIFAR-10, Dirichlet 0.5, seeds 0-2. **Held-out** means every run that was not used for that choice: all other dataset/partition cells, and seeds 3 and 4 of the two original cells.

## 6.1 Held-out runs only

| A2 minus        |   n | Acc ckpt             | Acc last10           | Worst-10% client     | Late-round swing     | Jain                 | Max wait                |
|:----------------|----:|:---------------------|:---------------------|:---------------------|:---------------------|:---------------------|:------------------------|
| FedAvg (random) |  39 | -0.04 [-0.33, +0.24] | -0.12 [-0.41, +0.17] | -1.55 [-4.43, +1.13] | +0.22 [-0.01, +0.47] | +0.08 [+0.07, +0.08] | -49.74 [-53.08, -46.36] |
| FedFACS (full)  |  39 | +0.08 [-0.27, +0.41] | +2.99 [+1.87, +4.23] | +3.62 [+0.51, +6.95] | -3.54 [-5.01, -2.18] | +0.00 [+0.00, +0.00] | -0.85 [-1.44, -0.31]    |
| Pow-D           |  39 | -0.12 [-0.33, +0.14] | +0.04 [-0.40, +0.51] | -0.41 [-3.95, +3.11] | -0.12 [-0.38, +0.15] | +0.27 [+0.24, +0.31] | -81.54 [-85.82, -76.67] |
| Oort-style      |  39 | -0.48 [-0.87, -0.08] | -0.48 [-1.09, +0.14] | -3.63 [-7.17, -0.37] | +0.69 [+0.39, +0.98] | +0.52 [+0.47, +0.57] | -75.79 [-77.92, -73.56] |
| FairFedCS       |  39 | -0.34 [-0.65, -0.03] | -0.82 [-1.17, -0.50] | -1.71 [-4.36, +0.70] | +0.49 [+0.25, +0.74] | +0.13 [+0.12, +0.14] | -28.62 [-29.15, -28.03] |

## 6.2 All runs (including those used for the choice)

| A2 minus        |   n | Acc ckpt             | Acc last10           | Worst-10% client     | Late-round swing     | Jain                 | Max wait                |
|:----------------|----:|:---------------------|:---------------------|:---------------------|:---------------------|:---------------------|:------------------------|
| FedAvg (random) |  45 | -0.00 [-0.25, +0.25] | -0.11 [-0.38, +0.16] | -1.10 [-3.62, +1.28] | +0.17 [-0.04, +0.39] | +0.08 [+0.08, +0.08] | -49.31 [-52.62, -46.20] |
| FedFACS (full)  |  45 | +0.15 [-0.16, +0.45] | +3.03 [+1.94, +4.19] | +3.26 [+0.60, +6.18] | -3.47 [-4.79, -2.27] | +0.00 [+0.00, +0.00] | -0.78 [-1.31, -0.31]    |
| Pow-D           |  45 | -0.05 [-0.26, +0.18] | +0.20 [-0.22, +0.62] | +0.07 [-2.93, +3.13] | -0.19 [-0.44, +0.06] | +0.27 [+0.24, +0.30] | -81.07 [-84.87, -76.64] |
| Oort-style      |  45 | -0.39 [-0.73, -0.03] | -0.41 [-0.93, +0.15] | -2.88 [-6.05, +0.00] | +0.63 [+0.38, +0.89] | +0.50 [+0.45, +0.55] | -74.53 [-76.84, -72.18] |
| FairFedCS       |  45 | -0.29 [-0.57, -0.02] | -0.77 [-1.09, -0.47] | -1.43 [-3.75, +0.68] | +0.45 [+0.23, +0.68] | +0.13 [+0.13, +0.14] | -28.71 [-29.22, -28.20] |

# 7. Does the KL utility predict the benefit of a client's update?

Spearman correlation between each client score and the validation-loss gain from adding that client's update (positive = higher score, larger gain). Cells give the mean over rounds and runs with a 95% interval. 'gce' is the global model's loss on the client's local examples; 'n' is the client's sample count.

| method    | scenario   |   n_round_runs | rho(kl)             | rho(var)            | rho(F)              | rho(fit)            | rho(gce)            | rho(n)              |
|:----------|:-----------|---------------:|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|
| abl_loss  | s3         |             18 | -0.78 [-0.87,-0.69] | -0.31 [-0.36,-0.25] | +0.23 [+0.12,+0.35] | +0.13 [+0.07,+0.19] | -0.78 [-0.87,-0.69] | +nan [+nan,+nan]    |
| abl_nopen | s3         |             18 | +0.12 [-0.12,+0.36] | +0.11 [-0.02,+0.24] | -0.06 [-0.13,+0.00] | -0.02 [-0.11,+0.07] | -0.76 [-0.87,-0.65] | +nan [+nan,+nan]    |
| fedfacs   | s1_0.1     |             90 | +0.50 [+0.42,+0.58] | +0.32 [+0.28,+0.36] | +0.14 [+0.11,+0.17] | +0.17 [+0.10,+0.23] | +0.64 [+0.59,+0.69] | -0.03 [-0.05,-0.00] |
| fedfacs   | s1_0.5     |             90 | +0.39 [+0.33,+0.45] | +0.25 [+0.21,+0.28] | +0.12 [+0.09,+0.14] | +0.17 [+0.13,+0.21] | +0.50 [+0.45,+0.55] | -0.02 [-0.06,+0.02] |
| fedfacs   | s2         |             90 | +0.73 [+0.69,+0.77] | +0.24 [+0.18,+0.30] | +0.14 [+0.11,+0.17] | +0.32 [+0.27,+0.38] | +0.75 [+0.71,+0.79] | +0.13 [+0.06,+0.19] |
| fedfacs   | s3         |             18 | +0.12 [-0.09,+0.33] | +0.11 [-0.01,+0.22] | -0.08 [-0.14,-0.03] | -0.04 [-0.12,+0.03] | -0.77 [-0.88,-0.65] | +nan [+nan,+nan]    |

# 8. Does the variance penalty detect noisy clients? (IID split, label noise 0-45%)

Detection AUC for clients with more than 22.5% label noise (0.5 = chance, 1.0 = perfect) and Spearman correlation between each score and the noise level.

| method    |   n | auc_kl           | auc_var          | auc_fit          | auc_gce          | rho_noise_kl       | rho_noise_var      | rho_noise_gce    |
|:----------|----:|:-----------------|:-----------------|:-----------------|:-----------------|:-------------------|:-------------------|:-----------------|
| abl_loss  |  18 | 0.99 [0.99,0.99] | 0.69 [0.65,0.72] | 0.43 [0.38,0.49] | 0.99 [0.99,0.99] | 0.97 [0.97,0.98]   | 0.37 [0.31,0.42]   | 0.97 [0.97,0.98] |
| abl_nopen |  18 | 0.45 [0.33,0.57] | 0.45 [0.38,0.52] | 0.55 [0.51,0.59] | 0.99 [0.99,0.99] | -0.10 [-0.33,0.13] | -0.09 [-0.21,0.03] | 0.97 [0.97,0.98] |
| fedfacs   |  18 | 0.46 [0.35,0.56] | 0.45 [0.39,0.52] | 0.54 [0.51,0.59] | 0.99 [0.99,0.99] | -0.10 [-0.30,0.10] | -0.09 [-0.19,0.02] | 0.97 [0.97,0.98] |

## 8.1 Accuracy and fairness in the noisy IID setting

| dataset   | method    |   seeds | acc_best     | jfi_raw       | jfi_quality_adj   | client_p10   |
|:----------|:----------|--------:|:-------------|:--------------|:------------------|:-------------|
| cifar10   | abl_loss  |       3 | 71.51 ± 0.67 | 0.999 ± 0.000 | 0.969 ± 0.003     | 65.48 ± 1.17 |
| cifar10   | abl_nopen |       3 | 71.51 ± 0.29 | 0.999 ± 0.000 | 0.974 ± 0.001     | 62.93 ± 1.69 |
| cifar10   | fairfedcs |       3 | 71.34 ± 0.22 | 0.905 ± 0.019 | 0.878 ± 0.019     | 65.15 ± 0.71 |
| cifar10   | fedfacs   |       3 | 71.14 ± 0.56 | 0.999 ± 0.000 | 0.973 ± 0.002     | 64.00 ± 0.68 |
| cifar10   | greedy    |       3 | 63.10 ± 0.86 | 0.119 ± 0.009 | 0.120 ± 0.011     | 56.30 ± 0.64 |
| cifar10   | powd      |       3 | 69.18 ± 0.69 | 0.751 ± 0.006 | 0.683 ± 0.008     | 62.22 ± 1.11 |
| cifar10   | random    |       3 | 71.15 ± 0.23 | 0.919 ± 0.006 | 0.899 ± 0.007     | 64.41 ± 1.17 |
| fmnist    | abl_loss  |       3 | 85.62 ± 0.17 | 0.998 ± 0.000 | 0.965 ± 0.004     | 81.82 ± 0.91 |
| fmnist    | abl_nopen |       3 | 85.64 ± 0.23 | 0.997 ± 0.000 | 0.963 ± 0.005     | 81.79 ± 0.91 |
| fmnist    | fairfedcs |       3 | 85.80 ± 0.40 | 0.877 ± 0.005 | 0.839 ± 0.013     | 81.79 ± 0.05 |
| fmnist    | fedfacs   |       3 | 85.75 ± 0.44 | 0.997 ± 0.000 | 0.963 ± 0.004     | 81.82 ± 0.91 |
| fmnist    | greedy    |       3 | 82.91 ± 0.75 | 0.119 ± 0.008 | 0.118 ± 0.008     | 77.85 ± 1.00 |
| fmnist    | powd      |       3 | 84.76 ± 0.17 | 0.539 ± 0.005 | 0.514 ± 0.006     | 80.61 ± 0.52 |
| fmnist    | random    |       3 | 85.74 ± 0.23 | 0.919 ± 0.006 | 0.894 ± 0.016     | 82.39 ± 0.50 |

# 9. Sensitivity (FMNIST, Dirichlet 0.5, 3 seeds)

| setting   |   seeds | acc_best     | r2t     | jfi           | cohort      | jitter      |
|:----------|--------:|:-------------|:--------|:--------------|:------------|:------------|
| default   |       3 | 85.07 ± 0.37 | 52 ± 9  | 0.997 ± 0.001 | 9.63 ± 0.04 | 2.59 ± 0.90 |
| _sB2      |       3 | 84.30 ± 0.34 | 56 ± 7  | 0.996 ± 0.001 | 9.53 ± 0.03 | 4.14 ± 1.69 |
| _sB8      |       3 | 85.19 ± 0.42 | 49 ± 13 | 0.997 ± 0.001 | 9.71 ± 0.03 | 2.55 ± 1.26 |
| _sbeta0.5 |       3 | 85.08 ± 0.56 | 51 ± 13 | 0.997 ± 0.001 | 9.65 ± 0.08 | 2.04 ± 0.11 |
| _scmin2   |       3 | 84.40 ± 0.74 | 45 ± 9  | 0.997 ± 0.001 | 9.27 ± 0.12 | 5.22 ± 1.29 |
| _scmin8   |       3 | 85.57 ± 0.44 | 48 ± 3  | 0.998 ± 0.001 | 9.93 ± 0.03 | 2.80 ± 0.34 |
| _slam10   |       3 | 85.07 ± 0.69 | 45 ± 7  | 0.997 ± 0.001 | 9.62 ± 0.10 | 2.64 ± 1.05 |
| _smu0     |       3 | 84.39 ± 0.19 | 55 ± 7  | 0.996 ± 0.001 | 9.50 ± 0.05 | 4.81 ± 2.72 |
| _smu10    |       3 | 85.02 ± 0.56 | 45 ± 8  | 0.997 ± 0.000 | 9.67 ± 0.08 | 1.69 ± 0.20 |

# 10. Scale (FMNIST, Dirichlet 0.5, 3 seeds)

|   N | method   |   seeds | acc_best     | down_GB      | up_GB      | s_per_round   | peak_MB    | jfi           | never_pct   | max_wait   |
|----:|:---------|--------:|:-------------|:-------------|:-----------|:--------------|:-----------|:--------------|:------------|:-----------|
|  50 | fedfacs  |       3 | 86.63 ± 0.37 | 168.0 ± 0.0  | 32.1 ± 0.3 | 3.10 ± 0.02   | 810 ± 109  | 0.999 ± 0.001 | 0.0 ± 0.0   | 5 ± 1      |
|  50 | random   |       3 | 86.73 ± 0.16 | 33.6 ± 0.0   | 33.6 ± 0.0 | 0.58 ± 0.00   | 827 ± 109  | 0.962 ± 0.006 | 0.0 ± 0.0   | 33 ± 6     |
| 100 | fedfacs  |       3 | 85.07 ± 0.37 | 336.0 ± 0.0  | 32.3 ± 0.1 | 3.40 ± 0.26   | 1218 ± 177 | 0.997 ± 0.001 | 0.0 ± 0.0   | 11 ± 0     |
| 100 | random   |       3 | 85.37 ± 0.04 | 33.6 ± 0.0   | 33.6 ± 0.0 | 0.31 ± 0.01   | 1123 ± 251 | 0.919 ± 0.006 | 0.0 ± 0.0   | 57 ± 12    |
| 200 | fedfacs  |       3 | 83.13 ± 0.39 | 671.9 ± 0.0  | 32.6 ± 0.2 | 4.23 ± 0.01   | 905 ± 108  | 0.992 ± 0.001 | 0.0 ± 0.0   | 21 ± 1     |
| 200 | random   |       3 | 83.28 ± 0.26 | 33.6 ± 0.0   | 33.6 ± 0.0 | 0.17 ± 0.00   | 922 ± 108  | 0.835 ± 0.013 | 0.7 ± 1.2   | 96 ± 4     |
| 400 | fedfacs  |       3 | 81.47 ± 0.69 | 1343.8 ± 0.0 | 32.8 ± 0.3 | 5.72 ± 0.02   | 947 ± 109  | 0.955 ± 0.002 | 0.0 ± 0.0   | 42 ± 1     |
| 400 | random   |       3 | 81.50 ± 0.66 | 33.6 ± 0.0   | 33.6 ± 0.0 | 0.10 ± 0.00   | 963 ± 109  | 0.711 ± 0.013 | 9.6 ± 0.6   | 100 ± 0    |

# 11. Targets and run health

Round-to-target uses a target equal to 97% of FedAvg's mean best validation accuracy:

| dataset   | scenario   |   target_val_acc |
|:----------|:-----------|-----------------:|
| cifar10   | s1_0.1     |            64.62 |
| cifar10   | s1_0.5     |            70.32 |
| cifar10   | s2         |            65.43 |
| cifar10   | s3         |            69.87 |
| fmnist    | s1_0.1     |            79.5  |
| fmnist    | s1_0.5     |            83.37 |
| fmnist    | s2         |            79.18 |
| fmnist    | s3         |            84.08 |
| mnist     | s1_0.1     |            90.92 |
| mnist     | s1_0.5     |            93.4  |
| mnist     | s2         |            90.63 |

Runs with a failed client update or a cancelled round: **0** of 621. Gradient-norm clipping events: 17326 (of about 61,211,846 training steps).

# 12. What the results support

| Claim | Supported? | Evidence (Sections) |
|:--------------------|:------|:--------------------------------------|
| Fair participation without starvation | Yes | Jain index, never-selected share, maximum wait (3, 4.3) |
| Accuracy at least as good as FedAvg | At the checkpoint only; not in the last 10 rounds | 4.1, 4.4 |
| Better outcomes for the worst clients | No | 4.1 (worst-10% client) |
| Lower communication cost | No: downloads and training are about 10 times higher; uploads about equal | 4.3 |
| Each component contributes | Yes for the fairness term, the controller and the variance penalty (stability weighting: next row) | 5 |
| Stability-weighted aggregation helps | No: sample weights give higher last-10 accuracy than stability weights on held-out runs | 5, 6 |
| KL utility predicts a client's benefit | Positive but weaker than the client's own loss | 7 |
| Variance penalty detects noisy clients | No (AUC about 0.5) | 8 |
| Selection score adds accuracy beyond random scores | No | 5 (random scores) |
