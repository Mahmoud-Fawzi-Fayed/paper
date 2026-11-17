p=r"C:\Users\0xRay\Downloads\paper\tools\build_rep.py"
s=open(p,encoding="utf8").read()
a='rev=upto_eol(REV, BS + "textit{Cumulative number of selected", CT)'
assert s.count(a)==1
s=s.replace(a,'rev=upto_eol(REV, BS + "textit{Cumulative number of selected", "control messages in round $t$.")')
open(p,"w",encoding="utf8").write(s)
