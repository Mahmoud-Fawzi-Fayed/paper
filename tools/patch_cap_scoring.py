OLD = "Steps and Scoring: local SGD steps and scoring or probing forward passes (thousands) per round."
NEW_TEX = (r"Steps: local SGD steps per round. Scoring: forward passes per round (thousands) that give $\Delta KL_i^t$ and $\sigma_i^2$ of the fitness score, Eq.~(14) (Eqs.~(5) and (12)); for Power-of-Choice and DivFL, the forward passes of their selection.")
NEW_MD = NEW_TEX.replace("Eq.~(14)", "Eq. (14)").replace("Eqs.~(5)", "Eqs. (5)")
BASE = r"C:\Users\0xRay\Downloads\paper"
for f in ("paper_overleaf_revised\\sn-article.tex", "paper_overleaf_revised\\section_5_4_selection_score.tex"):
    s = open(BASE + "\\" + f, encoding="utf8", newline="").read()
    assert s.count(OLD) == 1, f
    open(BASE + "\\" + f, "w", encoding="utf8", newline="").write(s.replace(OLD, NEW_TEX))
p = BASE + r"\tools\build_rep.py"
s = open(p, encoding="utf8").read()
assert s.count(OLD) == 1
open(p, "w", encoding="utf8").write(s.replace(OLD, NEW_MD))
print("ok")
