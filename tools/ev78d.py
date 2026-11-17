import json
import sys

sys.path.insert(0, r"C:\Users\0xRay\Downloads\paper\tools")
import numpy as np

import ev78c as E  # prints its own summary; D and met are reused

cells = E.cells
rows = {}
for m in ("abl_A1", "abl_A2", "a2_relcoh"):
    rows[m] = [E.met(E.D[(m,) + c]) for c in cells]
print("\nTABLE Z (6 runs: CIFAR-10 and FMNIST, alpha=0.5, seeds 0-2)")
for m, rs in rows.items():
    f = lambda k, fmt="%.2f": (fmt % np.mean([x[k] for x in rs])) + " +- " + (fmt % np.std([x[k] for x in rs], ddof=1))
    co = [x["cohort"] for x in rs]
    print(m, "| cohort %s | min m_t %d | at cmax %.0f%% | uploads GB %s | best %s | last10 %s | jfi %.3f | wait %.1f | never %.1f" % (
        f("cohort"), min(x["cmin"] for x in rs), np.mean([x["at_cmax"] for x in rs]), f("up", "%.1f"), f("best"), f("last10"),
        np.mean([x["jfi"] for x in rs]), np.mean([x["wait"] for x in rs]), np.mean([x["never"] for x in rs])))
up1 = np.mean([x["up"] for x in rows["abl_A1"]])
for m in ("abl_A2", "a2_relcoh"):
    print(m, "upload saving vs fixed: %.1f%%" % (100 * (1 - np.mean([x["up"] for x in rows[m]]) / up1)))
from analyze import paired
for m in ("abl_A2", "a2_relcoh"):
    for k in ("best", "last10", "up"):
        d, ci = paired([x[k] for x in rows[m]], [x[k] for x in rows["abl_A1"]])
        print("DIFF", m, "-A1", k, "%+.2f [%+.2f, %+.2f]" % (d, ci[0], ci[1]))
