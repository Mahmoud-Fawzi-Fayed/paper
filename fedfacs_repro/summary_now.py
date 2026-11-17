"""Pooled, paired summary of FedFACS vs each baseline over all (dataset, scenario, seed) cells that exist."""
import numpy as np
import analyze as A

rows = A.load()
base = [x for x in rows if x[4] == "" and x[1] in ("s1_0.1", "s1_0.5", "s2")]
M = {}
for ds, sc, me, seed, tag, r in base:
    M[(ds, sc, me, seed)] = A.run_metrics(r)
fed = {k[:2] + (k[3],): v for k, v in M.items() if k[2] == "fedfacs"}
print("FedFACS runs:", len(fed), "| cells:", sorted({k[:2] for k in fed}))
rng = np.random.default_rng(0)


def ci(d):
    d = np.asarray(d, float)
    b = rng.choice(d, (10000, len(d))).mean(1)
    return d.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5)


print("\nPaired FedFACS minus baseline, pooled over all paired runs (95% bootstrap CI)")
print("%-9s %4s | %-26s | %-26s | %-24s | %-22s" % ("baseline", "n", "acc_best (ckpt, pts)", "acc_last10 (pts)", "worst-10% client acc", "macro-F1"))
for me in ["random", "fedprox", "fednova", "qffl", "powd", "oort", "divfl"]:
    keys = [k for k in fed if (k[0], k[1], me, k[2]) in M]
    if not keys:
        continue
    out = []
    for m in ("acc_best", "acc_last10", "pc_p10", "macro_f1"):
        d = [fed[k][m] - M[(k[0], k[1], me, k[2])][m] for k in keys]
        mu, lo, hi = ci(d)
        out.append("%+.2f [%+.2f,%+.2f]" % (mu, lo, hi))
    print("%-9s %4d | %-26s | %-26s | %-24s | %-22s" % (me, len(keys), *out))

print("\nCell-level wins on checkpoint accuracy (mean over seeds, FedFACS > baseline):")
cells = sorted({k[:2] for k in fed})
for me in ["random", "fedprox", "fednova", "qffl", "powd", "oort", "divfl"]:
    w = 0; n = 0
    for c in cells:
        a = [fed[c + (s,)]["acc_best"] for s in range(5) if c + (s,) in fed and (c[0], c[1], me, s) in M]
        b = [M[(c[0], c[1], me, s)]["acc_best"] for s in range(5) if c + (s,) in fed and (c[0], c[1], me, s) in M]
        if a:
            n += 1; w += np.mean(a) > np.mean(b)
    print("  vs %-8s: %d of %d cells" % (me, w, n))

print("\nParticipation and cost (mean over runs):")
for me in ["random", "fedprox", "powd", "oort", "divfl", "fedfacs"]:
    v = [m for k, m in M.items() if k[2] == me]
    print("  %-8s n=%3d | JFI %.3f | never-selected %5.1f%% | max wait %5.1f rounds | download %6.1f GB | train steps %.2fM | acc_best %.2f | acc_last10 %.2f | late-round swing %.2f pts"
          % (me, len(v), np.mean([x["jfi"] for x in v]), np.mean([x["never"] for x in v]), np.mean([x["max_wait"] for x in v]),
             np.mean([x["down_gb"] for x in v]), np.mean([x["steps_m"] for x in v]), np.mean([x["acc_best"] for x in v]),
             np.mean([x["acc_last10"] for x in v]), np.mean([x["jitter"] for x in v])))

# fairness gap to the best accuracy-neutral baseline: starvation = clients never selected
print("\nBest single settings for FedFACS (acc_best, paired vs random, per cell, mean over seeds):")
for c in cells:
    keys = [c + (s,) for s in range(5) if c + (s,) in fed and (c[0], c[1], "random", s) in M]
    d = [fed[k]["acc_best"] - M[(k[0], k[1], "random", k[2])]["acc_best"] for k in keys]
    p = [fed[k]["pc_p10"] - M[(k[0], k[1], "random", k[2])]["pc_p10"] for k in keys]
    print("  %-8s %-7s n=%d  acc %+5.2f   worst-10%%-client %+6.2f" % (c[0], c[1], len(keys), np.mean(d), np.mean(p)))
