"""Relative-efficiency cohort rule (a2_relcoh) against the absolute rule (abl_A2): dataset x seed paired comparison."""
import glob
import json
import os
import sys

sys.path.insert(0, r"C:\Users\0xRay\Downloads\paper\fedfacs_repro")
import numpy as np

from analyze import jain, paired

R = r"C:\Users\0xRay\Downloads\paper\fedfacs_repro\results"
D = {}
for f in glob.glob(os.path.join(R, "*.json")):
    r = json.load(open(f))
    c = r["cfg"]
    D[(c["method"], c["dataset"], c["scenario"], c["seed"])] = r


def met(r):
    lg = r["log"]
    va, ta = np.array(lg["val_acc"]), np.array(lg["test_acc"])
    sc = np.array(r["sel_count"], float)
    co = np.array(lg["cohort"], float)
    return dict(best=ta[int(va.argmax())] * 100, last10=ta[-10:].mean() * 100, jfi=jain(sc), never=(sc == 0).mean() * 100,
                wait=max(r["max_wait"]), cohort=co.mean(), cmin=co.min(), cmax=co.max(), at_cmax=(co == 10).mean() * 100,
                up=lg["up"][-1] / 1e9, steps=lg["steps"][-1] / 1e6, jitter=np.abs(np.diff(ta[-30:])).mean() * 100,
                val_loss=np.array(lg["val_loss"])[-1])


out = {}
cells = [(d, "s1_0.5", s) for d in ("cifar10", "fmnist") for s in (0, 1, 2)]
rows = {"abl_A2": [], "a2_relcoh": []}
for cell in cells:
    for m in rows:
        r = D.get((m,) + cell)
        if r is None:
            print("missing", m, cell)
        else:
            rows[m].append(met(r))
n = min(len(rows["abl_A2"]), len(rows["a2_relcoh"]))
print("pairs", n)
for k in ("best", "last10", "jfi", "never", "wait", "cohort", "cmin", "at_cmax", "up", "jitter"):
    a = [x[k] for x in rows["a2_relcoh"][:n]]
    b = [x[k] for x in rows["abl_A2"][:n]]
    dm, ci = paired(a, b)
    print("%-8s relcoh %.3f | abs-rule %.3f | diff %+.3f [%+.3f, %+.3f]" % (k, np.mean(a), np.mean(b), dm, ci[0], ci[1]))
    out[k] = dict(rel=float(np.mean(a)), abs=float(np.mean(b)), diff=dm, lo=ci[0], hi=ci[1])
rel = rows["a2_relcoh"]
print("relcoh cohort range over runs: min of mins", min(x["cmin"] for x in rel), "max of maxes", max(x["cmax"] for x in rel))
print("saving vs fixed cohort of 10: relcoh %.1f%%  abs %.1f%%" % (100 * (1 - np.mean([x["cohort"] for x in rel]) / 10), 100 * (1 - np.mean([x["cohort"] for x in rows["abl_A2"]]) / 10)))
# per-dataset
for ds in ("cifar10", "fmnist"):
    sub = [met(D[("a2_relcoh", ds, "s1_0.5", s)]) for s in (0, 1, 2) if ("a2_relcoh", ds, "s1_0.5", s) in D]
    sa = [met(D[("abl_A2", ds, "s1_0.5", s)]) for s in (0, 1, 2) if ("a2_relcoh", ds, "s1_0.5", s) in D]
    if sub:
        print(ds, "relcoh cohort %.2f best %.2f last10 %.2f | A2 cohort %.2f best %.2f last10 %.2f" % (np.mean([x["cohort"] for x in sub]), np.mean([x["best"] for x in sub]), np.mean([x["last10"] for x in sub]), np.mean([x["cohort"] for x in sa]), np.mean([x["best"] for x in sa]), np.mean([x["last10"] for x in sa])))
json.dump(out, open(r"C:\Users\0xRay\Downloads\paper\tools\_work\relcoh.json", "w"))
