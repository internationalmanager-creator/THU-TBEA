# -*- coding: utf-8 -*-
"""
FASE E.3-C — Ajuste de beta con EB/TB de ACT DR6.
Modelo: EB = (1/2) sin(4b) [EE - BB], TB = sin(2b) TE
"""
import sys, json, time
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
ACT = LAB / "data" / "raw" / "act_dr6" / "act_dr6.02_spectra_and_cov_xtra" / "xtra"
CL_FILE = LAB / "data" / "intermediate" / "cl_lcdm_planck18.npz"

TOTAL = 8
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "=" * filled + "." * (40 - filled), pct

def paso(i, t, d):
    bar, pct = barra(i)
    print()
    print("=" * 72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {t}")
    print(f"  -> {d}")
    print("=" * 72)
    sys.stdout.flush()

# --- 1: Inspeccionar formato de .dat ---
paso(1, "Inspeccionar formato de EB.dat y TB.dat",
     "NO asumir formato, leer primeras lineas")

for fname in ["opt_weight_fg_subtracted_EB.dat", "opt_weight_fg_subtracted_TB.dat"]:
    f = ACT / fname
    print(f"\n  --- {fname} ---")
    lines = f.read_text(encoding="utf-8").splitlines()
    print(f"  Total lineas: {len(lines)}")
    print(f"  Primeras 5 lineas:")
    for l in lines[:5]:
        print(f"    {l}")
    print(f"  Ultimas 2 lineas:")
    for l in lines[-2:]:
        print(f"    {l}")

# --- 2: Inspeccionar .npy ---
paso(2, "Inspeccionar covarianzas .npy", "Shapes y valores")

cov_eb = np.load(ACT / "cov_opt_weight_EB.npy")
cov_tb = np.load(ACT / "cov_opt_weight_TB.npy")
print(f"  cov_EB shape: {cov_eb.shape}")
print(f"  cov_TB shape: {cov_tb.shape}")
print(f"  cov_EB diagonal: min={np.diag(cov_eb).min():.3e} max={np.diag(cov_eb).max():.3e}")
print(f"  cov_TB diagonal: min={np.diag(cov_tb).min():.3e} max={np.diag(cov_tb).max():.3e}")

# --- 3: Cargar datos ---
paso(3, "Cargar EB y TB observados", "Parsear .dat")

def load_dat(path):
    """Intenta parsear .dat. Asume: ell, D_l, sigma o ell, D_l."""
    data = np.loadtxt(path, comments="#")
    print(f"    {path.name}: shape={data.shape}")
    return data

eb_data = load_dat(ACT / "opt_weight_fg_subtracted_EB.dat")
tb_data = load_dat(ACT / "opt_weight_fg_subtracted_TB.dat")

# Inferir columnas
def extract_ells_and_dl(data, name):
    if data.ndim != 2:
        raise ValueError(f"{name}: no es 2D")
    ncols = data.shape[1]
    print(f"    {name}: ncols={ncols}, nrows={data.shape[0]}")
    if ncols >= 3:
        ell = data[:, 0]
        dl = data[:, 1]
        sigma = data[:, 2]
    elif ncols == 2:
        ell = data[:, 0]
        dl = data[:, 1]
        sigma = None
    else:
        raise ValueError(f"{name}: ncols={ncols} no soportado")
    return ell, dl, sigma

ell_eb, dl_eb, sig_eb = extract_ells_and_dl(eb_data, "EB")
ell_tb, dl_tb, sig_tb = extract_ells_and_dl(tb_data, "TB")

print(f"  ell_EB: {len(ell_eb)} bins, rango {ell_eb.min():.1f}..{ell_eb.max():.1f}")
print(f"  ell_TB: {len(ell_tb)} bins, rango {ell_tb.min():.1f}..{ell_tb.max():.1f}")

# --- 4: Cargar CAMB ---
paso(4, "Cargar C_l LCDM (CAMB)", "cl_lcdm_planck18.npz")

cl = np.load(CL_FILE)
ell_camb = cl["ell"]
cl_ee = cl["cl_ee"]; cl_bb = cl["cl_bb"]; cl_te = cl["cl_te"]
print(f"  CAMB: ell {ell_camb.min()}..{ell_camb.max()}")

# --- 5: Modelo EB(beta) y TB(beta) ---
paso(5, "Definir modelo y grid de beta",
     "EB = (1/2) sin(4b)(EE-BB), TB = sin(2b) TE")

# Interpolar teorico a los ells observados
ee_interp = np.interp(ell_eb, ell_camb, cl_ee)
bb_interp = np.interp(ell_eb, ell_camb, cl_bb)
te_interp = np.interp(ell_tb, ell_camb, cl_te)

# Diferencia EE - BB (para EB)
ee_minus_bb = ee_interp - bb_interp

# Para beta en grados -> rad
def model_eb(beta_deg):
    b = np.radians(beta_deg)
    return 0.5 * np.sin(4*b) * ee_minus_bb

def model_tb(beta_deg):
    b = np.radians(beta_deg)
    return np.sin(2*b) * te_interp

# Grid beta
betas = np.linspace(-1.0, 1.0, 2001)  # paso 0.001 deg
print(f"  Grid: {len(betas)} puntos, [{betas.min()}, {betas.max()}] deg")

# --- 6: chi^2(beta) ---
paso(6, "Calcular chi^2(beta)", "Grid search")

# Invertir covarianzas
try:
    inv_cov_eb = np.linalg.inv(cov_eb)
    inv_cov_tb = np.linalg.inv(cov_tb)
except np.linalg.LinAlgError:
    inv_cov_eb = np.linalg.pinv(cov_eb)
    inv_cov_tb = np.linalg.pinv(cov_tb)
    print("  ADVERTENCIA: cov singular, usando pinv")

# Asegurar shapes coherentes
n_eb = len(dl_eb)
n_tb = len(dl_tb)
print(f"  n_EB={n_eb}, n_TB={n_tb}")

if cov_eb.shape[0] != n_eb:
    print(f"  ADVERTENCIA: cov_EB shape {cov_eb.shape} != n_eb {n_eb}")
if cov_tb.shape[0] != n_tb:
    print(f"  ADVERTENCIA: cov_TB shape {cov_tb.shape} != n_tb {n_tb}")

# Ignorar autoespectro EE/BB de EB y solo usar EB y TB
chi2_arr = np.zeros(len(betas))
for i, b in enumerate(betas):
    r_eb = dl_eb - model_eb(b)
    r_tb = dl_tb - model_tb(b)
    chi2_eb = float(r_eb @ inv_cov_eb @ r_eb)
    chi2_tb = float(r_tb @ inv_cov_tb @ r_tb)
    chi2_arr[i] = chi2_eb + chi2_tb

# --- 7: Encontrar minimo y sigma ---
paso(7, "Encontrar beta_best y sigma", "delta chi^2 = 1")

i_best = int(np.argmin(chi2_arr))
beta_best = betas[i_best]
chi2_min = chi2_arr[i_best]

# sigma via delta chi^2 = 1
below = betas[chi2_arr < chi2_min + 1]
if len(below) > 1:
    sigma_lo = beta_best - below.min()
    sigma_hi = below.max() - beta_best
    sigma_avg = (sigma_lo + sigma_hi) / 2
else:
    sigma_avg = 0.0
    print("  ADVERTENCIA: no se encontro delta chi^2 = 1 (grid muy chico?)")

print(f"  beta_best    = {beta_best:.4f} deg")
print(f"  chi2_min     = {chi2_min:.4f}")
print(f"  dof          = {n_eb + n_tb}")
print(f"  chi2/dof     = {chi2_min / (n_eb+n_tb):.4f}")
print(f"  sigma (-)    = {sigma_lo:.4f} deg")
print(f"  sigma (+)    = {sigma_hi:.4f} deg")
print(f"  sigma (avg)  = {sigma_avg:.4f} deg")

# --- 8: Comparacion con THU-TBEA ---
paso(8, "Comparacion con beta_THU = 0.3803 deg", "Tension en sigma")

beta_thu = 0.3803
sigma_thu = 0.040
sigma_comb = np.sqrt(sigma_avg**2 + sigma_thu**2)
tension = abs(beta_best - beta_thu) / sigma_comb if sigma_comb > 0 else 0

print(f"  beta_ACT     = {beta_best:.4f} +/- {sigma_avg:.4f} deg (este analisis)")
print(f"  beta_THU     = {beta_thu:.4f} +/- {sigma_thu:.4f} deg (THU-TBEA 5.0)")
print(f"  beta_ACT_pub = 0.215  +/- 0.074  deg (Diego-Palazuelos 2025)")
print()
print(f"  Delta (THU - ACT) = {beta_thu - beta_best:.4f} deg")
print(f"  sigma_combinada   = {sigma_comb:.4f} deg")
print(f"  Tension           = {tension:.3f} sigma")

if tension < 1:
    print(f"  VEREDICTO: COMPATIBLE a < 1 sigma")
elif tension < 2:
    print(f"  VEREDICTO: COMPATIBLE a < 2 sigma")
elif tension < 3:
    print(f"  VEREDICTO: TENSION MARGINAL (2-3 sigma)")
else:
    print(f"  VEREDICTO: TENSION SIGNIFICATIVA (> 3 sigma)")

# Guardar
out = LAB / "data" / "inventory" / "resultado_beta_act_dr6.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({
    "beta_best_deg": float(beta_best),
    "sigma_avg_deg": float(sigma_avg),
    "sigma_lo_deg": float(sigma_lo),
    "sigma_hi_deg": float(sigma_hi),
    "chi2_min": float(chi2_min),
    "dof": int(n_eb + n_tb),
    "chi2_dof": float(chi2_min / (n_eb+n_tb)),
    "n_bins_eb": int(n_eb),
    "n_bins_tb": int(n_tb),
    "beta_thu_deg": beta_thu,
    "sigma_thu_deg": sigma_thu,
    "tension_sigma": float(tension),
    "fuente_datos": "ACT DR6.02 spectra_and_cov_xtra",
    "paper_beta": "Diego-Palazuelos & Komatsu, arXiv:2509.13654",
}, indent=2), encoding="utf-8")
print(f"\n  Resultado guardado: {out}")

t_total = time.time() - t0
print()
print("=" * 72)
print(f"  FIN E.3-C  (duracion: {t_total:.2f}s)")
print("=" * 72)
