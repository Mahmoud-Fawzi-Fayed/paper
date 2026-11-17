import os
import re

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper"
PT = os.path.join(P, "paper_overleaf_revised")
rho = "$" + B + "rho^{t-1}$"

# 1) the paragraph under Eq. (16)
p = os.path.join(PT, "sn-article.tex")
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")
i = t.index("When " + rho + " is large, the model is improving quickly")
j = t.index("\n", i)
new = ("A large " + rho + " means fast progress, so a smaller cohort suffices and the upload cost falls; a non-positive " + rho + " (stagnation or a loss increase) and the first round select $C_{k_{" + B + "max}}$, "
       "because averaging more clients reduces the variance of the aggregate and helps the model to leave the plateau. "
       "Intermediate values are interpolated linearly and rounded to the nearest integer, so any rounding convention changes a cohort by at most one client. "
       "Because the absolute " + rho + " keeps the cohort near $C_{k_{" + B + "max}}$ in our runs, Eq.~(16) can use the ratio $" + B + "rho^{t-1}/" + B + "Omega^{t}$ instead (zero if $" + B + "Omega^{t}" + B + "le 0$), "
       "which spans the full range and lowers the uploads without a detectable change in accuracy (Table~" + B + "ref{tab:cohort}). "
       "Clients whose update is not finite are excluded; if fewer than $m_t$ remain, all of them are selected.")
t = t[:i] + new + t[j:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))

# 2) drop the name FedFACS-R in section 5.4 (both copies)
for f in ("sn-article.tex", "section_5_4_selection_score.tex"):
    p = os.path.join(PT, f)
    s = open(p, encoding="utf8", newline="").read()
    s = s.replace("(FedFACS-R: the ratio $" + B + "rho^{t-1}/" + B + "Omega^{t}$ replaces $" + B + "rho^{t-1}$ in Eq.~(16))", "(the ratio $" + B + "rho^{t-1}/" + B + "Omega^{t}$ in place of $" + B + "rho^{t-1}$ in Eq.~(16))")
    s = s.replace("Relative pace (FedFACS-R)", "Relative rate")
    print(f, "FedFACS-R left:", s.count("FedFACS-R"))
    open(p, "w", encoding="utf8", newline="").write(s)

# 3) builders
for f in ("build_78.py", "build_missing.py", "build_final56.py"):
    p = os.path.join(P, "tools", f)
    s = open(p, encoding="utf8").read()
    s = s.replace("The efficiency can be measured against the reference pace of the run (FedFACS-R), which uses the whole range.", "The ratio of the loss reduction to the reference rate can replace the absolute reduction, which uses the whole range.")
    s = s.replace("With FedFACS-R the mean cohort", "With the ratio rule the mean cohort").replace("the relative-pace measure (FedFACS-R)", "the ratio rule")
    s = s.replace("Relative pace (FedFACS-R)", "Relative rate").replace("FedFACS-R uses the ratio", "the ratio rule uses the ratio").replace("FedFACS-R", "the ratio rule")
    open(p, "w", encoding="utf8").write(s)

# 4) marker in build_78
p = os.path.join(P, "tools", "build_78.py")
s = open(p, encoding="utf8").read()
a = '"When $" + BS + "rho^{t-1}$ is large"'
assert a in s
s = s.replace(a, '"A large $" + BS + "rho^{t-1}$ means fast progress"')
open(p, "w", encoding="utf8").write(s)
print("ok")
