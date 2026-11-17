import os

B = chr(92)
P = r"C:\Users\0xRay\Downloads\paper"
tex = [os.path.join(P, "paper_overleaf_revised", f) for f in ("sn-article.tex", "section_5_4_selection_score.tex")]
treps = [
    ("from 3.3 to 1.0 points on FMNIST", "from 3.9 to 1.0 points on FMNIST"),
    ("In the 129 runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2" + B + "% of the 5,724 rounds",
     "In the 96 main runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2" + B + "% of the 4,316 rounds"),
    ("The coefficient of the feedback rule settles at a median of 0.04 (mean 0.10; 5th--95th percentile 0.005--0.32).",
     "At the diagnostic rounds 5 to 100 the coefficients of the clients have a median of 0.10 (mean 0.14; 5th--95th percentile 0.001--0.33)."),
    ("$-0.30$ [$-0.57$, $+0.05$] and last-10-round accuracy $-0.08$ [$-0.56$, $+0.41$]", "$-0.29$ [$-0.57$, $+0.05$] and last-10-round accuracy $-0.08$ [$-0.55$, $+0.41$]"),
    ("the Jain index fell to 0.95--0.99, the longest wait rose to 18--20 rounds", "the Jain index fell to 0.94--0.99, the longest wait rose to 17--20 rounds"),
]
for f in tex:
    t = open(f, encoding="utf8", newline="").read()
    for a, b in treps:
        print(os.path.basename(f), t.count(a), a[:48])
        t = t.replace(a, b)
    open(f, "w", encoding="utf8", newline="").write(t)

for f, reps in ((os.path.join(P, "tools", "build_final56.py"), [
        ("In the 129 runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2% of the 5,724 rounds with ν > 0",
         "In the 96 main runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2% of the 4,316 rounds with ν > 0"),
        ("decreased in 98.2% of 5,724 rounds (129 runs)", "decreased in 98.2% of 4,316 rounds (96 main runs)"),
        ("In the 129 runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2\" + BS + \"% of the 5,724 rounds in which",
         "In the 96 main runs of FedFACS and FedFACS-A2 the mean mixing coefficient decreased in 98.2\" + BS + \"% of the 4,316 rounds in which"),
        ("Jain index of 0.95–0.99, longest waits of 18–20 rounds", "Jain index of 0.94–0.99, longest waits of 17–20 rounds"),
        ("0.95–0.99, longest waits of 18–20", "0.94–0.99, longest waits of 17–20")]),
        (os.path.join(P, "tools", "build_78.py"), [("-0.30 [-0.57, +0.05] (best round) and -0.08 [-0.56, +0.41]", "-0.29 [-0.57, +0.05] (best round) and -0.08 [-0.55, +0.41]"),
                                                   ("accuracy differs by -0.30 [-0.57, +0.05]", "accuracy differs by -0.29 [-0.57, +0.05]"), ("-0.08 [-0.56, +0.41] (last 10 rounds)", "-0.08 [-0.55, +0.41] (last 10 rounds)")])):
    t = open(f, encoding="utf8").read()
    for a, b in reps:
        print(os.path.basename(f), t.count(a), a[:50])
        t = t.replace(a, b)
    open(f, "w", encoding="utf8").write(t)

f = os.path.join(P, "tools", "verify_claims.py")
t = open(f, encoding="utf8").read()
t = t.replace('"98.2% of 5,724 (129 runs)", E1, E1 == "98.2% of 5724 (129 runs)"', '"98.2% of 4,316 (96 runs)", E1, E1 == "98.2% of 4316 (96 runs)"')
t = t.replace('"median 0.09 mean 0.14 p5-p95 0.001-0.33", E4, E4.startswith("median 0.09 mean 0.14 p5-p95 0.001-0.33")', '"median 0.10 mean 0.14 p5-p95 0.001-0.33", E4, E4.startswith("median 0.10 mean 0.14 p5-p95 0.001-0.33")')
t = t.replace('"0.995-0.998 / 10-13 / 0"', '"0.995-0.999 / 10-13 / 0"')
t = t.replace('0.9945 <= min(jr) and max(jr) <= 0.9985', '0.9945 <= min(jr) and max(jr) <= 0.9995')
t = t.replace('"-0.30 [-0.57, +0.05]"', '"-0.29 [-0.57, +0.05]"').replace('"-0.08 [-0.56, +0.41]"', '"-0.08 [-0.55, +0.41]"')
t = t.replace('"0.95-0.99 / 18-20 / -0.5 to -0.8"', '"0.94-0.99 / 17-20 / -0.5 to -0.8"')
open(f, "w", encoding="utf8").write(t)
