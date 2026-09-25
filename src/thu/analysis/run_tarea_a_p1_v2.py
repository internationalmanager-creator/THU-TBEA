# -*- coding: utf-8 -*-
"""Tarea A v2 — P1 con ajuste lineal (rapido + verificado)."""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
DESI_DIR = LAB / "data" / "raw" / "desi_dr2"
OUT = LAB / "data" / "inventory"

t0 = time.time()

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# ============================================================
# VERIFICACION 1: Covarianza
# ============================================================
hdr("VERIFICACION 1: Covarianza DESI")

desi_file = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
desi_cov_file = DESI_DIR / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

rows = []
with open(desi_file) as fh:
    for line in fh:
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split()
        rows.append((float(parts[0]), float(parts[1]), parts[2]))

z_bao = np.array([r[0] for r in rows])
val_bao = np.array([r[1] for r in rows])
q_bao = [r[2] for r in rows]
cov_bao = np.loadtxt(desi_cov_file)

print(f"  N puntos: {len(z_bao)}")
print(f"  cov shape: {cov_bao.shape}")
print(f"  max|cov - cov.T|: {np.max(np.abs(cov_bao - cov_bao.T)):.4e}")

eigvals = np.linalg.eigvalsh(cov_bao)
print(f"  autovalores: min={eigvals.min():.4e}, max={eigvals.max():.4e}")
assert eigvals.min() > 0, "cov NO positiva definida"
print(f"  OK: cov positiva definida")

cov_bao_inv = np.linalg.inv(cov_bao)

# ============================================================
# VERIFICACION 2: Modelo
# ============================================================
hdr("VERIFICACION 2: Modelo cosmologico")

c_km_s = 299792.458
r_d_fid = 147.46
H0_fid = 67.36
Om_r = 9.15e-5

def E_z(z, Om, w0, wa):
    f_de = (1.0 + z)**(3*(1 + w0 + wa)) * np.exp(-3*wa*z/(1.0 + z))
    Ode = 1.0 - Om - Om_r
    return np.sqrt(Om*(1+z)**3 + Om_r*(1+z)**4 + Ode*f_de)

def D_M_z(z, Om, w0, wa):
    val, _ = quad(lambda zp: c_km_s / (H0_fid * E_z(zp, Om, w0, wa)), 0, z, limit=50)
    return val

def D_H_z(z, Om, w0, wa):
    return c_km_s / (H0_fid * E_z(z, Om, w0, wa))

def D_V_z(z, Om, w0, wa):
    dm = D_M_z(z, Om, w0, wa); dh = D_H_z(z, Om, w0, wa)
    return (z * dm**2 * dh)**(1.0/3.0)

def pred_model(params, w0_wa=True):
    if w0_wa:
        Om, w0, wa = params
    else:
        Om = params[0]; w0 = -1.0; wa = 0.0
    out = np.zeros(len(z_bao))
    for i, (z, q) in enumerate(zip(z_bao, q_bao)):
        if q == "DV_over_rs": out[i] = D_V_z(z, Om, w0, wa) / r_d_fid
        elif q == "DM_over_rs": out[i] = D_M_z(z, Om, w0, wa) / r_d_fid
        elif q == "DH_over_rs": out[i] = D_H_z(z, Om, w0, wa) / r_d_fid
    return out

def chi2(params):
    r = val_bao - pred_model(params, w0_wa=True)
    return float(r @ cov_bao_inv @ r)

# Test conocido
chi2_test = chi2([0.31, -1.0, 0.0])
print(f"  chi2(Om=0.31, w0=-1, wa=0) = {chi2_test:.2f} (esperado ~32)")

# ============================================================
# Optimizar baseline
# ============================================================
hdr("Optimizando baseline w0-wa")

print(f"  Minimizando...")
t_opt = time.time()
best = minimize(chi2, x0=[0.31, -1.0, 0.0], method="Nelder-Mead",
                options={"xatol": 1e-5, "fatol": 1e-4, "maxiter": 5000})
Om_b, w0_b, wa_b = best.x
chi2_b = best.fun
print(f"  Om={Om_b:.4f}, w0={w0_b:.4f}, wa={wa_b:.4f}")
print(f"  chi2_baseline = {chi2_b:.4f}")
print(f"  Tiempo: {time.time()-t_opt:.1f}s")

# Residuos
r_b = val_bao - pred_model([Om_b, w0_b, wa_b], w0_wa=True)

# ============================================================
# VERIFICACION 3: Ajuste lineal
# ============================================================
hdr("VERIFICACION 3: Ajuste lineal oscilatorio")

def chi2_osc_linear(omega, r, C_inv, z):
    """Ajuste r = a*sin(omega*z) + b*cos(omega*z) via GLS."""
    M = np.column_stack([np.sin(omega * z), np.cos(omega * z)])
    Cinv_r = C_inv @ r
    Cinv_M = C_inv @ M
    Mt_Cinv_M = M.T @ Cinv_M
    try:
        Mt_Cinv_M_inv = np.linalg.inv(Mt_Cinv_M)
    except np.linalg.LinAlgError:
        return np.inf, 0.0, 0.0
    Mt_Cinv_r = M.T @ Cinv_r
    theta = Mt_Cinv_M_inv @ Mt_Cinv_r
    chi2_red = float(Cinv_r @ r - Mt_Cinv_r @ theta)
    return chi2_red, float(theta[0]), float(theta[1])

# Test omega -> 0
chi2_0, _, _ = chi2_osc_linear(0.001, r_b, cov_bao_inv, z_bao)
print(f"  Test omega~0: chi2 = {chi2_0:.4f}")
print(f"  chi2_baseline = {chi2_b:.4f}")
print(f"  |dif| = {abs(chi2_0 - chi2_b):.4f}")
if abs(chi2_0 - chi2_b) < 0.5:
    print(f"  OK: ajuste lineal correcto")
else:
    print(f"  *** ALERTA: dif > 0.5 ***")

# Test inyeccion
print(f"\n  Test inyeccion A=0.05, omega=5.0")
r_inj = r_b + 0.05 * np.sin(5.0 * z_bao)
_, a_rec, b_rec = chi2_osc_linear(5.0, r_inj, cov_bao_inv, z_bao)
amp_rec = np.sqrt(a_rec**2 + b_rec**2)
print(f"  Recuperado: amp = {amp_rec:.4f} (inyectado: 0.05)")
if abs(amp_rec - 0.05) < 0.02:
    print(f"  OK")
else:
    print(f"  ADVERTENCIA")

# ============================================================
# SCAN
# ============================================================
hdr("SCAN omega en datos reales")

omega_grid = np.linspace(0.5, 30.0, 300)
chi2_scan = np.zeros(len(omega_grid))
for i, om in enumerate(omega_grid):
    chi2_scan[i], _, _ = chi2_osc_linear(om, r_b, cov_bao_inv, z_bao)

i_best = np.argmin(chi2_scan)
omega_best = omega_grid[i_best]
chi2_best = chi2_scan[i_best]
delta_chi2_obs = chi2_b - chi2_best

print(f"  omega_best = {omega_best:.3f}")
print(f"  chi2_baseline = {chi2_b:.4f}")
print(f"  chi2_best_osc = {chi2_best:.4f}")
print(f"  Delta chi2 = {delta_chi2_obs:.4f}")

# ============================================================
# TEST NULO MC
# ============================================================
hdr("Test nulo Monte Carlo")

N_SIM = 500
print(f"  N_sim = {N_SIM}")

# Cholesky para ruido correlacionado
L_chol = np.linalg.cholesky(cov_bao)

np.random.seed(20260921)
delta_chi2_null = np.zeros(N_SIM)

t_mc = time.time()
for sim in range(N_SIM):
    noise = L_chol @ np.random.randn(len(z_bao))
    val_sim = pred_model([Om_b, w0_b, wa_b], w0_wa=True) + noise
    
    def chi2_sim(p):
        r_s = val_sim - pred_model(p, w0_wa=True)
        return float(r_s @ cov_bao_inv @ r_s)
    
    best_sim = minimize(chi2_sim, x0=[Om_b, w0_b, wa_b], method="Nelder-Mead",
                        options={"xatol": 1e-4, "fatol": 1e-3, "maxiter": 1000})
    chi2_base_sim = best_sim.fun
    r_sim = val_sim - pred_model(best_sim.x, w0_wa=True)
    
    chi2_scan_sim = np.zeros(len(omega_grid))
    for i, om in enumerate(omega_grid):
        chi2_scan_sim[i], _, _ = chi2_osc_linear(om, r_sim, cov_bao_inv, z_bao)
    
    delta_chi2_null[sim] = chi2_base_sim - np.min(chi2_scan_sim)

print(f"  MC completado en {time.time()-t_mc:.1f}s")

# p-value
p_value = float(np.mean(delta_chi2_null >= delta_chi2_obs))
n_mayores = int(np.sum(delta_chi2_null >= delta_chi2_obs))

print(f"\n  Delta chi2 obs: {delta_chi2_obs:.4f}")
print(f"  Nulo: media={delta_chi2_null.mean():.4f}, std={delta_chi2_null.std():.4f}")
print(f"  Nulo p95: {np.percentile(delta_chi2_null, 95):.4f}")
print(f"  Nulo p99: {np.percentile(delta_chi2_null, 99):.4f}")
print(f"  Nulos >= obs: {n_mayores}/{N_SIM}")
print(f"  p-value = {p_value:.4f}")

if p_value < 0.01:
    veredicto = "DETECCION_FUERTE"
elif p_value < 0.05:
    veredicto = "DETECCION_MODERADA"
elif p_value < 0.32:
    veredicto = "SIN_DETECCION"
else:
    veredicto = "CONSISTENTE_CON_NULO"

print(f"\n  VEREDICTO: {veredicto}")

# ============================================================
# Guardar
# ============================================================
hdr("Guardar resultado")

resultado = {
    "tarea": "A",
    "prediccion": "P1",
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "advertencia": "PDF no especifica omega ni A. Test exploratorio.",
    "datos": {
        "N_puntos": int(len(z_bao)),
        "z_range": [float(z_bao.min()), float(z_bao.max())],
    },
    "baseline": {
        "modelo": "w0-wa CPL",
        "Om": float(Om_b),
        "w0": float(w0_b),
        "wa": float(wa_b),
        "chi2": float(chi2_b),
    },
    "oscilacion": {
        "omega_best": float(omega_best),
        "chi2_best": float(chi2_best),
        "delta_chi2": float(delta_chi2_obs),
    },
    "test_nulo": {
        "N_sim": N_SIM,
        "delta_chi2_mean": float(delta_chi2_null.mean()),
        "delta_chi2_std": float(delta_chi2_null.std()),
        "delta_chi2_p95": float(np.percentile(delta_chi2_null, 95)),
        "delta_chi2_p99": float(np.percentile(delta_chi2_null, 99)),
        "p_value": float(p_value),
    },
    "veredicto": veredicto,
}

out = OUT / "fase_p1_oscilaciones_hz.json"
out.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"  Guardado: {out}")

# ============================================================
# Resumen
# ============================================================
hdr("RESUMEN")

print(f"  Tarea A: P1 — oscilaciones en H(z)")
print(f"  Datos: DESI DR2 ({len(z_bao)} puntos)")
print(f"  Baseline: w0-wa, chi2 = {chi2_b:.4f}")
print(f"  omega_best = {omega_best:.3f}, Delta chi2 = {delta_chi2_obs:.4f}")
print(f"  p-value = {p_value:.4f}")
print(f"  VEREDICTO: {veredicto}")
print(f"  Tiempo total: {time.time()-t0:.1f}s")
