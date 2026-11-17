import os
import shutil

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
p = os.path.join(P, "sn-article.tex")
shutil.copy(p, os.path.join(P, "sn-article_before_nonum7.tex"))
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")


def line_from(text, start):
    i = text.index(start)
    j = text.find("\n", i)
    return i, (len(text) if j < 0 else j)


rho = "$" + B + "rho^{t-1}$"
par = (
    "When " + rho + " indicates sharp improvement, a smaller cohort suffices: the global model is improving quickly, so the upload cost of the round falls without slowing progress, "
    "and the cohort reaches $C_{k_{" + B + "min}}$ at $" + B + "rho^{t-1}" + B + "ge 1$. "
    "When $" + B + "rho^{t-1}" + B + "le 0$ (stagnation or a loss increase) and in the first round ($" + B + "rho^0=0$), the cohort is $C_{k_{" + B + "max}}$: averaging more clients reduces the variance of the aggregate "
    "and supplies more diverse updates, which helps the model to leave the plateau. "
    "Intermediate values are interpolated linearly and rounded to the nearest integer, so that any rounding convention changes a cohort by at most one client and the participation count is insensitive to it. "
    "The absolute reduction " + rho + " is small in our runs and keeps the cohort near $C_{k_{" + B + "max}}$; FedFACS-R therefore measures it against the reference pace of the run, "
    "$e^{t-1}=" + B + "rho^{t-1}/" + B + "Omega^{t}$ ($e^{t-1}=0$ if $" + B + "Omega^{t}" + B + "le 0$), so that a round that progresses at least at that pace selects $C_{k_{" + B + "min}}$ clients "
    "and the whole range $[C_{k_{" + B + "min}},C_{k_{" + B + "max}}]$ is used, which lowers the upload volume without a detectable change in accuracy (Table~" + B + "ref{tab:cohort}). "
    "A candidate whose update is not finite is excluded; if fewer than $m_t$ candidates remain, all of them are selected.")
i, j = line_from(t, "When " + rho + " indicates sharp improvement")
t = t[:i] + par + t[j:]

i = t.index("Moreover, dynamic cohort sizing (FedFACS-A2)")
end = "for any configuration."
j = t.index(end, i) + len(end)
s51 = ("Moreover, dynamic cohort sizing (FedFACS-A2) changes the accuracy only slightly and lowers the upload volume by exactly the reduction of the mean cohort below the fixed size (Table~" + B + "ref{tab:cohort}); "
       "this reduction is bounded by $1-C_{k_{" + B + "min}}/C_{k_{" + B + "max}}$ for any configuration, so wider bounds allow a larger saving.")
t = t[:i] + s51 + t[j:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))
print("ok")
