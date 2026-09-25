# -*- coding: utf-8 -*-
"""FASE F.1 — Reconocimiento de C_L^alpha-alpha de Planck PR4."""
import sys, json
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
PP4 = LAB / "data" / "raw" / "planck_pr4"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# --- 1: Cargar CB spectra ---
hdr("1. Cargar NPIPE_CB_spectra.csv")

data = np.genfromtxt(PP4 / "cb_spectra" / "NPIPE_CB_spectra.csv",
                     delimiter=",", comments="#", skip_header=0)
print(f"  shape: {data.shape}")
print(f"  Columnas: L, Full mission, A x A, B x B, A x B")

# Extraer
L = data[1:, 0]           # skip NaN header row
CB_full = data[1:, 1]
CB_AxA  = data[1:, 2]
CB_BxB  = data[1:, 3]
CB_AxB  = data[1:, 4]

print(f"\n  L range: {L.min():.0f}..{L.max():.0f}")
print(f"  CB_full(L=0)  = {CB_full[0]:.6e}")
print(f"  CB_full(L=100)= {CB_full[100]:.6e}")
print(f"  CB_full(L=500)= {CB_full[500]:.6e}")
print(f"  CB_full(L=1000)={CB_full[1000]:.6e}")

# Estadísticas
print(f"\n  Estadisticas de CB_full:")
print(f"    media = {CB_full.mean():.6e}")
print(f"    std   = {CB_full.std():.6e}")
print(f"    min   = {CB_full.min():.6e}")
print(f"    max   = {CB_full.max():.6e}")

# --- 2: Estructura del espectro ---
hdr("2. Estructura del espectro (buscar peaks)")

# Suavizar para ver estructura
from scipy.ndimage import uniform_filter1d
CB_smooth = uniform_filter1d(CB_full, size=20)
peak_idx = np.argmax(np.abs(CB_smooth[1:])) + 1
print(f"  Peak en L = {L[peak_idx]:.0f} con valor {CB_smooth[peak_idx]:.4e}")

# Ratio CB_full / CB_AxA (auto vs cross)
ratio = CB_full / np.where(np.abs(CB_AxA) > 1e-20, CB_AxA, 1e-20)
ratio_med = np.median(ratio[10:100])
print(f"  Ratio mediano (Full / A x A) en L=10..100: {ratio_med:.4f}")

# --- 3: Cargar alpha-CMB cross-correlations ---
hdr("3. Cargar NPIPE_alpha_CMB_cc.csv")

alpha = np.genfromtxt(PP4 / "cb_spectra" / "NPIPE_alpha_CMB_cc.csv",
                      delimiter=",", comments="#", skip_header=0)
print(f"  shape: {alpha.shape}")
print(f"  Columnas: L bin, alpha T, alpha E, alpha B, err_alpha_T, err_alpha_E, err_alpha_B")

Lbin = alpha[1:, 0]
alphaT = alpha[1:, 1]
alphaE = alpha[1:, 2]
alphaB = alpha[1:, 3]
errT = alpha[1:, 4]
errE = alpha[1:, 5]
errB = alpha[1:, 6]

print(f"\n  L bin: {Lbin}")
print(f"  alpha*T:  {alphaT}")
print(f"  alpha*E:  {alphaE}")
print(f"  alpha*B:  {alphaB}")

# Significancia
print(f"\n  Significancia (alpha/sigma):")
print(f"    alpha*T: {alphaT/errT}")
print(f"    alpha*E: {alphaE/errE}")
print(f"    alpha*B: {alphaB/errB}")

# --- 4: Comparar NPIPE vs PR3 ---
hdr("4. Comparar NPIPE vs PR3")

pr3 = np.genfromtxt(PP4 / "cb_spectra" / "PR3_CB_spectra.csv",
                    delimiter=",", comments="#", skip_header=0)
PR3_full = pr3[1:, 1]

print(f"  NPIPE CB_full(L=0) = {CB_full[0]:.6e}")
print(f"  PR3   CB_full(L=0) = {PR3_full[0]:.6e}")
print(f"  Ratio NPIPE/PR3 en L=0: {CB_full[0]/PR3_full[0]:.4f}")

# Diferencia
diff = CB_full - PR3_full
print(f"  Diferencia media: {diff.mean():.4e}")
print(f"  Diferencia std:   {diff.std():.4e}")

# --- 5: Prediccion teorica (si existe) ---
hdr("5. Prediccion teorica de C_L^alpha-alpha")

print("  El PDF §10-11 deriva:")
print("    - beta_0 = 0.3803 deg (isotropo)")
print("    - Perfil beta(z)/beta_0 (Tabla 11.1)")
print("  NO deriva C_L^alpha-alpha explicitamente.")
print()
print("  Modelos competidores en la literatura:")
print("    - Sherwin-Namikawa 2021: C_L^alpha-alpha = A * C_L^lensing / L(L+1)")
print("    - Namikawa 2024: reionization anisotropy ~ 0")
print("    - Zagatti 2024: CB_spectra como este archivo")

# --- 6: Test chi2 vs nulo ---
hdr("6. Test estadistico: es C_L^alpha-alpha != 0?")

# Chi2 contra cero
# Ignorar L=0 (monopolo) y L=1 (dipolo)
mask = (L >= 2) & (L <= 500)  # rango donde suele estar la senal
CB_masked = CB_full[mask]

# Estimar sigma como std de la distribucion
sigma_est = CB_masked.std()
chi2_null = np.sum((CB_masked / sigma_est)**2)
dof = len(CB_masked)
print(f"  rango L: 2..500, n={dof}")
print(f"  sigma_est = {sigma_est:.4e}")
print(f"  chi2(contra 0) = {chi2_null:.2f}")
print(f"  dof = {dof}")
print(f"  chi2/dof = {chi2_null/dof:.4f}")
print()
if chi2_null/dof > 1.5:
    print("  -> C_L^alpha-alpha != 0 (chi2/dof > 1.5)")
elif chi2_null/dof < 0.5:
    print("  -> C_L^alpha-alpha ~ 0 (chi2/dof < 0.5)")
else:
    print("  -> Consistente con ruido")

# --- 7: Guardar analisis ---
hdr("7. Guardar analisis preliminar")

out_dir = LAB / "data" / "inventory"
out_dir.mkdir(parents=True, exist_ok=True)

resumen = {
    "fecha": "2026-09-21",
    "fuente": "NPIPE_CB_spectra.csv (Planck PR4)",
    "L_max": int(L.max()),
    "CB_L0": float(CB_full[0]),
    "CB_L100": float(CB_full[100]),
    "CB_L1000": float(CB_full[1000]),
    "chi2_null_L2_500": float(chi2_null),
    "chi2_dof_L2_500": float(chi2_null/dof),
    "significancia_alphaT": list((alphaT/errT).round(3)),
    "significancia_alphaE": list((alphaE/errE).round(3)),
    "significancia_alphaB": list((alphaB/errB).round(3)),
}
out = out_dir / "fase_f1_cbl_alpha.json"
out.write_text(json.dumps(resumen, indent=2), encoding="utf-8")
print(f"  Guardado: {out}")
