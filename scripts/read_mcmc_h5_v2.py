#!/usr/bin/env python3
"""Lector HDF5 emcee v2: maneja estructura de Grupo + burn-in + stats."""
import json
from pathlib import Path
from datetime import datetime
import numpy as np
import h5py

BASE = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
BM = BASE / "data" / "raw" / "cosmic-birefringence-planck-act" / "beta_mcmc"
H5 = BM.parent / "data" / "computed" / "mcmc_chain.h5"
OUT = BASE / "data" / "inventory" / "mcmc_run_id_3_final.json"

MCMC_N_BURN = 5000  # segun config guardada

print(f"[HDF5] {H5}")
if not H5.exists():
    raise SystemExit(f"No existe {H5}")

report = {
    "fecha": datetime.utcnow().isoformat() + "Z",
    "h5_path": str(H5),
    "n_burn": MCMC_N_BURN,
    "beta_mean": None, "beta_std": None,
    "beta_median": None, "beta_p16": None, "beta_p84": None,
    "n_samples": None, "chain_shape": None, "h5_keys": None,
    "h5_subkeys": None,
}

with h5py.File(H5, "r") as f:
    keys = list(f.keys())
    print(f"  top-level keys: {keys}")
    report["h5_keys"] = keys

    if "mcmc" not in f:
        raise SystemExit(f"grupo 'mcmc' ausente. keys={keys}")

    grp = f["mcmc"]
    subkeys = list(grp.keys())
    print(f"  mcmc sub-keys : {subkeys}")
    report["h5_subkeys"] = subkeys

    if "chain" not in grp:
        raise SystemExit(f"'chain' ausente dentro de mcmc. subkeys={subkeys}")

    chain = np.array(grp["chain"])  # (nsteps, nwalkers, ndim)
    print(f"  chain shape   : {chain.shape}")
    report["chain_shape"] = list(chain.shape)

    nsteps, nwalkers, ndim = chain.shape
    burn = min(MCMC_N_BURN, nsteps // 2)
    print(f"  burn-in       : {burn} (pedido {MCMC_N_BURN})")

    chain_post = chain[burn:, :, :]  # (nsteps-burn, nwalkers, ndim)
    flat = chain_post.reshape(-1, ndim)
    beta = flat[:, 0]
    beta_ok = beta[np.isfinite(beta)]

    if len(beta_ok) == 0:
        raise SystemExit("sin samples finitos tras burn-in")

    m  = float(np.mean(beta_ok))
    s  = float(np.std(beta_ok))
    p16 = float(np.percentile(beta_ok, 16))
    p50 = float(np.percentile(beta_ok, 50))
    p84 = float(np.percentile(beta_ok, 84))

    print()
    print(f"  n_samples     : {len(beta_ok)}")
    print(f"  beta mean+/−std: {m:.4f} +/- {s:.4f}")
    print(f"  beta median    : {p50:.4f} [{p16:.4f}, {p84:.4f}]")

    report.update({
        "beta_mean": m, "beta_std": s,
        "beta_median": p50, "beta_p16": p16, "beta_p84": p84,
        "n_samples": int(len(beta_ok)),
    })

    # otros parametros (alpha_i) — solo estadisticos basicos
    others = {}
    for j in range(1, ndim):
        col = flat[:, j]
        col_ok = col[np.isfinite(col)]
        if len(col_ok):
            others[f"param_{j}"] = {
                "mean": float(np.mean(col_ok)),
                "std":  float(np.std(col_ok)),
            }
    report["otros_parametros"] = others

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fp:
    json.dump(report, fp, indent=2, ensure_ascii=False)
print()
print(f"  -> {OUT}")
