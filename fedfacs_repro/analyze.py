"""Build all tables from results/*.json -> analysis/*.md and *.csv.   python analyze.py

Protocol (fixed before looking at results):
  * accuracy endpoint  : acc_best = TEST accuracy at the round of best VALIDATION accuracy; acc_last10 = mean test acc of last 10 rounds
  * round-to-target    : first round with VALIDATION accuracy >= target; target = 0.97 * mean over seeds of the best
                         validation accuracy of FedAvg(random) in the same dataset/scenario (common to all methods)
  * uncertainty        : mean +- std over seeds; paired differences (same seed = same partition and initialisation)
                         with a 95% bootstrap CI over seeds
  * participation JFI  : Jain index of raw selection counts (no injected noise); quality-adjusted JFI uses q_i = 10(1-noise_i)
"""
import glob
import json
import os
import re
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RES, OUT = os.path.join(HERE, "results"), os.path.join(HERE, "analysis")
os.makedirs(OUT, exist_ok=True)
MAIN_METHODS = ["random", "fedprox", "fednova", "qffl", "powd", "oort", "divfl", "fedfacs"]
ABL = ["fedfacs", "abl_A1", "abl_A2", "abl_fixmix", "abl_nofair", "abl_nopen", "abl_loss", "abl_randscore", "abl_rescale"]


def jain(x):
    x = np.asarray(x, float)
    return float(x.sum() ** 2 / (len(x) * (x ** 2).sum())) if (x ** 2).sum() > 0 else 0.0


def load():
    rows = []
    for p in sorted(glob.glob(os.path.join(RES, "*.json"))):
        r = json.load(open(p))
        c = r["cfg"]
        tag = re.sub(r"^.*_s\d+", "", os.path.basename(p)[:-5])
        rows.append((c["dataset"], c["scenario"], c["method"], c["seed"], tag, r))
    return rows


def run_metrics(r, target=None):
    lg = r["log"]
    va, ta = np.array(lg["val_acc"]), np.array(lg["test_acc"])
    sc = np.array(r["sel_count"], float)
    noise = np.array(r.get("noise", np.zeros(len(sc))))
    q = 10.0 * (1.0 - noise)
    pc = np.array(r["per_client_acc"])
    cm = np.array(r["confusion"], float)
    tp = np.diag(cm)
    rec = tp / np.maximum(cm.sum(1), 1)
    prec = tp / np.maximum(cm.sum(0), 1)
    f1 = 2 * prec * rec / np.maximum(prec + rec, 1e-12)
    m = dict(acc_best=ta[int(va.argmax())] * 100, acc_last10=ta[-10:].mean() * 100, acc_final=ta[-1] * 100,
             val_best=va.max() * 100, macro_recall=rec.mean() * 100, macro_prec=prec.mean() * 100, macro_f1=f1.mean() * 100,
             acc_from_cm=tp.sum() / cm.sum() * 100,
             jfi=jain(sc), jfi_q=jain(sc / q), never=(sc == 0).mean() * 100, max_wait=max(r["max_wait"]),
             pc_mean=pc.mean() * 100, pc_std=pc.std() * 100, pc_p10=np.percentile(pc, 10) * 100,
             cohort=np.mean(lg["cohort"]), up_gb=lg["up"][-1] / 1e9, down_gb=lg["down"][-1] / 1e9,
             steps_m=lg["steps"][-1] / 1e6, wall=np.mean(lg["wall"]), peak_mb=r.get("peak_mem_mb", np.nan),
             clip=r.get("clip_hits", 0), failed=r.get("failed_updates", 0), invalid=r.get("invalid_rounds", 0),
             jitter=np.abs(np.diff(ta[-30:])).mean() * 100)
    if target is not None:
        hit = np.where(va >= target)[0]
        rr = int(hit[0]) + 1 if len(hit) else None
        m["r2t"] = rr
        for k in ("up", "down"):
            m[k + "_gb_r2t"] = lg[k][rr - 1] / 1e9 if rr else None
        m["steps_m_r2t"] = lg["steps"][rr - 1] / 1e6 if rr else None
    return m


def ms(x, fmt="{:.2f}"):
    x = np.array([v for v in x if v is not None and not (isinstance(v, float) and np.isnan(v))], float)
    if len(x) == 0:
        return "n/a"
    return fmt.format(x.mean()) + (" ± " + fmt.format(x.std(ddof=1)) if len(x) > 1 else "")


def paired(a, b, n=10000, seed=0):
    """mean difference a-b over seeds and 95% bootstrap CI."""
    d = np.asarray(a, float) - np.asarray(b, float)
    d = d[~np.isnan(d)]
    if len(d) < 2:
        return float(d.mean()) if len(d) else float("nan"), (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    bm = rng.choice(d, (n, len(d))).mean(1)
    return float(d.mean()), (float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5)))


def md(df, path, floatfmt=None):
    df.to_csv(path.replace(".md", ".csv"), index=False)
    open(path, "w", encoding="utf8").write(df.to_markdown(index=False))


if __name__ == "__main__":
    rows = load()
    print(len(rows), "runs")
    base = [x for x in rows if x[4] == ""]
    # ---- targets
    targets = {}
    for (ds, sc) in {(x[0], x[1]) for x in base}:
        v = [run_metrics(x[5])["val_best"] for x in base if x[0] == ds and x[1] == sc and x[2] == "random"]
        if v:
            targets[(ds, sc)] = 0.97 * np.mean(v) / 100.0
    pd.DataFrame([dict(dataset=k[0], scenario=k[1], target_val_acc=round(v * 100, 2)) for k, v in sorted(targets.items())]
                 ).pipe(lambda d: md(d, os.path.join(OUT, "targets.md")))
    M = {}  # (ds, sc, method, tag, seed) -> metrics
    for ds, sc, me, seed, tag, r in rows:
        M[(ds, sc, me, tag, seed)] = run_metrics(r, targets.get((ds, sc)))

    def cell(ds, sc, me, tag=""):
        return {s: v for (d, c, m_, t, s), v in M.items() if (d, c, m_, t) == (ds, sc, me, tag)}

    # ---- 1. main comparison
    recs = []
    for (ds, sc) in sorted({(k[0], k[1]) for k in M if k[3] == "" and k[2] in MAIN_METHODS}):
        fed = cell(ds, sc, "fedfacs")
        for me in MAIN_METHODS:
            c = cell(ds, sc, me)
            if not c:
                continue
            seeds = sorted(c)
            reached = [c[s]["r2t"] for s in seeds if c[s].get("r2t")]
            row = dict(dataset=ds, scenario=sc, method=me, seeds=len(seeds),
                       acc_best=ms([c[s]["acc_best"] for s in seeds]), acc_last10=ms([c[s]["acc_last10"] for s in seeds]),
                       r2t=(ms(reached, "{:.0f}") + f" ({len(reached)}/{len(seeds)})") if reached else f"not reached (0/{len(seeds)})",
                       up_GB=ms([c[s]["up_gb"] for s in seeds], "{:.1f}"), down_GB=ms([c[s]["down_gb"] for s in seeds], "{:.1f}"),
                       steps_M=ms([c[s]["steps_m"] for s in seeds], "{:.2f}"),
                       jfi=ms([c[s]["jfi"] for s in seeds], "{:.3f}"), never_pct=ms([c[s]["never"] for s in seeds], "{:.1f}"),
                       max_wait=ms([c[s]["max_wait"] for s in seeds], "{:.0f}"),
                       client_p10=ms([c[s]["pc_p10"] for s in seeds]), macro_f1=ms([c[s]["macro_f1"] for s in seeds]))
            if me != "fedfacs" and fed:
                common = sorted(set(c) & set(fed))
                d_, ci = paired([fed[s]["acc_best"] for s in common], [c[s]["acc_best"] for s in common])
                row["fedfacs-minus-this acc_best (95% CI)"] = f"{d_:+.2f} [{ci[0]:+.2f}, {ci[1]:+.2f}] n={len(common)}"
            recs.append(row)
    if recs:
        md(pd.DataFrame(recs), os.path.join(OUT, "main_comparison.md"))

    # ---- 2. ablation (s1_0.5)
    recs = []
    for ds in sorted({k[0] for k in M if k[2] in ABL}):
        sc = "s1_0.5"
        full = cell(ds, sc, "fedfacs")
        for me in ABL:
            c = cell(ds, sc, me)
            if not c:
                continue
            seeds = sorted(c)
            row = dict(dataset=ds, variant=me, seeds=len(seeds), acc_best=ms([c[s]["acc_best"] for s in seeds]),
                       r2t=ms([c[s].get("r2t") for s in seeds], "{:.0f}"), jfi=ms([c[s]["jfi"] for s in seeds], "{:.3f}"),
                       never_pct=ms([c[s]["never"] for s in seeds], "{:.1f}"), cohort=ms([c[s]["cohort"] for s in seeds]),
                       client_p10=ms([c[s]["pc_p10"] for s in seeds]), jitter=ms([c[s]["jitter"] for s in seeds]))
            if me != "fedfacs" and full:
                common = sorted(set(c) & set(full))
                d_, ci = paired([c[s]["acc_best"] for s in common], [full[s]["acc_best"] for s in common])
                row["this-minus-full acc_best (95% CI)"] = f"{d_:+.2f} [{ci[0]:+.2f}, {ci[1]:+.2f}]"
            recs.append(row)
    if recs:
        md(pd.DataFrame(recs), os.path.join(OUT, "ablation.md"))

    # ---- 3. utility validity (diag): Spearman(score, marginal validation-loss gain of including the client)
    rec = []
    for ds, sc, me, seed, tag, r in rows:
        if tag != "" or not r.get("diag") or me not in ("fedfacs", "abl_nopen", "abl_loss"):
            continue
        for t, recs_ in r["diag"].items():
            d = pd.DataFrame(recs_)
            if len(d) < 10 or d["gain"].std() == 0:
                continue
            row = dict(dataset=ds, scenario=sc, method=me, seed=seed, round=int(t))
            for k in ("kl", "var", "F", "fit", "gce", "n"):
                row["rho_" + k] = stats.spearmanr(d[k], d["gain"])[0]
            row["rho_stab"] = stats.spearmanr(d["kl"] - d["var"], d["gain"])[0]
            rec.append(row)
    if rec:
        D = pd.DataFrame(rec)
        D.to_csv(os.path.join(OUT, "utility_validity_raw.csv"), index=False)
        out = []
        for me in sorted(D["method"].unique()):
            for sc in sorted(D["scenario"].unique()):
                sub = D[(D.method == me) & (D.scenario == sc)]
                if sub.empty:
                    continue
                row = dict(method=me, scenario=sc, n_round_runs=len(sub))
                for k in ("kl", "var", "F", "fit", "gce", "n"):
                    v = sub["rho_" + k].dropna().values
                    d_, ci = paired(v, np.zeros_like(v))
                    row[f"rho({k})"] = f"{d_:+.2f} [{ci[0]:+.2f},{ci[1]:+.2f}]"
                out.append(row)
        md(pd.DataFrame(out), os.path.join(OUT, "utility_validity.md"))

    # ---- 4. noise discrimination (s3)
    def auc(score, label):
        score, label = np.asarray(score), np.asarray(label, bool)
        if label.all() or (~label).all():
            return float("nan")
        rk = stats.rankdata(score)
        n1, n0 = label.sum(), (~label).sum()
        return (rk[label].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)

    rec = []
    for ds, sc, me, seed, tag, r in rows:
        if sc != "s3" or not r.get("diag") or me not in ("fedfacs", "abl_nopen", "abl_loss"):
            continue
        for t, recs_ in r["diag"].items():
            d = pd.DataFrame(recs_)
            noisy = d["noise"] > 0.225
            row = dict(dataset=ds, method=me, seed=seed, round=int(t))
            for k in ("kl", "var", "fit", "gce"):
                row["auc_" + k] = auc(d[k], noisy)                 # high score on noisy clients?
                row["rho_noise_" + k] = stats.spearmanr(d[k], d["noise"])[0]
            row["auc_stab_low"] = auc(-(d["kl"] - d["var"]), noisy)
            rec.append(row)
    if rec:
        D = pd.DataFrame(rec)
        D.to_csv(os.path.join(OUT, "noise_discrimination_raw.csv"), index=False)
        out = []
        for me in sorted(D.method.unique()):
            sub = D[D.method == me]
            row = dict(method=me, n=len(sub))
            for k in ("auc_kl", "auc_var", "auc_fit", "auc_gce", "rho_noise_kl", "rho_noise_var", "rho_noise_gce"):
                v = sub[k].dropna().values
                d_, ci = paired(v, np.full_like(v, 0.5 if k.startswith("auc") else 0.0))
                row[k] = f"{(d_ + (0.5 if k.startswith('auc') else 0)):.2f} [{ci[0] + (0.5 if k.startswith('auc') else 0):.2f},{ci[1] + (0.5 if k.startswith('auc') else 0):.2f}]"
            out.append(row)
        md(pd.DataFrame(out), os.path.join(OUT, "noise_discrimination.md"))
    # s3 accuracy + quality-adjusted fairness
    recs = []
    for ds in sorted({k[0] for k in M if k[1] == "s3"}):
        for me in sorted({k[2] for k in M if k[1] == "s3" and k[0] == ds}):
            c = cell(ds, "s3", me)
            seeds = sorted(c)
            recs.append(dict(dataset=ds, method=me, seeds=len(seeds), acc_best=ms([c[s]["acc_best"] for s in seeds]),
                             jfi_raw=ms([c[s]["jfi"] for s in seeds], "{:.3f}"), jfi_quality_adj=ms([c[s]["jfi_q"] for s in seeds], "{:.3f}"),
                             client_p10=ms([c[s]["pc_p10"] for s in seeds])))
    if recs:
        md(pd.DataFrame(recs), os.path.join(OUT, "noisy_s3_accuracy_fairness.md"))

    # ---- 5. sensitivity (fmnist s1_0.5, fedfacs)
    recs = []
    tags = sorted({k[3] for k in M if k[3].startswith("_s")})
    for tag in [""] + tags:
        c = {s: v for (d, sc, m_, t, s), v in M.items() if (d, sc, m_, t) == ("fmnist", "s1_0.5", "fedfacs", tag) and s < 3}
        if c:
            seeds = sorted(c)
            recs.append(dict(setting=tag or "default", seeds=len(seeds), acc_best=ms([c[s]["acc_best"] for s in seeds]),
                             r2t=ms([c[s].get("r2t") for s in seeds], "{:.0f}"), jfi=ms([c[s]["jfi"] for s in seeds], "{:.3f}"),
                             cohort=ms([c[s]["cohort"] for s in seeds]), jitter=ms([c[s]["jitter"] for s in seeds])))
    if len(recs) > 1:
        md(pd.DataFrame(recs), os.path.join(OUT, "sensitivity.md"))

    # ---- 6. scale
    recs = []
    for tag in ["_N50", "", "_N200", "_N400"]:
        for me in ("fedfacs", "random"):
            c = {s: v for (d, sc, m_, t, s), v in M.items() if (d, sc, m_, t) == ("fmnist", "s1_0.5", me, tag) and s < 3}
            if c:
                seeds = sorted(c)
                recs.append(dict(N=int(tag[2:]) if tag else 100, method=me, seeds=len(seeds),
                                 acc_best=ms([c[s]["acc_best"] for s in seeds]), down_GB=ms([c[s]["down_gb"] for s in seeds], "{:.1f}"),
                                 up_GB=ms([c[s]["up_gb"] for s in seeds], "{:.1f}"), s_per_round=ms([c[s]["wall"] for s in seeds]),
                                 peak_MB=ms([c[s]["peak_mb"] for s in seeds], "{:.0f}"), jfi=ms([c[s]["jfi"] for s in seeds], "{:.3f}"),
                                 never_pct=ms([c[s]["never"] for s in seeds], "{:.1f}"), max_wait=ms([c[s]["max_wait"] for s in seeds], "{:.0f}")))
    if len(recs) > 2:
        md(pd.DataFrame(recs), os.path.join(OUT, "scale.md"))

    # ---- 7. health of the runs
    h = pd.DataFrame([dict(run="/".join(map(str, k)), clip=v["clip"], failed=v["failed"], invalid=v["invalid"],
                           macro_recall_minus_acc=v["macro_recall"] - v["acc_from_cm"]) for k, v in M.items()])
    print("runs with failed/invalid:", int(((h["failed"] > 0) | (h["invalid"] > 0)).sum()), "| total clip hits:", int(h["clip"].sum()))
    print("written:", sorted(os.listdir(OUT)))
