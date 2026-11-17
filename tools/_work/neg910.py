import re
t=open(r"C:\Users\0xRay\Downloads\paper\tools\_work\final910.md",encoding="utf8").read()
i=t.index("# 2. Edits"); j=t.index("# 4. Notation")
body=t[i:j]
parts=re.split(r"(Before \(remove\)|After \(put instead\))",body)
cur=None
for k in range(1,len(parts),2):
    if parts[k].startswith("After"):
        seg=parts[k+1]
        for m in re.finditer(r"[^.\n]*\b(not|cannot|no |never|neither|unable|could not|unclear|only|however|but)\b[^.\n]*\.",seg):
            print("-",m.group(0).strip()[:260])
# section 3 text
for m in re.finditer(r"[^.\n]*\b(not|cannot|never|unable|but|lower)\b[^.\n]*\.",body[body.index("# 3."):] if "# 3." in body else ""):
    print("S3-",m.group(0).strip()[:260])
