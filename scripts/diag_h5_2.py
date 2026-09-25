import h5py, numpy as np, json
from pathlib import Path
BASE = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
H5 = BASE / "data" / "raw" / "cosmic-birefringence-planck-act" / "data" / "computed" / "mcmc_chain.h5"
OUT = BASE / "data" / "inventory" / "h5_diag.json"
print(f"H5: {H5}")
print(f"exists: {H5.exists()}")
if not H5.exists():
    raise SystemExit(1)
report = {"h5": str(H5)}
with h5py.File(H5, "r") as f:
    print("\n--- ARBOL ---")
    def walk(name, obj):
        kind = "G" if isinstance(obj, h5py.Group) else "D"
        if kind == "D":
            print(f"  [D] {name}  shape={obj.shape}  dtype={obj.dtype}")
            report.setdefault("datasets", []).append({"path":name,"shape":list(obj.shape),"dtype":str(obj.dtype)})
        else:
            print(f"  [G] {name}")
    f.visititems(walk)
    if "mcmc" in f and "chain" in f["mcmc"]:
        arr = np.array(f["mcmc"]["chain"])
        print(f"\n--- chain ---")
        print(f"  shape = {arr.shape}")
        print(f"  chain[0,0,:] = {arr[0,0,:]}")
        print(f"  chain[0,1,:] = {arr[0,1,:]}")
        print(f"  chain[500,0,:] = {arr[500,0,:]}")
        flat = arr.reshape(-1, arr.shape[-1])
        cols = []
        print(f"\n  Estadisticas por columna (raw):")
        for j in range(arr.shape[-1]):
            col = flat[:,j]
            col = col[np.isfinite(col)]
            m = float(np.mean(col)); s = float(np.std(col))
            print(f"    col {j}: mean={m:+.8f}  std={s:.8f}")
            cols.append({"idx":j,"mean":m,"std":s})
        report["cols"] = cols
        sqlite_val = 0.2090401684083868
        print(f"\n  SQLite dice: {sqlite_val}")
        print(f"  col0 mean : {cols[0]['mean']}")
        print(f"  ratio (SQLite/col0) = {sqlite_val/cols[0]['mean']:.4f}")
        print(f"  col0 * pi/180        = {cols[0]['mean'] * np.pi/180:.6f}")
        print(f"  col0 * 180/pi        = {cols[0]['mean'] * 180/np.pi:.6f}")
    for k in ["log_prob","accepted"]:
        if k in f["mcmc"]:
            a = np.array(f["mcmc"][k])
            print(f"  mcmc/{k}: shape={a.shape}")
json.dump(report, open(OUT,"w"), indent=2)
print(f"\n-> {OUT}")
