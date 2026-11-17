import docx,re,sys
d=docx.Document(r"C:\Users\0xRay\Downloads\paper\FedFACS_Replacements_9_10.docx")
t=[p.text for p in d.paragraphs]
txt="\n".join(t)
for bad in ("tab:","@@","\\","Table tab","??","$"):
    print(repr(bad), txt.count(bad))
open(r"C:\Users\0xRay\Downloads\paper\tools\_work\d910.txt","w",encoding="utf8").write(txt)
print(len(t))
