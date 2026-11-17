import json
r = json.load(open(r"C:\Users\0xRay\Downloads\paper\fedfacs_repro\results\cifar10_s1_0.1_fedfacs_s0_dist.json"))
d = r["diag"]
print(type(d), list(d.keys())[:8] if isinstance(d, dict) else len(d))
k = list(d.keys())[0]
print(k, type(d[k]), len(d[k]), d[k][0] if isinstance(d[k], list) else list(d[k].keys())[:10])
