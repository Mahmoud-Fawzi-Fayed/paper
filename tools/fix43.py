p = r"C:\Users\0xRay\Downloads\paper\tools\build_final56.py"
L = open(p, encoding="utf8").read().split("\n")
a = next(i for i, l in enumerate(L) if l.startswith("NEW43_NOTE"))
b = next(i for i, l in enumerate(L) if l.startswith("def section54_md"))
good = r'''NEW43_NOTE = ('::: {custom-style="BA-Note"}' + chr(10) + 'NEW SECTION: Section 4.3 does not exist in the original paper. Insert it as a new subsection after Section 4.2 and before Section 5 (Experimental Evaluation). '
              'Its full text follows; the replacements refer to it as "Section 4.3".' + chr(10) + ':::' + chr(10))


def section43_md():
    NLC = chr(10)
    i = REV.index(BS + "subsection{Properties of FedFACS}")
    j = REV.index(BS + "section{Experimental Evaluation}")
    t = NLC.join(l for l in REV[i:j].split(NLC) if not l.lstrip().startswith("%"))
    t = re.sub(BSR + r"subsection\{[^}]*\}" + BSR + r"label\{[^}]*\}", "", t)
    t = t.replace(BS + "hfill$" + BS + "square$", "$" + BS + "square$")
    paras = [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]
    out = ['::: {custom-style="BA-Sub"}' + NLC + '4.3 Properties of FedFACS (new subsection)' + NLC + ':::' + NLC]
    for p in paras:
        out.append(conv_text(" ".join(p.split(NLC))) + NLC)
    return NLC.join(out)

'''.split("\n")
L[a:b] = good
open(p, "w", encoding="utf8").write("\n".join(L))
print("fixed")
