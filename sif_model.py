"""
Subsidy Immunity Formula (SIF) - Reference Implementation
Author: Emmanuel Normabuena (2026)
Abstract:
This script implements the Strategic Shielding Time (SST) model derived in the
whitepaper. It calculates the optimal stopping time for mean-reversion strategies
using the Reflection Principle of Brownian Motion.

Dependencies: numpy, scipy, matplotlib
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def calculate_ec_exact(delta):
    """
    Calculates the exact Exigence Coefficient (EC) based on the Reflection Principle.
    Formula: EC(delta) = |Phi^-1( 1 / (2 * exp(delta)) )|
    """
    # Avoid division by zero or log domain errors for delta=0 using a small epsilon
    delta = np.maximum(delta, 1e-9)
    
    # Hit probability decay: P ~ 1 / (2 * e^delta)
    prob_hit = 1 / (2 * np.exp(delta))
    
    # Probit function (Inverse Normal CDF)
    # We take absolute value because we need the distance in std devs
    ec = np.abs(norm.ppf(prob_hit))
    
    return ec

def calculate_ec_robust(delta):
    """
    Polynomial approximation used in the Whitepaper for graphical stability.
    Approximation: EC ~ 0.9*delta - 0.07*delta^2
    """
    return 0.9 * delta - 0.07 * delta**2

def calculate_sst(delta, r, sigma, use_exact=True):
    """
    Calculates Strategic Shielding Time (SST).
    SST = (Linear Funding Time) - (Quadratic Volatility Penalty)
    SST = (delta / r) - [ delta / (sigma * EC) ]^2
    """
    if use_exact:
        ec = calculate_ec_exact(delta)
    else:
        ec = calculate_ec_robust(delta)
    
    # Intrinsic Duration (Linear Benefit)
    funding_time = delta / r
    
    # Volatility Latency (Quadratic Penalty)
    # Add epsilon to EC to avoid division by zero at delta=0
    vol_penalty = (delta / (sigma * (ec + 1e-9)))**2
    
    sst = funding_time - vol_penalty
    return sst


def save_series_csv(path, delta, series_dict):
    """Save multiple series to a CSV with a header."""
    # columns: delta, series1, series2, ...
    names = ['delta'] + list(series_dict.keys())
    data = [delta] + [series_dict[k] for k in series_dict.keys()]
    arr = np.column_stack(data)
    header = ','.join(names)
    np.savetxt(path, arr, delimiter=',', header=header, comments='')

# --- SIMULATION & PLOTTING ---

def run_simulation():
    output_dir = "figures"
    os.makedirs(output_dir, exist_ok=True)

    # Grid for Log-Moneyness (Displacement)
    delta = np.linspace(0.01, 5, 200)

    # 1. Figure 1 Reproduction: Standard vs High Vol (USING EXACT EC)
    plt.figure(figsize=(10, 6))
    
    # Standard Asset (r=5%, sigma=20%) - exact EC
    sst_std_exact = calculate_sst(delta, r=0.05, sigma=0.20, use_exact=True)
    plt.plot(delta, sst_std_exact, label='Standard (σ=20%) - exact', color='blue', linewidth=2)
    
    # High Vol Asset (r=5%, sigma=50%) - exact EC
    sst_vol_exact = calculate_sst(delta, r=0.05, sigma=0.50, use_exact=True)
    plt.plot(delta, sst_vol_exact, label='High Vol (σ=50%) - exact', color='red', linestyle='--', linewidth=2)
    
    # Also compute approximations for numeric comparison (not plotted)
    sst_std_approx = calculate_sst(delta, r=0.05, sigma=0.20, use_exact=False)
    sst_vol_approx = calculate_sst(delta, r=0.05, sigma=0.50, use_exact=False)
    
    # Numeric comparison stats
    def _print_stats(name, exact, approx):
        diff = np.abs(exact - approx)
        print(f"{name} - approx vs exact: max_abs_diff={diff.max():.6f}, mean_abs_diff={diff.mean():.6f}")
    _print_stats('Standard (σ=20%)', sst_std_exact, sst_std_approx)
    _print_stats('High Vol (σ=50%)', sst_vol_exact, sst_vol_approx)
    
    # Save data for reproducibility
    save_series_csv(os.path.join(output_dir, 'data_figure1_exact.csv'), delta, {'standard_exact': sst_std_exact, 'highvol_exact': sst_vol_exact})
    save_series_csv(os.path.join(output_dir, 'data_figure1_approx.csv'), delta, {'standard_approx': sst_std_approx, 'highvol_approx': sst_vol_approx})
    
    plt.axhline(0, color='black', linestyle=':', linewidth=1)
    plt.title('Figure 1: SST Comparison (Volatility Buys Time) - exact EC')
    plt.xlabel('Displacement δ (Log-Moneyness)')
    plt.ylabel('SST (Years)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # autoscale y-axis to avoid clipping extreme values
    plt.autoscale(enable=True, axis='y')
    
    # Save to file
    fig1_path = os.path.join(output_dir, "figure1_exact.png")
    plt.savefig(fig1_path, bbox_inches='tight')
    plt.close()
    print(f"Saved Figure 1 (exact EC) to {fig1_path}")

    # 2. Figure 2 Reproduction: Sensitivity to Rates (Rho)
    plt.figure(figsize=(10, 6))
    
    rates = [0.02, 0.05, 0.10]
    colors = ['green', 'blue', 'red']
    labels = ['r=2% (Patient)', 'r=5% (Base)', 'r=10% (Strict)']
    
    series_exact = {}
    series_approx = {}
    for r_val, col, lab in zip(rates, colors, labels):
        sst_exact = calculate_sst(delta, r=r_val, sigma=0.20, use_exact=True)
        plt.plot(delta, sst_exact, label=lab, color=col, linewidth=2)
        series_exact[lab] = sst_exact
        # approximation for comparison
        sst_approx = calculate_sst(delta, r=r_val, sigma=0.20, use_exact=False)
        series_approx[lab] = sst_approx

    # Numeric comparison stats for each rate
    for lab in labels:
        diff = np.abs(series_exact[lab] - series_approx[lab])
        print(f"{lab} - approx vs exact: max_abs_diff={diff.max():.6f}, mean_abs_diff={diff.mean():.6f}")

    # Save CSVs for reproducibility
    save_series_csv(os.path.join(output_dir, 'data_figure2_exact.csv'), delta, {k:series_exact[k] for k in series_exact})
    save_series_csv(os.path.join(output_dir, 'data_figure2_approx.csv'), delta, {k:series_approx[k] for k in series_approx})

    plt.axhline(0, color='black', linestyle=':', linewidth=1)
    plt.title('Figure 2: Sensitivity to Rates (Rho Risk) - exact EC')
    plt.xlabel('Displacement δ')
    plt.ylabel('SST (Years)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # autoscale y-axis to avoid clipping extreme values
    plt.autoscale(enable=True, axis='y')

    fig2_path = os.path.join(output_dir, "figure2_exact.png")
    plt.savefig(fig2_path, bbox_inches='tight')
    plt.close()
    print(f"Saved Figure 2 (exact EC) to {fig2_path}")

if __name__ == "__main__":
    run_simulation()
    print("Simulation complete. The math works.")
