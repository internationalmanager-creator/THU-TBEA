#!/usr/bin/env python3
"""Chequeo independiente del ajuste BAO DESI DR2.

Reproduce la convencion del script original (rd en Mpc con H0=100 fijo) y la
compara con la convencion correcta (parametro libre rd_h = rd * h, distancias
en Mpc*h), que es la que usan las tablas DM_over_rs / DH_over_rs / DV_over_rs.
No escribe archivos.
"""
import numpy as np
from pathlib import Path
from scipy.integrate import quad
from scipy.optimize import minimize, differential_evolution

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw" / "desi_dr2"
C_KMS = 299792.458


def cargar():
    d = np.loadtxt(RAW / "desi_gaussian_bao_ALL_GCcomb_mean.txt", comments="#", dtype=str)
    z = d[:, 0].astype(float)
    val = d[:, 1].astype(float)
    qty = d[:, 2]
    cov = np.loadtxt(RAW / "desi_gaussian_bao_ALL_GCcomb_cov.txt", comments="#")
    return z, val, qty, np.linalg.inv(cov)


def E(z, Om, Otau=0.0):
    OL = 1.0 - Om - Otau
    return np.sqrt(Om * (1 + z) ** 3 + Otau * (1 + z) ** 6 + OL)


def pred(z, qty, params):
    Om = params[0]
    Otau = params[1] if len(params) > 1 else 0.0
    DM = np.array([C_KMS / 100.0 * quad(lambda zp: 1.0 / E(zp, Om, Otau), 0, zi)[0] for zi in z])
    DH = C_KMS / 100.0 / E(z, Om, Otau)
    DV = (z * DM**2 * DH) ** (1 / 3)
    out = np.zeros_like(z)
    for i, q in enumerate(qty):
        out[i] = DM[i] if "DM" in q else (DH[i] if "DH" in q else DV[i])
    return out


def chi2(p, z, val, qty, cov_inv):
    rd = p[-1]
    return (val - pred(z, qty, p[:-1]) / rd) @ cov_inv @ (val - pred(z, qty, p[:-1]) / rd)


def main():
    z, val, qty, cov_inv = cargar()
    print("datos:", len(z), "puntos; primer valor/rd:", val[0], qty[0])

    for tag, bounds in [
        ("ORIGINAL: rd en Mpc, H0=100 fijo", [(0.05, 0.6), (130, 165)]),
        ("CORREGIDO: rd_h = rd*h en Mpc*h", [(0.05, 0.6), (90, 115)]),
    ]:
        print("\n===", tag, "===")
        r1 = differential_evolution(
            lambda p: chi2(p, z, val, qty, cov_inv), bounds, seed=42, maxiter=1000, tol=1e-10, polish=True
        )
        print("LCDM  Om=%.4f rd=%.2f  chi2=%.2f" % (r1.x[0], r1.x[1], r1.fun))
        r2 = differential_evolution(
            lambda p: chi2(p, z, val, qty, cov_inv),
            [bounds[0], (0.0, 0.3), bounds[1]],
            seed=42,
            maxiter=1000,
            tol=1e-10,
            polish=True,
        )
        print("THU   Om=%.4f Otau=%.4f rd=%.2f  chi2=%.2f" % (r2.x[0], r2.x[1], r2.x[2], r2.fun))
        print(
            "dchi2=%.2f  AIC_LCDM=%.2f  AIC_THU=%.2f  dAIC=%.2f"
            % (r1.fun - r2.fun, r1.fun + 4, r2.fun + 6, (r2.fun + 6) - (r1.fun + 4))
        )

    # chi2 de LCDM en parametros de Planck (Om=0.315, rd_h=99.1) como sanity check
    p = np.array([0.315, 99.1])
    print("\nsanity LCDM(Om=0.315, rd_h=99.1): chi2=%.2f" % chi2(p, z, val, qty, cov_inv))
    print("sanity LCDM(Om=0.315, rd=147.1 Mpc con H0=100): chi2=%.2f" % chi2(np.array([0.315, 147.1]), z, val, qty, cov_inv))


if __name__ == "__main__":
    main()
