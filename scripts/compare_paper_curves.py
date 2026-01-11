import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))
import numpy as np
import matplotlib.pyplot as plt
from sif_model import calculate_sst

out = Path('figures')
out.mkdir(exist_ok=True)

delta = np.linspace(0.01, 5, 400)

# exact EC-based SST
sst_exact = calculate_sst(delta, r=0.05, sigma=0.20, use_exact=True)
# original approximation used earlier in code (polynomial EC)
sst_approx = calculate_sst(delta, r=0.05, sigma=0.20, use_exact=False)
# whitepaper formula approximation provided by user
sst_paper = (delta / 0.05) - (delta / (0.2 * (0.8 * delta + 1.2))) ** 2

# Save CSV with all three
arr = np.column_stack([delta, sst_exact, sst_approx, sst_paper])
np.savetxt(out / 'compare_curves.csv', arr, delimiter=',', header='delta,exact,approx,whitepaper', comments='')

# Numeric diffs
def stats(a, b):
    d = np.abs(a - b)
    return d.max(), d.mean()

max_e_p, mean_e_p = stats(sst_exact, sst_paper)
max_a_p, mean_a_p = stats(sst_approx, sst_paper)
print(f'exact vs paper: max_abs_diff={max_e_p:.6f}, mean_abs_diff={mean_e_p:.6f}')
print(f'approx vs paper: max_abs_diff={max_a_p:.6f}, mean_abs_diff={mean_a_p:.6f}')

# Plot overlay
plt.figure(figsize=(10,6))
plt.plot(delta, sst_paper, label='Paper formula', color='black', linewidth=2)
plt.plot(delta, sst_exact, label='Exact EC', color='blue', linestyle='-')
plt.plot(delta, sst_approx, label='Polynomial approx EC', color='red', linestyle='--')
plt.axhline(0, color='gray', linestyle=':')
plt.xlabel('delta')
plt.ylabel('SST (years)')
plt.title('Comparison: Paper formula vs Exact EC vs Polynomial approx')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(out / 'compare_curves.png', bbox_inches='tight')
plt.close()
print('Wrote figures/compare_curves.png and figures/compare_curves.csv')
