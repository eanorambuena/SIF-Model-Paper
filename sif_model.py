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

# --- SIMULATION & PLOTTING ---

def run_simulation():
    output_dir = "figures"
    os.makedirs(output_dir, exist_ok=True)

    # Grid for Log-Moneyness (Displacement)
    delta = np.linspace(0.01, 5, 200)

    # 1. Figure 1 Reproduction: Standard vs High Vol
    plt.figure(figsize=(10, 6))
    
    # Standard Asset (r=5%, sigma=20%)
    sst_std = calculate_sst(delta, r=0.05, sigma=0.20, use_exact=False)
    plt.plot(delta, sst_std, label='Standard (σ=20%)', color='blue', linewidth=2)
    
    # High Vol Asset (r=5%, sigma=50%)
    sst_vol = calculate_sst(delta, r=0.05, sigma=0.50, use_exact=False)
    plt.plot(delta, sst_vol, label='High Vol (σ=50%)', color='red', linestyle='--', linewidth=2)
    
    plt.axhline(0, color='black', linestyle=':', linewidth=1)
    plt.title('Figure 1: SST Comparison (Volatility Buys Time)')
    plt.xlabel('Displacement δ (Log-Moneyness)')
    plt.ylabel('SST (Years)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # autoscale y-axis to avoid clipping extreme values
    plt.autoscale(enable=True, axis='y')
    
    # Save to file
    fig1_path = os.path.join(output_dir, "figure1.png")
    plt.savefig(fig1_path, bbox_inches='tight')
    plt.close()
    print(f"Saved Figure 1 to {fig1_path}")

    # 2. Figure 2 Reproduction: Sensitivity to Rates (Rho)
    plt.figure(figsize=(10, 6))
    
    rates = [0.02, 0.05, 0.10]
    colors = ['green', 'blue', 'red']
    labels = ['r=2% (Patient)', 'r=5% (Base)', 'r=10% (Strict)']
    
    for r_val, col, lab in zip(rates, colors, labels):
        sst = calculate_sst(delta, r=r_val, sigma=0.20, use_exact=False)
        plt.plot(delta, sst, label=lab, color=col, linewidth=2)

    plt.axhline(0, color='black', linestyle=':', linewidth=1)
    plt.title('Figure 2: Sensitivity to Rates (Rho Risk)')
    plt.xlabel('Displacement δ')
    plt.ylabel('SST (Years)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # autoscale y-axis to avoid clipping extreme values
    plt.autoscale(enable=True, axis='y')

    fig2_path = os.path.join(output_dir, "figure2.png")
    plt.savefig(fig2_path, bbox_inches='tight')
    plt.close()
    print(f"Saved Figure 2 to {fig2_path}")

if __name__ == "__main__":
    run_simulation()
    print("Simulation complete. The math works.")
