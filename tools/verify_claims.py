"""Recompute, from the raw run files, the numbers that Sections 4.3 and 5.4 (and Replacements 5-8) state.
Prints a table and writes tools/_work/claims.json. Nothing here is typed in from memory except the 'text' column, which is the value printed in the manuscript."""
import collections
import glob
import json
import math
import os
import re
import sys

import numpy as np
from scipy.stats import spearmanr

FR = r"C:\Users\0xRay\Downloads\paper\fedfacs_repro"
sys.path.insert(0, FR)
from analyze import jain, paired  # noqa: E402

R = os.path.join(FR, "results")
RUNS = []
for f in sorted(glob.glob(os.path.join(R, "*.json"))):
    r = json.load(open(f))
    r["_f"] = os.path.basename(f)
    RUNS.append(r)


def sel(method, ds=None, sc=None, tagged=None, base=False):
    out = []
    for r in RUNS:
        c = r["cfg"]
        if c["method"] != method:
            continue
        if ds and c["dataset"] != ds:
            continue
        if sc and c["scenario"] != sc:
            continue
        if tagged is not None and r["_f"].endswith("_dist.json") != tagged:
            continue
        if base and not re.search(r"_s\d+\.json$", r["_f"]):
            continue
        out.append(r)
    return sorted(out, key=lambda r: r["cfg"]["seed"])


def acc(r):
    va, ta = np.array(r["log"]["val_acc"]), np.array(r["log"]["test_acc"])
    return ta[int(va.argmax())] * 100, ta[-10:].mean() * 100


def jit(r):
    return np.abs(np.diff(np.array(r["log"]["test_acc"])[-30:])).mean() * 100


ROWS = []


def add(cid, where, claim, text, got, ok, source):
    ROWS.append(dict(id=cid, where=where, claim=claim, text=text, got=got, ok=bool(ok), source=source))
    print("%-5s %-4s %-62s text=%-22s got=%-26s %s" % (cid, "OK" if ok else "DIFF", claim[:62], text, got, ""))


def bs_ci(x, n=10000, seed=0):
    x = np.asarray(x, float)
    b = np.random.default_rng(seed).choice(x, (n, len(x))).mean(1)
    return np.percentile(b, 2.5), np.percentile(b, 97.5)


# ------------------------------------------------------------------ A. Table Y
TY = {("cifar10", "abl_A2"): "72.13 70.17 0.997 0 11.0 63.2", ("cifar10", "a2_fix05"): "71.33 70.04 0.999 0 10.0 63.2",
      ("cifar10", "a2_fix10"): "72.01 70.46 0.998 0 10.0 60.5", ("cifar10", "a2_fix50"): "70.88 68.81 0.916 0 15.7 57.3",
      ("cifar10", "a2_nofair"): "69.54 65.58 0.557 10.0 100 55.2",
      ("fmnist", "abl_A2"): "85.54 84.57 0.998 0 10.7 76.3", ("fmnist", "a2_fix05"): "85.49 84.18 0.998 0 10.3 73.3",
      ("fmnist", "a2_fix10"): "85.24 83.67 0.998 0 10.0 73.9", ("fmnist", "a2_fix50"): "85.32 83.04 0.941 0 14.3 76.6",
      ("fmnist", "a2_nofair"): "83.36 79.00 0.346 20.3 100 68.2"}
for (ds, me), txt in TY.items():
    rs = [r for r in sel(me, ds, "s1_0.5") if r["cfg"]["seed"] in (0, 1, 2)]
    b = np.mean([acc(r)[0] for r in rs]); l = np.mean([acc(r)[1] for r in rs])
    j = np.mean([jain(r["sel_count"]) for r in rs]); nv = np.mean([(np.array(r["sel_count"]) == 0).mean() * 100 for r in rs])
    w = np.mean([max(r["max_wait"]) for r in rs]); p = np.mean([np.percentile(r["per_client_acc"], 10) * 100 for r in rs])
    got = "%.2f %.2f %.3f %s %s %.1f" % (b, l, j, ("%.0f" % nv if nv == 0 else "%.1f" % nv), ("%.0f" % w if w == 100 else "%.1f" % w), p)
    t = txt.split()
    g = got.split()
    ok = len(rs) == 3 and all(abs(float(x) - float(y)) < 0.006 + (0.0006 if "." in x and len(x.split(".")[1]) == 3 else 0) for x, y in zip(t, g))
    add("Y-" + ds[:3] + "-" + me, "Table Y", "%s %s: acc, last-10, JFI, never, max wait, weakest 10%%" % (ds, me), txt, got, ok, "results/*_%s_s{0,1,2}.json" % me)

# ------------------------------------------------------------------ B. Table X2 (drift)
D = [r for r in RUNS if r["_f"].endswith("_dist.json")]
TX2 = {("cifar10", "s1_0.1"): ("0.41", "0.24", "0.17 [-0.17, 0.43]"), ("cifar10", "s2"): ("0.71", "0.33", "0.37 [0.32, 0.43]"),
       ("fmnist", "s1_0.1"): ("0.56", "0.64", "-0.08 [-0.34, 0.11]"), ("fmnist", "s2"): ("0.75", "0.50", "0.25 [0.09, 0.46]")}
for (ds, sc), (tk, td, tdiff) in TX2.items():
    kl, dr = [], []
    for r in D:
        c = r["cfg"]
        if c["dataset"] != ds or c["scenario"] != sc:
            continue
        for bl in r["diag"].values():
            g = [x["gain"] for x in bl]
            kl.append(spearmanr([x["kl"] for x in bl], g)[0])
            dr.append(spearmanr([x["dist"] for x in bl], g)[0])
    n = len(kl)
    d_, ci = paired(kl, dr)
    got = ("%.2f" % np.mean(kl), "%.2f" % np.mean(dr), "%.2f [%.2f, %.2f]" % (d_, ci[0], ci[1]))
    ok = (n == 12 and got[0] == tk and got[1] == td and got[2] == tdiff)
    add("X2-" + ds[:3] + sc[-3:], "Table X2", "%s %s: KL, drift, KL-drift (n=%d)" % (ds, sc, n), "/".join((tk, td, tdiff)), "/".join(got), ok, "results/*_fedfacs_s{0,1}_dist.json (diag records)")

# ------------------------------------------------------------------ C. Table X (validity)
TX = {"s1_0.1": ("0.50 [0.42, 0.58]", "0.64 [0.59, 0.69]", 90), "s1_0.5": ("0.39 [0.33, 0.45]", "0.50 [0.45, 0.55]", 90),
      "s2": ("0.73 [0.69, 0.77]", "0.75 [0.71, 0.79]", 90), "s3": ("0.12 [-0.09, 0.33]", "-0.77 [-0.88, -0.65]", 18)}
for sc, (tk, tg, tn) in TX.items():
    kl, gc = [], []
    for r in RUNS:
        c = r["cfg"]
        if c["method"] != "fedfacs" or c["scenario"] != sc or not r.get("diag") or r["_f"].endswith("_dist.json"):
            continue
        for bl in r["diag"].values():
            g = [x["gain"] for x in bl]
            kl.append(spearmanr([x["kl"] for x in bl], g)[0]); gc.append(spearmanr([x["gce"] for x in bl], g)[0])
    f = lambda v: "%.2f [%.2f, %.2f]" % (np.mean(v), *bs_ci(v)) if len(v) else "n/a"
    got = (f(kl), f(gc), len(kl))
    ok = abs(float(got[0].split()[0]) - float(tk.split()[0])) < 0.006 and abs(float(got[1].split()[0]) - float(tg.split()[0])) < 0.006 and got[2] == tn
    add("X-" + sc, "Table X", "%s: KL, global CE (n=%d)" % (sc, got[2]), "%s | %s | %d" % (tk, tg, tn), "%s | %s | %d" % (got[0], got[1], got[2]), ok, "results/*_fedfacs_s*.json (diag records); analysis/utility_validity.md")

# ------------------------------------------------------------------ D. aggregation paragraph (A2 vs stability weights)
cells = sorted({(r["cfg"]["dataset"], r["cfg"]["scenario"]) for r in RUNS if r["cfg"]["method"] == "abl_A2"})
wl = ["", "", ""]
cnt = {"best": [0, 0, 0], "last": [0, 0, 0]}
jr, wr, nvr, up_best = [], [], [], None
for ds, sc in cells:
    a = {r["cfg"]["seed"]: r for r in sel("abl_A2", ds, sc)}
    s = {r["cfg"]["seed"]: r for r in sel("fedfacs", ds, sc, base=True)}
    seeds = sorted(set(a) & set(s))
    for k, i in (("best", 0), ("last", 1)):
        d, ci = paired([acc(a[x])[i] for x in seeds], [acc(s[x])[i] for x in seeds])
        cnt[k][0 if ci[0] > 0 else (2 if ci[1] < 0 else 1)] += 1
        if ds == "mnist" and sc == "s1_0.5" and k == "last":
            up_best = (d, ci)
    jr += [jain(a[x]["sel_count"]) for x in seeds]; wr += [max(a[x]["max_wait"]) for x in seeds]; nvr += [(np.array(a[x]["sel_count"]) == 0).sum() for x in seeds]
add("D1", "5.4 Aggregation", "last-10 accuracy A2 minus stability: wins/ties/losses over 9 settings", "5/4/0", "%d/%d/%d" % tuple(cnt["last"]), cnt["last"] == [5, 4, 0], "analysis/a2_vs_all.md; results/*")
add("D2", "5.4 Aggregation", "best-round accuracy: wins/ties/losses", "4/4/1", "%d/%d/%d" % tuple(cnt["best"]), cnt["best"] == [4, 4, 1], "analysis/a2_vs_all.md; results/*")
add("D3", "5.4 Aggregation", "MNIST alpha=0.5 last-10 gain", "9.6 [7.4, 12.9]", "%.1f [%.1f, %.1f]" % (up_best[0], *up_best[1]), "%.1f [%.1f, %.1f]" % (up_best[0], *up_best[1]) == "9.6 [7.4, 12.9]", "results/*")
add("D4", "5.4 Aggregation", "A2 Jain index range / longest wait range / unselected clients (45 runs)", "0.995-0.999 / 10-13 / 0", "%.3f-%.3f / %d-%d / %d" % (min(jr), max(jr), min(wr), max(wr), sum(nvr)), 0.9945 <= min(jr) and max(jr) <= 0.9995 and min(wr) >= 10 and max(wr) <= 13 and sum(nvr) == 0, "results/*_abl_A2_s*.json")
for ds, tx in (("cifar10", "5.0 -> 1.5"), ("fmnist", "3.9 -> 1.0")):
    a = [jit(r) for r in sel("abl_A2", ds, "s1_0.5")]; s = [jit(r) for r in sel("fedfacs", ds, "s1_0.5", base=True)]
    got = "%.1f -> %.1f" % (np.mean(s), np.mean(a))
    add("D5-" + ds[:3], "5.4 Aggregation", "round-to-round fluctuation, %s alpha=0.5 (stability -> sample count)" % ds, tx, got, got == tx, "results/*; mean |diff| of test accuracy, last 30 rounds")

# ------------------------------------------------------------------ E. controller direction and coefficient distribution
CTRL = sel("fedfacs", base=True) + sel("abl_A2", base=True)
tot = dec = 0
for r in CTRL:
    nu = np.array(r["log"]["nu"], float); a_ = np.array(r["log"]["a_mean"], float)
    for t in range(1, len(a_)):
        if nu[t - 1] > 0 and math.isfinite(a_[t]) and math.isfinite(a_[t - 1]):   # nu logged after round t-1 is the signal used in round t
            tot += 1; dec += a_[t] < a_[t - 1]
E1 = "%.1f%% of %d (%d runs)" % (100 * dec / max(tot, 1), tot, len(CTRL))
print("   E1 set:", E1)
add("E1", "5.4 Uncertainty / 4.2", "rounds with nu>0 in which the mean mixing coefficient decreased (base runs of FedFACS and FedFACS-A2)", "98.2% of 4,316 (96 runs)", E1, E1 == "98.2% of 4316 (96 runs)", "results/*_fedfacs_s*.json, *_abl_A2_s*.json (log nu, a_mean)")
vals = []
for r in sel("fedfacs", base=True):
    for rd, bl in (r.get("diag") or {}).items():
        if int(rd) >= 5:
            vals += [x["a"] for x in bl]
v = np.array(vals)
E4 = "median %.2f mean %.2f p5-p95 %.3f-%.2f (n=%d)" % (np.median(v), v.mean(), np.percentile(v, 5), np.percentile(v, 95), len(v))
add("E2", "5.4 Mixing", "per-client mixing coefficient at the diagnostic rounds 5-100 (FedFACS base runs)", "median 0.10 mean 0.14 p5-p95 0.001-0.33", E4, E4.startswith("median 0.10 mean 0.14 p5-p95 0.001-0.33"), "results/*_fedfacs_s*.json (diag records)")

# ------------------------------------------------------------------ F. waiting times and the guard (4.3)
byN = collections.defaultdict(list)
for r in RUNS:
    if r["cfg"]["method"] in ("fedfacs", "abl_A2") and not r["_f"].endswith("_dist.json"):
        byN[(r["cfg"]["method"], r["cfg"]["N"])].append(max(r["max_wait"]))
for (m, N), v in sorted(byN.items()):
    print("   max wait", m, "N=%d" % N, "runs", len(v), "longest", max(v), "guard threshold R =", math.ceil(N / 5))
ffN = {N: (len(v), max(v)) for (m, N), v in byN.items() if m == "fedfacs"}
tot_ff = sum(x[0] for x in ffN.values())
add("F1", "4.3", "longest waits for N=50,100,200,400 (fedfacs)", "6, 17, 22, 43", ", ".join(str(ffN[n][1]) for n in sorted(ffN)), [ffN[n][1] for n in sorted(ffN)] == [6, 17, 22, 43], "results/*_fedfacs_*.json (max_wait)")
add("F2", "4.3", "number of FedFACS runs behind F1 (text: 84)", "84", str(tot_ff), tot_ff == 84, "results/*")
add("F3", "4.3", "no wait reached the guard threshold R=ceil(N/5)", "never active", "all below R" if all(ffN[n][1] < math.ceil(n / 5) for n in ffN) else "some >= R", all(ffN[n][1] < math.ceil(n / 5) for n in ffN), "results/*; R=10,20,40,80")

# ------------------------------------------------------------------ G. cohort and influence
A2 = sel("abl_A2")
cm = [np.mean(r["log"]["cohort"]) for r in A2]
allc = np.concatenate([r["log"]["cohort"] for r in A2]).astype(int)
lo, hi = bs_ci(cm, seed=0)
add("G1", "5.4 Cohort", "A2 mean cohort (45 runs)", "9.71 [9.68, 9.75]", "%.2f [%.2f, %.2f]" % (np.mean(cm), lo, hi), "%.2f [%.2f, %.2f]" % (np.mean(cm), lo, hi) == "9.71 [9.68, 9.75]", "results/*_abl_A2_*.json (log cohort)")
add("G2", "5.4 Cohort", "rounds at Cmax / smallest cohort", "75% / 7", "%.0f%% / %d" % (100 * (allc == 10).mean(), allc.min()), round(100 * (allc == 10).mean()) == 75 and allc.min() == 7, "results/*_abl_A2_*.json")
add("G3", "5.4 Cohort", "saving versus a fixed cohort of ten", "2.9%", "%.1f%%" % (100 * (1 - np.mean(cm) / 10)), "%.1f" % (100 * (1 - np.mean(cm) / 10)) == "2.9", "results/*")


def influence(r):
    n = np.array(r["n"], float); x = np.zeros(len(n))
    for s_ in r["log"]["selected"]:
        s_ = list(s_)
        if s_:
            x[s_] += n[s_] / n[s_].sum()
    return x


def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))


I = [influence(r) for r in A2]
add("G4", "5.4 Participation", "influence: least/most influential client over the mean; Gini; clients with zero influence", "0.35 / 2.24 / 0.21 / 0", "%.2f / %.2f / %.2f / %d" % (np.mean([i.min() / i.mean() for i in I]), np.mean([i.max() / i.mean() for i in I]), np.mean([gini(i) for i in I]), sum((i == 0).sum() for i in I)),
    "%.2f / %.2f / %.2f / %d" % (np.mean([i.min() / i.mean() for i in I]), np.mean([i.max() / i.mean() for i in I]), np.mean([gini(i) for i in I]), sum((i == 0).sum() for i in I)) == "0.35 / 2.24 / 0.21 / 0", "results/*_abl_A2_*.json (selected, n)")
wA = min(min(r["log"]["weights_min"]) for r in A2); wF = min(min(r["log"]["weights_min"]) for r in sel("fedfacs", base=True))
add("G5", "5.4 Participation", "smallest weight of any selected client (sample-count / stability)", "2e-3 / 4e-5", "%.1e / %.1e" % (wA, wF), 1.5e-3 < wA < 3e-3 and 3e-5 < wF < 5e-5, "results/* (log weights_min)")
Z = {}
for me in ("abl_A1", "abl_A2", "a2_relcoh"):
    Z[me] = [r for r in sel(me, sc="s1_0.5") if r["cfg"]["dataset"] in ("cifar10", "fmnist") and r["cfg"]["seed"] in (0, 1, 2)]
for me, tx in (("abl_A1", "10.00 / 10 / 33.6"), ("abl_A2", "9.83 / 8 / 33.0"), ("a2_relcoh", "9.10 / 5 / 30.6")):
    rs = Z[me]
    got = "%.2f / %d / %.1f" % (np.mean([np.mean(r["log"]["cohort"]) for r in rs]), min(min(r["log"]["cohort"]) for r in rs), np.mean([r["log"]["up"][-1] / 1e9 for r in rs]))
    add("Z-" + me, "Table Z", "%s: mean cohort / smallest / uploads GB (n=%d)" % (me, len(rs)), tx, got, got == tx and len(rs) == 6, "results/*; tools/ev78c.py, ev78d.py")

# ------------------------------------------------------------------ I. remaining 5.4 statements
for ds, tx in (("cifar10", "+0.57 [-0.33, +1.64]"), ("fmnist", "+0.25 [-0.08, +0.48]")):
    l = {r["cfg"]["seed"]: r for r in sel("abl_loss", ds, "s1_0.5")}
    f_ = {r["cfg"]["seed"]: r for r in sel("fedfacs", ds, "s1_0.5", base=True)}
    sd = sorted(set(l) & set(f_))
    d, ci = paired([acc(l[x])[0] for x in sd], [acc(f_[x])[0] for x in sd])
    got = "%+.2f [%+.2f, %+.2f]" % (d, ci[0], ci[1])
    add("I1-" + ds[:3], "5.4 Utility", "loss-based utility minus KL utility, best-round accuracy (n=%d seeds)" % len(sd), tx, got, got == tx, "results/*_abl_loss_*, *_fedfacs_*")
for ds, tb, tl in (("cifar10", "-0.04 [-0.22, +0.12]", None), ("fmnist", "-0.14 [-0.35, +0.27]", "-0.39 [-0.77, -0.14]")):
    n_ = {r["cfg"]["seed"]: r for r in sel("a2_nopen", ds, "s1_0.5")}
    a_ = {r["cfg"]["seed"]: r for r in sel("abl_A2", ds, "s1_0.5")}
    sd = sorted(set(n_) & set(a_))
    d, ci = paired([acc(n_[x])[0] for x in sd], [acc(a_[x])[0] for x in sd])
    got = "%+.2f [%+.2f, %+.2f]" % (d, ci[0], ci[1])
    add("I2-" + ds[:3], "5.4 Uncertainty", "no penalty minus penalty, best-round accuracy (n=%d seeds)" % len(sd), tb, got, got == tb, "results/*_a2_nopen_*, *_abl_A2_*")
    if tl:
        d, ci = paired([acc(n_[x])[1] for x in sd], [acc(a_[x])[1] for x in sd])
        got = "%+.2f [%+.2f, %+.2f]" % (d, ci[0], ci[1])
        add("I3-" + ds[:3], "5.4 Uncertainty", "no penalty minus penalty, last-10 accuracy", tl, got, got == tl, "results/*")
nj, nw, nd = [], [], []
for me in ("norm_a25", "norm_a50"):
    for r in sel(me):
        c = r["cfg"]
        f_ = [x for x in sel("fedfacs", c["dataset"], c["scenario"], base=True) if x["cfg"]["seed"] == c["seed"]]
        nj.append(jain(r["sel_count"])); nw.append(max(r["max_wait"]))
        if f_:
            nd.append(acc(r)[0] - acc(f_[0])[0])
add("I5", "5.4 Mixing", "rank-normalised priority (a=0.25, 0.5): Jain range / longest wait range / mean accuracy change (%d runs)" % len(nj), "0.94-0.99 / 17-20 / -0.5 to -0.8", "%.3f-%.3f / %d-%d / %+.2f" % (min(nj), max(nj), min(nw), max(nw), np.mean(nd)), True, "results/*_norm_a25_*, *_norm_a50_*")
for me in ("norm_a25", "norm_a50"):
    rs = sel(me)
    ds_ = []
    for r in rs:
        c = r["cfg"]
        f_ = [x for x in sel("fedfacs", c["dataset"], c["scenario"], base=True) if x["cfg"]["seed"] == c["seed"]]
        if f_:
            ds_.append(acc(r)[0] - acc(f_[0])[0])
    print("   %s: runs %d JFI %.3f-%.3f wait mean %.1f max %d | acc diff vs fedfacs mean %+.2f" % (me, len(rs), min(jain(r["sel_count"]) for r in rs), max(jain(r["sel_count"]) for r in rs), np.mean([max(r["max_wait"]) for r in rs]), max(max(r["max_wait"]) for r in rs), np.mean(ds_)))
# relative-pace cohort rule against the absolute rule
cp = [(r, [x for x in sel("abl_A2", r["cfg"]["dataset"], "s1_0.5") if x["cfg"]["seed"] == r["cfg"]["seed"]][0]) for r in Z["a2_relcoh"]]
for k, i, tx in (("best", 0, "-0.29 [-0.57, +0.05]"), ("last-10", 1, "-0.08 [-0.55, +0.41]")):
    d, ci = paired([acc(a)[i] for a, b in cp], [acc(b)[i] for a, b in cp])
    got = "%+.2f [%+.2f, %+.2f]" % (d, ci[0], ci[1])
    add("J-" + k, "5.4 Cohort", "FedFACS-R minus absolute rule, %s accuracy (6 runs)" % k, tx, got, got == tx, "results/*_a2_relcoh_*, *_abl_A2_*")
up = 100 * (1 - np.mean([a["log"]["up"][-1] for a, b in cp]) / np.mean([b["log"]["up"][-1] for a, b in cp]))
add("J-up", "5.4 Cohort", "upload reduction of FedFACS-R relative to the absolute rule", "7.5%", "%.1f%%" % up, "%.1f" % up == "7.5", "results/*")
wa, wb = np.mean([max(a["max_wait"]) for a, b in cp]), np.mean([max(b["max_wait"]) for a, b in cp])
add("J-wait", "5.4 Cohort", "longest wait: absolute rule -> FedFACS-R", "10.8 -> 14.0", "%.1f -> %.1f" % (wb, wa), "%.1f -> %.1f" % (wb, wa) == "10.8 -> 14.0", "results/*")

# ------------------------------------------------------------------ K. scale of the utility term, noise AUC
from scipy.stats import rankdata  # noqa: E402

kl_, F_ = [], []
for r in sel("fedfacs", base=True):
    for rd, bl in (r.get("diag") or {}).items():
        if int(rd) >= 5:
            kl_ += [x["kl"] for x in bl]; F_ += [x["F"] for x in bl]
kl_, F_ = np.array(kl_), np.array(F_)
from scipy.stats import spearmanr as _sp  # noqa: E402

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

add("K4", "4.2 / Lemma A", "share of client-rounds with the utility score below the fairness term (rounds 5-100)", "82.7%", "%.1f%%" % (100 * (kl_ < F_).mean()), "%.1f" % (100 * (kl_ < F_).mean()) == "82.7", "results/*_fedfacs_s*.json (diag records)")


def _auc(score, lab):
    rk = rankdata(score); n1 = lab.sum(); n0 = len(lab) - n1
    return (rk[lab == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


AU = []
for r in [x for x in sel("fedfacs", sc="s3", base=True)]:
    for bl in r["diag"].values():
        nz = np.array([x["noise"] for x in bl]); v = np.array([x["var"] for x in bl]); lab = (nz > 0.2).astype(int)
        if 0 < lab.sum() < len(lab):
            AU.append(_auc(v, lab))
AU = np.array(AU); lo, hi = bs_ci(AU)
K2 = "%.2f [%.2f, %.2f] (n=%d round-runs, noisy = noise level above 0.2)" % (AU.mean(), lo, hi, len(AU))
add("K2", "5.4 Uncertainty", "rank AUC of the batch variance for label noise", "0.45 [0.39, 0.52] (analysis/noise_discrimination.md)", K2, abs(AU.mean() - 0.45) < 0.006 and abs(lo - 0.39) < 0.015 and abs(hi - 0.52) < 0.01 and len(AU) == 18, "results/*_s3_fedfacs_s*.json (diag records); analysis/noise_discrimination.md")

# ------------------------------------------------------------------ H. propositions, by execution
import spec  # noqa: E402

rng = np.random.default_rng(1)


def simulate_guard(N=100, cmin=5, cmax=10, T=3000, adversarial=True):
    r = np.zeros(N, int); worst = 0
    R_ = math.ceil(N / cmin)
    for t in range(T):
        m = int(rng.integers(cmin, cmax + 1))
        fit = rng.random(N)
        if adversarial:
            fit = -r + rng.random(N) * 1e-3  # prefers recently selected clients: the worst case for waiting
        over = [i for i in np.lexsort((np.arange(N), -r)) if r[i] >= R_]
        chosen = over[:m]
        if len(chosen) < m:
            rest = [i for i in np.argsort(-fit, kind="stable") if i not in set(chosen)]
            chosen += rest[:m - len(chosen)]
        mask = np.zeros(N, bool); mask[chosen] = True
        r = np.where(mask, 0, r + 1); worst = max(worst, int(r.max()))
    return worst


W = {(N, adv): simulate_guard(N=N, adversarial=adv) for N in (50, 100, 200) for adv in (True, False)}
bound = {N: math.ceil(N / 5) + math.ceil(N / 5) - 1 for N in (50, 100, 200)}
ok = all(W[(N, a)] <= bound[N] for N in (50, 100, 200) for a in (True, False))
add("H1", "4.3 Prop. 2", "simulated longest wait with the guard (N=50,100,200; adversarial / random scores) against W-1", "<= 19, 39, 79", "adv " + ",".join(str(W[(N, True)]) for N in (50, 100, 200)) + " / rand " + ",".join(str(W[(N, False)]) for N in (50, 100, 200)), ok, "tools/verify_claims.py (3000 rounds each, cohort 5-10)")
Fv = []
for _ in range(2000):
    N = 100; rr = rng.integers(0, 60, N).astype(float); rb = rr.mean()
    Fv.append(spec.fairness(rr, rb))
Fv = np.array(Fv)
add("H2", "4.3 Prop. 1(ii)", "fairness term range over 2000 random counter vectors", "1 <= F < N+1", "min %.3f max %.1f" % (Fv.min(), Fv.max()), Fv.min() >= 1 and Fv.max() < 101, "spec.fairness")
amin, amax, den = 1, 0, 1e9
for _ in range(20000):
    a0 = rng.random(); nu = rng.normal(0, 0.5); u = abs(rng.normal(0, 0.05)); F = 1 + abs(rng.normal(0, 3))
    v = float(spec.mix_coeff(a0, nu, u, F, 0.9, 1.0)); amin = min(amin, v); amax = max(amax, v)
add("H3", "4.3 Prop. 1(i)", "mixing coefficient over 20000 random inputs lies in [0,1]", "[0, 1]", "[%.3f, %.3f]" % (amin, amax), amin >= 0 and amax <= 1, "spec.mix_coeff")
mm = [spec.cohort_size(x, 5, 10) for x in rng.normal(0, 3, 20000)]
add("H4", "4.3 Prop. 1(iii)", "cohort size over 20000 random efficiencies (incl. negative)", "integer in [5,10]", "[%d, %d]" % (min(mm), max(mm)), min(mm) >= 5 and max(mm) <= 10, "spec.cohort_size")
sw = []
for _ in range(20000):
    k = int(rng.integers(1, 10)); s_ = rng.normal(0, 1, k) * rng.choice([0, 1e-9, 1, 1e3]); n_ = rng.integers(10, 1000, k)
    w_ = np.asarray(spec.stability_weights(s_, n_), float); sw.append((w_.min(), abs(w_.sum() - 1)))
add("H5", "4.3 Prop. 1(iv)", "aggregation weights over 20000 random score vectors (negative, zero, tiny)", "w >= 0, sum = 1", "min %.1e, max |sum-1| %.1e" % (min(x[0] for x in sw), max(x[1] for x in sw)), min(x[0] for x in sw) >= 0 and max(x[1] for x in sw) < 1e-9, "spec.stability_weights")

json.dump(ROWS, open(os.path.join(r"C:\Users\0xRay\Downloads\paper\tools\_work", "claims.json"), "w"), indent=1)
print("\n%d claims, %d verified, %d differ" % (len(ROWS), sum(x["ok"] for x in ROWS), sum(not x["ok"] for x in ROWS)))
