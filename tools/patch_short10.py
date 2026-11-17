"""Replacement 10, shortest form (both tex files)."""
import re

BS = chr(92)


def L(s):
    return s.replace("@", BS)


RTT_OLD = L(r"@textit{Round-to-accuracy}: ")
RTT_NEW = L(r"@textit{Round-to-accuracy}: defines the first completed round at which the validation accuracy reaches the target; a run that does not reach it is recorded as not reached. Fewer rounds indicate faster convergence.")
EQ_NEW = L("""The total communication in bytes is
@begin{equation}
@mathrm{Comm}_{@mathrm{total}}(T)=@sum_{t=1}^{T}@left(@mathrm{Comm}^t_{@mathrm{down}}+@mathrm{Comm}^t_{@mathrm{up}}+@mathrm{Comm}^t_{@mathrm{aux}}@right)
@tag{23a}
@end{equation}
where $@mathrm{Comm}^t_{@mathrm{down}}$, $@mathrm{Comm}^t_{@mathrm{up}}$ and $@mathrm{Comm}^t_{@mathrm{aux}}$ are the bytes of the models sent, the updates uploaded and the control messages in round $t$.""")
JFI_NEW = L("""Therefore $JFI = 1$ means participation proportional to quality, and equal participation for $q_i=1$; the minimum value is $1/N$. The percentage of clients that are never selected is reported with the index (Table~@ref{tab:cost}).""")
PARA = L(r"""@textbf{Communication and participation.} Table~@ref{tab:cost} gives the terms of Eq.~(23a): Down and Up are the models sent and the updates uploaded per round (times the model size of 33.6~MB), and Total GB is their sum over 100 rounds. FedFACS sends the model to all $N=100$ candidates and uploads 520 updates to the target against 555 for random sampling (6.2@% fewer), at 198 against 37~GB.""")
CAP = L(r"""@caption{Methods under one communication model (45 runs each; 100 rounds; $N=100$). Steps: local SGD steps per round. To target: $C_{@mathrm{total}}$ and $@mathrm{Comm}_{@mathrm{total}}$ at the first round that reaches the common target accuracy. JFI: Eq.~(24) with $q_i=1$. Never: percentage of clients with $p_i=0$.}""")


def cut(s, a, b, new, incl=True):
    i = s.index(a)
    j = s.index(b, i) + (len(b) if incl else 0)
    return s[:i] + new + s[j:]


for f in ("sn-article.tex", "section_5_4_selection_score.tex"):
    p = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised" + "\\" + f
    s = open(p, encoding="utf8", newline="").read()
    crlf = "\r\n" in s
    s = s.replace("\r\n", "\n")
    if f == "sn-article.tex":
        i = s.index(RTT_OLD)
        j = s.index("\n", i)
        s = s[:i] + RTT_NEW + s[j:]
        s = cut(s, "The total communication in bytes over the first $T$ rounds is", "(Table~" + BS + "ref{tab:cost}).", EQ_NEW)
        s = cut(s, "Therefore $JFI = 1$ means", "(Table~" + BS + "ref{tab:cost}).", JFI_NEW)
    s = cut(s, BS + "textbf{Communication, computation and participation.}", BS + "begin{table}", PARA + "\n\n", incl=False)
    i = s.index(BS + "caption{Communication, computation and participation")
    j = s.index("\n", i)
    s = s[:i] + CAP + s[j:]
    open(p, "w", encoding="utf8", newline="").write(s.replace("\n", "\r\n") if crlf else s)
    print("ok", f)
