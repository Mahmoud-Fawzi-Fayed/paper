p = r"C:\Users\0xRay\Downloads\paper\tools\build_final56.py"
t = open(p, encoding="utf8").read()
bad = 'md.append("\n# 4a. New section to insert: 4.3\n")'
good = 'md.append(chr(10) + "# 4a. New section to insert: 4.3" + chr(10))'
assert t.count(bad) == 1
t = t.replace(bad, good)
old = "    md.append(body)\n    md.append(NOTATION)\n    md.append(PREP)"
new = ("    md.append(body)\n    md.append(chr(10) + \"# 3a. New section to insert: 4.3\" + chr(10))\n"
       "    md.append(NEW43_NOTE)\n    md.append(section43_md())\n    md.append(NOTATION)\n    md.append(PREP)")
assert t.count(old) == 1
t = t.replace(old, new)
open(p, "w", encoding="utf8").write(t)
import ast
ast.parse(t)
print("ok")
