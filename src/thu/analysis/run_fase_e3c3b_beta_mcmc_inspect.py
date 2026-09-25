# -*- coding: utf-8 -*-
"""E.3-C3-B — Inspeccionar archivos clave de beta_mcmc."""
import sys
from pathlib import Path

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")
BM = REPO / "beta_mcmc"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

def dump(path, max_lines=250):
    print(f"\n  --- {path.relative_to(REPO)} ---")
    print(f"  ({path.stat().st_size} bytes)")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for l in lines[:max_lines]:
        print(f"    {l}")
    if len(lines) > max_lines:
        print(f"    ... ({len(lines)-max_lines} lineas mas)")

# 1. precomputed_loader.py (COMPLETO)
hdr("1. precomputed_loader.py (COMPLETO)")
dump(BM / "precomputed_loader.py", max_lines=500)

# 2. config.py (COMPLETO)
hdr("2. config.py (COMPLETO)")
dump(BM / "config.py", max_lines=300)

# 3. act_dr6/core.py (primeras 150)
hdr("3. act_dr6/core.py (primeras 150 lineas)")
dump(BM / "act_dr6" / "core.py", max_lines=150)

# 4. run_beta_mcmc.py — solo cabecera y flujo principal
hdr("4. run_beta_mcmc.py (primeras 100 lineas)")
dump(BM / "run_beta_mcmc.py", max_lines=100)

# 5. Buscar en TODO el repo donde se leen .npz
hdr("5. Referencias a .npz en el codigo")
import re
for p in REPO.rglob("*.py"):
    txt = p.read_text(encoding="utf-8", errors="replace")
    for i, line in enumerate(txt.splitlines(), 1):
        if ".npz" in line.lower() or "np.load" in line:
            rel = p.relative_to(REPO)
            print(f"    {str(rel):55s}:{i:4d}  {line.strip()[:90]}")

# 6. Buscar menciones a "precomputed" o "external" o "download"
hdr("6. Menciones a 'precomputed', 'download', 'url'")
for p in REPO.rglob("*.py"):
    txt = p.read_text(encoding="utf-8", errors="replace").lower()
    for kw in ["precomputed", "download", "https://", "gdown"]:
        if kw in txt:
            print(f"    {str(p.relative_to(REPO)):55s}  contiene '{kw}'")
