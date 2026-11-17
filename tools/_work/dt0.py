import docx
d=docx.Document(r"C:\Users\0xRay\Downloads\paper\FedFACS_Replacement_10.docx")
for r in d.tables[0].rows: print(" | ".join(c.text for c in r.cells))
