#!/usr/bin/env python3
"""Residuos por punto del ajuste BAO en el best-fit, para ver si un dato domina."""
import numpy as np
from pathlib import Path
from scipy.integrate import quad

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw" / "desi_dr2"
C_KMS = 299792.458


def E(z, Om):
    return np.sqrt(Om * (1 + z) ** 3 + (1 - Om))


def cargar(name="desi_gaussian_bao_ALL_GCcomb"):
    d = np.loadtxt(RAW / f"{name}_mean.txt", comments="#", dtype=str)
    cov = np.loadtxt(RAW / f"{name}_cov.txt", comments="#")
    return d[:, 0].astype(float), d[:, 1].astype(float), d[:, 2], cov, np.linalg.inv(cov)


def pred(z, qty, Om, rd_h):
    DM = np.array([C_KMS / 100.0 * quad(lambda zp: 1.0 / E(zp, Om), 0, zi)[0] for zi in z])
    DH = C_KMS / 100.0 / E(z, Om)
    DV = (z * DM**2 * DH) ** (1 / 3)
    return np.array([DM[i] if "DM" in q else (DH[i] if "DH" in q else DV[i]) for i, q in enumerate(qty)]) / rd_h


def chi2(p, z, val, qty, cov_inv):
    r = val - pred(z, qty, p[0], p[1])
    return float(r @ cov_inv @ r)


def main():
    z, val, qty, cov, cov_inv = cargar()
    print("diag(cov) min/max:", cov.diagonal().min(), cov.diagonal().max())
    print("cov no diagonal? max abs offdiag:", np.abs(cov - np.diag(cov.diagonal())).max())
    for p in [(0.2975, 101.54), (0.2975, 99.4), (0.315, 99.1)]:
        print("chi2(Om=%.4f, rd_h=%.2f) = %.2f" % (p[0], p[1], chi2(p, z, val, qty, cov_inv)))
    p = (0.2975, 101.54)
    r = val - pred(z, qty, p[0], p[1])
    sig = np.sqrt(cov.diagonal())
    print("\npor punto:")
    for i in range(len(z)):
        print("  z=%.3f %-12s dato=%.4f modelo=%.4f  resid=%.4f  resid/sigma=%.2f" % (z[i], qty[i], val[i], val[i] - r[i], r[i], r[i] / sig[i]))
    print("\nchi2 total:", float(r @ cov_inv @ r), "| suma (resid/sigma)^2:", float(np.sum((r / sig) ** 2)))


if __name__ == "__main__":
    main()
