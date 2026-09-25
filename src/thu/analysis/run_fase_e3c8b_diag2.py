# -*- coding: utf-8 -*-
"""E.3-C8b — Diagnostico doble: HDF5 no escrito + bug de chi2."""
import sys, re
from pathlib import Path

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")
BM = REPO / "beta_mcmc"
COMPUTED = REPO / "data" / "computed"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# --- 1: Buscar TODO .h5 en el repo ---
hdr("1. Todos los .h5 en el repo")
h5s = list(REPO.rglob("*.h5"))
print(f"  Encontrados: {len(h5s)}")
for h in h5s:
    print(f"    {h.relative_to(REPO)}  ({h.stat().st_size} bytes)")

# --- 2: Contenido de data/computed/ ---
hdr("2. Contenido de data/computed/")
if COMPUTED.exists():
    items = list(COMPUTED.rglob("*"))
    print(f"  Items totales: {len(items)}")
    for item in items:
        if item.is_file():
            print(f"    [FILE] {item.relative_to(REPO)}  ({item.stat().st_size} B)")
        else:
            print(f"    [DIR]  {item.relative_to(REPO)}")
else:
    print(f"  NO EXISTE: {COMPUTED}")

# --- 3: Ver _run_mcmc completo (para entender el manejo del backend) ---
hdr("3. _run_mcmc en run_beta_mcmc.py")
run_file = BM / "run_beta_mcmc.py"
lines = run_file.read_text(encoding="utf-8").splitlines()
for i, l in enumerate(lines):
    if re.match(r"def _run_mcmc\(", l):
        start = i
        end = start + 1
        while end < len(lines):
            if re.match(r"^def |^if __name__", lines[end]):
                break
            end += 1
        print(f"  Lineas {start+1}..{end}")
        for j in range(start, end):
            print(f"    L{j+1}: {lines[j]}")
        break

# --- 4: Ver mk_chi2 (crash L202) ---
hdr("4. mk_chi2 en birefringence_likelihood.py (L150-230)")
bl_file = BM / "birefringence_likelihood.py"
bl_lines = bl_file.read_text(encoding="utf-8").splitlines()
for j in range(149, min(230, len(bl_lines))):
    prefix = ">>> " if j+1 == 202 else "    "
    print(f"  {prefix}L{j+1}: {bl_lines[j]}")

# --- 5: Ver como _compute_chi2 llama mk_chi2 ---
hdr("5. _compute_chi2 (fragmento alrededor de L218)")
for j in range(205, min(230, len(lines))):
    prefix = ">>> " if j+1 == 218 else "    "
    print(f"  {prefix}L{j+1}: {lines[j]}")
