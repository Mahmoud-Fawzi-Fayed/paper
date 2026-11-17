import os
import re

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper"
PT = os.path.join(P, "paper_overleaf_revised")

# 1) manuscript: paragraph under Eq. (16)
p = os.path.join(PT, "sn-article.tex")
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")
i = t.index("Since the absolute reduction $" + B + "rho^{t-1}$ keeps the cohort near")
j = t.index("Candidates whose update is not finite are excluded", i)
new = ("Since the absolute reduction $" + B + "rho^{t-1}$ keeps the cohort near $C_{k_{" + B + "max}}$ in our runs, FedFACS-R replaces it in Eq.~(16) by the ratio $" + B + "rho^{t-1}/" + B + "Omega^{t}$ of the reduction to the reference rate "
       "(taken as zero when $" + B + "Omega^{t}" + B + "le 0$): a round that progresses at least at the reference rate selects $C_{k_{" + B + "min}}$ clients, so the full range is used and the uploads fall without a detectable change in accuracy (Table~" + B + "ref{tab:cohort}). ")
t = t[:i] + new + t[j:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))

# 2) section 5.4 paragraph (both copies)
old = "($e^{t-1}=" + B + "rho^{t-1}/" + B + "Omega^{t}$, FedFACS-R)"
new2 = "(FedFACS-R: the ratio $" + B + "rho^{t-1}/" + B + "Omega^{t}$ replaces $" + B + "rho^{t-1}$ in Eq.~(16))"
for f in ("sn-article.tex", "section_5_4_selection_score.tex"):
    p = os.path.join(PT, f)
    s = open(p, encoding="utf8", newline="").read()
    print(f, s.count(old))
    s = s.replace(old, new2)
    open(p, "w", encoding="utf8", newline="").write(s)

# 3) builders
p = os.path.join(P, "tools", "build_78.py")
s = open(p, encoding="utf8").read()
k = s.index("| $" + B + "Omega^{t}$, $e^{t-1}=")
e = s.index("\n", k)
s = s[:k] + "| $" + B + "Omega^{t}$ | reference convergence rate (Eq. (11)); FedFACS-R uses the ratio $" + B + "rho^{t-1}/" + B + "Omega^{t}$ in Eq. (16), taken as zero when $" + B + "Omega^{t}" + B + "le 0$ |" + s[e:]
open(p, "w", encoding="utf8").write(s)

p = os.path.join(P, "tools", "build_missing.py")
s = open(p, encoding="utf8").read()
s = s.replace("$m(e)=", "$m(x)=").replace("clip}(e,0,1)", "clip}(x,0,1)").replace("$m(e)$", "$m(x)$").replace("m(e)" + B + "le", "m(x)" + B + "le").replace("every real $e$", "every real $x$").replace("nonincreasing in $e$", "nonincreasing in $x$")
open(p, "w", encoding="utf8").write(s)
print("left e-symbols in missing:", len(re.findall(r"m\(e\)|real \$e\$|in \$e\$", s)))
