"""Evidence for Replacements 9 and 10, recomputed from fedfacs_repro/results/*.json. Writes tools/_work/ev910.json."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "fedfacs_repro"))
import analyze as A  # noqa: E402

rows = A.load()
MAIN_SC = ("s1_0.1", "s1_0.5", "s2")
out = {}
BASELINES = {"random", "fedprox", "fednova", "qffl", "powd", "oort", "divfl", "greedy", "fairfedcs"}


def base(method, sc, ds=None):
    return [r for (d, s, m, seed, tag, r) in rows if m == method and s in sc and tag == "" and (ds is None or d == ds)]


def mean_sd(x, f="{:.2f}"):
    x = np.asarray(x, float)
    return f.format(x.mean()) + (" ± " + f.format(x.std(ddof=1)) if len(x) > 1 else "")


# ---------------------------------------------------------------- A. resource accounting (R1-08, R2-01)
res = {}
for m in ["random", "powd", "oort", "divfl", "abl_A2"]:
    rs = base(m, MAIN_SC)
    T = np.array([len(r["log"]["val_acc"]) for r in rs])
    B = np.array([r["bytes_per_model"] for r in rs], float)
    down = np.array([r["log"]["down"][-1] for r in rs]) / B / T
    up = np.array([r["log"]["up"][-1] for r in rs]) / B / T
    aux = np.array([r["log"]["aux"][-1] for r in rs]) / T / 1e3
    steps = np.array([r["log"]["steps"][-1] for r in rs], float) / T
    fwd = np.array([r["log"]["fwd"][-1] for r in rs], float) / T / 1e3
    tot = (np.array([r["log"]["down"][-1] + r["log"]["up"][-1] + r["log"]["aux"][-1] for r in rs])) / 1e9
    wall = np.array([np.mean(r["log"]["wall"]) for r in rs])
    res[m] = dict(n=len(rs), down=down.mean(), up=up.mean(), aux_kb=aux.mean(), steps=steps.mean(), fwd_k=fwd.mean(),
                  total_gb=tot.mean(), wall=wall.mean(), cohort=np.mean([np.mean(r["log"]["cohort"]) for r in rs]))
for m in res:
    res[m]["steps_rel"] = res[m]["steps"] / res["random"]["steps"]
    res[m]["total_rel"] = res[m]["total_gb"] / res["random"]["total_gb"]
    res[m]["wall_rel"] = res[m]["wall"] / res["random"]["wall"]
out["resource"] = res

# paired: FedFACS vs FedAvg-style random, cumulative uploads and total bytes to the common target (r2t)
# ---------------------------------------------------------------- B. fairness (R1-09, R2-15), scenario 3
fair = {}
for ds in ("cifar10", "fmnist"):
    for m in ["random", "powd", "greedy", "fairfedcs", "fedfacs"]:
        rs = [r for (d, s, mm, seed, tag, r) in rows if d == ds and s == "s3" and mm == m and tag == ""]
        if not rs:
            continue
        ms_ = [A.run_metrics(r) for r in rs]
        fair[ds + "|" + m] = dict(n=len(rs), jfi=[x["jfi"] for x in ms_], jfi_q=[x["jfi_q"] for x in ms_],
                                  never=[x["never"] for x in ms_], wait=[x["max_wait"] for x in ms_],
                                  pc_mean=[x["pc_mean"] for x in ms_], pc_std=[x["pc_std"] for x in ms_], pc_p10=[x["pc_p10"] for x in ms_],
                                  acc=[x["acc_best"] for x in ms_])
out["fair"] = fair

# selection-frequency distribution of FedFACS vs random (all main settings): quantiles of selection counts per run
dist = {}
for m in ("abl_A2", "random", "powd"):
    rs = base(m, MAIN_SC)
    q = np.array([np.percentile(r["sel_count"], [0, 10, 50, 90, 100]) for r in rs])
    dist[m] = q.mean(0).tolist()
out["seldist"] = dist

# quality example computed, not asserted
q = np.array([10.0, 5.0]); p = q.copy()
out["example_quality"] = dict(raw=A.jain(p), adj=A.jain(p / q))
x = np.r_[np.ones(90), np.zeros(10)]
out["example_90"] = A.jain(x)

# ---------------------------------------------------------------- C. classification metrics (macro averages)
cls = {}
dmax = 0.0
for (d, s, m, seed, tag, r) in rows:
    mm = A.run_metrics(r)
    dmax = max(dmax, abs(mm["acc_from_cm"] - mm["macro_recall"])) if d in ("cifar10", "fmnist", "mnist") else dmax
for ds in ("cifar10", "fmnist", "mnist"):
    for m in ("abl_A2", "random"):
        rs = base(m, MAIN_SC, ds)
        ms_ = [A.run_metrics(r) for r in rs]
        cls[ds + "|" + m] = dict(n=len(rs), acc=[x["acc_from_cm"] for x in ms_], rec=[x["macro_recall"] for x in ms_],
                                 prec=[x["macro_prec"] for x in ms_], f1=[x["macro_f1"] for x in ms_])
out["cls"] = cls
out["cls_max_gap_acc_recall"] = dmax

# ---------------------------------------------------------------- D. protocol audit (R1-21, R2-03, R2-08)
tot = dict(runs=0, ff=0, invalid=0, failed=0, clip=0, bounds=0, cohort_eq=0, wait_ok=0, selcnt_ok=0, up_ok=0, rounds_ok=0)
for (d, s, m, seed, tag, r) in rows:
    lg, cfg = r["log"], r["cfg"]
    tot["runs"] += 1
    tot["invalid"] += r.get("invalid_rounds", 0)
    tot["failed"] += r.get("failed_updates", 0)
    tot["clip"] += r.get("clip_hits", 0)
    if m in BASELINES:
        continue
    tot["ff"] += 1
    N, T = cfg["N"], len(lg["selected"])
    if all(cfg["cmin"] <= len(sel) <= cfg["cmax"] for sel in lg["selected"]):
        tot["bounds"] += 1
    if all(len(sel) == c for sel, c in zip(lg["selected"], lg["cohort"])):
        tot["cohort_eq"] += 1
    cnt = np.zeros(N, int)
    last = np.zeros(N, int)
    mw = np.zeros(N, int)
    for t, sel in enumerate(lg["selected"], 1):
        for i in sel:
            mw[i] = max(mw[i], t - last[i] - 1)
            last[i] = t
            cnt[i] += 1
    mw = np.maximum(mw, T - last)  # the logged longest wait includes the open stretch after the last selection
    if np.array_equal(cnt, np.array(r["sel_count"])):
        tot["selcnt_ok"] += 1
    if int(mw.max()) == int(max(r["max_wait"])):
        tot["wait_ok"] += 1
    if abs(lg["up"][-1] - sum(lg["cohort"]) * r["bytes_per_model"]) < 1:
        tot["up_ok"] += 1
    if T == cfg["rounds"]:
        tot["rounds_ok"] += 1
out["audit"] = tot

# ---------------------------------------------------------------- A2. cost to the common target (Eqs. 22-23a)
import csv
tg = {(r_["dataset"], r_["scenario"]): float(r_["target_val_acc"]) / 100 for r_ in csv.DictReader(open(os.path.join(HERE, "..", "fedfacs_repro", "analysis", "targets.csv")))}
tt = {}
for m in ["random", "powd", "oort", "divfl", "abl_A2"]:
    ok = n = 0
    r2t, upl, tgb, gp = [], [], [], []
    for (d, s, mm, seed, tag, r) in rows:
        if mm != m or s not in MAIN_SC or tag != "":
            continue
        n += 1
        va = np.array(r["log"]["val_acc"])
        hit = np.where(va >= tg[(d, s)])[0]
        if not len(hit):
            continue
        k = int(hit[0]); ok += 1
        B_ = r["bytes_per_model"]
        r2t.append(k + 1)
        upl.append(r["log"]["up"][k] / B_)
        tgb.append((r["log"]["down"][k] + r["log"]["up"][k] + r["log"]["aux"][k]) / 1e9)
    tt[m] = dict(n=n, reached=ok, r2t=float(np.mean(r2t)) if r2t else None, uploads=float(np.mean(upl)) if upl else None,
                 total_gb=float(np.mean(tgb)) if tgb else None)
out["target"] = tt
print(tt)

json.dump(out, open(os.path.join(HERE, "_work", "ev910.json"), "w"), indent=1)
print(json.dumps(out["audit"]), out["cls_max_gap_acc_recall"], out["example_quality"], out["example_90"])
for m, v in res.items():
    print(m, {k: round(x, 3) for k, x in v.items()})
print(dist)

# ---------------------------------------------------------------- A3. participation of the clients in the Table V runs (JFI with q_i = 1)
part = {}
for m in ["random", "powd", "oort", "divfl", "abl_A2"]:
    rs = base(m, MAIN_SC)
    ms_ = [A.run_metrics(r) for r in rs]
    part[m] = dict(jfi=float(np.mean([x["jfi"] for x in ms_])), never=float(np.mean([x["never"] for x in ms_])), wait=float(np.mean([x["max_wait"] for x in ms_])))
out["part"] = part
json.dump(out, open(os.path.join(HERE, "_work", "ev910.json"), "w"), indent=1)
print(part)
