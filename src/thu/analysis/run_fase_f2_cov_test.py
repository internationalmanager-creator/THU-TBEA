# -*- coding: utf-8 -*-
"""Test: que covarianza da chi2/dof ~ 1 con LCDM."""
import numpy as np
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
PAN = LAB / "data" / "raw" / "pantheon_plus"

# Cargar datos con scale/add
with open(PAN / "Pantheon+SH0ES.dat") as fh:
    header = fh.readline().strip().split()
idx = {h: i for i, h in enumerate(header)}
scale_idx = idx["biasCor_m_b_COVSCALE"]
add_idx = idx["biasCor_m_b_COVADD"]

z, m, scale, add = [], [], [], []
with open(PAN / "Pantheon+SH0ES.dat") as fh:
    fh.readline()
    for line in fh:
        p = line.split()
        if len(p) < len(header): continue
        z.append(float(p[idx["zCMB"]]))
        m.append(float(p[idx["m_b_corr"]]))
        scale.append(float(p[scale_idx]))
        add.append(float(p[add_idx]))

z = np.array(z); m = np.array(m)
scale = np.array(scale); add = np.array(add)
print(f"N total: {len(z)}")

# Filtro oficial
used = []
with open(PAN / "Pantheon+SH0ES.dat") as fh:
    fh.readline()
    for line in fh:
        p = line.split()
        if len(p) < len(header): continue
        used.append(int(p[idx["USED_IN_SH0ES_HF"]]))
used = np.array(used)

mask = (z > 0.01) & (used == 0)
idx_keep = np.where(mask)[0]
z = z[mask]; m = m[mask]
scale = scale[mask]; add = add[mask]
print(f"Tras filtro z>0.01 & used=0: {len(z)}")

# Cargar cov
with open(PAN / "Pantheon+SH0ES_STAT+SYS.cov") as fh:
    N = int(fh.readline())
    vals = np.fromfile(fh, sep="\n", dtype=np.float64)
cov_full = vals.reshape(N, N)

# Submatriz
cov = cov_full[np.ix_(idx_keep, idx_keep)]
print(f"cov sub shape: {cov.shape}")

# Comparar 3 versiones
versions = {
    "A_cov_cruda": cov.copy(),
    "B_cov_con_scale": cov * np.outer(scale, scale),
    "C_cov_scale_add": cov * np.outer(scale, scale) + np.diag(add),
    "D_igual_a_err_DIAG_diag": None,  # placeholder
}

# Para opción D: diag(err_DIAG^2)
with open(PAN / "Pantheon+SH0ES.dat") as fh:
    fh.readline()
    errs = []
    for line in fh:
        p = line.split()
        if len(p) < len(header): continue
        errs.append(float(p[idx["m_b_corr_err_DIAG"]]))
errs = np.array(errs)[mask]
versions["D_igual_a_err_DIAG_diag"] = np.diag(errs**2)

# Modelo LCDM
from scipy.integrate import quad
c = 299792.458
r_d = 147.46
H0 = 67.36
Om_r = 9.15e-5

def E(z, Om):
    Ode = 1 - Om - Om_r
    return np.sqrt(Om*(1+z)**3 + Om_r*(1+z)**4 + Ode)

def DM(z, Om):
    return quad(lambda zp: c/(H0*E(zp, Om)), 0, z)[0]

def mu_theory(z, Om):
    out = np.zeros(len(z))
    for i, zz in enumerate(z):
        out[i] = 5*np.log10((1+zz)*DM(zz, Om)*1e5)
    return out

# Chi2 para cada version
print(f"\n{'Version':30s}  {'chi2':>10s}  {'dof':>6s}  {'chi2/dof':>10s}")
for name, C in versions.items():
    try:
        inv = np.linalg.inv(C)
    except np.linalg.LinAlgError:
        inv = np.linalg.pinv(C)
    mu = mu_theory(z, 0.31)
    r = m - mu
    Cinv_r = inv @ r
    Cinv_1 = inv @ np.ones(len(r))
    M = np.sum(Cinv_r) / np.sum(Cinv_1)
    r_M = r - M
    chi2 = float(r_M @ inv @ r_M)
    dof = len(r) - 1  # M_B marginalizado
    print(f"{name:30s}  {chi2:10.2f}  {dof:6d}  {chi2/dof:10.4f}")

print()
print("El correcto debe dar chi2/dof ~ 1.0")
