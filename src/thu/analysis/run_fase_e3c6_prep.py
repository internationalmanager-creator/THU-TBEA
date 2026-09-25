# -*- coding: utf-8 -*-
"""E.3-C6 — Copiar SACC + inspeccionar run_beta_mcmc.py para planificar checkpoint."""
import sys, shutil, re
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
REPO = LAB / "data" / "raw" / "cosmic-birefringence-planck-act"
SACC_SRC = LAB / "data" / "raw" / "act_dr6_packages" / "data" / "ACTDR6MFLike" / "v1.0" / "dr6_data.fits"
SACC_DST = REPO / "data" / "act_dr6" / "v1.0" / "dr6_data.fits"

def hdr(t):
    print(); print("="*72); print(f"  {t}"); print("="*72); sys.stdout.flush()

# --- 1: Copiar SACC ---
hdr("1. Copiar SACC a la ubicacion esperada por el pipeline")

print(f"  Origen:  {SACC_SRC}")
print(f"  Destino: {SACC_DST}")

if not SACC_SRC.exists():
    print(f"  ERROR: origen no existe")
    sys.exit(1)

SACC_DST.parent.mkdir(parents=True, exist_ok=True)

if SACC_DST.exists():
    print(f"  Destino ya existe, saltando copia")
else:
    print(f"  Copiando 855 MB... (esto tarda ~30s en mismo disco)")
    shutil.copy2(SACC_SRC, SACC_DST)
    print(f"  OK")

print(f"  Tamaño destino: {SACC_DST.stat().st_size / 1024/1024:.2f} MB")

# --- 2: Inspeccionar run_beta_mcmc.py ---
hdr("2. Analizar run_beta_mcmc.py")
run_file = REPO / "beta_mcmc" / "run_beta_mcmc.py"
txt = run_file.read_text(encoding="utf-8", errors="replace")
lines = txt.splitlines()
print(f"  Total lineas: {len(lines)}")

# Buscar EnsembleSampler y run_mcmc
patterns = [
    (r"EnsembleSampler\(", "EnsembleSampler instantiation"),
    (r"\.run_mcmc\(", "run_mcmc call"),
    (r"HDFBackend", "HDFBackend (si ya existe)"),
    (r"def main\(", "def main"),
    (r"if __name__", "entry point"),
    (r"sys\.argv", "argv parsing"),
    (r"load_precomputed", "precomputed loader"),
]

for pat, label in patterns:
    print(f"\n  --- {label}: /{pat}/ ---")
    for i, line in enumerate(lines, 1):
        if re.search(pat, line):
            print(f"    L{i}: {line}")

# --- 3: Extraer funcion main completa ---
hdr("3. Extraer funcion main (si existe)")
main_start = None
for i, line in enumerate(lines):
    if re.match(r"def main\(", line):
        main_start = i
        break
if main_start is not None:
    # Encontrar el final de main (next def o EOF)
    main_end = main_start + 1
    while main_end < len(lines):
        if re.match(r"^def |^if __name__", lines[main_end]):
            break
        main_end += 1
    print(f"  main() lineas {main_start+1}..{main_end}")
    for i in range(main_start, main_end):
        print(f"    L{i+1}: {lines[i]}")
else:
    print(f"  No se encontro 'def main('")

# --- 4: Extraer contexto de EnsembleSampler ---
hdr("4. Contexto de EnsembleSampler")
for i, line in enumerate(lines, 1):
    if "EnsembleSampler" in line:
        print(f"  L{i-5}..L{i+15}:")
        for j in range(max(0, i-5), min(len(lines), i+15)):
            prefix = ">>> " if j == i-1 else "    "
            print(f"    {prefix}L{j+1}: {lines[j]}")

# --- 5: Extraer contexto de run_mcmc ---
hdr("5. Contexto de run_mcmc")
for i, line in enumerate(lines, 1):
    if re.search(r"\.run_mcmc\(", line):
        print(f"  L{i-8}..L{i+10}:")
        for j in range(max(0, i-8), min(len(lines), i+10)):
            prefix = ">>> " if j == i-1 else "    "
            print(f"    {prefix}L{j+1}: {lines[j]}")
        print()
