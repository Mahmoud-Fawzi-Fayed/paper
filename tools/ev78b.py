import glob
import json
import os
import sys

sys.path.insert(0, r"C:\Users\0xRay\Downloads\paper\fedfacs_repro")
import numpy as np

R = r"C:\Users\0xRay\Downloads\paper\fedfacs_repro\results"
D = {}
for f in glob.glob(os.path.join(R, "*.json")):
    r = json.load(open(f))
    c = r["cfg"]
    D[(c["method"], c["dataset"], c["scenario"], c["seed"])] = r


def acc(r):
    va, ta = np.array(r["log"]["val_acc"]), np.array(r["log"]["test_acc"])
    return ta[int(va.argmax())] * 100, ta[-10:].mean() * 100


cells = sorted({k[1:] for k in D if k[0] == "abl_A1"})
print("A1 cells:", cells)
d_b, d_l, up = [], [], []
for cell in cells:
    a1, a2 = D.get(("abl_A1",) + cell), D.get(("abl_A2",) + cell)
    if a1 and a2:
        b1, l1 = acc(a1)
        b2, l2 = acc(a2)
        d_b.append(b2 - b1)
        d_l.append(l2 - l1)
        up.append(100 * (1 - np.sum(a2["log"]["cohort"]) / np.sum(a1["log"]["cohort"])))
        print(cell, "A2-A1 best %+.2f last10 %+.2f upload saving %.1f%% cohort %.2f" % (b2 - b1, l2 - l1, up[-1], np.mean(a2["log"]["cohort"])))
print("n pairs", len(d_b), "mean diff best %+.2f last10 %+.2f saving %.1f%%" % (np.mean(d_b), np.mean(d_l), np.mean(up)))
