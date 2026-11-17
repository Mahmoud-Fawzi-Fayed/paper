import os

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper"
files = [os.path.join(P, "paper_overleaf_revised", f) for f in ("sn-article.tex", "section_5_4_selection_score.tex")]
reps = [
    ("When $" + B + "nu^t>0$ the mean mixing coefficient decreased in 96.7" + B + "% of 1,827 rounds, as Eq.~(8) predicts.",
     "In the 129 runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2" + B + "% of the 5,724 rounds in which $" + B + "nu^t>0$, as Eq.~(8) predicts."),
    ("from 3.9 to 1.0 points on FMNIST", "from 3.3 to 1.0 points on FMNIST"),
    ("(Jain index 0.995--0.998, longest wait 10--13 rounds", "(Jain index 0.995--0.999, longest wait 10--13 rounds"),
    ("the Jain index of the selection counts was 0.995--0.998", "the Jain index of the selection counts was 0.995--0.999"),
]
for f in files:
    t = open(f, encoding="utf8", newline="").read()
    for a, b in reps:
        n = t.count(a)
        print(os.path.basename(f), n, a[:50])
        t = t.replace(a, b)
    open(f, "w", encoding="utf8", newline="").write(t)

f = os.path.join(P, "tools", "build_final56.py")
t = open(f, encoding="utf8").read()
t = t.replace("When ν > 0 the mean mixing coefficient decreased in 96.7% of 1,827 rounds; Table Y.",
              "In the 129 runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2% of the 5,724 rounds with ν > 0; Table Y.")
t = t.replace("When the deviation signal is positive the mean mixing coefficient decreased in 96.7% of 1,827 rounds, as Eq. (8) predicts.",
              "When the deviation signal is positive the mean mixing coefficient decreased in 98.2% of 5,724 rounds (129 runs), as Eq. (8) predicts.")
t = t.replace('"When $" + BS + "nu^t>0$ the mean mixing coefficient decreased in 96.7" + BS + "% of 1,827 rounds, as Eq.~(8) predicts."',
              '"In the 129 runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2" + BS + "% of the 5,724 rounds in which $" + BS + "nu^t>0$, as Eq.~(8) predicts."')
open(f, "w", encoding="utf8").write(t)
print("1,827 left in builder:", t.count("1,827"))
f = os.path.join(P, "tools", "build_78.py")
t = open(f, encoding="utf8").read()
t = t.replace("Jain index 0.995-0.998;", "Jain index 0.995-0.999;")
open(f, "w", encoding="utf8").write(t)
