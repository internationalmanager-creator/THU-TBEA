"""Tests del motor estadistico."""
import numpy as np
import pytest

import estadistica as E


def test_bootstrap_ci_media():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 200)
    r = E.bootstrap_ci(x, n=500, seed=0)
    lo, hi = r["ci_percentil"]
    assert lo < 0 < hi
    assert r["n"] == 200


def test_ks_loguniform_datos_uniformes():
    rng = np.random.default_rng(0)
    x = 10 ** rng.uniform(-2, 1, 500)
    r = E.ks_loguniform(x)
    assert r["p_valor"] > 0.01, f"p={r['p_valor']}"


def test_ks_loguniform_datos_no_uniformes():
    rng = np.random.default_rng(0)
    x = 10 ** rng.normal(0, 0.3, 500)
    r = E.ks_loguniform(x)
    assert r["p_valor"] < 0.01, f"p={r['p_valor']}"


def test_cuantizacion_ratios_serie_geometrica():
    x = 2 ** np.arange(1, 20)
    r = E.cuantizacion_ratios(x)
    assert r["estadistico"] < 0.01
    assert r["veredicto"] == "rechaza_h0"


def test_cuantizacion_ratios_ruido():
    """Datos lognormal (dispersion en muchas decadas) -> CV alto (no cuantizacion)."""
    rng = np.random.default_rng(0)
    # Lognormal con sigma=2 -> dispersion real en ~4 ordenes de magnitud
    x = np.sort(np.exp(rng.normal(0, 2, 100)))
    r = E.cuantizacion_ratios(x)
    # Umbral de cuantizacion es CV < 0.3; con datos dispersos esperamos CV >> 0.3
    assert r["estadistico"] > 0.3, f"CV={r['estadistico']}"
    assert r["veredicto"] == "no_rechaza_h0"


def test_benford_fibonacci():
    fib = [1, 1]
    while len(fib) < 200:
        fib.append(fib[-1] + fib[-2])
    r = E.benford_test(np.array(fib))
    assert r["p_valor"] > 0.01


def test_autocorrelacion_ruido_blanco():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 500)
    r = E.autocorrelacion(x)
    assert r["veredicto"] == "no_rechaza_h0"


def test_autocorrelacion_senal_periodica():
    t = np.arange(500)
    rng = np.random.default_rng(0)
    x = np.sin(2 * np.pi * t / 20) + 0.1 * rng.normal(0, 1, 500)
    r = E.autocorrelacion(x, max_lag=30)
    assert r["veredicto"] == "rechaza_h0"


def test_anderson_normal():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 200)
    r = E.anderson_darling_normal(x)
    assert r["veredicto"] == "no_rechaza_h0"


def test_powerlaw_fit_sobre_datos_powerlaw():
    rng = np.random.default_rng(0)
    u = rng.uniform(0, 1, 1000)
    x = 1 * (1 - u) ** (-1 / (2.5 - 1))
    r = E.powerlaw_fit(x)
    assert 2.0 < r["estadistico"] < 3.0, f"alpha={r['estadistico']}"


def test_permutation_test_detecta_diferencia():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 50)
    y = rng.normal(1.0, 1, 50)
    r = E.permutation_test(x, y, n=500, seed=0)
    assert r["p_valor"] < 0.05, f"p={r['p_valor']}"


def test_permutation_test_no_detecta_sin_diferencia():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 50)
    y = rng.normal(0, 1, 50)
    r = E.permutation_test(x, y, n=500, seed=0)
    assert r["p_valor"] > 0.05, f"p={r['p_valor']}"