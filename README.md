<h1 align="center">The Subsidy Immunity Formula (SIF)</h1>
<h2 align="center">An Optimal Stopping Framework for Retail Mean Reversion Strategies</h2>

<p align="center">
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL_v3-blue.svg" alt="License: AGPL v3">
  </a>
  <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/">
    <img src="https://img.shields.io/badge/License-CC_BY--NC--ND_4.0-lightgrey.svg" alt="License: CC BY-NC-ND 4.0">
  </a>
</p>

<p align="center">
  <strong>Author:</strong> Emmanuel Normabuena<br>
  <strong>Affiliation:</strong> Independent Researcher / Systems Architect<br>
  <strong>Location:</strong> Santiago, Chile<br>
  <strong>Date:</strong> January 2026
</p>

<hr>

<h2>📄 Abstract</h2>

<p>
Retail investors frequently suffer from the Disposition Effect, holding losing positions due to a lack of explicit opportunity cost quantification. This repository hosts the technical whitepaper and reference implementation for the <strong>Subsidy Immunity Formula (SIF)</strong>.
</p>

<p>
The SIF model is derived from the <strong>Principle of Indifference</strong> and solves the implicit circularity of first-passage time probabilities. By algebraically isolating the volatility time horizon from the Reflection Principle equation, we define two novel metrics:
</p>
<ul>
  <li><strong>Intrinsic Duration (D<sub>i</sub>):</strong> The linear sensitivity of funding capital.</li>
  <li><strong>Dynamic Convexity (C):</strong> The quadratic penalty imposed by volatility.</li>
</ul>

<p>
The interaction of these terms determines the <strong>Strategic Shielding Time (SST)</strong>, identifying the critical "Log-Moneyness" barrier (δ<sub>crit</sub>) where a position becomes mathematically insolvent.
</p>

<h2>🧩 Key Definitions</h2>

<p>The framework establishes the following canonical equation for optimal stopping:</p>

<p align="center">
  <strong>SST = D<sub>i</sub> · δ - C(δ) · δ<sup>2</sup></strong>
</p>

<p>Where:</p>
<ul>
  <li><strong>D<sub>i</sub> = 1/r</strong> (Inverse of the risk-free rate)</li>
  <li><strong>C(δ) = 1 / [σ · EC(δ)]<sup>2</sup></strong> (Volatility penalty scaled by the Exigence Coefficient)</li>
</ul>

<h2>📂 Repository Contents</h2>

<ul>
  <li><a href="SIF_Whitepaper.pdf">SIF_Whitepaper.pdf</a>: The complete technical paper explaining the derivation, proofs, and scenario analysis (Hawk vs. Panic regimes).</li>
  <li><a href="sif_model.py">sif_model.py</a>: Python reference implementation. It replicates the figures found in the paper, simulating the SST collapse and calculating the Greeks (ρ<sub>sif</sub>, ν<sub>sif</sub>).</li>
</ul>

<h2>🚀 Quick Start</h2>

<p>To run the simulation and generate the sensitivity graphs, execute the following commands in your terminal:</p>

<pre><code># Clone the repository
git clone https://github.com/eanorambuena/SIF-Model-Paper.git

# Navigate to the directory
cd SIF-Model-Paper

# Run the model
python sif_model.py
</code></pre>
<h2>⚠️ Numerical Stability & Overflow Solutions</h2>

<h3>The Probit Function Overflow Problem & Solution</h3>

<p>The core calculation uses the exact inverse-probit formula for the Exigence Coefficient:</p>

<p align="center">
  <strong>EC(δ) = |Φ<sup>-1</sup>( 1 / (2·e<sup>δ</sup>) )|</strong>
</p>

<h4>The Problem (Before)</h4>

<p>The naive implementation had numerical limitations:</p>

<ul>
  <li><strong>Mathematically:</strong> The formula is valid for all δ ∈ ℝ.</li>
  <li><strong>Computationally (IEEE 754):</strong> Computing exp(δ) directly overflows for δ > 709.</li>
  <li><strong>Symptom:</strong> For δ ≥ 710, the term 1/(2·exp(δ)) collapsed to exactly zero, causing a discontinuous jump in EC and SST.</li>
  <li><strong>Result:</strong> Figures were artificially limited to δ ≤ 700, missing important parameter regimes.</li>
</ul>

<h4>The Solution (Log-Space)</h4>

<p>We implemented the mathematically equivalent but numerically stable form:</p>

<table border="1" cellpadding="10" cellspacing="0">
  <tr>
    <th>Form</th>
    <th>Formula</th>
    <th>Stability</th>
    <th>Notes</th>
  </tr>
  <tr>
    <td><strong>Original (Naive)</strong></td>
    <td>P = 1 / (2·e<sup>δ</sup>)</td>
    <td>❌ Overflows for δ > 709</td>
    <td>Direct computation of e<sup>δ</sup> causes overflow</td>
  </tr>
  <tr>
    <td><strong>Log-Space (Stable)</strong></td>
    <td>P = e<sup>−(δ + ln 2)</sup></td>
    <td>✓ Stable for δ up to ~1,000,000</td>
    <td>Exponential of negative number never overflows</td>
  </tr>
</table>

<h4>Mathematical Equivalence</h4>

<p>Both forms are algebraically identical:</p>

<p align="center">
  <strong>1/(2·e<sup>δ</sup>) = e<sup>−ln(2)</sup> · e<sup>−δ</sup> = e<sup>−(δ + ln 2)</sup></strong>
</p>

<p>This is simply a rearrangement of the exponent rules. The only difference is which route we take through the computation:</p>

<ul>
  <li><strong>Route 1 (naive):</strong> Calculate huge e<sup>δ</sup>, then divide 1 by it → OVERFLOW</li>
  <li><strong>Route 2 (stable):</strong> Add negative numbers (−δ − ln 2), then take e<sup>...</sup> → ALWAYS SAFE</li>
</ul>

<h4>Solution: Hybrid Exact + Asymptotic</h4>

<p>To overcome underflow while maintaining accuracy, the implementation uses a <strong>hybrid approach</strong>:</p>

<table border="1" cellpadding="10" cellspacing="0">
  <tr>
    <th>Range</th>
    <th>Method</th>
    <th>Formula</th>
    <th>Accuracy</th>
  </tr>
  <tr>
    <td><strong>δ < 700</strong></td>
    <td>Exact Probit</td>
    <td>EC = |Φ<sup>-1</sup>(e<sup>−(δ + ln 2)</sup>)|</td>
    <td>Machine precision</td>
  </tr>
  <tr>
    <td><strong>δ ≥ 700</strong></td>
    <td>Asymptotic</td>
    <td>EC ≈ √(2·δ)</td>
    <td>Error < 0.3%</td>
  </tr>
</table>

<h4>Why Asymptotic Works</h4>

<p>For very small probabilities p, the inverse-probit function has a known asymptotic expansion:</p>

<p align="center">
  <strong>Φ<sup>-1</sup>(p) ≈ −√(2·ln(1/p))</strong>
</p>

<p>When p = e<sup>−(δ + ln 2)</sup>, this becomes:</p>

<p align="center">
  <strong>EC(δ) ≈ √(2·(δ + ln 2)) ≈ √(2·δ)</strong>
</p>

<p>(The ln(2) term becomes negligible for δ >> 1.)</p>

<h4>Impact</h4>

<ul>
  <li><strong>Figure 3</strong> now extends to δ = 2000 without discontinuities, showing all curves smoothly through their zero crossings and beyond.</li>
  <li><strong>No new dependencies:</strong> Uses only NumPy, no mpmath or external libraries required.</li>
  <li><strong>Computational cost:</strong> Negligible; asymptotic branch is faster than probit.</li>
  <li><strong>Accuracy:</strong> Exact where possible, < 0.3% error in asymptotic regime.</li>
</ul>

<p><strong>Example:</strong> σ=10% now visibly crosses zero at δ ≈ 712 and continues smoothly up to δ = 2000, demonstrating the model's behavior across a wide range of displacement values.</p>

<!-- Examples were used during development to compare formula variants. These example artifacts are not committed to the canonical history. Generate comparison outputs locally with the scripts in `scripts/` or by running `python sif_model.py`. -->


<h2>⚖️ License & Legal Warning</h2>

<p><strong>Copyright © 2026 Emmanuel Normabuena. All Rights Reserved.</strong></p>

<p>This repository is dual-licensed to ensure maximum protection of the intellectual property while allowing academic transparency.</p>

<h3>1. The Source Code (Software)</h3>
<p>The code provided in <code>sif_model.py</code> and any associated scripts are licensed under the <strong>GNU Affero General Public License v3.0 (AGPLv3)</strong>.</p>
<ul>
  <li>✅ <strong>Open Source:</strong> You are free to run, study, share, and modify the code.</li>
  <li>⚠️ <strong>Network Use Clause:</strong> If you run this software on a server (e.g., a web service, SaaS, or internal bank backend) and let users interact with it remotely, <strong>you MUST release your full source code</strong> under this same license.</li>
  <li>See the <code>LICENSE</code> file for the full legal text.</li>
</ul>

<h3>2. The Whitepaper (PDF)</h3>
<p>The academic paper <em>"The Subsidy Immunity Formula (SIF)"</em> is licensed under the <strong>Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License (CC BY-NC-ND 4.0)</strong>.</p>
<ul>
  <li>✅ <strong>You are free to:</strong> Share, copy, and redistribute the material in any medium or format.</li>
  <li>❌ <strong>You may NOT:</strong> Use the material for commercial purposes (selling, training paid models, inclusion in paid courses).</li>
  <li>❌ <strong>You may NOT:</strong> Remix, transform, or build upon the material. If you modify the material, you may not distribute the modified material.</li>
</ul>

<hr>
<p><em>For commercial licensing inquiries or academic collaboration, please contact the author directly.</em></p>
