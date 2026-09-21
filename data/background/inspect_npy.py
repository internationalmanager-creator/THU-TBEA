import numpy as np
import json
from pathlib import Path

EXT = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\extracted\zen_runtime")

# Archivos .npy clave
keyFiles = [
    "Planck_NPIPE_CamSpec_PR4_TTTEEE_likelihood_runtime/CamSpec_PR4_TTTEEE_v1_20260919/lower_cholesky.npy",
    "Joint_Planck_PR4_likelihood_runtime_data_for_Joint/JointCMB_planck_v1_20260919/inv_cov.npy",
    "CMB_Lite_Likelihood_Data/cmblite_data/cmblite_data/camspec_npipe_lite/covariance.npy",
]

for rel in keyFiles:
    f = EXT / rel
    if not f.exists():
        print(f"  FALTA: {rel}")
        continue
    try:
        arr = np.load(f, mmap_mode='r')
        print(f"  {rel.split('/')[-1]:50s} shape={arr.shape} dtype={arr.dtype} MB={f.stat().st_size/1024/1024:.1f}")
    except Exception as e:
        print(f"  ERROR {rel}: {e}")

# Listar .json de configuracion
print("\n  --- Archivos .json (metadata de likelihood) ---")
for j in EXT.rglob("*.json"):
    try:
        d = json.loads(j.read_text())
        keys = list(d.keys())[:5]
        print(f"  {j.name:50s} keys={keys}")
    except:
        pass
