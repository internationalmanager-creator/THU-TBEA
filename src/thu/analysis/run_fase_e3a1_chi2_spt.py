# -*- coding: utf-8 -*-
"""
FASE E.3-A1 v2 — chi^2 SPT-3G D1 (TT/TE/EE). Ventanas transpuestas.
"""
import sys, json, time
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
SPT = (LAB / "data" / "extracted" / "zen_runtime" /
       "SPT_3G_D1_T_E_likelihood_runtime_data_for_SPTLikel" /
       "SPT3G_D1_TnE_v0_20260917")
CL_FILE = LAB / "data" / "intermediate" / "cl_lcdm_planck18.npz"

TOTAL = 7
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "=" * filled + "." * (40 - filled), pct

def paso(i, titulo, desc):
    bar, pct = barra(i)
    print()
    print("=" * 72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {titulo}")
    print(f"  -> {desc}")
    print("=" * 72)
    sys.stdout.flush()

# -- 1 --
paso(1, "Cargar C_l LCDM", "cl_lcdm_planck18.npz")
cl = np.load(CL_FILE)
ell_camb = cl["ell"]
cl_tt = cl["cl_tt"]; cl_ee = cl["cl_ee"]
cl_bb = cl["cl_bb"]; cl_te = cl["cl_te"]
print(f"  ell: {ell_camb.min()}..{ell_camb.max()}")
print(f"  D_l^TT(1000) = {cl_tt[1000]:.2f} muK^2")

# -- 2 --
paso(2, "Cargar metadata y data_vector", "SPT-3G D1")
meta = json.loads((SPT / "metadata.json").read_text())
dv = np.load(SPT / "data_vector.npy")
cov = np.load(SPT / "covariance.npy")
ells_obs = np.load(SPT / "ells.npy")
spectrum_order = meta["spectrum_order"]
bins_per = meta["bins_per_spectrum"]
print(f"  N espectros: {len(spectrum_order)}, bins total: {sum(bins_per)}")
print(f"  dv: {dv.shape}, cov: {cov.shape}, ells: {ells_obs.shape}")

# -- 3 --
paso(3, "Cargar ventanas y verificar orientacion",
     "Verificar shape antes de proyectar")

ventanas = []
for i in range(1, 22):
    w = np.load(SPT / "windows" / f"{i:02d}.npy")
    ventanas.append(w)

print(f"  Shapes: {[w.shape for w in ventanas[:3]]} ...")
print(f"  Interpretacion: (n_ell, n_bin)")

# Verificar coherencia: suma de shape[1] debe ser 1392
total_bins = sum(w.shape[1] for w in ventanas)
print(f"  Suma shape[1] = {total_bins} (debe ser 1392)")
assert total_bins == 1392, f"MISMATCH: {total_bins} != 1392"
print(f"  OK: bins coherentes")

# Verificar que shape[0] = len(ells_obs) para todas
n_ell = ells_obs.shape[0]
for i, w in enumerate(ventanas):
    assert w.shape[0] == n_ell, f"Ventana {i+1}: {w.shape[0]} != {n_ell}"
print(f"  OK: todas las ventanas cubren {n_ell} multipolos")

# -- 4 --
paso(4, "Proyectar C_l CAMB a bins observados",
     "D_bin = W.T @ D_l (transpuesta!)")

modelo_bins = np.zeros(sum(bins_per))
idx = 0
espectro_teorico = {
    "TT": cl_tt, "TE": cl_te, "EE": cl_ee,
    "ET": cl_te, "BB": cl_bb
}

for i, spec in enumerate(spectrum_order):
    tipo = spec.split()[0]
    W = ventanas[i]           # (n_ell, n_bin)
    n_bins = bins_per[i]
    teorico = espectro_teorico[tipo]
    d_l_teorico = np.interp(ells_obs, ell_camb, teorico)  # (n_ell,)
    modelo_bins[idx:idx+n_bins] = W.T @ d_l_teorico       # (n_bin,)
    idx += n_bins

print(f"  Modelo: {modelo_bins.shape}")
print(f"  Primeros 5: {modelo_bins[:5]}")
print(f"  Data  5:    {dv[:5]}")

# -- 5 --
paso(5, "Residuos y chi^2", "chi^2 = r^T C^-1 r")

residuos = dv - modelo_bins
print(f"  Residuos: media={residuos.mean():.4f}, std={residuos.std():.4f}")
print(f"  rango: [{residuos.min():.2f}, {residuos.max():.2f}]")

# Invertir covarianza
try:
    cov_inv = np.linalg.inv(cov)
    print(f"  cov invertida OK")
except np.linalg.LinAlgError:
    cov_inv = np.linalg.pinv(cov)
    print(f"  ADVERTENCIA: cov singular, usando pinv")

chi2 = float(residuos @ cov_inv @ residuos)
dof = len(dv)
chi2_dof = chi2 / dof
print(f"  chi^2 = {chi2:.2f}")
print(f"  dof   = {dof}")
print(f"  chi^2/dof = {chi2_dof:.4f}")

# -- 6 --
paso(6, "Residuos por espectro", "Estructura por tipo")

idx = 0
diag = np.diag(cov)
for i, spec in enumerate(spectrum_order):
    n = bins_per[i]
    r = residuos[idx:idx+n]
    s = np.sqrt(diag[idx:idx+n])
    rn = r / s
    print(f"  {spec:12s}: n={n:3d}  |r|_med={np.abs(r).mean():7.2f}  "
          f"r/sigma_med={np.abs(rn).mean():5.2f}  max|r/sigma|={np.abs(rn).max():5.2f}")
    idx += n

# -- 7 --
paso(7, "Conclusion", "chi^2/dof cercano a 1 => pipeline sano")

print(f"  chi^2/dof = {chi2_dof:.4f}")
if 0.9 <= chi2_dof <= 1.1:
    print(f"  VEREDICTO: PIPELINE SANO")
    print(f"  -> Listo para birefringencia")
elif 0.7 <= chi2_dof <= 1.3:
    print(f"  VEREDICTO: ACEPTABLE (revisar residuos)")
else:
    print(f"  VEREDICTO: REVISAR")
    print(f"  -> chi^2/dof fuera de [0.7, 1.3]")

t_total = time.time() - t0
print()
print("=" * 72)
print(f"  FIN E.3-A1 v2   (duracion: {t_total:.2f}s)")
print("=" * 72)
