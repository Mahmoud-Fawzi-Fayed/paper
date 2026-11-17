B=chr(92)
def depth(t):
    d=0
    for ch in t.replace(B+"{","").replace(B+"}",""):
        d+=(ch=="{")-(ch=="}")
    return d
s=open(r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised\sn-article.tex",encoding="utf8").read()
b0=open(r"C:\Users\0xRay\Downloads\paper\paper_overleaf_revised\sn-article_before_910.tex",encoding="utf8").read()
print(depth(s),depth(b0))
a=s.index(B+"textbf{Communication and computation cost.}"); b=s.index(B+"textbf{Uncertainty penalty.}")
blk=s[a:b]
for part in blk.split("\n\n"):
    print(depth(part), part[:60].replace("\n"," "))
