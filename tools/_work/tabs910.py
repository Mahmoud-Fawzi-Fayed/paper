import docx
d=docx.Document(r"C:\Users\0xRay\Downloads\paper\FedFACS_Replacements_9_10.docx")
for i,t in enumerate(d.tables):
    print("TABLE",i,len(t.rows),"x",len(t.columns))
    for r in t.rows[:4]:
        print(" | ".join(c.text[:28] for c in r.cells))
