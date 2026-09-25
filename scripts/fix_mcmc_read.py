"""Corrige lectura del chain: filtra filas de relleno, convierte rad->deg, actualiza cierre."""
import h5py, numpy as np, json, sqlite3
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
H5 = BASE / "data" / "raw" / "cosmic-birefringence-planck-act" / "data" / "computed" / "mcmc_chain.h5"
SQLITE = H5.parent / "mcmc_runs.sqlite"
OUT = BASE / "data" / "inventory" / "mcmc_run_id_3_final.json"
CIERRE = BASE / "registry" / "thu" / "fase_e_cierre.json"

BURN = 5000
DEG = 180.0 / np.pi

# --- 1. Leer SQLite para saber el step real ---
con = sqlite3.connect(f"file:{SQLITE}?mode=ro", uri=True)
cur = con.cursor()
cur.execute("SELECT current_step, n_walkers, n_params FROM mcmc_runs WHERE run_id=3")
row = cur.fetchone()
current_step, n_walkers, n_params = int(row[0]), int(row[1]), int(row[2])
con.close()
print(f"SQLite: run_id=3 -> current_step={current_step}, n_walkers={n_walkers}, n_params={n_params}")

# --- 2. Leer chain + log_prob del HDF5 ---
with h5py.File(H5, "r") as f:
    chain = np.array(f["mcmc"]["chain"])      # (30000, 12, 6)
    logp  = np.array(f["mcmc"]["log_prob"])   # (30000, 12)

print(f"Chain shape completa: {chain.shape}")

# Detectar filas de relleno: logp == 0 (o no finitas) en TODOS los walkers
mask_row = ~np.all((logp == 0) | ~np.isfinite(logp), axis=1)
valid_rows = np.where(mask_row)[0]
print(f"Filas con logp valido: {valid_rows.size}  (primera={valid_rows[0]}, ultima={valid_rows[-1]})")

# Consistencia con SQLite
if valid_rows[-1] + 1 != current_step:
    print(f"[WARN] valid_rows termina en {valid_rows[-1]+1}, SQLite dice {current_step}")

# --- 3. Aplicar burn-in ---
burn = min(BURN, current_step // 2)
keep = valid_rows[valid_rows >= burn]
print(f"Burn-in: {burn}, filas post-burn validas: {keep.size}")

# --- 4. Extraer beta (col 0) y convertir rad->deg ---
chain_valid = chain[keep]                # (n_valid, 12, 6)
flat = chain_valid.reshape(-1, n_params)
beta_rad = flat[:, 0]
beta_rad = beta_rad[np.isfinite(beta_rad)]

beta_deg = beta_rad * DEG
m = float(np.mean(beta_deg))
s = float(np.std(beta_deg))
p16 = float(np.percentile(beta_deg, 16))
p50 = float(np.percentile(beta_deg, 50))
p84 = float(np.percentile(beta_deg, 84))

print(f"\n=== RESULTADO ===")
print(f"  n_samples          : {beta_deg.size}")
print(f"  beta_deg mean+/-std: {m:.4f} +/- {s:.4f}")
print(f"  beta_deg median    : {p50:.4f} [{p16:.4f}, {p84:.4f}]")

# --- 5. Comparar con SQLite y paper ---
sqlite_final = 0.2090401684083868
print(f"\n  SQLite final       : {sqlite_final:.6f}")
print(f"  Diferencia (deg)   : {abs(m - sqlite_final):.6f}")

ref_prev  = 0.207;  s_prev  = 0.073
ref_paper = 0.215;  s_paper = 0.074
for label, ref, sig in [("E.3-C8f", ref_prev, s_prev), ("Diego-Palazuelos 25", ref_paper, s_paper)]:
    sc = float(np.sqrt(s*s + sig*sig))
    diff_sigma = abs(m - ref) / sc
    print(f"  vs {label:22s}: {diff_sigma:.2f} sigma")

# --- 6. Guardar final json ---
out = {
    "fecha": datetime.now(timezone.utc).isoformat(),
    "h5_path": str(H5),
    "run_id": 3,
    "current_step_sqlite": current_step,
    "n_walkers": n_walkers,
    "n_params": n_params,
    "n_burn": burn,
    "valid_rows_used": int(keep.size),
    "n_samples_post_burn": int(beta_deg.size),
    "beta_mean_deg": m,
    "beta_std_deg": s,
    "beta_median_deg": p50,
    "beta_p16_deg": p16,
    "beta_p84_deg": p84,
    "unidad_origen_chain": "radianes (convertido a grados)",
    "nota": "Chain recuperado post PermissionError. Filas post-crash (logp=0) excluidas.",
}
OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"\n-> {OUT}")

# --- 7. Actualizar fase_e_cierre.json ---
if CIERRE.exists():
    cierre = json.loads(CIERRE.read_text(encoding="utf-8"))
else:
    cierre = {}

cierre["mcmc_run_id_3"] = {
    "run_id": 3,
    "status": "completed_90pct_recuperado",
    "steps_completados": current_step,
    "steps_objetivo": 30000,
    "n_walkers": n_walkers,
    "n_params": n_params,
    "n_burn": burn,
    "beta_mean_deg": m,
    "beta_std_deg": s,
    "beta_median_deg": p50,
    "beta_p16_deg": p16,
    "beta_p84_deg": p84,
    "n_samples_post_burn": int(beta_deg.size),
    "chain_shape": list(chain.shape),
    "unidad_origen": "radianes -> grados",
    "fecha_lectura": datetime.now(timezone.utc).isoformat(),
    "h5_path": str(H5),
    "nota": "Chain recuperado post crash. Filas post-27100 con logp=0 excluidas del analisis.",
}
CIERRE.write_text(json.dumps(cierre, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"-> {CIERRE}")
