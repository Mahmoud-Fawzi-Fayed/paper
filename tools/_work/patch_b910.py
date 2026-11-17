p=r"C:\Users\0xRay\Downloads\paper\tools\build_910.py"
s=open(p,encoding="utf8").read()
add='''

SP = chr(0xE000)


def fix_titles(t):
    t = re.sub(r"\\textit\{Cumulative number of selected clients until convergence\s+\(\$C_\{total\}\$\)\}",
               "*Cumulative" + SP + "number" + SP + "of" + SP + "selected" + SP + "clients" + SP + "until" + SP + "convergence" + SP + "($C_{total}$)*", t)
    t = re.sub(r"\\textit\{Jain.s Fairness Index \(JFI\)\}", "*Jain" + SP + "Fairness" + SP + "Index" + SP + "(JFI)*", t)
    return t


for _e in EDITS:
    _e["orig"], _e["rev"] = fix_titles(_e["orig"]), fix_titles(_e["rev"])
'''
marker="\nHEAD = r\"\"\""
assert s.count(marker)==1
s=s.replace(marker, add+marker)
s=s.replace('open(md_path, "w", encoding="utf8").write(build_md())','open(md_path, "w", encoding="utf8").write(build_md().replace(SP, " "))')
open(p,"w",encoding="utf8").write(s)
