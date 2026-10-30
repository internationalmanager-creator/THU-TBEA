#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D.4 (alternativas) --- Ajuste cosmologico de modelos con torsion extendida
frente a Lambda-CDM, con DESI DR2 BAO + Pantheon+ SNe.

Modelos:
  M0  LCDM                      E^2 = Om(1+z)^3 + OL                    (k=3)
  M1  THU rigido                E^2 = Om(1+z)^3 + Ot(1+z)^6 + OL        (k=4)
  M2  torsion + potencial       E^2 = Om(1+z)^3 + Ot(1+z)^{3(1+w)} + OL (k=5)
      (V(phi) no nulo que decae; w=1 recupera el rigido, w<1 decae mas lento)
  M3  acoplamiento no minimo    Q = xi H rho_m  (DM -> torsion)
      rho_m = Om a^{-(3+xi)}
      rho_t = [Ot + Om xi/(3-xi)] a^{-6} - Om xi/(3-xi) a^{-(3+xi)}      (k=5)
  M4  torsion-DE interactuante  Q = xi H rho_t  (torsion -> DE)
      rho_t = Ot a^{-(6+xi)}
      rho_DE = OL + Ot xi/(5+xi) [1 - a^{-(5+xi)}]                       (k=5)

Parametros comunes: Om, Ot, xi/w, rd_h (Mpc*h), M0 (offset de magnitud SNe).
Convencion de distancias: H0 = 100 km/s/Mpc -> DM, DH, DV en Mpc*h y
d_L en Mpc*h; M0 absorbe 5 log10(h). Esto evita el error de unidades del
script original (rd en Mpc con H0=100).

Datos:
  BAO: DESI DR2, 13 puntos, covarianza completa.
  SNe: Pantheon+ (1701), covarianza STAT+SYS completa, M marginalizada
       analiticamente.
"""
import numpy as np
from pathlib import Path
from scipy.integrate import quad
from scipy.linalg import cho_factor, cho_solve
from scipy.optimize import differential_evolution, minimize
import json
import sys
import time

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
C_KMS = 299792.458

GL_X, GL_W = np.polynomial.legendre.leggauss(64)   # nodos para DM(z) del BAO


# ---------------------------------------------------------------------------
# datos
# ---------------------------------------------------------------------------
def cargar_bao():
    d = np.loadtxt(RAW / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt", comments="#", dtype=str)
    z = d[:, 0].astype(float)
    val = d[:, 1].astype(float)
    qty = d[:, 2]
    cov = np.loadtxt(RAW / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt", comments="#")
    return z, val, qty, np.linalg.inv(cov)


def cargar_sne():
    path = RAW / "pantheon_plus" / "Pantheon+SH0ES.dat"
    data = np.loadtxt(path, skiprows=1, usecols=(2, 8, 9))  # zHD, m_b_corr, err_DIAG
    z, mb, err = data[:, 0], data[:, 1], data[:, 2]
    # el archivo trae "1701" en la primera linea y luego la matriz por filas.
    # Se cachea en .npy: np.fromstring con separador tarda minutos con 2.9e6 valores.
    cache = RAW / "pantheon_plus" / "_cov.npy"
    if cache.exists():
        vals = np.load(cache)
    else:
        with open(RAW / "pantheon_plus" / "Pantheon+SH0ES_STAT+SYS.cov", "rb") as fh:
            fh.readline()
            vals = np.array(fh.read().split(), dtype=float)
        np.save(cache, vals)
    n = len(z)
    cov = vals.reshape(n, n)
    return z, mb, err, cov


# ---------------------------------------------------------------------------
# modelos: E^2(z)
# ---------------------------------------------------------------------------
def E2(z, p, modelo):
    Om = p[0]
    if modelo == "LCDM":
        return Om * (1 + z) ** 3 + (1 - Om)
    if modelo == "WCDM":
        # control: un solo fluido de DE con w libre (mismo k que THU+1)
        w = p[1]
        return Om * (1 + z) ** 3 + (1 - Om) * (1 + z) ** (3 * (1 + w))
    Ot = p[1]
    if modelo == "THU":
        return Om * (1 + z) ** 3 + Ot * (1 + z) ** 6 + (1 - Om - Ot)
    if modelo == "POT":
        w = p[2]
        return Om * (1 + z) ** 3 + Ot * (1 + z) ** (3 * (1 + w)) + (1 - Om - Ot)
    a = 1.0 / (1 + z)
    xi = p[2]
    if modelo == "TAU_DM":
        rm = Om * a ** (-(3 + xi))
        rt = (Ot + Om * xi / (3 - xi)) * a ** (-6) - Om * xi / (3 - xi) * a ** (-(3 + xi))
        return rm + rt + (1 - Om - Ot)
    if modelo == "TAU_DE":
        rm = Om * a ** (-3)
        rt = Ot * a ** (-(6 + xi))
        rde = (1 - Om - Ot) + Ot * xi / (5 + xi) * (1 - a ** (-(5 + xi)))
        return rm + rt + rde
    raise ValueError(modelo)


# ---------------------------------------------------------------------------
# chi2
# ---------------------------------------------------------------------------
def chi2_bao(z, val, qty, cov_inv, p, modelo):
    # DM(z) por cuadratura de Gauss-Legendre (64 nodos): rapida y exacta para E(z) suave
    half = z / 2.0
    nodes = half[:, None] * (GL_X[None, :] + 1.0)
    En = np.sqrt(np.maximum(E2(nodes, p, modelo), 1e-12))
    DM = C_KMS / 100.0 * half * np.sum(GL_W[None, :] / En, axis=1)
    DH = C_KMS / 100.0 / np.sqrt(np.maximum(E2(z, p, modelo), 1e-12))
    DV = (z * DM**2 * DH) ** (1 / 3)
    rd = p[-1]
    pred = np.array([DM[i] if "DM" in q else (DH[i] if "DH" in q else DV[i]) for i, q in enumerate(qty)]) / rd
    delta = val - pred
    return float(delta @ cov_inv @ delta)


def chi2_sne(z, mb, cinv, w, s2, p, modelo, sne_cache):
    """chi2 con M marginalizada analiticamente.

    cinv = C^-1 (precomputada), w = C^-1 1, s2 = 1^T C^-1 1.
    Se evita cho_solve porque en esta maquina tarda 65 ms por llamada.
    """
    zs, idx = sne_cache
    E = np.sqrt(np.maximum(E2(zs, p, modelo), 1e-12))
    invE = 1.0 / E
    zs_ext = np.concatenate([[0.0], zs])
    invE_ext = np.concatenate([[1.0], invE])
    dz = np.diff(zs_ext)
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (invE_ext[1:] + invE_ext[:-1]) * dz)])[1:]
    dl_h = (1 + zs) * C_KMS / 100.0 * cum          # Mpc*h
    if np.any(~np.isfinite(dl_h)) or np.any(dl_h <= 0):
        return 1e12
    mu = 5.0 * np.log10(dl_h) + 25.0
    delta = (mb - mu)[idx]
    s0 = float(delta @ (cinv @ delta))
    s1 = float(delta @ w)
    return s0 - s1**2 / s2


# ---------------------------------------------------------------------------
def main():
    print("=" * 78)
    print("  AJUSTE COSMOLOGICO: TORSION EXTENDIDA vs LCDM")
    print("=" * 78)

    zb, vb, qb, covb_inv = cargar_bao()
    print(f"BAO : {len(zb)} puntos", flush=True)
    zs, mbs, errs, covs = cargar_sne()
    print(f"SNe : {len(zs)} puntos (Pantheon+, cov STAT+SYS {covs.shape})", flush=True)
    cho = cho_factor(covs, lower=True)
    cinv = np.linalg.inv(covs)
    ones = np.ones(len(zs))
    w = cinv @ ones
    s2 = float(ones @ w)
    print("covarianza invertida", flush=True)

    order = np.argsort(zs)
    idx = np.argsort(order)
    sne_cache = (zs[order], idx)

    def chi2_total(p, modelo):
        e = E2(np.array([0.0, 0.5, 1.0, 2.0, 3.0]), p, modelo)
        if np.any(~np.isfinite(e)) or np.any(e <= 0):
            return 1e12
        return chi2_bao(zb, vb, qb, covb_inv, p, modelo) + chi2_sne(zs, mbs, cinv, w, s2, p, modelo, sne_cache)

    modelos = {
        #  nombre        bounds                                        k
        "LCDM": ([(0.15, 0.5), (90, 115)], 3),
        "WCDM": ([(0.15, 0.5), (-1.5, 0.0), (90, 115)], 4),      # control DE
        "THU": ([(0.15, 0.5), (0.0, 0.20), (90, 115)], 4),
        "POT": ([(0.15, 0.5), (0.0, 0.30), (-1.0, 1.0), (90, 115)], 5),
        "TAU_DM": ([(0.15, 0.5), (0.0, 0.30), (0.0, 2.0), (90, 115)], 5),
        "TAU_DE": ([(0.15, 0.5), (0.0, 0.30), (0.0, 2.0), (90, 115)], 5),
    }
    # punto anidado LCDM dentro de cada modelo extendido (Ot=0, x=0):
    # sirve para verificar que el optimizador no se quedo en un minimo malo
    def plegado(nombre, p_lcdm):
        Om, rd = p_lcdm
        if nombre in ("LCDM", "WCDM"):
            return None
        if nombre == "THU":
            return [Om, 0.0, rd]
        if nombre == "POT":
            return [Om, 0.0, -1.0, rd]
        return [Om, 0.0, 0.0, rd]

    def bounds_ok(p, bounds):
        return all(lo - 1e-9 <= v <= hi + 1e-9 for v, (lo, hi) in zip(p, bounds))

    resultados = {}
    for nombre, (bounds, k) in modelos.items():
        t0 = time.time()
        res = differential_evolution(
            lambda p: chi2_total(p, nombre), bounds, seed=42, maxiter=50,
            tol=1e-6, polish=True, popsize=10, workers=1,
        )
        chi2 = res.fun
        p = list(res.x)
        # chequeo anidado: si el modelo contiene LCDM, comparar con ese punto
        nota = ""
        if "LCDM" in resultados:
            pn = plegado(nombre, [resultados["LCDM"]["p"][0], resultados["LCDM"]["p"][-1]])
            if pn is not None and bounds_ok(pn, bounds):
                cn = chi2_total(pn, nombre)
                if cn < chi2 - 0.05:
                    chi2, p = cn, pn
                    nota = " [se uso el punto anidado LCDM: DE habia quedado en un minimo malo]"
        if nombre == "LCDM":
            desc = f"Om={p[0]:.4f} rd_h={p[1]:.2f}"
        elif nombre == "WCDM":
            desc = f"Om={p[0]:.4f} w={p[1]:+.3f} rd_h={p[2]:.2f}"
        elif nombre == "THU":
            desc = f"Om={p[0]:.4f} Ot={p[1]:.4f} rd_h={p[2]:.2f}"
        else:
            desc = f"Om={p[0]:.4f} Ot={p[1]:.4f} x={p[2]:+.3f} rd_h={p[3]:.2f}"
        resultados[nombre] = {"chi2": chi2, "k": k, "p": p, "AIC": chi2 + 2 * k, "desc": desc}
        print(f"{nombre:>7}: chi2 = {chi2:9.2f} (k={k}) AIC = {chi2+2*k:9.2f}  {desc}   [{time.time()-t0:.0f}s]{nota}", flush=True)

    base = resultados["LCDM"]["AIC"]
    print("\n" + "=" * 78)
    print("  COMPARACION")
    print("=" * 78)
    print(f"{'modelo':>8} {'chi2':>10} {'k':>3} {'AIC':>10} {'dAIC':>8} {'dchi2':>8}")
    for nombre, r in resultados.items():
        print(f"{nombre:>8} {r['chi2']:>10.2f} {r['k']:>3} {r['AIC']:>10.2f} "
              f"{r['AIC']-base:>+8.2f} {r['chi2']-resultados['LCDM']['chi2']:>+8.2f}")

    # limite sobre Ot: barrido 1D con los demas parametros FIJOS en el best fit
    # (perfil aproximado; se declara como tal)
    print("\n" + "=" * 78)
    print("  LIMITE SOBRE Ot (barrido 1D, otros parametros fijos en el best fit)")
    print("=" * 78)
    mejor = resultados["THU"]
    p_thu = list(mejor["p"])
    chis = []
    for ot in [0.0, 0.002, 0.005, 0.01, 0.02, 0.04, 0.08]:
        p = [p_thu[0], ot, p_thu[2]]
        c = chi2_total(p, "THU")
        chis.append((ot, c))
        print(f"   Ot = {ot:.3f}  chi2 = {c:.2f}   dchi2 = {c - mejor['chi2']:+.2f}")
    limite = max([ot for ot, c in chis if c - mejor["chi2"] <= 1.0], default=0.0)
    print(f"   -> Ot <~ {limite:.3f} (95%: ~{2*limite:.3f} si el perfil es par)")

    print("\n" + "=" * 78)
    print("  VEREDICTO")
    print("=" * 78)
    mejor_modelo = min(resultados, key=lambda n: resultados[n]["AIC"])
    print(f"   mejor AIC: {mejor_modelo}")
    for nombre, r in resultados.items():
        if nombre == "LCDM":
            continue
        d = r["AIC"] - base
        etiqueta = "mejora" if d < -2 else ("equivalente" if d < 2 else "no mejora")
        print(f"   {nombre:>7}: dAIC = {d:+7.2f}  ({etiqueta})")

    out = BASE / "registry" / "thu" / "ajuste_cosmologico_alternativas.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "p"} for k, v in resultados.items()},
                  fh, indent=2, ensure_ascii=False)
    print(f"\nGuardado: {out}")
    return resultados


if __name__ == "__main__":
    main()
