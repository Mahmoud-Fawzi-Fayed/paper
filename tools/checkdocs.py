import re
import zipfile

import docx

P = r"C:\Users\0xRay\Downloads\paper"
for f in ("FedFACS_Replacements_5_6.docx", "FedFACS_Replacement_6.docx", "FedFACS_Replacements_7_8.docx"):
    path = P + chr(92) + f
    d = docx.Document(path)
    T = [p.text for p in d.paragraphs if p.text.strip()]
    print(f, len(T), "tables", len(d.tables))
    print("  ", [t[:60] for t in T if t.startswith(("NEW ELEMENTS", "NEW SECTION", "4.3 Prop", "Proposition 1"))])
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf8")
    for m in re.finditer(re.escape(chr(92)), x):
        print("   backslash:", x[max(0, m.start() - 80):m.start() + 60])
