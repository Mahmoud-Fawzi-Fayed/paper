"""Unit tests for the corrected equations. Run: python -m pytest -q  (or python test_spec.py)."""
import math
import numpy as np
import spec


def test_original_idle_counter_never_increments():
    r = np.zeros(5, dtype=int)
    for _ in range(10):
        r = spec.original_idle_update(r, np.array([1, 0, 0, 0, 0], bool))
    assert (r == 0).all()  # reviewer's point: every counter stays 0 -> F_i == 1 for all i


def test_corrected_idle_counter_increments_and_resets():
    r = np.zeros(5, dtype=int)
    sel = np.array([1, 0, 0, 0, 0], bool)
    for t in range(1, 4):
        r, rbar = spec.idle_update(r, sel)
    assert list(r) == [0, 3, 3, 3, 3] and abs(rbar - 2.4) < 1e-12
    r, _ = spec.idle_update(r, np.array([0, 1, 0, 0, 0], bool))
    assert list(r) == [1, 0, 4, 4, 4]


def test_fairness_range_fixed_population():
    N = 20
    rng = np.random.default_rng(0)
    for _ in range(200):
        r = rng.integers(0, 50, N)
        F = spec.fairness(r, r.mean())
        assert (F >= 1.0).all() and (F < N + 1).all()


def test_mix_denominator_positive_where_original_vanishes():
    F, nu = 2.0, 1.0
    dkl = F - 1.0 * F / nu  # makes original denominator lam*F + nu*(dkl-F) == 0
    assert abs(spec.original_mix_denominator(nu, dkl, F)) < 1e-12
    a = spec.mix_coeff(0.5, nu, dkl, F)
    assert np.isfinite(a) and 0.0 <= a <= 1.0


def test_mix_coeff_bounded_and_finite_everywhere():
    rng = np.random.default_rng(1)
    for _ in range(2000):
        a = spec.mix_coeff(rng.uniform(0, 1), rng.normal(0, 3), rng.uniform(0, 5), 1 + rng.uniform(0, 20))
        assert np.isfinite(a) and 0.0 <= a <= 1.0


def test_positive_nu_does_not_imply_larger_a():
    # F>=1 > dkl  =>  nu>0 gives a NEGATIVE feedback target, so a decreases (reviewer's point)
    a0 = 0.5
    a1 = spec.mix_coeff(a0, nu=1.0, dkl=0.05, F=1.5)
    assert a1 < a0


def test_stability_weights_nonnegative_sum_one_with_negative_scores():
    s = np.array([-0.3, 0.2, 0.1, -0.05])
    n = np.array([100, 100, 100, 100])
    w = spec.stability_weights(s, n)
    assert (w >= 0).all() and abs(w.sum() - 1) < 1e-12 and w[0] == 0 and w[3] == 0
    # original rule gives a negative weight
    assert (spec.original_stability_normalise(s) < 0).any()


def test_stability_weights_fallback_to_sample_counts():
    w = spec.stability_weights(np.zeros(3), np.array([10, 30, 60]))
    assert np.allclose(w, [0.1, 0.3, 0.6])
    w = spec.stability_weights(np.array([-1.0, -2.0]), np.array([1, 3]))
    assert np.allclose(w, [0.25, 0.75])


def test_identical_models_zero_scores_do_not_divide_by_zero():
    w = spec.stability_weights(np.zeros(4), np.array([5, 5, 5, 5]))
    assert np.isfinite(w).all() and abs(w.sum() - 1) < 1e-12


def test_cohort_is_integer_and_within_bounds_for_any_rho():
    for rho in [-5.0, -0.1, 0.0, 0.2, 0.5, 0.99, 1.0, 3.0]:
        m = spec.cohort_size(rho, 5, 10)
        assert isinstance(m, int) and 5 <= m <= 10
    assert spec.cohort_size(0.0, 5, 10) == 10 and spec.cohort_size(-2.0, 5, 10) == 10
    assert spec.cohort_size(1.0, 5, 10) == 5
    assert spec.cohort_size(0.5, 8, 10) == 9


def test_cohort_original_formula_exceeds_max_for_negative_rho():
    cmin, cmax, rho = 8, 10, -0.5
    assert cmin + (cmax - cmin) * (1 - rho) > cmax  # reviewer's point


def test_rho_update_guards():
    assert abs(spec.rho_update(2.0, 1.0) - 0.5) < 1e-12
    assert spec.rho_update(1.0, 1.5) < 0  # loss increase kept, signed
    for bad in [(0.0, 1.0), (float("nan"), 1.0), (1.0, float("inf"))]:
        try:
            spec.rho_update(*bad)
        except ValueError:
            continue
        raise AssertionError("expected ValueError for %r" % (bad,))


def test_causal_reference_uses_only_past_rounds():
    rho = [0.0]  # rho^0
    om = 0.0
    nus = {}
    losses = [1.0, 0.8, 0.7, 0.72, 0.6]
    for t in range(1, len(losses)):
        rho.append(spec.rho_update(losses[t - 1], losses[t]))  # rho^t
        om, nus[t + 1] = spec.omega_nu_next(t, om, rho)
    # nu^2 = Omega^2 - rho^1 = -rho^1 ; Omega^3 = 0.9*0 + 0.1*rho^1
    assert abs(nus[2] + rho[1]) < 1e-12
    assert abs(nus[3] - (0.1 * rho[1] - rho[2])) < 1e-12


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fns:
        f()
        print("ok", f.__name__)
    print(len(fns), "tests passed")
