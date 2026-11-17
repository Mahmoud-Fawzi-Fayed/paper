import glob
import json
import math
import os

import numpy as np

R = r"C:\Users\0xRay\Downloads\paper\fedfacs_repro\results"
runs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(R, "*.json")))]
ff = [r for r in runs if r["cfg"]["method"] in ("fedfacs",) and not r["cfg"].get("diag_rounds")]
print("fedfacs runs without diag:", len(ff))
for label, rs in (("fedfacs", ff), ("abl_A2", [r for r in runs if r["cfg"]["method"] == "abl_A2"]), ("both", ff + [r for r in runs if r["cfg"]["method"] == "abl_A2"])):
    for lag in (0, 1):
        for cmp_ in ("lt", "le"):
            tot = dec = 0
            for r in rs:
                nu = np.array(r["log"]["nu"], float); a = np.array(r["log"]["a_mean"], float)
                for t in range(1, len(a)):
                    n_ = nu[t - lag]
                    if n_ > 0 and math.isfinite(a[t]) and math.isfinite(a[t - 1]):
                        tot += 1
                        dec += (a[t] < a[t - 1]) if cmp_ == "lt" else (a[t] <= a[t - 1])
            print(label, "nu lag", lag, cmp_, tot, "%.1f%%" % (100 * dec / max(tot, 1)))
r = ff[0]
print([round(x, 4) for x in r["log"]["nu"][:8]], [round(x, 4) for x in r["log"]["a_mean"][:8]])
