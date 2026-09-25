# -*- coding: utf-8 -*-
"""
FASE E.2 — CAMB: C_l teoricos ΛCDM.
Parametros Planck 2018 (TT,TE,EE+lowE+lensing). FIJOS.
No se ajustan. Sin fine-tuning.
"""
import sys, time, json
from pathlib import Path
import numpy as np

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
OUT_DIR = LAB / "data" / "intermediate"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOTAL = 5
t0 = time.time()

def barra(i):
    pct = int(100 * i / TOTAL)
    filled = pct * 40 // 100
    return "█" * filled + "░" * (40 - filled), pct

def paso(i, titulo, desc):
    bar, pct = barra(i)
    print()
    print("═" * 72)
    print(f"  PASO {i}/{TOTAL}  [{bar}]  {pct:3d}%")
    print(f"  {titulo}")
    print(f"  → {desc}")
    print("═" * 72)
    sys.stdout.flush()

# ── 1: Importar CAMB ──
paso(1, "Importar CAMB",
    "Verificar que camb esta instalado y funciona")
import camb
from camb import model as camb_model
print(f"  CAMB version: {camb.__version__}")
print(f"  ✓ Import OK")

# ── 2: Definir parametros Planck 2018 ΛCDM ──
paso(2, "Definir parametros Planck 2018 ΛCDM",
    "Valores publicados. NO se ajustan. Fuente: Planck 2018 VI (A&A 641, A6)")

# Parametros de la tabla 2, columna TT,TE,EE+lowE+lensing
params_planck18 = {
    "H0": 67.36,        # km/s/Mpc
    "ombh2": 0.02237,   # Omega_b h^2
    "omch2": 0.1200,    # Omega_c h^2
    "tau": 0.0544,      # reionization optical depth
    "mnu": 0.06,        # sum m_nu [eV]
    "ns": 0.9649,       # scalar spectral index
    "As": 2.100e-9,     # scalar amplitude
    "lmax": 4000,       # max multipole
}

print(f"  Parametros (Planck 2018 VI, TT,TE,EE+lowE+lensing):")
for k, v in params_planck18.items():
    print(f"    {k:8s} = {v}")

# ── 3: Computar C_l con CAMB ──
paso(3, "Computar C_l con CAMB",
    "TT, TE, EE, BB para l = 2..4000")

t_start = time.time()
pars = camb_model.CAMBparams()

pars.set_cosmology(
    H0=params_planck18["H0"],
    ombh2=params_planck18["ombh2"],
    omch2=params_planck18["omch2"],
    tau=params_planck18["tau"],
    mnu=params_planck18["mnu"],
    omk=0,
    nnu=3.046
)
pars.InitPower.set_params(
    As=params_planck18["As"],
    ns=params_planck18["ns"],
    r=0  # tensor-to-scalar = 0 (ΛCDM estandar)
)
pars.set_for_lmax(params_planck18["lmax"], lens_potential_accuracy=1)

results = camb.get_results(pars)
powers = results.get_cmb_power_spectra(pars, CMB_unit="muK")

# Extraer TT, EE, BB, TE
ell = np.arange(powers["total"].shape[0])
cl_TT = powers["total"][:, 0]   # muK^2
cl_EE = powers["total"][:, 1]
cl_BB = powers["total"][:, 2]
cl_TE = powers["total"][:, 3]

t_camb = time.time() - t_start
print(f"  Tiempo CAMB: {t_camb:.2f}s")
print(f"  Shape: {cl_TT.shape}")
print(f"  l range: {ell.min()}..{ell.max()}")

# Sanity check: valores en l=100, 500, 1000
print(f"\n  Sanity check (l=100,500,1000):")
for l_test in [100, 500, 1000]:
    i = np.argmin(np.abs(ell - l_test))
    print(f"    l={l_test:4d}:  TT={cl_TT[i]:10.2f}  EE={cl_EE[i]:9.2f}  BB={cl_BB[i]:7.3f}  TE={cl_TE[i]:9.2f}  [muK^2]")

# ── 4: Verificar BB ≈ 0 (paridad preservada en ΛCDM) ──
paso(4, "Verificar BB = 0 en ΛCDM",
    "Sin violacion de paridad, C_l^BB debe ser ~0 en l < 100")

l_mask = (ell >= 2) & (ell <= 100)
bb_peak = np.max(np.abs(cl_BB[l_mask]))
ee_peak = np.max(np.abs(cl_EE[l_mask]))
ratio = bb_peak / ee_peak if ee_peak > 0 else 0

print(f"  BB peak (l=2..100): {bb_peak:.6e} muK^2")
print(f"  EE peak (l=2..100): {ee_peak:.6e} muK^2")
print(f"  Ratio BB/EE: {ratio:.3e}")
print(f"  ✓ BB ~ 0 en ΛCDM: {ratio < 1e-3}")

# ── 5: Guardar C_l a disco ──
paso(5, "Guardar C_l a disco",
    "Binario .npz para reusar sin recomputar")

out = OUT_DIR / "cl_lcdm_planck18.npz"
np.savez(
    out,
    ell=ell,
    cl_tt=cl_TT,
    cl_ee=cl_EE,
    cl_bb=cl_BB,
    cl_te=cl_TE,
    params=json.dumps(params_planck18),
    source="camb",
    camb_version=camb.__version__
)

print(f"  Guardado: {out}")
print(f"  Tamaño: {out.stat().st_size / 1024:.1f} KB")

# Metadata del calculo
meta = {
    "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "camb_version": camb.__version__,
    "params": params_planck18,
    "source": "Planck 2018 VI (A&A 641, A6)",
    "lmax": params_planck18["lmax"],
    "unit": "muK^2",
    "spectra": ["TT", "EE", "BB", "TE"],
    "t_camb_seconds": round(t_camb, 3),
}
meta_path = OUT_DIR / "cl_lcdm_planck18_meta.json"
meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
print(f"  Metadata: {meta_path}")

t_total = time.time() - t0
print()
print("╔" + "═" * 70 + "╗")
print("║" + " RESUMEN FASE E.2 ".center(70) + "║")
print("╚" + "═" * 70 + "╝")
print(f"  C_l ΛCDM computados con CAMB")
print(f"  Parámetros: Planck 2018 (fijos, no ajustados)")
print(f"  l = 2..4000")
print(f"  BB ~ 0 (paridad preservada)")
print(f"  Duración: {t_total:.2f}s")
print(f"  Output: {out}")
print()
print("  → Listos para comparar contra likelihoods reales en E.3")
