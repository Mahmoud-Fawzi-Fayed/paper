"""Federated simulator: FedFACS (corrected spec, with ablation switches) and baselines.

One process = one (dataset, scenario, method, seed) run; per-round log is returned as a dict.
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
        # eval-mode BatchNorm with frozen running statistics; gamma/beta stay trainable
        sc = bn.weight * torch.rsqrt(bn.running_var + bn.eps)
        return h * sc + (bn.bias - bn.running_mean * sc)

    def feats(self, x):
        """Exact matrix-multiply form of layer4 for 2x2 inputs.

        With a 2x2 map, the stride-2 3x3 conv sees only taps (1..2, 1..2); every later 3x3 conv acts on a 1x1
        map and sees only its centre tap; the stride-2 1x1 downsample sees pixel (0,0). Same parameters,
        same outputs and gradients as layer4 (checked in test_fast.py), but ~4x faster.
        """
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
    #                 cohort      agg        mix      mu   utility
    "fedfacs":        dict(cohort="adaptive", agg="stab",    mix="ctrl",  mu=1.0, utility="kl"),
    "abl_A1":         dict(cohort="fixed",    agg="samples", mix="ctrl",  mu=1.0, utility="kl"),
    "abl_A2":         dict(cohort="adaptive", agg="samples", mix="ctrl",  mu=1.0, utility="kl"),
    "abl_fixmix":     dict(cohort="adaptive", agg="stab",    mix="fixed", mu=1.0, utility="kl"),
    "abl_nofair":     dict(cohort="adaptive", agg="stab",    mix="one",   mu=1.0, utility="kl"),
    "abl_nopen":      dict(cohort="adaptive", agg="stab",    mix="ctrl",  mu=0.0, utility="kl"),
    "abl_loss":       dict(cohort="adaptive", agg="stab",    mix="ctrl",  mu=1.0, utility="loss"),
    "abl_randscore":  dict(cohort="adaptive", agg="samples", mix="ctrl",  mu=1.0, utility="rand"),
}
BASELINES = ["random", "fedprox", "powd", "divfl", "oort"]
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
        self.gm.requires_grad_(False)  # the global model is never differentiated
        self._graphs = {}
        self.gp, self.wp = list(self.gm.parameters()), list(self.wm.parameters())
        self.nbytes = sum(p.numel() for p in self.gp) * 4
        # fixed per-client scoring/probe subset (client-local examples)
        self.S = c["S"]
        self.score_ids, self.score_off, off = [], [0], 0
        for i in range(self.N):
            ids = self.fed["tr"][i]
            sid = ids[torch.randperm(len(ids), generator=torch.Generator().manual_seed(c["seed"] * 1000 + i))[: self.S].to(dev)]
            self.score_ids.append(sid)
            off += len(sid)
            self.score_off.append(off)
        self.score_X = self.fed["X"][torch.cat(self.score_ids)]
        self.score_Y = self.fed["Y"][torch.cat(self.score_ids)]

    # ------------------------------------------------------------------ evaluation
    @torch.no_grad()
    def _eval(self, X, Y, chunk=5000):
        loss = torch.zeros((), device=self.dev)
        corr = torch.zeros((), device=self.dev)
        for s in range(0, len(X), chunk):
            out = self.gm(X[s:s + chunk].float())
            loss += F.cross_entropy(out, Y[s:s + chunk], reduction="sum")
            corr += (out.argmax(1) == Y[s:s + chunk]).sum()
        return (loss / len(X)).item(), (corr / len(X)).item()

    def val(self):
        v = self.fed["val"]
        return self._eval(self.fed["X"][v], self.fed["Y"][v])

    def test(self):
        return self._eval(self.fed["Xte"], self.fed["Yte"])[1]

    @torch.no_grad()
    def per_client_acc(self):
        accs = []
        for i in range(self.N):
            ids = self.fed["lt"][i]
            accs.append(self._eval(self.fed["X"][ids], self.fed["Y"][ids])[1])
        return accs

    # ------------------------------------------------------------------ local training
    def _graph_step(self, mu_prox):
        """CUDA-graph-captured SGD step on a fixed-size, masked batch (exact: BN is in eval mode)."""
        key = float(mu_prox)
        if key in self._graphs:
            return self._graphs[key]
        dev, bs, lr = self.dev, self.cfg["bs"], self.cfg["lr"]
        sx = torch.zeros(bs, 256, 2, 2, device=dev)
        sy = torch.zeros(bs, dtype=torch.long, device=dev)
        sm = torch.zeros(bs, device=dev)
        acc = torch.zeros((), device=dev)

        def step():
            ce = F.cross_entropy(self.wm(sx), sy, reduction="none")
            cnt = sm.sum().clamp(min=1.0)
            loss = (ce * sm).sum() / cnt
            grads = torch.autograd.grad(loss, self.wp)
            with torch.no_grad():
                if mu_prox > 0:
                    grads = torch._foreach_add(grads, torch._foreach_sub(self.wp, self.gp), alpha=mu_prox)
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
        self._graphs[key] = (g, sx, sy, sm, acc)
        return self._graphs[key]

    def local_train(self, i, mu_prox=0.0):
        c, ids = self.cfg, self.fed["tr"][i]
        n, bs = len(ids), c["bs"]
        g, sx, sy, sm, acc = self._graph_step(mu_prox)
        cx, cy = self.fed["X"][ids], self.fed["Y"][ids]
        with torch.no_grad():
            torch._foreach_copy_(self.wp, self.gp)
        acc.zero_()
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
        return acc / (n * c["epochs"]), steps

    def clone_params(self):
        return [p.detach().clone() for p in self.wp]

    @torch.no_grad()
    def aggregate(self, plists, weights):
        acc = [torch.zeros_like(p) for p in self.gp]
        for pl, w in zip(plists, weights):
            torch._foreach_add_(acc, pl, alpha=float(w))
        return acc

    # ------------------------------------------------------------------ scoring helpers
    @torch.no_grad()
    def global_logq(self, ids=None):
        """log-probs of the unchanged global model on each client's scoring examples."""
        out = []
        ids = range(self.N) if ids is None else ids
        for i in ids:
            sl = slice(self.score_off[i], self.score_off[i + 1])
            out.append(F.log_softmax(self.gm(self.score_X[sl].float()), 1))
        return out

    @torch.no_grad()
    def kl_stats(self, i, logq, utility):
        """Return (utility score, batch variance) for client i after local training (work model)."""
        sl = slice(self.score_off[i], self.score_off[i + 1])
        x, y = self.score_X[sl].float(), self.score_Y[sl]
        B = self.cfg["B"]
        if utility == "kl":
            logp = F.log_softmax(self.wm(x), 1)
            d = (logp.exp() * (logp - logq)).sum(1)
        else:  # 'loss': cross-entropy of the received global model on the same examples
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
            lq = self._probe_logq(i)
            loss.append(F.nll_loss(lq, self.score_Y[sl]).item())
        order = np.lexsort((cand, -np.array(loss)))
        return sorted(cand[order[:m]].tolist())

    @torch.no_grad()
    def sel_divfl(self, t, m):
        """DivFL-style: greedy facility location over last-layer gradients at the global model (all clients)."""
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

    # ------------------------------------------------------------------ one run
    def run(self, method, verbose=False):
        c = self.cfg
        N, T, m_fix = self.N, c["rounds"], c["m"]
        log = {k: [] for k in ["val_loss", "val_acc", "test_acc", "cohort", "selected", "wall",
                               "down", "up", "aux", "steps", "fwd", "weights_min", "a_mean", "F_mean", "nu"]}
        sel_count = np.zeros(N, int)
        last_sel = np.full(N, 0)
        max_wait = np.zeros(N, int)
        cum = dict(down=0.0, up=0.0, aux=0.0, steps=0, fwd=0)
        if method == "oort":
            self.oort = dict(util=np.zeros(N), last=np.ones(N), explored=np.zeros(N, bool))
        is_ff = method in FEDFACS_VARIANTS
        if is_ff:
            v = FEDFACS_VARIANTS[method]
            r, a = np.zeros(N, int), np.full(N, 0.5)
            rbar, rho, omega, nu = 0.0, [0.0], 0.0, 0.0
        L_prev, _ = self.val()  # L^0
        B_ = self.nbytes
        t_start = time.time()
        for t in range(1, T + 1):
            t0 = time.time()
            d_cl = u_cl = 0
            aux = steps_tot = fwd = 0
            wts_min = float("nan")
            if is_ff:
                m_t = spec.cohort_size(rho[t - 1], c["cmin"], c["cmax"]) if v["cohort"] == "adaptive" else c["cmax"]
                Fv = spec.fairness(r, rbar)
                logq = self.global_logq() if v["utility"] != "rand" else None
                keep = []  # (fit, id, params, s_i)
                fits = np.zeros(N)
                a_new = a.copy()
                for i in range(N):
                    _, steps = self.local_train(i)
                    steps_tot += steps
                    if v["utility"] == "rand":
                        fit = float(self.rng.random())
                        s_i, a_i = fit, a[i]
                    else:
                        u, var = self.kl_stats(i, logq[i], v["utility"])
                        if v["mix"] == "ctrl":
                            a_i = float(spec.mix_coeff(a[i], nu, u, Fv[i], c["beta"], c["lam"]))
                        elif v["mix"] == "fixed":
                            a_i = 0.5
                        else:
                            a_i = 1.0
                        P = spec.priority(a_i, u, Fv[i])
                        fit = float(spec.fitness(P, var, v["mu"]))
                        s_i = float(spec.stability(u, var, v["mu"]))
                    a_new[i] = a_i
                    fits[i] = fit
                    key = (fit, -i)
                    if len(keep) < m_t or key > min((k[0], -k[1]) for k in keep):
                        keep.append((fit, i, self.clone_params(), s_i))
                        if len(keep) > m_t:
                            worst = min(range(len(keep)), key=lambda q: (keep[q][0], -keep[q][1]))
                            keep.pop(worst)
                fwd += N * self.S * 2
                keep.sort(key=lambda k: (-k[0], k[1]))
                sel = [k[1] for k in keep]
                s_sel = np.array([k[3] for k in keep])
                n_sel = self.n[sel].astype(float)
                if v["agg"] == "stab":
                    w = spec.stability_weights(s_sel, n_sel)
                else:
                    w = n_sel / n_sel.sum()
                wts_min = float(w.min())
                newp = self.aggregate([k[2] for k in keep], w)
                d_cl, u_cl = N, len(sel)
                aux = N * 4 + len(sel) * 8
                del keep
            else:
                m_t = m_fix
                mu_prox = c["prox"] if method == "fedprox" else 0.0
                if method in ("random", "fedprox"):
                    sel = self.sel_random(t, m_t)
                    d_cl = m_t
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
                u_cl = len(sel)
                plists = []
                for i in sel:
                    l0, steps = self.local_train(i, mu_prox)
                    steps_tot += steps
                    plists.append(self.clone_params())
                    if method == "oort":
                        st = self.oort
                        st["util"][i] = self.n[i] * math.sqrt(float(l0) ** 2)
                        st["explored"][i] = True
                        st["last"][i] = t
                w = self.n[sel] / self.n[sel].sum()
                newp = self.aggregate(plists, w)
                del plists
            # ---- validate candidate aggregate, then commit together
            torch._foreach_copy_(self.gp, newp)
            L_t, vacc = self.val()
            if is_ff:
                rho_t = spec.rho_update(L_prev, L_t)
                rho.append(rho_t)
                omega, nu = spec.omega_nu_next(t, omega, rho, c["beta_ref"])
                mask = np.zeros(N, bool)
                mask[sel] = True
                r, rbar = spec.idle_update(r, mask)
                a = a_new
            L_prev = L_t
            mask = np.zeros(N, bool)
            mask[sel] = True
            sel_count += mask
            wait = t - last_sel
            max_wait = np.maximum(max_wait, np.where(mask, wait - 1, 0))
            last_sel[mask] = t
            cum["down"] += d_cl * B_
            cum["up"] += u_cl * B_
            cum["aux"] += aux
            cum["steps"] += steps_tot
            cum["fwd"] += fwd
            log["val_loss"].append(L_t); log["val_acc"].append(vacc); log["test_acc"].append(self.test())
            log["cohort"].append(len(sel)); log["selected"].append(sel); log["wall"].append(time.time() - t0)
            for k in ("down", "up", "aux", "steps", "fwd"):
                log[k].append(cum[k])
            log["weights_min"].append(wts_min)
            log["a_mean"].append(float(a.mean()) if is_ff else float("nan"))
            log["F_mean"].append(float(Fv.mean()) if is_ff else float("nan"))
            log["nu"].append(float(nu) if is_ff else float("nan"))
            if verbose and (t % 5 == 0 or t == 1):
                print(f"[{method}] t={t:3d} val_acc={vacc:.4f} test={log['test_acc'][-1]:.4f} m={len(sel)} "
                      f"{time.time() - t0:.1f}s", flush=True)
        # end-of-run fairness statistics
        wait = T - last_sel
        max_wait = np.maximum(max_wait, wait)
        out = dict(log=log, sel_count=sel_count.tolist(), max_wait=max_wait.tolist(),
                   per_client_acc=self.per_client_acc(), n=self.n.tolist(), total_time=time.time() - t_start,
                   bytes_per_model=B_)
        return out
