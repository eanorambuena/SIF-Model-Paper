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

    # Figure 1: SST Comparison (Standard vs High Vol) — use exact EC
    delta1 = np.linspace(0.001, 1.0, 400)
    sst_std = calculate_sst(delta1, r=0.05, sigma=0.20, use_exact=True)
    sst_high = calculate_sst(delta1, r=0.05, sigma=0.50, use_exact=True)

    plt.figure(figsize=(8, 5))
    plt.plot(delta1, sst_std, label='Standard (σ=20%)', color='blue', linewidth=2)
    plt.plot(delta1, sst_high, label='High Vol (σ=50%)', color='red', linestyle='--', linewidth=2)
    plt.axhline(0, color='black', linestyle=':', linewidth=1)
    plt.title('Figure 1: SST Comparison (Volatility Buys Time)')
    plt.xlabel('Displacement δ (Log-Moneyness)')
    plt.ylabel('SST (Years)')
    # Autoscale with 10% margins
    y_min, y_max = min(sst_std.min(), sst_high.min()), max(sst_std.max(), sst_high.max())
    y_margin = (y_max - y_min) * 0.1
    plt.ylim(y_min - y_margin, y_max + y_margin)
    plt.xlim(delta1.min(), delta1.max())
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save data and figure
    save_series_csv(os.path.join(output_dir, 'data_figure1_paper.csv'), delta1, {'standard': sst_std, 'highvol': sst_high})
    fig1_path = os.path.join(output_dir, 'figure1_paper.png')
    plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'figure1_paper.pdf'), bbox_inches='tight')
    plt.close()
    print(f"Saved Figure 1 to {fig1_path}")

    # Figure 2: Sensitivity to Rates (r = 2%, 5%, 10%), sigma=20%
    delta2 = np.linspace(0.001, 4.0, 400)
    rates = [0.02, 0.05, 0.10]
    plt.figure(figsize=(8, 5))
    series = {}
    for r_val, color, label in zip(rates, ['green', 'blue', 'red'], ['r=2% (Patient)', 'r=5% (Base)', 'r=10% (Strict)']):
        sst_r = calculate_sst(delta2, r=r_val, sigma=0.20, use_exact=True)
        series[label] = sst_r
        plt.plot(delta2, sst_r, label=label, color=color, linewidth=2)

    plt.axhline(0, color='black', linestyle=':', linewidth=1)
    plt.title('Figure 2: Sensitivity to Rates (Duration)')
    plt.xlabel('Displacement δ')
    plt.ylabel('SST (Years)')
    # Autoscale with 10% margins
    y_vals = [series[k] for k in series]
    y_min = min([v.min() for v in y_vals])
    y_max = max([v.max() for v in y_vals])
    y_margin = (y_max - y_min) * 0.1
    plt.ylim(y_min - y_margin, y_max + y_margin)
    plt.xlim(delta2.min(), delta2.max())
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    save_series_csv(os.path.join(output_dir, 'data_figure2_paper.csv'), delta2, series)
    fig2_path = os.path.join(output_dir, 'figure2_paper.png')
    plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'figure2_paper.pdf'), bbox_inches='tight')
    plt.close()
    print(f"Saved Figure 2 to {fig2_path}")

    # Figure 3: Sensitivity to Volatility (σ = 20%, 15%, 10%), r=5%
    delta3 = np.linspace(0.001, 4.5, 400)
    sigmas = [0.20, 0.15, 0.10]
    plt.figure(figsize=(8, 5))
    series_v = {}
    labels = ['σ=20%', 'σ=15%', 'σ=10%']
    colors = ['green', 'blue', 'red']
    for sigma, color, label in zip(sigmas, colors, labels):
        sst_v = calculate_sst(delta3, r=0.05, sigma=sigma, use_exact=True)
        series_v[label] = sst_v
        plt.plot(delta3, sst_v, label=label, color=color, linewidth=2, linestyle='-' if sigma==0.20 else '--')

    plt.axhline(0, color='black', linestyle=':', linewidth=1)
    plt.title('Figure 3: Sensitivity to Volatility (Convexity)')
    plt.xlabel('Displacement δ')
    plt.ylabel('SST (Years)')
    # Autoscale with 10% margins
    y_vals_v = [series_v[k] for k in series_v]
    y_min_v = min([v.min() for v in y_vals_v])
    y_max_v = max([v.max() for v in y_vals_v])
    y_margin_v = (y_max_v - y_min_v) * 0.1
    plt.ylim(y_min_v - y_margin_v, y_max_v + y_margin_v)
    plt.xlim(delta3.min(), delta3.max())
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    save_series_csv(os.path.join(output_dir, 'data_figure3_paper.csv'), delta3, series_v)
    fig3_path = os.path.join(output_dir, 'figure3_paper.png')
    plt.savefig(fig3_path, dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'figure3_paper.pdf'), bbox_inches='tight')
    plt.close()
    print(f"Saved Figure 3 to {fig3_path}")

if __name__ == "__main__":
    run_simulation()
    print("Simulation complete. The math works.")
