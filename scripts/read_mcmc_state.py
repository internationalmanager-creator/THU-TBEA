#!/usr/bin/env python3
"""Lee estado del MCMC tras PermissionError. Solo lectura."""
import json, sqlite3
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
BM = BASE / "data" / "raw" / "cosmic-birefringence-planck-act" / "beta_mcmc"
COMPUTED = BM.parent / "data" / "computed"
H5 = COMPUTED / "mcmc_chain.h5"
SQLITE = COMPUTED / "mcmc_runs.sqlite"
OUT = BASE / "data" / "inventory" / "mcmc_state_h2.json"

OUT.parent.mkdir(parents=True, exist_ok=True)
print("=== Estado del MCMC (post-fallo) ===")
print(f"HDF5  : {H5}  (existe={H5.exists()})")
print(f"SQLite: {SQLITE}  (existe={SQLITE.exists()})")
print()

report = {
    "fecha": datetime.utcnow().isoformat() + "Z",
    "h5_path": str(H5), "sqlite_path": str(SQLITE),
    "h5_ok": False, "h5_shape": None, "h5_error": None,
    "sqlite_ok": False, "run_id_3": None, "sqlite_error": None,
}

# ---------- HDF5 ----------
if H5.exists():
    print("[HDF5] Abriendo en read-only...")
    try:
        import h5py
        import numpy as np
        with h5py.File(H5, "r") as f:
            keys = list(f.keys())
            print(f"  Keys: {keys}")
            if "mcmc" in f:
                d = f["mcmc"]
                print(f"  mcmc shape: {d.shape}")
                report["h5_shape"] = list(d.shape)
                chain = np.array(d)
                flat = chain.reshape(-1, chain.shape[-1])
                beta_all = flat[:, 0]
                beta_ok = beta_all[np.isfinite(beta_all)]
                if len(beta_ok) > 0:
                    m = float(np.mean(beta_ok))
                    s = float(np.std(beta_ok))
                    p16 = float(np.percentile(beta_ok, 16))
                    p50 = float(np.percentile(beta_ok, 50))
                    p84 = float(np.percentile(beta_ok, 84))
                    print(f"  beta samples: {len(beta_ok)}")
                    print(f"  mean +/- std   : {m:.4f} +/- {s:.4f}")
                    print(f"  median [16,84] : {p50:.4f} [{p16:.4f}, {p84:.4f}]")
                    report.update({
                        "h5_ok": True, "beta_mean": m, "beta_std": s,
                        "beta_median": p50, "beta_p16": p16,
                        "beta_p84": p84, "n_samples": int(len(beta_ok)),
                    })
                else:
                    report["h5_error"] = "chain sin samples finitos"
            else:
                report["h5_error"] = f"dataset 'mcmc' no encontrado; keys={keys}"
    except Exception as e:
        report["h5_error"] = str(e)
        print(f"  ERROR: {e}")
else:
    print("[HDF5] No existe.")
print()

# ---------- SQLite ----------
if SQLITE.exists():
    print("[SQLite] Consultando runs...")
    try:
        con = sqlite3.connect(f"file:{SQLITE}?mode=ro", uri=True)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabs = [r[0] for r in cur.fetchall()]
        print(f"  Tablas: {tabs}")
        report["sqlite_tables"] = tabs
        for tname in tabs:
            cur.execute(f"PRAGMA table_info({tname})")
            cols = [r[1] for r in cur.fetchall()]
            if "run_id" in cols:
                cur.execute(f"SELECT * FROM {tname} WHERE run_id=3")
                rows = cur.fetchall()
                print(f"  {tname}.run_id=3: {len(rows)} filas")
                for row in rows:
                    d = dict(zip(cols, row))
                    print(f"    {d}")
                    report["run_id_3"] = d
                    report["sqlite_ok"] = True
        con.close()
    except Exception as e:
        report["sqlite_error"] = str(e)
        print(f"  ERROR: {e}")
else:
    print("[SQLite] No existe.")
print()

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"Guardado: {OUT}")
