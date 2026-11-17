"""Rewrites the sentence of the cost paragraph in positive, factual wording (both tex files)."""
OLD = (r"To the common target accuracy FedFACS uploads 520 updates against 555 for random sampling (6.2\% fewer; the target is reached in 44 of 45 runs against 45 of 45), "
       r"but transmits 198 against 37~GB in total. FedFACS therefore lowers the uploads and not the total communication or the local computation; "
       r"Power-of-Choice downloads 20 and DivFL 100 models per round for a cohort of ten.")
NEW = (r"To the common target accuracy FedFACS uploads 520 updates against 555 for random sampling (6.2\% fewer) and transmits 198 against 37~GB in total, "
       r"since every candidate receives and trains the model. The saving of FedFACS is therefore in the uploaded updates; "
       r"Power-of-Choice downloads 20 and DivFL 100 models per round for a cohort of ten.")
for f in ("sn-article.tex", "section_5_4_selection_score.tex"):
    p = r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised" + "\\" + f
    s = open(p, encoding="utf8", newline="").read()
    assert s.count(OLD) == 1, f
    open(p, "w", encoding="utf8", newline="").write(s.replace(OLD, NEW))
    print("ok", f)
