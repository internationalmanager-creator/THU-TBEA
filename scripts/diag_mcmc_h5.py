#!/usr/bin/env python3
"""Diagnostico exhaustivo del HDF5 del MCMC. Solo lectura. No interpreta, solo reporta."""
import json
from pathlib import Path
import numpy as np
import h5py

BASE = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
BM = BASE / "data" / "raw" / "cosmic-birefringence-planck-act" / "beta_mcmc"
H5 = BM.parent / "data" / "computed" / "mcmc_chain.h5"
OUT = BASE / "data" / "inventory" / "mcmc_h5_diag.json"

print(f"H5: {H5}")
if not H5.exists():
    raise SystemExit("No existe HDF5")

report = {"h5_path": str(H5), "groups": [], "datasets": []}

def walk(name, obj):
    kind = "group" if isinstance(obj, h5py.Group) else "dataset"
    entry = {"path": name, "kind": kind}
    if kind == "dataset":
        entry["shape"] = list(obj.shape)
        entry["dtype"] = str(obj.dtype)
        entry["attrs"] = {k: str(v) for k, v in obj.attrs.items()}
    else:
        entry["attrs"] = {k: str(v) for k, v in obj.attrs.items()}
    if kind == "group":
        report["groups"].append(entry)
    else:
        report["datasets"].append(entry)

with h5py.File(H5, "r") as f:
    print("\n--- ARBOL HDF5 ---")
    f.visititems(walk)
    for g in report["groups"]:
        print(f"  [G] {g['path']}")
        for ak, av in g.get("attrs", {}).items():
            print(f"       attr {ak} = {av}")
    for d in report["datasets"]:
        print(f"  [D] {d['path']}  shape={d['shape']}  dtype={d['dtype']}")
        for ak, av in d.get("attrs", {}).items():
            print(f"       attr {ak} = {av}")

    # Analizar 'chain' si existe
    print("\n--- ANALISIS DEL CHAIN ---")
    if "mcmc" in f and "chain" in f["mcmc"]:
        chain = np.array(f["mcmc"]["chain"])
        print(f"  chain.shape = {chain.shape}  (esperado: nsteps, nwalkers, ndim)")
        print(f"  chain.ndim  = {chain.ndim}")
        print(f"  nsteps inferred: {chain.shape[0]}")
        print(f"  nwalkers inferred: {chain.shape[1] if chain.ndim>=2 else '?'}")
        print(f"  ndim inferred: {chain.shape[-1]}")

        # Dump de cada columna (último eje) — estadisticos por columna
        print("\n  Estadisticos por columna (ultimo eje = parametros):")
        ndim = chain.shape[-1]
        nsteps = chain.shape[0]
        nwalkers = chain.shape[1]
        # aplanar (nsteps*nwalkers, ndim)
        flat = chain.reshape(-1, ndim)
        for j in range(ndim):
            col = flat[:, j]
            col = col[np.isfinite(col)]
            if len(col) == 0:
                print(f"    col {j}: vacia")
                continue
            m = float(np.mean(col))
            s = float(np.std(col))
            p50 = float(np.percentile(col, 50))
            print(f"    col {j}: mean={m:+.6f}  std={s:.6f}  median={p50:+.6f}  n={len(col)}")
            report.setdefault("columns", []).append({
                "idx": j, "mean": m, "std": s, "median": p50,
                "n_samples": int(len(col)),
            })

        # Comparacion con snapshots SQLite (0.2090 en grados)
        print("\n  Comparacion con SQLite snapshots:")
        print(f"    SQLite final beta_mean = 0.2090401684083868 (deg segun config)")
        if report.get("columns"):
            beta_guess_deg = report["columns"][0]["mean"]
            beta_guess_rad = beta_guess_deg * 180.0 / np.pi
            print(f"    col 0 raw mean        = {beta_guess_deg:+.6f}")
            print(f"    col 0 * 180/pi        = {beta_guess_rad:+.6f}  (si raw fuera rad)")
            print(f"    col 0 * pi/180        = {beta_guess_deg * np.pi / 180.0:+.6f}  (si raw fuera deg)")

        # Primeras muestras crudas para inspeccion visual
        print("\n  Primeras 3 muestras crudas (chain[0, 0:3, :]):")
        for k in range(min(3, nwalkers)):
            row = chain[0, k, :]
            print(f"    walker {k}: " + "  ".join(f"{v:+.6e}" for v in row))

    else:
        print("  'mcmc/chain' no encontrado")

with open(OUT, "w", encoding="utf-8") as fp:
    json.dump(report, fp, indent=2, ensure_ascii=False)
print(f"\n-> {OUT}")
