import glob
import json
import os
import re
import sys

import numpy as np
from scipy.stats import rankdata

R = r"C:\Users\0xRay\Downloads\paper\fedfacs_repro\results"
runs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(R, "*_s3_fedfacs_s*.json"))) if re.search(r"_s\d+\.json$", f)]
print(len(runs), [r["cfg"]["dataset"] + str(r["cfg"]["seed"]) for r in runs])


def auc(score, lab):
    r = rankdata(score)
    n1 = lab.sum(); n0 = len(lab) - n1
    return (r[lab == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


for thr in (0.0, 0.1, 0.2, 0.25, 0.3):
    A = []
    for r in runs:
        for bl in r["diag"].values():
            nz = np.array([x["noise"] for x in bl]); v = np.array([x["var"] for x in bl])
            lab = (nz > thr).astype(int)
            if 0 < lab.sum() < len(lab):
                A.append(auc(v, lab))
    A = np.array(A)
    b = np.random.default_rng(0).choice(A, (10000, len(A))).mean(1)
    print("thr", thr, "n", len(A), "AUC(var) %.2f [%.2f, %.2f]" % (A.mean(), *np.percentile(b, [2.5, 97.5])))
