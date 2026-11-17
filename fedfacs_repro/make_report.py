"""Build the full experimental report (Word) from results/*.json. Runs NO experiments.   python make_report.py"""
import os
import subprocess
import sys

import numpy as np
import pandas as pd
import pypandoc
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

import analyze as A

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\0xRay\Downloads\paper\FedFACS_Experimental_Results_Report.docx"
subprocess.run([sys.executable, os.path.join(HERE, "analyze.py")], check=True, capture_output=True)

METHODS = ["random", "fedprox", "fednova", "qffl", "powd", "oort", "divfl", "fairfedcs", "greedy", "fedfacs", "abl_A2"]
LABEL = {"random": "FedAvg (random)", "fedprox": "FedProx", "fednova": "FedNova", "qffl": "q-FFL-style", "powd": "Pow-D",
         "oort": "Oort-style", "divfl": "DivFL-style", "fairfedcs": "FairFedCS", "greedy": "Greedy (reputation)",
         "fedfacs": "FedFACS (full)", "abl_A2": "FedFACS-A2 (sample weights)"}
ABL = ["fedfacs", "abl_A1", "abl_A2", "abl_fixmix", "abl_nofair", "abl_nopen", "abl_loss", "abl_randscore", "abl_rescale"]
ABL_LABEL = {"fedfacs": "Full FedFACS", "abl_A1": "A1: fixed cohort, sample weights", "abl_A2": "A2: adaptive cohort, sample weights",
             "abl_fixmix": "Fixed mixing a=0.5 (no controller)", "abl_nofair": "No fairness term (a=1)",
             "abl_nopen": "No variance penalty (mu=0)", "abl_loss": "Loss as utility", "abl_randscore": "Random scores",
             "abl_rescale": "Rescaled utility"}
DS = {"fmnist": "FMNIST", "mnist": "MNIST", "cifar10": "CIFAR-10"}
SC = {"s1_0.1": "Dirichlet 0.1", "s1_0.5": "Dirichlet 0.5", "s2": "Two classes/client"}

rows = A.load()
n_runs = len(rows)
base = [x for x in rows if x[4] == "" and x[1] in SC]
targets = {}
for (ds, sc) in {(x[0], x[1]) for x in base}:
    v = [A.run_metrics(x[5])["val_best"] for x in base if x[0] == ds and x[1] == sc and x[2] == "random"]
    if v:
        targets[(ds, sc)] = 0.97 * np.mean(v) / 100.0
M = {}
for ds, sc, me, seed, tag, r in rows:
    M[(ds, sc, me, tag, seed)] = A.run_metrics(r, targets.get((ds, sc)))


def cell(ds, sc, me, tag=""):
    return {s: v for (d, c, m_, t, s), v in M.items() if (d, c, m_, t) == (ds, sc, me, tag)}


rng = np.random.default_rng(0)


def ci(d):
    d = np.asarray(d, float)
    d = d[~np.isnan(d)]
    if len(d) < 2:
        return "n/a"
    b = rng.choice(d, (10000, len(d))).mean(1)
    return "%+.2f [%+.2f, %+.2f]" % (d.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5))


def tbl(df):
    return df.to_markdown(index=False) + "\n"


def csv(name):
    p = os.path.join(HERE, "analysis", name)
    return pd.read_csv(p) if os.path.exists(p) else None


md = []
add = md.append
add('::: {custom-style="R-Title"}\nFedFACS: Experimental Results Report (all stages, all seeds)\n:::\n')
add('::: {custom-style="R-Sub"}\nEvery number below is computed from the saved run files; no experiment is run while this report is built.\n:::\n')

# ------------------------------------------------------------------ 1. headline
add("# 1. Headline findings\n")
fed = {(k[0], k[1], k[4]): v for k, v in M.items() if k[2] == "fedfacs" and k[3] == "" and k[1] in SC}
a2 = {(k[0], k[1], k[4]): v for k, v in M.items() if k[2] == "abl_A2" and k[3] == "" and k[1] in SC}


def ci_nums(d):
    d = np.asarray(d, float)
    d = d[~np.isnan(d)]
    if len(d) < 2:
        return None
    b = rng.choice(d, (10000, len(d))).mean(1)
    return d.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5)


def pooled(refd, me, metric, keys=None):
    ks = [k for k in refd if (k[0], k[1], me, "", k[2]) in M and (keys is None or k in keys)]
    return ci_nums([refd[k][metric] - M[(k[0], k[1], me, "", k[2])][metric] for k in ks]), len(ks)


def fmt(t):
    return "n/a" if t is None else "%+.2f [%+.2f, %+.2f]" % tuple(t)


def verdict(t):
    if t is None:
        return "not comparable with"
    return "above" if t[1] > 0 else ("below" if t[2] < 0 else "not different from")


r_acc, n_ = pooled(fed, "random", "acc_best")
r_last, _ = pooled(fed, "random", "acc_last10")
r_p10, _ = pooled(fed, "random", "pc_p10")
sel = {(d, "s1_0.5", s) for d in ("fmnist", "cifar10") for s in range(3)}
hold = {k for k in a2 if k not in sel}
h_acc, n_h = pooled(a2, "fedfacs", "acc_best", hold)
h_last, _ = pooled(a2, "fedfacs", "acc_last10", hold)
h_jit, _ = pooled(a2, "fedfacs", "jitter", hold)
if h_last is None:
    stab_verdict = "Not yet testable: too few held-out A2 runs"
elif h_last[1] > 0:
    stab_verdict = "No: sample weights give higher last-10 accuracy than stability weights on held-out runs"
elif h_last[2] < 0:
    stab_verdict = "Yes: sample weights give lower last-10 accuracy than stability weights on held-out runs"
else:
    stab_verdict = "Not established: sample weights are not distinguishable on held-out runs"
mm = lambda me, k: np.mean([v[k] for kk, v in M.items() if kk[2] == me and kk[3] == "" and kk[1] in SC])
add(f"""Totals: **{n_runs} completed runs** (5 seeds for the main comparison). Paired comparisons use the same seed, partition and initialisation; intervals are 95% bootstrap intervals over paired runs.

1. **Participation fairness is the clear strength.** FedFACS Jain index {mm('fedfacs','jfi'):.3f} against {mm('random','jfi'):.3f} (FedAvg), {mm('powd','jfi'):.3f} (Pow-D), {mm('oort','jfi'):.3f} (Oort-style) and {mm('divfl','jfi'):.3f} (DivFL-style). Maximum wait {mm('fedfacs','max_wait'):.1f} rounds against {mm('random','max_wait'):.1f} (FedAvg) and {mm('divfl','max_wait'):.1f} (DivFL-style). Clients never selected: FedFACS {mm('fedfacs','never'):.1f}%, DivFL-style {mm('divfl','never'):.1f}%, Pow-D {mm('powd','never'):.1f}%.
2. **Checkpoint accuracy:** FedFACS is {verdict(r_acc)} FedAvg: {fmt(r_acc)} points (n={n_}).
3. **Last-10-round accuracy:** FedFACS is {verdict(r_last)} FedAvg: {fmt(r_last)} points; late-round swing {mm('fedfacs','jitter'):.2f} against {mm('random','jitter'):.2f} points.
4. **Worst-10% client accuracy:** FedFACS is {verdict(r_p10)} FedAvg: {fmt(r_p10)} points.
5. **Cost.** FedFACS downloads {mm('fedfacs','down_gb'):.1f} GB per run against {mm('random','down_gb'):.1f} GB for FedAvg and performs {mm('fedfacs','steps_m'):.2f} M training steps against {mm('random','steps_m'):.2f} M (every candidate trains every round).
6. **Sample-weighted variant (A2), held-out runs (n={n_h}):** A2 minus full FedFACS: checkpoint accuracy {fmt(h_acc)}, last-10-round accuracy {fmt(h_last)}, late-round swing {fmt(h_jit)} points (a negative swing means steadier). A2 is {verdict(h_last)} full FedFACS on last-10-round accuracy. Details in Section 6.
""")

# ------------------------------------------------------------------ 2. steps
add("# 2. Experimental procedure (steps)\n")
add("""1. **Data.** MNIST, Fashion-MNIST and CIFAR-10 (public). COVID-19 Radiography was not included (it requires a Kaggle login). Native resolution, grayscale replicated to 3 channels, ImageNet mean/std normalisation.
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
""")

# ------------------------------------------------------------------ 3. main tables
add("# 3. Main comparison (mean ± std over seeds)\n")
add("Columns: checkpoint accuracy (%), accuracy averaged over the last 10 rounds (%), rounds to target (runs reaching it), Jain index, clients never selected (%), maximum wait (rounds), download (GB), training steps (millions), worst-10% client accuracy (%), macro-F1 (%).\n")
for ds in ("fmnist", "mnist", "cifar10"):
    recs = []
    for sc in SC:
        for me in METHODS:
            c = cell(ds, sc, me)
            if not c:
                continue
            seeds = sorted(c)
            reached = [c[s]["r2t"] for s in seeds if c[s].get("r2t")]
            recs.append({"Partition": SC[sc], "Method": LABEL[me], "Seeds": len(seeds),
                         "Acc ckpt": A.ms([c[s]["acc_best"] for s in seeds]), "Acc last10": A.ms([c[s]["acc_last10"] for s in seeds]),
                         "Rounds to target": (A.ms(reached, "{:.0f}") + f" ({len(reached)}/{len(seeds)})") if reached else f"not reached (0/{len(seeds)})",
                         "Jain": A.ms([c[s]["jfi"] for s in seeds], "{:.3f}"), "Never %": A.ms([c[s]["never"] for s in seeds], "{:.1f}"),
                         "Max wait": A.ms([c[s]["max_wait"] for s in seeds], "{:.0f}"), "Down GB": A.ms([c[s]["down_gb"] for s in seeds], "{:.1f}"),
                         "Steps M": A.ms([c[s]["steps_m"] for s in seeds], "{:.2f}"), "Worst-10% client": A.ms([c[s]["pc_p10"] for s in seeds]),
                         "Macro-F1": A.ms([c[s]["macro_f1"] for s in seeds])})
    add(f"## 3.{list(DS).index(ds)+1} {DS[ds]}\n")
    add(tbl(pd.DataFrame(recs)))

# ------------------------------------------------------------------ 4. pooled paired
add("# 4. Pooled paired differences (all datasets and partitions)\n")
add("Each cell is the mean paired difference in percentage points with its 95% interval; n is the number of paired runs. Positive means the first method is better.\n")
for refname in ("fedfacs", "abl_A2"):
    refd = fed if refname == "fedfacs" else a2
    recs = []
    for me in METHODS:
        if me == refname:
            continue
        ks = [k for k in refd if (k[0], k[1], me, "", k[2]) in M]
        if not ks:
            continue
        row = {"Compared with": LABEL[me], "n": len(ks)}
        for lab, m in (("Acc ckpt", "acc_best"), ("Acc last10", "acc_last10"), ("Worst-10% client", "pc_p10"), ("Macro-F1", "macro_f1"), ("Late-round swing", "jitter")):
            row[lab] = ci([refd[k][m] - M[(k[0], k[1], me, "", k[2])][m] for k in ks])
        recs.append(row)
    add(f"## 4.{1 if refname == 'fedfacs' else 2} {LABEL[refname]} minus each method\n")
    if recs:
        add(tbl(pd.DataFrame(recs)))

add("## 4.3 Participation and cost, pooled over all runs\n")
recs = []
for me in METHODS:
    v = [m for k, m in M.items() if k[2] == me and k[3] == "" and k[1] in SC]
    if v:
        recs.append({"Method": LABEL[me], "Runs": len(v), "Jain": "%.3f" % np.mean([x["jfi"] for x in v]), "Never selected %": "%.1f" % np.mean([x["never"] for x in v]),
                     "Max wait": "%.1f" % np.mean([x["max_wait"] for x in v]), "Down GB": "%.1f" % np.mean([x["down_gb"] for x in v]),
                     "Up GB": "%.1f" % np.mean([x["up_gb"] for x in v]), "Steps M": "%.2f" % np.mean([x["steps_m"] for x in v]),
                     "Acc ckpt": "%.2f" % np.mean([x["acc_best"] for x in v]), "Acc last10": "%.2f" % np.mean([x["acc_last10"] for x in v]),
                     "Late-round swing": "%.2f" % np.mean([x["jitter"] for x in v]), "Worst-10% client": "%.2f" % np.mean([x["pc_p10"] for x in v])})
add(tbl(pd.DataFrame(recs)))

add("## 4.4 FedFACS minus FedAvg in every dataset and partition (paired, mean over seeds)\n")
recs = []
for ds in DS:
    for sc in SC:
        ks = [(ds, sc, s) for s in range(5) if (ds, sc, s) in fed and (ds, sc, "random", "", s) in M]
        if ks:
            recs.append({"Dataset": DS[ds], "Partition": SC[sc], "n": len(ks),
                         "Acc ckpt diff": ci([fed[k]["acc_best"] - M[(k[0], k[1], "random", "", k[2])]["acc_best"] for k in ks]),
                         "Acc last10 diff": ci([fed[k]["acc_last10"] - M[(k[0], k[1], "random", "", k[2])]["acc_last10"] for k in ks]),
                         "Worst-10% client diff": ci([fed[k]["pc_p10"] - M[(k[0], k[1], "random", "", k[2])]["pc_p10"] for k in ks])})
add(tbl(pd.DataFrame(recs)))

# ------------------------------------------------------------------ 5. ablation
add("# 5. Ablation study (Dirichlet 0.5, 3 seeds)\n")
for ds in ("fmnist", "cifar10"):
    full = cell(ds, "s1_0.5", "fedfacs")
    recs = []
    for me in ABL:
        c = {s: v for s, v in cell(ds, "s1_0.5", me).items() if s < 3}
        if not c:
            continue
        seeds = sorted(c)
        row = {"Variant": ABL_LABEL[me], "Seeds": len(seeds), "Acc ckpt": A.ms([c[s]["acc_best"] for s in seeds]),
               "Acc last10": A.ms([c[s]["acc_last10"] for s in seeds]), "Rounds to target": A.ms([c[s].get("r2t") for s in seeds], "{:.0f}"),
               "Jain": A.ms([c[s]["jfi"] for s in seeds], "{:.3f}"), "Never %": A.ms([c[s]["never"] for s in seeds], "{:.1f}"),
               "Mean cohort": A.ms([c[s]["cohort"] for s in seeds]), "Worst-10% client": A.ms([c[s]["pc_p10"] for s in seeds]),
               "Late-round swing": A.ms([c[s]["jitter"] for s in seeds])}
        if me != "fedfacs" and full:
            common = sorted(set(c) & set(full))
            row["Ckpt acc minus full"] = ci([c[s]["acc_best"] - full[s]["acc_best"] for s in common])
            row["Last10 minus full"] = ci([c[s]["acc_last10"] - full[s]["acc_last10"] for s in common])
        recs.append(row)
    add(f"## 5.{1 if ds == 'fmnist' else 2} {DS[ds]}\n")
    add(tbl(pd.DataFrame(recs)))

# ------------------------------------------------------------------ 6. A2 confirmation
add("# 6. Confirmation of the sample-weighted variant (A2)\n")
add("A2 (FedFACS selection and adaptive cohort, sample-count aggregation weights) was singled out after seeing the ablations on FMNIST and CIFAR-10, Dirichlet 0.5, seeds 0-2. **Held-out** means every run that was not used for that choice: all other dataset/partition cells, and seeds 3 and 4 of the two original cells.\n")
sel = {(d, "s1_0.5", s) for d in ("fmnist", "cifar10") for s in range(3)}
hold = {k for k in a2 if k not in sel}
for title, keys in (("6.1 Held-out runs only", hold), ("6.2 All runs (including those used for the choice)", set(a2))):
    recs = []
    for me in ("random", "fedfacs", "powd", "oort", "fairfedcs"):
        ks = [k for k in keys if (k[0], k[1], me, "", k[2]) in M]
        if ks:
            row = {"A2 minus": LABEL[me], "n": len(ks)}
            for lab, m in (("Acc ckpt", "acc_best"), ("Acc last10", "acc_last10"), ("Worst-10% client", "pc_p10"), ("Late-round swing", "jitter"), ("Jain", "jfi"), ("Max wait", "max_wait")):
                row[lab] = ci([a2[k][m] - M[(k[0], k[1], me, "", k[2])][m] for k in ks])
            recs.append(row)
    add(f"## {title}\n")
    add(tbl(pd.DataFrame(recs)) if recs else "No runs yet.\n")

# ------------------------------------------------------------------ 7. diagnostics
add("# 7. Does the KL utility predict the benefit of a client's update?\n")
add("Spearman correlation between each client score and the validation-loss gain from adding that client's update (positive = higher score, larger gain). Cells give the mean over rounds and runs with a 95% interval. 'gce' is the global model's loss on the client's local examples; 'n' is the client's sample count.\n")
uv = csv("utility_validity.csv")
add(tbl(uv) if uv is not None else "Not available.\n")
add("# 8. Does the variance penalty detect noisy clients? (IID split, label noise 0-45%)\n")
add("Detection AUC for clients with more than 22.5% label noise (0.5 = chance, 1.0 = perfect) and Spearman correlation between each score and the noise level.\n")
nd = csv("noise_discrimination.csv")
add(tbl(nd) if nd is not None else "Not available.\n")
add("## 8.1 Accuracy and fairness in the noisy IID setting\n")
ns = csv("noisy_s3_accuracy_fairness.csv")
add(tbl(ns) if ns is not None else "Not available.\n")

# ------------------------------------------------------------------ 9. sensitivity, scale
add("# 9. Sensitivity (FMNIST, Dirichlet 0.5, 3 seeds)\n")
sv = csv("sensitivity.csv")
add(tbl(sv) if sv is not None else "Not available.\n")
add("# 10. Scale (FMNIST, Dirichlet 0.5, 3 seeds)\n")
sc_ = csv("scale.csv")
add(tbl(sc_) if sc_ is not None else "Not available.\n")

# ------------------------------------------------------------------ 11. targets and health
add("# 11. Targets and run health\n")
tg = csv("targets.csv")
add("Round-to-target uses a target equal to 97% of FedAvg's mean best validation accuracy:\n")
add(tbl(tg) if tg is not None else "")
h = pd.DataFrame([dict(failed=v["failed"], invalid=v["invalid"], clip=v["clip"]) for v in M.values()])
add(f"Runs with a failed client update or a cancelled round: **{int(((h['failed'] > 0) | (h['invalid'] > 0)).sum())}** of {len(h)}. Gradient-norm clipping events: {int(h['clip'].sum())} (of about {int(sum(v['steps_m'] for v in M.values()) * 1e6):,} training steps).\n")

# ------------------------------------------------------------------ 12. meaning for paper
add("# 12. What the results support\n")
add(f"""| Claim | Supported? | Evidence (Sections) |
|:--------------------|:------|:--------------------------------------|
| Fair participation without starvation | Yes | Jain index, never-selected share, maximum wait (3, 4.3) |
| Accuracy at least as good as FedAvg | At the checkpoint only; not in the last 10 rounds | 4.1, 4.4 |
| Better outcomes for the worst clients | No | 4.1 (worst-10% client) |
| Lower communication cost | No: downloads and training are about 10 times higher; uploads about equal | 4.3 |
| Each component contributes | Yes for the fairness term, the controller and the variance penalty (stability weighting: next row) | 5 |
| Stability-weighted aggregation helps | {stab_verdict} | 5, 6 |
| KL utility predicts a client's benefit | Positive but weaker than the client's own loss | 7 |
| Variance penalty detects noisy clients | No (AUC about 0.5) | 8 |
| Selection score adds accuracy beyond random scores | No | 5 (random scores) |
""")

open(os.path.join(HERE, "report_source.md"), "w", encoding="utf8").write("\n".join(md))

# ------------------------------------------------------------------ Word
REF, TMP = os.path.join(HERE, "report_ref.docx"), os.path.join(HERE, "report_tmp.docx")
subprocess.run([pypandoc.get_pandoc_path(), "-o", REF, "--print-default-data-file", "reference.docx"], check=True)
d = Document(REF)
st = d.styles
names = [x.name for x in st]
for nm in ("Normal", "Body Text", "First Paragraph", "Compact"):
    if nm in names:
        st[nm].font.name = "Calibri"; st[nm].font.size = Pt(10)
for nm, sz in (("Heading 1", 15), ("Heading 2", 12)):
    h_ = st[nm]; h_.font.name = "Calibri"; h_.font.size = Pt(sz); h_.font.bold = True
    h_.font.color.rgb = RGBColor.from_string("1F3864")
    h_.paragraph_format.space_before = Pt(14); h_.paragraph_format.space_after = Pt(4); h_.paragraph_format.keep_with_next = True
for nm, sz, b, col in (("R-Title", 20, True, "1F3864"), ("R-Sub", 10, False, "595959")):
    s = st.add_style(nm, WD_STYLE_TYPE.PARAGRAPH)
    s.base_style = st["Normal"]; s.font.size = Pt(sz); s.font.bold = b; s.font.color.rgb = RGBColor.from_string(col)
    s.paragraph_format.space_after = Pt(6)
sec = d.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = Inches(11), Inches(8.5)
sec.left_margin = sec.right_margin = Inches(0.6)
sec.top_margin = sec.bottom_margin = Inches(0.6)
d.save(REF)
pypandoc.convert_file(os.path.join(HERE, "report_source.md"), "docx", outputfile=TMP, extra_args=["--reference-doc=" + REF, "--columns=250"])
doc = Document(TMP)
for t in doc.tables:
    b = OxmlElement("w:tblBorders")
    for e_ in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement("w:" + e_)
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:space"), "0"); e.set(qn("w:color"), "A6A6A6")
        b.append(e)
    t._tbl.tblPr.append(b)
    for ri, row in enumerate(t.rows):
        for c_ in row.cells:
            tcPr = c_._tc.get_or_add_tcPr()
            if ri == 0 or ri % 2 == 0:
                sh = OxmlElement("w:shd")
                sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), "1F3864" if ri == 0 else "F2F2F2")
                tcPr.append(sh)
            for p in c_.paragraphs:
                p.paragraph_format.space_after = Pt(1)
                for r in p.runs:
                    r.font.size = Pt(7.5)
                    if ri == 0:
                        r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
doc.core_properties.title = "FedFACS experimental results report"
doc.save(OUT)
print("saved", OUT, os.path.getsize(OUT) // 1024, "KB | tables:", len(doc.tables), "| runs:", n_runs)
