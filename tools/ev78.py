"""Evidence for Replacements 7 (cohort) and 8 (aggregation), computed from the reproduced runs only."""
import collections
import glob
import json
import os

import numpy as np

R = r"C:\Users\0xRay\Downloads\paper\fedfacs_repro\results"
rng = np.random.default_rng(0)


def boot(x, n=4000):
    x = np.array(x, float)
    b = [rng.choice(x, len(x)).mean() for _ in range(n)]
    return x.mean(), np.percentile(b, 2.5), np.percentile(b, 97.5)


def load(pat):
    return [json.load(open(f)) for f in sorted(glob.glob(os.path.join(R, pat)))]


A2 = load("*_abl_A2_s*.json")
FF = load("*_fedfacs_s*.json")
print("A2 runs", len(A2), "FedFACS runs", len(FF))
for name, rs in (("A2", A2), ("FedFACS", FF)):
    m = [np.mean(r["log"]["cohort"]) for r in rs]
    mean, lo, hi = boot(m)
    print(name, "mean cohort %.2f [%.2f, %.2f]  saving vs 10: %.1f%% [%.1f, %.1f]" % (mean, lo, hi, 100 * (1 - mean / 10), 100 * (1 - hi / 10), 100 * (1 - lo / 10)))
    allc = np.concatenate([r["log"]["cohort"] for r in rs]).astype(int)
    print("  histogram of m_t (0..10):", np.bincount(allc, minlength=11).tolist(), " min", allc.min(), " cmin cfg", set(r["cfg"]["cmin"] for r in rs))
    print("  rounds with m_t=cmax: %.0f%%" % (100 * (allc == 10).mean()))
    print("  invalid rounds:", sum(r["invalid_rounds"] for r in rs), " failed updates:", sum(r["failed_updates"] for r in rs))
# per scenario A2
S = collections.defaultdict(list)
for r in A2:
    c = r["cfg"]
    S[(c["dataset"], c["scenario"])].append(np.mean(r["log"]["cohort"]))
print("per cell A2 mean cohort:", {k: round(float(np.mean(v)), 2) for k, v in sorted(S.items())})
# rounds with cohort below 8 in FedFACS (where and why)
low = [(r["cfg"]["dataset"], r["cfg"]["scenario"], r["cfg"]["seed"], int(min(r["log"]["cohort"])), r["failed_updates"]) for r in FF if min(r["log"]["cohort"]) < r["cfg"]["cmin"]]
print("FedFACS runs with a round below cmin:", len(low), low[:5])
# weights
wm = [min(r["log"]["weights_min"]) for r in FF]
print("min aggregation weight, FedFACS (stability): %.3g ; A2: %.3g" % (min(wm), min(min(r["log"]["weights_min"]) for r in A2)))
# cumulative aggregation influence under sample-count weights (A2): sum over rounds of n_i / sum n_sel
def influence(r):
    n = np.array(r["n"], float)
    infl = np.zeros(len(n))
    for sel in r["log"]["selected"]:
        sel = list(sel)
        if not sel:
            continue
        infl[sel] += n[sel] / n[sel].sum()
    return infl


def gini(x):
    x = np.sort(np.asarray(x, float))
    n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))


rows = []
for r in A2:
    i = influence(r)
    rows.append((np.mean(i == 0) * 100, i.min() / i.mean(), i.max() / i.mean(), gini(i)))
rows = np.array(rows)
print("A2 cumulative aggregation influence: share of clients with zero influence %.2f%%, min/mean %.2f, max/mean %.2f, Gini %.3f" % tuple(rows.mean(0)))
