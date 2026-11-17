import os
import shutil

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
p = os.path.join(P, "sn-article.tex")
shutil.copy(p, os.path.join(P, "sn-article_before_here.tex"))
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")
i = t.index("Here $L_{global}^{t}$ is the validation loss after round $t$ ($L_{global}^{0}$: initial model).")
j = t.index("\n", i)
new = ("Here $L_{global}^{t}$ is the validation loss after round $t$ and $L_{global}^{0}$ that of the initial model. Hence $" + B + "rho^{t}" + B + "le 1$: it is positive when the loss falls and negative when it rises, "
       "and a negative value is kept because it selects the maximum cohort. If the previous loss is zero or non-finite, $" + B + "rho^{t}$ is undefined and the round is cancelled with all state unchanged.")
t = t[:i] + new + t[j:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))
print("ok")
