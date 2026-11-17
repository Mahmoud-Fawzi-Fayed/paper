p = r"C:\Users\0xRay\Downloads\paper\tools\verify_claims.py"
t = open(p, encoding="utf8").read()
marker = "# ------------------------------------------------------------------ H. propositions, by execution"
add = '''# ------------------------------------------------------------------ K. scale of the utility term, noise AUC
from scipy.stats import rankdata  # noqa: E402

kl_, F_ = [], []
for r in sel("fedfacs", base=True):
    for rd, bl in (r.get("diag") or {}).items():
        if int(rd) >= 5:
            kl_ += [x["kl"] for x in bl]; F_ += [x["F"] for x in bl]
kl_, F_ = np.array(kl_), np.array(F_)
K1 = "median %.3f, 95th percentile %.3f, share below F %.1f%%, share below 1 %.1f%% (n=%d)" % (np.median(kl_), np.percentile(kl_, 95), 100 * (kl_ < F_).mean(), 100 * (kl_ < 1).mean(), len(kl_))
add("K1", "4.2 / 5.4", "scale of the utility term at the diagnostic rounds 5-100 (FedFACS main runs)", "KL typically much smaller than 1; KL < F in nearly all client-rounds", K1, np.median(kl_) < 0.2 and (kl_ < F_).mean() > 0.95, "results/*_fedfacs_s*.json (diag records)")


def _auc(score, lab):
    rk = rankdata(score); n1 = lab.sum(); n0 = len(lab) - n1
    return (rk[lab == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


AU = []
for r in [x for x in sel("fedfacs", sc="s3", base=True)]:
    for bl in r["diag"].values():
        nz = np.array([x["noise"] for x in bl]); v = np.array([x["var"] for x in bl]); lab = (nz > 0.2).astype(int)
        if 0 < lab.sum() < len(lab):
            AU.append(_auc(v, lab))
AU = np.array(AU); lo, hi = bs_ci(AU)
K2 = "%.2f [%.2f, %.2f] (n=%d round-runs, noisy = noise level above 0.2)" % (AU.mean(), lo, hi, len(AU))
add("K2", "5.4 Uncertainty", "rank AUC of the batch variance for label noise", "0.45 [0.39, 0.52] (analysis/noise_discrimination.md)", K2, abs(AU.mean() - 0.45) < 0.006 and abs(lo - 0.39) < 0.015 and abs(hi - 0.52) < 0.01 and len(AU) == 18, "results/*_s3_fedfacs_s*.json (diag records); analysis/noise_discrimination.md")

'''
assert "K1" not in t
t = t.replace(marker, add + marker, 1)
open(p, "w", encoding="utf8").write(t)
print("ok")
