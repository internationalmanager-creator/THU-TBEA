# -*- coding: utf-8 -*-
"""E.3-C7b — Diagnostico de imports + fix de pspy."""
import sys, re
from pathlib import Path

REPO = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto\data\raw\cosmic-birefringence-planck-act")

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# --- 1: Ver tools/data_loading.py ---
hdr("1. Inspeccionar tools/data_loading.py")
dl = REPO / "tools" / "data_loading.py"
txt = dl.read_text(encoding="utf-8")
lines = txt.splitlines()
print(f"  Total lineas: {len(lines)}")
print(f"  Contenido COMPLETO:")
for i, l in enumerate(lines, 1):
    print(f"    L{i:3d}: {l}")

# --- 2: Buscar quien importa data_loading ---
hdr("2. Archivos que importan tools.data_loading")
for p in REPO.rglob("*.py"):
    if p.name == "data_loading.py":
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    if "data_loading" in t or "NPIPE_TIME_SPLIT_FREQS" in t or "NPIPE_DUST_FREQS" in t:
        print(f"  {p.relative_to(REPO)}")
        for i, l in enumerate(t.splitlines(), 1):
            if "data_loading" in l or "NPIPE_TIME_SPLIT_FREQS" in l or "NPIPE_DUST_FREQS" in l:
                print(f"    L{i}: {l.strip()[:100]}")

# --- 3: Verificar si NPIPE_TIME_SPLIT_FREQS esta definida localmente ---
hdr("3. Donde se definen NPIPE_TIME_SPLIT_FREQS y NPIPE_DUST_FREQS")
for p in REPO.rglob("*.py"):
    t = p.read_text(encoding="utf-8", errors="replace")
    for kw in ["NPIPE_TIME_SPLIT_FREQS", "NPIPE_DUST_FREQS"]:
        for i, l in enumerate(t.splitlines(), 1):
            if kw in l and ("=" in l and "import" not in l):
                print(f"  {p.relative_to(REPO)}:L{i}  {l.strip()[:120]}")

# --- 4: Probar instalacion pip de pspy ---
hdr("4. Verificar si pspy es instalable via pip")
import subprocess
r = subprocess.run([sys.executable, "-m", "pip", "install", "pspy", "--dry-run"],
                   capture_output=True, text=True, timeout=60)
print(f"  stdout: {r.stdout[:500]}")
print(f"  stderr: {r.stderr[:500]}")
print(f"  returncode: {r.returncode}")
