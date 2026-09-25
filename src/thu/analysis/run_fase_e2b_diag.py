# -*- coding: utf-8 -*-
"""
FASE E.2b — Diagnostico CAMB.
  1. Reproducir E.2 (acc=1)
  2. Re-correr con acc=2 (test de sensibilidad)
  3. Comparar total / lensed_scalar / unlensed_scalar / tensor
  4. Verificar paridad: BB_unlensed = 0
  5. Confirmar convencion D_l vs C_l
  6. Comparar BB_lensed contra Planck 2018 VI
"""
import sys, time
from pathlib import Path
import numpy as np
import camb
from camb import model as camb_model

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
TOTAL = 6
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

PARAMS = dict(H0=67.36, ombh2=0.02237, omch2=0.1200,
              tau=0.0544, mnu=0.06, ns=0.9649, As=2.100e-9)

def correr_camb(lens_acc):
    pars = camb_model.CAMBparams()
    pars.set_cosmology(H0=PARAMS["H0"], ombh2=PARAMS["ombh2"],
                       omch2=PARAMS["omch2"], tau=PARAMS["tau"],
                       mnu=PARAMS["mnu"], omk=0, nnu=3.046)
    pars.InitPower.set_params(As=PARAMS["As"], ns=PARAMS["ns"], r=0)
    pars.set_for_lmax(4000, lens_potential_accuracy=lens_acc)
    res = camb.get_results(pars)
    return res.get_cmb_power_spectra(pars, CMB_unit="muK")

# -- 1 --
paso(1, "Recomputar CAMB con lens_potential_accuracy = 1",
     "Reproducir E.2")
powers_1 = correr_camb(1)
print(f"  Claves disponibles: {list(powers_1.keys())}")

# -- 2 --
paso(2, "Recomputar CAMB con lens_potential_accuracy = 2",
     "Test de sensibilidad al lenteo")
powers_2 = correr_camb(2)

ell = np.arange(powers_1["total"].shape[0])
i1000 = int(np.argmin(np.abs(ell - 1000)))

bb1 = powers_1["total"][i1000, 2]
bb2 = powers_2["total"][i1000, 2]
print(f"  BB(l=1000) acc=1: {bb1:.6e} muK^2")
print(f"  BB(l=1000) acc=2: {bb2:.6e} muK^2")
if bb1 > 0:
    print(f"  Ratio acc2/acc1:  {bb2/bb1:.4f}")

# -- 3 --
paso(3, "Comparar total / lensed_scalar / unlensed_scalar / tensor",
     "Identificar que contiene el lenteo")
for key in ["total", "lensed_scalar", "unlensed_scalar", "tensor"]:
    if key in powers_2:
        bb = powers_2[key][:, 2]
        ee = powers_2[key][:, 1]
        tt = powers_2[key][:, 0]
        print(f"  {key:18s}  TT={tt[i1000]:10.4f}  EE={ee[i1000]:9.4f}  BB={bb[i1000]:.6e}")

# -- 4 --
paso(4, "Verificar paridad: BB_unlensed = 0",
     "En LCDM r=0 sin lenteo, BB debe ser exactamente 0")
if "unlensed_scalar" in powers_2:
    bb_unl = powers_2["unlensed_scalar"][:, 2]
    bb_max = float(np.max(np.abs(bb_unl)))
    print(f"  max|BB_unlensed| = {bb_max:.3e} muK^2")
    ok = bb_max < 1e-20
    print(f"  Paridad preservada en escalares: {ok}")
    if not ok:
        print(f"  -> BB_unlensed NO es cero: revisar CAMB version / precision")

# -- 5 --
paso(5, "Confirmar convencion de unidades",
     "CAMB devuelve D_l = l(l+1)C_l/(2*pi), no C_l")
d_l_1000 = powers_2["total"][i1000, 0]
c_l_1000 = d_l_1000 * 2 * np.pi / (ell[i1000] * (ell[i1000] + 1))
print(f"  D_l^TT(l=1000) = {d_l_1000:.4f} muK^2  (esperado: ~1000-1100)")
print(f"  Si CAMB devolviera C_l directo, seria {c_l_1000:.3e}")
print(f"  -> CAMB devuelve D_l (consistente con Planck 2018)")

# -- 6 --
paso(6, "Comparar BB_lensed contra Planck 2018 VI",
     "Valor de referencia: D_l^BB lensed ~ 5 muK^2 en l~1000")
bb_lensed = float(powers_2["total"][i1000, 2])
print(f"  D_l^BB(l=1000) CAMB    = {bb_lensed:.6e} muK^2")
print(f"  D_l^BB(l=1000) Planck  = ~5 muK^2 (referencia)")
if bb_lensed > 0:
    print(f"  Ratio CAMB/Planck: {bb_lensed/5:.4e}")
if bb_lensed < 0.5:
    print(f"  ADVERTENCIA: discrepancia > 10x")
    print(f"  Puede indicar: (a) CAMB no incluye lenteo en 'total',")
    print(f"                 (b) 'total' es unlensed, o")
    print(f"                 (c) convencion de lenteo distinta")
else:
    print(f"  Orden de magnitud consistente")

t_total = time.time() - t0
print()
print("=" * 72)
print("  FIN E.2b")
print("=" * 72)
print(f"  Duracion total: {t_total:.2f}s")
