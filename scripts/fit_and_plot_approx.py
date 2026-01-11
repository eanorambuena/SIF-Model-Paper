import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from sif_model import calculate_sst

out = Path('examples')
out.mkdir(exist_ok=True)

# sst approximation form used in paper: delta/r - (delta / (sigma * (a*delta + b)))**2
def sst_paper_form(delta, r, sigma, a, b):
    return (delta / r) - (delta / (sigma * (a * delta + b))) ** 2

# objective for single sigma: minimize MSE between sst_paper_form and exact sst

def fit_params_for_sigma(delta, r, sigma, a0=(0.8,1.2)):
    exact = calculate_sst(delta, r=r, sigma=sigma, use_exact=True)

    def loss_ab(ab):
        a, b = ab
        pred = sst_paper_form(delta, r, sigma, a, b)
        return np.mean((pred - exact) ** 2)

    bounds = [(1e-6, 10.0), (1e-6, 10.0)]
    res = minimize(loss_ab, x0=np.array(a0), bounds=bounds, method='L-BFGS-B')
    return res

# global fit across multiple sigmas: sum MSE

def fit_params_global(delta, r, sigmas, a0=(0.8,1.2)):
    ex_by_sigma = [calculate_sst(delta, r=r, sigma=s, use_exact=True) for s in sigmas]

    def loss_ab(ab):
        a, b = ab
        s = 0.0
        for sigma, exact in zip(sigmas, ex_by_sigma):
            pred = sst_paper_form(delta, r, sigma, a, b)
            s += np.mean((pred - exact) ** 2)
        return s

    bounds = [(1e-6, 10.0), (1e-6, 10.0)]
    res = minimize(loss_ab, x0=np.array(a0), bounds=bounds, method='L-BFGS-B')
    return res


def make_plot(delta, r, sigma, a_fit, b_fit, outname_prefix):
    exact = calculate_sst(delta, r=r, sigma=sigma, use_exact=True)
    approx = calculate_sst(delta, r=r, sigma=sigma, use_exact=False)
    paper_orig = sst_paper_form(delta, r, sigma, 0.8, 1.2)
    paper_fit = sst_paper_form(delta, r, sigma, a_fit, b_fit)

    # Plot
    plt.figure(figsize=(8,5))
    plt.plot(delta, exact, label='Exact EC', color='blue')
    plt.plot(delta, paper_orig, label='Paper orig (0.8,1.2)', color='black', linewidth=2)
    plt.plot(delta, paper_fit, label=f'Fitted (a={a_fit:.4f}, b={b_fit:.4f})', color='green', linestyle='--')
    plt.plot(delta, approx, label='Poly approx', color='red', linestyle=':')
    plt.axhline(0, color='gray', linestyle=':')
    plt.xlabel('delta')
    plt.ylabel('SST (years)')
    plt.title(f'Compare (r={r}, sigma={sigma})')
    plt.legend(fontsize='small')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / f'{outname_prefix}_fit.png', dpi=300)
    plt.savefig(out / f'{outname_prefix}_fit.pdf')
    plt.close()

    # Save CSV
    arr = np.column_stack([delta, exact, paper_orig, paper_fit, approx])
    np.savetxt(out / f'{outname_prefix}_fit.csv', arr, delimiter=',', header='delta,exact,paper_orig,paper_fit,poly_approx', comments='')

    # stats
    def stats(a, b):
        d = np.abs(a - b)
        return float(d.max()), float(d.mean()), float(np.sqrt((d ** 2).mean()))

    return stats(exact, paper_fit), stats(exact, paper_orig), stats(exact, approx)


if __name__ == '__main__':
    r = 0.05
    # use zoom range where paper figures focus
    delta_zoom = np.linspace(0.001, 1.0, 400)

    # Fit separately for sigma=0.2 and sigma=0.5
    res20 = fit_params_for_sigma(delta_zoom, r, 0.2)
    res50 = fit_params_for_sigma(delta_zoom, r, 0.5)

    print('Fit results sigma=0.2:', res20.x, 'loss:', res20.fun)
    print('Fit results sigma=0.5:', res50.x, 'loss:', res50.fun)

    # Global fit across both sigmas
    res_global = fit_params_global(delta_zoom, r, [0.2, 0.5])
    print('Global fit (both sigmas):', res_global.x, 'loss:', res_global.fun)

    # Make plots and get stats
    s20_fit_stats, s20_orig_stats, s20_poly_stats = make_plot(delta_zoom, r, 0.2, res20.x[0], res20.x[1], 'sigma20')
    s50_fit_stats, s50_orig_stats, s50_poly_stats = make_plot(delta_zoom, r, 0.5, res50.x[0], res50.x[1], 'sigma50')
    s_global_20_stats, _, _ = make_plot(delta_zoom, r, 0.2, res_global.x[0], res_global.x[1], 'sigma20_globalfit')
    s_global_50_stats, _, _ = make_plot(delta_zoom, r, 0.5, res_global.x[0], res_global.x[1], 'sigma50_globalfit')

    print('\nStats (exact vs fitted, exact vs orig, exact vs poly):')
    print('sigma=20%: fitted stats (max,mean,rmse) =', s20_fit_stats)
    print('sigma=20%: orig stats (max,mean,rmse)   =', s20_orig_stats)
    print('sigma=20%: poly stats (max,mean,rmse)   =', s20_poly_stats)

    print('sigma=50%: fitted stats (max,mean,rmse) =', s50_fit_stats)
    print('sigma=50%: orig stats (max,mean,rmse)   =', s50_orig_stats)
    print('sigma=50%: poly stats (max,mean,rmse)   =', s50_poly_stats)

    print('Global fit params:', res_global.x)
    print('Done. Plots and CSVs saved to examples/')
