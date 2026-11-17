p = r"C:\Users\0xRay\Downloads\paper\tools\build_rep.py"
s = open(p, encoding="utf8").read()
old = '    if REP == 9:\n        lo, lr = alg_lines(ORIG), alg_lines(REV)'
assert s.count(old) == 1
new = '''    if REP == 10:
        md.append('\\n::: {custom-style="BA-Edit"}\\nEdit 4: range of the fairness term of Eq. (6)\\n:::\\n')
        md.append('::: {custom-style="BA-Loc"}\\nLocation: Section 4.2, directly after Eq. (6) (original line %d)\\n:::\\n' % B.line_of(ORIG, "The counter of idle rounds $r_i^t$"))
        md.append('::: {custom-style="BA-Label-Before"}\\nBefore (remove)\\n:::\\n')
        md.append("No statement of the range of $F_i^t$.\\n")
        md.append('::: {custom-style="BA-Label-After"}\\nAfter (put instead)\\n:::\\n')
        md.append('[Since $0\\\\le r_i^t\\\\le N\\\\,\\\\overline{r^t}$, the fairness term satisfies $1\\\\le F_i^t < N+1$.]{custom-style="Add"}\\n')
        md.append('::: {custom-style="BA-Note"}\\nDeclaration: no new symbol. The bound follows from $\\\\sum_j r_j^t=N\\\\,\\\\overline{r^t}$ and $F_i^t=1+r_i^t/(1+\\\\overline{r^t})$; it is Proposition 1 (ii) of Section 4.3, with its proof, and a unit test checks it.\\n:::\\n')
'''
s = s.replace(old, new + old)
open(p, "w", encoding="utf8").write(s)
print("ok")
