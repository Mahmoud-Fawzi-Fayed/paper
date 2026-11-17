import re
import zipfile

import docx

P = r"C:\Users\0xRay\Downloads\paper" + chr(92)
for f in ("FedFACS_Missing_Sections_5-8.docx", "FedFACS_Replacements_5_6.docx", "FedFACS_Replacement_6.docx", "FedFACS_Replacements_7_8.docx"):
    d = docx.Document(P + f)
    T = [p.text for p in d.paragraphs if p.text.strip()]
    full = "\n".join(T)
    x = zipfile.ZipFile(P + f).read("word/document.xml").decode("utf8")
    print(f, "paras", len(T), "tables", len(d.tables), "oMath", x.count("<m:oMath>"))
    for bad in ("tab:", "sec:", "eq:", "much smaller than one", "grouped by", "96.7", "1,827", "fairness-first"):
        if bad in full:
            i = full.index(bad)
            print("   FOUND", bad, "|", full[max(0, i - 60):i + 60].replace("\n", " "))
if True:
    d = docx.Document(P + "FedFACS_Missing_Sections_5-8.docx")
    for p in d.paragraphs:
        if p.style.name.startswith(("Heading", "BA-Sub", "BA-Title")) and p.text.strip():
            print("  H:", p.text[:90])
