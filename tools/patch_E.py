p = r"C:\Users\0xRay\Downloads\paper\tools\verify_claims.py"
L = open(p, encoding="utf8").read().split("\n")
a = next(i for i, l in enumerate(L) if l.startswith("# ----") and "E. controller direction" in l)
b = next(i for i, l in enumerate(L) if l.startswith("# ----") and "F. waiting times" in l)
new = '''# ------------------------------------------------------------------ E. controller direction and coefficient distribution
CTRL = sel("fedfacs", base=True) + sel("abl_A2", base=True)
tot = dec = 0
for r in CTRL:
    nu = np.array(r["log"]["nu"], float); a_ = np.array(r["log"]["a_mean"], float)
    for t in range(1, len(a_)):
        if nu[t - 1] > 0 and math.isfinite(a_[t]) and math.isfinite(a_[t - 1]):   # nu logged after round t-1 is the signal used in round t
            tot += 1; dec += a_[t] < a_[t - 1]
E1 = "%.1f%% of %d (%d runs)" % (100 * dec / max(tot, 1), tot, len(CTRL))
print("   E1 set:", E1)
add("E1", "5.4 Uncertainty / 4.2", "rounds with nu>0 in which the mean mixing coefficient decreased (base runs of FedFACS and FedFACS-A2)", "98.2% of 5,724 (129 runs)", E1, E1 == "98.2% of 5724 (129 runs)", "results/*_fedfacs_s*.json, *_abl_A2_s*.json (log nu, a_mean)")
vals = []
for r in sel("fedfacs", base=True):
    for rd, bl in (r.get("diag") or {}).items():
        if int(rd) >= 5:
            vals += [x["a"] for x in bl]
v = np.array(vals)
E4 = "median %.2f mean %.2f p5-p95 %.3f-%.2f (n=%d)" % (np.median(v), v.mean(), np.percentile(v, 5), np.percentile(v, 95), len(v))
add("E2", "5.4 Mixing", "per-client mixing coefficient at the diagnostic rounds 5-100 (FedFACS base runs)", "median 0.09 mean 0.14 p5-p95 0.001-0.33", E4, E4.startswith("median 0.09 mean 0.14 p5-p95 0.001-0.33"), "results/*_fedfacs_s*.json (diag records)")
'''.split("\n")
L[a:b] = new
t = "\n".join(L)
# the old I4 (mean of per-round means) is replaced by E2
i = t.index('am = np.concatenate([np.array(r["log"]["a_mean"]')
j = t.index('nj, nw, nd = [], [], []')
t = t[:i] + t[j:]
t = t.replace('wF = min(min(r["log"]["weights_min"]) for r in sel("fedfacs", tagged=False))', 'wF = min(min(r["log"]["weights_min"]) for r in sel("fedfacs", base=True))')
open(p, "w", encoding="utf8").write(t)
print("ok")
