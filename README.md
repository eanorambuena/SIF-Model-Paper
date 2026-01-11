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
<h2>⚠️ Numerical Stability & Limitations</h2>

<h3>The Probit Function Overflow Problem</h3>

<p>The core calculation uses the exact inverse-probit formula for the Exigence Coefficient:</p>

<p align="center">
  <strong>EC(δ) = |Φ<sup>-1</sup>( 1 / (2·e<sup>δ</sup>) )|</strong>
</p>

<p>This formula exhibits a critical numerical limitation for large displacement values:</p>

<ul>
  <li><strong>For δ < ~700:</strong> The computation is numerically stable and accurate.</li>
  <li><strong>For δ ≥ ~710:</strong> The exponential term <code>exp(δ)</code> overflows to infinity in IEEE 754 floating-point arithmetic, causing <code>1/(2·exp(δ))</code> to collapse to zero.</li>
  <li><strong>Result:</strong> When the probit argument becomes zero, <code>Φ<sup>-1</sup>(0) = -∞</code>, causing a discontinuous jump in EC and SST.</li>
</ul>

<p><strong>Figure 3 (Sensitivity to Volatility)</strong> demonstrates this phenomenon:</p>

<ul>
  <li><strong>σ=20%:</strong> Crosses zero at δ ≈ 2.3 (well-behaved)</li>
  <li><strong>σ=15%:</strong> Crosses zero at δ ≈ 702 (approaching stability limit)</li>
  <li><strong>σ=10%:</strong> Theoretically crosses at δ ≈ 712, but numerical overflow prevents display</li>
</ul>

<p><strong>Mitigation:</strong> The implementation caps the displacement range at δ = 700 to ensure all curves remain continuous and mathematically sound.</p>

<h3>Theoretical Behavior at Large δ</h3>

<p>Mathematically, as δ → ∞:</p>

<ul>
  <li>EC(δ) → √(2·δ) [asymptotic approximation]</li>
  <li>The quadratic penalty term → constant or grows slower than the linear term</li>
  <li>SST eventually becomes positive for all volatility levels (but computationally intractable)</li>
</ul>

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
