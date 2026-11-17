"""Federated simulator: FedFACS (corrected spec, ablation switches) and baselines.

One process = one (dataset, scenario, method, seed) run; per-round log is returned as a dict.
v2 adds: gradient clipping, failed-update exclusion, staged commit (non-finite rounds are cancelled),
confusion matrices, memory logging, utility-validity diagnostics, a rescaled-mixing variant,
noisy-label scenarios, and FedNova / q-FFL-style baselines.
"""
import math
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import spec
from data import build_stem, make_federation, NUM_CLASSES

torch.backends.cudnn.benchmark = True


# ----------------------------------------------------------------------------- model
class Head(nn.Module):
    """layer4 + global-avg-pool + fc, trained in FL. BatchNorm statistics are frozen (eval mode),
    so BN buffers keep their round-start values as required by the specification."""

    def __init__(self, layer4, fc):
        super().__init__()
        self.layer4, self.fc = layer4, fc

    def feats_ref(self, x):
        """Reference path through torchvision's layer4 (used only to validate the fast path)."""
        return self.layer4(x).mean((2, 3))

    @staticmethod
    def _bn(bn, h):
        sc = bn.weight * torch.rsqrt(bn.running_var + bn.eps)
        return h * sc + (bn.bias - bn.running_mean * sc)

    def feats(self, x):
        """Exact matrix-multiply form of layer4 for 2x2 inputs (verified in test_fast.py)."""
        b1, b2 = self.layer4[0], self.layer4[1]
        B = x.shape[0]
        w = b1.conv1.weight[:, :, 1:, 1:].reshape(512, -1)
        h = F.relu(self._bn(b1.bn1, x.reshape(B, -1) @ w.t()))
        h = self._bn(b1.bn2, h @ b1.conv2.weight[:, :, 1, 1].t())
        d = self._bn(b1.downsample[1], x[:, :, 0, 0] @ b1.downsample[0].weight[:, :, 0, 0].t())
        y = F.relu(h + d)
        h = F.relu(self._bn(b2.bn1, y @ b2.conv1.weight[:, :, 1, 1].t()))
        h = self._bn(b2.bn2, h @ b2.conv2.weight[:, :, 1, 1].t())
        return F.relu(h + y)

    def forward(self, x):
        return self.fc(self.feats(x))

    def train(self, mode=True):
        return super().train(False)


def init_head(seed, dev):
    _, m = build_stem()
    g = torch.Generator().manual_seed(seed)
    fc = nn.Linear(512, NUM_CLASSES)
    with torch.no_grad():
        fc.weight.copy_(torch.randn(NUM_CLASSES, 512, generator=g) * 0.01)
        fc.bias.zero_()
    return Head(m.layer4, fc).to(dev).eval()


# ----------------------------------------------------------------------------- variants
FEDFACS_VARIANTS = {
    "fedfacs":       dict(cohort="adaptive", agg="stab",    mix="ctrl",  mu=1.0, utility="kl"),
    "abl_A1":        dict(cohort="fixed",    agg="samples", mix="ctrl",  mu=1.0, utility="kl"),
    "abl_A2":        dict(cohort="adaptive", agg="samples", mix="ctrl",  mu=1.0, utility="kl"),
    "abl_fixmix":    dict(cohort="adaptive", agg="stab",    mix="fixed", mu=1.0, utility="kl"),
    # fixed small mixing coefficients (the controller's observed median is 0.04, mean 0.10): is the controller needed?
    "abl_fix05":     dict(cohort="adaptive", agg="stab",    mix="fixed", mu=1.0, utility="kl", a_fixed=0.05),
    "abl_fix10":     dict(cohort="adaptive", agg="stab",    mix="fixed", mu=1.0, utility="kl", a_fixed=0.10),
    "abl_nofair":    dict(cohort="adaptive", agg="stab",    mix="one",   mu=1.0, utility="kl"),
    "abl_nopen":     dict(cohort="adaptive", agg="stab",    mix="ctrl",  mu=0.0, utility="kl"),
    "abl_loss":      dict(cohort="adaptive", agg="stab",    mix="ctrl",  mu=1.0, utility="loss"),
    "abl_randscore": dict(cohort="adaptive", agg="samples", mix="ctrl",  mu=1.0, utility="rand"),
    # utility and its variance divided by the previous round's mean utility (scale-matched to F ~ O(1))
    "a2_fix05":      dict(cohort="adaptive", agg="samples", mix="fixed", mu=1.0, utility="kl", a_fixed=0.05),
    "a2_fix10":      dict(cohort="adaptive", agg="samples", mix="fixed", mu=1.0, utility="kl", a_fixed=0.10),
    "a2_fix50":      dict(cohort="adaptive", agg="samples", mix="fixed", mu=1.0, utility="kl", a_fixed=0.50),
    "a2_nofair":     dict(cohort="adaptive", agg="samples", mix="one",   mu=1.0, utility="kl"),
    "a2_nopen":      dict(cohort="adaptive", agg="samples", mix="ctrl",  mu=0.0, utility="kl"),
    "norm_a25":      dict(cohort="adaptive", agg="stab",    mix="fixed", mu=1.0, utility="kl", norm=True, guard=True, a_fixed=0.25),
    "norm_a50":      dict(cohort="adaptive", agg="stab",    mix="fixed", mu=1.0, utility="kl", norm=True, guard=True, a_fixed=0.50),
    "abl_rescale":   dict(cohort="adaptive", agg="stab",    mix="ctrl",  mu=1.0, utility="kl", rescale=True),
}
BASELINES = ["random", "fedprox", "powd", "divfl", "oort", "fednova", "qffl", "fairfedcs", "greedy"]
FAIR_REP = ("fairfedcs", "greedy")
ALL_METHODS = list(FEDFACS_VARIANTS) + BASELINES


class Sim:
    def __init__(self, cfg, dev="cuda"):
        self.cfg, self.dev = cfg, dev
        c = cfg
        self.fed = make_federation(c["dataset"], c["scenario"], c["N"], c["seed"], dev)
        self.N = c["N"]
        self.n = self.fed["n"]
        self.rng = np.random.default_rng(c["seed"])
        self.gen = torch.Generator(device=dev).manual_seed(c["seed"])
        torch.manual_seed(c["seed"])
        self.gm = init_head(c["seed"], dev)  # global model (same init for every method of a seed)
        self.wm = init_head(c["seed"], dev)  # work model
        self.em = init_head(c["seed"], dev)  # scratch model: staged evaluation and diagnostics
        for m_ in (self.gm, self.em):
            m_.requires_grad_(False)
        self._graphs = {}
        self.gp, self.wp, self.ep = list(self.gm.parameters()), list(self.wm.parameters()), list(self.em.parameters())
        self.nbytes = sum(p.numel() for p in self.gp) * 4
        self.Xv = self.fed["X"][self.fed["val"]]
        self.Yv = self.fed["Y"][self.fed["val"]]
        self.S = c["S"]
        self.score_ids, self.score_off, off = [], [0], 0
        for i in range(self.N):
            ids = self.fed["tr"][i]
            sid = ids[torch.randperm(len(ids), generator=torch.Generator().manual_seed(c["seed"] * 1000 + i))[: self.S].to(dev)]
            self.score_ids.append(sid)
            off += len(sid)
            self.score_off.append(off)
        cat = torch.cat(self.score_ids)
        self.score_X = self.fed["X"][cat]
        self.score_Y = self.fed["Yn"][cat]  # clients only know their (possibly noisy) labels
        self.clip_hits = 0
        self.failed_updates = 0
        self.invalid_rounds = 0

    # ------------------------------------------------------------------ evaluation
    @torch.no_grad()
    def _eval(self, X, Y, chunk=5000, model=None):
        model = model or self.gm
        loss = torch.zeros((), device=self.dev)
        corr = torch.zeros((), device=self.dev)
        for s in range(0, len(X), chunk):
            out = model(X[s:s + chunk].float())
            loss += F.cross_entropy(out, Y[s:s + chunk], reduction="sum")
            corr += (out.argmax(1) == Y[s:s + chunk]).sum()
        return (loss / len(X)).item(), (corr / len(X)).item()

    def val(self, model=None):
        return self._eval(self.Xv, self.Yv, model=model)

    def test(self):
        return self._eval(self.fed["Xte"], self.fed["Yte"])[1]

    @torch.no_grad()
    def per_client_acc(self):
        accs = []
        for i in range(self.N):
            ids = self.fed["lt"][i]
            accs.append(self._eval(self.fed["X"][ids], self.fed["Y"][ids])[1])
        return accs

    @torch.no_grad()
    def confusion(self):
        out = self.gm(self.fed["Xte"].float()).argmax(1).cpu().numpy()
        y = self.fed["Yte"].cpu().numpy()
        cm = np.zeros((NUM_CLASSES, NUM_CLASSES), int)
        np.add.at(cm, (y, out), 1)
        return cm.tolist()

    # ------------------------------------------------------------------ local training
    def _graph_step(self, mu_prox):
        """CUDA-graph-captured clipped SGD step on a fixed-size, masked batch (exact: BN in eval mode)."""
        key = float(mu_prox)
        if key in self._graphs:
            return self._graphs[key]
        dev, bs, lr, clip = self.dev, self.cfg["bs"], self.cfg["lr"], self.cfg.get("clip")
        sx = torch.zeros(bs, 256, 2, 2, device=dev)
        sy = torch.zeros(bs, dtype=torch.long, device=dev)
        sm = torch.zeros(bs, device=dev)
        acc = torch.zeros((), device=dev)
        nclip = torch.zeros((), device=dev)

        def step():
            ce = F.cross_entropy(self.wm(sx), sy, reduction="none")
            cnt = sm.sum().clamp(min=1.0)
            loss = (ce * sm).sum() / cnt
            grads = torch.autograd.grad(loss, self.wp)
            with torch.no_grad():
                if mu_prox > 0:
                    grads = torch._foreach_add(grads, torch._foreach_sub(self.wp, self.gp), alpha=mu_prox)
                if clip:
                    tot = torch.linalg.vector_norm(torch.stack(torch._foreach_norm(grads)))
                    coef = (clip / (tot + 1e-6)).clamp(max=1.0)
                    grads = torch._foreach_mul(grads, coef)
                    nclip.add_((tot > clip).float() * (sm.sum() > 0).float())
                torch._foreach_add_(self.wp, grads, alpha=-lr)
                acc.add_(loss.detach() * sm.sum())

        side = torch.cuda.Stream()
        side.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(side):
            sm.fill_(1.0)
            for _ in range(3):
                step()
        torch.cuda.current_stream().wait_stream(side)
        torch.cuda.synchronize()
        g = torch.cuda.CUDAGraph()
        with torch.cuda.graph(g):
            step()
        self._graphs[key] = (g, sx, sy, sm, acc, nclip)
        return self._graphs[key]

    def local_train(self, i, mu_prox=0.0):
        """Returns (mean training loss, steps, ok); ok=False if the update is non-finite."""
        c, ids = self.cfg, self.fed["tr"][i]
        n, bs = len(ids), c["bs"]
        g, sx, sy, sm, acc, nclip = self._graph_step(mu_prox)
        cx, cy = self.fed["X"][ids], self.fed["Yn"][ids]
        with torch.no_grad():
            torch._foreach_copy_(self.wp, self.gp)
        acc.zero_(); nclip.zero_()
        nb = math.ceil(n / bs)
        pad = nb * bs - n
        mask = torch.ones(nb * bs, device=self.dev)
        mask[n:] = 0.0
        steps = 0
        for ep in range(c["epochs"]):
            perm = torch.randperm(n, device=self.dev, generator=self.gen)
            xs, ys = cx[perm].float(), cy[perm]
            if pad:
                xs = torch.cat([xs, torch.zeros(pad, *xs.shape[1:], device=self.dev)])
                ys = torch.cat([ys, torch.zeros(pad, dtype=torch.long, device=self.dev)])
            for k in range(nb):
                sl = slice(k * bs, (k + 1) * bs)
                sx.copy_(xs[sl]); sy.copy_(ys[sl]); sm.copy_(mask[sl])
                g.replay()
                steps += 1
        with torch.no_grad():
            ok = bool(torch.isfinite(torch.stack(torch._foreach_norm(self.wp))).all())
        self.clip_hits += int(nclip.item())
        if not ok:
            self.failed_updates += 1
        return acc / (n * c["epochs"]), steps, ok

    def clone_params(self):
        return [p.detach().clone() for p in self.wp]

    def select_norm(self, v, r, m_t, logq, mu_eff, c, t):
        """Rank-normalised priority (both terms on a common [0,1] scale) with the waiting-time guard.
        utility = percentile rank of the stability score s = dKL - mu*var among the candidates;
        waiting = percentile rank of the idle counter; priority = a*utility + (1-a)*waiting (a fixed).
        Guard: clients with r >= R = ceil(N/cmin) are taken first, oldest first, ties by identifier.
        Candidate parameters are not stored: the m selected clients are re-trained with the same seed."""
        from scipy.stats import rankdata
        N = self.N
        recs, steps_tot = [], 0
        for i in range(N):
            self.gen.manual_seed(1000003 * t + i)
            _, steps, ok = self.local_train(i)
            steps_tot += steps
            if not ok:
                continue
            u, var = self.kl_stats(i, logq[i], v["utility"])
            recs.append((i, float(u), float(var)))
        if not recs:
            return [], steps_tot, 0
        ids = np.array([x[0] for x in recs])
        s = np.array([x[1] - mu_eff * x[2] for x in recs])

        def pct(z):
            z = np.asarray(z, float)
            return (rankdata(z) - 1.0) / (len(z) - 1.0) if len(z) > 1 else np.zeros(len(z))

        a_ = float(v.get("a_fixed", 0.5))
        pri = a_ * pct(s) + (1.0 - a_) * pct(r[ids].astype(float))
        R = int(math.ceil(N / c["cmin"]))
        over = []
        if v.get("guard"):
            over = sorted([q for q in range(len(recs)) if r[ids[q]] >= R], key=lambda q: (-int(r[ids[q]]), int(ids[q])))
        chosen = over[:m_t]
        taken = set(chosen)
        rest = sorted([q for q in range(len(recs)) if q not in taken], key=lambda q: (-pri[q], int(ids[q])))
        chosen = chosen + rest[:m_t - len(chosen)]
        keep = []
        for q in chosen:  # re-train the selected clients with the same seed (candidate parameters are not stored)
            self.gen.manual_seed(1000003 * t + int(ids[q]))
            _, steps, ok = self.local_train(int(ids[q]))
            steps_tot += steps
            if ok:
                keep.append((float(pri[q]), int(ids[q]), self.clone_params(), float(s[q])))
        return keep, steps_tot, len(over[:m_t])

    @torch.no_grad()
    def aggregate(self, plists, weights):
        acc = [torch.zeros_like(p) for p in self.gp]
        for pl, w in zip(plists, weights):
            torch._foreach_add_(acc, pl, alpha=float(w))
        return acc

    @torch.no_grad()
    def aggregate_nova(self, plists, p, taus):
        """FedNova: w+ = w + (sum p_i tau_i) * sum p_i (w_i - w) / tau_i."""
        acc = [torch.zeros_like(q) for q in self.gp]
        for pl, pi, ti in zip(plists, p, taus):
            delta = torch._foreach_sub(pl, self.gp)
            torch._foreach_add_(acc, delta, alpha=float(pi) / float(ti))
        tau_eff = float(np.sum(np.asarray(p) * np.asarray(taus)))
        new = [q.clone() for q in self.gp]
        torch._foreach_add_(new, acc, alpha=tau_eff)
        return new

    # ------------------------------------------------------------------ scoring helpers
    @torch.no_grad()
    def global_logq(self, ids=None):
        out = []
        ids = range(self.N) if ids is None else ids
        for i in ids:
            sl = slice(self.score_off[i], self.score_off[i + 1])
            out.append(F.log_softmax(self.gm(self.score_X[sl].float()), 1))
        return out

    @torch.no_grad()
    def kl_stats(self, i, logq, utility):
        """(utility score, batch variance) for client i after local training (work model)."""
        sl = slice(self.score_off[i], self.score_off[i + 1])
        x, y = self.score_X[sl].float(), self.score_Y[sl]
        B = self.cfg["B"]
        if utility == "kl":
            logp = F.log_softmax(self.wm(x), 1)
            d = (logp.exp() * (logp - logq)).sum(1)
        else:
            d = F.nll_loss(logq, y, reduction="none")
        parts = torch.tensor_split(d, B)
        kb = torch.stack([p.mean() for p in parts])
        sz = torch.tensor([len(p) for p in parts], device=self.dev, dtype=torch.float32)
        return ((kb * sz).sum() / sz.sum()).item(), kb.var(unbiased=True).item()

    # ------------------------------------------------------------------ selection (baselines)
    def _probe_logq(self, i):
        return self.global_logq([i])[0]

    def sel_random(self, t, m):
        return sorted(self.rng.choice(self.N, m, replace=False).tolist())

    def sel_powd(self, t, m, d):
        cand = self.rng.choice(self.N, d, replace=False, p=self.n / self.n.sum())
        loss = []
        for i in cand:
            sl = slice(self.score_off[i], self.score_off[i + 1])
            loss.append(F.nll_loss(self._probe_logq(i), self.score_Y[sl]).item())
        order = np.lexsort((cand, -np.array(loss)))
        return sorted(cand[order[:m]].tolist())

    @torch.no_grad()
    def sel_divfl(self, t, m):
        G = []
        for i in range(self.N):
            sl = slice(self.score_off[i], self.score_off[i + 1])
            h = self.gm.feats(self.score_X[sl].float())
            p = F.softmax(self.gm.fc(h), 1)
            p[torch.arange(len(p)), self.score_Y[sl]] -= 1.0
            G.append(torch.cat([(p.T @ h / len(p)).flatten(), p.mean(0)]))
        G = torch.stack(G)
        D = torch.cdist(G, G)
        sim = D.max() - D
        chosen, cur = [], torch.zeros(self.N, device=self.dev)
        for _ in range(m):
            gain = torch.clamp(sim - cur[:, None], min=0).sum(0)
            gain[chosen] = -1
            j = int(gain.argmax())
            chosen.append(j)
            cur = torch.maximum(cur, sim[:, j])
        return sorted(chosen)

    def sel_oort(self, t, m):
        st = self.oort
        eps = max(0.2, 0.9 * 0.98 ** (t - 1))
        explored = np.where(st["explored"])[0]
        k_exploit = min(len(explored), int(round((1 - eps) * m)))
        sel = []
        if k_exploit > 0:
            bonus = np.sqrt(0.1 * math.log(max(t, 2)) / np.maximum(st["last"][explored], 1))
            score = st["util"][explored] + bonus
            order = np.lexsort((explored, -score))
            sel += explored[order[:k_exploit]].tolist()
        rest = [i for i in range(self.N) if i not in sel]
        unexp = [i for i in rest if not st["explored"][i]]
        pool = unexp if len(unexp) >= m - len(sel) else rest
        sel += self.rng.choice(pool, m - len(sel), replace=False).tolist()
        return sorted(sel)

    def sel_fair(self, t, m, greedy):
        """FairFedCS (Shi et al., ICME 2023): top-m by CSI = sigma*r_i + Q_i; Greedy: top-m by reputation r_i."""
        st = self.rep
        r = (st["a"] + 1.0) / (st["a"] + st["b"] + 2.0)
        score = r if greedy else self.cfg.get("sigma", 0.6) * r + st["Q"]
        order = np.lexsort((np.arange(self.N), -score))
        return sorted(order[:m].tolist())

    @torch.no_grad()
    def loo_contrib(self, newp, plists, p):
        """Leave-one-out validation-accuracy contribution of each selected client (approximates GTG-Shapley)."""
        torch._foreach_copy_(self.ep, newp)
        base = self.val(model=self.em)[1]
        out = []
        for pl, pi in zip(plists, p):
            if len(plists) == 1:
                out.append(0.0)
                continue
            wo = [(a_ - pi * b_) / (1.0 - pi) for a_, b_ in zip(newp, pl)]
            torch._foreach_copy_(self.ep, wo)
            out.append(base - self.val(model=self.em)[1])
        return out

    # ------------------------------------------------------------------ one run
    def run(self, method, verbose=False):
        c = self.cfg
        N, T, m_fix = self.N, c["rounds"], c["m"]
        log = {k: [] for k in ["val_loss", "val_acc", "test_acc", "cohort", "selected", "wall", "valid",
                               "down", "up", "aux", "steps", "fwd", "weights_min", "a_mean", "F_mean", "nu"]}
        sel_count = np.zeros(N, int)
        last_sel = np.zeros(N, int)
        max_wait = np.zeros(N, int)
        cum = dict(down=0.0, up=0.0, aux=0.0, steps=0, fwd=0)
        diag, diag_set = {}, set(c.get("diag_rounds") or [])
        if method == "oort":
            self.oort = dict(util=np.zeros(N), last=np.ones(N), explored=np.zeros(N, bool))
        if method in FAIR_REP:
            self.rep = dict(a=np.zeros(N), b=np.zeros(N), Q=np.zeros(N))
        contrib = None
        is_ff = method in FEDFACS_VARIANTS
        if is_ff:
            v = FEDFACS_VARIANTS[method]
            mu_eff = c["mu"] if c.get("mu") is not None else v["mu"]
            guard_hits = []
            r, a = np.zeros(N, int), np.full(N, 0.5)
            rbar, rho, omega, nu, ubar = 0.0, [0.0], 0.0, 0.0, 1.0
        L_prev, vacc_prev = self.val()  # L^0
        tacc_prev = self.test()
        B_ = self.nbytes
        torch.cuda.reset_peak_memory_stats()
        t_start = time.time()
        for t in range(1, T + 1):
            t0 = time.time()
            d_cl = u_cl = 0
            aux = steps_tot = fwd = 0
            wts_min = float("nan")
            newp = None
            Fv = None
            if is_ff:
                m_t = spec.cohort_size(rho[t - 1], c["cmin"], c["cmax"]) if v["cohort"] == "adaptive" else c["cmax"]
                Fv = spec.fairness(r, rbar)
                logq = self.global_logq() if v["utility"] != "rand" else None
                keep = []
                a_new = a.copy()
                u_all, drec = [], []
                for i in (() if v.get("norm") else range(N)):
                    _, steps, ok = self.local_train(i)
                    steps_tot += steps
                    if not ok:  # failed client update: reported as unavailable, never selectable
                        continue
                    if v["utility"] == "rand":
                        fit = float(self.rng.random())
                        s_i, a_i, u = fit, a[i], float("nan")
                    else:
                        u, var = self.kl_stats(i, logq[i], v["utility"])
                        u_all.append(u)
                        if v.get("rescale"):
                            u_s, var_s = u / ubar, var / ubar ** 2
                        else:
                            u_s, var_s = u, var
                        if v["mix"] == "ctrl":
                            a_i = float(spec.mix_coeff(a[i], nu, u_s, Fv[i], c["beta"], c["lam"]))
                        elif v["mix"] == "fixed":
                            a_i = float(v.get("a_fixed", 0.5))
                        else:
                            a_i = 1.0
                        P = spec.priority(a_i, u_s, Fv[i])
                        fit = float(spec.fitness(P, var_s, mu_eff))
                        s_i = float(spec.stability(u_s, var_s, mu_eff))
                    a_new[i] = a_i
                    if t in diag_set and v["utility"] != "rand":
                        with torch.no_grad():
                            torch._foreach_copy_(self.ep, self.gp)
                            torch._foreach_add_(self.ep, torch._foreach_sub(self.wp, self.gp), alpha=1.0 / m_t)
                        Lc, _ = self.val(model=self.em)
                        with torch.no_grad():
                            dist = float(sum(((x - y) ** 2).sum() for x, y in zip(self.wp, self.gp)).sqrt())
                        sl = slice(self.score_off[i], self.score_off[i + 1])
                        drec.append(dict(i=i, kl=u, var=var, F=float(Fv[i]), fit=fit, a=a_i, n=int(self.n[i]),
                                         gce=float(F.nll_loss(logq[i], self.score_Y[sl]).item()),
                                         dist=dist,
                                         noise=float(self.fed["noise"][i]), gain=L_prev - Lc))
                    key = (fit, -i)
                    if len(keep) < m_t or key > min((k[0], -k[1]) for k in keep):
                        keep.append((fit, i, self.clone_params(), s_i))
                        if len(keep) > m_t:
                            worst = min(range(len(keep)), key=lambda q: (keep[q][0], -keep[q][1]))
                            keep.pop(worst)
                if v.get("norm"):
                    keep, st_add, n_over = self.select_norm(v, r, m_t, logq, mu_eff, c, t)
                    steps_tot += st_add
                    guard_hits.append(n_over)
                    a_new[:] = float(v.get("a_fixed", 0.5))
                if drec:
                    diag[t] = drec
                fwd += N * self.S * 2
                if keep:
                    keep.sort(key=lambda k: (-k[0], k[1]))
                    sel = [k[1] for k in keep]
                    s_sel = np.array([k[3] for k in keep])
                    n_sel = self.n[sel].astype(float)
                    w = spec.stability_weights(s_sel, n_sel) if v["agg"] == "stab" else n_sel / n_sel.sum()
                    wts_min = float(w.min())
                    newp = self.aggregate([k[2] for k in keep], w)
                else:
                    sel = []
                d_cl, u_cl = N, len(sel)
                aux = N * 4 + len(sel) * 8
                del keep
            else:
                m_t = m_fix
                mu_prox = c["prox"] if method == "fedprox" else 0.0
                if method in ("random", "fedprox", "fednova", "qffl"):
                    sel = self.sel_random(t, m_t)
                    d_cl = m_t
                elif method in FAIR_REP:
                    sel = self.sel_fair(t, m_t, method == "greedy")
                    d_cl, aux = m_t, m_t * 4
                elif method == "powd":
                    sel = self.sel_powd(t, m_t, c["d"])
                    d_cl, aux, fwd = c["d"], c["d"] * 4, c["d"] * self.S
                elif method == "divfl":
                    sel = self.sel_divfl(t, m_t)
                    d_cl, aux, fwd = N, N * (512 * NUM_CLASSES + NUM_CLASSES) * 4, N * self.S
                elif method == "oort":
                    sel = self.sel_oort(t, m_t)
                    d_cl, aux = m_t, m_t * 4
                else:
                    raise ValueError(method)
                plists, good, losses, taus = [], [], [], []
                for i in sel:
                    l0, steps, ok = self.local_train(i, mu_prox)
                    steps_tot += steps
                    if not ok:
                        continue
                    plists.append(self.clone_params()); good.append(i); losses.append(float(l0)); taus.append(steps)
                    if method == "oort":
                        st = self.oort
                        st["util"][i] = self.n[i] * abs(float(l0))
                        st["explored"][i] = True
                        st["last"][i] = t
                sel = good
                u_cl = len(sel)
                if sel:
                    p = self.n[sel] / self.n[sel].sum()
                    if method == "fednova":
                        newp = self.aggregate_nova(plists, p, taus)
                    elif method == "qffl":
                        wq = self.n[sel] * np.maximum(np.array(losses), 1e-8)  # q = 1
                        newp = self.aggregate(plists, wq / wq.sum())
                    else:
                        newp = self.aggregate(plists, p)
                    if method in FAIR_REP:
                        contrib = (list(sel), self.loo_contrib(newp, plists, p))
                del plists
            # ---- stage: evaluate the candidate aggregate; commit only if all checks pass
            valid = newp is not None
            if valid:
                torch._foreach_copy_(self.ep, newp)
                L_t, vacc = self.val(model=self.em)
                valid = math.isfinite(L_t) and L_prev > 0
            if valid:
                torch._foreach_copy_(self.gp, newp)
                if is_ff:
                    rho_t = spec.rho_update(L_prev, L_t)
                    rho.append(rho_t)
                    omega, nu = spec.omega_nu_next(t, omega, rho, c["beta_ref"])
                    mask = np.zeros(N, bool); mask[sel] = True
                    r, rbar = spec.idle_update(r, mask)
                    a = a_new
                    if v.get("rescale") and u_all:
                        ubar = max(float(np.mean(u_all)), 1e-8)
                if method in FAIR_REP and contrib is not None:
                    st = self.rep
                    for i_, phi in zip(*contrib):
                        if phi >= 0:   # phi = acc(with i) - acc(without i) >= 0: positive contribution (FairFedCS: a_i += 1)
                            st["a"][i_] += 1
                        else:
                            st["b"][i_] += 1
                    rr = (st["a"] + 1.0) / (st["a"] + st["b"] + 2.0)
                    x = np.zeros(N); x[sel] = 1.0
                    eps_ = c["m"] / N
                    st["Q"] = np.maximum(0.0, st["Q"] + eps_ * rr * (1.0 - x) - x)
                L_prev, vacc_prev, tacc_prev = L_t, vacc, self.test()
            else:  # cancelled attempt: state unchanged, resources still counted
                self.invalid_rounds += 1
                sel = []
                if is_ff:
                    rho.append(0.0)  # keep the history aligned without moving the feedback state
            mask = np.zeros(N, bool); mask[sel] = True
            sel_count += mask
            wait = t - last_sel
            max_wait = np.maximum(max_wait, np.where(mask, wait - 1, 0))
            last_sel[mask] = t
            cum["down"] += d_cl * B_; cum["up"] += (len(sel) if valid else u_cl) * B_
            cum["aux"] += aux; cum["steps"] += steps_tot; cum["fwd"] += fwd
            log["val_loss"].append(L_prev); log["val_acc"].append(vacc_prev); log["test_acc"].append(tacc_prev)
            log["cohort"].append(len(sel)); log["selected"].append(sel); log["wall"].append(time.time() - t0)
            log["valid"].append(bool(valid))
            for k in ("down", "up", "aux", "steps", "fwd"):
                log[k].append(cum[k])
            log["weights_min"].append(wts_min)
            log["a_mean"].append(float(a.mean()) if is_ff else float("nan"))
            log["F_mean"].append(float(Fv.mean()) if is_ff else float("nan"))
            log["nu"].append(float(nu) if is_ff else float("nan"))
            if verbose and (t % 5 == 0 or t == 1):
                print(f"[{method}] t={t:3d} val_acc={vacc_prev:.4f} test={tacc_prev:.4f} m={len(sel)} "
                      f"{time.time() - t0:.1f}s", flush=True)
        wait = T - last_sel
        max_wait = np.maximum(max_wait, wait)
        return dict(log=log, sel_count=sel_count.tolist(), max_wait=max_wait.tolist(),
                    per_client_acc=self.per_client_acc(), n=self.n.tolist(), total_time=time.time() - t_start,
                    bytes_per_model=B_, confusion=self.confusion(), noise=self.fed["noise"].tolist(),
                    peak_mem_mb=torch.cuda.max_memory_allocated() / 1e6, clip_hits=self.clip_hits,
                    failed_updates=self.failed_updates, invalid_rounds=self.invalid_rounds, diag=diag,
                    guard_hits=(guard_hits if is_ff else []))
