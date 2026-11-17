p = r"C:\Users\0xRay\Downloads\paper\tools\build_rep.py"
s = open(p, encoding="utf8").read()
s = s.replace("Communication, computation and participation.}", "Communication and participation.}")
a = s.index('    cap = (r"Table V.')
b = s.index('    return tbl(["Method", "Down"')
new = ('    cap = (r"Table V. Methods under one communication model (45 runs each; 100 rounds; $N=100$). Steps: local SGD steps per round. To target: $C_{\\mathrm{total}}$ and $\\mathrm{Comm}_{\\mathrm{total}}$ at the first round that reaches the common target accuracy. "\n'
       '           r"JFI: Eq. (24) with $q_i=1$. Never: percentage of clients with $p_i=0$.")\n')
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf8").write(s)
print("ok")
