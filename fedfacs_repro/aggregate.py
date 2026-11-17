"""Aggregate results/*.json into tables with mean +- std over seeds and paired 95% bootstrap CIs.

Metrics per run
  acc_final   test accuracy at the last round
  acc_best    test accuracy at the round of best validation accuracy (checkpoint selection)
  r2t         first round whose VALIDATION accuracy >= target (None if never)
  up_r2t / down_r2t / steps_r2t   cumulative uploaded MB / downloaded MB / training steps at that round
  jfi         Jain index of raw participation counts (q_i = const: no injected noise)
  never       fraction of clients never selected;  max_wait  max rounds any client waited
  pc_mean / pc_p10 / pc_std       per-client accuracy of the final global model on held-out local data
"""
import glob
import json
import os
import sys
import numpy as np

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def load(pattern="*.json"):
    runs = []
    for p in sorted(glob.glob(os.path.join(RES, pattern))):
        runs.append(json.load(open(p)))
    return runs


def jain(x):
    x = np.asarray(x, float)
    return float(x.sum() ** 2 / (len(x) * (x ** 2).sum())) if (x ** 2).sum() > 0 else 0.0


def metrics(run, target=None):
    lg = run["log"]
    va, ta = np.array(lg["val_acc"]), np.array(lg["test_acc"])
    mb = lambda v: v / 1e6
    out = dict(acc_final=ta[-1], acc_best=ta[int(va.argmax())], val_best=va.max(),
               cohort_mean=float(np.mean(lg["cohort"])), wall_per_round=float(np.mean(lg["wall"])))
    sc = np.array(run["sel_count"], float)
    out.update(jfi=jain(sc), never=float((sc == 0).mean()), max_wait=int(max(run["max_wait"])),
               sel_cv=float(sc.std() / sc.mean()) if sc.mean() > 0 else 0.0)
    pc = np.array(run["per_client_acc"])
    out.update(pc_mean=float(pc.mean()), pc_std=float(pc.std()), pc_p10=float(np.percentile(pc, 10)))
    out.update(up_total=mb(lg["up"][-1]), down_total=mb(lg["down"][-1]), steps_total=lg["steps"][-1])
    if target is not None:
        hit = np.where(va >= target)[0]
        r = int(hit[0]) + 1 if len(hit) else None
        out["r2t"] = r
        for k in ("up", "down", "steps"):
            out[k + "_r2t"] = (mb(lg[k][r - 1]) if k != "steps" else lg[k][r - 1]) if r else None
        out["reached"] = r is not None
    return out


def group(runs):
    g = {}
    for r in runs:
        c = r["cfg"]
        g.setdefault((c["dataset"], c["scenario"], c["method"]), {})[c["seed"]] = r
    return g


def boot_ci(diffs, n=10000, seed=0):
    d = np.asarray(diffs, float)
    if len(d) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    m = rng.choice(d, (n, len(d)), replace=True).mean(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def ms(vals, f="{:.2f}", scale=1.0):
    v = np.array([x for x in vals if x is not None], float) * scale
    if len(v) == 0:
        return "n/a"
    s = f.format(v.mean()) + (" ± " + f.format(v.std(ddof=1)) if len(v) > 1 else "")
    return s


if __name__ == "__main__":
    pat = sys.argv[1] if len(sys.argv) > 1 else "*.json"
    runs = load(pat)
    print(len(runs), "runs")
    G = group(runs)
    for key in sorted(G):
        seeds = sorted(G[key])
        mm = [metrics(G[key][s]) for s in seeds]
        print(key, "seeds", seeds, "acc_best", ms([m["acc_best"] for m in mm], scale=100),
              "jfi", ms([m["jfi"] for m in mm], "{:.3f}"))
