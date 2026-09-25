# -*- coding: utf-8 -*-
"""Tarea A — P1: Busqueda de oscilaciones en residuos H(z) de DESI DR2."""
import sys, json, time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
DESI_DIR = LAB / "data" / "raw" / "desi_dr2"
OUT = LAB / "data" / "inventory"

TOTAL = 8
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "=" * filled + "." * (40 - filled), pct

def paso(i, t, d=""):
    bar, pct = barra(i)
    print(); print("="*72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {t}")
    if d: print(f"  -> {d}")
    print("="*72); sys.stdout.flush()

# ============================================================
# 1: Cargar DESI DR2
# ============================================================
paso(1, "Cargar DESI DR2 BAO")

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

# Invertir
cov_bao_inv = np.linalg.inv(cov_bao)

print(f"  N mediciones: {len(z_bao)}")
print(f"  z range: {z_bao.min():.3f}..{z_bao.max():.3f}")
print(f"  Quantity types: {set(q_bao)}")

# ============================================================
# 2: Modelo cosmologico
# ============================================================
paso(2, "Modelo LCDM + w0-wa")

c_km_s = 299792.458
r_d_fid = 147.46
H0_fid = 67.36
Om_r = 9.15e-5

def E_z(z, Om, w0, wa):
    f_de = (1.0 + z)**(3*(1 + w0 + wa)) * np.exp(-3*wa*z/(1.0 + z))
    Ode = 1.0 - Om - Om_r
    return np.sqrt(Om*(1+z)**3 + Om_r*(1+z)**4 + Ode*f_de)

def D_M_z(z, Om, w0, wa):
    f = lambda zp: c_km_s / (H0_fid * E_z(zp, Om, w0, wa))
    val, _ = quad(f, 0, z, limit=50)
    return val

def D_H_z(z, Om, w0, wa):
    return c_km_s / (H0_fid * E_z(z, Om, w0, wa))

def D_V_z(z, Om, w0, wa):
    dm = D_M_z(z, Om, w0, wa); dh = D_H_z(z, Om, w0, wa)
    return (z * dm**2 * dh)**(1.0/3.0)

def pred_model(params, w0_wa=False):
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

def chi2(params, w0_wa=False):
    r = val_bao - pred_model(params, w0_wa)
    return float(r @ cov_bao_inv @ r)

# Ajuste LCDM
best_lcdm = minimize(lambda p: chi2(p, w0_wa=False),
                     x0=[0.31], method="Nelder-Mead")
chi2_lcdm = best_lcdm.fun
Om_lcdm = best_lcdm.x[0]
print(f"  LCDM: Om = {Om_lcdm:.4f}, chi2 = {chi2_lcdm:.2f}")

# Ajuste w0-wa
best_w0wa = minimize(lambda p: chi2(p, w0_wa=True),
                     x0=[0.31, -1.0, 0.0], method="Nelder-Mead")
chi2_w0wa = best_w0wa.fun
Om_w0wa, w0_w0wa, wa_w0wa = best_w0wa.x
print(f"  w0-wa: Om = {Om_w0wa:.4f}, w0 = {w0_w0wa:.4f}, wa = {wa_w0wa:.4f}")
print(f"  chi2(w0-wa) = {chi2_w0wa:.2f}")

# ============================================================
# 3: Residuos
# ============================================================
paso(3, "Residuos del mejor ajuste")

# Usamos w0-wa como baseline (mas flexible)
pred_w0wa = pred_model(best_w0wa.x, w0_wa=True)
residuos = val_bao - pred_w0wa

# Normalizados por sigma diagonal
sigma_diag = np.sqrt(np.diag(cov_bao))
residuos_norm = residuos / sigma_diag

print(f"  Residuos (raw):")
print(f"  {'z':>6s}  {'q':>12s}  {'data':>10s}  {'model':>10s}  {'resid':>10s}  {'r/sig':>8s}")
for z, q, d, m, r, rn in zip(z_bao, q_bao, val_bao, pred_w0wa, residuos, residuos_norm):
    print(f"  {z:6.3f}  {q:>12s}  {d:10.4f}  {m:10.4f}  {r:10.4f}  {rn:+8.3f}")

# Chi2 de residuos normalizados
print(f"\n  chi2 residuos (diag): {np.sum(residuos_norm**2):.2f}")
print(f"  N puntos: {len(z_bao)}")

# ============================================================
# 4: Scan de oscilaciones
# ============================================================
paso(4, "Scan de oscilaciones: residuo ~ A*sin(omega*z + phi)")

# Modelo: val_bao = pred_w0wa + A * sin(omega*z + phi)
# Para cada omega, ajustamos A y phi (o equivalentemente a*sin + b*cos)

def chi2_with_osc(params, omega):
    Om, w0, wa, a_sin, a_cos = params
    pred_cosmo = pred_model([Om, w0, wa], w0_wa=True)
    z_norm = (z_bao - z_bao.mean()) / z_bao.std()
    osc = a_sin * np.sin(omega * z_norm) + a_cos * np.cos(omega * z_norm)
    r = val_bao - (pred_cosmo + osc)
    return float(r @ cov_bao_inv @ r)

# Grid de omega (en unidades de z_norm)
omega_grid = np.linspace(0.1, 20.0, 200)  # radianes sobre z_normalizado
chi2_osc = np.zeros_like(omega_grid)

print(f"  Scan sobre {len(omega_grid)} valores de omega...")
for i, om in enumerate(omega_grid):
    # Optimizar sobre (Om, w0, wa, a_sin, a_cos)
    # Partimos del mejor w0-wa
    x0 = [Om_w0wa, w0_w0wa, wa_w0wa, 0.0, 0.0]
    res = minimize(lambda p: chi2_with_osc(p, om),
                   x0=x0, method="Nelder-Mead",
                   options={"xatol": 1e-4, "fatol": 1e-3, "maxiter": 500})
    chi2_osc[i] = res.fun

# Mejor omega
i_best = np.argmin(chi2_osc)
omega_best = omega_grid[i_best]
chi2_best_osc = chi2_osc[i_best]
delta_chi2 = chi2_w0wa - chi2_best_osc

print(f"\n  Mejor omega: {omega_best:.3f}")
print(f"  chi2(baseline w0-wa): {chi2_w0wa:.2f}")
print(f"  chi2(baseline + osc): {chi2_best_osc:.2f}")
print(f"  Delta chi2: {delta_chi2:.2f}")

# ============================================================
# 5: Test nulo via Monte Carlo
# ============================================================
paso(5, "Test nulo: simular datos del baseline + covarianza")

# Simulamos: val_sim = pred_w0wa + N(0, cov_bao)
# Para cada simulacion, escaneamos omega y obtenemos max Delta chi2

N_SIM = 200
print(f"  {N_SIM} simulaciones Monte Carlo...")

np.random.seed(20260921)
delta_chi2_null = []

for sim in range(N_SIM):
    # Ruido correlacionado
    noise = np.random.multivariate_normal(np.zeros(len(z_bao)), cov_bao)
    val_sim = pred_w0wa + noise
    
    # Chi2 con baseline
    def chi2_base(params):
        Om, w0, wa = params
        pred = pred_model([Om, w0, wa], w0_wa=True)
        r = val_sim - pred
        return float(r @ cov_bao_inv @ r)
    
    best_base = minimize(chi2_base, x0=[Om_w0wa, w0_w0wa, wa_w0wa],
                          method="Nelder-Mead",
                          options={"xatol": 1e-4, "fatol": 1e-3})
    chi2_base_min = best_base.fun
    
    # Scan oscilaciones (grid reducido para velocidad)
    omega_grid_sim = np.linspace(0.1, 20.0, 100)
    chi2_min_sim = chi2_base_min
    for om in omega_grid_sim:
        def chi2_osc_sim(params, om=om):
            Om, w0, wa, a_sin, a_cos = params
            pred_cosmo = pred_model([Om, w0, wa], w0_wa=True)
            z_norm = (z_bao - z_bao.mean()) / z_bao.std()
            osc = a_sin * np.sin(om * z_norm) + a_cos * np.cos(om * z_norm)
            r = val_sim - (pred_cosmo + osc)
            return float(r @ cov_bao_inv @ r)
        
        res = minimize(lambda p: chi2_osc_sim(p, om=om),
                       x0=[best_base.x[0], best_base.x[1], best_base.x[2], 0, 0],
                       method="Nelder-Mead",
                       options={"xatol": 1e-3, "fatol": 1e-2, "maxiter": 300})
        if res.fun < chi2_min_sim:
            chi2_min_sim = res.fun
    
    delta = chi2_base_min - chi2_min_sim
    delta_chi2_null.append(delta)

delta_chi2_null = np.array(delta_chi2_null)
print(f"  Completado")

# ============================================================
# 6: Significancia
# ============================================================
paso(6, "Significancia de la oscilacion detectada")

# p-value: fraccion de simulaciones con Delta chi2 >= observado
p_value = np.mean(delta_chi2_null >= delta_chi2)
n_mayores = np.sum(delta_chi2_null >= delta_chi2)

print(f"  Delta chi2 observado: {delta_chi2:.2f}")
print(f"  Distribucion nula: media = {delta_chi2_null.mean():.2f}, std = {delta_chi2_null.std():.2f}")
print(f"  Percentil 95: {np.percentile(delta_chi2_null, 95):.2f}")
print(f"  Percentil 99: {np.percentile(delta_chi2_null, 99):.2f}")
print(f"  Maximo nulo: {delta_chi2_null.max():.2f}")
print()
print(f"  Simulaciones con Delta chi2 >= observado: {n_mayores}/{N_SIM}")
print(f"  p-value: {p_value:.4f}")

# Veredicto
if p_value < 0.01:
    veredicto = "DETECCION_FUERTE"
    print(f"  VEREDICTO: Deteccion fuerte (p < 0.01)")
elif p_value < 0.05:
    veredicto = "DETECCION_MODERADA"
    print(f"  VEREDICTO: Deteccion moderada (p < 0.05)")
elif p_value < 0.32:
    veredicto = "SIN_DETECCION"
    print(f"  VEREDICTO: Sin deteccion significativa")
else:
    veredicto = "CONSISTENTE_CON_NULO"
    print(f"  VEREDICTO: Consistente con ruido (p > 0.32)")

# ============================================================
# 7: Guardar
# ============================================================
paso(7, "Guardar resultado")

resultado = {
    "fase": "Tarea A (P1)",
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "descripcion": "Busqueda de oscilaciones en residuos H(z) de DESI DR2",
    "prediccion_P1": "Residuo ausente a 3 sigma (PDF v5.0, 17.1)",
    "advertencia": "El PDF no especifica omega ni A. Test es exploratorio, no confirmatorio.",
    "datos": {
        "N_puntos": int(len(z_bao)),
        "z_range": [float(z_bao.min()), float(z_bao.max())],
        "z_mean": float(z_bao.mean()),
        "z_std": float(z_bao.std()),
    },
    "baseline": {
        "modelo": "w0-wa CPL",
        "Om": float(Om_w0wa),
        "w0": float(w0_w0wa),
        "wa": float(wa_w0wa),
        "chi2": float(chi2_w0wa),
    },
    "oscilacion": {
        "omega_best": float(omega_best),
        "chi2_best": float(chi2_best_osc),
        "delta_chi2": float(delta_chi2),
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
# 8: Resumen
# ============================================================
paso(8, "RESUMEN Tarea A")

print(f"  Analisis de P1 (oscilaciones helicoidales en H(z)):")
print(f"    Datos: DESI DR2 BAO ({len(z_bao)} puntos)")
print(f"    Baseline: w0-wa CPL, chi2 = {chi2_w0wa:.2f}")
print(f"    Mejor oscilacion: omega = {omega_best:.3f}")
print(f"    Delta chi2 vs baseline: {delta_chi2:.2f}")
print()
print(f"    Test nulo (MC, N={N_SIM}):")
print(f"      p-value: {p_value:.4f}")
print(f"      Nulos con Delta chi2 >= obs: {n_mayores}")
print()
print(f"    VEREDICTO: {veredicto}")
print()
print(f"  Tiempo: {time.time()-t0:.1f}s")
print()
print("=" * 72)
print("  INTERPRETACION PARA THU-TBEA")
print("=" * 72)
if veredicto == "CONSISTENTE_CON_NULO" or veredicto == "SIN_DETECCION":
    print("  P1 no detectada -> consistente con 'residuo ausente' del PDF.")
    print("  NO falsada (P1 no exige que la oscilacion exista en DESI DR2).")
    print("  Esperar DESI DR3 / Euclid para mayor sensibilidad.")
else:
    print("  P1 potencialmente detectada.")
    print("  Requiere analisis adicional y verificacion con otros datasets.")
