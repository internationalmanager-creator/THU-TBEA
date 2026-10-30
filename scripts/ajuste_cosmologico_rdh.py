"""Ajuste cosmologico THU vs Lambda-CDM con DESI DR2 BAO.

Variante corregida de scripts/ajuste_cosmologico.py.

Diferencia con el original: los datos son DM/rd, DH/rd, DV/rd, y las distancias
se calculan con H0 = 100 km/s/Mpc, o sea en unidades Mpc*h. Por lo tanto el
parametro libre NO es rd en Mpc sino rd_h = rd * h en Mpc*h (~99-101), y el
rango de busqueda debe ser 90-115 (el original usaba 130-165, incompatible con
esa normalizacion: el optimizador quedaba pegado al borde inferior).

Escribe registry/thu/ajuste_cosmologico_corregido.json
"""
import json
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import differential_evolution

BASE = Path(__file__).resolve().parents[1]
BAO_MEAN = BASE / "data" / "raw" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
BAO_COV = BASE / "data" / "raw" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
OUT_FILE = BASE / "registry" / "thu" / "ajuste_cosmologico_corregido.json"

C_KMS = 299792.458


def cargar_bao():
    data = np.loadtxt(BAO_MEAN, comments="#", dtype=str)
    z = data[:, 0].astype(float)
    val = data[:, 1].astype(float)
    qty = data[:, 2]
    cov = np.loadtxt(BAO_COV, comments="#")
    print(f"BAO: {len(z)} puntos, cov {cov.shape}")
    return z, val, qty, cov


def E_LCDM(z, Om):
    return np.sqrt(Om * (1 + z) ** 3 + (1.0 - Om))


def E_THU(z, Om, Otau):
    return np.sqrt(Om * (1 + z) ** 3 + Otau * (1 + z) ** 6 + (1.0 - Om - Otau))


def predecir(z_arr, E_func, params):
    """DM, DH, DV en Mpc*h (H0 = 100 km/s/Mpc)."""
    DM = np.empty_like(z_arr)
    DH = np.empty_like(z_arr)
    for i, zi in enumerate(z_arr):
        DM[i] = C_KMS / 100.0 * quad(lambda zp: 1.0 / E_func(zp, *params), 0, zi)[0]
        DH[i] = C_KMS / 100.0 / E_func(zi, *params)
    DV = (z_arr * DM**2 * DH) ** (1 / 3)
    return DM, DH, DV


def chi2_bao(z, val, qty, cov_inv, E_func, params, rd_h):
    DM, DH, DV = predecir(z, E_func, params)
    pred = np.empty_like(val)
    for i, q in enumerate(qty):
        pred[i] = DM[i] if "DM" in q else (DH[i] if "DH" in q else DV[i])
    delta = val - pred / rd_h
    return float(delta @ cov_inv @ delta)


def main():
    print("=" * 60)
    print("  AJUSTE COSMOLOGICO THU vs LCDM (unidades rd*h)")
    print("=" * 60)

    z, val, qty, cov = cargar_bao()
    cov_inv = np.linalg.inv(cov)

    print("\n[1] Ajuste Lambda-CDM...")
    res_lcdm = differential_evolution(
        lambda p: chi2_bao(z, val, qty, cov_inv, E_LCDM, [p[0]], p[1]),
        [(0.05, 0.6), (90, 115)],
        seed=42,
        maxiter=1000,
        tol=1e-10,
        polish=True,
    )
    print(f"  Om = {res_lcdm.x[0]:.4f}, rd_h = {res_lcdm.x[1]:.2f} Mpc*h")
    print(f"  chi2 = {res_lcdm.fun:.2f}")

    print("\n[2] Ajuste THU (differential_evolution)...")
    res_thu = differential_evolution(
        lambda p: chi2_bao(z, val, qty, cov_inv, E_THU, [p[0], p[1]], p[2]),
        [(0.05, 0.6), (0.0, 0.3), (90, 115)],
        seed=42,
        maxiter=1000,
        tol=1e-10,
        polish=True,
    )
    print(f"  Om = {res_thu.x[0]:.4f}, Otau = {res_thu.x[1]:.4f}, rd_h = {res_thu.x[2]:.2f} Mpc*h")
    print(f"  chi2 = {res_thu.fun:.2f}")

    n_lcdm, n_thu = 2, 3
    aic_lcdm = res_lcdm.fun + 2 * n_lcdm
    aic_thu = res_thu.fun + 2 * n_thu
    delta_chi2 = res_lcdm.fun - res_thu.fun
    delta_aic = aic_thu - aic_lcdm

    print("\n[3] Comparacion:")
    print(f"  chi2_LCDM = {res_lcdm.fun:.2f} (k={n_lcdm})")
    print(f"  chi2_THU  = {res_thu.fun:.2f} (k={n_thu})")
    print(f"  Delta chi2 = {delta_chi2:.2f}")
    print(f"  AIC_LCDM = {aic_lcdm:.2f}")
    print(f"  AIC_THU  = {aic_thu:.2f}")
    print(f"  Delta AIC = {delta_aic:.2f}")
    print(f"  dof = {len(z) - n_lcdm}, chi2/dof (LCDM) = {res_lcdm.fun / (len(z) - n_lcdm):.2f}")

    if delta_aic < -2:
        veredicto = "THU preferido"
    elif delta_aic > 2:
        veredicto = "LCDM preferido"
    else:
        veredicto = "equivalentes"
    print("  ->", veredicto, "por AIC")

    resultado = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "datos": "DESI DR2 BAO (13 puntos)",
        "unidades_rd": "Mpc*h (H0=100; rd_h = rd*h)",
        "modelo_LCDM": {
            "Om": float(res_lcdm.x[0]),
            "rd_h": float(res_lcdm.x[1]),
            "chi2": float(res_lcdm.fun),
            "k": n_lcdm,
            "AIC": float(aic_lcdm),
        },
        "modelo_THU": {
            "Om": float(res_thu.x[0]),
            "Otau": float(res_thu.x[1]),
            "rd_h": float(res_thu.x[2]),
            "chi2": float(res_thu.fun),
            "k": n_thu,
            "AIC": float(aic_thu),
        },
        "delta_chi2": float(delta_chi2),
        "delta_AIC": float(delta_aic),
        "n_datos": len(z),
        "veredicto": veredicto,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, indent=2, ensure_ascii=False)
    print(f"\nGuardado: {OUT_FILE}")
    return resultado


if __name__ == "__main__":
    main()
