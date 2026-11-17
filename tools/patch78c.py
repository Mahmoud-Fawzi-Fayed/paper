"""Reconcile abstract, introduction, discussion and conclusion with kappa = 0 (sample-count aggregation)."""
import os
import shutil

P = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised"
p = os.path.join(P, "sn-article.tex")
t = open(p, encoding="utf8", newline="").read()
shutil.copy(p, os.path.join(P, "sn-article_before_78c.tex"))
R = [
    ("Furthermore, we propose a stability-weighted aggregation method that aligns model aggregation with the stability criteria.",
     "Furthermore, we propose a nonnegative normalised aggregation family whose default, the sample-count weighting, keeps the aggregate consistent with the population objective, and we compare it with stability weighting."),
    ("Furthermore, the client contributions are quantified using stability score which is used to adaptively weight global model aggregation.",
     "Furthermore, the client contributions are quantified by a stability score that defines an optional weighting of the global aggregation, which is evaluated against sample-count weights."),
    ("Finally, the server aggregates the uploaded models with their stability weights (Eq. (4))",
     "Finally, the server aggregates the uploaded models with their normalised weights (Eqs. (4) and (18))"),
    ("adaptive cohort sizing, and stability-weighted aggregation, which enhance",
     "adaptive cohort sizing, and normalised nonnegative aggregation weights, which enhance"),
    ("Furthermore, the stability-weighted aggregation strategy improves accuracy by assigning greater weights to updates from more stable clients.",
     "Furthermore, the sample-count aggregation keeps the global model stable at the end of training (Section~\\ref{sec:score_analysis})."),
    ("dynamic cohort sizing, and adaptive stability-weighted aggregation.",
     "dynamic cohort sizing, and normalised aggregation."),
    ("Moreover, stability-aware aggregation is employed, assigning higher weights to reliable client updates, thereby enhancing the stability and reliability of the resulting global model.",
     "Moreover, the aggregation uses nonnegative normalised weights, with sample-count weighting as the default, which gives the more stable global model at the end of training in the comparison of Section~\\ref{sec:score_analysis}."),
]
for a, b in R:
    assert t.count(a) == 1, a[:60]
    t = t.replace(a, b)
open(p, "w", encoding="utf8", newline="").write(t)
print("ok", len(R))
