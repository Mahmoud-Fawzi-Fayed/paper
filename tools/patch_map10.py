p = r"C:\Users\0xRay\Downloads\paper\tools\build_rep.py"
s = open(p, encoding="utf8").read()

# 1. mapping table builder
fn = '''

def mapping_md():
    f, r, tf, tr = R["abl_A2"], R["random"], T["abl_A2"], T["random"]
    gb = lambda x: x["total_gb"]
    per = lambda x: (x["down"] + x["up"]) * 33.595432 / 1000.0
    rows = [
        ["Models sent per round", r"$\\mathrm{Comm}^t_{\\mathrm{down}}$ divided by the model size", "Down", "%.1f" % f["down"], "%.1f" % r["down"]],
        ["Updates uploaded per round", r"$\\mathrm{Comm}^t_{\\mathrm{up}}$ divided by the model size", "Up", "%.2f" % f["up"], "%.2f" % r["up"]],
        ["Volume per round (GB)", r"$\\mathrm{Comm}^t_{\\mathrm{down}}+\\mathrm{Comm}^t_{\\mathrm{up}}$ (the term $\\mathrm{Comm}^t_{\\mathrm{aux}}$ is below 0.1% of it)", "none", "%.2f" % per(f), "%.2f" % per(r)],
        ["Volume after 100 rounds (GB)", r"$\\mathrm{Comm}_{\\mathrm{total}}(100)$, sum over $t=1,\\dots,100$", "Total GB", "%.1f" % gb(f), "%.1f" % gb(r)],
        ["Uploads to the target", r"$C_{\\mathrm{total}}$ of Eq. (23) at the first round that reaches the target", "Uploads to target", "%.0f" % tf["uploads"], "%.0f" % tr["uploads"]],
        ["Volume to the target (GB)", r"$\\mathrm{Comm}_{\\mathrm{total}}$ of Eq. (23a) at that round", "GB to target", "%.1f" % tf["total_gb"], "%.1f" % tr["total_gb"]],
        ["Saving in uploads", r"$1-C_{\\mathrm{total}}^{\\mathrm{FedFACS}}/C_{\\mathrm{total}}^{\\mathrm{random}}$", "none", "%.1f%%" % (100 * (1 - tf["uploads"] / tr["uploads"])), "none"],
    ]
    cap = ("Reading guide (explanatory, not for the manuscript). Model size: 33.6 MB (trainable weights). Down, Up and the volumes are averages over the 45 runs of each method; "
           "the values of each row follow from the previous rows up to the averaging over runs.")
    return tbl(["Quantity", "Equation term", "Column of Table V", "FedFACS", "Random sampling"], rows, cap)
'''
marker = "\n\ndef section3_md():"
assert s.count(marker) == 1
s = s.replace(marker, fn + marker)

# 2. insert in build_md after section 3
old = "    md.append(section3_md())\n"
assert s.count(old) == 1
s = s.replace(old, old + '    if REP == 10:\n        md.append("\\n# 3a. How each number of Table V follows from Eq. (23a)\\n")\n        md.append(mapping_md())\n')

# 3. widths and alignment
s = s.replace('widths = {10: [[1.6, 0.5, 0.45, 0.5, 0.6, 0.75, 0.65, 0.5, 0.6], [2.4, 4.1]], 9: [[5.2, 1.2], [2.4, 4.1]]}[REP]',
              'widths = {10: [[1.6, 0.5, 0.45, 0.5, 0.6, 0.75, 0.65, 0.5, 0.6], [1.4, 2.3, 1.0, 0.8, 1.0], [2.4, 4.1]], 9: [[5.2, 1.2], [2.4, 4.1]]}[REP]')
s = s.replace("for ti, t in enumerate(doc.tables[:2]):", "for ti, t in enumerate(doc.tables[:len(widths)]):")
s = s.replace("p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (c_i == 0 or len(widths[ti]) == 2) else WD_ALIGN_PARAGRAPH.CENTER",
              "p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (c_i == 0 or len(widths[ti]) == 2 or (REP == 10 and ti == 1 and c_i == 1)) else WD_ALIGN_PARAGRAPH.CENTER")
open(p, "w", encoding="utf8").write(s)
print("ok")
