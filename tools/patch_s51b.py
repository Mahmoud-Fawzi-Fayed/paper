import os
import shutil

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
p = os.path.join(P, "sn-article.tex")
shutil.copy(p, os.path.join(P, "sn-article_before_s51b.tex"))
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")
i = t.index("Moreover, dynamic cohort sizing (FedFACS-A2)")
end = "between the two bounds (Table~" + B + "ref{tab:cohort})."
j = t.index(end, i) + len(end)
new = ("Moreover, dynamic cohort sizing (FedFACS-A2) changes the accuracy only slightly. Relative to a fixed cohort of $C_{k_{" + B + "max}}$ clients, it saves the fraction by which the mean cohort size falls below $C_{k_{" + B + "max}}$; "
       "this fraction cannot exceed $1-C_{k_{" + B + "min}}/C_{k_{" + B + "max}}$, so it grows with the distance between the two bounds (Table~" + B + "ref{tab:cohort}).")
t = t[:i] + new + t[j:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))
f = r"C:\Users\0xRay\Downloads\paper\tools\build_78.py"
s = open(f, encoding="utf8").read()
a = '"between the two bounds (Table~" + BS + "ref{tab:cohort})."'
assert a in s
s = s.replace(a, '"distance between the two bounds (Table~" + BS + "ref{tab:cohort})."')
open(f, "w", encoding="utf8").write(s)
print("ok")
