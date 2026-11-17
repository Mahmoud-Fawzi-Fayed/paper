import os
import shutil

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
p = os.path.join(P, "sn-article.tex")
shutil.copy(p, os.path.join(P, "sn-article_before_short7.tex"))
t = open(p, encoding="utf8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
t = t.replace("\r\n", "\n")


def line_from(text, start):
    i = text.index(start)
    j = text.find("\n", i)
    return i, (len(text) if j < 0 else j)


# 1) the long paragraph below Eq. (16)
i, j = line_from(t, "When $" + B + "rho^{t-1}$ indicates sharp improvement")
new_par = (
    "When $" + B + "rho^{t-1}$ indicates sharp improvement the cohort decreases; it equals $C_{k_{" + B + "max}}$ when $" + B + "rho^{t-1}" + B + "le 0$ (stagnation or a loss increase) and in the first round ($" + B + "rho^0=0$), "
    "and it reaches $C_{k_{" + B + "min}}$ at $" + B + "rho^{t-1}" + B + "ge 1$. Intermediate values are interpolated linearly and rounded to the nearest integer, which changes a cohort by at most one client relative to any other rounding convention. "
    "Because $" + B + "rho^{t-1}$ is an absolute loss reduction, it kept the cohort at $C_{k_{" + B + "max}}$ in 75" + B + "% of the rounds in our runs (Section~" + B + "ref{sec:score_analysis}). "
    "FedFACS-R therefore uses the relative efficiency $e^{t-1}=" + B + "rho^{t-1}/" + B + "Omega^{t}$ ($e^{t-1}=0$ if $" + B + "Omega^{t}" + B + "le 0$) in Eq.~(16), so that a round that progresses at the reference pace selects $C_{k_{" + B + "min}}$ clients (Table~" + B + "ref{tab:cohort}). "
    "A candidate whose update is not finite is excluded; if fewer than $m_t$ candidates remain, all of them are selected.")
t = t[:i] + new_par + t[j:]

# 2) the sentence on the loss terms
i, j = line_from(t, "Here $L_{global}^{t}$ is the validation loss of the global model after round $t$")
old = t[i:j]
new_s = ("Here $L_{global}^{t}$ is the validation loss after round $t$ ($L_{global}^{0}$: initial model). A negative $" + B + "rho^{t}$ is a loss increase and is kept; a zero or non-finite previous loss cancels the round.")
t = t[:i] + new_s + t[j:]

# 3) Section 5.1 sentence
i = t.index("Moreover, introducing dynamic cohort sizing in FedFACS-A2")
end = "for any configuration."
j = t.index(end, i) + len(end)
new5 = ("Moreover, dynamic cohort sizing (FedFACS-A2) changes the accuracy only slightly and lowers the upload volume by the reduction of the mean cohort below the fixed size, 1.7" + B + "% in our runs (bounds 5 and 10, Table~" + B + "ref{tab:cohort}); "
        "this saving cannot exceed $1-C_{k_{" + B + "min}}/C_{k_{" + B + "max}}$ for any configuration.")
t = t[:i] + new5 + t[j:]
open(p, "w", encoding="utf8", newline="").write(t.replace("\n", nl))
print("ok; old sentence kept after Here:", old[-60:])
