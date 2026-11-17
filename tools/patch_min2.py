import os

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
p = os.path.join(P, "sn-article.tex")
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")
rho = "$" + B + "rho^{t-1}$"
i = t.index("A large " + rho + " means fast progress")
j = t.index("\n", i)
new = ("A large " + rho + " means fast progress, so a smaller cohort suffices and the uploads fall; stagnation or a loss increase ($" + B + "rho^{t-1}" + B + "le 0$) and the first round select $C_{k_{" + B + "max}}$, "
       "since averaging more clients reduces the variance of the aggregate. Values in between are interpolated linearly and rounded to the nearest integer. "
       "Since " + rho + " alone keeps the cohort near $C_{k_{" + B + "max}}$, the ratio $" + B + "rho^{t-1}/" + B + "Omega^{t}$ can replace it, which spans the full range and lowers the uploads without a detectable change in accuracy (Table~" + B + "ref{tab:cohort}). "
       "Clients with a non-finite update are excluded; if fewer than $m_t$ remain, all are selected.")
t = t[:i] + new + t[j:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))
print("ok")
