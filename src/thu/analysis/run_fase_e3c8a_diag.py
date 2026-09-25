# -*- coding: utf-8 -*-
"""E.3-C8a — Leer HDF5 + diagnosticar bug de _compute_chi2."""
import sys
from pathlib import Path

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")
BM = REPO / "beta_mcmc"
CHAIN = REPO / "data" / "computed" / "mcmc_chain.h5"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# --- 1: Leer HDF5 directamente ---
hdr("1. Leer HDF5 chain (via h5py + emcee)")

import h5py
with h5py.File(CHAIN, "r") as f:
    print(f"  Keys en HDF5: {list(f.keys())}")
    for k in f.keys():
        item = f[k]
        if hasattr(item, "shape"):
            print(f"    {k}: shape={item.shape}")
        else:
            print(f"    {k}: {item}")

import emcee
reader = emcee.backends.HDFBackend(str(CHAIN), read_only=True)
print(f"\n  Iteration: {reader.iteration}")
print(f"  N walkers: {reader.shape[0]}, n_params: {reader.shape[2]}")

import numpy as np
chain = reader.get_chain()
print(f"  chain shape: {chain.shape}")

# Analisis basico
if reader.iteration > 0:
    burn = min(20, reader.iteration // 2)
    flat = reader.get_chain(discard=burn, flat=True)
    if len(flat) > 0:
        # Convertir rad->deg
        beta_deg = np.rad2deg(flat[:, 0])
        print(f"\n  Beta (deg) post burn-in ({len(flat)} samples):")
        print(f"    media  = {beta_deg.mean():.4f}")
        print(f"    std    = {beta_deg.std():.4f}")
        print(f"    mediana= {np.median(beta_deg):.4f}")
        print(f"    p16    = {np.percentile(beta_deg, 16):.4f}")
        print(f"    p84    = {np.percentile(beta_deg, 84):.4f}")

# --- 2: Inspeccionar _compute_chi2 en run_beta_mcmc.py ---
hdr("2. Inspeccionar _compute_chi2")
run_file = BM / "run_beta_mcmc.py"
lines = run_file.read_text(encoding="utf-8").splitlines()

for i, l in enumerate(lines, 1):
    if "def _compute_chi2" in l:
        start = i - 1
        print(f"  Encontrado en L{i}")
        for j in range(start, min(start + 60, len(lines))):
            print(f"    L{j+1}: {lines[j]}")
        break

# --- 3: Inspeccionar mk_chi2 en birefringence_likelihood.py ---
hdr("3. Inspeccionar mk_chi2")
bl_file = BM / "birefringence_likelihood.py"
bl_lines = bl_file.read_text(encoding="utf-8").splitlines()

for i, l in enumerate(bl_lines, 1):
    if "def mk_chi2" in l:
        start = i - 1
        print(f"  Encontrado en L{i}")
        for j in range(start, min(start + 60, len(bl_lines))):
            print(f"    L{j+1}: {bl_lines[j]}")
        break

# --- 4: Ver contexto del crash L202 de birefringence_likelihood ---
hdr("4. Contexto del crash (L190-210 de birefringence_likelihood.py)")
for j in range(188, min(215, len(bl_lines))):
    prefix = ">>> " if j == 201 else "    "
    print(f"    {prefix}L{j+1}: {bl_lines[j]}")
