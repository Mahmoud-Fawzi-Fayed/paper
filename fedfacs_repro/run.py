"""Run one experiment: python run.py --dataset cifar10 --scenario s1_0.5 --method fedfacs --seed 0"""
import argparse
import json
import os
import sys

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def default_cfg(**kw):
    cfg = dict(dataset="cifar10", scenario="s1_0.5", method="fedfacs", seed=0, N=100, rounds=100, epochs=2,
               bs=32, lr=None, m=10, cmin=5, cmax=10, B=4, S=256, beta=0.9, lam=1.0, beta_ref=0.9,
               prox=0.1, d=20, clip=50.0, mu=None, diag_rounds=[])
    cfg.update(kw)
    if cfg["lr"] is None:
        cfg["lr"] = 0.05 if cfg["dataset"] == "cifar10" else 0.01
    return cfg


def result_path(cfg, tag=""):
    name = f"{cfg['dataset']}_{cfg['scenario']}_{cfg['method']}_s{cfg['seed']}{tag}.json"
    return os.path.join(RESULTS, name)


def run_one(cfg, tag="", verbose=True, force=False):
    import torch
    from fl import Sim
    path = result_path(cfg, tag)
    if os.path.exists(path) and not force:
        print("skip (exists):", path, flush=True)
        return path
    os.makedirs(RESULTS, exist_ok=True)
    sim = Sim(cfg)
    out = sim.run(cfg["method"], verbose=verbose)
    out["cfg"] = cfg
    with open(path, "w") as f:
        json.dump(out, f)
    del sim
    torch.cuda.empty_cache()
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="cifar10")
    ap.add_argument("--scenario", default="s1_0.5")
    ap.add_argument("--method", default="fedfacs")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--tag", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    cfg = default_cfg(dataset=a.dataset, scenario=a.scenario, method=a.method, seed=a.seed,
                      rounds=a.rounds, epochs=a.epochs)
    print(run_one(cfg, a.tag, force=a.force))
