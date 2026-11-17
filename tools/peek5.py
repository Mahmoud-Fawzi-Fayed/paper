import glob
import json
import os
import re

import numpy as np
from scipy.stats import spearmanr

R = r"C:\Users\0xRay\Downloads\paper\fedfacs_repro\results"
runs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(R, "*_fedfacs_s*.json"))) if re.search(r"_s\d+\.json$", f)]
runs = [r for r in runs if r.get("diag")]
print("runs with diag", len(runs))
rhoPF, rhoPK, share, over = [], [], [], []
Fall, Kall, Aall, ratio = [], [], [], []
for r in runs:
    for rd, bl in r["diag"].items():
        t = int(rd)
        if t < 5:
            continue
        kl = np.array([x["kl"] for x in bl]); F = np.array([x["F"] for x in bl]); a = np.array([x["a"] for x in bl])
        P = a * kl + (1 - a) * F
        rhoPF.append(spearmanr(P, F)[0]); rhoPK.append(spearmanr(P, kl)[0])
        sel = list(r["log"]["selected"][t - 1])
        share.append(np.mean(F[sel] >= np.median(F)))
        Fall += list(F); Kall += list(kl); Aall += list(a)
        ratio += list((a * kl) / ((1 - a) * F))
Fall, Kall, Aall, ratio = map(np.array, (Fall, Kall, Aall, ratio))
print("F median %.2f p5 %.2f p95 %.2f | KL median %.2f p95 %.2f | a median %.2f" % (np.median(Fall), np.percentile(Fall, 5), np.percentile(Fall, 95), np.median(Kall), np.percentile(Kall, 95), np.median(Aall)))
print("Spearman(priority, F) mean %.2f ; Spearman(priority, KL) mean %.2f" % (np.mean(rhoPF), np.mean(rhoPK)))
print("share of selected clients with F >= median F: %.1f%%" % (100 * np.mean(share)))
print("weight of the utility term relative to the fairness term a*KL/((1-a)*F): median %.3f p95 %.3f" % (np.median(ratio), np.percentile(ratio, 95)))
