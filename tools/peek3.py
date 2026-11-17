import glob
import json
import os

import numpy as np

R = r"C:\Users\0xRay\Downloads\paper\fedfacs_repro\results"
runs = {}
for f in sorted(glob.glob(os.path.join(R, "*.json"))):
    r = json.load(open(f))
    runs[os.path.basename(f)] = r


def acc(r):
    va, ta = np.array(r["log"]["val_acc"]), np.array(r["log"]["test_acc"])
    return ta[int(va.argmax())] * 100


for ds in ("fmnist",):
    for me in ("abl_loss", "fedfacs"):
        print(me, [(k.split("_")[-1], round(acc(r), 2)) for k, r in runs.items() if r["cfg"]["method"] == me and r["cfg"]["dataset"] == ds and r["cfg"]["scenario"] == "s1_0.5" and not k.endswith("_dist.json")])
# per-client a from diag (fedfacs runs with diag, rounds >= 5)
for label, filt in (("fedfacs diag", lambda k, r: r["cfg"]["method"] == "fedfacs" and r.get("diag")),):
    vals = []
    for k, r in runs.items():
        if filt(k, r):
            for rd, bl in r["diag"].items():
                if int(rd) >= 5:
                    vals += [x["a"] for x in bl]
    v = np.array(vals)
    print(label, len(v), "median %.3f mean %.3f p5 %.4f p95 %.3f" % (np.median(v), v.mean(), np.percentile(v, 5), np.percentile(v, 95)))
vals = []
for k, r in runs.items():
    if r["cfg"]["method"] == "fedfacs" and r.get("diag"):
        for rd, bl in r["diag"].items():
            vals += [x["a"] for x in bl]
v = np.array(vals)
print("all rounds incl. 1:", len(v), "median %.3f mean %.3f p5 %.4f p95 %.3f" % (np.median(v), v.mean(), np.percentile(v, 5), np.percentile(v, 95)))
