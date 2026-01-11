import numpy as np
import pytest
from scipy.stats import norm

from sif_model import calculate_ec_exact, calculate_ec_robust, calculate_sst


def test_ec_exact_matches_inverse_probit():
    """EC exact should equal |Phi^-1(1 / (2 * exp(delta)))|."""
    deltas = np.array([0.01, 0.1, 0.5, 1.0, 2.0])
    prob = 1.0 / (2.0 * np.exp(deltas))
    expected = np.abs(norm.ppf(prob))
    actual = calculate_ec_exact(deltas)
    assert np.allclose(actual, expected, rtol=1e-7, atol=1e-12)


def test_approximation_deviates_from_exact_sst():
    """The polynomial approximation should meaningfully differ from the exact EC for SST.

    This ensures the tests detect when figures using the approximation would not match
    the exact inverse-probit-based curves from the paper.
    """
    delta = np.linspace(0.01, 5, 200)
    sst_exact = calculate_sst(delta, r=0.05, sigma=0.20, use_exact=True)
    sst_approx = calculate_sst(delta, r=0.05, sigma=0.20, use_exact=False)
    diff = np.abs(sst_exact - sst_approx)

    # We expect at least one point with > 1 year absolute difference (observed in repo)
    assert diff.max() > 1.0


def test_sst_scalar_consistency():
    """Check the SST formula for a scalar delta against manual computation."""
    delta = 1.234
    r = 0.05
    sigma = 0.20
    ec = calculate_ec_exact(delta)
    expected = delta / r - (delta / (sigma * ec)) ** 2
    actual = calculate_sst(delta, r, sigma, use_exact=True)

    # Allow for small floating point differences across platforms
    assert np.isclose(actual, expected, rtol=1e-7, atol=1e-12)


def test_whitepaper_approx_formula_matches_expression():
    """Validate the whitepaper approximation formula: (x/0.05) - ( x / (0.2 * (0.8*x + 1.2)) )^2."""
    delta = np.array([0.01, 0.1, 0.5, 1.0, 2.0])
    sst_from_expr = (delta / 0.05) - (delta / (0.2 * (0.8 * delta + 1.2))) ** 2
    # Build same expression elementwise to ensure no broadcasting surprises
    sst_manual = np.array([ (d / 0.05) - (d / (0.2 * (0.8 * d + 1.2))) ** 2 for d in delta ])
    assert np.allclose(sst_from_expr, sst_manual, rtol=1e-12, atol=1e-15)


def test_whitepaper_approx_differs_from_exact():
    """Compare the whitepaper formula to the exact inverse-probit EC and ensure a meaningful difference."""
    delta = np.linspace(0.01, 5, 200)
    sst_paper = (delta / 0.05) - (delta / (0.2 * (0.8 * delta + 1.2))) ** 2
    sst_exact = calculate_sst(delta, r=0.05, sigma=0.20, use_exact=True)
    diff = np.abs(sst_paper - sst_exact)

    # Print stats for debugging (pytest captures stdout on failure)
    print(f"whitepaper approx vs exact: max_abs_diff={diff.max():.6f}, mean_abs_diff={diff.mean():.6f}")

    # Based on observed behavior, expect at least one point with > 1 year difference
    assert diff.max() > 1.0
