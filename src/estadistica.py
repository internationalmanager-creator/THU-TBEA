"""Motor estadistico para PIR.

Tests implementados:
    1. bootstrap_ci         - CI percentil + BCa
    2. permutation_test     - H0: x,y misma distribucion
    3. ks_loguniform        - H0: log10(x) ~ Uniforme
    4. powerlaw_fit         - Clauset-Shalizi-Newman 2009
    5. cuantizacion_ratios  - CV de ratios consecutivos
    6. benford_test         - Chi-cuadrado del primer digito
    7. autocorrelacion      - ACF clasica
    8. anderson_darling_normal - normalidad robusta

Cada test devuelve dict con:
    {
        "test": nombre,
        "estadistico": valor,
        "p_valor": valor o None,
        "n": tamano de muestra,
        "parametros": {...},
        "veredicto": "rechaza_h0" | "no_rechaza_h0" | "inconcluso",
        "interpretacion": "..."
    }
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats
from tqdm import tqdm


# ============================================================
# 1. Bootstrap CI
# ============================================================

def bootstrap_ci(x, stat_fn=None, n=10000, alpha=0.05, seed=42):
    """Percentile bootstrap CI + BCa.

    x: array 1-D
    stat_fn: funcion(x) -> escalar. Default: media.
    """
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    N = len(x)
    if N < 5:
        return {"test": "bootstrap_ci", "estadistico": None, "p_valor": None,
                "n": N, "veredicto": "inconcluso",
                "interpretacion": "N < 5"}

    stat_fn = stat_fn or np.mean
    theta_hat = float(stat_fn(x))
    boots = np.empty(n)
    idx = np.arange(N)
    for i in tqdm(range(n), desc="bootstrap", ncols=80, leave=False):
        s = rng.choice(idx, size=N, replace=True)
        boots[i] = stat_fn(x[s])

    lo = float(np.percentile(boots, 100 * alpha / 2))
    hi = float(np.percentile(boots, 100 * (1 - alpha / 2)))

    # BCa
    try:
        z0 = float(stats.norm.ppf(np.mean(boots < theta_hat)))
        jack = np.array([stat_fn(np.delete(x, i)) for i in range(N)])
        jack_mean = jack.mean()
        num = float(np.sum((jack_mean - jack) ** 3))
        den = 6 * (float(np.sum((jack_mean - jack) ** 2)) ** 1.5)
        a_hat = num / den if den != 0 else 0.0
        z_lo = stats.norm.ppf(alpha / 2)
        z_hi = stats.norm.ppf(1 - alpha / 2)
        a1 = stats.norm.cdf(z0 + (z0 + z_lo) / (1 - a_hat * (z0 + z_lo)))
        a2 = stats.norm.cdf(z0 + (z0 + z_hi) / (1 - a_hat * (z0 + z_hi)))
        lo_bca = float(np.percentile(boots, 100 * a1))
        hi_bca = float(np.percentile(boots, 100 * a2))
    except Exception:
        lo_bca, hi_bca = lo, hi

    return {
        "test": "bootstrap_ci",
        "estadistico": theta_hat,
        "p_valor": None,
        "n": N,
        "parametros": {"n_resamples": n, "alpha": alpha, "seed": seed},
        "ci_percentil": [lo, hi],
        "ci_bca": [lo_bca, hi_bca],
        "veredicto": "no_rechaza_h0",
        "interpretacion": (
            f"Media = {theta_hat:.4g}  CI95% percentil = [{lo:.4g}, {hi:.4g}]  "
            f"CI95% BCa = [{lo_bca:.4g}, {hi_bca:.4g}]"
        ),
    }


# ============================================================
# 2. Permutation test
# ============================================================

def permutation_test(x, y, stat_fn=None, n=10000, seed=42):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float); x = x[np.isfinite(x)]
    y = np.asarray(y, dtype=float); y = y[np.isfinite(y)]
    stat_fn = stat_fn or (lambda a, b: np.mean(a) - np.mean(b))
    obs = float(stat_fn(x, y))
    pool = np.concatenate([x, y])
    nx = len(x)
    dist = np.empty(n)
    for i in tqdm(range(n), desc="permutacion", ncols=80, leave=False):
        rng.shuffle(pool)
        dist[i] = stat_fn(pool[:nx], pool[nx:])
    p = float(np.mean(np.abs(dist) >= np.abs(obs)))
    return {
        "test": "permutation_test",
        "estadistico": obs,
        "p_valor": p,
        "n": [len(x), len(y)],
        "parametros": {"n_permutaciones": n, "seed": seed},
        "veredicto": "rechaza_h0" if p < 0.05 else "no_rechaza_h0",
        "interpretacion": f"diferencia = {obs:.4g}, p = {p:.4g}",
    }

# === PARTE 2 se agrega a continuacion ===

# ============================================================
# 3. KS contra log-uniforme
# ============================================================

def ks_loguniform(x, rango=None):
    """H0: log10(x) ~ Uniforme(rango).

    Test de Kolmogorov-Smirnov sobre log10(x).
    """
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x) & (x > 0)]
    if len(x) < 5:
        return {"test": "ks_loguniform", "estadistico": None, "p_valor": None,
                "n": len(x), "veredicto": "inconcluso",
                "interpretacion": "N < 5 o valores no positivos"}
    logx = np.log10(x)
    lo, hi = (float(min(logx)), float(max(logx))) if rango is None else rango
    z = (logx - lo) / (hi - lo)
    D, p = stats.kstest(z, "uniform")
    return {
        "test": "ks_loguniform",
        "estadistico": float(D),
        "p_valor": float(p),
        "n": int(len(x)),
        "parametros": {"rango_log10": [float(lo), float(hi)]},
        "veredicto": "no_rechaza_h0" if p >= 0.05 else "rechaza_h0",
        "interpretacion": (
            f"KS D = {D:.4f}, p = {p:.4f}. "
            f"{'Compatible con log-uniforme' if p >= 0.05 else 'No compatible con log-uniforme'}."
        ),
    }


# ============================================================
# 4. Power-law fit (Clauset-Shalizi-Newman 2009)
# ============================================================

def powerlaw_fit(x, xmin=None):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x) & (x > 0)]
    if len(x) < 10:
        return {"test": "powerlaw_fit", "estadistico": None, "p_valor": None,
                "n": int(len(x)), "veredicto": "inconcluso",
                "interpretacion": "N < 10"}

    if xmin is None:
        candidatos = np.unique(np.percentile(x, np.arange(5, 100, 5)))
        best = (np.inf, None, None, 0)
        for xm in candidatos:
            cola = x[x >= xm]
            if len(cola) < 10:
                continue
            alpha = 1 + len(cola) / np.sum(np.log(cola / xm))
            sorted_cola = np.sort(cola)
            cdf_emp = np.arange(1, len(sorted_cola) + 1) / len(sorted_cola)
            cdf_teo = 1 - (sorted_cola / xm) ** (1 - alpha)
            D = float(np.max(np.abs(cdf_emp - cdf_teo)))
            if D < best[0]:
                best = (D, float(xm), float(alpha), len(cola))
        D, xm, alpha, n_cola = best
    else:
        cola = x[x >= xmin]
        alpha = float(1 + len(cola) / np.sum(np.log(cola / xmin)))
        sorted_cola = np.sort(cola)
        cdf_emp = np.arange(1, len(sorted_cola) + 1) / len(sorted_cola)
        cdf_teo = 1 - (sorted_cola / xmin) ** (1 - alpha)
        D = float(np.max(np.abs(cdf_emp - cdf_teo)))
        xm = float(xmin)
        n_cola = int(len(cola))

    return {
        "test": "powerlaw_fit",
        "estadistico": float(alpha),
        "p_valor": None,
        "n": int(n_cola),
        "parametros": {"xmin": float(xm), "D_ks": float(D)},
        "veredicto": "inconcluso",
        "interpretacion": (
            f"alpha = {alpha:.4f}, xmin = {xm:.4g}, D_KS = {D:.4f}, "
            f"n_cola = {n_cola}. Comparar con lognormal y exponencial "
            f"antes de afirmar ley de potencia."
        ),
    }


# ============================================================
# 5. Cuantizacion por CV de ratios
# ============================================================

def cuantizacion_ratios(x):
    """CV de ratios consecutivos. CV < 0.3 sugiere cuantizacion."""
    x = np.sort(np.asarray(x, dtype=float))
    x = x[np.isfinite(x) & (x > 0)]
    if len(x) < 5:
        return {"test": "cuantizacion_ratios", "estadistico": None,
                "p_valor": None, "n": int(len(x)), "veredicto": "inconcluso",
                "interpretacion": "N < 5"}
    ratios = x[1:] / x[:-1]
    media = float(np.mean(ratios))
    std = float(np.std(ratios, ddof=1))
    cv = std / media if media > 0 else float("inf")
    return {
        "test": "cuantizacion_ratios",
        "estadistico": float(cv),
        "p_valor": None,
        "n": int(len(x)),
        "parametros": {"media_ratios": media, "std_ratios": std},
        "veredicto": "rechaza_h0" if cv < 0.3 else "no_rechaza_h0",
        "interpretacion": (
            f"CV ratios = {cv:.4f} (media={media:.4g}, std={std:.4g}). "
            f"{'CV bajo sugiere cuantizacion' if cv < 0.3 else 'Sin evidencia de cuantizacion'}"
        ),
    }

# === PARTE 3 se agrega a continuacion ===

# ============================================================
# 6. Benford (Newcomb-Benford 1881/1938)
# ============================================================

def benford_test(x):
    x = np.abs(np.asarray(x, dtype=float))
    x = x[np.isfinite(x) & (x > 0)]
    if len(x) < 30:
        return {"test": "benford", "estadistico": None, "p_valor": None,
                "n": int(len(x)), "veredicto": "inconcluso",
                "interpretacion": "N < 30"}
    primeros = np.array([int(str(int(v)).lstrip("0")[0]) for v in x if v >= 1])
    if len(primeros) < 30:
        return {"test": "benford", "estadistico": None, "p_valor": None,
                "n": int(len(primeros)), "veredicto": "inconcluso",
                "interpretacion": "Pocos valores >= 1"}
    esperado = np.log10(1 + 1 / np.arange(1, 10))
    observado = np.array([np.sum(primeros == d) for d in range(1, 10)])
    observado = observado / observado.sum()
    chi2, p = stats.chisquare(observado, esperado)
    return {
        "test": "benford",
        "estadistico": float(chi2),
        "p_valor": float(p),
        "n": int(len(x)),
        "parametros": {},
        "veredicto": "no_rechaza_h0" if p >= 0.05 else "rechaza_h0",
        "interpretacion": (
            f"chi2 = {chi2:.4f}, p = {p:.4f}. "
            f"{'Compatible con Benford' if p >= 0.05 else 'NO compatible con Benford'}"
        ),
    }


# ============================================================
# 7. Autocorrelacion
# ============================================================

def autocorrelacion(x, max_lag=20):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 10:
        return {"test": "autocorrelacion", "estadistico": None,
                "p_valor": None, "n": int(len(x)), "veredicto": "inconcluso",
                "interpretacion": "N < 10"}
    xc = x - x.mean()
    acf = np.correlate(xc, xc, mode="full")[len(x) - 1:] / np.sum(xc ** 2)
    acf = acf[:max_lag + 1]
    umbral = 1.96 / np.sqrt(len(x))
    significativos = int(np.sum(np.abs(acf[1:]) > umbral))
    return {
        "test": "autocorrelacion",
        "estadistico": float(np.max(np.abs(acf[1:]))),
        "p_valor": None,
        "n": int(len(x)),
        "parametros": {"max_lag": max_lag, "umbral_95": float(umbral)},
        "acf": acf.tolist(),
        "veredicto": "rechaza_h0" if significativos > 0 else "no_rechaza_h0",
        "interpretacion": (
            f"{significativos} lags > umbral 95% ({umbral:.4f}). "
            f"{'Hay estructura temporal' if significativos > 0 else 'Ruido blanco compatible'}"
        ),
    }


# ============================================================
# 8. Anderson-Darling normalidad
# ============================================================

def anderson_darling_normal(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < 8:
        return {"test": "anderson_darling_normal", "estadistico": None,
                "p_valor": None, "n": int(len(x)), "veredicto": "inconcluso",
                "interpretacion": "N < 8"}
    res = stats.anderson(x, dist="norm", method="interpolate")
    A2 = float(res.statistic)
    p = float(res.pvalue) if hasattr(res, "pvalue") else None
    if p is not None:
        rechaza = p < 0.05
        veredicto = "rechaza_h0" if rechaza else "no_rechaza_h0"
        interp = (
            f"A2 = {A2:.4f}, p = {p:.4f}. "
            f"{'Rechaza normalidad' if rechaza else 'Compatible con normal'}"
        )
    else:
        # Fallback API antigua
        crit_5 = float(res.critical_values[2])
        rechaza = A2 > crit_5
        veredicto = "rechaza_h0" if rechaza else "no_rechaza_h0"
        interp = (
            f"A2 = {A2:.4f}, critico 5% = {crit_5:.4f}. "
            f"{'Rechaza normalidad' if rechaza else 'Compatible con normal'}"
        )
    return {
        "test": "anderson_darling_normal",
        "estadistico": A2,
        "p_valor": p,
        "n": int(len(x)),
        "parametros": {},
        "veredicto": veredicto,
        "interpretacion": interp,
    }


# ============================================================
# CLI
# ============================================================

TESTS = {
    "bootstrap_ci": bootstrap_ci,
    "ks_loguniform": ks_loguniform,
    "powerlaw_fit": powerlaw_fit,
    "cuantizacion_ratios": cuantizacion_ratios,
    "benford": benford_test,
    "autocorrelacion": autocorrelacion,
    "anderson_darling_normal": anderson_darling_normal,
    "permutation": permutation_test,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", required=True, choices=list(TESTS.keys()))
    ap.add_argument("--input", required=True, help="CSV con datos")
    ap.add_argument("--col", default="valor_principal")
    ap.add_argument("--col2", default=None, help="segunda columna (permutation)")
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    import pandas as pd
    df = pd.read_csv(args.input)
    if args.col not in df.columns:
        print(f"ERROR: columna '{args.col}' no existe", file=sys.stderr)
        sys.exit(1)
    x = df[args.col].values

    if args.test == "permutation":
        if not args.col2 or args.col2 not in df.columns:
            print("ERROR: --col2 requerido para permutation", file=sys.stderr)
            sys.exit(1)
        res = permutation_test(x, df[args.col2].values, n=args.n)
    elif args.test == "bootstrap_ci":
        res = bootstrap_ci(x, n=args.n)
    else:
        res = TESTS[args.test](x)

    print(json.dumps(res, indent=2, ensure_ascii=False))
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(res, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")


if __name__ == "__main__":
    import sys as _sys
    import warnings as _warnings

    # Silenciar FutureWarning de scipy.anderson (API cambia en 1.19)
    _warnings.filterwarnings("ignore", category=FutureWarning)

    # Si hay argumentos CLI -> main()
    # Si no hay argumentos -> auto-test
    if len(_sys.argv) > 1:
        main()
    else:
        from tqdm import tqdm
        print("=== Test estadistica.py ===")
        rng = np.random.default_rng(0)

        def _fib(n):
            f = [1, 1]
            while len(f) < n:
                f.append(f[-1] + f[-2])
            return f

        casos = [
            ("bootstrap_ci",              lambda: bootstrap_ci(rng.normal(0, 1, 200), n=500, seed=0)),
            ("permutation_test",          lambda: permutation_test(rng.normal(0, 1, 50), rng.normal(0.5, 1, 50), n=500, seed=0)),
            ("ks_loguniform (uniforme)",  lambda: ks_loguniform(10 ** rng.uniform(-2, 1, 500))),
            ("ks_loguniform (normal)",    lambda: ks_loguniform(10 ** rng.normal(0, 0.3, 500))),
            ("powerlaw_fit",              lambda: powerlaw_fit(1 * (1 - rng.uniform(0, 1, 1000)) ** (-1 / 1.5))),
            ("cuantizacion_ratios (geo)", lambda: cuantizacion_ratios(2.0 ** np.arange(1, 20))),
            ("benford (fibonacci)",       lambda: benford_test(np.array(_fib(200)))),
            ("autocorrelacion (ruido)",   lambda: autocorrelacion(rng.normal(0, 1, 500))),
            ("anderson (normal)",         lambda: anderson_darling_normal(rng.normal(0, 1, 200))),
        ]

        for nombre, fn in tqdm(casos, desc="Tests", ncols=80):
            r = fn()
            v = r["veredicto"]
            assert v in ("rechaza_h0", "no_rechaza_h0", "inconcluso"), f"{nombre}: veredicto invalido {v}"

        print("=== TEST OK ===")