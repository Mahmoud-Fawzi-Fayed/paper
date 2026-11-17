import os
import shutil

P = r"C:\Users\0xRay\Downloads\paper"
PT = os.path.join(P, "paper_overleaf_revised")
B = chr(92)

TEX = [
    ("which is larger in magnitude, so that clients are first grouped by how long they have waited and the KL score orders the clients within each group. Among clients with similar waiting times, those whose updates are more informative are therefore preferred",
     "which is larger in magnitude and is weighted by $1-a_i^t$, so that the priority is determined mainly by how long clients have waited and the KL score orders the clients with similar waiting times. Among such clients, those whose updates are more informative are therefore preferred"),
    ("would place clients with corrupted labels first within each group, whereas the KL score does not.",
     "would place clients with corrupted labels first among clients with similar waiting times, whereas the KL score does not."),
    ("Since $F_i^t \\ge 1$ while $\\Delta KL_i^t$ is typically much smaller than one, the priority is fairness-first by design: clients are grouped by waiting time and the utility term orders the clients within each group, so that no client is excluded by a low utility.",
     "Since $F_i^t \\ge 1$ and the feedback rule keeps the mixing coefficient small, the priority is determined mainly by the fairness term: the utility term orders the clients with similar waiting times, so that no client is excluded by a low utility."),
    ("Because $F_i^t\\ge 1$ while $\\Delta KL_i^t$ is typically much smaller than one, the priority of Eq.~(9) is fairness-first: clients are grouped by waiting time and the utility term orders the clients within a group.",
     "At the diagnostic rounds 5 to 100 the fairness term has a median of 1.88 and the utility score $\\Delta KL_i^t$ a median of 0.73, and the coefficients have a median of 0.10 (below). The weighted utility term $a_i^t\\Delta KL_i^t$ is therefore a median 3\\% of $(1-a_i^t)F_i^t$, the priority of Eq.~(9) is rank-correlated with $F_i^t$ (Spearman 0.92 against 0.27 for $\\Delta KL_i^t$), and 98.9\\% of the selected clients have a fairness term above the median: the priority is determined mainly by the waiting time, and the utility term orders the clients with similar waiting times."),
]
for f in ("sn-article.tex", "section_5_4_selection_score.tex"):
    p = os.path.join(PT, f)
    t = open(p, encoding="utf8", newline="").read()
    shutil.copy(p, p.replace(".tex", "_before_scale.tex"))
    for a, b in TEX:
        n = t.count(a)
        print(f, n, a[:50])
        if n:
            t = t.replace(a, b)
    open(p, "w", encoding="utf8", newline="").write(t)

p = os.path.join(P, "tools", "build_final56.py")
t = open(p, encoding="utf8").read()
R = [
    ("The priority of Eq. (9) is stated as fairness-first by design: F ≥ 1 groups clients by waiting time and the utility term orders clients within a group. Two alternatives with comparable weights were implemented and evaluated.",
     "The priority of Eq. (9) is stated with the quantities that determine it: at the diagnostic rounds the fairness term has a median of 1.88, the utility score 0.73 and the coefficient 0.10, so that the weighted utility term is a median 3% of the weighted fairness term and the priority is rank-correlated with F (Spearman 0.92). Two alternatives with comparable weights were implemented and evaluated."),
    ("The fairness-first regime is the configuration that preserves near-uniform participation at the highest accuracy; the feedback rule reaches it without tuning the coefficient.",
     "The regime in which the priority is determined mainly by the waiting time is the configuration that preserves near-uniform participation at the highest accuracy; the feedback rule reaches it without tuning the coefficient."),
    ("- **Why is the utility term small?** The priority is fairness-first by design: waiting time groups the clients and the utility term orders them inside a group. A comparable weight (a constant of 0.5, or rank normalisation) lowered the Jain index and did not raise accuracy (Table Y).",
     "- **Is the utility term small?** The score itself is not (median 0.73, against 1.88 for F); its weighted contribution is, because the feedback rule keeps the coefficient at a median of 0.10: a·ΔKL is a median 3% of (1−a)·F, and the priority is rank-correlated with F (0.92). A comparable weight (a constant of 0.5, or rank normalisation) lowered the Jain index and did not raise accuracy (Table Y)."),
    ("- **Why is the utility term small?** By design the priority is fairness-first (Section 5.4). The utility term orders clients within a waiting group; a comparable weight lowered the Jain index and did not raise accuracy.",
     "- **Is the utility term small?** Its weighted contribution is (a·ΔKL is a median 3% of (1−a)·F, Section 5.4); the utility term orders clients with similar waiting times, and a comparable weight lowered the Jain index and did not raise accuracy."),
]
for a, b in R:
    print("builder", t.count(a), a[:50])
    t = t.replace(a, b)
open(p, "w", encoding="utf8").write(t)

# verification: replace K1 by the facts the text now states
p = os.path.join(P, "tools", "verify_claims.py")
t = open(p, encoding="utf8").read()
i = t.index('K1 = "median')
j = t.index("def _auc(score, lab):")
new = '''from scipy.stats import spearmanr as _sp  # noqa: E402

rhoPF, rhoPK, shr, A_, ratio = [], [], [], [], []
for r in sel("fedfacs", base=True):
    for rd, bl in (r.get("diag") or {}).items():
        if int(rd) < 5:
            continue
        kl = np.array([x["kl"] for x in bl]); F = np.array([x["F"] for x in bl]); a_ = np.array([x["a"] for x in bl])
        P_ = a_ * kl + (1 - a_) * F
        rhoPF.append(_sp(P_, F)[0]); rhoPK.append(_sp(P_, kl)[0])
        s_ = list(r["log"]["selected"][int(rd) - 1]); shr.append(np.mean(F[s_] >= np.median(F)))
        A_ += list(a_); ratio += list((a_ * kl) / ((1 - a_) * F))
add("K1", "5.4 Mixing", "median fairness term / median utility score / median coefficient at rounds 5-100 (FedFACS main runs)", "1.88 / 0.73 / 0.10", "%.2f / %.2f / %.2f" % (np.median(F_), np.median(kl_), np.median(A_)), "%.2f / %.2f / %.2f" % (np.median(F_), np.median(kl_), np.median(A_)) == "1.88 / 0.73 / 0.10", "results/*_fedfacs_s*.json (diag records, 51 runs)")
add("K3", "5.4 Mixing", "Spearman of the priority with F / with the utility score; selected clients above median F; median a*KL/((1-a)*F)", "0.92 / 0.27 / 98.9% / 3%", "%.2f / %.2f / %.1f%% / %.0f%%" % (np.mean(rhoPF), np.mean(rhoPK), 100 * np.mean(shr), 100 * np.median(ratio)), "%.2f / %.2f / %.1f%% / %.0f%%" % (np.mean(rhoPF), np.mean(rhoPK), 100 * np.mean(shr), 100 * np.median(ratio)) == "0.92 / 0.27 / 98.9% / 3%", "results/*_fedfacs_s*.json (diag records, log selected)")

'''
t = t[:i] + new + t[j:]
open(p, "w", encoding="utf8").write(t)
