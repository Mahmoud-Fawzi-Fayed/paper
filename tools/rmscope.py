p = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised\sn-article.tex"
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")
i = t.index(chr(92) + "textbf{Scope.} We do not derive a convergence rate")
j = t.index("\n", i)
t = t[:i] + t[j + 2:] if t[j:j + 2] == "\n\n" else t[:i] + t[j + 1:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))
print("removed")
