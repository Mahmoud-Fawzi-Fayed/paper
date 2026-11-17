import os
import shutil

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
p = os.path.join(P, "sn-article.tex")
shutil.copy(p, os.path.join(P, "sn-article_before_short7b.tex"))
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")
rho = "$" + B + "rho^{t-1}$"
par = (
    "When " + rho + " is large, the model is improving quickly and a smaller cohort suffices, which lowers the upload cost without slowing progress; the cohort reaches $C_{k_{" + B + "min}}$ at $" + B + "rho^{t-1}" + B + "ge 1$. "
    "When $" + B + "rho^{t-1}" + B + "le 0$ (stagnation or a loss increase) and in the first round, the cohort is $C_{k_{" + B + "max}}$: averaging more clients reduces the variance of the aggregate and helps the model to leave the plateau. "
    "Intermediate values are interpolated linearly and rounded to the nearest integer, which changes a cohort by at most one client relative to any other rounding convention. "
    "Since the absolute reduction " + rho + " keeps the cohort near $C_{k_{" + B + "max}}$ in our runs, FedFACS-R uses $e^{t-1}=" + B + "rho^{t-1}/" + B + "Omega^{t}$ ($e^{t-1}=0$ if $" + B + "Omega^{t}" + B + "le 0$) in Eq.~(16): "
    "a round that progresses at the reference pace selects $C_{k_{" + B + "min}}$ clients, so the full range is used and the uploads fall without a detectable change in accuracy (Table~" + B + "ref{tab:cohort}). "
    "Candidates whose update is not finite are excluded; if fewer than $m_t$ remain, all of them are selected.")
i = t.index("When " + rho + " indicates sharp improvement, a smaller cohort suffices")
j = t.index("\n", i)
t = t[:i] + par + t[j:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))

f = os.path.join(r"C:\Users\0xRay\Downloads\paper\tools", "build_78.py")
s = open(f, encoding="utf8").read()
a = 'rev=upto_eol(REV, "On the server-side, it receives fitness scores", "When $" + BS + "rho^{t-1}$ indicates sharp improvement"),'
assert a in s
s = s.replace(a, 'rev=upto_eol(REV, "On the server-side, it receives fitness scores", "When $" + BS + "rho^{t-1}$ is large"),')
open(f, "w", encoding="utf8").write(s)
print("ok")
