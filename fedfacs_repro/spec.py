"""Corrected FedFACS specification (manuscript Sec. 4), framework-free (numpy only).

Every function maps to one numbered equation of the revised manuscript so the
equations can be unit-tested independently of any training code.
"""
import math
import numpy as np

EPS = 1e-12


def fairness(r, rbar):
    """Eq. (fair): F_i = 1 + r_i / (1 + rbar)."""
    return 1.0 + np.asarray(r, dtype=np.float64) / (1.0 + float(rbar))


def idle_update(r, selected_mask):
    """Eq. (idle)+(rbar): selected -> 0, non-selected -> +1; returns (r_next, rbar_next)."""
    r = np.asarray(r)
    r_next = np.where(selected_mask, 0, r + 1)
    return r_next, float(r_next.mean())


def mix_coeff(a_prev, nu, dkl, F, beta=0.9, lam=1.0):
    """Eq. (a): bounded EMA feedback; denominator = lam*F + |nu*(dkl-F)| > 0."""
    a_prev = np.asarray(a_prev, dtype=np.float64)
    sig = nu * (np.asarray(dkl, dtype=np.float64) - np.asarray(F, dtype=np.float64))
    den = lam * np.asarray(F, dtype=np.float64) + np.abs(sig)
    a = beta * a_prev + (1.0 - beta) * sig / den
    return np.clip(a, 0.0, 1.0)


def priority(a, dkl, F):
    """Eq. (prio)."""
    return a * dkl + (1.0 - a) * F


def stability(dkl, var, mu):
    """Eq. (s): raw stability score (may be negative)."""
    return np.asarray(dkl) - mu * np.asarray(var)


def fitness(P, var, mu):
    """Eq. (fit)."""
    return np.asarray(P) - mu * np.asarray(var)


def rho_update(L_prev, L_curr):
    """Eq. (rho): validation-loss reduction of a completed round; invalid inputs raise."""
    if not (math.isfinite(L_prev) and math.isfinite(L_curr)) or L_prev <= 0.0:
        raise ValueError("invalid loss pair for rho: %r, %r" % (L_prev, L_curr))
    return (L_prev - L_curr) / L_prev


def omega_nu_next(t, omega_t, rho_hist, beta_ref=0.9):
    """After committed round t return (Omega^{t+1}, nu^{t+1}).

    rho_hist[k] = rho^k with rho_hist[0] = 0 (rho^0). Eq. (omega): Omega^2 = 0 and
    Omega^{t+1} = beta_ref*Omega^t + (1-beta_ref)*rho^{t-1} for t >= 2. Eq. (nu):
    nu^{t+1} = Omega^{t+1} - rho^t.
    """
    if t == 1:
        om = 0.0
    else:
        om = beta_ref * omega_t + (1.0 - beta_ref) * rho_hist[t - 1]
    return om, om - rho_hist[t]


def cohort_size(rho_prev, cmin, cmax):
    """Eq. (cohort): integer, half-up rounding, clamped to [cmin, cmax]."""
    if not math.isfinite(rho_prev):
        raise ValueError("non-finite rho")
    ratio = 1.0 - min(1.0, max(0.0, rho_prev))
    m = math.floor(cmin + (cmax - cmin) * ratio + 0.5)
    return int(min(cmax, max(cmin, m)))


def stability_weights(s, n, eps=EPS):
    """Eqs. (splus)+(S): weights over the selected clients; nonnegative, sum to 1.

    s: raw stability scores of the selected clients; n: their sample counts.
    Positive parts are normalised (scaled by the largest for numerical stability);
    if no score is positive, fall back to sample-count weights.
    """
    s = np.asarray(s, dtype=np.float64)
    n = np.asarray(n, dtype=np.float64)
    sp = np.maximum(s, 0.0)
    smax = sp.max() if sp.size else 0.0
    if smax > eps:
        z = sp / smax
        return z / z.sum()
    return n / n.sum()


# ---- the ORIGINAL (defective) rules, kept only so tests can show why they were replaced ----
def original_idle_update(r, selected_mask):
    """Original Eq. (7): selected -> 0, otherwise unchanged (never increments)."""
    return np.where(selected_mask, 0, np.asarray(r))


def original_mix_denominator(nu, dkl, F, lam=1.0):
    """Original Eq. (8) denominator: lam*F + nu*(dkl-F) (can be zero or negative)."""
    return lam * F + nu * (dkl - F)


def original_stability_normalise(s):
    """Original Eq. (18): s_i / sum_j s_j (negative weights / division by zero possible)."""
    s = np.asarray(s, dtype=np.float64)
    return s / s.sum()
