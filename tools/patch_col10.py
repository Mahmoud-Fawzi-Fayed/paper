import json
import re

BS = chr(92)
P = r"C:\Users\0xRay\Downloads\paper"
O = json.load(open(P + r"\tools\_work\ev910.json"))
R, T, PT = O["resource"], O["target"], O["part"]
names = [("random", "Random sampling (FedAvg)"), ("powd", "Power-of-Choice"), ("oort", "Oort"), ("divfl", "DivFL"), ("abl_A2", "FedFACS ($" + BS + "kappa=0$)")]
rows = []
for k, nm in names:
    r, t, p = R[k], T[k], PT[k]
    rows.append("%s & %.1f & %.2f & %.0f & %.1f & %.1f & %.0f & %.1f & %.3f & %.1f %s" % (nm, r["down"], r["up"], r["steps"], r["fwd_k"], r["total_gb"], t["uploads"], t["total_gb"], p["jfi"], p["never"], BS + BS))
HEAD = "Method & Down & Up & Steps & Scoring & Total GB & Uploads to target & GB to target & JFI & Never (" + BS + "%) " + BS + BS

for f in ("sn-article.tex", "section_5_4_selection_score.tex"):
    path = P + r"\paper_overleaf_revised" + "\\" + f
    s = open(path, encoding="utf8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    a = s.index("Method & Down & Up & Steps & Total GB")
    b = s.index(BS + "bottomrule", a)
    s = s[:a] + HEAD + nl + BS + "midrule" + nl + nl.join(rows) + nl + s[b:]
    s = s.replace("lcccccccc@{}}", "lccccccccc@{}}", 1) if "Scoring & Total GB" in s else s
    old = "Steps: local SGD steps per round."
    assert s.count(old) == 1, f
    s = s.replace(old, "Steps and Scoring: local SGD steps and scoring or probing forward passes (thousands) per round.")
    open(path, "w", encoding="utf8", newline="").write(s)
    print("ok", f)

# build_rep: table and widths
p = P + r"\tools\build_rep.py"
s = open(p, encoding="utf8").read()
s = s.replace('"%.0f" % r["steps"], "%.1f" % r["total_gb"]', '"%.0f" % r["steps"], "%.1f" % r["fwd_k"], "%.1f" % r["total_gb"]')
s = s.replace('["Method", "Down", "Up", "Steps", "Total GB"', '["Method", "Down", "Up", "Steps", "Scoring", "Total GB"')
s = s.replace("Steps: local SGD steps per round.", "Steps and Scoring: local SGD steps and scoring or probing forward passes (thousands) per round.")
s = s.replace("[[1.6, 0.5, 0.45, 0.5, 0.6, 0.75, 0.65, 0.5, 0.6], [1.4", "[[1.5, 0.45, 0.4, 0.5, 0.55, 0.5, 0.7, 0.6, 0.45, 0.5], [1.4")
open(p, "w", encoding="utf8").write(s)
print("build ok")
