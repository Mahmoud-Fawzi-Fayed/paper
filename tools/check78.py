import re

t = open(r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised\sn-article.tex", encoding="utf8").read()
B = chr(92)
for env in ("table", "equation"):
    print(env, t.count(B + "begin{" + env + "}"), t.count(B + "end{" + env + "}"))
print("tab:cohort label", t.count("label{tab:cohort}"), "refs", t.count("ref{tab:cohort}"))
d = 0
for ch in t.replace(B + "{", "").replace(B + "}", ""):
    d += (ch == "{") - (ch == "}")
print("brace depth", d)
for lab in set(re.findall(re.escape(B) + r"ref\{([^}]*)\}", t)):
    if t.count("label{" + lab + "}") == 0:
        print("missing label", lab)
print("CR+ef corruption:", t.count("\ref") if False else t.count("\ref"))
