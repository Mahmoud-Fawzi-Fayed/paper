"""Neutral, definitional wording for the two sentences on the fairness index (both tex files)."""
PAIRS = [
    (r"The quality-adjusted index of Eq.~(24) is lower (0.973 and 0.963) because FedFACS serves the clients almost uniformly and not in proportion to $q_i$: the adjusted index equals one only if $p_i$ is proportional to $q_i$, so that",
     r"The quality-adjusted index of Eq.~(24) is 0.973 and 0.963; it equals one when $p_i$ is proportional to $q_i$, whereas FedFACS serves the clients almost uniformly, so that"),
    (r"The minimum value is $1/N$, and a value between $0.5$ and $1$ does not imply that every client participates (serving 90 of 100 equal-quality clients uniformly gives $0.9$).",
     r"The minimum value is $1/N$, and a value between $0.5$ and $1$ can also arise when some clients are never served (serving 90 of 100 equal-quality clients uniformly gives $0.9$)."),
]
for f in ("sn-article.tex", "section_5_4_selection_score.tex"):
    p = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised" + "\\" + f
    s = open(p, encoding="utf8", newline="").read()
    for a, b in PAIRS:
        n = s.count(a)
        if n == 1:
            s = s.replace(a, b)
        else:
            print("skip", f, n, a[:50])
    open(p, "w", encoding="utf8", newline="").write(s)
print("done")
