"""Resumable sweep driver. python sweep.py <plan.json>

plan = {"rounds", "epochs", "datasets", "scenarios", "methods", "seeds", "tag", "extra": {cfg overrides},
        "grid": [{"tag": "_B2", "extra": {"B": 2}}, ...]}      # grid optional: one run set per grid point
Runs are sequential inside one worker; finished runs are skipped, so a crashed worker can simply be restarted.
A failed job is logged and skipped (it never stops the worker).
"""
import json
import sys
import time
import traceback

from run import default_cfg, run_one

if __name__ == "__main__":
    plan = json.load(open(sys.argv[1]))
    grids = plan.get("grid") or [{"tag": plan.get("tag", ""), "extra": {}}]
    jobs = [(g, d, s, m, seed) for seed in plan["seeds"] for g in grids for d in plan["datasets"]
            for s in plan["scenarios"] for m in plan["methods"]]
    print(f"{len(jobs)} jobs", flush=True)
    t0, failed = time.time(), []
    for k, (g, d, s, m, seed) in enumerate(jobs, 1):
        extra = {**plan.get("extra", {}), **g.get("extra", {})}
        cfg = default_cfg(dataset=d, scenario=s, method=m, seed=seed, rounds=plan["rounds"],
                          epochs=plan["epochs"], **extra)
        t1 = time.time()
        try:
            run_one(cfg, g.get("tag", plan.get("tag", "")), verbose=False)
            print(f"[{k}/{len(jobs)}] {d} {s} {m} seed={seed}{g.get('tag', '')} done in {time.time() - t1:.0f}s "
                  f"(elapsed {(time.time() - t0) / 60:.1f} min)", flush=True)
        except Exception:
            failed.append((d, s, m, seed, g.get("tag", "")))
            print(f"[{k}/{len(jobs)}] FAILED {d} {s} {m} seed={seed}{g.get('tag', '')}", flush=True)
            traceback.print_exc()
    print("FAILED JOBS:", failed, flush=True)
    print("ALL DONE", flush=True)
