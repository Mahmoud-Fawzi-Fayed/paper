"""Four-line paragraph for Table V (both tex files)."""
BS = chr(92)
NEW = (r"@textbf{Communication, computation and participation.} Table~@ref{tab:cost} evaluates Eq.~(23a): $@mathrm{Comm}^t_{@mathrm{down}}$ and $@mathrm{Comm}^t_{@mathrm{up}}$ equal the number of models sent (Down) and of updates uploaded (Up) times the model size of 33.6~MB, "
       r"$@mathrm{Comm}^t_{@mathrm{aux}}$ is below 0.1@% of the total for every method, Total GB is their sum over 100 rounds, and Uploads to target is $C_{@mathrm{total}}$ of Eq.~(23). "
       r"FedFACS sends the model to all $N=100$ candidates (10.0 times the local steps of random sampling) and uploads 520 updates to the target against 555 (6.2@% fewer), so that its volume is 198 against 37~GB. "
       r"JFI (Eq.~(24), $q_i=1$) is 0.997 against 0.920, with no unselected client.").replace("@", BS)
for f in ("sn-article.tex", "section_5_4_selection_score.tex"):
    p = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised" + "\\" + f
    s = open(p, encoding="utf8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    a = s.index(BS + "textbf{Communication, computation and participation.}")
    b = s.index(BS + "begin{table}", a)
    s = s[:a] + NEW + nl + nl + s[b:]
    open(p, "w", encoding="utf8", newline="").write(s)
    print("ok", f)
