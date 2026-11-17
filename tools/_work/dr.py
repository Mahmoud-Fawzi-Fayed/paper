import docx,sys
for n in (9,10):
    d=docx.Document(r"C:\Users\0xRay\Downloads\paper\FedFACS_Replacement_%d.docx"%n)
    t="\n".join(p.text for p in d.paragraphs)
    print(n,len(d.tables),[b for b in ("tab:","@@","\\","$") if b in t])
    if n==10:
        print(t[t.index("3. New text"):][:1600])
        for r in d.tables[0].rows: print(" | ".join(c.text for c in r.cells))
