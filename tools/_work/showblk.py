B=chr(92)
s=open(r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised\sn-article.tex",encoding="utf8").read()
a=s.index(B+"textbf{Communication and computation cost.}"); b=s.index(B+"textbf{Uncertainty penalty.}")
blk=s[a:b]
for part in blk.split("\n\n"):
    if part.startswith(B+"textbf"): print(part,"\n")
i=blk.index(B+"begin{table}"); print(blk[i:i+2300])
