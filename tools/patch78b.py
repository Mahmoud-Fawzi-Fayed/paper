import os

P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
old = r"The saving of either rule is bounded by $1-C_{k_{\min}}/C_{k_{\max}}$."
new = (old + r" The cohort size is the number of uploads per round; the cumulative uploads to a target accuracy are the sum of the cohort sizes over the rounds needed to reach it, "
       r"so that a reduction of the cumulative count can come from smaller cohorts or from fewer rounds, and the two are reported separately (Section~\ref{sec:score_analysis} and the round-to-target columns of Section 5).")
for f in ("sn-article.tex", "section_5_4_selection_score.tex"):
    p = os.path.join(P, f)
    t = open(p, encoding="utf8", newline="").read()
    assert t.count(old) == 1 and "reported separately" not in t, f
    open(p, "w", encoding="utf8", newline="").write(t.replace(old, new))
print("ok")
