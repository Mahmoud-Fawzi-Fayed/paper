p=r"C:\Users\0xRay\Downloads\paper\tools\build_910.py"
s=open(p,encoding="utf8").read()
a="per-round selections and cohort sizes, scores' summaries and metrics (JSON); a release statement needs the authors' confirmation."
b="per-round selections, cohort sizes, validation loss and accuracy, the mean mixing coefficient and fairness term, the deviation signal and the traffic counters (JSON); the individual fitness scores of every round are not logged, so a package that includes them needs a rerun; a release statement needs the authors' confirmation."
assert s.count(a)==1
open(p,"w",encoding="utf8").write(s.replace(a,b))
