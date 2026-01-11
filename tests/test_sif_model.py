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
