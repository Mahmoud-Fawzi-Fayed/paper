import zipfile,re
x=zipfile.ZipFile(r"C:\Users\0xRay\Downloads\paper\FedFACS_Replacements_9_10.docx").read("word/document.xml").decode("utf8")
for s in ("Del","Add","DelBlock","AddBlock"): print(s, len(re.findall(r'w:val="%s"'%s,x)))
