import os
import shutil

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
p = os.path.join(P, "sn-article.tex")
shutil.copy(p, os.path.join(P, "sn-article_before_s51.tex"))
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")
i = t.index("Moreover, dynamic cohort sizing (FedFACS-A2)")
end = "so wider bounds allow a larger saving."
j = t.index(end, i) + len(end)
new = ("Moreover, dynamic cohort sizing (FedFACS-A2) changes the accuracy only slightly. Its saving in uploads relative to a fixed cohort of $C_{k_{" + B + "max}}$ is $1-" + B + "bar m/C_{k_{" + B + "max}}$, "
       "where $" + B + "bar m$ is the mean cohort, and it cannot exceed $1-C_{k_{" + B + "min}}/C_{k_{" + B + "max}}$; it therefore grows with the distance between the two bounds (Table~" + B + "ref{tab:cohort}).")
t = t[:i] + new + t[j:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))

f = r"C:\Users\0xRay\Downloads\paper\tools\build_78.py"
s = open(f, encoding="utf8").read()
a = 'rev=seg(REV, "Moreover, dynamic cohort sizing (FedFACS-A2)", "allow a larger saving."),'
assert a in s
s = s.replace(a, 'rev=seg(REV, "Moreover, dynamic cohort sizing (FedFACS-A2)", "between the two bounds (Table~" + BS + "ref{tab:cohort})."),')
open(f, "w", encoding="utf8").write(s)
print("ok")
